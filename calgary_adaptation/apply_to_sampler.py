"""
apply_to_sampler.py -- apply the Calgary re-calibration to the sampler and
generate / validate the SimParc input CSVs. Combines four former scripts, each a
sub-command:

    bn        rewrite the heating-fuel + heating-system odds AND the housing-mix
              nodes they are averaged over (dwelling type, vintage, tenure,
              storeys, floor area) in the Bayesian network ->
              data/processed/bayesian_network/BN_Calgary.XDSL
              (non-destructive; the Quebec BN_EUEMr.XDSL is left untouched)
    cpt       reweight one ResStock-style detail table (a ;-separated CPT CSV in
              data/processed/housing_characteristics/) while preserving its header
              grammar (demo boosts the 80%-AFUE gas furnace in the gas rows)
    batch     run the sampler (BN_Calgary.XDSL when `bn` has built it, else the
              Quebec BN with a loud warning) -> building-input.csv (97
              human-readable columns), building-mapping.csv (~219 HPXML args),
              building-test.csv (the two concatenated), for 1000 dwellings,
              plus building-input.provenance.json recording exactly which
              probability files produced them
    validate  two independent groups of assertions:
              (a) plumbing  -- Calgary weather file, UTC -7, daylight saving on,
                  zero 'Bi-energie'. These are hardcoded in Mapping.py and pass
                  regardless of which BN was used, so they prove nothing about
                  the re-calibration.
              (b) calibration -- the drawn heating-fuel and heating-system shares
                  match the Calgary targets below within Monte-Carlo tolerance,
                  and the fuel propagated into the HPXML args. Only (b) can tell
                  a Calgary run from a Quebec one.

Usage (from repo root):
    uv run python calgary_adaptation/apply_to_sampler.py [bn|cpt|batch|validate|all]
`all` runs bn -> cpt -> batch -> validate. (batch is the heavy step.)
"""

import collections
import datetime as _dt
import hashlib
import itertools
import json
import math
import os
import shutil
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

BN_DIR = os.path.join(PROJECT_DIR, "data", "processed", "bayesian_network")
BN_IN = os.path.join(BN_DIR, "BN_EUEMr.XDSL")
BN_OUT = os.path.join(BN_DIR, "BN_Calgary.XDSL")
OUT = os.path.join(PROJECT_DIR, "data", "output")
HC = os.path.join(PROJECT_DIR, "data", "processed", "housing_characteristics")
CALGARY_EPW = "CAN_AB_Calgary.Intl.AP.718770_CWEC2016.epw"
N_DWELLINGS = 1000


# --------------------------------------------------------------------------- #
# bn: rewrite the fuel + heating-system CPTs -> BN_Calgary.XDSL
#
# The numbers come from data/output/calgary_bn_targets.json, produced by
# derive_targets.py out of 73,927 census-weighted Calgary audits, conditioned on
# exactly the parents the BN uses:
#     Source_Energie_Chauf | Type_Batiment, An_ConstructionCode
#     Chauffage_Logement   | Type_Logement, Source_Energie_Chauf
# The dicts below are no longer what gets applied -- they are kept as a SANITY
# ANCHOR. If the derived answer drifts far from them, something broke upstream.
# Keys MUST be exact BN state labels (accents included) or KeyError.
# --------------------------------------------------------------------------- #

TARGETS_JSON = os.path.join(OUT, "calgary_bn_targets.json")

# Anchor only -- the hand-typed estimates this work replaced.
SOURCE_ENERGIE_CHAUF = {
    "Gaz naturel": 0.85,   # hand-typed guess; the audits say ~98%
    "Electricite": 0.10,
    "Bois":        0.03,
    "Mazout":      0.02,
    "Bi-energie":  0.00,   # Hydro-Quebec-only tariff -> impossible in Alberta
}
ANCHOR_TOLERANCE = 0.15    # flag, do not fail, if derived gas is >15pp off anchor
# Chauffage_Logement: 20 system combos. Chauffage_Logement is a CHILD of
# Source_Energie_Chauf, so its targets must be conditional on the drawn fuel --
# an unconditional override produces incoherent pairs like
# (Gaz naturel, Plinthes electriques), and the downstream tables have no row for
# those, so the sampler dies with "Error in sampling for attribute". Each fuel
# below therefore spreads a full 1.0 over ONLY the systems that fuel supports in
# housing_characteristics/HVAC Heating Efficiency.csv. `check_coverage()`
# enforces this against the actual CSVs rather than trusting this comment.
# Anchor only -- superseded by the derived, per-dwelling-type numbers.
CHAUFFAGE_LOGEMENT_BY_FUEL = {
    # Calgary gas homes: forced-air furnace almost exclusively.
    "Gaz naturel": {
        "Système central à air chaud":     0.92,
        "Système central à eau chaude":    0.04,
        "Fournaise murale ou de plancher": 0.04,
    },
    # The electrically-heated minority: baseboards, with some heat pumps.
    "Electricite": {
        "Plinthes électriques":                        0.60,
        "Thermopompe murale":                          0.10,
        "Thermopompe murale et Plinthes électriques":  0.10,
        "Thermopompe et Système central à air chaud":  0.08,
        "Unités convecteurs, plancher ou plafond radiant": 0.07,
        "Système central à air chaud":                 0.05,
    },
    "Bois": {
        "Fournaise ou poêle à bois":                          0.40,
        "Fournaise ou poêle à bois et Plinthes électriques":  0.25,
        "Fournaise ou poêle à bois et Système central à air chaud": 0.25,
        "Fournaise ou poêle à bois et Fournaise murale ou de plancher": 0.10,
    },
    "Mazout": {
        "Système central à air chaud":     0.70,
        "Système central à eau chaude":    0.25,
        "Fournaise murale ou de plancher": 0.05,
    },
    # Never drawn (fuel probability 0), but the slice must stay coherent.
    "Bi-energie": {
        "Système central à air chaud": 1.00,
    },
}


def _retarget(labels, current, targets):
    """Probability vector (label order) with `targets` pinned and the remaining
    mass spread over the other labels in proportion to their current weights."""
    fixed = sum(targets.values())
    if not (0.0 <= fixed <= 1.0 + 1e-9):
        raise ValueError(f"target weights must sum to <= 1.0, got {fixed}")
    remaining = max(0.0, 1.0 - fixed)
    free = [l for l in labels if l not in targets]
    free_mass = sum(current[labels.index(l)] for l in free)
    vec = []
    for l in labels:
        if l in targets:
            vec.append(float(targets[l]))
        elif free_mass > 0:
            vec.append(current[labels.index(l)] / free_mass * remaining)
        else:
            vec.append(remaining / len(free) if free else 0.0)
    s = sum(vec)
    return [v / s for v in vec]


def force_node(bn, node, targets):
    """Overwrite every parent-conditioned distribution of `node` with the Calgary
    target, preserving the relative structure of the non-targeted states.

    `targets` is either a {state: weight} dict applied to every parent slice, or
    a callable(parent_instantiation_dict) -> {state: weight} when the target has
    to depend on the parents (as Chauffage_Logement's does on the drawn fuel)."""
    var = bn.variable(node)
    labels = list(var.labels())

    def _validate(t):
        for lbl in t:
            if lbl not in labels:
                raise KeyError(f"'{lbl}' is not a state of '{node}'. States: {labels}")
        return t

    if not callable(targets):
        _validate(targets)
    cpt = bn.cpt(node)
    parents = [n for n in cpt.names if n != node]
    if not parents:
        if callable(targets):
            raise ValueError(f"'{node}' has no parents; pass a plain dict")
        cpt[:] = _retarget(labels, list(cpt.toarray()), targets)
        return 1
    parent_label_lists = [list(bn.variable(p).labels()) for p in parents]
    n = 0
    for combo in itertools.product(*parent_label_lists):
        inst = {p: lbl for p, lbl in zip(parents, combo)}
        t = _validate(targets(inst)) if callable(targets) else targets
        cpt[inst] = _retarget(labels, list(cpt[inst]), t)
        n += 1
    return n


def load_targets():
    """The derived per-parent-cell targets, or None if they were never built."""
    if not os.path.exists(TARGETS_JSON):
        return None
    with open(TARGETS_JSON, encoding="utf-8") as f:
        return json.load(f)


def _cell_lookup(node_block):
    """A callable(parent_instantiation) -> {state: weight} for force_node.

    Fails loudly on a parent combination the derivation did not cover: a silent
    fallback here would quietly reinstate a flat, unconditional number, which is
    exactly what this work removed."""
    parents = node_block["parents"]
    cells = node_block["cells"]

    def lookup(inst):
        key = "|".join(str(inst[p]) for p in parents)
        cell = cells.get(key)
        if cell is None:
            raise KeyError(
                f"no derived target for {key!r} (parents {parents}). "
                f"Re-run: uv run python calgary_adaptation/derive_targets.py")
        return cell["shares"]
    return lookup


# Every node this pipeline re-calibrates, in the order it is applied. The
# deterministic children (Type_Batiment, An_ConstructionCode) are deliberately
# absent: they collapse their parents and must be left alone.
STOCK_NODES = ("Type_Logement", "An_Construction", "Mode_Occupation",
               "Nombre_Etages", "Superficie_Totale", "Nombre_Personnes")
ENDUSE_NODES = ("Climatisation", "ChaufEau_ChaufType", "ChaufEau_Type",
                "Presence_SousSol", "Infiltration")
CALIBRATED_NODES = (("Source_Energie_Chauf", "Chauffage_Logement")
                    + STOCK_NODES + ENDUSE_NODES)


def expected_marginals(bn_path=None, nodes=CALIBRATED_NODES):
    """What the network itself says each node's overall share should be.

    Computed by exact inference over the whole network rather than multiplying
    the target dicts by hand -- the parents have their own distributions, so the
    hand calculation was only right while the targets were flat."""
    import pyagrum as gum
    bn = gum.loadBN(bn_path or default_bn())
    ie = gum.LazyPropagation(bn)
    ie.makeInference()
    out = {}
    for n in nodes:
        post = ie.posterior(n)
        out[n] = {lbl: float(post[{n: lbl}]) for lbl in bn.variable(n).labels()}
    return out


def rake_node_marginal(bn, node, target, rounds=50, tol=1e-6):
    """Move a node's *marginal* onto `target` without inventing a joint.

    Superficie_Totale hangs off Nombre_Pieces and EnerGuide records no room
    count, so there is no observed P(area | rooms) to write. Rewriting the CPT
    would mean fabricating that relationship. Instead scale each area state by
    target/current across every parent slice and renormalize: Quebec's
    room-to-size shape survives, Calgary's sizes win. Iterated because
    renormalizing each slice perturbs the marginal it was meant to fix.

    Returns the residual max error so the caller can report it rather than
    quietly accept a bad fit."""
    import pyagrum as gum
    labels = list(bn.variable(node).labels())
    tgt = np.array([target.get(l, 0.0) for l in labels], dtype=float)
    assert tgt.sum() > 0, f"empty target for {node}"
    tgt /= tgt.sum()

    cpt = bn.cpt(node)
    parents = [n for n in cpt.names if n != node]
    parent_label_lists = [list(bn.variable(p).labels()) for p in parents]

    err = float("inf")
    for _ in range(rounds):
        ie = gum.LazyPropagation(bn)
        ie.makeInference()
        cur = np.array([float(ie.posterior(node)[{node: l}]) for l in labels])
        err = float(np.abs(cur - tgt).max())
        if err < tol:
            break
        # A state the Quebec CPT gives zero everywhere cannot be lifted by
        # scaling; report it rather than dividing by zero.
        stuck = [l for l, c, t in zip(labels, cur, tgt) if c <= 0 and t > 0]
        if stuck:
            print(f"  NOTE: {node} states unreachable from the Quebec CPT "
                  f"(zero in every slice), target dropped: {stuck}")
        scale = np.divide(tgt, cur, out=np.zeros_like(tgt), where=cur > 0)
        for combo in itertools.product(*parent_label_lists):
            inst = {p: lbl for p, lbl in zip(parents, combo)}
            v = np.array(list(cpt[inst]), dtype=float) * scale
            s = v.sum()
            cpt[inst] = (v / s) if s > 0 else tgt
    return err


def apply_stock(bn, stock):
    """Pin the housing mix the heating odds get averaged over.

    Only the free nodes are touched. Type_Batiment | Type_Logement and
    An_ConstructionCode | An_Construction are deterministic collapses -- they
    inherit the new mix on their own, and overwriting them would break the
    identity the fuel targets are keyed on."""
    applied = []
    for node in ("An_Construction", "Mode_Occupation", "Nombre_Etages"):
        n = force_node(bn, node, _cell_lookup(stock[node]))
        applied.append(f"{node} ({n} rows, by {' x '.join(stock[node]['parents'])})")
    n = force_node(bn, "Type_Logement", stock["Type_Logement"]["shares"])
    applied.append(f"Type_Logement ({n} row, census marginal)")

    err = rake_node_marginal(bn, "Superficie_Totale",
                             stock["Superficie_Totale"]["shares"])
    applied.append(f"Superficie_Totale (marginal raked, residual {err:.2e})")

    # Same treatment, same reason: Nombre_Personnes hangs off Nombre_Pieces and
    # nothing in the census or the audits crosses household size with room
    # count, so only the marginal moves. Quebec keeps the rooms-to-people shape.
    if "Nombre_Personnes" in stock:
        err_p = rake_node_marginal(bn, "Nombre_Personnes",
                                   stock["Nombre_Personnes"]["shares"])
        applied.append(f"Nombre_Personnes (census marginal raked, "
                       f"residual {err_p:.2e})")
    return applied


def apply_enduse(bn, enduse):
    """Pin the end uses that housing mix gets multiplied by: cooling, water-heater
    fuel and size, basement, airtightness.

    Every one is a plain force_node over a derived cell table. The slices that
    have to keep their Quebec values -- heat-pump heating for Climatisation, and
    "no water heater" for the two ChaufEau_* nodes -- arrive from derive_targets
    with empty shares, which makes _retarget an identity. Keeping that decision in
    the data means there is no special case to forget about here."""
    applied = []
    for node in ENDUSE_NODES:
        block = enduse[node]
        n = force_node(bn, node, _cell_lookup(block))
        kept = sum(1 for c in block["cells"].values() if not c["shares"])
        note = f", {kept} Quebec row(s) kept" if kept else ""
        applied.append(
            f"{node} ({n} rows, by {' x '.join(block['parents'])}{note})")
    return applied


def make_bn():
    import pyagrum as gum
    targets = load_targets()
    assert targets is not None, (
        f"{os.path.relpath(TARGETS_JSON, PROJECT_DIR)} missing -- run "
        f"`uv run python calgary_adaptation/derive_targets.py` first.")

    bn = gum.loadBN(BN_IN)
    n1 = force_node(bn, "Source_Energie_Chauf",
                    _cell_lookup(targets["Source_Energie_Chauf"]))
    n2 = force_node(bn, "Chauffage_Logement",
                    _cell_lookup(targets["Chauffage_Logement"]))

    # The housing mix has to be pinned too, or Calgary's conditional heating odds
    # get integrated over Quebec's building stock.
    stock = targets.get("stock")
    assert stock is not None, (
        "no 'stock' block in the targets file -- re-run "
        "`uv run python calgary_adaptation/derive_targets.py`")
    applied = apply_stock(bn, stock)

    # The end uses that mix drives. Without these the network still cools
    # half of Calgary that has no air conditioner and runs a quarter of its
    # water heating on electricity that actually burns gas.
    enduse = targets.get("enduse")
    assert enduse is not None, (
        "no 'enduse' block in the targets file -- re-run "
        "`uv run python calgary_adaptation/derive_targets.py`")
    applied_enduse = apply_enduse(bn, enduse)

    gum.saveBN(bn, BN_OUT)

    src = targets["Source_Energie_Chauf"]
    print(f"Source_Energie_Chauf : rewrote {n1} rows from {targets['n_calgary_homes']:,} "
          f"audited homes, by {' x '.join(src['parents'])}")
    print(f"Chauffage_Logement   : rewrote {n2} rows, by "
          f"{' x '.join(targets['Chauffage_Logement']['parents'])}")
    print("housing stock        : " + "\n                       ".join(applied))
    print("end uses             : " + "\n                       ".join(applied_enduse))

    marg = expected_marginals(BN_OUT)
    print("\n  resulting city-wide shares (exact, from the network):")
    for node in CALIBRATED_NODES:
        for lbl, p in sorted(marg[node].items(), key=lambda kv: -kv[1]):
            if p >= 0.005:
                print(f"    {node:<22} {p:6.1%}  {lbl}")

    gas = marg["Source_Energie_Chauf"].get("Gaz naturel", 0.0)
    anchor = SOURCE_ENERGIE_CHAUF["Gaz naturel"]
    if abs(gas - anchor) > ANCHOR_TOLERANCE:
        print(f"\n  NOTE: derived gas share {gas:.1%} is {abs(gas - anchor):.0%}pp from "
              f"the {anchor:.0%} hand-typed anchor. Expected -- the anchor was a "
              f"guess. See the caveats in {os.path.basename(TARGETS_JSON)}: apartments "
              f"are 27% of Calgary but only 121 were audited, so gas is biased high.")
    print(f"\nSaved: {BN_OUT}")
    # Derived from the network rather than typed out, so this line cannot go
    # stale the way it did when Nombre_Personnes was calibrated but still
    # listed here as Quebec.
    structural = {"Territoire_HQ", "Region_Administrative",      # single-state
                  "Type_Batiment", "An_ConstructionCode"}        # deterministic
    still_qc = sorted(set(bn.names()) - set(CALIBRATED_NODES) - structural)
    print(f"NOTE: {len(CALIBRATED_NODES)} of {len(bn.names())} nodes are Calgary "
          f"(+2 deterministic children that inherit it, +2 single-state "
          f"geography). Still Quebec ({len(still_qc)}): "
          f"{', '.join(still_qc)}.")
    print("      Why each is still Quebec is recorded in PROVENANCE.md; the "
          "short version is that pools, spas, appliances, garages and EVs have "
          "no Calgary source in this repo, Nombre_Pieces is a room count "
          "EnerGuide never records, and ChaufEau_Presence cannot be separated "
          "from a building-central water heater.")


# --------------------------------------------------------------------------- #
# preflight: does every combination the BN can draw have a row downstream?
# --------------------------------------------------------------------------- #

# Fuels that arrive as combustion at the dwelling. Bi-energie is dual by
# definition (Hydro-Quebec tariff: electric + fuel backup) so it is exempt from
# both directions of the test; its probability is 0 in Alberta anyway.
COMBUSTION_FUELS = ("Gaz naturel", "Mazout", "Bois")

# Three (fuel, system, option) triples in the untouched Quebec table put a
# `Fuel Boiler` in an *electrically*-heated home. They come with the Quebec
# model, not with this re-calibration: the state is literally "central hot
# water", and Quebec priced that as a boiler regardless of the drawn fuel. The
# Calgary network gives the system ~4e-18 probability, so nothing is ever drawn
# through them. They are listed rather than silently tolerated -- anything NOT
# on this list is a defect this pipeline introduced.
KNOWN_INCOHERENT = {
    ("Electricite", "Thermopompe et Système central à eau chaude",
     "Fuel Boiler, 72% AFUE & ASHP, SEER 10, 6.2 HSPF"),
    ("Electricite", "Thermopompe et Système central à eau chaude",
     "Fuel Boiler, 72% AFUE & ASHP, SEER 13, 7.7 HSPF"),
    ("Electricite", "Thermopompe et Système central à eau chaude",
     "Fuel Boiler, 72% AFUE & ASHP, SEER 15, 8.5 HSPF"),
}


def _burns_fuel(option):
    """Does this equipment option combust anything? ResStock names every
    combustion device `Fuel <something>`; combinations join with ' & '."""
    return any(part.strip().startswith("Fuel ") for part in option.split("&"))


def check_fuel_coherence(path=None):
    """Every non-zero equipment option must be able to burn the row's fuel.

    A static check on the table itself -- no sampling, no BN. It exists because
    the reweighter can silently create impossible dwellings: renormalizing a row
    whose free options are all zero spreads mass uniformly over *every* other
    option, which is how 8.1% of the shipped gas homes ended up with electric
    baseboards and geothermal heat pumps. `check_coverage` cannot see that: the
    dependency row still exists and still sums to 1.0. This can."""
    path = path or os.path.join(HC, "HVAC Heating Efficiency.csv")
    t = pd.read_csv(path, sep=SEP)
    opts = [c for c in t.columns if c.startswith("Option=")]

    problems = []
    for _, row in t.iterrows():
        fuel = str(row["Dependency=Source_Energie_Chauf"]).strip()
        system = str(row["Dependency=Chauffage_Logement"]).strip()
        for col in opts:
            raw = str(row[col]).strip()
            if raw in ("", "nan") or float(raw) <= 0:
                continue
            option = col[len("Option="):]
            fuelled = _burns_fuel(option)
            if fuel == "Electricite" and fuelled:
                why = "electrically-heated home given combustion equipment"
            elif fuel in COMBUSTION_FUELS and not fuelled:
                why = f"{fuel}-heated home given equipment that burns nothing"
            else:
                continue
            if (fuel, system, option) in KNOWN_INCOHERENT:
                continue
            problems.append((fuel, system, option, float(raw), why))

    if problems:
        lines = "\n".join(
            f"    {f} + {sy!r} -> {o!r} at p={w:.4f}  ({why})"
            for f, sy, o, w, why in problems[:15])
        raise AssertionError(
            f"{len(problems)} physically incoherent (fuel, equipment) pair(s) in "
            f"{os.path.basename(path)} -- a rewrite has put equipment in homes that "
            f"cannot run it:\n{lines}"
            + (f"\n    ... and {len(problems) - 15} more" if len(problems) > 15 else ""))
    print(f"  coherence OK: every non-zero equipment option in "
          f"{os.path.basename(path)} can burn its row's fuel "
          f"({len(KNOWN_INCOHERENT)} known Quebec-inherited exception(s) skipped).")


def check_coverage(bn_path=None, n=20000):
    """Draw from the BN alone (seconds) and confirm every dependency combination
    it produces has a usable row in each housing_characteristics table.

    resstock_args_sampling raises a bare "Error in sampling for attribute: X"
    when a drawn combination matches no row (or only all-zero rows) -- minutes
    into `batch`, with no indication of which combination. Re-calibrating a
    parent node without its children silently creates such combinations. This
    reports them up front, by name."""
    from src.utils.sampler.Sampler import Sampler
    check_fuel_coherence()
    bn_path = bn_path or default_bn()
    df = Sampler(bn_path).GUM_Sampling(n, evs={})

    problems, skipped = [], []
    for fname in sorted(f for f in os.listdir(HC) if f.endswith(".csv")):
        t = pd.read_csv(os.path.join(HC, fname), sep=SEP)
        dep_cols = [c for c in t.columns if c.startswith("Dependency=")]
        deps = [c[len("Dependency="):] for c in dep_cols]
        opts = [c for c in t.columns if c.startswith("Option=")]
        if not deps:
            continue
        if not set(deps) <= set(df.columns):
            # depends on ResStock-sampled attributes too; not checkable from BN draws
            skipped.append(fname)
            continue
        have = set(map(tuple, t[dep_cols].astype(str).values))
        dead = set(map(tuple, t.loc[t[opts].sum(axis=1) <= 0, dep_cols].astype(str).values))
        for combo in map(tuple, df[deps].astype(str).drop_duplicates().values):
            if combo not in have:
                problems.append((fname, dict(zip(deps, combo)), "no matching row"))
            elif combo in dead:
                problems.append((fname, dict(zip(deps, combo)), "row sums to zero"))

    if problems:
        lines = "\n".join(f"    {f}: {why} for {combo}" for f, combo, why in problems[:15])
        raise AssertionError(
            f"{len(problems)} unreachable combination(s) drawn by "
            f"{os.path.basename(bn_path)} -- `batch` would crash:\n{lines}"
            + (f"\n    ... and {len(problems) - 15} more" if len(problems) > 15 else ""))
    print(f"  coverage  OK: {n:,} BN draws, every dependency combination has a "
          f"usable row ({len(skipped)} table(s) skipped: depend on ResStock attrs).")


# --------------------------------------------------------------------------- #
# cpt: grammar-preserving reweighter for the housing_characteristics CSVs
# --------------------------------------------------------------------------- #

SEP = ";"


def reweight_cpt(path, boosts, where=None, backup=True, encoding="utf-8"):
    """Rewrite only `Option=` cells of a ;-separated CPT CSV (optionally only rows
    matching `where={dependency: value}`), renormalizing each changed row to 1.0.
    Preserves the header + non-Option columns byte-for-byte; writes a one-time
    .bak. `boosts` = {option_value: target_weight}, summing to [0, 1]."""
    where = where or {}
    with open(path, encoding=encoding) as f:
        lines = f.read().splitlines()
    header = lines[0].split(SEP)
    opt_idx = {h[len("Option="):]: i for i, h in enumerate(header) if h.startswith("Option=")}
    dep_idx = {h[len("Dependency="):]: i for i, h in enumerate(header) if h.startswith("Dependency=")}
    for opt in boosts:
        if opt not in opt_idx:
            raise KeyError(f"Option '{opt}' not found in {os.path.basename(path)}.\n"
                           f"Available options: {list(opt_idx)}")
    for dep in where:
        if dep not in dep_idx:
            raise KeyError(f"Dependency '{dep}' not found in {os.path.basename(path)}.\n"
                           f"Available dependencies: {list(dep_idx)}")
    target_sum = sum(boosts.values())
    if not (0.0 <= target_sum <= 1.0):
        raise ValueError(f"Sum of boost weights must be in [0, 1]; got {target_sum}")

    out = [lines[0]]
    n_changed = 0
    for line in lines[1:]:
        if not line.strip():
            out.append(line)
            continue
        cells = line.split(SEP)
        if any(cells[dep_idx[d]].strip() != v for d, v in where.items()):
            out.append(line)
            continue
        cur = {}
        for opt, i in opt_idx.items():
            c = cells[i].strip()
            cur[opt] = float(c) if c not in ("", "nan") else 0.0
        free = [o for o in opt_idx if o not in boosts]
        free_mass = sum(cur[o] for o in free)
        remaining = 1.0 - target_sum
        new = {}
        for o in opt_idx:
            if o in boosts:
                new[o] = boosts[o]
            elif free_mass > 0:
                new[o] = cur[o] / free_mass * remaining
            else:
                new[o] = remaining / len(free) if free else 0.0
        s = sum(new.values())
        for o, i in opt_idx.items():
            cells[i] = repr(new[o] / s)
        assert abs(sum(float(cells[i]) for i in opt_idx.values()) - 1.0) < 1e-9
        out.append(SEP.join(cells))
        n_changed += 1
    if backup and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write("\n".join(out) + "\n")
    print(f"{os.path.basename(path)}: reweighted {n_changed} row(s) "
          f"(where={where or 'ALL rows'}); boosted {boosts}.")


def set_cpt_rows(path, rewrites, backup=True, encoding="utf-8"):
    """Replace whole `Option=` distributions on the rows a `where` clause selects.

    `reweight_cpt` above pins a few options and rescales the rest; this writes a
    complete distribution instead, and can introduce option columns the table
    does not yet have. That second part is the reason it exists: Quebec's HVAC
    efficiency table stops at "Fuel Furnace, 80% AFUE", so there was nowhere to
    put Calgary's condensing fleet until the 85 / 90 / 92.5 / 96% columns are
    added. Adding a column is not renaming one -- every label used here is an
    existing ResStock name that Mapping.dct_HVAC_Heating already prices, so
    nothing downstream has to change.

    `rewrites` is an iterable of {"where": {dep: value}, "shares": {option: p}}.
    Every option not named in `shares` is set to 0 on the matched rows: the
    shares are a full distribution, not a boost.
    """
    with open(path, encoding=encoding) as f:
        lines = f.read().splitlines()
    header = lines[0].split(SEP)

    wanted = {o for rw in rewrites for o in rw["shares"]}
    have = {h[len("Option="):] for h in header if h.startswith("Option=")}
    added = [o for o in sorted(wanted - have)]
    if added:
        header = header + [f"Option={o}" for o in added]
        lines = [SEP.join(header)] + [
            SEP.join(ln.split(SEP) + ["0"] * len(added)) if ln.strip() else ln
            for ln in lines[1:]]

    opt_idx = {h[len("Option="):]: i for i, h in enumerate(header) if h.startswith("Option=")}
    dep_idx = {h[len("Dependency="):]: i for i, h in enumerate(header) if h.startswith("Dependency=")}
    for rw in rewrites:
        for dep in rw["where"]:
            if dep not in dep_idx:
                raise KeyError(f"Dependency {dep!r} not in {os.path.basename(path)}: "
                               f"{list(dep_idx)}")
        for opt in rw["shares"]:
            if opt not in opt_idx:
                raise KeyError(f"Option {opt!r} could not be added to "
                               f"{os.path.basename(path)}")

    out, n_changed, unmatched = [lines[0]], 0, []
    for rw in rewrites:
        rw["_hit"] = 0
    for line in lines[1:]:
        if not line.strip():
            out.append(line)
            continue
        cells = line.split(SEP)
        for rw in rewrites:
            if all(cells[dep_idx[d]].strip() == v for d, v in rw["where"].items()):
                break
        else:
            out.append(line)
            continue
        total = sum(rw["shares"].values())
        for opt, i in opt_idx.items():
            cells[i] = repr(rw["shares"].get(opt, 0.0) / total)
        assert abs(sum(float(cells[i]) for i in opt_idx.values()) - 1.0) < 1e-9
        rw["_hit"] += 1
        n_changed += 1
        out.append(SEP.join(cells))

    unmatched = [rw["where"] for rw in rewrites if not rw.pop("_hit")]
    if unmatched:
        raise AssertionError(
            f"{len(unmatched)} rewrite(s) matched no row in "
            f"{os.path.basename(path)} -- the derived label and the table label "
            f"have drifted apart: {unmatched}")

    if backup and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write("\n".join(out) + "\n")
    return n_changed, added


def _label_group(option_label):
    """Group an Option= label by its leading comma-separated field."""
    return option_label.split(",")[0].strip()


def set_cpt_group_shares(path, rewrites, backup=True, encoding="utf-8"):
    """Move *group* totals onto a target while preserving the shape inside each.

    The Tier-B write: Alberta says how many homes are double- vs triple-glazed,
    but nothing about which frame or coating, so each group is rescaled as a
    block and the Quebec proportions inside it survive untouched.

    The one trap here is a group the Quebec row gives zero mass to. Spreading
    that group's new mass over *every* option is what produced gas homes with
    geothermal heat pumps (see rewrite_hc_tables). So a zero-mass group is
    filled evenly across the options **in that group only** -- a triple-glazed
    home can only ever land on a triple-glazed option.

    `rewrites` is an iterable of {"where": {...}, "group_shares": {group: p}}.
    """
    with open(path, encoding=encoding) as f:
        lines = f.read().splitlines()
    header = lines[0].split(SEP)
    opt_idx = {h[len("Option="):]: i for i, h in enumerate(header) if h.startswith("Option=")}
    dep_idx = {h[len("Dependency="):]: i for i, h in enumerate(header) if h.startswith("Dependency=")}

    groups = {}
    for opt in opt_idx:
        groups.setdefault(_label_group(opt), []).append(opt)

    for rw in rewrites:
        for dep in rw["where"]:
            if dep not in dep_idx:
                raise KeyError(f"Dependency {dep!r} not in {os.path.basename(path)}")
        for g in rw["group_shares"]:
            if g not in groups:
                raise KeyError(
                    f"group {g!r} matches no option in {os.path.basename(path)}; "
                    f"groups present: {sorted(groups)}")
        rw["_hit"] = 0

    out, n_changed = [lines[0]], 0
    for line in lines[1:]:
        if not line.strip():
            out.append(line)
            continue
        cells = line.split(SEP)
        for rw in rewrites:
            if all(cells[dep_idx[d]].strip() == v for d, v in rw["where"].items()):
                break
        else:
            out.append(line)
            continue

        cur = {}
        for opt, i in opt_idx.items():
            c = cells[i].strip()
            cur[opt] = float(c) if c not in ("", "nan") else 0.0

        target = rw["group_shares"]
        total = sum(target.values())
        new = {opt: 0.0 for opt in opt_idx}
        for g, opts in groups.items():
            share = target.get(g, 0.0) / total
            if share <= 0:
                continue
            mass = sum(cur[o] for o in opts)
            for o in opts:
                new[o] = (cur[o] / mass * share) if mass > 0 else share / len(opts)

        s = sum(new.values())
        for opt, i in opt_idx.items():
            cells[i] = repr(new[opt] / s)
        assert abs(sum(float(cells[i]) for i in opt_idx.values()) - 1.0) < 1e-9
        rw["_hit"] += 1
        n_changed += 1
        out.append(SEP.join(cells))

    unmatched = [rw["where"] for rw in rewrites if not rw.pop("_hit")]
    if unmatched:
        raise AssertionError(
            f"{len(unmatched)} rewrite(s) matched no row in "
            f"{os.path.basename(path)}: {unmatched}")

    if backup and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write("\n".join(out) + "\n")
    return n_changed, []


def rewrite_hc_tables():
    """Rewrite the housing-characteristics tables Alberta data can fill.

    The predecessor of this function boosted "Fuel Furnace, 80% AFUE" to 0.85
    within the natural-gas rows, and it was wrong twice over:

      * The Quebec row was 1.0 on that single option and 0.0 everywhere else, so
        `reweight_cpt` had no free mass to redistribute and fell into its
        `remaining / len(free)` branch -- scattering the leftover 0.15 evenly
        over all 37 other options. Gas homes came out holding electric
        baseboards, electric boilers and geothermal heat pumps: 79 of 981 gas
        dwellings (8.1%) in the shipped building-input.csv. `check_coverage`
        could not see it, because the row still existed and still summed to 1.
      * The direction was backwards. Calgary's post-2010 fleet is dominated by
        condensing 92-96% AFUE furnaces, so mass should move up, not off.

    What replaces it is derived, per (fuel, system) row, from what the auditors
    measured in 73,014 Calgary furnaces -- see derive_targets.build_stage2.
    """
    targets = load_targets()
    assert targets is not None, (
        f"{os.path.relpath(TARGETS_JSON, PROJECT_DIR)} missing -- run "
        f"`uv run python calgary_adaptation/derive_targets.py` first.")
    stage2 = targets.get("stage2")
    if not stage2:
        print("  cpt       : no 'stage2' block in the targets file -- nothing "
              "rewritten. Re-run derive_targets.py.")
        return []

    written = []
    for fname, block in stage2.items():
        rewrites = list(block["rewrites"].values())
        if not rewrites:
            continue
        # A block carries either full distributions ("shares") or group totals
        # ("group_shares"); the writer follows the data rather than a per-file list.
        grouped = any("group_shares" in r for r in rewrites)
        writer = set_cpt_group_shares if grouped else set_cpt_rows
        n, added = writer(os.path.join(HC, fname), rewrites)
        written.append(fname)
        print(f"  {fname}: rewrote {n} row(s)"
              + (f", added {len(added)} option column(s): {', '.join(added)}"
                 if added else ""))
        # One line per table, not per row: the insulation tables carry 45 cells
        # each and the interesting number is the summary the derivation printed.
        summary = ", ".join(
            f"{k.replace('_', ' ')} {v}"
            for k, v in block.items()
            if k.startswith("weighted_mean") or k == "n_homes")
        if summary:
            print(f"      {summary}")
        direct = sum(1 for r in rewrites if r.get("level") == "cell")
        if any("level" in r for r in rewrites):
            print(f"      {direct} of {len(rewrites)} cells derived directly, "
                  f"{len(rewrites) - direct} broadened for thin support")
    n_tables = len([f for f in os.listdir(HC) if f.endswith(".csv")])
    print(f"  cpt       : {len(written)} of {n_tables} tables rewritten; the rest "
          f"stay Quebec/ResStock.")
    return written


# --------------------------------------------------------------------------- #
# batch: run the sampler -> the three building-*.csv files
# --------------------------------------------------------------------------- #

PROVENANCE = os.path.join(OUT, "building-input.provenance.json")


def default_bn():
    """BN_Calgary.XDSL once `bn` has built it, else the Quebec original.

    The old default was BN_IN unconditionally, which made `all` build the Calgary
    network and then silently sample from the Quebec one."""
    return BN_OUT if os.path.exists(BN_OUT) else BN_IN


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_DIR,
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def write_provenance(bn_path, n):
    """Record which probability files produced the CSVs, so 'is this Calgary or
    Quebec?' is a lookup rather than a forensic exercise.

    Hashes every housing_characteristics CSV that carries a .bak -- a .bak exists
    iff `cpt` rewrote that table, so this lists exactly the reweighted tables."""
    reweighted = sorted(
        f for f in os.listdir(HC)
        if f.endswith(".csv") and os.path.exists(os.path.join(HC, f + ".bak"))
    )
    prov = {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(),
        "n_dwellings": n,
        "bayesian_network": {
            "path": os.path.relpath(bn_path, PROJECT_DIR).replace("\\", "/"),
            "sha256": _sha256(bn_path),
            "is_calgary": os.path.abspath(bn_path) == os.path.abspath(BN_OUT),
        },
        "bn_targets": {
            "derived_from": (os.path.relpath(TARGETS_JSON, PROJECT_DIR).replace("\\", "/")
                             if os.path.exists(TARGETS_JSON) else None),
            "n_audited_homes": (load_targets() or {}).get("n_calgary_homes"),
            "caveats": (load_targets() or {}).get("caveats"),
            "expected_marginals": expected_marginals(bn_path),
            "hand_typed_anchor": SOURCE_ENERGIE_CHAUF,
        },
        "reweighted_housing_characteristics": [
            {"file": f, "sha256": _sha256(os.path.join(HC, f))} for f in reweighted
        ],
    }
    with open(PROVENANCE, "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=2, ensure_ascii=False)
    return prov


def run_batch(bn_path=None, n=N_DWELLINGS):
    """Generate building-input/mapping/test.csv + the provenance sidecar.

    Defaults to the Calgary BN when it exists. Falling back to Quebec is legal
    (it tests the plumbing) but never silent."""
    bn_path = bn_path or default_bn()
    if os.path.abspath(bn_path) != os.path.abspath(BN_OUT):
        print(f"WARNING: sampling from {os.path.basename(bn_path)} -- these are "
              f"QUEBEC probabilities. Run `apply_to_sampler.py bn` first for Calgary.")
    else:
        print(f"Sampling from {os.path.basename(bn_path)} (Calgary probabilities).")
    from src.utils.sampler.Sampler import Sampler
    s = Sampler(bn_path).run_parallel(n, ev={})     # run_parallel REQUIRES ev=
    pd.DataFrame(s.lst_dct_args).to_csv(os.path.join(OUT, "building-input.csv"), index=False)
    pd.DataFrame(s.lst_dct_HPXML).to_csv(os.path.join(OUT, "building-mapping.csv"), index=False)
    s.to_df().to_csv(os.path.join(OUT, "building-test.csv"), index=False)
    write_provenance(bn_path, n)
    print(f"Wrote building-input/mapping/test.csv ({n} dwellings) to {OUT}")
    print(f"Wrote {os.path.basename(PROVENANCE)}")


# --------------------------------------------------------------------------- #
# validate: assert the Calgary plumbing held
# --------------------------------------------------------------------------- #

# Below this expected count the normal approximation to the binomial is not
# usable and the tolerance switches to the Poisson tail.
NORMAL_APPROX_MIN_COUNT = 10.0


def _binom_tol(p, n, z=4.0):
    """4-sigma Monte-Carlo tolerance on a share drawn n times (~1-in-16k false
    alarm per check). A zero target collapses to 'exactly zero', which is what we
    want for impossible-in-Alberta states.

    The normal band is only meaningful once the expected count is large. For a
    rare state it is narrower than one dwelling -- Superficie_Totale's [1 - 500)
    bin expects 0.05 homes per 1,000 and gets a +/-0.09% band -- so a single draw
    fails a network that is in fact exactly on target. Below the threshold, fall
    back to the Poisson upper tail at the same confidence, which is the right law
    for rare counts and leaves every well-populated state unchanged."""
    if p <= 0.0:
        return 0.0
    normal = z * math.sqrt(max(p * (1.0 - p), 0.0) / n)
    lam = p * n
    if lam >= NORMAL_APPROX_MIN_COUNT:
        return normal
    # Smallest k with P(X <= k) >= 1 - alpha, alpha being the one-sided normal
    # tail at z, so the two regimes agree on how often they cry wolf.
    alpha = 0.5 * math.erfc(z / math.sqrt(2.0))
    term = cum = math.exp(-lam)
    k = 0
    while cum < 1.0 - alpha and k < n:
        k += 1
        term *= lam / k
        cum += term
    return max(normal, (k - lam) / n)


def check_plumbing(i, m, n):
    """Hardcoded-constant checks. These live in Mapping.py and pass no matter
    which BN was sampled -- they say nothing about the re-calibration."""
    bad_epw = m.loc[m["weather_station_epw_filepath"] != CALGARY_EPW, "weather_station_epw_filepath"]
    assert bad_epw.empty, f"{len(bad_epw)}/{n} rows have a non-Calgary EPW: {bad_epw.unique()[:5]}"
    utc = pd.to_numeric(m["site_time_zone_utc_offset"], errors="coerce")
    assert np.allclose(utc, -7.0), f"UTC offsets present: {utc.value_counts(dropna=False).to_dict()}"
    dst = m["simulation_control_daylight_saving_enabled"].astype(str).str.lower()
    assert dst.isin(["true", "1"]).all(), f"DST not all True: {dst.value_counts().to_dict()}"
    n_bie = int((i["Source_Energie_Chauf"] == "Bi-energie").sum())
    assert n_bie == 0, f"{n_bie}/{n} rows still drew Bi-energie in Source_Energie_Chauf"
    hit = m.apply(lambda c: c.astype(str).str.contains("Bi-energie", case=False, na=False)).any().any()
    assert not hit, "Found the literal 'Bi-energie' somewhere in building-mapping.csv"
    print(f"  plumbing  OK: 100% Calgary EPW, UTC -7.0, DST on, zero Bi-energie.")


def _check_shares(i, node, targets, n):
    """Every targeted state's drawn share must match its target within 4 sigma."""
    failures = []
    for label, target in targets.items():
        got = float((i[node] == label).mean())
        tol = _binom_tol(target, n)
        flag = "ok " if abs(got - target) <= tol else "FAIL"
        if flag == "FAIL":
            failures.append((label, target, got))
        print(f"    {flag}  {node:<22} {label:<32} target {target:6.1%}  got {got:6.1%}"
              f"  (+/-{tol:.1%})")
    return failures


def check_calibration(i, m, n, bn_path=None):
    """The only checks that can distinguish a Calgary run from a Quebec one.

    Two layers, because either alone can be fooled:
      (a) the drawn shares reproduce the network they claim to come from, and
      (b) that network is actually gas-dominated, i.e. genuinely re-calibrated.
    Checking only (a) would pass a Quebec BN faithfully sampled."""
    marg = expected_marginals(bn_path)

    gas = marg["Source_Energie_Chauf"].get("Gaz naturel", 0.0)
    assert gas >= 0.75, (
        f"the network itself only puts {gas:.1%} on natural gas -- it has not been "
        f"re-calibrated for Calgary. Run `derive_targets.py` then `apply_to_sampler.py bn`.")

    failures = []
    # Both the heating odds and the stock they are averaged over: a network with
    # Calgary fuel shares over a Quebec building mix is not a Calgary network.
    for node in CALIBRATED_NODES:
        if node in i.columns:
            failures += _check_shares(i, node, marg[node], n)
    if failures:
        worst = ", ".join(f"{lbl}: target {t:.1%} vs got {g:.1%}" for lbl, t, g in failures)
        raise AssertionError(
            f"{len(failures)} share(s) off target -- these are NOT the Calgary "
            f"probabilities ({worst}). Did `batch` sample from BN_EUEMr.XDSL? "
            f"Run `apply_to_sampler.py bn` then `batch`.")

    # Did the fuel actually reach the simulator arguments, or did a mapping rule
    # override it? Looser bound: the mapper routes some dwellings through heat
    # pumps / 'none', so an exact share match is not expected here.
    gas = float((m["heating_system_fuel"] == "natural gas").mean())
    assert gas >= 0.60, (
        f"only {gas:.1%} of building-mapping.csv rows have "
        f"heating_system_fuel='natural gas' although the BN drew "
        f"{float((i['Source_Energie_Chauf'] == 'Gaz naturel').mean()):.1%} gas -- "
        f"a Mapping.py rule is overriding the fuel.")
    print(f"    ok    heating_system_fuel   natural gas                     "
          f"         got {gas:6.1%}  (>=60.0%)")


# ALBERTA_RECALIBRATION_PLAN.md 5.2 asks for TV distance < 0.02, but it asks
# for it on 10,000-50,000 draws. `batch` generates 1,000, and at that size 0.02
# is *below* the noise floor: five states at Calgary's dwelling-type shares
# produce an expected TV distance of ~0.020 from sampling alone, so a network
# that is exactly on target fails half the time. The floor is kept as a lower
# bound for large runs and the real threshold is simulated per node.
TV_TOLERANCE = 0.02
TV_NULL_DRAWS = 4000
TV_NULL_QUANTILE = 0.999
TV_NULL_SEED = 20260820


def _tv_tolerance(target, n, floor=TV_TOLERANCE):
    """How far a *correct* network can drift at this sample size, by simulation.

    Rather than approximate the null distribution of the TV distance, draw from
    it: sample n dwellings from `target` a few thousand times and take a high
    quantile. Exact for any support size and any skew, which matters here
    because Superficie_Totale spreads 11 states from 24% down to 0.05% and no
    closed form covers that gracefully. Seeded, so the threshold is stable
    between runs and a failure means the data moved, not the dice.
    """
    p = np.array([float(v) for v in target.values()], dtype=float)
    p = p / p.sum()
    rng = np.random.default_rng(TV_NULL_SEED)
    draws = rng.multinomial(n, p, size=TV_NULL_DRAWS) / float(n)
    null = 0.5 * np.abs(draws - p).sum(axis=1)
    return max(floor, float(np.quantile(null, TV_NULL_QUANTILE)))


def _tv(a, b):
    """Total-variation distance between two distributions on the same support."""
    keys = set(a) | set(b)
    return 0.5 * sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys)


def source_marginals(targets=None):
    """The city-wide distributions the *derivation* produced, by node.

    Deliberately read from calgary_bn_targets.json and not from the network.
    check_calibration compares the drawn CSVs against the BN's own posterior,
    which proves the sampler is faithful but says nothing about whether the BN
    matches the data it claims to come from. Anything that corrupts the network
    or the housing_characteristics tables *after* derivation -- which is exactly
    what the hand-typed 80%-AFUE boost did -- passes that check and fails this
    one.
    """
    targets = targets or load_targets()
    if not targets:
        return {}
    out = {}
    # Only the marginals the network is *built* to reproduce exactly. The
    # `city_wide` entries on the two heating nodes are deliberately NOT used:
    # they are the raw weighted marginal over all Calgary homes, whereas the
    # network integrates the derived per-cell distributions over the census
    # stock. Those two quantities are close but not identical by construction,
    # and once thin cells are shrunk toward their group they separate by several
    # points -- so comparing them would flag correct behaviour as drift. The
    # heating nodes are checked where their numbers actually live, cell by cell,
    # in check_target_cells below.
    for node, block in (targets.get("stock") or {}).items():
        if isinstance(block, dict) and block.get("shares"):
            out[node] = block["shares"]
    return out


CELL_CHECK_MIN_DRAWN = 200


def check_target_cells(i, tol=0.05, min_drawn=CELL_CHECK_MIN_DRAWN):
    """Conditional distributions, cell by cell, against the derived targets.

    Stronger than the marginal check and immune to the estimator mismatch above:
    calgary_bn_targets.json states P(node | parents) directly, and the drawn
    sample can be conditioned on the same parents. A cell that no longer matches
    means the CPT was overwritten after `bn` ran.

    Cells drawn fewer than `min_drawn` times are skipped -- with 20,000 draws
    spread over 25 (type x fuel) cells, the rare ones carry more noise than
    signal, and the tolerance that would let them pass would let real drift pass
    too.
    """
    targets = load_targets()
    if not targets:
        return
    checked = failures = skipped = 0
    for node in ("Source_Energie_Chauf", "Chauffage_Logement"):
        block = targets.get(node)
        if not block or node not in i.columns:
            continue
        parents = block["parents"]
        if not set(parents) <= set(i.columns):
            continue
        worst = (0.0, None)
        node_failures = 0
        for key, cell in block["cells"].items():
            if not cell.get("shares"):
                continue
            mask = np.ones(len(i), dtype=bool)
            for p, v in zip(parents, key.split("|")):
                mask &= (i[p].astype(str) == v).to_numpy()
            if mask.sum() < min_drawn:
                skipped += 1
                continue
            drawn = i.loc[mask, node].value_counts(normalize=True).to_dict()
            d = _tv(drawn, cell["shares"])
            checked += 1
            if d > worst[0]:
                worst = (d, key)
            if d > tol:
                failures += 1
                node_failures += 1
                print(f"    FAIL  {node:<22} cell {key!r} TV {d:.4f} > {tol:.2f}")
        if worst[1] is not None:
            flag = "FAIL" if node_failures else "ok "
            suffix = (f", {node_failures} over tolerance" if node_failures
                      else f"  (<= {tol:.2f})")
            print(f"    {flag}  {node:<22} {checked} cell(s) checked, worst TV "
                  f"{worst[0]:.4f} at {worst[1]!r}{suffix}")
    if skipped:
        print(f"         ({skipped} cell(s) skipped: fewer than {min_drawn} draws)")
    if failures:
        raise AssertionError(
            f"{failures} conditional cell(s) no longer match "
            f"calgary_bn_targets.json -- a CPT was rewritten after `bn` ran.")


# Phase 5.2 asks for this check on 10,000-50,000 draws, and the number matters
# more than it looks. Run against `batch`'s 1,000 dwellings the check is close
# to powerless: forcing 12% of the sample to detached -- a gross corruption --
# lands at TV 0.041 against a 0.057 noise threshold and passes. Drawing 20,000
# from the network costs about five seconds and shrinks the threshold ~4.5x,
# which is the difference between a check and a decoration.
TARGET_CHECK_DRAWS = 20000


def check_targets(bn_path=None, n=TARGET_CHECK_DRAWS, tol=TV_TOLERANCE):
    """Every drawn marginal must match the derived source within sampling noise.

    This is the plan's Phase 5.2 check, and it closes the loop the other two
    leave open: `plumbing` tests hardcoded constants, `calibration` tests the
    sampler against the network, and this tests the network against the numbers
    that actually came out of the audits. Only this one can catch a probability
    that was rewritten after `bn` ran.
    """
    src = source_marginals()
    if not src:
        print("  targets   SKIP: no calgary_bn_targets.json to compare against.")
        return
    from src.utils.sampler.Sampler import Sampler
    i = Sampler(bn_path or default_bn()).GUM_Sampling(n, evs={})
    check_target_cells(i)

    failures = []
    for node, target in sorted(src.items()):
        if node not in i.columns:
            continue
        drawn = i[node].value_counts(normalize=True).to_dict()
        d = _tv(drawn, target)
        limit = _tv_tolerance(target, n, floor=tol)
        flag = "ok " if d <= limit else "FAIL"
        if d > limit:
            failures.append((node, d, limit))
        print(f"    {flag}  {node:<22} TV distance from derived source "
              f"{d:.4f}  (<= {limit:.4f} at n={n:,})")

    if failures:
        worst = ", ".join(f"{n_}: TV {d:.4f} > {l:.4f}" for n_, d, l in failures)
        raise AssertionError(
            f"{len(failures)} marginal(s) drifted from the derived targets "
            f"({worst}). The CSVs do not reproduce calgary_bn_targets.json -- "
            f"either the network was rebuilt from different targets, or "
            f"something rewrote a probability after `bn` ran.")


IMPLAUSIBLE_INHERITED = {
    # node: (state, share above which it is not credible for Calgary, why)
    "Piscine_Presence": (
        "Oui", 0.05,
        "in-ground/above-ground pools at a Quebec rate; Calgary's climate and "
        "lot sizes put the real figure far lower, and nothing in this repo "
        "sources it"),
    "Vehicule_Presence": (
        None, 0.05,
        "EV/PHEV ownership at a Quebec rate; Alberta's EV share of the fleet "
        "is a fraction of Quebec's"),
}


def report_inherited_loads(i, n):
    """Name the Quebec-inherited nodes that carry a materially wrong load.

    These are not failures -- there is no Calgary source in the repo to replace
    them with, and substituting an invented number would be worse than keeping
    a labelled Quebec one. But they are the largest known errors left in the
    model, and a silent wrong number is how a Quebec pool rate ends up quoted as
    a Calgary result. So they are printed on every run, with their size.
    """
    for node, (state, threshold, why) in IMPLAUSIBLE_INHERITED.items():
        if node not in i.columns:
            continue
        if state is None:
            # "any state that is not the 'none' baseline" -- read the baseline
            # off the data as the most common state rather than naming it here.
            share = 1.0 - float(i[node].value_counts(normalize=True).iloc[0])
        else:
            share = float((i[node] == state).mean())
        if share > threshold:
            print(f"  WARNING  {node}: {share:.1%} of the generated dwellings -- "
                  f"{why}.")


def validate():
    m = pd.read_csv(os.path.join(OUT, "building-mapping.csv"))
    i = pd.read_csv(os.path.join(OUT, "building-input.csv"))
    n = len(m)

    bn_used = None
    if os.path.exists(PROVENANCE):
        with open(PROVENANCE, encoding="utf-8") as f:
            prov = json.load(f)
        bn = prov["bayesian_network"]
        bn_used = os.path.join(PROJECT_DIR, bn["path"])
        n_homes = prov.get("bn_targets", {}).get("n_audited_homes")
        print(f"  provenance: {bn['path']}  sha256 {bn['sha256'][:12]}...  "
              f"generated {prov['generated_utc']}  n={prov['n_dwellings']}"
              + (f"  (targets from {n_homes:,} audited homes)" if n_homes else ""))
        rw = prov["reweighted_housing_characteristics"]
        print(f"              {len(rw)} reweighted housing-characteristics table(s): "
              f"{', '.join(r['file'] for r in rw) or '(none)'}")
        if not bn["is_calgary"]:
            print("  WARNING: provenance says these CSVs came from the QUEBEC BN.")
    else:
        print(f"  provenance: {os.path.basename(PROVENANCE)} missing -- CSVs predate "
              f"provenance tracking; falling back to the share checks alone.")

    check_plumbing(i, m, n)
    # Source-of-truth check first: if the network no longer reproduces the
    # derived targets, the share checks below are comparing two equally wrong
    # things. Sampled fresh and large, because at n=1,000 it cannot see much.
    check_targets(bn_used)
    # Compare against the network the CSVs actually came from, so a Quebec run
    # fails on the gas-share gate rather than on a confusing share mismatch.
    check_calibration(i, m, n, bn_path=bn_used)
    report_inherited_loads(i, n)
    print(f"PASS  ({n} dwellings): Calgary plumbing AND Calgary probabilities.")


DATA_DESCRIPTION = os.path.join(PROJECT_DIR, "data", "processed", "Data_description.csv")
BN_CSV = os.path.join(BN_DIR, "Bn.csv")
PROVENANCE_MD = os.path.join(PROJECT_DIR, "calgary_adaptation", "PROVENANCE.md")

# Columns that describe the network's *structure* and can therefore be
# regenerated from it. Description / Echantillonneur / Source are human-authored
# prose and are carried over untouched -- regenerating those would mean writing
# documentation nobody checked.
DERIVED_DOC_COLUMNS = ("Valeurs", "Dépendance (parents)", "Dépendance (enfants)")


def refresh_descriptions(bn_path=None):
    """Bring Data_description.csv and Bn.csv back in line with the network.

    Both files still describe Quebec: five Territoire_HQ territories and fifteen
    Region_Administrative regions that the geography collapse removed. That is
    not harmless documentation drift -- Dashboard.py loads Data_description.csv
    and renders it as the Bayesian Network page's *Description* tab, so the app
    currently tells its users the model covers Montreal and Gaspesie.

    Only the three structural columns are rewritten, from the live network. The
    French question text and the Source column are left exactly as they are.
    """
    import pyagrum as gum
    bn = gum.loadBN(bn_path or default_bn())
    names = set(bn.names())

    structure = {}
    for name in names:
        nid = bn.idFromName(name)
        structure[name] = {
            "Valeurs": str([str(l) for l in bn.variable(name).labels()]),
            "Dépendance (parents)": str(sorted(bn.variable(p).name()
                                               for p in bn.parents(nid))),
            "Dépendance (enfants)": str(sorted(bn.variable(c).name()
                                               for c in bn.children(nid))),
        }

    touched = []
    for path in (DATA_DESCRIPTION, BN_CSV):
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path, index_col=0)
        if "Nom" not in df.columns:
            continue
        # Positional access, not label access. 57 of the 97 rows in
        # Data_description.csv carry an empty id, so they all share a NaN index
        # label -- and `df.at[nan, col] = v` writes to *every one of them*. Doing
        # this by label overwrote Battery, Ceiling Fan and 55 other ResStock rows
        # with Infiltration's ACH50 states.
        changed = 0
        col_pos = {c: df.columns.get_loc(c) for c in DERIVED_DOC_COLUMNS
                   if c in df.columns}
        for row_pos, nom in enumerate(df["Nom"].tolist()):
            info = structure.get(str(nom))
            if info is None:
                continue          # a ResStock attribute, not a BN node
            for col, cpos in col_pos.items():
                if str(df.iat[row_pos, cpos]) != info[col]:
                    df.iat[row_pos, cpos] = info[col]
                    changed += 1
        if not os.path.exists(path + ".bak"):
            shutil.copy2(path, path + ".bak")
        df.to_csv(path, encoding="utf-8")
        touched.append((os.path.basename(path), changed))
        print(f"  {os.path.basename(path)}: refreshed {changed} structural "
              f"cell(s) from {os.path.basename(bn_path or default_bn())}")
    return touched


def _relposix(path):
    """Repo-relative path with forward slashes, for embedding in Markdown."""
    return os.path.relpath(path, PROJECT_DIR).replace("\\", "/")


def write_provenance_md(bn_path=None):
    """Phase 7's PROVENANCE.md: every node, where its numbers came from.

    building-input.provenance.json is a *run receipt* -- hashes, commit, counts
    -- which answers "did these CSVs come from the Calgary network?". It does
    not answer "where did this probability come from?", which is the question
    someone quoting a number needs answered. Everything required is already in
    calgary_bn_targets.json: each cell records its source, its support and
    whether it was derived or broadened.
    """
    import pyagrum as gum
    targets = load_targets() or {}
    bn = gum.loadBN(bn_path or default_bn())
    all_nodes = sorted(bn.names())
    structural = {"Territoire_HQ", "Region_Administrative",
                  "Type_Batiment", "An_ConstructionCode"}

    def _support(block):
        cells = block.get("cells") if isinstance(block, dict) else None
        if isinstance(cells, dict) and cells:
            vals = [c for c in cells.values() if isinstance(c, dict)]
            levels = collections.Counter(c.get("level") for c in vals)
            # A census-sourced cell is not a *failed* derivation, so counting it
            # as "0 of 5 derived directly" reads as a defect when it is the
            # opposite: the census is the better source and was preferred.
            census = sum(n for lv, n in levels.items()
                         if lv and str(lv).startswith("census"))
            if census == len(vals):
                return f"{len(vals)} cells straight from the census"
            direct = levels.get("cell", 0)
            preserved = sum(n for lv, n in levels.items()
                            if lv and str(lv).startswith("quebec-preserved"))
            bits = [f"{direct}/{len(vals)} cells derived directly"]
            if preserved:
                bits.append(f"{preserved} deliberately kept Québec")
            return ", ".join(bits)
        if isinstance(block, dict) and block.get("n_homes"):
            return f"n = {block['n_homes']:,}"
        return ""

    blocks = {}
    for node in ("Source_Energie_Chauf", "Chauffage_Logement"):
        if node in targets:
            blocks[node] = targets[node]
    blocks.update({k: v for k, v in (targets.get("stock") or {}).items()
                   if isinstance(v, dict)})
    blocks.update({k: v for k, v in (targets.get("enduse") or {}).items()
                   if isinstance(v, dict)})

    lines = [
        "# PROVENANCE — where every probability in the Calgary model comes from",
        "",
        "Generated by `apply_to_sampler.py docs`; do not edit by hand.",
        "",
        f"- Network: `{_relposix(bn_path or default_bn())}`",
        f"- Targets: `{_relposix(TARGETS_JSON)}`",
        f"- Audited Calgary homes behind the derived numbers: "
        f"**{targets.get('n_calgary_homes', 0):,}**",
        f"- Generated (UTC): {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Stage 1 — Bayesian network nodes",
        "",
        "| Node | Status | Source | Support |",
        "|---|---|---|---|",
    ]
    for node in all_nodes:
        if node in structural:
            lines.append(f"| `{node}` | structural | single-state or a "
                         f"deterministic collapse of its parent; inherits Calgary "
                         f"automatically | — |")
        elif node in blocks:
            b = blocks[node]
            src = str(b.get("source", "derived from EnerGuide, Calgary-raked"))
            lines.append(f"| `{node}` | **Calgary** | {src} | {_support(b)} |")
        else:
            lines.append(f"| `{node}` | Québec | no Calgary source in this repo | — |")

    lines += ["", "## Stage 2 — housing-characteristics tables", "",
              "| Table | Status | Source |", "|---|---|---|"]
    for fname, block in (targets.get("stage2") or {}).items():
        lines.append(f"| `{fname}` | **Calgary** | {block.get('source', '')} |")
    for fname, why in (targets.get("stage2_not_derived") or {}).items():
        lines.append(f"| `{fname}` | Québec | not derivable: {why} |")
    n_tables = len([f for f in os.listdir(HC) if f.endswith(".csv")])
    n_done = len(targets.get("stage2") or {})
    lines += ["",
              f"The other {n_tables - n_done} of {n_tables} tables are untouched "
              f"Québec/ResStock defaults.", ""]

    caveats = targets.get("caveats") or {}
    if caveats.get("note"):
        lines += ["## Standing caveats", "", f"- {caveats['note']}"]
        for thin in caveats.get("thin_building_types", []):
            lines.append(f"- `{thin['type']}` rests on **{thin['n_audited']}** "
                         f"audited homes while carrying "
                         f"{thin['weighted_share']:.1%} of the city's weight.")
        lines.append("")

    with open(PROVENANCE_MD, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  wrote {_relposix(PROVENANCE_MD)} "
          f"({len(all_nodes)} nodes, {n_done} rewritten table(s))")
    return PROVENANCE_MD


def refresh_docs(bn_path=None):
    refresh_descriptions(bn_path)
    write_provenance_md(bn_path)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Apply the Calgary re-calibration to the sampler")
    ap.add_argument("step", nargs="?", default="validate",
                    choices=["targets", "bn", "cpt", "batch", "coverage",
                             "validate", "docs", "all"])
    args = ap.parse_args()
    if args.step in ("targets", "all"):
        from calgary_adaptation.derive_targets import build as build_targets
        build_targets()
    if args.step in ("bn", "all"):
        make_bn()
    if args.step in ("cpt", "all"):
        rewrite_hc_tables()
    # cheap pre-flight: fail in seconds rather than minutes into the batch
    if args.step in ("coverage", "batch", "all"):
        check_coverage()
    if args.step in ("batch", "all"):
        run_batch()
    if args.step in ("validate", "all"):
        validate()
    # Last, so the docs describe the network that was just built and validated.
    if args.step in ("docs", "all"):
        refresh_docs()


if __name__ == "__main__":
    main()
