"""
derive_targets.py -- read the Calgary heating probabilities out of the audit data
instead of hand-typing them.

apply_to_sampler.py used to carry two hand-written blocks ("85% of Calgary homes
burn gas", "92% of those use a furnace"). Both were estimates. The weighted
EnerGuide table already answers the question from 74k audited Calgary homes, and
answers it *per house age and type* -- which the Bayesian network is built to
accept but was being fed a flat number for.

Two heating tables are produced, each keyed on exactly the parents the BN
conditions on (read from Bn.yml, not assumed):

    Source_Energie_Chauf | Type_Batiment, An_ConstructionCode
    Chauffage_Logement   | Type_Logement, Source_Energie_Chauf

Both use POND_AB, the census-corrected weight from calibrate_stock.py. Counting
audited homes directly would hand back the selection bias the weighting exists to
remove (too many detached houses, too many new builds).

A third block, "stock", supplies the housing mix those heating odds get averaged
over -- without it the network draws Calgary fuel shares for a Quebec city:

    Type_Logement                       (census marginal)
    An_Construction   | Type_Logement   (EnerGuide joint, IPF-fitted to census)
    Mode_Occupation   | Type_Logement   (census tenure x structural type)
    Nombre_Etages     | Type_Logement   (EnerGuide STOREYS, weighted)
    Superficie_Totale                   (marginal only -- see build_stock)

Usage (from repo root):
    uv run python calgary_adaptation/derive_targets.py
Writes data/output/calgary_bn_targets.json and prints both tables with the number
of homes behind every cell.
"""

from __future__ import annotations

import itertools
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# The census margins live in calibrate_stock because that is where they are
# raked to. Import rather than re-type: a second copy of these numbers is
# exactly the drift this file exists to prevent.
from calgary_adaptation.calibrate_stock import (  # noqa: E402
    CENSUS_MARGINS_CALGARY_2021,
    OWNER_SHARE_BY_TYPE,
    rake_to_census_margins,
)

STOCK = os.path.join(PROJECT_DIR, "data", "input", "alberta", "energuide",
                     "alberta_stock_mapped.parquet")
HC = os.path.join(PROJECT_DIR, "data", "processed", "housing_characteristics")
HVAC_CSV = os.path.join(HC, "HVAC Heating Efficiency.csv")
OUT_JSON = os.path.join(PROJECT_DIR, "data", "output", "calgary_bn_targets.json")

# A cell resting on fewer than this many audited homes is not trusted on its own;
# it falls back to the broader group. 50 mirrors the sparse-category threshold
# calibrate_stock.py already uses when raking.
MIN_SUPPORT = 50

# A cell is shrunk toward its group whenever its effective support is below
# MIN_SUPPORT x this factor. Above that the pull is under ~17% and not worth
# labelling, so the cell is reported as its own; the arithmetic is continuous
# either way, this only decides where the reporting line falls.
SHRINK_REPORT_FACTOR = 5.0

WEIGHT = "POND_AB"


# --------------------------------------------------------------------------- #
# Deriving the two parent columns the BN conditions on but the stock table lacks
# --------------------------------------------------------------------------- #

# Bn.yml: An_ConstructionCode = ['< 1946','[1946 - 1971)','[1971 - 1986)',
#                                '[1986 - 2013)','>= 2013']
AN_CODE_EDGES = [1946, 1971, 1986, 2013]
AN_CODE_LABELS = ["< 1946", "[1946 - 1971)", "[1971 - 1986)", "[1986 - 2013)", ">= 2013"]

# Type_Batiment is a deterministic child of Type_Logement (Bn.yml). Rather than
# guess the collapse, read it off the Quebec network at runtime.
TYPE_BATIMENT_FALLBACK = {
    "Collective": "Collective",
    "Triplex": "Plex",
    "Duplex": "Plex",
    "Maison en rangee": "Maison",
    "Maison individuelle": "Maison",
}


def bn_states(nodes, bn_path=None) -> dict[str, list[str]]:
    """The exact state list of each node, read off the network.

    The targets have to cover every parent combination the BN can present, in the
    BN's own spelling -- not just the combinations the audits happen to contain.
    """
    bn_path = bn_path or os.path.join(PROJECT_DIR, "data", "processed",
                                      "bayesian_network", "BN_EUEMr.XDSL")
    import pyagrum as gum
    bn = gum.loadBN(bn_path)
    return {n: list(bn.variable(n).labels()) for n in nodes}


def type_batiment_map(bn_path=None):
    """Read Type_Logement -> Type_Batiment off the BN, so this file cannot drift
    from the network. Falls back to the literal mapping if pyAgrum is absent."""
    bn_path = bn_path or os.path.join(PROJECT_DIR, "data", "processed",
                                      "bayesian_network", "BN_EUEMr.XDSL")
    try:
        import pyagrum as gum
        bn = gum.loadBN(bn_path)
        cpt = bn.cpt("Type_Batiment")
        bat = list(bn.variable("Type_Batiment").labels())
        out = {}
        for log in bn.variable("Type_Logement").labels():
            row = list(cpt[{"Type_Logement": log}])
            out[log] = bat[int(np.argmax(row))]
        return out
    except Exception as exc:                                  # pragma: no cover
        print(f"  note: could not read Type_Batiment from the BN ({exc}); "
              f"using the literal mapping")
        return dict(TYPE_BATIMENT_FALLBACK)


# --------------------------------------------------------------------------- #
# Deriving Chauffage_Logement from the EnerGuide equipment fields
# --------------------------------------------------------------------------- #

# The audits describe equipment as a make/efficiency phrase ("Condensing
# furnace", "Boiler with continuous pilot"). The BN wants one of 20 system
# labels. Match on substrings rather than enumerating all 29 spellings, which
# vary across the 20 yearly files.
_HP_REAL = {"central split system", "coils only", "ground source heat pump",
            "water source heat pump", "ductless mini- or multi-split system",
            "compact ducted mini- or multi-split system"}


def _base_system(furnace_type: str, fuel: str) -> str:
    """The primary system implied by FURNACETYPE, before heat-pump/wood overlays."""
    f = (furnace_type or "").strip().casefold()
    if "wood stove" in f or "wood" in f:
        return "Fournaise ou poêle à bois"
    if "baseboard" in f:
        # covers "Baseboard/Hydronic/Plenum(duct) htrs."
        return ("Plinthes électriques" if fuel == "Electricite"
                else "Système central à eau chaude")
    # A combined furnace/boiler or a P9/IMS package is hydronic at heart.
    if "boil" in f or f.startswith("p9") or f.startswith("ims"):
        return "Système central à eau chaude"
    if "furnace" in f:
        return "Système central à air chaud"
    if "heater" in f:
        # wall/floor space heater rather than a ducted furnace
        return "Fournaise murale ou de plancher"
    return "Système central à air chaud"      # unlabelled: the Calgary default


def _heat_pump_system(hp_type: str, base: str) -> str | None:
    """The BN label for a home whose primary system includes a heat pump."""
    h = (hp_type or "").strip().casefold()
    if h not in _HP_REAL:
        return None
    ducted_backup = base in ("Système central à air chaud",
                             "Fournaise murale ou de plancher")
    if "ground source" in h or "water source" in h:
        return "Thermopompe géothermique et Fournaise" if ducted_backup \
            else "Thermopompe géothermique seule"
    if "mini" in h or "ductless" in h:
        return "Thermopompe murale et Fournaise" if ducted_backup \
            else "Thermopompe murale"
    if base == "Système central à eau chaude":
        return "Thermopompe et Système central à eau chaude"
    return "Thermopompe et Système central à air chaud"


def derive_chauffage_logement(df: pd.DataFrame) -> pd.Series:
    """One BN heating-system label per audited home."""
    base = [
        _base_system(ft, fu)
        for ft, fu in zip(df["FURNACETYPE"].astype(str), df["Source_Energie_Chauf"])
    ]
    out = []
    for b, hp, fuel in zip(base, df["HPEquipType"].astype(str), df["Source_Energie_Chauf"]):
        if fuel == "Bois":
            # Primary fuel is wood => the primary system is the wood appliance.
            out.append("Fournaise ou poêle à bois")
            continue
        out.append(_heat_pump_system(hp, b) or b)
    return pd.Series(out, index=df.index, name="Chauffage_Logement")


# --------------------------------------------------------------------------- #
# Which (fuel, system) pairs the downstream table can actually price
# --------------------------------------------------------------------------- #

def valid_systems_by_fuel() -> dict[str, set[str]]:
    """Read the legal pairings straight out of HVAC Heating Efficiency.csv.

    A pairing with no row there crashes the sampler ("Error in sampling for
    attribute"), so anything we derive has to be filtered through this."""
    t = pd.read_csv(HVAC_CSV, sep=";")
    out: dict[str, set[str]] = defaultdict(set)
    for fuel, system in zip(t["Dependency=Source_Energie_Chauf"],
                            t["Dependency=Chauffage_Logement"]):
        out[str(fuel).strip()].add(str(system).strip())
    return dict(out)


# --------------------------------------------------------------------------- #
# Weighted shares, with a fallback for thin cells
# --------------------------------------------------------------------------- #

def _kish_neff(w) -> float:
    """Kish effective sample size: how many *equally weighted* homes a weighted
    cell is really worth. Imported in spirit from calibrate_stock, which prints
    the same statistic for the raking diagnostics."""
    w = np.asarray(w, dtype=float)
    ssq = float((w ** 2).sum())
    return float(w.sum() ** 2 / ssq) if ssq > 0 else 0.0


def _shrink(cell_shares, broad_shares, n_eff, prior_strength):
    """Dirichlet posterior mean: pull a thin cell toward the broader answer.

        p = (n_eff * p_cell + k * p_broad) / (n_eff + k)

    This replaces a hard n < 50 cutoff. The cutoff threw away a cell standing on
    49 homes entirely and trusted one standing on 51 completely, which is a
    cliff nothing in the data justifies -- ALBERTA_RECALIBRATION_PLAN.md risk 3
    asks for shrinkage toward the type-marginal instead, and this is it.

    `n_eff` is the *Kish effective* count, not the row count. That distinction
    is not pedantry here: raking 73,927 Calgary audits onto census margins
    leaves a Kish n_eff of 974, and apartments -- 27% of the city -- are worth
    73 independent homes out of 121 records. Shrinking on raw counts would treat
    a cell carried by a handful of 500x-weighted apartments as though it rested
    on hundreds of observations.
    """
    if not broad_shares:
        return dict(cell_shares)
    if not cell_shares:
        return dict(broad_shares)
    keys = set(cell_shares) | set(broad_shares)
    w_cell = n_eff / (n_eff + prior_strength)
    out = {k: w_cell * cell_shares.get(k, 0.0)
              + (1.0 - w_cell) * broad_shares.get(k, 0.0) for k in keys}
    total = sum(out.values())
    return {k: v / total for k, v in out.items() if v > 0} if total > 0 else dict(broad_shares)


def _shares(df: pd.DataFrame, col: str, allowed: set[str] | None = None):
    """Census-weighted share of each `col` value, optionally masked to `allowed`
    and renormalized. Returns (shares, n_homes, share_of_weight_dropped)."""
    w = df.groupby(col, observed=True)[WEIGHT].sum()
    total = w.sum()
    if total <= 0:
        return {}, len(df), 0.0
    dropped = 0.0
    if allowed is not None:
        keep = w.index.isin(allowed)
        dropped = float(w[~keep].sum() / total)
        w = w[keep]
        if w.sum() <= 0:
            return {}, len(df), dropped
    return {k: float(v / w.sum()) for k, v in w.items()}, len(df), dropped


def derive_conditional(df, target, by, states, fallback_by=None, allowed_for=None,
                       min_support=MIN_SUPPORT):
    """Weighted distribution of `target` for every combination of `by`.

    Cells resting on fewer than `min_support` audited homes fall back to the
    broader answer -- first `fallback_by` alone, then city-wide -- so a figure
    standing on four houses is never presented as measured. Every cell records
    how many homes are behind it and which level supplied it.

    `fallback_by` must name the column that dominates the answer, which is not
    always the first one. Heating *equipment* is driven by fuel far more than by
    dwelling shape, so a thin (row house, wood) cell has to broaden to "all wood
    homes" -- broadening to "all row houses" would average over gas furnaces and
    then be masked back down to wood-legal systems, which is nonsense.
    """
    fallback_by = fallback_by or by[0]
    assert fallback_by in by, f"fallback_by={fallback_by!r} not in {by}"
    city, n_city, _ = _shares(df, target)

    # Enumerate the FULL product of the BN's parent states, not just the
    # combinations the audits happen to contain. The network asks for every
    # combination; a missing one is a KeyError at build time.
    out = {}
    for keys in itertools.product(*[states[c] for c in by]):
        ctx = dict(zip(by, keys))
        allowed = allowed_for(ctx) if allowed_for else None
        mask = np.ones(len(df), dtype=bool)
        for col, val in ctx.items():
            mask &= (df[col] == val).to_numpy()
        grp = df[mask]
        shares, n, dropped = _shares(grp, target, allowed)
        n_eff = _kish_neff(grp[WEIGHT].to_numpy()) if len(grp) else 0.0
        level = "cell"

        # Shrink toward the broader answer instead of switching to it. A cell
        # with plenty of independent evidence keeps essentially its own numbers;
        # a thin one is pulled most of the way to the group it sits in; nothing
        # jumps at a threshold. `level` still records where the mass came from so
        # PROVENANCE can report it, but it now describes a blend, not a swap.
        if shares and n_eff < min_support * SHRINK_REPORT_FACTOR:
            broad = df[df[fallback_by] == ctx[fallback_by]]
            broad_shares, _, _ = _shares(broad, target, allowed)
            if not broad_shares:
                broad_shares, _, _ = _shares(df, target, allowed)
            before = shares
            shares = _shrink(shares, broad_shares, n_eff, min_support)
            if shares != before:
                level = f"shrunk:{fallback_by}"

        if not shares:
            broad = df[df[fallback_by] == ctx[fallback_by]]
            shares, n_broad, dropped = _shares(broad, target, allowed)
            level = f"fallback:{fallback_by}"
            if not shares:
                shares, _, dropped = _shares(df, target, allowed)
                level = "fallback:city"
            if not shares:
                # Nothing anywhere in the sample is legal for this combination.
                # Spread evenly over whatever the downstream table does allow so
                # the slice stays valid; it is unreachable in practice.
                pool = sorted(allowed) if allowed else sorted(city)
                shares = {k: 1.0 / len(pool) for k in pool}
                level = "uniform-over-legal"
        out["|".join(keys)] = {
            "shares": shares, "n_homes": int(n), "n_eff": round(n_eff, 1),
            "level": level, "reassigned_weight": round(dropped, 4),
        }
    return out, city, n_city


# --------------------------------------------------------------------------- #
# The housing stock: which homes the heating odds get averaged over
#
# The heating tables above are conditional on Type_Batiment x An_Construction-
# Code, but the network drew those parents from Quebec. The blocks below pin the
# mix to Calgary.
#
# Source of truth is CENSUS_MARGINS_CALGARY_2021. It used to be the only
# defensible source: calibrate_stock rakes the whole 191,618-row ALBERTA frame
# to Calgary-CSD margins, and taking the Calgary rows out afterwards landed on a
# subset that reproduced neither (Collective 34.4% weighted vs 27.1% census;
# [1990-2000) 20.7% vs 13.5%). load_calgary() now re-rakes the Calgary subset
# itself, so the weights agree with the census to ~1e-8 and every conditional
# derived below rests on a correct frame. The marginals are still read off the
# census rather than off the weights, because the census figure is exact and the
# raked one is only fitted to it.
# --------------------------------------------------------------------------- #

# EnerGuide STOREYS -> the BN's 3 Nombre_Etages states. Keys are casefolded and
# accent-stripped, so the 8 spellings across the 20 yearly files collapse here
# rather than in the caller. Split-level and split-entry are counted the way the
# Quebec survey counts them: by full storeys above grade.
STOREYS_TO_BN = {
    "one storey":                    "Un etage",
    "one and a half":                "Un etage",
    "split entry / raised basement": "Un etage",
    "split entry/raised base.":      "Un etage",
    "two storeys":                   "Deux etages",
    "two and a half":                "Deux etages",
    "split level":                   "Deux etages",
    "three storeys":                 "Trois etages et plus",
}

# HEATEDFLOORAREA is square METRES; Superficie_Totale's states are square FEET
# (Mapping.py builds them as 0..5000 step 500, from the Quebec SUPERTOT column).
M2_TO_FT2 = 10.7639

# Above this, a "dwelling" area in a multi-unit building is the building. Set at
# the top of the BN's binned range, and comfortably inside the observed gap
# between per-unit records (max 4,666 ft2) and whole-building ones (min 6,553).
PER_DWELLING_CEILING_FT2 = 5000

# Smoothing applied to the EnerGuide seed before IPF. IPF cannot move mass into a
# cell whose seed is exactly zero, and thin cells (Triplex x < 1950) are zero by
# accident of sampling, not because Calgary has none. Mixing 1% of the
# independence table in makes every cell reachable while leaving the observed
# correlation -- Calgary apartments skew new -- essentially intact.
IPF_SEED_SMOOTHING = 0.01


# EnerGuide AIRCONDTYPE -> the BN's 4 Climatisation states. "Not installed" and
# "None" are genuine survey codes here rather than nulls -- the column is 84%
# populated and its nulls are separate -- so they carry the real Calgary answer:
# 83.9% of the city has no air conditioning, against the 29.5% Quebec assumed.
AIRCOND_TO_BN = {
    "not installed":                              "Aucune",
    "none":                                       "Aucune",
    "window a/c":                                 "Fenetre, mobile, portable",
    "window a/c w/vent cooling":                  "Fenetre, mobile, portable",
    "window a/c w/ economizer":                   "Fenetre, mobile, portable",
    "mini-split ductless":                        "Murale",
    "ductless mini- or multi-split system":       "Murale",
    "compact ducted mini- or multi-split system": "Murale",
    "central split system":                       "Centrale",
    "central single package system":              "Centrale",
    # Legacy HOT2000 spelling for a ducted central unit, not a room air
    # conditioner: it predates the split/package distinction, so it belongs with
    # Centrale rather than with the window machines.
    "conventional a/c":                           "Centrale",
    "conventional a/c: with vent. cooling":       "Centrale",
    "a/c with economizer":                        "Centrale",
    "coils only":                                 "Centrale",
}

# EnerGuide PDHWFUEL -> ChaufEau_ChaufType. The extract carries two spellings of
# natural gas ("Natural gas" 40,335 rows and "Natural Gas" 25,108); folding the
# keys collapses them here instead of silently stranding 34% of the gas mass in
# an unmapped bin.
PDHWFUEL_TO_BN = {
    "natural gas":    "Gaz Naturel",
    "electricity":    "Electrique",
    "propane":        "Propane",
    "oil":            "Mazout",
    "wood":           "Bois",
    "not applicable": "Aucun",
}

# Solar has no ChaufEau_ChaufType state. It is 0.1% of Calgary and a solar system
# still needs a backup fuel, so folding it into "Aucun" -- which means no water
# heater at all -- would be worse than dropping it and renormalizing.
PDHWFUEL_DROP = {"solar"}

# A PDHWTYPE containing either substring is tankless ("Instantaneous",
# "Instantaneous (condensing)", "Tankless coil", ...). Everything else is a
# storage tank and gets binned by volume.
PDHWTYPE_TANKLESS = ("instantaneous", "tankless")

# PRIMARYDHWTANKVOLUME is litres: its two dominant values are 151.4 L = 40.0 US
# gal and 189.3 L = 50.0. ChaufEau_Type's states are US gallons.
L_TO_USGAL = 3.785

# Upper edges (exclusive) for ChaufEau_Type's gallon states. The Quebec survey
# offered overlapping choices -- both "23-40" and "40", both "60" and "60 et
# plus" -- so the exact round sizes get a narrow bin of their own and the ranges
# take what falls between them.
DHW_GALLON_BINS = [
    (22.0,   "Moins de 22 gallons"),
    (23.0,   "22 gallons"),
    (39.5,   "23-40 gallons"),
    (41.0,   "40 gallons"),
    (59.5,   "41-59 gallons"),
    (61.0,   "60 gallons"),
    (np.inf, "60 et plus gallons"),
]

# ACH50 values behind the BN's 13 Infiltration states. They are unevenly spaced
# (1..8, then 10, 15, 20, 25, 30), so records are assigned to the nearest value
# rather than cut on regular edges.
INFILTRATION_ACH = [1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20, 25, 30]


def _fold(s: str) -> str:
    """Casefolded, accent-stripped form, for matching our spellings against the
    BN's ('Un etage' -> the network's 'Un étage')."""
    return "".join(c for c in unicodedata.normalize("NFKD", str(s))
                   if not unicodedata.combining(c)).casefold().strip()


def _match_label(labels: list[str], key: str) -> str:
    """The BN's own spelling of `key`. Matching on the folded form keeps this
    file readable in ASCII without risking a silent accent mismatch, which
    force_node() would only report as a KeyError much later."""
    want = _fold(key)
    for lbl in labels:
        if _fold(lbl) == want:
            return lbl
    raise KeyError(f"no state matching {key!r} among {labels}")


def _mapped_series(df, column, mapping, states, drop=frozenset()):
    """EnerGuide `column` folded and mapped onto BN state labels; NaN where the
    spelling is unknown or deliberately dropped.

    Folding both sides means the yearly extracts' spelling drift collapses here
    rather than silently stranding weight in an unmapped bin -- STOREYS arrives
    in 8 spellings and PDHWFUEL in two casings of "Natural gas", which between
    them cover a third of Calgary's water heating."""
    folded = df[column].map(_fold)
    unknown = sorted(set(folded.dropna()) - set(mapping) - set(drop) - {"", "nan"})
    if unknown:
        print(f"  note: {len(unknown)} unmapped {column} value(s) dropped: {unknown[:5]}")
    return folded.map(mapping).map(
        lambda v: _match_label(states, v) if isinstance(v, str) else v)


def ipf_table(seed: pd.DataFrame, row_target: dict, col_target: dict,
              tol: float = 1e-10, max_iter: int = 500) -> pd.DataFrame:
    """Fit a 2-D joint to both its marginals by iterative proportional fitting.

    The census publishes dwelling type and period of construction as separate
    marginals; it does not publish the cross-tab. IPF is the standard way to
    recover a joint that honours both while keeping the association structure of
    a seed table -- here the EnerGuide one, which knows that Calgary apartments
    are newer than its houses. calibrate_stock.ipf_rake does the same arithmetic
    on row weights; this is the table-shaped version.
    """
    t = seed.to_numpy(dtype=float).copy()
    rt = np.array([row_target[i] for i in seed.index], dtype=float)
    ct = np.array([col_target[c] for c in seed.columns], dtype=float)
    assert t.min() >= 0, "seed has negative cells"
    rt, ct = rt / rt.sum(), ct / ct.sum()

    t = t / t.sum()
    t = (1.0 - IPF_SEED_SMOOTHING) * t + IPF_SEED_SMOOTHING * np.outer(rt, ct)

    for _ in range(max_iter):
        rs = t.sum(axis=1)
        t *= np.divide(rt, rs, out=np.zeros_like(rt), where=rs > 0)[:, None]
        cs = t.sum(axis=0)
        t *= np.divide(ct, cs, out=np.zeros_like(ct), where=cs > 0)[None, :]
        if np.abs(t.sum(axis=1) - rt).max() < tol:
            break
    else:
        raise AssertionError(f"IPF did not converge in {max_iter} iterations")
    return pd.DataFrame(t, index=seed.index, columns=seed.columns)


def _weighted_joint(df, rows: str, cols: str,
                    row_states: list[str], col_states: list[str]) -> pd.DataFrame:
    """POND_AB-weighted cross-tab, reindexed onto the BN's full state lists so a
    combination the audits never saw is a zero rather than a missing row."""
    j = df.pivot_table(index=rows, columns=cols, values=WEIGHT,
                       aggfunc="sum", fill_value=0.0, observed=True)
    return j.reindex(index=row_states, columns=col_states, fill_value=0.0)


def _cells(shares_by_key: dict, n_by_key: dict, level: str) -> dict:
    """Wrap plain {parent: {state: share}} into the cell schema apply_to_sampler's
    _cell_lookup() already reads."""
    return {
        key: {"shares": shares, "n_homes": int(n_by_key.get(key, 0)),
              "level": level, "reassigned_weight": 0.0}
        for key, shares in shares_by_key.items()
    }


def superficie_marginal(df: pd.DataFrame, states: list[str]) -> tuple[dict, int]:
    """Calgary's weighted floor-area distribution over the BN's 11 ft^2 bins.

    Returned as a marginal, not a CPT: the BN hangs Superficie_Totale off
    Nombre_Pieces, and EnerGuide records no room count, so there is no joint to
    observe. apply_to_sampler rakes the Quebec conditional to this marginal
    instead -- Quebec's room-to-size shape survives, Calgary's sizes win.
    """
    a = pd.to_numeric(df["HEATEDFLOORAREA"], errors="coerce") * M2_TO_FT2
    keep = a.notna() & (a > 0)

    # In multi-unit buildings HEATEDFLOORAREA is recorded inconsistently: some
    # records give the evaluated unit, some the whole building. Calgary's
    # Collective records split cleanly in two -- 40 between 511 and 4,666 ft2,
    # then 22 between 6,553 and 21,050 ft2 with the same unit counts, so the
    # second group is buildings. NUMDWELLINGUNITS cannot tell them apart, but the
    # gap can. Left in, those 22 records ride 27% of the city's weight and put
    # 6.7% of Calgary dwellings above 5,000 ft2 against 1.2% unweighted.
    units = pd.to_numeric(df["NUMDWELLINGUNITS"], errors="coerce")
    whole_building = (units > 1) & (a > PER_DWELLING_CEILING_FT2)
    n_dropped = int((keep & whole_building).sum())
    if n_dropped:
        print(f"  note: dropped {n_dropped} floor-area record(s) above "
              f"{PER_DWELLING_CEILING_FT2:,} ft2 in multi-unit buildings "
              f"(whole-building area, not per-dwelling)")
    keep &= ~whole_building

    a, w = a[keep], df.loc[keep, WEIGHT]

    edges = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, np.inf]
    assert len(edges) - 1 == len(states), f"{len(edges)-1} bins vs {len(states)} states"
    binned = pd.cut(a, bins=edges, labels=states, right=False)
    w_by = w.groupby(binned, observed=False).sum().reindex(states, fill_value=0.0)

    median = float(a.median())
    assert 800 <= median <= 3000, (
        f"median floor area {median:,.0f} ft^2 is implausible -- HEATEDFLOORAREA "
        f"is metres squared and must be scaled by {M2_TO_FT2}; check the units.")
    return {k: float(v / w_by.sum()) for k, v in w_by.items()}, int(keep.sum())


CENSUS_FSA_PARQUET = os.path.join(PROJECT_DIR, "data", "input", "alberta",
                                  "census", "calgary_fsa_composition.parquet")
CENSUS_HHSIZE_COLUMNS = ("hh_1", "hh_2", "hh_3", "hh_4", "hh_5plus")


def nombre_personnes_marginal(states: list) -> tuple:
    """Calgary household-size shares, summed over the 36 census FSAs.

    Tier A in the plan and the only Tier-A node that had been left Quebec. The
    counts come from the 2021 Census Profile table already cached on disk
    (98-401-X2021013), so this needs no network call and no hand-typed figure.

    The five census categories land exactly on the five BN states -- "5 or more
    persons" is the BN's "5 et plus" -- so there is no folding judgement here,
    unlike the dwelling-type margins where Triplex has no census counterpart.

    Returned as a marginal, for the same reason Superficie_Totale is: the BN
    hangs Nombre_Personnes off Nombre_Pieces, the census publishes no
    household-size-by-room-count crosstab at this geography, and EnerGuide
    records no room count at all. Writing a CPT would mean inventing
    P(persons | rooms); raking the marginal keeps Quebec's rooms-to-people shape
    and moves only the household-size totals onto Calgary.
    """
    assert os.path.exists(CENSUS_FSA_PARQUET), (
        f"{CENSUS_FSA_PARQUET} missing -- run "
        f"`uv run python calgary_adaptation/fetch_data.py` first")
    census = pd.read_parquet(CENSUS_FSA_PARQUET)
    missing = [c for c in CENSUS_HHSIZE_COLUMNS if c not in census.columns]
    assert not missing, (
        f"{os.path.basename(CENSUS_FSA_PARQUET)} predates household size "
        f"({missing}); re-run fetch_data.py to re-parse the cached census zip")
    counts = census[list(CENSUS_HHSIZE_COLUMNS)].sum()
    total = float(counts.sum())
    assert len(states) == len(CENSUS_HHSIZE_COLUMNS), (
        f"BN Nombre_Personnes has {len(states)} states, census has "
        f"{len(CENSUS_HHSIZE_COLUMNS)}: {states}")
    shares = {st: float(counts[c] / total)
              for st, c in zip(states, CENSUS_HHSIZE_COLUMNS)}
    return shares, int(total)


def build_stock(df: pd.DataFrame, states: dict[str, list[str]]) -> dict:
    """The four stock CPTs plus the floor-area marginal."""
    census_type = CENSUS_MARGINS_CALGARY_2021["Type_Logement"]
    census_vintage = CENSUS_MARGINS_CALGARY_2021["An_Construction"]
    type_states = states["Type_Logement"]
    assert set(census_type) == set(type_states), (
        f"census Type_Logement {sorted(census_type)} != BN {sorted(type_states)}")

    # -- Type_Logement: the census marginal, verbatim ------------------------ #
    type_shares = {t: float(census_type[t]) for t in type_states}

    # -- An_Construction | Type_Logement ------------------------------------- #
    vintage_states = states["An_Construction"]
    assert set(census_vintage) == set(vintage_states), (
        "census An_Construction bins do not match the BN's")
    seed = _weighted_joint(df, "Type_Logement", "An_Construction",
                           type_states, vintage_states)
    # Same MIN_SUPPORT rule the heating tables use: a dwelling type resting on
    # fewer than 50 audited homes does not get to assert its own vintage profile
    # (47 audited triplexes would otherwise put 82% of Calgary's triplexes in the
    # 1980s). Collapse it to the city-wide shape and let IPF do the rest.
    n_by_type = df.groupby("Type_Logement", observed=True).size().to_dict()
    city_vintage = seed.sum(axis=0)
    thin_types = [t for t in type_states if n_by_type.get(t, 0) < MIN_SUPPORT]
    for t in thin_types:
        seed.loc[t] = city_vintage * (seed.loc[t].sum() or 1.0) / city_vintage.sum()
    if thin_types:
        print(f"  note: vintage profile for {thin_types} fell back to city-wide "
              f"(< {MIN_SUPPORT} audited homes)")
    joint = ipf_table(seed, census_type, census_vintage)
    vintage_cells = {
        t: {v: float(joint.loc[t, v] / joint.loc[t].sum()) for v in vintage_states}
        for t in type_states
    }

    # -- Mode_Occupation | Type_Logement ------------------------------------- #
    # Seeded from the census tenure x structural-type table rather than from
    # POND_AB: the imputed Mode_Occupation column in the parquet was DRAWN from
    # OWNER_SHARE_BY_TYPE, so deriving it back out would only add sampling noise.
    # The two census dicts are independent roundings and disagree by ~1.7pp on
    # the overall owner share, so IPF them onto both margins the same way the
    # vintage joint is handled -- otherwise the BN reproduces neither.
    occ_states = states["Mode_Occupation"]
    owner = _match_label(occ_states, "Proprietaire")
    renter = _match_label(occ_states, "Locataire")
    occ_seed = pd.DataFrame(
        [[census_type[t] * OWNER_SHARE_BY_TYPE[t],
          census_type[t] * (1.0 - OWNER_SHARE_BY_TYPE[t])] for t in type_states],
        index=type_states, columns=[owner, renter])
    occ_joint = ipf_table(
        occ_seed, census_type,
        {owner: CENSUS_MARGINS_CALGARY_2021["Mode_Occupation"]["Proprietaire"],
         renter: CENSUS_MARGINS_CALGARY_2021["Mode_Occupation"]["Locataire"]})
    occ_cells = {
        t: {o: float(occ_joint.loc[t, o] / occ_joint.loc[t].sum()) for o in (owner, renter)}
        for t in type_states
    }

    # -- Nombre_Etages | Type_Logement --------------------------------------- #
    etage_states = states["Nombre_Etages"]
    st = df.assign(
        Nombre_Etages=_mapped_series(df, "STOREYS", STOREYS_TO_BN, etage_states))
    st = st.dropna(subset=["Nombre_Etages"])
    etage_cells, etage_city, _ = derive_conditional(
        st, "Nombre_Etages", ["Type_Logement"], states, fallback_by="Type_Logement")

    # -- Superficie_Totale (marginal only) ----------------------------------- #
    area_shares, n_area = superficie_marginal(df, states["Superficie_Totale"])

    # -- Nombre_Personnes (marginal only, straight from the census) ----------- #
    pers_shares, n_pers = nombre_personnes_marginal(states["Nombre_Personnes"])

    n_all = {t: n_by_type.get(t, 0) for t in type_states}
    return {
        "note": ("Type_Logement / An_Construction / Mode_Occupation are read "
                 "straight off the 2021 census. load_calgary() now re-rakes the "
                 "Calgary subset to those same margins, so the weighted subset "
                 "reproduces them to ~1e-8 and the two routes agree; the census "
                 "is kept as the source of truth because it is exact where the "
                 "weights are only fitted."),
        "Type_Logement": {
            "parents": [],
            "shares": type_shares,
            "source": "CENSUS_MARGINS_CALGARY_2021",
        },
        "An_Construction": {
            "parents": ["Type_Logement"],
            "cells": _cells(vintage_cells, n_all, "census-IPF"),
            "source": "EnerGuide joint, IPF-fitted to both census margins",
        },
        "Mode_Occupation": {
            "parents": ["Type_Logement"],
            "cells": _cells(occ_cells, n_all, "census"),
            "source": "OWNER_SHARE_BY_TYPE (census tenure x structural type)",
        },
        "Nombre_Etages": {
            "parents": ["Type_Logement"],
            "cells": etage_cells,
            "city_wide": etage_city,
            "source": "EnerGuide STOREYS, POND_AB-weighted",
        },
        "Superficie_Totale": {
            "parents": [],
            "shares": area_shares,
            "n_homes": n_area,
            "source": (f"EnerGuide HEATEDFLOORAREA x {M2_TO_FT2} ft2/m2, "
                       f"POND_AB-weighted; {n_area:,} of {len(df):,} Calgary homes "
                       f"report a usable area"),
            "applied_as": "marginal rake of P(Superficie_Totale | Nombre_Pieces)",
        },
        "Nombre_Personnes": {
            "parents": [],
            "shares": pers_shares,
            "n_homes": n_pers,
            "source": ("2021 Census Profile 98-401-X2021013, household size "
                       "(characteristics 51-55) summed over Calgary's 36 FSAs"),
            "applied_as": "marginal rake of P(Nombre_Personnes | Nombre_Pieces)",
        },
    }


def print_stock(stock: dict) -> None:
    print("\n=== The housing mix the heating odds are averaged over ===")
    print("  Type_Logement (2021 census):")
    for t, p in sorted(stock["Type_Logement"]["shares"].items(), key=lambda kv: -kv[1]):
        print(f"    {t:<22} {p:6.1%}")
    print("  An_Construction | Type_Logement (EnerGuide shape, census margins):")
    for t, cell in stock["An_Construction"]["cells"].items():
        top = sorted(cell["shares"].items(), key=lambda kv: -kv[1])[:2]
        print(f"    {t:<22} n={cell['n_homes']:>6,}  "
              + "; ".join(f"{k} {v:.0%}" for k, v in top))
    print("  Nombre_Etages | Type_Logement:")
    for t, cell in stock["Nombre_Etages"]["cells"].items():
        top = sorted(cell["shares"].items(), key=lambda kv: -kv[1])[:2]
        note = "" if cell["level"] == "cell" else f"  <- {cell['level']}"
        print(f"    {t:<22} n={cell['n_homes']:>6,}  "
              + "; ".join(f"{k} {v:.0%}" for k, v in top) + note)
    pers = stock["Nombre_Personnes"]
    print("  Nombre_Personnes (2021 census, n={:,} households): ".format(pers["n_homes"])
          + "; ".join(f"{k} {v:.0%}" for k, v in pers["shares"].items()))
    area = stock["Superficie_Totale"]
    shown = sorted(area["shares"].items(), key=lambda kv: -kv[1])[:3]
    print(f"  Superficie_Totale (marginal, n={area['n_homes']:,}): "
          + "; ".join(f"{k} {v:.0%}" for k, v in shown))


def _expand(inner_cells: dict, parents: list[str], states: dict,
            inner_parent: str, skip_when=None,
            skip_level: str = "quebec-preserved") -> dict:
    """Broadcast a conditional derived on ONE parent across the BN's full parent
    product, so _cell_lookup() finds every combination the network can ask for.

    `skip_when(inst) -> bool` marks the combinations whose Quebec row has to
    survive. Those get empty shares, which makes force_node's _retarget an
    identity -- "leave this slice alone" expressed as data, so the application
    side needs no special case for them."""
    out = {}
    for combo in itertools.product(*[states[p] for p in parents]):
        inst = dict(zip(parents, combo))
        key = "|".join(combo)
        if skip_when is not None and skip_when(inst):
            out[key] = {"shares": {}, "n_homes": 0, "level": skip_level,
                        "reassigned_weight": 0.0}
        else:
            out[key] = dict(inner_cells[inst[inner_parent]])
    return out


def build_enduse(df: pd.DataFrame, states: dict[str, list[str]]) -> dict:
    """The five end-use CPTs: cooling, water-heater fuel and size, basement and
    airtightness.

    Unlike the stock block above these carry no census-margin caveat. They are
    POND_AB-weighted EnerGuide observations -- things an auditor measured inside
    Calgary homes -- so the raking-frame mismatch does not reach them."""
    n_all = len(df)
    no_heater = _match_label(states["ChaufEau_Presence"], "Aucun")

    def is_no_heater(inst):
        return inst["ChaufEau_Presence"] == no_heater

    # -- Climatisation | Chauffage_Logement x Type_Logement ------------------ #
    # AIRCONDTYPE gives cooling by dwelling type, but the BN also conditions on
    # the heating system, which EnerGuide cannot answer at that resolution.
    # Broadcast the type answer across the heating states -- EXCEPT the heat-pump
    # ones, where the heating equipment IS the cooling equipment and Quebec's
    # rows already say so. Flattening those would tell the sampler a heat-pump
    # home probably has no cooling. It costs almost nothing: Calgary is 98.4%
    # gas-heated, so the heat-pump slices carry negligible weight.
    clim_states = states["Climatisation"]
    ac = df.assign(Climatisation=_mapped_series(
        df, "AIRCONDTYPE", AIRCOND_TO_BN, clim_states)).dropna(subset=["Climatisation"])
    clim_by_type, clim_city, _ = derive_conditional(
        ac, "Climatisation", ["Type_Logement"], states, fallback_by="Type_Logement")

    # -- ChaufEau_ChaufType | Source_Energie_Chauf x ChaufEau_Presence ------- #
    # Cross-tabbed against the heating fuel rather than raked to a marginal, so
    # the real correlation between space- and water-heating fuel survives.
    fuel_states = states["ChaufEau_ChaufType"]
    dhw = df.assign(ChaufEau_ChaufType=_mapped_series(
        df, "PDHWFUEL", PDHWFUEL_TO_BN, fuel_states,
        drop=PDHWFUEL_DROP)).dropna(subset=["ChaufEau_ChaufType"])
    dhwfuel, dhwfuel_city, _ = derive_conditional(
        dhw, "ChaufEau_ChaufType", ["Source_Energie_Chauf"], states,
        fallback_by="Source_Energie_Chauf")

    # -- ChaufEau_Type | ChaufEau_Presence x Type_Logement ------------------- #
    # PDHWTYPE identifies tankless cleanly; everything else is a storage tank and
    # needs PRIMARYDHWTANKVOLUME, which is 43.5% null. The observed sizes are
    # renormalized to 1, leaving 'Non definit' and 'Ne sait pas' at zero: a
    # missing audit field is a gap in the record, not a physical property of the
    # house, and the sampler downstream has to pick an actual tank.
    tank_states = states["ChaufEau_Type"]
    tankless = df["PDHWTYPE"].map(_fold).str.contains(
        "|".join(PDHWTYPE_TANKLESS), na=False, regex=True)
    gal = pd.to_numeric(df["PRIMARYDHWTANKVOLUME"], errors="coerce") / L_TO_USGAL
    sized = ~tankless & gal.notna() & (gal > 0)
    lab = pd.Series(pd.NA, index=df.index, dtype="object")
    lab[tankless] = _match_label(tank_states, "Chauffe-eau sans reservoir")
    lab[sized] = pd.cut(gal[sized],
                        bins=[0.0] + [e for e, _ in DHW_GALLON_BINS],
                        labels=[_match_label(tank_states, n) for _, n in DHW_GALLON_BINS],
                        right=False, ordered=False).astype(object)
    tank = df.assign(ChaufEau_Type=lab).dropna(subset=["ChaufEau_Type"])
    tank_cells, tank_city, _ = derive_conditional(
        tank, "ChaufEau_Type", ["Type_Logement"], states, fallback_by="Type_Logement")

    # -- Presence_SousSol | Nombre_Etages x Type_Logement -------------------- #
    # Read off the area fields, not FNDTYPE: FNDTYPE is 17.2% literal "None" and
    # its 44 semicolon-joined code strings say nothing about basement height,
    # while the area fields are 99.1% populated and answer directly.
    sous_states = states["Presence_SousSol"]
    bas_a = pd.to_numeric(df["BASEMENTFLOORAR"], errors="coerce")
    crawl_a = pd.to_numeric(df["CRAWLSPFLOORAR"], errors="coerce")
    observed = (bas_a.notna() | crawl_a.notna()).to_numpy()
    bas, crawl = (bas_a.fillna(0) > 0), (crawl_a.fillna(0) > 0)
    raw = np.select(
        [bas & crawl, bas & ~crawl, ~bas & crawl],
        ["Sous-sol et vide sanitaire", "Sous sol 6 pied", "Vide sanitaire moins 6 pieds"],
        default="Aucun Sous-sol ou vide sanitaire")
    lut = {k: _match_label(sous_states, k) for k in set(raw.tolist())}
    sd = df.assign(
        Presence_SousSol=pd.Series(raw, index=df.index).map(lut),
        Nombre_Etages=_mapped_series(df, "STOREYS", STOREYS_TO_BN,
                                     states["Nombre_Etages"]),
    )[observed].dropna(subset=["Nombre_Etages"])
    sous_cells, sous_city, _ = derive_conditional(
        sd, "Presence_SousSol", ["Nombre_Etages", "Type_Logement"], states,
        fallback_by="Type_Logement")

    # -- Infiltration | Type_Logement x An_Construction ---------------------- #
    # AIR50P is the cleanest column in the set: no nulls, 0.17-46.2 ACH50. The
    # BN's 13 states are unevenly spaced (1..8, then 10, 15, 20, 25, 30), so
    # assign each record to the nearest rather than cutting on regular edges.
    inf_states = states["Infiltration"]
    ach = pd.to_numeric(df["AIR50P"], errors="coerce")
    grid = np.array(INFILTRATION_ACH, dtype=float)
    nearest = np.abs(ach.to_numpy(dtype=float)[:, None] - grid[None, :]).argmin(axis=1)
    ilut = {v: _match_label(inf_states, f"{v} ACH50") for v in INFILTRATION_ACH}
    ilab = pd.Series([ilut[INFILTRATION_ACH[i]] for i in nearest],
                     index=df.index, dtype="object")
    ilab[(ach.isna() | (ach <= 0)).to_numpy()] = pd.NA
    idf = df.assign(Infiltration=ilab).dropna(subset=["Infiltration"])
    # Airtightness is driven by construction era far more than by dwelling
    # shape, so a thin cell broadens over vintage, not over type.
    inf_cells, inf_city, _ = derive_conditional(
        idf, "Infiltration", ["Type_Logement", "An_Construction"], states,
        fallback_by="An_Construction")

    return {
        "note": ("Cooling, water heating and envelope, straight from POND_AB-"
                 "weighted EnerGuide observations. ChaufEau_Presence is NOT here: "
                 "EnerGuide has no field separating a dwelling's own water heater "
                 "from a building-central one, and the only cell where that "
                 "matters (Collective) is exactly the one it cannot identify."),
        "Climatisation": {
            "parents": ["Chauffage_Logement", "Type_Logement"],
            "cells": _expand(
                clim_by_type, ["Chauffage_Logement", "Type_Logement"], states,
                "Type_Logement",
                skip_when=lambda i: "thermopompe" in _fold(i["Chauffage_Logement"]),
                skip_level="quebec-preserved:heat-pump-is-the-cooling"),
            "city_wide": clim_city,
            "by_type": clim_by_type,
            "source": (f"EnerGuide AIRCONDTYPE, POND_AB-weighted; {len(ac):,} of "
                       f"{n_all:,} Calgary homes report a cooling record"),
            "limitation": ("Broadcast over Chauffage_Logement rather than jointly "
                           "derived; heat-pump heating states keep their Quebec rows."),
        },
        "ChaufEau_ChaufType": {
            "parents": ["Source_Energie_Chauf", "ChaufEau_Presence"],
            "cells": _expand(
                dhwfuel, ["Source_Energie_Chauf", "ChaufEau_Presence"], states,
                "Source_Energie_Chauf", skip_when=is_no_heater,
                skip_level="quebec-preserved:no-water-heater"),
            "city_wide": dhwfuel_city,
            "by_heating_fuel": dhwfuel,
            "source": (f"EnerGuide PDHWFUEL x Source_Energie_Chauf, POND_AB-"
                       f"weighted; {len(dhw):,} of {n_all:,} homes"),
        },
        "ChaufEau_Type": {
            "parents": ["ChaufEau_Presence", "Type_Logement"],
            "cells": _expand(
                tank_cells, ["ChaufEau_Presence", "Type_Logement"], states,
                "Type_Logement", skip_when=is_no_heater,
                skip_level="quebec-preserved:no-water-heater"),
            "city_wide": tank_city,
            "coverage": round(len(tank) / n_all, 4),
            "source": (f"EnerGuide PDHWTYPE (tankless) + PRIMARYDHWTANKVOLUME / "
                       f"{L_TO_USGAL} L per US gal; {len(tank):,} of {n_all:,} homes "
                       f"report a usable size"),
            "limitation": ("PRIMARYDHWTANKVOLUME is 43.5% null. Observed sizes are "
                           "renormalized to 1, so 'Non definit' and 'Ne sait pas' "
                           "fall to zero rather than absorbing the non-response."),
        },
        "Presence_SousSol": {
            "parents": ["Nombre_Etages", "Type_Logement"],
            "cells": sous_cells,
            "city_wide": sous_city,
            "source": (f"EnerGuide BASEMENTFLOORAR / CRAWLSPFLOORAR, POND_AB-"
                       f"weighted; {len(sd):,} of {n_all:,} homes"),
            "limitation": ("The 6-foot threshold in the Quebec state labels is not "
                           "observable here: any basement maps to 'Sous sol 6 pied'. "
                           "Calgary basements are essentially all full height."),
        },
        "Infiltration": {
            "parents": ["Type_Logement", "An_Construction"],
            "cells": inf_cells,
            "city_wide": inf_city,
            "source": (f"EnerGuide AIR50P snapped to the nearest of "
                       f"{len(INFILTRATION_ACH)} ACH50 states, POND_AB-weighted; "
                       f"{len(idf):,} of {n_all:,} homes"),
        },
    }


ENDUSE_NODES = ("Climatisation", "ChaufEau_ChaufType", "ChaufEau_Type",
                "Presence_SousSol", "Infiltration")


def print_enduse(enduse: dict) -> None:
    print("\n=== The end uses that stock gets multiplied by ===")
    clim = enduse["Climatisation"]
    print("  Climatisation | Type_Logement (broadcast; heat-pump rows preserved):")
    for t, cell in clim["by_type"].items():
        top = sorted(cell["shares"].items(), key=lambda kv: -kv[1])[:2]
        note = "" if cell["level"] == "cell" else f"  <- {cell['level']}"
        print(f"    {t:<22} n={cell['n_homes']:>6,}  "
              + "; ".join(f"{k} {v:.0%}" for k, v in top) + note)
    print(f"    {'CITY-WIDE':<22} no cooling "
          f"{clim['city_wide'].get('Aucune', 0):.1%}")

    fuel = enduse["ChaufEau_ChaufType"]
    print("  ChaufEau_ChaufType | Source_Energie_Chauf:")
    for f, cell in fuel["by_heating_fuel"].items():
        top = sorted(cell["shares"].items(), key=lambda kv: -kv[1])[:2]
        note = "" if cell["level"] == "cell" else f"  <- {cell['level']}"
        print(f"    {f:<22} n={cell['n_homes']:>6,}  "
              + "; ".join(f"{k} {v:.0%}" for k, v in top) + note)

    for node, label in (("ChaufEau_Type", "water-heater size"),
                        ("Presence_SousSol", "basement"),
                        ("Infiltration", "airtightness")):
        city = enduse[node]["city_wide"]
        top = sorted(city.items(), key=lambda kv: -kv[1])[:3]
        fell = sum(1 for c in enduse[node]["cells"].values()
                   if c["level"].startswith("fallback"))
        note = f"  [{fell} cell(s) fell back]" if fell else ""
        print(f"  {node} ({label}), city-wide: "
              + "; ".join(f"{k} {v:.0%}" for k, v in top) + note)


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #

def load_calgary() -> pd.DataFrame:
    assert os.path.exists(STOCK), (
        f"{STOCK} missing -- run `uv run python calgary_adaptation/calibrate_stock.py` first")
    df = pd.read_parquet(STOCK)
    assert WEIGHT in df.columns, f"{WEIGHT} missing: the stock table is not raked"
    df = df[df["CLIENTCITY"].astype(str).str.strip().str.casefold() == "calgary"].copy()

    # Re-rake, on the Calgary subset, to the Calgary margins.
    #
    # calibrate_stock rakes the whole ~191k-row ALBERTA frame to Calgary-CSD
    # margins. IPF makes the *frame it is given* reproduce those margins, so
    # taking the Calgary rows out afterwards lands on a subset that reproduces
    # neither Alberta nor Calgary: Collective came out 34.4% weighted against
    # the census's 27.1%, [1990-2000) 20.7% against 13.5%. Every conditional
    # below -- fuel, equipment, cooling, water-heater fuel and size, basements,
    # airtightness -- is a weighted crosstab, so all of them inherited that
    # error. Raking the subset itself is the fix, and it is the same thing
    # energy_profile.load_calgary_pool() already does to the MEUI pool.
    df = df.drop(columns=[WEIGHT], errors="ignore")
    print()
    print(f"re-raking the {len(df):,} Calgary rows to census margins "
          f"(the parquet's Alberta-frame weight is discarded):")
    df = rake_to_census_margins(df)

    df = df.dropna(subset=["Source_Energie_Chauf", "Type_Logement", "YEARBUILT", WEIGHT])

    df["Type_Batiment"] = df["Type_Logement"].map(type_batiment_map())
    assert not df["Type_Batiment"].isna().any(), "unmapped Type_Logement -> Type_Batiment"
    df["An_ConstructionCode"] = pd.cut(
        pd.to_numeric(df["YEARBUILT"], errors="coerce"),
        bins=[-np.inf] + AN_CODE_EDGES + [np.inf],
        labels=AN_CODE_LABELS, right=False,
    ).astype(str)
    df = df[df["An_ConstructionCode"] != "nan"]
    df["Chauffage_Logement"] = derive_chauffage_logement(df)
    return df


# --------------------------------------------------------------------------- #
# Stage 2: the housing_characteristics tables
#
# The BN says *which* system a home has; these tables say how efficient it is.
# Quebec's HVAC Heating Efficiency.csv puts 100% of gas forced-air homes on a
# single "Fuel Furnace, 80% AFUE" option. Calgary's audited stock is nothing
# like that: 43,719 of 73,927 homes have a condensing furnace, and the weighted
# mean is nearer 87% AFUE. Leaving it at 80% overstates gas heating for the 83%
# of dwellings that run a gas furnace.
# --------------------------------------------------------------------------- #

# The AFUE ladders Mapping.py already knows how to price (dct_HVAC_Heating).
# Nothing here invents an option label: these are existing ResStock names, and
# the ones missing from the CSV are added as new columns, never renamed.
FURNACE_AFUE_TIERS = (60.0, 68.0, 72.0, 76.0, 80.0, 85.0, 90.0, 92.5, 96.0)
BOILER_AFUE_TIERS = (72.0, 76.0, 80.0, 82.0, 85.0, 90.0, 96.0)

# Efficiency below this is a missing-data sentinel, not a furnace (EnerGuide
# writes 0; Calgary has 135 such rows and nothing at all between 0 and 50).
MIN_PLAUSIBLE_EFF = 50.0


def effective_afue(df: pd.DataFrame) -> pd.Series:
    """AFUE per home, preferring the recorded AFUE and converting the rest.

    Two fields describe the same furnace and they are not interchangeable:

      * HEATAFUE is the annual fuel utilization efficiency the option labels are
        written in -- but it is recorded for only 56% of Calgary gas homes, and
        that 56% is not a random half: 75% of condensing furnaces carry it
        against 27% of non-condensing ones. HEATAFUE alone would read the city
        as far newer than it is.
      * FURSSEFF is *steady-state* efficiency, present for 100% of them. It sits
        above AFUE because it ignores cycling and off-cycle losses.

    So: take HEATAFUE where it exists, and convert FURSSEFF where it does not,
    using the offset measured on the 41,285 homes that report both. That offset
    is estimated separately for condensing and non-condensing equipment because
    it differs between them -- a median of 1.1 pp against 2.2 pp -- and the
    non-condensing group is exactly the one a single pooled number would
    mis-correct, since it supplies most of the homes that need converting.
    """
    afue = pd.to_numeric(df["HEATAFUE"], errors="coerce")
    sse = pd.to_numeric(df["FURSSEFF"], errors="coerce")
    condensing = df["FURNACETYPE"].astype(str).str.lower().str.contains("condensing")

    have_afue = afue > MIN_PLAUSIBLE_EFF
    have_sse = sse > MIN_PLAUSIBLE_EFF
    both = have_afue & have_sse

    out = pd.Series(np.nan, index=df.index, dtype=float)
    out[have_afue] = afue[have_afue]

    for is_cond in (False, True):
        grp = condensing == is_cond
        ref = (sse - afue)[both & grp]
        # Fall back to the pooled offset if a group never reports both.
        offset = float(ref.median()) if len(ref) else float((sse - afue)[both].median())
        fill = grp & have_sse & ~have_afue
        out[fill] = sse[fill] - offset
    return out


def _nearest_tier(value: float, tiers: tuple) -> float:
    """Closest available option, ties going to the *lower* tier.

    Ties are real and common: 15,787 Calgary furnaces sit at exactly 78% steady
    state, equidistant from the 76 and 80 options. Rounding a tie down is the
    conservative choice -- it cannot manufacture efficiency the audit did not
    measure -- and it only ever moves the tie itself.
    """
    arr = np.asarray(tiers, dtype=float)
    return float(arr[np.abs(arr - value).argmin()])


def _tier_shares(eff: pd.Series, weights: np.ndarray,
                 tiers: tuple, label: str) -> dict:
    """Weighted share of homes at each AFUE tier, keyed by Option= label."""
    assigned = np.array([_nearest_tier(v, tiers) for v in eff.to_numpy(float)])
    total = weights.sum()
    shares = {}
    for t in tiers:
        s = float(weights[assigned == t].sum() / total)
        if s > 0:
            shares[f"{label}, {t:g}% AFUE"] = s
    # Renormalize away float drift so the written row sums to exactly 1.
    tot = sum(shares.values())
    return {k: v / tot for k, v in shares.items()}


def build_stage2(df: pd.DataFrame, states: dict) -> dict:
    """Heating-equipment efficiency for the two rows Calgary can actually fill.

    Only natural gas is rewritten. The Calgary audits contain 5 oil-heated and 3
    wood-heated homes; a distribution read off those would be noise wearing a
    data costume, so those rows keep their Quebec values. Gas covers ~98% of the
    city, and within gas only the two plain central systems are touched --
    forced air and hot water. Combination systems (furnace + heat pump, boiler +
    baseboard) are left alone because the audits do not say how the load splits
    between the two devices, and guessing would repeat the mistake the
    hand-typed 80%-AFUE boost made.
    """
    fuel = df["FURNACEFUEL"].astype(str)
    eff = effective_afue(df)
    ftype = df["FURNACETYPE"].astype(str).str.lower()
    # "Condensing furnace/boiler" and "Induced draft fan furnace/boil" name both;
    # they are furnaces with a boiler option, so only an unambiguous boiler counts.
    is_boiler = ftype.str.contains("boiler") & ~ftype.str.contains("furnace")

    usable = (fuel == "Natural Gas") & eff.notna() & (eff > MIN_PLAUSIBLE_EFF)
    w = df[WEIGHT].to_numpy(float)

    rows = {}
    specs = [
        ("Systeme central a air chaud", ~is_boiler, FURNACE_AFUE_TIERS, "Fuel Furnace"),
        ("Systeme central a eau chaude", is_boiler, BOILER_AFUE_TIERS, "Fuel Boiler"),
    ]
    for system_ascii, device, tiers, label in specs:
        # _match_label gives the BN its own accented spelling, so this file
        # stays ASCII and an accent drift becomes a loud KeyError here rather
        # than a silent no-op in the CSV writer.
        system = _match_label(states["Chauffage_Logement"], system_ascii)
        mask = usable & device
        n = int(mask.sum())
        if n < MIN_SUPPORT:
            print(f"  note: {system} rests on {n} audited homes "
                  f"(< {MIN_SUPPORT}) -- keeping the Quebec row")
            continue
        sub_w = w[mask.to_numpy()]
        shares = _tier_shares(eff[mask], sub_w, tiers, label)
        mean_afue = float((sub_w * eff[mask].to_numpy(float)).sum() / sub_w.sum())
        rows[f"Gaz naturel|{system}"] = {
            "where": {"Source_Energie_Chauf": "Gaz naturel",
                      "Chauffage_Logement": system},
            "shares": shares,
            "n_homes": n,
            "weighted_mean_afue": round(mean_afue, 2),
        }
        top = "; ".join(f"{k.split(', ')[1]} {v:.0%}"
                        for k, v in sorted(shares.items(), key=lambda kv: -kv[1])[:3])
        print(f"  {system:<30} n={n:>6,}  mean AFUE {mean_afue:.1f}%  ({top})")

    return {
        "HVAC Heating Efficiency.csv": {
            "rewrites": rows,
            "source": ("EnerGuide HEATAFUE where recorded, else FURSSEFF less the "
                       "measured steady-state-to-AFUE offset (1.1 pp condensing, "
                       "2.2 pp not); weighted by the Calgary-raked POND_AB"),
            "note": ("Only the natural-gas forced-air and hot-water rows are "
                     "rewritten. Oil (5 homes) and wood (3) keep Quebec, as do "
                     "all combination systems: the audits do not split the load "
                     "between a furnace and its heat pump."),
        }
    }

# --------------------------------------------------------------------------- #
# Stage 2, envelope: the three insulation tables
#
# EnerGuide records CEILINS / MAINWALLINS / FNDWALLINS as *nominal insulation*
# RSI, and the QC_R option labels are nominal insulation R too -- Mapping.py
# reads "QC_R41" as ceiling_insulation_r=41 and derives the assembly value from
# it. So the two describe the same quantity and the conversion is arithmetic
# (R = RSI x 5.678), not an assumption. Coverage is essentially complete: 73,909
# of 73,927 Calgary homes report a ceiling value, 73,871 a wall value, 71,831 a
# foundation-wall value.
# --------------------------------------------------------------------------- #

RSI_TO_R = 5.678

# table -> (EnerGuide column, the label prefix/suffix the options are written in)
INSULATION_TABLES = {
    "Insulation Ceiling.csv": "CEILINS",
    "Insulation Wall.csv": "MAINWALLINS",
    "Insulation Foundation Wall.csv": "FNDWALLINS",
}


def _table_dependencies(path: str) -> list:
    """The Dependency= columns a housing-characteristics table is keyed on.

    Read from the file rather than assumed: Insulation Ceiling and Wall are
    keyed on (Type_Logement, An_Construction) but Foundation Wall is keyed on
    An_Construction alone, and deriving on the wrong key silently produces
    rewrites that match no row.
    """
    with open(path, encoding="utf-8") as f:
        header = [c.strip() for c in f.readline().split(";")]
    deps = [h[len("Dependency="):] for h in header if h.startswith("Dependency=")]
    assert deps, f"no Dependency= columns in {os.path.basename(path)}"
    return deps


def _option_r_values(path: str) -> dict:
    """{option label -> R value} parsed out of a table's own header.

    The R number is read from the label rather than hard-coded, so the ladder
    cannot drift out of sync with the file: "QC_R24.6" -> 24.6,
    "QC_WoodStud-R20.7" -> 20.7, "QC_Wall-R17.1, interior" -> 17.1.
    """
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(";")
    out = {}
    for h in header:
        if not h.startswith("Option="):
            continue
        label = h[len("Option="):]
        m = re.search(r"R-?([0-9]+(?:\.[0-9]+)?)", label)
        if m:
            out[label] = float(m.group(1))
    assert out, f"no R-valued options found in {os.path.basename(path)}"
    return out


def build_stage2_insulation(df: pd.DataFrame, states: dict) -> dict:
    """Envelope R-values by dwelling type and vintage, from measured RSI.

    Each home is assigned the nearest R option the table already offers, then
    `derive_conditional` does the weighting, the thin-cell fallback and the
    bookkeeping -- the same machinery the heating tables use, so the two cannot
    drift apart in how a sparse cell is handled.

    One honest limit, worth knowing before reading the ceiling numbers: the QC
    ladder stops at R41 and 17.5% of Calgary ceilings measure above it (5.8%
    above R49, up to R108). Those homes are pinned to R41, so modelled ceiling
    insulation is understated for roughly one home in six, which biases heating
    energy slightly *high*. Widening the ladder means adding ResStock's generic
    R-49 / R-60 options, which Mapping.py can already price but which follow a
    different labelling family; that is a deliberate follow-up, not an oversight.
    The wall and foundation ladders have no such problem -- only 0.4% and 0.5%
    of homes sit above their top rung.
    """
    out = {}
    for fname, column in INSULATION_TABLES.items():
        path = os.path.join(HC, fname)
        by = _table_dependencies(path)
        ladder = _option_r_values(path)
        labels = list(ladder)
        r_vals = np.array([ladder[l] for l in labels], dtype=float)

        measured = pd.to_numeric(df[column], errors="coerce") * RSI_TO_R
        col = f"_R_{column}"
        # Zero means "not recorded", not "uninsulated": EnerGuide writes 0 for a
        # missing value and there is no separate sentinel. Dropping those rows
        # lets derive_conditional count support honestly.
        valid = measured > 0
        sub = df[valid].copy()
        sub[col] = [labels[int(np.abs(r_vals - v).argmin())]
                    for v in measured[valid].to_numpy(float)]

        cells, city, n_city = derive_conditional(
            sub, col, by, states, fallback_by=by[0])

        rewrites = {}
        for key, cell in cells.items():
            rewrites[key] = {
                "where": dict(zip(by, key.split("|"))),
                "shares": cell["shares"],
                "n_homes": cell["n_homes"],
                "level": cell["level"],
            }
        direct = sum(1 for c in cells.values() if c["level"] == "cell")
        mean_r = float((df.loc[valid, WEIGHT] * measured[valid]).sum()
                       / df.loc[valid, WEIGHT].sum())
        out[fname] = {
            "rewrites": rewrites,
            "source": (f"EnerGuide {column} (nominal insulation RSI) x {RSI_TO_R}, "
                       f"snapped to the table's own R ladder, Calgary-raked "
                       f"POND_AB-weighted"),
            "n_homes": int(valid.sum()),
            "weighted_mean_r": round(mean_r, 1),
        }
        print(f"  {fname:<32} n={int(valid.sum()):>6,}  mean R {mean_r:5.1f}  "
              f"{direct}/{len(cells)} cells direct")
    return out

# --------------------------------------------------------------------------- #
# Stage 2, windows: glazing count only, and deliberately only that
#
# EnerGuide stores windows as a HOT2000 WINDOWCODE -- 1,034 distinct 6-digit
# codes across Calgary, present on 66% of homes. The first digit is the number
# of glazings and decodes cleanly (2 = double 86%, 3 = triple 11%, 1 = single
# 2%, 4 = quad 1%), which is both the largest driver of window heat loss and the
# leading field of every option label in Windows.csv.
#
# The remaining digits encode coating, fill gas, spacer and frame. The repo has
# no HOT2000 codebook, so decoding them would mean guessing -- and a guess
# dressed as a derivation is precisely what the hand-typed 80%-AFUE boost was.
# So this pins the glazing-count *margin* per (type, vintage) and leaves
# Quebec's split within each glazing count untouched. That is the plan's Tier-B
# method: keep the conditional structure, move the margin onto Alberta.
# --------------------------------------------------------------------------- #

GLAZING_BY_LEADING_DIGIT = {"1": "Single", "2": "Double", "3": "Triple", "4": "Triple"}


def _glazing_group(option_label: str) -> str:
    """Which glazing group an Option= label belongs to, read off the label.

    Every label in Windows.csv starts with the glazing count ("Double, Low-E,
    Non-metal, Air, L-Gain"), so the grouping comes from the file rather than
    from a mapping this file would have to keep in sync.
    """
    return option_label.split(",")[0].strip()


def build_stage2_windows(df: pd.DataFrame, states: dict) -> dict:
    """Glazing-count margins by dwelling type and vintage.

    Quad-glazed homes (0.8%) are folded into Triple: Windows.csv has no quad
    option, and inventing one would change the schema for a rounding error.
    """
    path = os.path.join(HC, "Windows.csv")
    by = _table_dependencies(path)

    code = (df["WINDOWCODE"].astype("string").str.strip()
            .str.replace(r"\.0$", "", regex=True))
    usable = code.str.fullmatch(r"\d{6}").fillna(False)
    col = "_Glazing"
    sub = df[usable].copy()
    sub[col] = code[usable].str[0].map(GLAZING_BY_LEADING_DIGIT)
    sub = sub[sub[col].notna()]

    cells, city, n_city = derive_conditional(
        sub, col, by, states, fallback_by=by[0])

    rewrites = {}
    for key, cell in cells.items():
        rewrites[key] = {
            "where": dict(zip(by, key.split("|"))),
            "group_shares": cell["shares"],
            "n_homes": cell["n_homes"],
            "level": cell["level"],
        }
    direct = sum(1 for c in cells.values() if c["level"] == "cell")
    print(f"  {'Windows.csv':<32} n={len(sub):>6,}  "
          f"{'; '.join(f'{k} {v:.0%}' for k, v in sorted(city.items(), key=lambda kv: -kv[1]))}  "
          f"{direct}/{len(cells)} cells direct")

    return {
        "Windows.csv": {
            "rewrites": rewrites,
            "grouped_by": "glazing count (first field of the option label)",
            "source": ("EnerGuide WINDOWCODE leading digit (HOT2000 glazing "
                       "count), Calgary-raked POND_AB-weighted; 66% of homes "
                       "carry a well-formed code"),
            "note": ("Only the glazing-count margin is Calgary. Coating, fill "
                     "gas, spacer and frame keep their Quebec proportions "
                     "within each glazing count -- the remaining WINDOWCODE "
                     "digits need a HOT2000 codebook the repo does not have."),
        }
    }

# --------------------------------------------------------------------------- #
# Stage 2, setpoints: NOT derived, and the reason is not lack of effort
#
# ALBERTA_RECALIBRATION_PLAN.md 3.2 grades ModeConsigne / Heating Setpoint as
# Tier A/B on the premise that "EnerGuide TMAIN & ThermostatHeatingNighttime
# give (day, night) pairs". Measured on the Calgary extract, that premise is
# false. Those fields carry no occupant behaviour at all:
#
#     TMAIN                       21.0 C for 99.65% of homes (5 distinct values)
#     ThermostatHeatingNighttime  18.0 C for 100%  (ONE distinct value)
#     ThermostatCooling           25.0 C for 100%  (ONE distinct value)
#
# They are HOT2000 modelling defaults. An energy auditor rates the building, not
# the household -- nobody recorded what temperature these families actually
# keep, so the software substituted a standard operating condition.
#
# Deriving setpoints from them would replace Quebec's distribution -- which
# comes from the Hydro-Quebec "Sondage Sensibilisation integree", an actual
# behavioural survey spread over 677 (day, evening, night) triples -- with a
# degenerate spike at (21, 21, 18). That is not a re-calibration; it is throwing
# away the only behavioural evidence in the model and calling the result
# Calgary. Quebec setpoints are a weak assumption for Calgary. A constant is a
# worse one.
#
# What would actually fill this: the Households and the Environment Survey
# (StatCan 38-10-0019/0020/0026) publishes Alberta thermostat-setback shares,
# and PROGSMARTTHERMOSTAT (56% coverage here) could corroborate the programmable
# share -- but neither is in the repo, and neither yields the full triple. Until
# one is fetched, ModeConsigne.csv, Heating Setpoint.csv, Cooling Setpoint.csv
# and the Basement/Garage variants stay Quebec, and PROVENANCE records them as
# such.
# --------------------------------------------------------------------------- #

SETPOINT_TABLES_NOT_DERIVED = {
    "ModeConsigne.csv": "EnerGuide records no occupant setpoint (TMAIN is a HOT2000 default)",
    "Heating Setpoint.csv": "same -- ThermostatHeatingNighttime is 18.0 C for 100% of homes",
    "Cooling Setpoint.csv": "same -- ThermostatCooling is 25.0 C for 100% of homes",
}

def build(save: bool = True) -> dict:
    df = load_calgary()
    print(f"Calgary homes with a usable heating record: {len(df):,}")

    valid = valid_systems_by_fuel()

    states = bn_states(["Type_Batiment", "An_ConstructionCode", "Type_Logement",
                        "Source_Energie_Chauf", "Chauffage_Logement",
                        "An_Construction", "Mode_Occupation", "Nombre_Etages",
                        "Superficie_Totale", "Nombre_Personnes",
                        "Climatisation", "ChaufEau_Presence",
                        "ChaufEau_ChaufType", "ChaufEau_Type", "Presence_SousSol",
                        "Infiltration"])

    # Fuel: building type dominates, so thin age cells broaden over age.
    fuel_tbl, fuel_city, _ = derive_conditional(
        df, "Source_Energie_Chauf", ["Type_Batiment", "An_ConstructionCode"],
        states, fallback_by="Type_Batiment")
    # Equipment: fuel dominates, so thin cells broaden over dwelling type.
    system_tbl, system_city, _ = derive_conditional(
        df, "Chauffage_Logement", ["Type_Logement", "Source_Energie_Chauf"],
        states, fallback_by="Source_Energie_Chauf",
        allowed_for=lambda k: valid.get(k["Source_Energie_Chauf"], set()))

    expected_fuel = len(states["Type_Batiment"]) * len(states["An_ConstructionCode"])
    expected_sys = len(states["Type_Logement"]) * len(states["Source_Energie_Chauf"])
    assert len(fuel_tbl) == expected_fuel, f"{len(fuel_tbl)} != {expected_fuel} fuel cells"
    assert len(system_tbl) == expected_sys, f"{len(system_tbl)} != {expected_sys} system cells"

    # Every BN state must appear, including the ones Alberta never uses, so the
    # network keeps its full vocabulary (Bi-energie stays a state at probability 0).
    for cell in fuel_tbl.values():
        cell["shares"].setdefault("Bi-energie", 0.0)

    print("\n=== Which fuel, by building type and age "
          "(census-weighted; homes behind each) ===")
    for key, cell in sorted(fuel_tbl.items()):
        gas = cell["shares"].get("Gaz naturel", 0.0)
        el = cell["shares"].get("Electricite", 0.0)
        note = "" if cell["level"] == "cell" else f"  <- {cell['level']}"
        print(f"  {key:<34} n={cell['n_homes']:>6,}   gas {gas:6.1%}  "
              f"elec {el:6.1%}{note}")
    print(f"  {'CITY-WIDE':<34} n={len(df):>6,}   "
          f"gas {fuel_city.get('Gaz naturel', 0):6.1%}  "
          f"elec {fuel_city.get('Electricite', 0):6.1%}")

    print("\n=== Which equipment, by home type and fuel ===")
    for key, cell in sorted(system_tbl.items()):
        top = sorted(cell["shares"].items(), key=lambda kv: -kv[1])[:2]
        shown = "; ".join(f"{k} {v:.0%}" for k, v in top)
        note = "" if cell["level"] == "cell" else f"  <- {cell['level']}"
        drop = (f"  [{cell['reassigned_weight']:.1%} reassigned]"
                if cell["reassigned_weight"] > 0.001 else "")
        print(f"  {key:<48} n={cell['n_homes']:>6,}  {shown}{note}{drop}")

    # ---- what the reader has to be told before quoting any of this ---------- #
    print("\n=== how much evidence sits under each building type ===")
    thin = []
    for bat, grp in df.groupby("Type_Batiment", observed=True):
        share_of_stock = grp[WEIGHT].sum() / df[WEIGHT].sum()
        print(f"  {bat:<12} {len(grp):>6,} audited homes  ->  weighted to "
              f"{share_of_stock:5.1%} of Calgary")
        if len(grp) < 500:
            thin.append((bat, len(grp), share_of_stock))
    for bat, n, share in thin:
        print(f"  WARNING {bat}: {share:.0%} of Calgary's homes are described by only "
              f"{n} audited ones. Raking fixes HOW MANY {bat.lower()} homes there "
              f"are, not WHICH ones got audited -- their fuel mix is the least "
              f"reliable number here and is biased toward gas.")

    gas = fuel_city.get("Gaz naturel", 0.0)
    print(f"\n  city-wide gas share: {gas:.1%} (weighted) vs "
          f"{(df['Source_Energie_Chauf'] == 'Gaz naturel').mean():.1%} raw. "
          f"Hand-typed anchor was 85%.")
    if not 0.88 <= gas <= 0.99:
        print("  WARNING: outside the plausible 88-99% band for Calgary -- check upstream.")
    elif gas > 0.965:
        print("  NOTE: high end of plausible. Alberta-wide figures put natural-gas "
              "space heating nearer 93-96%; the excess is the apartment scarcity above.")

    stock = build_stock(df, states)
    print_stock(stock)
    enduse = build_enduse(df, states)
    print()
    print("=== Equipment efficiency (Stage 2: housing_characteristics) ===")
    stage2 = build_stage2(df, states)
    stage2.update(build_stage2_insulation(df, states))
    stage2.update(build_stage2_windows(df, states))
    print_enduse(enduse)

    payload = {
        "source": os.path.relpath(STOCK, PROJECT_DIR).replace("\\", "/"),
        "caveats": {
            "thin_building_types": [
                {"type": b, "n_audited": n, "weighted_share": round(s, 4)}
                for b, n, s in thin
            ],
            "city_wide_gas_share": round(gas, 4),
            "note": ("Gas share is biased high: apartments are 27% of Calgary but "
                     "only 121 were audited, and audited apartments skew gas-heated. "
                     "Raking corrects how many apartments there are, not which ones "
                     "entered the sample."),
        },
        "n_calgary_homes": int(len(df)),
        "min_support": MIN_SUPPORT,
        "weight_column": WEIGHT,
        "Source_Energie_Chauf": {
            "parents": ["Type_Batiment", "An_ConstructionCode"],
            "city_wide": fuel_city,
            "cells": fuel_tbl,
        },
        "Chauffage_Logement": {
            "parents": ["Type_Logement", "Source_Energie_Chauf"],
            "city_wide": system_city,
            "cells": system_tbl,
        },
        "stock": stock,
        "enduse": enduse,
        "stage2": stage2,
        "stage2_not_derived": SETPOINT_TABLES_NOT_DERIVED,
    }
    if save:
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"\nWrote {os.path.relpath(OUT_JSON, PROJECT_DIR)}")
    return payload


if __name__ == "__main__":
    build()
