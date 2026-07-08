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
    python calgary_adaptation/build_alberta_weights.py
Writes data/input/alberta/energuide/alberta_stock_mapped.parquet and prints a
sanity report.
"""

from __future__ import annotations

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
    files = sorted(ENERGUIDE_DIR.glob("energuide_ab_*.parquet"))
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
          .first()
          .drop(columns=["_rank", "_date"])
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


if __name__ == "__main__":
    build()
