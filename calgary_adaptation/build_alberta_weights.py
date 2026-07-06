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


