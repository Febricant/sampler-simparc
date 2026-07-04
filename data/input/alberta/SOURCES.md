# Alberta data sources - provenance log

Automated pulls (see `calgary_adaptation/fetch_alberta_data.py` and
`energuide/manifest.json` for exact row counts and retrieval dates):

| Source | Location | Licence |
|---|---|---|
| NRCan EnerGuide Rating System Open Data (PROVINCE=AB, 2004-2025) | `energuide/*.parquet` | Open Government Licence - Canada |
| City of Calgary BenchmarkYYC (new + existing buildings) | `benchmarkyyc/*.csv` | Open Government Licence - City of Calgary |

Manual downloads - fill one row per file you add:

| File | Source dataset (table id) | URL | Retrieved | Used for |
|---|---|---|---|---|
| `res_ab_e.xlsx` | NRCan CEUD, Residential Sector Alberta, Tables 1-41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm | (add date) | Tier-B margins: heating system stock, appliance stock, water heaters |
| | StatCan 38-10-0286 (primary heating systems and type of energy) | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810028601 | | `Source_Energie_Chauf` / `Chauffage_Logement` cross-check |
| | Census 2021 Profile, Calgary CSD (dwelling type x period x tenure x household size) | https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm | | Raking margins (IPF) |
| | StatCan 20-10-0025 (ZEV registrations, AB) | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010002501 | | `Vehicule_Presence` |
| | CMHC Rental Market Survey, Calgary vacancy | https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research | | `Vacancy Status` |
| | HES tables (AC saturation, thermostats) | https://www150.statcan.gc.ca/n1/en/surveys/3881 | | `Climatisation`, `ModeConsigne` |
