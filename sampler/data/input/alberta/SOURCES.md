# Alberta data sources - provenance log

Automated pulls (see `calgary_adaptation/fetch_data.py` and
`energuide/manifest.json` for exact row counts and retrieval dates):

| Source | Location | Licence |
|---|---|---|
| NRCan EnerGuide Rating System Open Data (PROVINCE=AB, 2004-2025) | `energuide/energuide_ab_<year>.parquet` | Open Government Licence - Canada |
| City of Calgary BenchmarkYYC (new + existing buildings) | `benchmarkyyc/*.csv` | Open Government Licence - City of Calgary |
| StatCan 2021 Census Profile, Forward Sortation Areas (98-401-X2021013) | `census/calgary_fsa_composition.parquet` (+ `census/manifest.json`) | Statistics Canada Open Licence |
| StatCan 2021 FSA digital boundary file (lfsa000a21a) | `census/_raw/lfsa000a21a_e.zip` (choropleth geometry) | Statistics Canada Open Licence |

Derived tables (regenerable - do not edit by hand, see
`calgary_adaptation/calibrate_stock.py` and
`energuide/energuide_ab_combined_manifest.json`):

| File | Built by | Grain | Rows |
|---|---|---|---|
| `energuide/energuide_ab_evaluations.parquet` | `calibrate_stock.py` | one row per HOUSEID + EVALUATIONSID + EVALTYPE; pre- and post-retrofit records both kept | 351,184 |
| `energuide/energuide_ab_houses.parquet` | `calibrate_stock.py` | one row per HOUSEID (D > E > N > P, then earliest ENTRYDATE) | 191,621 |
| `energuide/alberta_stock_mapped.parquet` | `calibrate_stock.py` | house-level, plus BN state labels and the `POND_AB` IPF weight | 191,618 |
| `../../output/calgary_energy_profile.csv` | `energy_profile.py` | Calgary mean MEUI (kWh/m²/yr) with 95% bootstrap CI, overall + by dwelling type + by vintage | 15 |
| `../../output/calgary_fsa_energy_profile.csv` | `energy_profile.py` | per-FSA mean MEUI with 95% CI + hybrid/borrow-only city aggregate (area-based) | 38 |

The Calgary energy-use profile is documented in
`calgary_adaptation/ENERGY_PROFILE_METHODOLOGY.md` (city-wide weighted bootstrap)
and `calgary_adaptation/AREA_ENERGY_PROFILE_METHODOLOGY.md` (per-FSA area-based
version); figures `calgary_adaptation/figures/19-23_*.png`. The spatial
choropleth (`figures/24_calgary_meui_map.png`) is drawn by
`calgary_adaptation/energy_profile.py` (reads FSA boundaries with pyshp).

Manual downloads - fill one row per file you add:

| File | Source dataset (table id) | URL | Retrieved | Used for |
|---|---|---|---|---|
| `data/input/alberta/res_ab_e.xlsx` | NRCan CEUD, Residential Sector Alberta, Tables 1-41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm | (add date) | Tier-B margins: heating system stock, appliance stock, water heaters |
| | StatCan 38-10-0286 (primary heating systems and type of energy) | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810028601 | | `Source_Energie_Chauf` / `Chauffage_Logement` cross-check |
| | Census 2021 Profile, Calgary CSD (dwelling type x period x tenure x household size) | https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm | | Raking margins (IPF) |
| | StatCan 20-10-0025 (ZEV registrations, AB) | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010002501 | | `Vehicule_Presence` |
| | CMHC Rental Market Survey, Calgary vacancy | https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research | | `Vacancy Status` |
| | HES tables (AC saturation, thermostats) | https://www150.statcan.gc.ca/n1/en/surveys/3881 | | `Climatisation`, `ModeConsigne` |
