# LTE‑Sampler‑Residential — Reverse‑Engineering Brief & Alberta Adaptation Assessment

*A technical breakdown of the Quebec residential housing‑stock CSV generator: nomenclature, methodology, execution, Alberta portability, and ResStock/SimParc integration.*

---

## Executive Summary

**What it is.** `LTE-Sampler-Residential` (internally branded **"ResStock‑QC"**) is a **synthetic residential building‑stock generator** built by Hydro‑Québec's research lab (LTE — *Laboratoire des technologies de l'énergie*). Given a target sample size *N* (and optional constraints), it emits *N* rows of synthetic Québec dwellings, each described as a complete set of **OpenStudio‑HPXML `BuildResidentialHPXML` measure arguments** ready for EnergyPlus simulation.

**How it works — three layers:**

1. **A Bayesian network (BN)** of **40 dwelling/occupant variables**, learned offline from Hydro‑Québec's **EUEMr 2022** residential energy survey (weighted by survey weights). Sampling this network (via **pyAgrum**) produces a statistically realistic joint draw of *Territoire, dwelling type, vintage, heating fuel/system, appliances, pool/spa, EVs…*
2. **ResStock‑style conditional probability tables (CPTs)** — 53 `;`‑separated CSVs that add ~52 *technical* attributes (envelope R‑values, windows, infiltration, HVAC efficiency, setpoints, PV, …) conditioned on the BN draw.
3. **A deterministic HPXML mapper** (`doMapping`, ~6,200 lines) that translates the French survey/ResStock labels into ~219 snake_case OS‑HPXML arguments (weather file, geometry, fuels, efficiencies, schedules).

**Output.** Three CSVs — `building-input.csv` (97 human‑readable columns), `building-mapping.csv` (219 HPXML args), `building-test.csv` (316 = the two concatenated). It is a *building‑description generator*, not a simulator — EnergyPlus runs downstream (this feeds Hydro‑Québec's **SimParc** stock simulator).

**Alberta portability (headline).** The **target format is already location‑agnostic** (OS‑HPXML works anywhere given a weather file). The *climate* port is surprisingly small — essentially **swap ~3 hardcoded `.epw` filenames and change the UTC offset from −5 to −7**. The *hard* problem is **data**: the entire model is conditioned on a Quebec survey with no Alberta equivalent, and Alberta's housing energy reality is structurally different (natural‑gas‑dominant heating vs Quebec's electric baseboards; deregulated fossil grid vs hydro; different building‑code vintages). Adapting the *plumbing* is days of work; rebuilding the *statistical content* for Alberta is the real project.

---

## 1. Translation & Nomenclature

### 1.1 What "EUEMr" is
**EUEMr** = *Étude sur l'Utilisation de l'Énergie chez les Ménages résidentiels* — Hydro‑Québec's recurring **residential household energy‑use survey** (the 2022 wave is the data source). Raw survey columns are opaque codes (`QA4`, `QC1R`, `TERR_HQ`, …); `src/utils/euemr/` recodes them into the 40 clean BN variables. "**EUEMR modifié**" (the `Source` tag in `Data_description.csv`) means *the recoded survey*.

### 1.2 The 40 Bayesian‑network variables (glossary)
All are tagged `Échantillonneur = Réseau Bayesien` in `data/processed/Data_description.csv`. Representative subset (full list in that file / `Bn.yml`):

| French node | English | Represents | Example values (translated) |
|---|---|---|---|
| `Territoire_HQ` | Hydro‑Québec Territory | Utility billing territory — **BN root**, drives weather file | Est et Nord du Québec, Laurentides, Montmorency, Montréal, Richelieu |
| `Region_Administrative` | Administrative Region | Quebec admin region (15) | Bas‑Saint‑Laurent, Capitale‑Nationale, Montérégie, Montréal… |
| `Type_Logement` | Dwelling Type | Unit typology (most‑connected node) | Maison individuelle (*detached*), Maison en rangée (*row*), Duplex, Triplex, Collective (*multi‑unit*) |
| `Type_Batiment` | Building Type | Coarse typology | Maison, Plex, Collective |
| `Nombre_Etages` / `Nombre_Pieces` | # Storeys / # Rooms | Geometry (incl. basement+garage) | Un/Deux/Trois étages et plus; 1…15 et plus |
| `Superficie_Totale` | Total Floor Area | Habitable area, sq ft (binned) | [1‑500) … ≥ 5000 |
| `Presence_SousSol` | Basement Presence | Basement/crawlspace | Sous‑sol 6 pied, Vide sanitaire, Aucun, Les deux |
| `Nombre_Personnes` | # Occupants | Household size | 1,2,3,4, 5 et plus |
| `Presence_Garage` | Garage | Presence + heating | Pas de Garage, Non chauffé, Chauffé électricité/autre |
| `Mode_Occupation` | Tenure | Owner vs renter | Proprietaire, Locataire |
| `An_Construction` | Construction Year | Decade bands | < 1950 … ≥ 2020 |
| `An_ConstructionCode` | Construction Year (code‑era) | **Building‑code vintages** | < 1946, [1946‑1971), [1971‑1986), [1986‑2013), ≥ 2013 |
| `Source_Energie_Chauf` | Heating Energy Source | Primary heating fuel | Electricite, Mazout (*oil*), Gaz naturel, **Bi‑energie** (*dual*), Bois (*wood*) |
| `Chauffage_Logement` | Heating System | 20 system combos | Plinthes électriques (*electric baseboards*), Thermopompe murale (*ductless HP*), Système central à air chaud (*furnace*), Fournaise ou poêle à bois (*wood*) … |
| `Climatisation` | Air Conditioning | Cooling type | Aucune, Fenêtre/mobile, Murale, Centrale |
| `ChaufEau_ChaufType` / `_Type` / `_Presence` | Water‑Heater fuel / capacity / scope | DHW | Electrique, Gaz, Mazout, Bois; tankless…60+ gal; Logement/Central |
| `Spa_*`, `Piscine_*` | Spa / Pool family | Presence, type, season, heating | Hors‑Terre, Creusée; Thermopompe/Electrique/Solaire… |
| `Vehicule_Presence` / `_BornePresence` | EV / Charger | EV+PHEV ownership; home charger | **VE**=*BEV*, **VHR**=*PHEV*; Aucune_VE_Aucune_VHR… |
| `Congelateur_Nombre`, `Refrigerateur_Nombre`, `LaveLinge_Type`, `SecheLinge_Presence`, `LaveVaisselle_Presence`, `Cuisiniere_Presence/_Energie` | Appliances | Freezers, fridges, washer/dryer/dishwasher, stove+fuel | Aucun/1/2…; Frontale/Traditionnelle; Electrique/Gaz |
| `Eclairage_LED` | LED Lighting Share | % LED (**DEL** = FR for LED) | 0%, 1‑24%, 25‑50%, Plus de 50% |

### 1.3 Key French data **values** worth knowing
- **Heating systems:** *Plinthes électriques* = electric baseboards (the iconic Quebec system); *Thermopompe (murale/géothermique)* = (ductless/ground‑source) heat pump; *Fournaise* = furnace; *Système central à air chaud / à eau chaude* = central forced‑air / hydronic; *Fournaise ou poêle à bois* = wood furnace/stove; *Unités convecteurs* = convectors.
- **Energy sources:** *Électricité, Gaz naturel, Mazout (huile)* = heating oil, *Propane, Bois (granules)* = wood (pellets), **Bi‑énergie** = *dual‑energy* (electric + fossil backup that switches below a cold‑temperature threshold — a Hydro‑Québec tariff product).
- **Tokens:** *Oui/Non* = yes/no; *Aucun(e)* = none; *Ne sait pas / NSP‑NRP* = don't know / no answer; *Logement* = dwelling unit; *Immeuble* = building.

### 1.4 Code identifiers & acronyms
| Identifier | Meaning |
|---|---|
| `GUM_Sampling` / `draw_GUM_Sample` | Sampling via **pyAgrum** (`import pyagrum as gum`) `BNDatabaseGenerator.drawSamples` |
| `lst_NOEUD` | *NŒUD* = **node** — ordered list of the 40 BN nodes |
| `run_hors_bn` | *"hors BN"* = **outside the Bayesian network** — adds the ResStock + code‑generated variables after BN sampling |
| `BuildstockBatchArguments` | NREL **BuildStockBatch/ResStock** conditional sampler (the CPT‑CSV layer) |
| `Consigne` / `Tconsignes_chauffage_H1..H4` / `ModeConsigne` / `HConsignes` | *Setpoint* / heating setback **schedule hours** / setback **behavior pattern** / function generating setback hours |
| `Bi‑energie` | Dual‑energy heating (HP/electric + fossil backup, cold‑temp lockout) |
| `POND1`, `PONDNew`, `Create_Pond`, `raked_data.csv` | Survey **weights** (*pondération*); statistical **raking** to known marginals |
| `Territoire_HQ`, `ZONE`, `Region_Administrative`, `MONTREAL_RMR` | Hydro‑Québec territory / billing zone / admin region / Montréal metro flag (RMR = census metro area) |
| `evs` / Evidence | BN **evidence** (conditioning) passed via `-ev` |
| `SimParc` | Hydro‑Québec building‑**stock simulator** this tool feeds |

### 1.5 Energy‑modeling acronyms
**BN** Bayesian Network · **CPT** Conditional Probability Table · **HPXML** Home Performance XML (BPI/ANSI building schema) · **EPW** EnergyPlus Weather file · **CWEC** Canadian Weather for Energy Calculations (TMY) · **ResStock/BuildStockBatch** NREL US residential stock model + batch runner · **OpenStudio/OS‑HPXML** NREL simulation platform/workflow over EnergyPlus · **R‑value** thermal resistance · **ACH50** air changes/hr at 50 Pa (blower‑door tightness) · **DHW** domestic hot water · **PV** photovoltaic · **ASHP/MSHP/GSHP** air‑source / mini‑split / ground‑source heat pump · **SEER/EER/HSPF/AFUE/COP** efficiency ratings · **HDD/CDD** heating/cooling degree‑days.

---

## 2. Core Methodology & Logic

### 2.1 Architecture: an offline "training" pipeline + an online "sampling" pipeline

```
OFFLINE (regenerate artifacts; src/utils/euemr/ + notebooks)
  EUEMr 2022 survey (xlsx)
    → EUEMR_formatage (euemr/Mapping.py): recode raw Qxxx → 40 French BN vars; re-weight (raking vs raked_data.csv)
    → EUEMr.Make_BN (EUEMR_bn_generator.py): hand-coded DAG + weighted-crosstab CPTs → BN_EUEMr.XDSL, Bn.yml
    → EUEMr.Make_csv / Create_housing_characteristics.ipynb: → housing_characteristics/*.csv (Dependency=/Option= CPTs)
    → ParseHPXMLinputs.py: measure.xml (BuildResidentialHPXML) → HPXMLArg.py (522 arg schema)

ONLINE (runtime; src/utils/sampler/ ; ui/Dashboard.py ; CLI)
  1. Sampler.GUM_Sampling(N, evs)        → draw N dwellings from the BN (pyAgrum)         → 40 vars
  2. resstock_args_sampling(...)          → per dwelling, sample 52 ResStock attrs from CPTs + HConsignes() hours
  3. merge BN ⊕ ResStock dicts
  4. MapHPXML.run → doMapping(...)        → ~219 HPXML measure arguments per dwelling
  5. to_df / to_csv / Streamlit download  → building-input.csv | building-mapping.csv | building-test.csv
```

### 2.2 Bayesian‑network construction (the statistical heart)
In `EUEMR_bn_generator.py`:
- **Nodes** — exactly **40**, fixed in `lst_NOEUD` (`:33-72`).
- **Structure (DAG)** — **hand‑specified** in `diDep` (`:165-206`), not learned. `Territoire_HQ` is the **root**; e.g. `Region_Administrative ← Territoire_HQ`, `Type_Logement ← Region_Administrative`, and critically **`Source_Energie_Chauf ← [Territoire_HQ, Type_Batiment, An_ConstructionCode]`** (heating fuel is modeled as a function of HQ territory, building type, and code era).
- **CPTs** — built by **weighted cross‑tabulation**: `pd.crosstab(parents, child, values=POND1, aggfunc="sum")` then **row‑normalized** to probabilities (`:217-267`). `POND1` is the survey weight; null‑weight rows (new‑construction‑only records) are dropped.
- **Weighting/raking** — `Create_Pond` (`euemr/Mapping.py:757`) computes a `PONDNew` weight by matching survey counts to external targets in `raked_data.csv` over *Vintage × Territoire × Typo × Source* (iterative proportional fitting).

**Statistical methods used:** discrete Bayesian network (pyAgrum `LabelizedVariable` + CPT tensors); survey‑weighted MLE of CPTs via crosstab normalization; survey raking; and rejection/oversampling to hit an exact *N* under evidence (`GUM_Sampling` loops `draw_GUM_Sample` with a multiplier until enough rows survive the evidence; `Sampler.py:63-102`).

### 2.3 ResStock conditional sampling (the "hors‑BN" layer)
`BuildstockBatchArguments` (`sampler/Mapping.py:6229`) loads 53 CSVs into `{attr: {Table, Dependency, Option, …}}`. For each dwelling and each of the 52 `listAttributs`, `resstock_args_sampling` (`Sampler.py:104-160`):
1. builds a filter from the row's BN+prior context using the `Dependency=<parent>` columns,
2. selects the matching CPT row, **normalizes the `Option=<value>` weights to probabilities**,
3. draws one option with `numpy` `Generator.choice(p=…)`, parsing the value out of `Option=<value>`.

Then `HConsignes()` (`utils.py`) appends four **thermostat‑setback schedule hours** `Tconsignes_chauffage_H1..H4` (morning/evening setback start/end, with ±random jitter). These plus the CSV‑driven `ModeConsigne`/`Heating Setpoint` encode **occupant behavior** (e.g. *Baisse de nuit uniquement* = night‑only setback, *Constant*, *Hausse de soir et baisse de nuit* = evening boost + night setback).

### 2.4 HPXML mapping (deterministic translation)
`MapHPXML.doMapping` (`sampler/Mapping.py:12-6227`) is a long, explicit rule cascade. Each rule reads a French/ResStock attribute and writes one or more HPXML keys, e.g. the very first rule maps `Territoire_HQ → weather_station_epw_filepath`; subsequent rules cover geometry, envelope assemblies (`QC_WoodStud-R…` → `wall_assembly_r`), HVAC type/fuel/efficiency, DHW, appliances, PV/battery, ventilation, and setpoint schedules (with **°C→°F** conversion). Six internal helper keys are excluded before return. **Note:** `options_lookup.tsv` is *not* used at runtime — it is an upstream ResStock authoring reference (only read by the offline `Create_housing_characteristics.ipynb`). The runtime translator is `doMapping`.

### 2.5 Inputs & outputs (concrete shapes)
**Runtime inputs (committed):**
- `data/processed/bayesian_network/BN_EUEMr.XDSL` (the BN, loaded by `gum.loadBN`) + `Bn.yml` (a 3‑tuple `[lst_NOEUD, LIST_Dict, dict_info]` of node names, index→label maps, and metadata for the UI).
- `data/processed/housing_characteristics/*.csv` — **53** `;`‑separated CPTs. Header grammar: `Dependency=<parent>;…;Option=<value>;…`, each row a conditional distribution whose `Option=*` weights normalize to 1.0 (many are one‑hot/deterministic). Largest is `Heating Setpoint.csv` (677 `Option=(h,d,n)` temperature‑triple columns).
- `data/processed/Data_description.csv` — the authoritative **97‑row crosswalk** (`Nom, Description, Valeurs, Dépendance parents/enfants, Échantillonneur, Source`).

**Outputs (`data/output/`, comma‑separated):**
| File | Cols | Content |
|---|---|---|
| `building-input.csv` | **97** | 52 ResStock attrs + 4 `Tconsignes_chauffage_H*` + 40 BN vars (1 is "Mixed": `Infiltration`); mix of English ResStock labels and French BN states |
| `building-mapping.csv` | **219** | snake_case OS‑HPXML `BuildResidentialHPXML` arguments (e.g. `weather_station_epw_filepath`, `geometry_unit_type`, `heating_system_type`, `water_heater_fuel_type`, `hvac_control_heating_weekday_setpoint`) |
| `building-test.csv` | **316** | horizontal concat (97 + 219) — one synthetic dwelling per row |

`building-input-column-classification.csv` annotates each input column's **Provenance** (52 ResStock, 40 EUEMr survey, 4 code‑generated, 1 mixed) and **SpatialDependency** (86 location‑independent, 11 location‑dependent: `Territoire_HQ`, `Region_Administrative`, `Source_Energie_Chauf`, `Climatisation`, `Orientation`, `Overhangs`, `Has PV`, `PV Orientation`, `PV System Size`, `Battery`, `Roof Material`).

---

## 3. Execution Guide

### 3.1 Environment
- **Python ≥ 3.11**, managed with **uv** (build backend `uv_build`, `module-name = "src"`). Key deps (`pyproject.toml`): `pandas`, **`pyagrum`** (BN engine), `streamlit`, `dask[complete]`, `dtale[streamlit]`, `plotly`, `openpyxl`, `pyarrow`, `notebook`/`ipykernel`. `joblib` and `PyYAML` are used at runtime as well.
- Native libs for pyAgrum/graphviz on the Docker image: `build-essential graphviz libgraphviz-dev python3-dev`.

### 3.2 Install
```bash
# with uv (recommended)
uv sync                       # or: uv venv && uv pip install -r requirements.txt
# or plain pip
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
```
*(Corporate note from README: set `http.proxy` to the Artifactory proxy if behind the IREQ firewall. The README's VS Code task automates venv creation on Windows.)*

### 3.3 Run — three entry points
```bash
# 1) Streamlit dashboard (interactive: evidence, BN explorer, export)
streamlit run ui/Dashboard.py            # → http://localhost:8501

# 2) CLI batch sampler (parallel; joblib loky)
python -m src.utils.sampler.Sampler \
  data/processed/bayesian_network/BN_EUEMr.XDSL \
  1000 \
  data/output/samples.csv \
  -ev '{"Type_Logement": "Maison individuelle"}'   # optional BN evidence

# 3) Notebook: run src/main.ipynb from src/ (writes the three building-*.csv)

# Docker
docker build -t lte-sampler . && docker run -p 8501:8501 lte-sampler
```
CLI args: `bayesian_network_filepath` (.XDSL), `samples_number` (int), `output_file` (.csv), `-ev/--evidence` (JSON; keys/values must match BN node labels).

### 3.4 Caveats
- `pyproject.toml` declares `[project.scripts] test = "scripts.test:main"` but there is **no `scripts/` package** — tests are not wired.
- Dict‑merge order differs by path (Dashboard `d1|d2` vs CLI `d2|d1`); harmless because BN and ResStock key domains are essentially disjoint.
- A missing housing CSV is silently skipped; a zero‑probability CPT row raises `Exception("Error in sampling for attribute: …")`.
- `site_time_zone_utc_offset` has a latent bug (set to `True` then overwritten with `-5`); functionally `-5`.

---

## 4. Adaptability & Extensibility — Alberta

### 4.1 The crucial distinction: data‑driven vs hardcoded
The system separates cleanly:

- **Data‑driven (adapts with NO Python edits, just regenerate artifacts):** the BN joint distribution (`BN_EUEMr.XDSL`/`Bn.yml`) and all option *probabilities* in `housing_characteristics/*.csv` (fuel mix, insulation‑by‑vintage, infiltration, setpoints, EV/pool/spa prevalence). Feed Alberta survey data through the offline pipeline and these change automatically.
- **Hardcoded in Python (MUST be edited):** `doMapping`'s label‑→‑value translations — most importantly the **weather file**, **UTC offset**, the **`QC_*` R‑value tables**, **fuel mappings**, **heat‑pump cold‑climate lockouts**, and locale constants. A new label that isn't in these dicts raises `KeyError`.

**Key insight:** location/climate is conveyed almost entirely by **two hardcoded outputs** — the `weather_station_epw_filepath` and `site_time_zone_utc_offset = -5`. No zip, lat/long, state code, IECC zone, HDD/CDD, or design temps are written anywhere; OS‑HPXML derives them from the EPW. So the *climate* port is small; the *statistical content* port is large.

### 4.2 Hardcoded Quebec assumptions to change (by category, with line refs)

**Climate / weather** — `sampler/Mapping.py:20-51`
- 3 hardcoded QC EPWs + Montreal fallback: `2020s_CAN_QC_Saguenay-Bagotville…717270_CWEC2016.epw` (`:25`), `…Montreal-McTavish.716120…` (`:27,32,34,40` default), `…Quebec-Lesage…717140…` (`:29`). → Replace with Alberta CWEC files (Calgary 718770, Edmonton 711230/Stony Plain, Lethbridge, Fort McMurray, Grande Prairie).
- `site_time_zone_utc_offset = -5` (`:51`) → **`-7`** (Mountain). Fix the buggy `True` on `:49-50`.
- DST `True` (`:43-45`) — OK for Alberta, but not parameterized.
- Heat‑pump compressor **lockout temps** hardcoded: −20 °C (`:1999,2066,3622`), −15 °C (`:2374,4237`), −12 °C biénergie switchover (`:4312`). → Re‑tune to Alberta design temps.

**Hydro‑Québec / grid** — `Territoire_HQ` is the *only* driver of weather selection (`:20-34`); `Bi-energie` dual‑energy class (`euemr/Mapping.py:97-104`, mapping at `sampler/Mapping.py:4308-4324,4375-4376`); pool multiplier `0.45 # site web hq` (`:4597`). Alberta has no HQ territories, no biénergie tariff, and a deregulated multi‑utility, fossil‑heavy grid.

**Geography** — `Territoire_HQ` (5), `Region_Administrative` (15 QC admin regions, `euemr/Mapping.py:114-131,707-723`), `ZONE` (27 HQ billing zones, `EUEMR_attributs.py:72-104`). → Replace with Alberta regions/utility service areas and rewire the EPW switch.

**Energy sources** — fuel mapping `Electricite/Mazout/Gaz naturel/Bi-energie/Bois → electricity/fuel oil/natural gas/…` (`:4365-4378`); **electricity‑as‑default** for water heater (`:4660`), dryer (`:4778`), and pervasive `heat_pump_backup_fuel:"electricity"` (50+ entries). → Alberta is **natural‑gas‑dominant**; flip defaults and rebuild the `Source_Energie_Chauf` distribution.

**Building code / vintage** — `QC_WoodStud-R…` wall (`:725-732`), `QC_R…` ceiling (`:752-759`), `QC_Wall-R…, interior` foundation (`:852-915`) assemblies; `An_ConstructionCode` bins `<1946/1946-1971/1971-1986/1986-2013/≥2013` (`euemr/Mapping.py:88-94`) tied to **Quebec code‑revision years**. → Re‑derive to NBC/Alberta Building Code envelope tiers and code‑era boundaries.

**Locale constants** — EV charging `3274/2248 kWh` "from the OPE model" (`:4447-4448`); **US RECS‑2015** plug‑load regression (`:5377-5384`); 8‑ft ceilings (`:88`); DHW setpoint 125 °F (`:4619-4668`); HRV/ERV‑heavy ventilation defaults (`:5451-5528`). → Replace with Alberta/Canadian sources.

**Latent blocker:** `HPXMLArg.py:204` `site_state_code` choices are **US‑states‑only** (no provinces) — currently unused (never written), but would reject Canadian values if ever populated.

### 4.3 The real barrier: data, not code
- **No Alberta EUEMr.** The model is conditioned end‑to‑end on a Quebec survey. Alberta needs an equivalent: NRCan **SHEU**/**CEUD** (Comprehensive Energy Use Database), StatCan housing/census data, or a utility survey (ENMAX/EPCOR/ATCO/Fortis). None drops into the EUEMr schema directly — you'd remap to the 40‑node structure (or re‑localize the schema).
- **Structural domain differences Alberta must reflect:**
  - **Heating:** Alberta ≈ natural‑gas forced‑air dominant; Quebec ≈ electric baseboards/heat pumps. The `Source_Energie_Chauf`/`Chauffage_Logement` CPTs essentially invert.
  - **Grid:** Quebec hydro (~very low gCO₂/kWh) vs Alberta historically coal→gas (high gCO₂/kWh). This tool doesn't compute emissions, but any downstream GHG accounting in SimParc/ResStock must swap emission factors.
  - **Climate:** colder northern AB + Chinook‑driven southern swings; different design temps drive different envelope/HP‑sizing norms.
  - **Code:** NBC/Alberta Building Code + National Energy Code for Buildings vintages ≠ Quebec milestones; envelope R‑value‑by‑vintage relationships differ.

### 4.4 Effort assessment & recommended path
| Task | Effort | Notes |
|---|---|---|
| EPW files + UTC offset + region→EPW switch | **Low** (hours) | Highest climate impact for least work |
| Re‑key fuel defaults to gas; biénergie removal; lockout temps | **Low–Med** | Mechanical dict edits in `doMapping` |
| `QC_*` envelope tables → AB/NBC R‑values + vintage bins | **Med** | Edit dicts + regenerate insulation CSVs |
| New region taxonomy (replace Territoire/Region/ZONE) | **Med** | Touches BN node set + mapping + weighting |
| **Source & ingest Alberta survey → rebuild BN + CPTs** | **High** (the project) | The genuine effort; everything statistical depends on it |
| Locale constants (EV/plug/pool) → AB sources | **Low–Med** | Constant swaps |

**Recommended approach:** (1) stand up the climate/region/fuel plumbing first to get *runnable* Alberta HPXML; (2) in parallel, source an Alberta survey/stock dataset and regenerate the BN + CPTs offline — that yields *statistically valid* Alberta samples. The `building-input-column-classification.csv` is a useful starting map (it flags which 11 columns are location‑dependent), but note it does **not** capture the EPW/UTC/Territoire hardcoding buried in `doMapping`.

---

## 5. Framework Integration (ResStock / SimParc)

### 5.1 What the output actually is
`building-mapping.csv` columns are the argument set of OpenStudio‑HPXML's **`BuildResidentialHPXML`** measure (confirmed: `data/hpxml/measure.xml` `<class_name>BuildResidentialHPXML</class_name>`, docs reference OS‑HPXML **v1.10.0**; `HPXMLArg.py` is a Python transcription of that schema). So each row is **directly consumable by the OS‑HPXML workflow** that turns measure args → an `.xml` → an EnergyPlus run.

### 5.2 Relationship to ResStock
This is a **ResStock‑derived, ResStock‑compatible** design with a **different sampler**:
- **Same artifacts/conventions:** ships ResStock's `options_lookup.tsv` (14,006 lines); the `housing_characteristics/*.csv` use ResStock's exact `Dependency=`/`Option=` grammar; the loader class is literally named `BuildstockBatchArguments` (NREL **BuildStockBatch**); many attribute Sources are tagged `"ResStock"`; the UI is titled **"ResStock‑QC"**.
- **Different sampling engine:** NREL ResStock samples a US housing stock via quota/conditional sampling over its TSV ecosystem (producing `buildstock.csv`). Here, the *core demographic/equipment* draw comes from a **pyAgrum Bayesian network trained on a Quebec survey**, and only the *technical* attributes use ResStock‑style CPTs. This injects real provincial joint structure (e.g. fuel ↔ territory ↔ vintage) that ResStock's US tables wouldn't capture for Quebec.

**Bridging to ResStock/BuildStockBatch:** to feed NREL's pipeline proper, you'd map this tool's `building-input.csv` columns to ResStock **Parameter Names** and supply an `options_lookup.tsv` — i.e. treat `building-input.csv` as an externally‑produced `buildstock.csv`. Conversely, `building-mapping.csv` already *bypasses* ResStock's sampler and is ready for the `BuildResidentialHPXML` step directly (the part BuildStockBatch ultimately calls). Minor transforms: column‑name alignment, unit/format conventions (this tool already emits HPXML‑native units, e.g. °F setpoint strings), and supplying `BuildResidentialScheduleFile`/weather paths for a full run.

### 5.3 Relationship to SimParc
`Sampler.main()`'s argparse description is literally *"Bayesian network sampler for SimParc."* **SimParc** is Hydro‑Québec's residential building‑**stock simulation** framework; this tool is its **front‑end population generator** — it produces the synthetic dwelling fleet (as OS‑HPXML args) that SimParc simulates at scale. Integration here is native: this *is* the SimParc input generator. (No transformation needed beyond what SimParc's OS‑HPXML runner already expects.)

### 5.4 Transformations summary
| Target | Already provided | Still needed |
|---|---|---|
| **OS‑HPXML `BuildResidentialHPXML`** | `building-mapping.csv` = the measure args, HPXML‑native units | weather `.epw` files on disk; schedule‑file generation; per‑row `hpxml_path` |
| **ResStock / BuildStockBatch** | `Dependency=/Option=` CPTs, `options_lookup.tsv`, ResStock arg names | map `building-input.csv` → `buildstock.csv` (Parameter Name alignment); project.yml wiring |
| **SimParc** | native HPXML‑arg CSV | none beyond SimParc's standard runner inputs |

---

*Sources: first‑hand reading of `Sampler.py`, `utils.py`, `bayesian_network.py`, the `euemr/` pipeline, `BuildstockBatchArguments`/`doMapping`, `HPXMLArg.py`, `measure.xml`, `Data_description.csv`, the housing CPTs, and the three output CSVs; cross‑checked against `Data_description.csv` as the authoritative crosswalk. Line references are to the current working tree.*
