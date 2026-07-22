"""
Calgary regional energy-use profile via weighted bootstrap
(Alberta re-calibration action items #2-#7).

Estimates the average household energy-use intensity (MEUI, kWh/m2/yr) for the
Calgary housing stock, WITH an uncertainty band, by resampling EnerGuide homes
to match the 2021 census composition many times over.

The procedure (the "100 buildings -> 80 homes census -> 80 from EnerGuide,
average, repeat" recipe) is a post-stratified bootstrap:

    1. The census fixes the regional stock composition (dwelling type x vintage
       x tenure), via CENSUS_MARGINS_CALGARY_2021 in build_alberta_weights.py.
    2. Each EnerGuide home is binned into those same census cells ("intersect").
    3. IPF raking gives every home a weight so the weighted sample reproduces
       ALL census margins jointly - so drawing homes with probability
       proportional to that weight reproduces the census composition across
       type AND vintage AND tenure at once (the multi-dimensional generalization
       of the per-type quota in the example).
    4. Draw n homes with replacement ~ weight, average their MEUI; repeat K
       times -> a distribution of the regional mean -> point estimate + 95% CI.

Modelling assumption ("assume the Quebec survey is randomly distributed"):
within each census cell, EnerGuide homes are treated as a random, representative
sample of that cell's true population, so within-cell draws are uniform and a
home's only role is its cell membership.

See calgary_adaptation/ENERGY_PROFILE_METHODOLOGY.md for the diagram and prose.

This module merges the former build_energy_profile / build_area_energy_profile /
make_calgary_meui_map / make_energuide_figures scripts behind one command.

Usage (from repo root):
    uv run python calgary_adaptation/energy_profile.py [all|city|area|map|describe]
`city` -> calgary_energy_profile.csv + figs 19-21; `area` ->
calgary_fsa_energy_profile.csv + figs 22-23; `map` -> fig 24; `describe` ->
figs 01-18. `all` (default) runs describe, city, area, map.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath

from _shared import (
    AQUA, BASELINE, BLUE, GRID, INK, INK_2, MUTED, SURFACE, VIOLET, YELLOW,
    apply_style, load_calgary_fsa_shapes,
)
from calibrate_stock import (
    CENSUS_MARGINS_CALGARY_2021,
    ENERGUIDE_DIR,
    EnerGuideToBN,
    _kish_neff,
    ipf_rake,
    rake_to_census_margins,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STOCK_PATH = ENERGUIDE_DIR / "alberta_stock_mapped.parquet"
OUT_CSV = REPO_ROOT / "data" / "output" / "calgary_energy_profile.csv"
FIG_DIR = Path(__file__).resolve().parent / "figures"

# ---- Configuration --------------------------------------------------------- #
REGION_CITY = "CALGARY"       # matched against CLIENTCITY.strip().upper()
METRIC = "MEUI"               # energy quantity to profile (kWh/m2/yr)
METRIC_UNIT = "kWh/m2/yr"
N_BOOTSTRAP = 5000            # Monte Carlo iterations
SEED = 20260720
# Draws per iteration; None -> the pool size (so the CI reflects the real sample
# size). Set to e.g. 100 to model a smaller "region of N buildings".
SAMPLE_SIZE: int | None = None

# The two stratification dimensions we report a per-cell profile for. Tenure
# (Mode_Occupation) is a raking margin but imputed, not an EnerGuide signal, so
# we don't break the profile out by it.
PROFILE_DIMS = ["Type_Logement", "An_Construction"]

# Shared palette + matplotlib style (see _shared.py).
apply_style()

# Vintage bins in chronological order for consistent figure/CSV ordering.
VINTAGE_ORDER = [
    "< 1950", "[1950 - 1960)", "[1960 - 1970)", "[1970 - 1980)",
    "[1980 - 1990)", "[1990 - 2000)", "[2000 - 2010)", "[2010 - 2020)",
    ">= 2020",
]


# --------------------------------------------------------------------------- #
# 1. Build the Calgary MEUI pool
# --------------------------------------------------------------------------- #

def load_calgary_meui_pool() -> pd.DataFrame:
    """Calgary homes with a usable MEUI, UNweighted, with a parsed `FSA` column.

    Reads the mapped stock (already carries the BN strata columns), restricts to
    Calgary, coerces MEUI to numeric, keeps MEUI-available rows, and parses the
    forward-sortation area from CLIENTPCODE (which stores the FSA only). This is
    the shared pool for both the city-wide profile (which then rakes it) and the
    area-based profile (which rakes it per FSA).
    """
    df = pd.read_parquet(STOCK_PATH)
    print(f"loaded {len(df):,} mapped Alberta homes")

    city = df["CLIENTCITY"].astype("string").str.strip().str.upper()
    cal = df[city == REGION_CITY].copy()
    print(f"  {len(cal):,} in {REGION_CITY.title()}")

    cal[METRIC] = pd.to_numeric(cal[METRIC], errors="coerce")
    pool = cal[cal[METRIC].notna()].copy()
    pool["FSA"] = (pool["CLIENTPCODE"].astype("string")
                   .str.replace(" ", "").str.upper().str[:3])
    print(f"  {len(pool):,} with a usable {METRIC} "
          f"({len(pool) / len(cal):.0%} coverage) - the resampling pool")
    return pool


def load_calgary_pool() -> pd.DataFrame:
    """The Calgary MEUI pool re-raked to Calgary census margins (mean-1 POND_AB).

    The existing POND_AB was raked over all of Alberta, so it does not reproduce
    Calgary margins on the Calgary subset; raking the subset itself gives a
    Calgary-correct weight on precisely the homes we resample.
    """
    pool = load_calgary_meui_pool().drop(columns=["POND_AB"], errors="ignore")
    print(f"\nre-raking the {REGION_CITY.title()} {METRIC} pool to census margins:")
    return rake_to_census_margins(pool)


# --------------------------------------------------------------------------- #
# 2. Weighted bootstrap
# --------------------------------------------------------------------------- #

def _boot_weighted_mean(y: np.ndarray, w: np.ndarray, n: int,
                        rng: np.random.Generator) -> np.ndarray:
    """N_BOOTSTRAP replicate weighted means from resampling the observed homes.

    Each replicate draws `n` home-indices UNIFORMLY with replacement (an
    ordinary nonparametric bootstrap of the observed sample) and recomputes the
    census-weighted mean sum(w*y)/sum(w) on the resampled homes. This is the
    textbook bootstrap for the standard error of a weighted mean: when the
    weight sits on a few homes (small Kish n_eff), whether those homes land in a
    given resample swings the weighted mean, so the interval widens honestly -
    unlike drawing n proportional-to-weight and taking a plain mean, whose
    spread collapses as n grows no matter how concentrated the weight is.
    """
    m = len(y)
    idx = rng.integers(0, m, size=(N_BOOTSTRAP, n))
    yb, wb = y[idx], w[idx]
    return (yb * wb).sum(axis=1) / wb.sum(axis=1)


def _summarize(reps: np.ndarray, y: np.ndarray, w: np.ndarray) -> dict:
    """Point estimate + 95% percentile CI.

    The point estimate is the DETERMINISTIC weighted mean, not the mean of the
    bootstrap replicates: for a ratio estimator with heavy weight concentration
    (small n_eff) the replicate distribution is skewed, so its mean is a biased
    summary while the deterministic weighted mean is exact. The replicates serve
    only to set the interval. `boot_mean` is retained for the diagnostic check.
    """
    return {
        f"mean_{METRIC}": float(np.average(y, weights=w)),
        "ci95_low": float(np.percentile(reps, 2.5)),
        "ci95_high": float(np.percentile(reps, 97.5)),
        "boot_mean": float(np.mean(reps)),
    }


def bootstrap_profile(pool: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """Bootstrap the census-weighted regional mean MEUI, overall and per stratum.

    Returns the profile table and the overall bootstrap replicates (for the
    distribution figure). Each stratum resamples only its own homes, so its CI
    reflects that cell's effective sample size.
    """
    rng = np.random.default_rng(SEED)
    y = pool[METRIC].to_numpy(dtype=float)
    w = pool["POND_AB"].to_numpy(dtype=float)
    n = SAMPLE_SIZE or len(pool)
    print(f"\nbootstrap: {N_BOOTSTRAP:,} iterations x n={n:,} resampled homes "
          f"(seed {SEED})")

    overall = _boot_weighted_mean(y, w, n, rng)
    rows: list[dict] = [{
        "dimension": "All", "stratum": f"All {REGION_CITY.title()}",
        "n": len(pool), "n_eff": round(_kish_neff(w)),
        **_summarize(overall, y, w),
    }]

    for dim in PROFILE_DIMS:
        order = VINTAGE_ORDER if dim == "An_Construction" else None
        cats = order or sorted(pool[dim].dropna().unique())
        for cat in cats:
            m = (pool[dim] == cat).to_numpy()
            if not m.any():
                continue
            yc, wc = y[m], w[m]
            nc = SAMPLE_SIZE or int(m.sum())
            reps = _boot_weighted_mean(yc, wc, nc, rng)
            rows.append({
                "dimension": dim, "stratum": cat,
                "n": int(m.sum()), "n_eff": round(_kish_neff(wc)),
                **_summarize(reps, yc, wc),
            })

    prof = pd.DataFrame(rows)
    # Sanity: on the well-supported overall figure the bootstrap centre must
    # match the deterministic weighted mean (per-cell divergence is expected and
    # meaningful where n_eff is tiny - it signals a skewed, wide interval).
    overall_row = prof.iloc[0]
    rel = abs(overall_row["boot_mean"] - overall_row[f"mean_{METRIC}"]) \
        / abs(overall_row[f"mean_{METRIC}"])
    assert rel < 0.02, \
        f"overall bootstrap mean diverges from weighted mean by {rel:.1%}"
    skewed = prof[abs(prof["boot_mean"] - prof[f"mean_{METRIC}"])
                  / prof[f"mean_{METRIC}"].abs() > 0.02]
    for _, r in skewed.iterrows():
        print(f"  note: {r['stratum']} has a skewed bootstrap "
              f"(n_eff={r['n_eff']}, boot mean {r['boot_mean']:.0f} vs "
              f"weighted {r[f'mean_{METRIC}']:.0f}) - wide interval, thin support")
    return prof, overall


# --------------------------------------------------------------------------- #
# 3. Figures
# --------------------------------------------------------------------------- #

def _save(fig, name: str) -> None:
    FIG_DIR.mkdir(exist_ok=True)
    out = FIG_DIR / name
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


def fig_bootstrap_distribution(overall: np.ndarray, summary: dict) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(overall, bins=60, color=BLUE, alpha=0.85, edgecolor=SURFACE)
    lo, hi, pt = summary["ci95_low"], summary["ci95_high"], summary[f"mean_{METRIC}"]
    for x, style in ((lo, ":"), (hi, ":"), (pt, "-")):
        ax.axvline(x, color=INK, linestyle=style, linewidth=1.2)
    ax.set_title(
        f"{REGION_CITY.title()} mean {METRIC} - bootstrap sampling distribution\n"
        f"{pt:.1f} {METRIC_UNIT}  (95% CI {lo:.1f}-{hi:.1f}), "
        f"{N_BOOTSTRAP:,} iterations")
    ax.set_xlabel(f"regional mean {METRIC} ({METRIC_UNIT})")
    ax.set_ylabel("bootstrap iterations")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    _save(fig, "19_meui_bootstrap_distribution.png")


def fig_ipf_reweight(pool: pd.DataFrame) -> None:
    """Raw vs raked vs census composition - what the IPF weights actually do.

    The raked series should land on the census series by construction; the point
    of plotting it is that a visible gap means the raking or the margins are
    wrong. Companion to fig_type_vs_census (02), which shows only the "before".
    """
    census = CENSUS_MARGINS_CALGARY_2021["Type_Logement"]
    order = list(census)
    labels = {
        "Maison individuelle": "Single-detached",
        "Maison en rangee": "Row house",
        "Duplex": "Semi / duplex",
        "Triplex": "Triplex",
        "Collective": "Apartment",
    }

    raw = pool["Type_Logement"].value_counts(normalize=True) * 100
    w = pool.groupby("Type_Logement")["POND_AB"].sum()
    raked = w / w.sum() * 100

    series = [
        ("EnerGuide sample (raw)", [raw.get(k, 0.0) for k in order], BLUE),
        ("after IPF raking", [raked.get(k, 0.0) for k in order], YELLOW),
        ("Census 2021 (target)", [census[k] * 100 for k in order], AQUA),
    ]

    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    for i, (label, vals, color) in enumerate(series):
        offset = (1 - i) * 0.27           # raw on top, census at the bottom
        bars = ax.barh(y - offset, vals, height=0.25, color=color, label=label,
                       edgecolor=SURFACE, linewidth=1)
        pct_labels(ax, bars, vals, dx=1.2)
    ax.set_yticks(y, [labels[k] for k in order])
    style_barh(ax, 105)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share of dwellings (%)")
    ax.legend(frameon=False, loc="lower right", labelcolor=INK_2)
    ax.set_title(
        "Raking pulls the sample onto the census\n"
        f"n = {len(pool):,} homes, Kish effective n = {_kish_neff(pool['POND_AB'].to_numpy()):,.0f}",
        loc="left")
    _save(fig, "25_ipf_reweight.png")


def fig_profile_bars(prof: pd.DataFrame, dim: str, title: str, fname: str) -> None:
    d = prof[prof["dimension"] == dim].copy()
    labels = d["stratum"].tolist()
    pt = d[f"mean_{METRIC}"].to_numpy()
    lo = pt - d["ci95_low"].to_numpy()
    hi = d["ci95_high"].to_numpy() - pt
    ypos = np.arange(len(d))

    fig, ax = plt.subplots(figsize=(7, 0.5 * len(d) + 1.6))
    ax.barh(ypos, pt, color=AQUA, alpha=0.85,
            xerr=[lo, hi], error_kw=dict(ecolor=INK_2, elinewidth=1.1, capsize=3))
    # Label past the upper whisker so it never overlaps the error bar.
    for y, v, hic, n in zip(ypos, pt, d["ci95_high"], d["n"]):
        ax.text(hic, y, f"  {v:.0f}  (n={n:,})", va="center", ha="left",
                color=INK_2, fontsize=8)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels)
    ax.set_title(title)
    ax.set_xlabel(f"mean {METRIC} ({METRIC_UNIT}), 95% CI whiskers")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    ax.set_xlim(0, max(d["ci95_high"]) * 1.45)
    _save(fig, fname)


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #

def run_city() -> None:
    pool = load_calgary_pool()
    prof, overall = bootstrap_profile(pool)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    cols = ["dimension", "stratum", "n", "n_eff",
            f"mean_{METRIC}", "ci95_low", "ci95_high"]
    prof[cols].to_csv(OUT_CSV, index=False)
    print(f"\nwrote {OUT_CSV.relative_to(REPO_ROOT)}")

    summary = prof.iloc[0].to_dict()
    print(f"\n=== {REGION_CITY.title()} regional {METRIC} profile ===")
    print(f"  {summary[f'mean_{METRIC}']:.1f} {METRIC_UNIT}  "
          f"(95% CI {summary['ci95_low']:.1f}-{summary['ci95_high']:.1f}), "
          f"n={summary['n']:,}, Kish n_eff={summary['n_eff']:,}")
    print("\n  per stratum:")
    print(prof[cols].round(1).to_string(index=False))

    print("\nfigures:")
    fig_ipf_reweight(pool)
    fig_bootstrap_distribution(overall, summary)
    fig_profile_bars(prof, "Type_Logement",
                     f"{REGION_CITY.title()} mean {METRIC} by dwelling type",
                     "20_meui_by_dwelling_type.png")
    fig_profile_bars(prof, "An_Construction",
                     f"{REGION_CITY.title()} mean {METRIC} by construction vintage",
                     "21_meui_by_vintage.png")

# ==========================================================================
# AREA-BASED PER-FSA PROFILE (was build_area_energy_profile.py)
# ==========================================================================
"""
Area-based Calgary energy-use profile (per-FSA -> aggregate).

The city-wide build (build_energy_profile.py) uses one Calgary composition. This
one works per census area (forward sortation area, FSA), the finest geography in
the data (EnerGuide CLIENTPCODE holds the FSA), and aggregates:

    for each FSA a:
        take a's census housing composition (type x vintage) and dwelling count N_a
        draw EnerGuide homes matching that composition, average their MEUI  -> m_a
        (bootstrapped -> a 95% CI on m_a)
    aggregate:  M = sum(N_a * m_a) / sum(N_a)      (population-weighted city mean)

This is the user's recipe made spatial: "get a census area, find its housing
composition, draw that many EnerGuide homes, average, repeat, aggregate."

Draw source is HYBRID (per the plan): an FSA with >= MIN_AREA_SUPPORT MEUI homes
draws from its OWN homes (captures real neighbourhood effects); a sparser FSA
BORROWS from the whole Calgary pool, composition-matched to that FSA. Both modes
IPF-rake to the FSA's census type x vintage margins, then bootstrap the weighted
mean. Reported twice - hybrid vs borrow-only - so the gap isolates the
neighbourhood signal the from-area FSAs add over pure composition-matching.

Assumption: BORROW mode assumes energy depends on home characteristics, not
location given composition (energy _|_ location | composition); FROM-AREA mode
relaxes it where the data allow. See AREA_ENERGY_PROFILE_METHODOLOGY.md.

Usage (from repo root):
    uv run python calgary_adaptation/energy_profile.py area
Requires data/input/alberta/census/calgary_fsa_composition.parquet
(run: python calgary_adaptation/fetch_data.py --only census).
"""

# ===== Area-based profile (merged); imports live at the top of energy_profile.py.

REPO_ROOT = Path(__file__).resolve().parents[1]
CENSUS_PATH = (REPO_ROOT / "data" / "input" / "alberta" / "census"
               / "calgary_fsa_composition.parquet")
OUT_FSA_CSV = REPO_ROOT / "data" / "output" / "calgary_fsa_energy_profile.csv"
FIG_DIR = Path(__file__).resolve().parent / "figures"

MIN_AREA_SUPPORT = 100       # >= this many MEUI homes -> draw from the FSA's own
AREA_SEED = 20260721

# Fold the pool's BN dwelling type onto the 4 census-backed area types. The BN's
# Triplex has no census counterpart, so it folds into Collective (multi-unit).
POOL_TYPE_TO_AREA = {
    "Maison individuelle": "individuelle",
    "Duplex": "duplex",
    "Maison en rangee": "rangee",
    "Collective": "collective",
    "Triplex": "collective",
}
TYPE_COLS = ["type_individuelle", "type_duplex", "type_rangee", "type_collective"]
TYPE_CATS = ["individuelle", "duplex", "rangee", "collective"]

# YEARBUILT -> the census period-of-construction bins (the FSA table's own 8).
VINT_EDGES = [-np.inf, 1960, 1980, 1990, 2000, 2005, 2010, 2015, np.inf]
VINT_CATS = ["vint_pre1961", "vint_1961_1980", "vint_1981_1990", "vint_1991_2000",
             "vint_2001_2005", "vint_2006_2010", "vint_2011_2015", "vint_2016plus"]


# --------------------------------------------------------------------------- #
# 1. Load pool + per-FSA census composition
# --------------------------------------------------------------------------- #

def load_pool_with_strata() -> pd.DataFrame:
    """Calgary MEUI pool with `area_type` and `vint` folded to census categories."""
    pool = load_calgary_meui_pool()
    pool["area_type"] = pool["Type_Logement"].map(POOL_TYPE_TO_AREA)
    yb = pd.to_numeric(pool["YEARBUILT"], errors="coerce")
    pool["vint"] = pd.cut(yb, bins=VINT_EDGES, labels=VINT_CATS, right=True)
    n0 = len(pool)
    pool = pool[pool["area_type"].notna() & pool["vint"].notna()].copy()
    pool["vint"] = pool["vint"].astype(str)
    if len(pool) < n0:
        print(f"  dropped {n0 - len(pool)} homes lacking a usable type/vintage")
    return pool


def load_census() -> pd.DataFrame:
    assert CENSUS_PATH.exists(), (
        f"{CENSUS_PATH} missing - run "
        "`python calgary_adaptation/fetch_data.py --only census`")
    c = pd.read_parquet(CENSUS_PATH).set_index("FSA")
    print(f"loaded census composition for {len(c)} Calgary FSAs "
          f"({int(c['dwelling_count'].sum()):,} dwellings)")
    return c


def _shares(counts: pd.Series, cols: list[str], cats: list[str]) -> dict[str, float]:
    """Census counts -> normalized shares over `cats`, dropping zero-share cells."""
    vals = counts[cols].fillna(0.0).to_numpy(dtype=float)
    total = vals.sum()
    if total <= 0:
        return {}
    return {cat: v / total for cat, v in zip(cats, vals) if v > 0}


# --------------------------------------------------------------------------- #
# 2. Per-FSA weighting + bootstrap
# --------------------------------------------------------------------------- #

def _rake_quiet(df: pd.DataFrame, margins: dict) -> np.ndarray | None:
    """IPF-rake `df` to `margins` (type + vintage), suppressing its chatter.

    Restricts `df` to homes whose categories have positive census share in this
    FSA (so a category the FSA lacks cannot leak in), then rakes. Returns mean-1
    weights aligned to the returned index, or None if nothing is rakeable.
    """
    keep = (df["area_type"].isin(margins["area_type"])
            & df["vint"].isin(margins["vint"]))
    sub = df[keep]
    if len(sub) < 5:
        return None, sub
    with contextlib.redirect_stdout(io.StringIO()):
        w, _ = ipf_rake(sub, margins, max_weight_ratio=500.0)
    return w, sub


def bootstrap_fsa(y: np.ndarray, w: np.ndarray, n: int,
                  rng: np.random.Generator) -> tuple[float, np.ndarray]:
    """Deterministic weighted mean + K bootstrap replicate means."""
    return float(np.average(y, weights=w)), _boot_weighted_mean(y, w, n, rng)


def build_profile(pool: pd.DataFrame, census: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(AREA_SEED)
    by_fsa = {f: g for f, g in pool.groupby("FSA")}

    rows: list[dict] = []
    reps_borrow: dict[str, np.ndarray] = {}   # every FSA (borrow-only aggregate)
    reps_hybrid: dict[str, np.ndarray] = {}   # from-area where supported, else borrow

    for fsa, crow in census.iterrows():
        margins = {
            "area_type": _shares(crow, TYPE_COLS, TYPE_CATS),
            "vint": _shares(crow, VINT_CATS, VINT_CATS),
        }
        N_a = float(crow["dwelling_count"])
        own = by_fsa.get(fsa, pool.iloc[0:0])
        n_own = len(own)

        # BORROW: rake the whole city pool to this FSA's composition.
        wb, sub_b = _rake_quiet(pool, margins)
        if wb is None:
            print(f"  {fsa}: not rakeable, skipped")
            continue
        yb = sub_b[METRIC].to_numpy(float)
        m_borrow, rep_borrow = bootstrap_fsa(yb, wb, len(yb), rng)
        reps_borrow[fsa] = rep_borrow

        use_area = n_own >= MIN_AREA_SUPPORT
        if use_area:
            wa, sub_a = _rake_quiet(own, margins)
            if wa is None:               # FSA sample too thin after category align
                use_area = False
        if use_area:
            ya = sub_a[METRIC].to_numpy(float)
            m_a, rep_a = bootstrap_fsa(ya, wa, len(ya), rng)
            n_eff = _kish_neff(wa)
            method = "from-area"
            reps_hybrid[fsa] = rep_a
        else:
            m_a, rep_a = m_borrow, rep_borrow
            n_eff = _kish_neff(wb)
            method = "borrow"
            reps_hybrid[fsa] = rep_borrow

        rows.append({
            # n_local = MEUI homes physically in this FSA (the support that
            # decides from-area vs borrow); n_eff = effective sample of the
            # estimate actually used (for a borrowed FSA this is the
            # composition-matched city draw, so it can exceed n_local).
            "FSA": fsa, "N_a": N_a, "n_local": n_own, "n_eff": round(n_eff),
            "method": method,
            f"mean_{METRIC}": m_a,
            "ci95_low": float(np.percentile(rep_a, 2.5)),
            "ci95_high": float(np.percentile(rep_a, 97.5)),
            # share of dwellings built pre-1980, for the spatial-signal figure
            "pre1980_share": float(
                (crow[["vint_pre1961", "vint_1961_1980"]].fillna(0).sum())
                / max(crow[VINT_CATS].fillna(0).sum(), 1)),
        })

    prof = pd.DataFrame(rows).sort_values(f"mean_{METRIC}").reset_index(drop=True)
    agg = _aggregate(prof, reps_borrow, reps_hybrid)
    return pd.concat([agg, prof], ignore_index=True)


def _aggregate(prof: pd.DataFrame, reps_borrow: dict, reps_hybrid: dict) -> pd.DataFrame:
    """Population-weighted city mean + CI, for hybrid and borrow-only."""
    N = prof.set_index("FSA")["N_a"]

    def combine(reps: dict) -> tuple[float, np.ndarray]:
        fsas = [f for f in prof["FSA"] if f in reps]
        w = N.loc[fsas].to_numpy(float)
        R = np.vstack([reps[f] for f in fsas])          # (n_fsa, K)
        Mk = (w[:, None] * R).sum(0) / w.sum()          # (K,)
        M = float((w * np.array([np.mean(reps[f]) for f in fsas])).sum() / w.sum())
        return M, Mk

    m_h, mk_h = combine(reps_hybrid)
    m_b, mk_b = combine(reps_borrow)
    print(f"\naggregate mean {METRIC}:")
    print(f"  hybrid      {m_h:6.1f}  (95% CI {np.percentile(mk_h,2.5):.1f}"
          f"-{np.percentile(mk_h,97.5):.1f})")
    print(f"  borrow-only {m_b:6.1f}  (95% CI {np.percentile(mk_b,2.5):.1f}"
          f"-{np.percentile(mk_b,97.5):.1f})")
    print(f"  neighbourhood signal (hybrid - borrow): {m_h - m_b:+.1f} {METRIC_UNIT}")
    return pd.DataFrame([
        {"FSA": "AGG (hybrid)", "N_a": N.sum(), "n_local": len(prof), "n_eff": np.nan,
         "method": "aggregate", f"mean_{METRIC}": m_h,
         "ci95_low": float(np.percentile(mk_h, 2.5)),
         "ci95_high": float(np.percentile(mk_h, 97.5)), "pre1980_share": np.nan},
        {"FSA": "AGG (borrow-only)", "N_a": N.sum(), "n_local": len(prof), "n_eff": np.nan,
         "method": "aggregate", f"mean_{METRIC}": m_b,
         "ci95_low": float(np.percentile(mk_b, 2.5)),
         "ci95_high": float(np.percentile(mk_b, 97.5)), "pre1980_share": np.nan},
    ])


# --------------------------------------------------------------------------- #
# 3. Figures
# --------------------------------------------------------------------------- #

def fig_ranked(prof: pd.DataFrame) -> None:
    d = prof[prof["method"] != "aggregate"].copy()
    d = d.sort_values(f"mean_{METRIC}")
    y = np.arange(len(d))
    pt = d[f"mean_{METRIC}"].to_numpy()
    lo = pt - d["ci95_low"].to_numpy()
    hi = d["ci95_high"].to_numpy() - pt
    colors = np.where(d["method"].to_numpy() == "from-area", BLUE, YELLOW)

    fig, ax = plt.subplots(figsize=(7, 0.28 * len(d) + 1.4))
    ax.barh(y, pt, color=colors, alpha=0.85,
            xerr=[lo, hi], error_kw=dict(ecolor=INK_2, elinewidth=0.9, capsize=2))
    ax.set_yticks(y)
    ax.set_yticklabels(d["FSA"], fontsize=7)
    ax.set_title(f"Calgary mean {METRIC} by FSA (95% CI)\n"
                 f"blue = drawn from the FSA's own homes, "
                 f"yellow = borrowed (composition-matched)")
    ax.set_xlabel(f"mean {METRIC} ({METRIC_UNIT})")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    _save(fig, "22_fsa_meui_ranked.png")


def fig_vs_vintage(prof: pd.DataFrame) -> None:
    d = prof[prof["method"] != "aggregate"].copy()
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    fa = d["method"] == "from-area"
    ax.scatter(d.loc[fa, "pre1980_share"] * 100, d.loc[fa, f"mean_{METRIC}"],
               s=28, color=BLUE, label="from-area", zorder=3)
    ax.scatter(d.loc[~fa, "pre1980_share"] * 100, d.loc[~fa, f"mean_{METRIC}"],
               s=28, color=YELLOW, label="borrow", zorder=3)
    ax.set_title(f"Older FSAs use more energy\n"
                 f"per-FSA mean {METRIC} vs share of dwellings built before 1980")
    ax.set_xlabel("share built before 1980 (%)")
    ax.set_ylabel(f"mean {METRIC} ({METRIC_UNIT})")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    _save(fig, "23_fsa_meui_vs_vintage.png")


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #

def run_area() -> None:
    pool = load_pool_with_strata()
    census = load_census()
    # keep only FSAs present in both the census and the pool
    census = census[census.index.isin(pool["FSA"].unique())]
    print(f"  {len(census)} FSAs common to census and the EnerGuide pool")

    prof = build_profile(pool, census)

    OUT_FSA_CSV.parent.mkdir(parents=True, exist_ok=True)
    cols = ["FSA", "N_a", "n_local", "n_eff", "method",
            f"mean_{METRIC}", "ci95_low", "ci95_high", "pre1980_share"]
    prof[cols].to_csv(OUT_FSA_CSV, index=False)
    print(f"\nwrote {OUT_FSA_CSV.relative_to(REPO_ROOT)}")

    n_area = (prof["method"] == "from-area").sum()
    n_borrow = (prof["method"] == "borrow").sum()
    print(f"  {n_area} FSAs from-area, {n_borrow} borrowed")
    print("\nper-FSA profile (sorted by mean):")
    print(prof[cols].round(2).to_string(index=False))

    print("\nfigures:")
    fig_ranked(prof)
    fig_vs_vintage(prof)

# ==========================================================================
# FSA CHOROPLETH MAP (was make_calgary_meui_map.py)
# ==========================================================================
# ===== FSA choropleth map (merged into energy_profile.py; imports live at the
# top of that module). Draws figure 24 from the per-FSA profile CSV, using the
# shared boundary loader (_shared.load_calgary_fsa_shapes). No geopandas/GDAL.

PROFILE_CSV = REPO_ROOT / "data" / "output" / "calgary_fsa_energy_profile.csv"


def make_map() -> None:
    """FSA choropleth of mean MEUI (figure 24). Requires the area profile CSV."""
    assert PROFILE_CSV.exists(), (
        f"{PROFILE_CSV} missing - run the area profile first (energy_profile.py area)")
    prof = pd.read_csv(PROFILE_CSV)
    prof = prof[prof["method"] != "aggregate"].copy()
    values = dict(zip(prof["FSA"], prof["mean_MEUI"]))
    method = dict(zip(prof["FSA"], prof["method"]))

    shapes = load_calgary_fsa_shapes()
    paths = {f: p for f, (p, c) in shapes.items() if f in values}
    centroids = {f: c for f, (p, c) in shapes.items() if f in values}
    missing = set(values) - set(paths)
    if missing:
        print(f"  WARNING: no boundary for {sorted(missing)}")
    print(f"drawing {len(paths)} FSA polygons")

    vmin = float(np.floor(prof["mean_MEUI"].min() / 10) * 10)
    vmax = float(np.ceil(prof["mean_MEUI"].max() / 10) * 10)
    cmap = plt.get_cmap("YlOrRd")
    norm = plt.Normalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    patches, colors = [], []
    for fsa, path in paths.items():
        patches.append(PathPatch(path))
        colors.append(values[fsa])
    pc = PatchCollection(patches, edgecolor="white", linewidths=0.6)
    pc.set_array(np.asarray(colors))
    pc.set_cmap(cmap)
    pc.set_norm(norm)
    ax.add_collection(pc)

    # Label each FSA at its centroid; ring the borrowed FSAs (dashed) so the
    # reader knows which rest on the borrow assumption.
    for fsa, path in paths.items():
        cx, cy = centroids[fsa]
        borrowed = method.get(fsa) == "borrow"
        ax.text(cx, cy, fsa, ha="center", va="center", fontsize=6,
                color=INK if norm(values[fsa]) < 0.6 else "white",
                weight="bold" if borrowed else "normal")
        if borrowed:
            ax.add_patch(PathPatch(path, fill=False, edgecolor=INK_2,
                                   linewidth=1.1, linestyle=(0, (3, 2))))

    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Mean household energy-use intensity across Calgary\n"
                 "EnerGuide MEUI (kWh/m²·yr)", fontsize=12, color=INK)

    cb = fig.colorbar(pc, ax=ax, shrink=0.6, pad=0.02)
    cb.set_label("mean MEUI (kWh/m²·yr)", color=INK_2)
    cb.outline.set_edgecolor(BASELINE)

    agg = pd.read_csv(PROFILE_CSV)
    hyb = agg.loc[agg["FSA"] == "AGG (hybrid)", "mean_MEUI"]
    if len(hyb):
        ax.text(0.01, 0.01, f"city aggregate: {hyb.iloc[0]:.0f} kWh/m²·yr",
                transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")

    FIG_DIR.mkdir(exist_ok=True)
    out = FIG_DIR / "24_calgary_meui_map.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")

# ==========================================================================
# DESCRIPTIVE FIGURES 01-18 (was make_energuide_figures.py)
# ==========================================================================
"""
Simple one-panel matplotlib figures describing the EnerGuide Alberta pull
(data/input/alberta/energuide/*.parquet). Each figure is saved individually
under calgary_adaptation/figures/.

Stock-composition figures use one record per house (latest evaluation, so a
retrofitted house counts in its post-retrofit state); volume figures use all
evaluation rows.

Usage:
    python calgary_adaptation/energy_profile.py describe
"""

# ===== Descriptive EnerGuide figures 01-18 (merged into energy_profile.py;
# imports + palette live at the top of that module).

# Census margins + the type mapping come from calibrate_stock (single source).
CENSUS_TYPE = CENSUS_MARGINS_CALGARY_2021["Type_Logement"]
CENSUS_VINTAGE = CENSUS_MARGINS_CALGARY_2021["An_Construction"]
TYPE_LOGEMENT = EnerGuideToBN.TYPE_LOGEMENT
FUEL_MAP = {  # figure-specific English relabelling (not the BN's French mapping)
    "natural gas": "Natural gas", "propane": "Natural gas",
    "electricity": "Electricity", "oil": "Oil",
    "mixed wood": "Wood", "hardwood": "Wood", "softwood": "Wood",
    "wood pellets": "Wood",
}
VINTAGE_EDGES = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
VINTAGE_LABELS = list(CENSUS_VINTAGE)


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #

def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(all evaluation rows, one latest record per house)."""
    parts = []
    # [0-9] keeps this to the raw per-year pulls; the derived tables written by
    # build_energuide_dataset.py share the energuide_ab_ prefix and would
    # otherwise be concatenated in on top of their own inputs.
    for f in sorted(ENERGUIDE_DIR.glob("energuide_ab_[0-9]*.parquet")):
        d = pd.read_parquet(f)
        d["_yearfile"] = f.stem.replace("energuide_ab_", "")
        parts.append(d)
    df = pd.concat(parts, ignore_index=True).replace("", np.nan)
    df["_date"] = pd.to_datetime(df["ENTRYDATE"], errors="coerce")

    houses = df[df["HOUSEID"].notna()].copy()
    # latest evaluation per house; E ranks above D on same-month ties and N
    # above P always, so the kept record is the house's current state.
    houses["_tie"] = houses["EVALTYPE"].map({"E": 0, "N": 0, "D": 1, "P": 2})
    houses = (
        houses.sort_values(["HOUSEID", "_date", "_tie"],
                           ascending=[True, False, True])
              .drop_duplicates("HOUSEID")
    )
    return df, houses


def pct_labels(ax, bars, values, dx=0.5):
    """Value label at each bar end - ink colored, never the series color."""
    for bar, v in zip(bars, values):
        if 0 < v < 0.05:
            txt = "<0.1%"
        elif v >= 99:
            txt = f"{v:.2f}%"
        else:
            txt = f"{v:.1f}%"
        ax.text(bar.get_width() + dx, bar.get_y() + bar.get_height() / 2,
                txt, va="center", ha="left", fontsize=9, color=INK_2)


def style_barh(ax, xmax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlim(0, xmax)
    ax.invert_yaxis()


save = _save  # shared saver (defined in the city-profile section above)


# --------------------------------------------------------------------------- #
# Figures
# --------------------------------------------------------------------------- #

def fig_heating_fuel(houses: pd.DataFrame):
    stock = houses[houses["EVALTYPE"].isin(["D", "E"])]
    fuel = (stock["FURNACEFUEL"].str.strip().str.casefold()
            .map(FUEL_MAP).fillna("Other"))
    share = fuel.value_counts(normalize=True) * 100
    share = share.reindex(["Natural gas", "Electricity", "Wood", "Oil", "Other"]).dropna()

    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    bars = ax.barh(share.index, share.values, height=0.62, color=BLUE)
    pct_labels(ax, bars, share.values, dx=1.2)
    style_barh(ax, 112)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Houses (%)")
    ax.set_title("Heating Fuel",
                 loc="left")
    save(fig, "01_heating_fuel_share.png")


def fig_type_vs_census(houses: pd.DataFrame):
    t = (houses["TYPEOFHOUSE"].str.strip().str.casefold().map(TYPE_LOGEMENT))
    sample = t.value_counts(normalize=True) * 100
    order = list(CENSUS_TYPE)
    labels = {
        "Maison individuelle": "Single-detached",
        "Maison en rangee": "Row house",
        "Duplex": "Semi / duplex",
        "Triplex": "Triplex",
        "Collective": "Apartment",
    }
    s = [sample.get(k, 0) for k in order]
    c = [CENSUS_TYPE[k] * 100 for k in order]

    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    b1 = ax.barh(y - 0.21, s, height=0.38, color=BLUE, label="EnerGuide sample",
                 edgecolor=SURFACE, linewidth=1)
    b2 = ax.barh(y + 0.21, c, height=0.38, color=AQUA, label="Census 2021 (Calgary)",
                 edgecolor=SURFACE, linewidth=1)
    pct_labels(ax, b1, s, dx=1.2)
    pct_labels(ax, b2, c, dx=1.2)
    ax.set_yticks(y, [labels[k] for k in order])
    style_barh(ax, 105)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share of dwellings (%)")
    ax.legend(frameon=False, loc="lower right", labelcolor=INK_2)
    ax.set_title("Dwelling type: EnerGuide sample vs the real Calgary stock\n"
                 "the self-selection bias the IPF raking corrects", loc="left")
    save(fig, "02_dwelling_type_vs_census.png")


def fig_vintage_vs_census(houses: pd.DataFrame):
    years = pd.to_numeric(houses["YEARBUILT"], errors="coerce")
    years = years.where((years >= 1850) & (years <= 2026))
    binned = pd.cut(years, bins=[-np.inf, *VINTAGE_EDGES, np.inf],
                    labels=VINTAGE_LABELS, right=False)
    sample = binned.value_counts(normalize=True).reindex(VINTAGE_LABELS) * 100
    census = [CENSUS_VINTAGE[k] * 100 for k in VINTAGE_LABELS]

    x = np.arange(len(VINTAGE_LABELS))
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.bar(x - 0.2, sample.values, width=0.38, color=BLUE,
           label="EnerGuide sample", edgecolor=SURFACE, linewidth=1)
    ax.bar(x + 0.2, census, width=0.38, color=AQUA,
           label="Census 2021 (Calgary)", edgecolor=SURFACE, linewidth=1)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(x, [l.replace(" - ", "-") for l in VINTAGE_LABELS],
                  rotation=30, ha="right")
    ax.set_ylabel("share of dwellings (%)")
    ax.legend(frameon=False, labelcolor=INK_2)
    ax.set_title("Construction vintage: EnerGuide sample vs Calgary census stock",
                 loc="left")
    save(fig, "03_vintage_vs_census.png")


def fig_volume_per_year(df: pd.DataFrame):
    counts = df["_yearfile"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.bar(counts.index, counts.values, color=BLUE, width=0.7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("evaluations")
    ax.set_title("Evaluations per year ", loc="left")
    save(fig, "04_evaluations_per_year.png")


def fig_evaltype_mix(df: pd.DataFrame):
    mix = (df.groupby(["_yearfile", "EVALTYPE"]).size()
             .unstack(fill_value=0)
             .reindex(columns=["D", "E", "N", "P"], fill_value=0))
    shares = mix.div(mix.sum(axis=1), axis=0) * 100
    names = {"D": "D - existing, pre-retrofit", "E": "E - post-retrofit",
             "N": "N - new, as built", "P": "P - new, from plans"}
    colors = {"D": BLUE, "E": AQUA, "N": YELLOW, "P": VIOLET}

    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    bottom = np.zeros(len(shares))
    for t in ["D", "E", "N", "P"]:
        ax.bar(shares.index, shares[t].values, bottom=bottom, width=0.7,
               color=colors[t], label=names[t],
               edgecolor=SURFACE, linewidth=1)
        bottom += shares[t].values
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("share of evaluations (%)")
    ax.legend(frameon=False, ncols=2, loc="upper center",
              bbox_to_anchor=(0.5, -0.28), labelcolor=INK_2)
    ax.set_title("Evaluation type mix per year - retrofit waves vs new-home labelling",
                 loc="left")
    save(fig, "05_evaltype_mix_per_year.png")


def fig_airtightness(houses: pd.DataFrame):
    stock = houses[houses["EVALTYPE"].isin(["D", "E"])].copy()
    ach = pd.to_numeric(stock["AIR50P"], errors="coerce")
    years = pd.to_numeric(stock["YEARBUILT"], errors="coerce")
    ok = ach.between(0.2, 30) & years.between(1850, 2026)
    binned = pd.cut(years[ok], bins=[-np.inf, *VINTAGE_EDGES, np.inf],
                    labels=VINTAGE_LABELS, right=False)
    med = ach[ok].groupby(binned, observed=True).median().reindex(VINTAGE_LABELS)

    x = np.arange(len(VINTAGE_LABELS))
    fig, ax = plt.subplots(figsize=(8.5, 4.0))
    ax.plot(x, med.values, color=BLUE, linewidth=2, marker="o", markersize=6,
            markerfacecolor=BLUE, markeredgecolor=SURFACE, markeredgewidth=1.5)
    for xi, v in zip(x, med.values):
        ax.annotate(f"{v:.1f}", (xi, v), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=9, color=INK_2)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(x, [l.replace(" - ", "-") for l in VINTAGE_LABELS],
                  rotation=30, ha="right")
    ax.set_ylim(0, float(med.max()) * 1.15)  # headroom for the point labels
    ax.set_ylabel("median ACH50 (air changes/h at 50 Pa)")
    ax.set_title("Homes get tighter with every construction era\n"
                 "measured blower-door airtightness by vintage (existing stock)",
                 loc="left")
    save(fig, "06_airtightness_by_vintage.png")


def fig_dhw_fuel(houses: pd.DataFrame):
    stock = houses[houses["EVALTYPE"].isin(["D", "E"])]
    fuel = (stock["PDHWFUEL"].str.strip().str.casefold()
            .map(FUEL_MAP).fillna("Other"))
    share = fuel.value_counts(normalize=True) * 100
    share = share.reindex(["Natural gas", "Electricity", "Wood", "Oil", "Other"]).dropna()

    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    bars = ax.barh(share.index, share.values, height=0.62, color=BLUE)
    pct_labels(ax, bars, share.values, dx=1.2)
    style_barh(ax, 112)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share of houses (%)")
    ax.set_title("Water-heater fuel - existing Alberta stock in EnerGuide\n"
                 f"one record per house, latest evaluation (n = {len(stock):,})",
                 loc="left")
    save(fig, "07_water_heater_fuel_share.png")


# --------------------------------------------------------------------------- #
# Basic column snapshots (08+): one simple chart per column, existing stock
# (one record per house, latest evaluation) unless noted.
# NOTE - TMAIN and TOTALOCCUPANTS are deliberately NOT charted: they are
# standardized operating-condition inputs (99.8% of TMAIN is exactly 21.0 C),
# not observed behaviour.
# --------------------------------------------------------------------------- #

def _share_barh(share_pct: pd.Series, title: str, fname: str,
                figsize=(7.5, 4.0)):
    """One horizontal share bar per category - the basic distribution view."""
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(share_pct.index, share_pct.values, height=0.62, color=BLUE)
    pct_labels(ax, bars, share_pct.values, dx=1.2)
    style_barh(ax, max(share_pct.max() * 1.18, 30))
    ax.set_xlabel("share of houses (%)")
    ax.set_title(title, loc="left")
    save(fig, fname)


def _hist(values: pd.Series, bins, title: str, xlabel: str, fname: str):
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.hist(values.dropna(), bins=bins, color=BLUE,
            edgecolor=SURFACE, linewidth=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("houses")
    ax.set_title(title, loc="left")
    save(fig, fname)


def _adoption_line(share_by_year: pd.Series, title: str, ylabel: str,
                   fname: str):
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    x = share_by_year.index.astype(int)
    ax.plot(x, share_by_year.values, color=BLUE, linewidth=2, marker="o",
            markersize=6, markerfacecolor=BLUE, markeredgecolor=SURFACE,
            markeredgewidth=1.5)
    for xi, v in zip(x, share_by_year.values):
        ax.annotate(f"{v:.1f}", (xi, v), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=9, color=INK_2)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(x)
    ax.set_ylim(0, share_by_year.max() * 1.25)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    save(fig, fname)


def _stock(houses: pd.DataFrame) -> pd.DataFrame:
    return houses[houses["EVALTYPE"].isin(["D", "E"])]


def fig_storeys(houses: pd.DataFrame):
    s = _stock(houses)["STOREYS"].str.strip().str.casefold()
    s = s.replace({"split entry/raised base.": "split entry / raised basement"})
    share = (s.value_counts(normalize=True) * 100).head(6)
    share.index = [v.capitalize() for v in share.index]
    _share_barh(share, "Number of storeys - existing stock",
                "08_storeys.png")


def fig_foundation(houses: pd.DataFrame):
    fnd = _stock(houses)["FNDTYPE"].dropna().str.upper()
    def classify(v: str) -> str:
        has = {code[0] for code in v.split(";") if code}
        if "B" in has:
            return "Basement" + (" + other" if has - {"B"} else "")
        if "C" in has:
            return "Crawlspace"
        if "S" in has:
            return "Slab-on-grade"
        return "Other"
    share = (fnd.map(classify).value_counts(normalize=True) * 100)
    _share_barh(share, "Foundation type - existing stock\n"
                "(HOT2000 codes: B=basement, C=crawlspace, S=slab)",
                "09_foundation_type.png")


def fig_furnace_type(houses: pd.DataFrame):
    t = _stock(houses)["FURNACETYPE"].str.strip()
    top = t.value_counts(normalize=True) * 100
    share = top.head(5)
    share["Other"] = top.iloc[5:].sum()
    _share_barh(share, "Primary heating equipment type - existing stock",
                "10_furnace_type.png", figsize=(8.5, 4.2))


def fig_furnace_efficiency(houses: pd.DataFrame):
    eff = pd.to_numeric(_stock(houses)["FURSSEFF"], errors="coerce")
    eff = eff.where(eff.between(60, 100))
    _hist(eff, bins=np.arange(60, 101, 2),
          title="Primary heating equipment efficiency - existing stock\n"
                "two fleets: ~80% conventional vs 92-97% condensing furnaces",
          xlabel="steady-state efficiency (%)",
          fname="11_furnace_efficiency.png")


def fig_ac_type(houses: pd.DataFrame):
    ac = _stock(houses)["AIRCONDTYPE"].str.strip().str.casefold()
    def classify(v):
        if pd.isna(v) or v == "not installed":
            return "No air conditioning"
        if "central" in v or v == "conventional a/c" or "coils" in v:
            return "Central A/C"
        if "window" in v:
            return "Window / room unit"
        return "Other (mini-split, ...)"
    share = ac.map(classify).value_counts(normalize=True) * 100
    _share_barh(share, "Air conditioning - existing stock",
                "12_air_conditioning.png")


def fig_dhw_type(houses: pd.DataFrame):
    t = _stock(houses)["PDHWTYPE"].str.strip()
    top = t.value_counts(normalize=True) * 100
    share = top.head(5)
    share["Other"] = top.iloc[5:].sum()
    _share_barh(share, "Water heater type - existing stock",
                "13_water_heater_type.png", figsize=(8.5, 4.2))


def fig_floor_area(houses: pd.DataFrame):
    area = pd.to_numeric(houses["HEATEDFLOORAREA"], errors="coerce")
    area = area.where(area.between(20, 600))
    _hist(area, bins=np.arange(0, 601, 25),
          title="Heated floor area (m2) - houses with an ERS v11+ evaluation\n"
                f"median {area.median():.0f} m2 (field exists since ~2015)",
          xlabel="heated floor area (m2)",
          fname="14_heated_floor_area.png")


def fig_ers_rating(houses: pd.DataFrame):
    ers = pd.to_numeric(houses["ERSRATING"], errors="coerce")
    ers = ers.where(ers.between(1, 400))
    _hist(ers, bins=np.arange(0, 401, 20),
          title="EnerGuide rating (GJ/year, lower is better)\n"
                f"median {ers.median():.0f} GJ/yr - GJ scale replaced the "
                "0-100 scale in 2016",
          xlabel="rated annual energy consumption (GJ)",
          fname="15_ers_rating.png")


def fig_heatpump_adoption(df: pd.DataFrame):
    d = df[df["HPEquipType"].notna()].copy()
    d["_year"] = d["_date"].dt.year
    d = d[d["_year"].between(2019, 2025)]
    has = d["HPEquipType"].str.strip().str.casefold() != "not installed"
    share = has.groupby(d["_year"]).mean() * 100
    _adoption_line(share,
                   "Heat pump present - share of evaluations per year\n"
                   "(field populated since 2021; grant-program sample, "
                   "biased toward adopters)",
                   "share of evaluations (%)",
                   "16_heat_pump_adoption.png")


def fig_pv_adoption(df: pd.DataFrame):
    d = df.copy()
    d["_year"] = d["_date"].dt.year
    d = d[d["_year"].between(2016, 2025)]
    kw = pd.to_numeric(d["KWPV"], errors="coerce")
    d = d[kw.notna()]
    share = (kw[kw.notna()] > 0).groupby(d["_year"]).mean() * 100
    _adoption_line(share,
                   "Solar PV present - share of evaluations per year\n"
                   "(grant-program sample, biased toward adopters)",
                   "share of evaluations (%)",
                   "17_pv_adoption.png")


def fig_ventilation(houses: pd.DataFrame):
    v = _stock(houses)["CENVENTSYSTYPE"].str.strip().str.casefold()
    def classify(x):
        if pd.isna(x) or x == "no ventilation system":
            return "No ventilation system"
        if "fans" in x:  # "Fans without heat recovery" - test before the HRV match
            return "Fans, no heat recovery"
        if "hrv" in x or "heat recovery" in x:
            return "HRV (heat recovery)"
        return "Other"
    share = v.map(classify).value_counts(normalize=True) * 100
    _share_barh(share, "Central ventilation system - existing stock",
                "18_ventilation.png")


def run_describe():
    print("loading parquet files...")
    df, houses = load()
    print(f"  {len(df):,} evaluations, {len(houses):,} unique houses")
    fig_heating_fuel(houses)
    fig_type_vs_census(houses)
    fig_vintage_vs_census(houses)
    fig_volume_per_year(df)
    fig_evaltype_mix(df)
    fig_airtightness(houses)
    fig_dhw_fuel(houses)
    fig_storeys(houses)
    fig_foundation(houses)
    fig_furnace_type(houses)
    fig_furnace_efficiency(houses)
    fig_ac_type(houses)
    fig_dhw_type(houses)
    fig_floor_area(houses)
    fig_ers_rating(houses)
    fig_heatpump_adoption(df)
    fig_pv_adoption(df)
    fig_ventilation(houses)

# =========================================================================== #
# Entry point: one branch per sub-command
# =========================================================================== #

def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Calgary energy-use profiles, map, and descriptive figures")
    ap.add_argument("step", nargs="?", default="all",
                    choices=["all", "city", "area", "map", "describe"],
                    help="city = city MEUI profile + figs 19-21; "
                         "area = per-FSA profile + figs 22-23; "
                         "map = FSA choropleth fig 24; "
                         "describe = descriptive figs 01-18")
    args = ap.parse_args()
    if args.step in ("all", "describe"):
        run_describe()
    if args.step in ("all", "city"):
        run_city()
    if args.step in ("all", "area"):
        run_area()
    if args.step in ("all", "map"):
        make_map()


if __name__ == "__main__":
    main()
