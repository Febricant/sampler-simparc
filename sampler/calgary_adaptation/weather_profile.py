"""
Per-neighbourhood temperature / degree-day weather profile for Calgary, from
local NSRDB data.

Replaces the single hardcoded Calgary-airport weather file (used citywide by the
sampler) with a neighbourhood-by-year view of recent actual weather. Reads the
local NREL NSRDB export - 60 grid points x 8 years (2018-2025) of hourly outdoor
temperature over Calgary - assigns each grid point to the forward sortation area
(FSA = first 3 characters of a postal code, e.g. "T2E") that contains it, and
summarizes temperature and heating/cooling degree-days per FSA per year.

Honest scope: this NSRDB export is TEMPERATURE ONLY (no sunlight / humidity /
wind), so it cannot build a full simulator weather file - the recent, multi-year,
neighbourhood-resolved temperature is the value here (vs the single 2020 typical
year the simulator still uses). The grid is a ~11 x 13 km box over central
Calgary, and prairie temperature is nearly uniform, so the recent-years dimension
is the real gain, not fine spatial detail.

Usage (from repo root):
    uv run python calgary_adaptation/weather_profile.py
Writes data/output/calgary_fsa_weather_profile.csv and prints a report. No
network: reads the local NSRDB folder + the cached FSA boundary file.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from _shared import LambertNAD83, load_calgary_fsa_shapes

REPO_ROOT = Path(__file__).resolve().parents[1]
NSRDB_DIR = REPO_ROOT / "22e393a6216edb1d2f9c7f83062bd235" / "22e393a6216edb1d2f9c7f83062bd235"
OUT_PATH = REPO_ROOT / "data" / "output" / "calgary_fsa_weather_profile.csv"

# Degree-day base (Canada standard is 18 C, hourly method -> C-days).
DD_BASE = 18.0
NSRDB_FILE_RE = re.compile(r"^(\d+)_([\d.]+)_(-?[\d.]+)_(\d{4})\.csv$")


# --------------------------------------------------------------------------- #
# NSRDB grid: per grid-point x year temperature / degree-day stats
# --------------------------------------------------------------------------- #

def load_grid_point_stats() -> pd.DataFrame:
    files = sorted(NSRDB_DIR.glob("*.csv"))
    assert files, f"no NSRDB CSVs under {NSRDB_DIR}"
    records = []
    for i, f in enumerate(files, 1):
        m = NSRDB_FILE_RE.match(f.name)
        if not m:
            continue
        loc_id, lat, lon, year = m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4))
        # 2 metadata rows, then a header row (Year,Month,Day,Hour,Minute,Temperature)
        t = pd.read_csv(f, skiprows=2, usecols=["Temperature"])["Temperature"].to_numpy(float)
        below = np.clip(DD_BASE - t, 0, None)
        above = np.clip(t - DD_BASE, 0, None)
        records.append({
            "loc_id": loc_id, "lat": lat, "lon": lon, "year": year,
            "n_hours": len(t),
            "mean_temp_C": float(t.mean()),
            "hdd18": float(below.sum() / 24.0),
            "cdd18": float(above.sum() / 24.0),
            "tmin": float(t.min()), "tmax": float(t.max()),
        })
        if i % 100 == 0:
            print(f"  read {i}/{len(files)} NSRDB files")
    df = pd.DataFrame(records)
    print(f"NSRDB: {df['loc_id'].nunique()} grid points x "
          f"{df['year'].nunique()} years ({df['year'].min()}-{df['year'].max()}), "
          f"{len(df)} point-years")
    return df


# --------------------------------------------------------------------------- #
# Assign grid points -> FSAs, aggregate to FSA x year
# --------------------------------------------------------------------------- #

def assign_points_to_fsas(points: pd.DataFrame, paths: dict,
                          centroids: dict) -> pd.DataFrame:
    """Add an `fsa_contains` column: the FSA whose polygon contains each grid
    point (blank if none). Grid points are projected into the boundary file's
    Lambert metres so they can be tested against the polygons."""
    proj = LambertNAD83()
    grid = points[["loc_id", "lat", "lon"]].drop_duplicates("loc_id").copy()
    xy = grid.apply(lambda r: proj.forward(r["lat"], r["lon"]), axis=1)
    grid["x"] = [p[0] for p in xy]
    grid["y"] = [p[1] for p in xy]

    contain: dict[str, str] = {}
    for _, g in grid.iterrows():
        hit = ""
        for fsa, path in paths.items():
            if path.contains_point((g["x"], g["y"])):
                hit = fsa
                break
        contain[g["loc_id"]] = hit

    grid["fsa_contains"] = grid["loc_id"].map(contain)
    n_contained = int((grid["fsa_contains"] != "").sum())
    print(f"grid->FSA: {n_contained}/{len(grid)} points fall inside a Calgary FSA")
    return grid


def build(save: bool = True) -> pd.DataFrame:
    shapes = load_calgary_fsa_shapes()
    paths = {f: p for f, (p, c) in shapes.items()}
    centroids = {f: c for f, (p, c) in shapes.items()}
    print(f"FSA boundaries: {len(paths)} Calgary FSAs")

    points = load_grid_point_stats()
    grid = assign_points_to_fsas(points, paths, centroids)

    stat_cols = ["mean_temp_C", "hdd18", "cdd18", "tmin", "tmax"]
    years = sorted(points["year"].unique())

    rows = []
    for fsa in sorted(paths):
        members = grid.loc[grid["fsa_contains"] == fsa, "loc_id"].tolist()
        method = "contains"
        if not members:
            # nearest grid point to this FSA's centroid
            fx, fy = centroids[fsa]
            d = ((grid["x"] - fx) ** 2 + (grid["y"] - fy) ** 2) ** 0.5
            members = [grid.loc[d.idxmin(), "loc_id"]]
            method = "nearest"
        sub = points[points["loc_id"].isin(members)]
        for year in years:
            yr = sub[sub["year"] == year]
            if yr.empty:
                continue
            row = {"FSA": fsa, "year": year, "n_grid_points": len(yr), "method": method}
            for c in stat_cols:
                row[c] = round(float(yr[c].mean()), 2)
            rows.append(row)

    profile = pd.DataFrame(rows).sort_values(["FSA", "year"]).reset_index(drop=True)
    if save:
        profile.to_csv(OUT_PATH, index=False)

    # ---- report ----------------------------------------------------------- #
    print(f"\nwrote {len(profile)} rows ({profile['FSA'].nunique()} FSAs x "
          f"{profile['year'].nunique()} years) -> {OUT_PATH.relative_to(REPO_ROOT)}")
    n_nearest = profile.loc[profile["method"] == "nearest", "FSA"].nunique()
    print(f"  {profile['FSA'].nunique() - n_nearest} FSAs use interior grid points, "
          f"{n_nearest} fall back to nearest.")

    print("\n=== city-mean by year (the recent-actuals signal) ===")
    city = (profile.groupby("year")
                   .agg(mean_temp_C=("mean_temp_C", "mean"),
                        hdd18=("hdd18", "mean"),
                        cdd18=("cdd18", "mean"))
                   .round(1))
    print(city.to_string())

    fsa_mean = profile.groupby("FSA")["mean_temp_C"].mean()
    fsa_hdd = profile.groupby("FSA")["hdd18"].mean()
    print(f"\nintra-city spread (8-yr FSA means): "
          f"temp {fsa_mean.min():.1f}..{fsa_mean.max():.1f} C "
          f"(range {fsa_mean.max() - fsa_mean.min():.2f}), "
          f"HDD18 {fsa_hdd.min():.0f}..{fsa_hdd.max():.0f} "
          f"(range {fsa_hdd.max() - fsa_hdd.min():.0f} C-days)")
    print("  -> temperature is nearly uniform citywide; the multi-year dimension is the gain.")
    return profile


if __name__ == "__main__":
    build()
