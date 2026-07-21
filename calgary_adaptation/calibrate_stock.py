"""
Phase 2 - Clean & de-bias the EnerGuide Alberta pull
(see ALBERTA_RECALIBRATION_PLAN.md, section 4, Phase 2).

Turns the raw per-year Parquet files produced by fetch_alberta_data.py into a
weighted "Alberta pseudo-survey" table whose columns carry the *exact* state
labels of the Hydro-Quebec Bayesian network (Bn.yml vocabulary, names kept
verbatim - only probabilities will ever change downstream).

Pipeline:
    1. load_energuide()      - concat data/input/alberta/energuide/*.parquet
    2. dedupe_stock()        - one record per HOUSEID; pre-retrofit ("D")
                               preferred over post-retrofit ("E") so we
                               characterize the *existing* stock, not the
                               upgraded one; new homes ("N" preferred over
                               plan-stage "P") kept as a separate cohort
    3. EnerGuideToBN().apply() - translate EnerGuide vocabularies to the BN's
                               French state labels (Tier-A nodes), failing
                               loudly on any unmapped category
    4. rake_to_census_margins() - IPF post-stratification to census margins
                               (placeholder; will adapt Create_Pond from
                               src/utils/euemr/Mapping.py)

Usage (from repo root):
    uv run python calgary_adaptation/calibrate_stock.py [combine|weights|all]
`combine` writes energuide_ab_houses/evaluations.parquet; `weights` writes
alberta_stock_mapped.parquet (mapped + census-raked); `all` (default) does both.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ENERGUIDE_DIR = REPO_ROOT / "data" / "input" / "alberta" / "energuide"
BN_YML = REPO_ROOT / "data" / "processed" / "bayesian_network" / "Bn.yml"
OUT_PATH = ENERGUIDE_DIR / "alberta_stock_mapped.parquet"

# Sane bounds for YEARBUILT; the pull contains a handful of junk values (<1850).
YEARBUILT_MIN, YEARBUILT_MAX = 1850, 2026


# --------------------------------------------------------------------------- #
# 1. Loading
# --------------------------------------------------------------------------- #

def load_energuide(columns: list[str] | None = None) -> pd.DataFrame:
    """Concatenate every per-year Parquet file into one DataFrame.

    `columns` restricts the read (Parquet is columnar, so this is cheap);
    a `source_file_year` column records which year-resource each row came
    from (the *evaluation* vintage, not the construction vintage).
    """
    # The [0-9] guard keeps this to the raw per-year pulls: the derived tables
    # written by build_energuide_dataset.py (energuide_ab_evaluations.parquet,
    # energuide_ab_houses.parquet) live in the same directory and would
    # otherwise be concatenated back in on top of their own inputs.
    files = sorted(ENERGUIDE_DIR.glob("energuide_ab_[0-9]*.parquet"))
    assert files, f"no Parquet files under {ENERGUIDE_DIR} - run fetch_alberta_data.py first"
    frames = []
    for f in files:
        year_label = f.stem.replace("energuide_ab_", "")
        df = pd.read_parquet(f, columns=columns)
        df["source_file_year"] = year_label
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    print(f"loaded {len(out):,} rows from {len(files)} files "
          f"({files[0].stem[-4:]}..{files[-1].stem[-4:]})")
    return out


# --------------------------------------------------------------------------- #
# 2. De-duplication
# --------------------------------------------------------------------------- #

# The record key NRCan documents in the open-data dictionary: "Files can be
# linked together using the following fields: EVALTYPE, EVALUATIONSID and
# HOUSEID." Note `_id` is NOT a usable key - it is a CKAN per-resource row
# number whose ranges overlap across files, so keying on it deletes real rows.
RECORD_KEY = ["HOUSEID", "EVALUATIONSID", "EVALTYPE"]

# A restatement count far above this means the upstream data changed shape and
# the "later file wins" rule deserves a fresh look rather than silent trust.
RESTATEMENT_ALERT_THRESHOLD = 100


def resolve_restatements(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Collapse records NRCan restated in a later annual release.

    The same (HOUSEID, EVALUATIONSID, EVALTYPE) can appear in two adjacent-year
    files with revised values; the later file wins. There were 9 such records on
    the 2004-2025 pull. Returns the de-duplicated frame plus one report entry
    per resolved key. `source_file_year` sorts correctly as a string here
    ("2004-2006" < "2007" < ... < "2025").
    """
    dup_mask = df.duplicated(RECORD_KEY, keep=False)
    n_dup_rows = int(dup_mask.sum())

    report: list[dict] = []
    if n_dup_rows:
        payload = [c for c in df.columns
                   if c not in {"_id", "source_row_id", "source_file_year"}]
        for key, grp in df[dup_mask].groupby(RECORD_KEY, dropna=False, sort=True):
            differing = [c for c in payload if grp[c].astype(str).nunique() > 1]
            report.append({
                "HOUSEID": key[0],
                "EVALUATIONSID": key[1],
                "EVALTYPE": key[2],
                "source_files": sorted(grp["source_file_year"]),
                "kept_from": max(grp["source_file_year"]),
                "n_differing_columns": len(differing),
                "differing_columns": differing,
            })

    out = (
        df.sort_values(RECORD_KEY + ["source_file_year"])
          .drop_duplicates(RECORD_KEY, keep="last")
          .reset_index(drop=True)
    )

    n_dropped = len(df) - len(out)
    if n_dropped:
        print(f"  resolved {n_dropped} restated record(s) "
              f"({n_dup_rows} rows in {len(report)} conflicting group(s)); "
              f"kept the later release of each")
    else:
        print("  no restated records found")

    if n_dropped > RESTATEMENT_ALERT_THRESHOLD:
        print(f"  WARNING: {n_dropped} restatements is far above the expected "
              f"handful - check whether the upstream pull changed shape")

    return out, report

# EVALTYPE codes in the open data:
#   D = evaluation of an existing house BEFORE retrofit  (what we want)
#   E = follow-up evaluation AFTER retrofit              (upgraded stock)
#   N = new house, evaluated as built
#   P = new house, evaluated from plans (may never match the built house)
# Rank = preference order within one HOUSEID (lower = kept).
EVALTYPE_RANK = {"D": 0, "E": 1, "N": 2, "P": 3}
EXISTING_EVALTYPES = {"D", "E"}


def dedupe_stock(df: pd.DataFrame) -> pd.DataFrame:
    """One record per house: best EVALTYPE rank, then earliest ENTRYDATE.

    Prioritizing "D" (pre-retrofit) over "E" (post-retrofit) keeps the
    *existing* stock's characteristics rather than the upgraded ones; the
    earliest date breaks ties (a house can have several D evaluations across
    grant programs). Rows with a null HOUSEID cannot be de-duplicated and are
    dropped with a warning. A `cohort` column separates the existing-stock
    records ("existing": D/E) from new-construction records ("new": N/P) so
    Phase 3 can build vintage-specific CPTs from the right population.

    The rank is applied globally within a HOUSEID, so a house holding both a D
    and an N record collapses to the D row and is labelled "existing". The
    evaluation-level table from build_energuide_dataset.py keeps both records
    if you need to recover such houses.

    Selection uses .head(1), NOT .groupby(...).first(): pandas' GroupBy.first()
    returns the first *non-null* value per column independently, which silently
    back-fills the winning row's nulls from the losing evaluation - i.e. it
    mixes post-retrofit values into a pre-retrofit record. That affected 17,868
    of 191,621 houses (9.3%) on the 2004-2025 pull.
    """
    n0 = len(df)
    null_ids = df["HOUSEID"].isna()
    if null_ids.any():
        print(f"  dropping {null_ids.sum()} rows with null HOUSEID")
        df = df[~null_ids]

    unknown = set(df["EVALTYPE"].dropna().unique()) - set(EVALTYPE_RANK)
    assert not unknown, f"unknown EVALTYPE codes {unknown} - extend EVALTYPE_RANK"

    df = df.assign(
        _rank=df["EVALTYPE"].map(EVALTYPE_RANK),
        _date=pd.to_datetime(df["ENTRYDATE"], errors="coerce"),
    )
    df = (
        df.sort_values(["HOUSEID", "_rank", "_date"])
          .groupby("HOUSEID", as_index=False, sort=False)
          .head(1)
          .drop(columns=["_rank", "_date"])
          .reset_index(drop=True)
    )
    df["cohort"] = np.where(
        df["EVALTYPE"].isin(list(EXISTING_EVALTYPES)), "existing", "new"
    )
    print(f"  de-duplicated {n0:,} evaluations -> {len(df):,} houses "
          f"({(df['cohort'] == 'existing').sum():,} existing, "
          f"{(df['cohort'] == 'new').sum():,} new)")
    return df


# --------------------------------------------------------------------------- #
# 3. Mapping framework: EnerGuide vocabulary -> BN state labels
# --------------------------------------------------------------------------- #

class UnmappedValueError(AssertionError):
    """Raised when the EnerGuide data contains a category we never mapped."""


class EnerGuideToBN:
    """Translate EnerGuide columns into the BN's exact (French) state labels.

    Design rules:
    - Target labels are copied verbatim from Bn.yml and *verified against it
      at runtime* (`verify_against_bnyml`), so a typo here or a future BN
      regeneration cannot silently desynchronize the two.
    - Source keys are matched case-insensitively (the open data mixes
      "Single detached" / "Single Detached" across years).
    - Any source value without a mapping raises UnmappedValueError listing
      the offending values and their counts - never a silent NaN.
    """

    # ----- Type_Logement --------------------------------------------------- #
    # BN states: Collective | Triplex | Duplex | Maison en rangee | Maison individuelle
    #
    # Best-guess correspondences (to iterate on together):
    # - "Double/Semi-detached" -> Duplex: two dwellings sharing one structure.
    #   NOTE Quebec's "Duplex" usually means *stacked* units, while a
    #   semi-detached is side-by-side; the alternative reading is
    #   "Maison individuelle" (jumelee). Flagged for review.
    # - "Mobile home" -> Maison individuelle: the BN has no mobile-home state;
    #   detached single dwelling is the closest geometry (143+39 rows only).
    # - "Apartment Row" (row-oriented MURB) -> Collective.
    TYPE_LOGEMENT = {
        "single detached": "Maison individuelle",
        "mobile home": "Maison individuelle",
        "row house, end unit": "Maison en rangee",
        "row house, middle unit": "Maison en rangee",
        "row, end unit": "Maison en rangee",
        "row, middle unit": "Maison en rangee",
        "double/semi-detached": "Duplex",
        "attached duplex": "Duplex",
        "detached duplex": "Duplex",
        "duplex (non-murb)": "Duplex",
        "attached triplex": "Triplex",
        "detached triplex": "Triplex",
        "apartment": "Collective",
        "apartment row": "Collective",
    }

    # ----- An_Construction (binning, not a dict) --------------------------- #
    # BN states (Bn.yml): "< 1950", "[1950 - 1960)", ..., "[2010 - 2020)", ">= 2020"
    AN_CONSTRUCTION_EDGES = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
    AN_CONSTRUCTION_LABELS = [
        "< 1950", "[1950 - 1960)", "[1960 - 1970)", "[1970 - 1980)",
        "[1980 - 1990)", "[1990 - 2000)", "[2000 - 2010)", "[2010 - 2020)",
        ">= 2020",
    ]

    # ----- Source_Energie_Chauf -------------------------------------------- #
    # BN states: Electricite | Mazout | Gaz naturel | Bi-energie | Bois
    #
    # - "Bi-energie" is a Hydro-Quebec-only tariff: nothing maps to it, so its
    #   probability will land at 0 while the state name is preserved.
    # - Propane -> Gaz naturel: closest combustion-gas equipment class in the
    #   BN vocabulary (0.13% of AB rows). Flagged for review.
    # - All wood variants (4 spellings) -> Bois.
    SOURCE_ENERGIE_CHAUF = {
        "natural gas": "Gaz naturel",
        "propane": "Gaz naturel",
        "electricity": "Electricite",
        "oil": "Mazout",
        "mixed wood": "Bois",
        "hardwood": "Bois",
        "softwood": "Bois",
        "wood pellets": "Bois",
    }

    # (source column, output column, mapping dict) for the dict-based nodes
    DICT_MAPPINGS = [
        ("TYPEOFHOUSE", "Type_Logement", TYPE_LOGEMENT),
        ("FURNACEFUEL", "Source_Energie_Chauf", SOURCE_ENERGIE_CHAUF),
    ]

    # ------------------------------------------------------------------ #

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add one BN-labelled column per mapped node; loud on unmapped values."""
        df = df.copy()
        for src_col, out_col, mapping in self.DICT_MAPPINGS:
            df[out_col] = self._map_column(df[src_col], mapping, src_col)
        df["An_Construction"] = self._bin_an_construction(df["YEARBUILT"])
        return df

    @staticmethod
    def _map_column(series: pd.Series, mapping: dict[str, str],
                    src_name: str) -> pd.Series:
        """Case-insensitive dict lookup that fails loudly on unmapped values."""
        normalized = series.str.strip().str.casefold()
        mapped = normalized.map(mapping)
        bad = normalized[mapped.isna() & normalized.notna()]
        if len(bad):
            counts = bad.value_counts().to_dict()
            raise UnmappedValueError(
                f"{src_name}: unmapped categories {counts} - "
                f"extend EnerGuideToBN mappings"
            )
        return mapped

    @classmethod
    def _bin_an_construction(cls, yearbuilt: pd.Series) -> pd.Series:
        """YEARBUILT (text) -> the BN's 9 An_Construction vintage bins.

        Junk years (outside [YEARBUILT_MIN, YEARBUILT_MAX]) become NaN and are
        counted by the caller's sanity report rather than crashing: unlike a
        category typo, a bad year is a data-entry problem in the source, not a
        mapping gap.
        """
        years = pd.to_numeric(yearbuilt, errors="coerce")
        years = years.where((years >= YEARBUILT_MIN) & (years <= YEARBUILT_MAX))
        binned = pd.cut(
            years,
            bins=[-np.inf, *cls.AN_CONSTRUCTION_EDGES, np.inf],
            labels=cls.AN_CONSTRUCTION_LABELS,
            right=False,  # [1950, 1960) etc., matching the BN labels
        )
        return binned.astype(object)

    # ------------------------------------------------------------------ #

    def verify_against_bnyml(self) -> None:
        """Assert every mapping target is a real state label in Bn.yml."""
        import yaml
        docs = yaml.safe_load(open(BN_YML, encoding="utf-8"))
        labels = docs[1]  # documents: 0=descriptions, 1=state labels, 2=structure
        checks = [
            ("Type_Logement", set(self.TYPE_LOGEMENT.values())),
            ("Source_Energie_Chauf", set(self.SOURCE_ENERGIE_CHAUF.values())),
            ("An_Construction", set(self.AN_CONSTRUCTION_LABELS)),
        ]
        for node, targets in checks:
            valid = set(labels[node].values())
            rogue = targets - valid
            assert not rogue, (
                f"{node}: mapping targets {rogue} are not states in Bn.yml "
                f"(valid: {sorted(valid)})"
            )
        print("  mapping targets verified against Bn.yml")


# --------------------------------------------------------------------------- #
# 4. Raking (Phase 2b): IPF to Calgary 2021 census margins
# --------------------------------------------------------------------------- #
#
# The Quebec pipeline's Create_Pond (src/utils/euemr/Mapping.py:723) is a
# direct post-stratification: PONDNew = target_share / sample_share per JOINT
# (Vintage x Territoire x Typo x Source) cell, read from raked_data.csv. That
# only works when every joint cell is populated. Our EnerGuide pull has
# essentially no Collective records (0.06% vs ~30% of the real stock), so most
# Collective joint cells are EMPTY and the direct method divides by zero.
#
# We therefore keep Create_Pond's core ratio idea but apply it ITERATIVELY,
# one margin at a time (classical IPF / raking): each pass multiplies the
# weights by target_share/current_share of ONE margin, cycling until all
# margins agree. IPF needs support per marginal category only - far weaker
# than joint support - and the remaining pathologies are handled explicitly:
#   * a target category with ZERO sample support cannot be raked to: it is
#     dropped from the margin (renormalized) with a loud warning;
#   * critically sparse categories converge mathematically but concentrate
#     huge weight on a handful of rows: an optional trim-and-re-rake loop
#     caps single-row weights, and Kish effective-sample-size diagnostics
#     make the concentration visible instead of silent.

# ---- Census 2021 targets, Calgary CSD (4806016), occupied private dwellings.
# Hardcoded estimates for now - derived from the 2021 Census Profile
# (structural type, period of construction, tenure), with census categories
# folded onto the BN vocabulary:
#   Maison individuelle = single-detached + movable
#   Duplex              = semi-detached + apartment/flat in a duplex
#   Maison en rangee    = row house + other single-attached
#   Collective          = apartment <5 storeys + apartment >=5 storeys
#   Triplex             = no census category (folded into low-rise apartments
#                         by StatCan); tiny share carved out of Collective
# Period-of-construction census bins ("1960 or before", "1961-1980", ...) are
# split onto the BN decade bins. TODO Phase 2b-doc: replace with exact table
# extracts and log retrieval in data/input/alberta/SOURCES.md.
CENSUS_MARGINS_CALGARY_2021: dict[str, dict[str, float]] = {
    "Type_Logement": {
        "Maison individuelle": 0.552,
        "Maison en rangee":    0.088,
        "Duplex":              0.084,
        "Triplex":             0.005,
        "Collective":          0.271,
    },
    "An_Construction": {
        "< 1950":         0.035,
        "[1950 - 1960)":  0.048,
        "[1960 - 1970)":  0.105,
        "[1970 - 1980)":  0.158,
        "[1980 - 1990)":  0.129,
        "[1990 - 2000)":  0.135,
        "[2000 - 2010)":  0.211,
        "[2010 - 2020)":  0.155,
        ">= 2020":        0.024,
    },
    "Mode_Occupation": {
        "Proprietaire": 0.709,
        "Locataire":    0.291,
    },
}

# Census-conditional owner share by dwelling type (Calgary 2021, tenure x
# structural type). Used ONLY to impute Mode_Occupation - EnerGuide records
# no tenure - so this column carries census structure, not EnerGuide signal.
OWNER_SHARE_BY_TYPE = {
    "Maison individuelle": 0.87,
    "Duplex":              0.62,
    "Maison en rangee":    0.62,
    "Triplex":             0.35,
    "Collective":          0.38,
}

RAKING_VARS = list(CENSUS_MARGINS_CALGARY_2021)


def impute_mode_occupation(df: pd.DataFrame, seed: int = 20260707) -> pd.DataFrame:
    """Draw Locataire/Proprietaire per record from P(tenure | Type_Logement).

    EnerGuide has no tenure field, but Mode_Occupation is both a BN node and a
    census raking margin. Imputing it conditionally on dwelling type gives the
    pseudo-survey a tenure column whose JOINT structure with type follows the
    census; the subsequent IPF pass then pins its marginal exactly. Fixed seed
    -> reproducible builds.
    """
    rng = np.random.default_rng(seed)
    p_owner = df["Type_Logement"].map(OWNER_SHARE_BY_TYPE)
    assert not p_owner.isna().any(), (
        "Type_Logement values missing from OWNER_SHARE_BY_TYPE: "
        f"{sorted(set(df['Type_Logement'][p_owner.isna()]))}"
    )
    df = df.copy()
    df["Mode_Occupation"] = np.where(
        rng.random(len(df)) < p_owner.to_numpy(), "Proprietaire", "Locataire"
    )
    return df


def _kish_neff(w: np.ndarray) -> float:
    """Kish effective sample size: (sum w)^2 / sum w^2."""
    return float(w.sum() ** 2 / np.square(w).sum()) if len(w) else 0.0


def ipf_rake(
    df: pd.DataFrame,
    margins: dict[str, dict[str, float]],
    max_iter: int = 200,
    tol: float = 1e-7,
    max_weight_ratio: float | None = 500.0,
    trim_rounds: int = 10,
    min_support: int = 50,
) -> tuple[np.ndarray, dict[str, dict[str, float]]]:
    """Iterative proportional fitting of row weights to categorical margins.

    Returns (weights, effective_margins). Weights are normalized to mean 1.

    Robustness mechanics:
    - **Zero-support fallback**: a target category with no rows in `df` is
      removed from its margin and the margin renormalized (loud warning) -
      IPF cannot move mass onto an empty category, and pretending otherwise
      is what makes naive implementations divide by zero. The dropped mass is
      reported so downstream CPT-building knows census coverage is partial.
    - **Sparse-category warning**: categories with < `min_support` rows still
      converge, but the warning + per-category Kish n_eff printed by the
      caller make the weight concentration explicit.
    - **Trim-and-re-rake**: after convergence, weights above
      `max_weight_ratio` x mean are capped and the IPF re-run on the capped
      weights (`trim_rounds` rounds). Trimming trades exact margin agreement
      for bounded single-row influence; the residual margin error is
      reported by the caller. Set `max_weight_ratio=None` to disable.
    """
    n = len(df)
    assert n > 0, "cannot rake an empty DataFrame"

    # -- validate categories & apply the zero-support fallback ------------- #
    eff_margins: dict[str, dict[str, float]] = {}
    for var, target in margins.items():
        observed = set(df[var].dropna().unique())
        rogue = observed - set(target)
        assert not rogue, f"{var}: data categories {sorted(rogue)} absent from census target"
        empty = {c for c in target if c not in observed}
        kept = {c: p for c, p in target.items() if c not in empty}
        if empty:
            lost = sum(target[c] for c in empty)
            print(f"  WARNING {var}: no sample support for {sorted(empty)} "
                  f"({lost:.1%} of census mass) - dropped from margin and renormalized")
        total = sum(kept.values())
        eff_margins[var] = {c: p / total for c, p in kept.items()}
        sparse = {c: int((df[var] == c).sum()) for c in kept
                  if (df[var] == c).sum() < min_support}
        if sparse:
            print(f"  WARNING {var}: critically sparse categories {sparse} "
                  f"(< {min_support} rows) - weights will concentrate, watch n_eff")

    # -- the IPF loop ------------------------------------------------------- #
    codes = {var: df[var].to_numpy() for var in eff_margins}
    w = np.ones(n)

    def _rake_until_converged(w: np.ndarray) -> tuple[np.ndarray, float]:
        for _ in range(max_iter):
            max_dev = 0.0
            for var, target in eff_margins.items():
                cur = pd.Series(w).groupby(codes[var]).sum()
                cur_share = cur / w.sum()
                # factor per category; guard: cur>0 for all kept categories
                factor = {c: target[c] / cur_share[c] for c in target}
                w = w * pd.Series(codes[var]).map(factor).to_numpy()
                dev = max(abs(cur_share[c] - target[c]) for c in target)
                max_dev = max(max_dev, dev)
            if max_dev < tol:
                break
        return w, max_dev

    w, _ = _rake_until_converged(w)

    # -- trim-and-re-rake ---------------------------------------------------- #
    if max_weight_ratio is not None:
        for round_ in range(trim_rounds):
            cap = max_weight_ratio * w.mean()
            over = w > cap
            if not over.any():
                break
            w = np.minimum(w, cap)
            w, _ = _rake_until_converged(w)
        if over.any():
            print(f"  trim: {int(over.sum())} weights still at the "
                  f"{max_weight_ratio:.0f}x-mean cap after {trim_rounds} rounds")

    return w / w.mean(), eff_margins


def rake_to_census_margins(
    df: pd.DataFrame,
    margins: dict[str, dict[str, float]] | None = None,
    max_weight_ratio: float | None = 500.0,
) -> pd.DataFrame:
    """Assign each record a census-calibrated weight POND_AB.

    Rakes over ALL records (existing + new cohorts together): the census
    describes the entire 2021 occupied stock, and nearly all of the sample's
    scarce Collective / >=2020 support lives in the new-construction cohort -
    excluding it would make those margins un-rakeable. Rows lacking a raking
    variable (invalid YEARBUILT) are dropped with a note.

    Prints a target-vs-achieved margin table (the convergence proof) plus
    weight-concentration diagnostics (max weight, Kish n_eff overall and for
    the sparsest dimension, Type_Logement).
    """
    margins = margins or CENSUS_MARGINS_CALGARY_2021

    if "Mode_Occupation" not in df.columns:
        df = impute_mode_occupation(df)

    n0 = len(df)
    df = df.dropna(subset=RAKING_VARS).copy()
    if len(df) < n0:
        print(f"  raking: dropped {n0 - len(df)} rows lacking a raking variable")

    w, eff_margins = ipf_rake(df, margins, max_weight_ratio=max_weight_ratio)
    df["POND_AB"] = w

    # ---- convergence proof: target vs achieved ---------------------------- #
    print("\n  === raking validation: census target vs weighted sample ===")
    for var, target in eff_margins.items():
        achieved = df.groupby(var)["POND_AB"].sum() / df["POND_AB"].sum()
        unweighted = df[var].value_counts(normalize=True)
        lines = pd.DataFrame({
            "target": pd.Series(target),
            "achieved": achieved,
            "unweighted": unweighted,
        }).reindex(target.keys())
        lines["abs_err"] = (lines["achieved"] - lines["target"]).abs()
        print(f"\n  {var}  (max |err| = {lines['abs_err'].max():.2e})")
        print(lines.round(4).to_string())

    # ---- weight-concentration diagnostics --------------------------------- #
    print("\n  weight diagnostics: "
          f"max={w.max():.1f}x mean, n={len(w):,}, "
          f"Kish n_eff={_kish_neff(w):,.0f} "
          f"({_kish_neff(w) / len(w):.1%} of nominal)")
    for cat, grp in df.groupby("Type_Logement")["POND_AB"]:
        print(f"    n_eff[{cat}] = {_kish_neff(grp.to_numpy()):,.0f} "
              f"(n={len(grp):,})")
    return df


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #

def build(save: bool = True) -> pd.DataFrame:
    df = load_energuide()
    df, _ = resolve_restatements(df)
    df = dedupe_stock(df)

    mapper = EnerGuideToBN()
    mapper.verify_against_bnyml()
    df = mapper.apply(df)

    n_bad_year = df["An_Construction"].isna().sum()
    if n_bad_year:
        print(f"  note: {n_bad_year} houses with invalid YEARBUILT "
              f"(outside [{YEARBUILT_MIN}, {YEARBUILT_MAX}]) -> An_Construction=NaN")

    df = rake_to_census_margins(df)

    # ---- sanity report ---------------------------------------------------- #
    print("\n=== sanity report ===")
    print("\nSource_Energie_Chauf shares (unweighted -> census-weighted):")
    report = pd.DataFrame({
        "unweighted": df["Source_Energie_Chauf"].value_counts(normalize=True),
        "weighted": df.groupby("Source_Energie_Chauf")["POND_AB"].sum()
                      / df["POND_AB"].sum(),
    })
    print(report.round(4).to_string())
    print("\nAn_Construction x Type_Logement (unweighted counts):")
    xtab = pd.crosstab(df["An_Construction"], df["Type_Logement"])
    xtab = xtab.reindex(EnerGuideToBN.AN_CONSTRUCTION_LABELS)
    print(xtab.to_string())

    if save:
        df.to_parquet(OUT_PATH, index=False)
        print(f"\nwrote {len(df):,} rows -> {OUT_PATH.relative_to(REPO_ROOT)}")
    return df


# --------------------------------------------------------------------------- #
# Combine step (was build_energuide_dataset.py): the 20 per-year EnerGuide pulls
# -> one de-duplicated evaluation table and one house-level table.
# --------------------------------------------------------------------------- #

EVALUATIONS_PATH = ENERGUIDE_DIR / "energuide_ab_evaluations.parquet"
HOUSES_PATH = ENERGUIDE_DIR / "energuide_ab_houses.parquet"
COMBINED_MANIFEST_PATH = ENERGUIDE_DIR / "energuide_ab_combined_manifest.json"


def combine_energuide() -> None:
    """Combine + de-duplicate the raw per-year pulls into two tables:
    energuide_ab_evaluations.parquet (one row per evaluation) and
    energuide_ab_houses.parquet (one row per house). See resolve_restatements /
    dedupe_stock above for the de-duplication rules.
    """
    print("Loading raw per-year pulls")
    raw = load_energuide()
    n_raw = len(raw)

    # Keep _id for traceability but rename it so nothing mistakes a per-resource
    # row number for a stable record id.
    if "_id" in raw.columns:
        raw = raw.rename(columns={"_id": "source_row_id"})

    print("\nBuilding evaluation-level table")
    evaluations, restatements = resolve_restatements(raw)
    for entry in restatements:
        print(f"    HOUSEID={entry['HOUSEID']} "
              f"EVAL={entry['EVALUATIONSID']}/{entry['EVALTYPE']} "
              f"{entry['source_files']} -> kept {entry['kept_from']} "
              f"({entry['n_differing_columns']} column(s) differ)")
    assert not evaluations.duplicated(RECORD_KEY).any(), \
        "evaluation table still holds duplicate record keys"
    print(f"  {n_raw:,} raw rows -> {len(evaluations):,} evaluations")
    print("  EVALTYPE breakdown: "
          + ", ".join(f"{k}={v:,}" for k, v
                      in evaluations["EVALTYPE"].value_counts().items()))
    evaluations.to_parquet(EVALUATIONS_PATH, index=False)
    print(f"  wrote {EVALUATIONS_PATH.relative_to(REPO_ROOT)}")

    print("\nBuilding house-level table")
    houses = dedupe_stock(evaluations)
    assert not houses.duplicated("HOUSEID").any(), \
        "house table still holds duplicate HOUSEIDs"
    houses.to_parquet(HOUSES_PATH, index=False)
    print(f"  wrote {HOUSES_PATH.relative_to(REPO_ROOT)}")

    manifest = {
        "inputs": sorted(
            f.name for f in ENERGUIDE_DIR.glob("energuide_ab_[0-9]*.parquet")
        ),
        "record_key": RECORD_KEY,
        "rows_raw": n_raw,
        "rows_evaluations": len(evaluations),
        "rows_houses": len(houses),
        "restatements_resolved": len(restatements),
        "restatement_detail": restatements,
        "evaltype_counts_evaluations":
            {str(k): int(v) for k, v
             in evaluations["EVALTYPE"].value_counts().items()},
        "cohort_counts_houses":
            {str(k): int(v) for k, v
             in houses["cohort"].value_counts().items()},
    }
    COMBINED_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"  wrote {COMBINED_MANIFEST_PATH.name}")
    print(f"\nDone. {n_raw:,} raw rows -> {len(evaluations):,} evaluations "
          f"-> {len(houses):,} houses")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Combine + weight the EnerGuide Alberta pull for Calgary")
    ap.add_argument("step", nargs="?", default="all",
                    choices=["all", "combine", "weights"],
                    help="combine = house/evaluation tables; "
                         "weights = map+rake -> alberta_stock_mapped.parquet")
    args = ap.parse_args()
    if args.step in ("all", "combine"):
        combine_energuide()
    if args.step in ("all", "weights"):
        build()


if __name__ == "__main__":
    main()
