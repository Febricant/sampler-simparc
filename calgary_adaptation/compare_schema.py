"""
Compare the EnerGuide Alberta microdata against the Quebec sampler input schema.

The sampler (the front end for Hydro-Quebec's SimParc stock simulator) expects a
97-column "Quebec input CSV" (`data/output/building-input.csv`: 40 EUEMR
Bayesian-network nodes + 52 ResStock attributes + 4 code-generated columns + 1
mixed). Re-calibrating it to Calgary means answering, column by column: *can the
NRCan EnerGuide open microdata supply this, and how well is it populated?*

This script operationalizes section 3 of ALBERTA_RECALIBRATION_PLAN.md into a
data-driven crosswalk. For every Quebec input column it records:

    quebec_column, provenance, spatial_dependency, tier, status,
    energuide_field, pct_populated, note

where `status` is where the Alberta values would come from:

    direct     - a named EnerGuide field maps to it (Tier-A/B microdata);
                 pct_populated is the share of Calgary EnerGuide rows that
                 actually carry a usable value (surfaces theory-vs-reality gaps,
                 e.g. MEUI-style ~44% coverage).
    imputed    - no EnerGuide field; derived from census / external aggregate
                 (e.g. Mode_Occupation from census tenure).
    keep-qc    - Tier-C/D survey node with no Alberta microdata; keep the Quebec
                 conditional probabilities (e.g. Spa_*, Piscine_*, appliances).
    resstock   - ResStock/Buildstock location-independent default, not sourced
                 from a survey at all; kept generic.
    derived    - a deterministic child of another node (Type_Batiment) or a
                 code-generated schedule column (Tconsignes_*).
    set-calgary- geography node already collapsed to Calgary/Alberta.

Usage (from repo root):
    uv run python calgary_adaptation/compare_schema.py
Writes data/output/energuide_vs_quebec_crosswalk.csv and prints a summary.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = REPO_ROOT / "data" / "output" / "building-input-column-classification.csv"
HOUSES_PARQUET = REPO_ROOT / "data" / "input" / "alberta" / "energuide" / "energuide_ab_houses.parquet"
OUT_PATH = REPO_ROOT / "data" / "output" / "energuide_vs_quebec_crosswalk.csv"


# --------------------------------------------------------------------------- #
# The crosswalk: Quebec input column -> (status, energuide_field, tier, note)
#
# Sources for each decision:
#   - EnerGuideToBN dicts in build_alberta_weights.py (the mappings already coded)
#   - section 3 (3.1 BN nodes, 3.2 ResStock CSVs) of ALBERTA_RECALIBRATION_PLAN.md
#   - the field list actually present in energuide_ab_houses.parquet
#
# energuide_field must be an EnerGuide column that exists on disk (checked at
# runtime) or None. Columns absent from this map fall back to a provenance-based
# default (see classify_default), so the map only needs the non-default cases.
# --------------------------------------------------------------------------- #
CrosswalkRow = tuple[str, str | None, str, str]

QUEBEC_MAP: dict[str, CrosswalkRow] = {
    # ---- EUEMR Bayesian-network nodes ------------------------------------- #
    "Territoire_HQ":        ("set-calgary", None, "done", "collapsed to Calgary"),
    "Region_Administrative": ("set-calgary", None, "done", "collapsed to Alberta"),
    "Type_Logement":        ("direct", "TYPEOFHOUSE", "A", "dwelling typology; EnerGuideToBN.TYPE_LOGEMENT"),
    "Type_Batiment":        ("derived", None, "-", "deterministic child of Type_Logement"),
    "An_Construction":      ("direct", "YEARBUILT", "A", "binned to 9 BN vintages"),
    "An_ConstructionCode":  ("direct", "YEARBUILT", "A", "code-era bins from YEARBUILT"),
    "Nombre_Etages":        ("direct", "STOREYS", "A", "raked to census type margins"),
    "Nombre_Pieces":        ("keep-qc", None, "B", "no census cross at needed grain; rescale QC CPT"),
    "Superficie_Totale":    ("direct", "HEATEDFLOORAREA", "A", "binned to existing area states"),
    "Presence_SousSol":     ("direct", "FNDTYPE", "A", "basement/crawlspace from foundation code"),
    "Presence_Garage":      ("keep-qc", None, "B/C", "no EnerGuide field; city assessment or keep QC"),
    "Nombre_Personnes":     ("direct", "TOTALOCCUPANTS", "A", "household size (also census-checkable)"),
    "Mode_Occupation":      ("imputed", None, "A", "no tenure field; imputed from census P(tenure|type)"),
    "Source_Energie_Chauf": ("direct", "FURNACEFUEL", "A", "primary heating fuel; Bi-energie->0"),
    "Chauffage_Logement":   ("direct", "FURNACETYPE", "A", "heating system; blend with HPEquipType"),
    "Climatisation":        ("direct", "AIRCONDTYPE", "A/B", "AC type; blend with HES saturation"),
    "ChaufEau_Presence":    ("direct", "PDHWFUEL", "A", "DHW presence"),
    "ChaufEau_Type":        ("direct", "PRIMARYDHWTANKVOLUME", "A", "tank capacity class"),
    "ChaufEau_ChaufType":   ("direct", "PDHWFUEL", "A", "DHW fuel"),
    "Cuisiniere_Presence":  ("keep-qc", None, "B", "SHEU/CEUD range stock"),
    "Cuisiniere_Energie":   ("keep-qc", None, "B", "gas-range share (AB >> QC), SHEU/CEUD"),
    "Refrigerateur_Nombre": ("keep-qc", None, "B", "SHEU appliance stock"),
    "Congelateur_Nombre":   ("keep-qc", None, "B", "SHEU appliance stock (AB freezer share higher)"),
    "LaveLinge_Type":       ("keep-qc", None, "B/D", "near-universal; rescale SHEU"),
    "SecheLinge_Presence":  ("keep-qc", None, "B/D", "near-universal; rescale SHEU"),
    "LaveVaisselle_Presence": ("keep-qc", None, "B/D", "near-universal; rescale SHEU"),
    "Eclairage_LED":        ("keep-qc", None, "B/C", "HES lighting tables or keep QC"),
    "Vehicule_Presence":    ("imputed", None, "B", "StatCan ZEV registrations; EnerGuide EVCharger biased"),
    "Vehicule_BornePresence": ("keep-qc", None, "B", "charger conditional kept from QC"),
    "Spa_Presence":         ("keep-qc", None, "C", "no AB microdata; permit counts or keep QC +-MC"),
    "Spa_Logement":         ("keep-qc", None, "C", "keep QC conditional"),
    "Spa_Saison":           ("keep-qc", None, "C", "keep QC conditional"),
    "Spa_Utilisation_SaisonChaude": ("keep-qc", None, "C", "keep QC conditional"),
    "Spa_Utilisation_SaisonFroide": ("keep-qc", None, "C", "keep QC conditional"),
    "Piscine_Presence":     ("keep-qc", None, "C", "AB pool prevalence << QC; permit anchor or keep QC"),
    "Piscine_Type":         ("keep-qc", None, "C", "keep QC conditional"),
    "Piscine_Chauffee":     ("keep-qc", None, "C", "keep QC conditional"),
    "Piscine_ChaufType":    ("keep-qc", None, "C", "keep QC conditional"),
    "Piscine_Toile":        ("keep-qc", None, "C", "keep QC conditional"),
    "Piscine_Minuterie":    ("keep-qc", None, "C", "keep QC conditional"),
    "Infiltration":         ("direct", "AIR50P", "A", "measured blower-door ACH50 - best AB data"),

    # ---- ResStock / Buildstock attributes (replaceable from EnerGuide per 3.2)
    "Geometry Stories":     ("direct", "STOREYS", "A/B", "storeys"),
    "Geometry Building Number Units": ("resstock", "NUMDWELLINGUNITS", "B", "MURB unit count from census/BenchmarkYYC"),
    "Geometry Foundation Type": ("direct", "FNDTYPE", "A/B", "foundation type"),
    "Windows":              ("direct", "WINDOWCODE", "A/B", "glazing shares by type/vintage"),
    "Insulation Wall":      ("direct", "MAINWALLINS", "A", "wall RSI -> nearest QC_R* label"),
    "Insulation Ceiling":   ("direct", "CEILINS", "A", "ceiling RSI -> nearest QC_R* label"),
    "Insulation Foundation Wall": ("direct", "FNDWALLINS", "A", "foundation-wall RSI -> nearest QC_R* label"),
    "Insulation Slab":      ("direct", "SLABINSUL", "A", "slab RSI"),
    "HVAC Heating Efficiency": ("direct", "FURSSEFF", "A", "AFUE/HSPF from FURSSEFF/HEATAFUE"),
    "Has PV":               ("direct", "KWPV", "B", "PV presence from KWPV>0 (retrofit-biased)"),
    "PV System Size":       ("direct", "KWPV", "B", "system size from KWPV"),
    "Battery":              ("direct", "BATTERYSTORAGE", "B", "battery presence"),
    "ModeConsigne":         ("direct", "ThermostatHeatingNighttime", "A/B", "setback mode from day/night pair"),
    "Heating Setpoint":     ("direct", "TMAIN", "A/B", "daytime heating setpoint"),
    "Basement Heating Setpoint": ("direct", "TBSMNT", "A/B", "basement setpoint"),
    "Cooling Setpoint":     ("direct", "ThermostatCooling", "B", "sparse; else shift QC"),
    "Mechanical Ventilation": ("direct", "CENVENTSYSTYPE", "B", "ventilation system type/HRV"),
    "Vacancy Status":       ("imputed", None, "B", "CMHC vacancy + census unoccupied share"),
}

# ResStock columns explicitly left as generic (Tier D / no AB signal). Anything
# ResStock-provenance not in QUEBEC_MAP and not here still defaults to resstock,
# but listing the deliberate ones documents the intent.
RESSTOCK_GENERIC_NOTE = "ResStock-generic behavioural/physical default; not Alberta-specific"


def classify_default(provenance: str) -> CrosswalkRow:
    """Fallback status for columns not in QUEBEC_MAP, from their provenance."""
    prov = provenance.lower()
    if "code-generated" in prov:
        return ("derived", None, "-", "code-generated schedule column")
    if "resstock" in prov or "buildstock" in prov:
        return ("resstock", None, "D", RESSTOCK_GENERIC_NOTE)
    if "mixed" in prov:
        return ("keep-qc", None, "B", "survey node extended through program logic")
    # EUEMR survey node with no explicit mapping -> keep QC probabilities.
    return ("keep-qc", None, "C", "EUEMR node with no Alberta microdata; keep QC")


def pct_populated(series: pd.Series) -> float:
    """Share of rows with a usable (non-null, non-empty, non-sentinel) value."""
    s = series
    if s.dtype == object or pd.api.types.is_string_dtype(s):
        s = s.astype("string").str.strip()
        bad = s.isna() | s.eq("") | s.str.upper().isin(["N/A", "NA", "NONE", "UNKNOWN"])
    else:
        s = pd.to_numeric(s, errors="coerce")
        bad = s.isna()
    return float((~bad).mean() * 100.0)


def main() -> None:
    classification = pd.read_csv(CLASSIFICATION)
    print(f"Quebec input schema: {len(classification)} columns "
          f"(from {CLASSIFICATION.relative_to(REPO_ROOT)})")

    houses = pd.read_parquet(HOUSES_PARQUET)
    city = houses["CLIENTCITY"].astype("string").str.strip().str.upper()
    calgary = houses[city == "CALGARY"]
    print(f"EnerGuide houses: {len(houses):,} total, {len(calgary):,} Calgary "
          f"(coverage computed on the Calgary subset)")
    energuide_fields = set(houses.columns)

    rows = []
    for _, r in classification.iterrows():
        col = r["Column"]
        provenance = str(r["Provenance"])
        spatial = str(r.get("SpatialDependency", ""))

        status, eg_field, tier, note = QUEBEC_MAP.get(col) or classify_default(provenance)

        pct = ""
        if eg_field is not None:
            assert eg_field in energuide_fields, (
                f"{col}: mapped EnerGuide field {eg_field!r} is not in "
                f"energuide_ab_houses.parquet - fix QUEBEC_MAP"
            )
            pct = round(pct_populated(calgary[eg_field]), 1)

        rows.append({
            "quebec_column": col,
            "provenance": provenance,
            "spatial_dependency": spatial,
            "tier": tier,
            "status": status,
            "energuide_field": eg_field or "",
            "pct_populated": pct,
            "note": note,
        })

    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)

    # ---- summary ---------------------------------------------------------- #
    print("\n=== crosswalk summary: how each SimParc input is sourced ===")
    counts = out["status"].value_counts()
    for status, n in counts.items():
        print(f"  {status:<12} {n:>3} columns")

    direct = out[out["status"] == "direct"].copy()
    direct["pct_populated"] = pd.to_numeric(direct["pct_populated"], errors="coerce")
    print(f"\n{len(direct)} columns map DIRECTLY to an EnerGuide field. "
          f"Population coverage (Calgary subset):")
    print(direct.sort_values("pct_populated")
              [["quebec_column", "energuide_field", "pct_populated"]]
              .to_string(index=False))

    thin = direct[direct["pct_populated"] < 60]
    if len(thin):
        print(f"\n  NOTE: {len(thin)} 'direct' fields are <60% populated in Calgary "
              f"- they map in theory but are sparse in practice:")
        for _, t in thin.iterrows():
            print(f"    {t['quebec_column']} <- {t['energuide_field']} "
                  f"({t['pct_populated']}%)")

    print(f"\nwrote {len(out)} rows -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
