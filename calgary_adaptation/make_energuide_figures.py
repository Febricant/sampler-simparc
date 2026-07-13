"""
Simple one-panel matplotlib figures describing the EnerGuide Alberta pull
(data/input/alberta/energuide/*.parquet). Each figure is saved individually
under calgary_adaptation/figures/.

Stock-composition figures use one record per house (latest evaluation, so a
retrofitted house counts in its post-retrofit state); volume figures use all
evaluation rows.

Usage:
    python calgary_adaptation/make_energuide_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ENERGUIDE_DIR = REPO_ROOT / "data" / "input" / "alberta" / "energuide"
FIG_DIR = Path(__file__).resolve().parent / "figures"

# --------------------------------------------------------------------------- #
# Palette (dataviz reference instance, light mode)
# --------------------------------------------------------------------------- #
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"     # categorical slot 1 - single-series default
AQUA = "#1baf7a"     # slot 2 - comparison series
YELLOW = "#eda100"   # slot 3
VIOLET = "#4a3aa7"   # slot 5

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"],
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.titlecolor": INK,
    "font.size": 10,
    "axes.titlesize": 12,
    "figure.dpi": 150,
})

# Census 2021 margins, Calgary CSD - same values Phase 2b rakes to
# (build_alberta_weights.CENSUS_MARGINS_CALGARY_2021).
CENSUS_TYPE = {
    "Maison individuelle": 0.552,
    "Maison en rangee": 0.088,
    "Duplex": 0.084,
    "Triplex": 0.005,
    "Collective": 0.271,
}
CENSUS_VINTAGE = {
    "< 1950": 0.035, "[1950 - 1960)": 0.048, "[1960 - 1970)": 0.105,
    "[1970 - 1980)": 0.158, "[1980 - 1990)": 0.129, "[1990 - 2000)": 0.135,
    "[2000 - 2010)": 0.211, "[2010 - 2020)": 0.155, ">= 2020": 0.024,
}

TYPE_LOGEMENT = {  # EnerGuideToBN.TYPE_LOGEMENT (build_alberta_weights.py)
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
FUEL_MAP = {  # EnerGuideToBN.SOURCE_ENERGIE_CHAUF
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
    for f in sorted(ENERGUIDE_DIR.glob("energuide_ab_*.parquet")):
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


def save(fig, name):
    FIG_DIR.mkdir(exist_ok=True)
    out = FIG_DIR / name
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}")


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


def main():
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


if __name__ == "__main__":
    main()
