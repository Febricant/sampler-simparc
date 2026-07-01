# Alberta/Calgary Probability Re-calibration Plan — LTE-Sampler-Residential

**Goal:** replace the Québec (EUEMr 2022 / Hydro-Québec) probabilities in the sampler with
probabilities that reflect Albertan (specifically Calgary) energy-use patterns, **without renaming
any parameter, node, or option label**. Only the probability *values* change; where a state is
impossible in Alberta (e.g. `Bi-energie`) its probability is set to 0, the state is kept.

---

## 1. Where the probabilities live (what must be edited)

The sampler draws a dwelling in three layers. Each layer has its own probability store:

| Layer | File(s) | What it holds | How to edit |
|---|---|---|---|
| **Stage 1 — Bayesian network** | `data/processed/bayesian_network/BN_EUEMr.XDSL` | CPTs of the 40 "demographic/equipment" nodes (dwelling type, vintage, fuel, heating system, water heater, appliances, EV, pool/spa…) | pyAgrum (`gum.loadBN` → `bn.cpt(node)[...] = …` → `saveBN`), pattern already in `calgary_adaptation/make_calgary_bn.py` (deleted in working tree, recoverable via `git checkout HEAD -- calgary_adaptation/`) |
| **Stage 2 — housing-characteristics CPTs** | `data/processed/housing_characteristics/*.csv` (52 files, `Dependency=…;Option=…` grammar) | Envelope (insulation, windows, infiltration), HVAC equipment efficiency, setpoints, PV, geometry, appliance usage | `calgary_adaptation/reweight_cpt_csv.py` (grammar-preserving reweighter) or full-row regeneration keeping the header untouched |
| **Stage 3 — deterministic mapping** | `src/utils/sampler/Mapping.py` | Hardcoded constants (EPW, UTC, DST — **already Calgary**), plus residual QC constants (heat-pump lockout temps, pool multiplier `0.45`, plug-load regression) | direct code edit |

Supporting facts about the current `calgary` branch:

- Geography is **already collapsed**: `Territoire_HQ = {Calgary}`, `Region_Administrative = {Alberta}` in `Bn.yml`/XDSL; `Mapping.py:17-31` forces the Calgary EPW (`CAN_AB_Calgary.Intl.AP.718770_CWEC2020.epw`), UTC −7, DST on.
- **Every CPT number downstream is still Québec**: `Source_Energie_Chauf` is still electricity-dominant with `Bi-energie` mass, envelope CSVs still carry `QC_*` R-value weights by Québec code eras, setpoints come from the HQ "Sondage Sensibilisation intégrée".
- `Bn.csv` and `data/processed/Data_description.csv` are **stale documentation** (still list 5 QC territories / 15 regions); the sampler never reads them, but they should be regenerated at the end.
- `res_ab_e.xlsx` (repo root, untracked) is **NRCan CEUD — Residential Sector, Alberta** (Tables 1–41, 2000–2017): heating-system stock by type, housing stock by type/vintage, water-heater and appliance stock. It is the aggregate backbone for several Tier-B parameters below.

---

## 2. Data sources (assessed, with endpoints)

### 2.1 ★ NRCan EnerGuide Rating System Open Data — the primary source (CKAN DataStore)

This is the dataset that makes the whole re-calibration feasible, and it is served by **exactly the
CKAN Data API requested** (`datastore_search`):

```
https://open.canada.ca/data/en/api/3/action/datastore_search
    ?resource_id=<year-resource-id>
    &filters={"PROVINCE":"AB"}            # or {"PROVINCE":"AB","CLIENTCITY":"Calgary"}
    &limit=32000&offset=0                 # paginate with offset
```

- Package id `0a7619fd-2ffe-44b5-9027-3dfcec0866fd`; one CSV resource per year, 2004–2025, all
  `datastore_active: true` (e.g. 2024 = `35aeeb59-b793-4396-8833-7d605823a82f`, 404,901 rows total,
  **54,293 Alberta rows, 18,069 Calgary rows** — verified 2026-07-06).
- **House-level microdata** (~400 fields): `YEARBUILT`, `TYPEOFHOUSE`, `STOREYS`, `FNDTYPE`,
  `HEATEDFLOORAREA`, `CEILINS`/`MAINWALLINS`/`FNDWALLINS` (RSI), `AIR50P` (blower-door ACH50),
  `WINDOWCODE`/`NUMWINDOWS`/`NUMWINESTAR`, `FURNACEFUEL`/`FURNACETYPE`/`FURSSEFF`/`HEATAFUE`,
  `SUPPHTGFUEL1/2`, `AIRCONDTYPE`, `PDHWFUEL`/`PDHWTYPE`/`PDHWEF`/`PRIMARYDHWTANKVOLUME`,
  `TMAIN`/`ThermostatHeatingNighttime`/`ThermostatCooling`/`PROGSMARTTHERMOSTAT`,
  `TOTALOCCUPANTS`, `KWPV`, `EGHRATING`/`ERSRATING`/`ERSENERGYINTENSITY`, fuel consumptions
  (`EGHFCON*`).
- **Known bias — must be corrected, not ignored:** the sample is self-selected (retrofit-grant
  applicants + new-home labelling). Older detached homes are over-represented pre-2020; new builds
  dominate `EVALTYPE = N`-type records. Mitigation: post-stratify (rake/IPF) to census margins —
  the codebase already has IPF machinery (`Create_Pond` in `src/utils/euemr/Mapping.py`).
  Also de-duplicate on `HOUSEID` (pre-/post-retrofit pairs) and keep the *pre-retrofit* ("E")
  record for stock characterization.

### 2.2 City of Calgary BenchmarkYYC APIs (the two requested endpoints)

```
New buildings:      https://data.calgary.ca/api/v3/views/a3uu-975p/query.csv   (SODA: /resource/a3uu-975p.csv)
Existing buildings: https://data.calgary.ca/api/v3/views/ixvd-v9b3/query.csv   (SODA: /resource/ixvd-v9b3.csv)
```

Verified content (2026-07-06):

- **New buildings** (12 rows, years 2024–2025): *aggregated* min/avg/max per property type —
  modelled floor area, storeys, FDWR (window-to-wall), % better than NECB reference, proposed
  electricity/gas/total energy and intensities, GHG, cost. Residential rows: `Multifamily
  Residential`, `Stacked Townhome`, `Mixed-Use`.
- **Existing buildings** (201 rows, 2019–2024): aggregated per property type — site/source EUI
  (GJ/m²), weather-normalized EUI, electricity/gas/district-heat use, GHG, `Average of Year Built`.
  Residential row: `Multifamily Housing`.

**Honest assessment:** these are aggregated, overwhelmingly *commercial/institutional* datasets.
They cannot supply household-level probabilities. Their correct roles in this project:

1. **Validation targets** — simulated Calgary multifamily (`Collective`) EUI distribution must
   bracket the BenchmarkYYC `Multifamily Housing` average site EUI (GJ/m², weather-normalized) and
   its year-to-year spread.
2. **New-construction anchors** — `≥2020` vintage rows of `Superficie_Totale`, `Nombre_Etages`,
   `Windows` (via FDWR) for multifamily/rowhouse can be sanity-checked or nudged toward the "new
   buildings" min/avg/max envelope.
3. Direct probability replacement from these two files: **none** (no per-dwelling categorical data).

### 2.3 Statistics Canada (via open.canada.ca CKAN catalogue → StatCan tables)

CKAN `package_search` locates these; the CSVs themselves are downloaded from StatCan (full-table
CSV zip or WDS API), since these packages are not DataStore-active:

| Dataset (CKAN id) | Use |
|---|---|
| *Primary heating systems and type of energy* (`ec3282b6…`, StatCan 38-10-0286) | Provincial heating fuel × equipment shares → priors/cross-check for `Source_Energie_Chauf`, `Chauffage_Logement` |
| *Household energy consumption, by type of dwelling* (`dc9943a6…`) | AB GJ/household by dwelling type → energy validation |
| Census 2021 Profile, Calgary CSD/CMA (98-316; also *Period of Construction × Structural Type × Tenure* crosstabs, `681bec18…`) | **Raking margins**: `Type_Logement`, `An_Construction`, `Mode_Occupation`, `Nombre_Personnes` (household size × dwelling type) |
| *Housing stock, dwelling units by type and tenure* (`4cf57f91…`) | Stock totals cross-check |
| Households and the Environment Survey (HES, tables 38-10-0019/0020/0026…) | AC saturation, programmable-thermostat share, thermostat setback behaviour (province level) → `Climatisation`, `ModeConsigne` |
| ZEV registrations (StatCan 20-10-0025) + AB transportation registrations | `Vehicule_Presence` (EV/PHEV per household in AB) |
| CMHC Rental Market Survey (Calgary vacancy rate) + census "dwellings not occupied by usual residents" | `Vacancy Status` |

### 2.4 NRCan CEUD Alberta residential (`res_ab_e.xlsx`, already in repo)

Tables 21–25 (heating system stock by building type & system type), 28–31 (water heater and
appliance stock by energy source), 14–20 (housing stock by type/vintage/floor space), 26 (stock
efficiencies). Aggregate (province, by year to 2017; newer editions to ~2021 downloadable from
oee.nrcan.gc.ca). Backbone for Tier-B reweighting and for appliance-fuel nodes.

### 2.5 Gap-fillers

- **SHEU-2015** (NRCan Survey of Household Energy Use, AB/Prairies tables): appliance counts,
  second refrigerators/freezers, range fuel, lighting.
- **City of Calgary open data (same Socrata portal)**: property assessments & building permits
  (garage presence, pool/hot-tub permits → `Presence_Garage`, `Piscine_Presence` proxies),
  Calgary civic census (historical) for household size.
- **AUC / ENMAX microgeneration statistics**: count of residential solar microgeneration sites in
  Calgary → `Has PV` marginal (KWPV in EnerGuide is biased high for retrofit applicants).
- **NECB/NBC(AE) code editions**: Alberta adopted energy requirements (9.36) in Nov 2016 — used to
  re-interpret the `An_ConstructionCode` *bins* (names kept) when assigning envelope tiers.

---

## 3. Parameter-by-parameter replacement map

Legend — **Tier A**: replace directly with Alberta/Calgary microdata (EnerGuide crosstabs, raked).
**Tier B**: only aggregate margins exist → keep Québec conditional *structure*, rescale to Alberta
margins (IPF / minimum cross-entropy). **Tier C**: no usable data → expert prior + Monte-Carlo
sensitivity. **Tier D**: location-independent, leave unchanged.

### 3.1 Stage-1 BN nodes (`BN_EUEMr.XDSL`)

| Node (name unchanged) | Tier | Alberta source → method |
|---|---|---|
| `Territoire_HQ`, `Region_Administrative` | done | already degenerate (Calgary / Alberta) |
| `Type_Logement` | **A** | Census 2021 Calgary CSD structural-type counts (map: Single-detached→`Maison individuelle`, Row→`Maison en rangee`, Semi/duplex→`Duplex`, small apt→`Triplex`… , apartment→`Collective`) — census is the *truth* for stock shares; EnerGuide only for conditionals |
| `An_Construction` (and derived `An_ConstructionCode` — keep QC-era state names, they are just bins) | **A** | Census period-of-construction × structural type (Calgary), refined with EnerGuide `YEARBUILT` |
| `Nombre_Etages` | **A** | EnerGuide `STOREYS` × `TYPEOFHOUSE`, raked to census type margins |
| `Nombre_Pieces` | **B** | Census "rooms" distribution not published at needed cross → rescale QC CPT (given `Type_Logement`,`Nombre_Etages`) to census *bedrooms+2* approximation; sensitivity in MC |
| `Superficie_Totale` | **A** | EnerGuide `HEATEDFLOORAREA` binned to the existing area states, by type; cross-check new-construction bins vs BenchmarkYYC new-buildings avg floor area |
| `Presence_SousSol` | **A** | EnerGuide `FNDTYPE` (B*/C*/S*/walkout codes) by type/vintage |
| `Presence_Garage` | **B/C** | City of Calgary property-assessment attributes (garage flag) if extractable; else HOT2000 `FOOTPRINT` heuristics; else keep QC + MC |
| `Nombre_Personnes` | **A** | Census household size × dwelling type (Calgary) |
| `Mode_Occupation` | **A** | Census tenure × dwelling type (Calgary) |
| **`Source_Energie_Chauf`** | **A** (top priority) | EnerGuide `FURNACEFUEL`(+`SUPPHTGFUEL*`) × `Type_Batiment` × vintage-code, raked; cross-check StatCan 38-10-0286 (AB ≈ 85–90 % natural gas, ~5–8 % electric, wood/propane rural remainder). `Bi-energie` → 0.0 (state kept). `Mazout` ≈ 0 in Calgary |
| **`Chauffage_Logement`** | **A** | EnerGuide `FURNACETYPE`/`HPEquipType` mapped onto the 20 existing French system states (`Système central à air chaud` dominant ~85 %+ for gas; `Plinthes électriques` marginal; growing ASHP share post-2020 from Greener-Homes records) |
| `Climatisation` | **A/B** | EnerGuide `AIRCONDTYPE` (biased) blended with HES AB central-AC saturation (rapidly rising; ~40–55 % range) — rake EnerGuide crosstab to HES margin |
| `ChaufEau_Presence`, `ChaufEau_Type`, `ChaufEau_ChaufType` | **A** | EnerGuide `PDHWFUEL`/`PDHWTYPE`/`PRIMARYDHWTANKVOLUME` (AB: gas storage tank dominant, electric minority, tankless growing in new builds); cross-check CEUD Tables 28–29 |
| `Cuisiniere_Presence`, `Cuisiniere_Energie` | **B** | SHEU-2015 AB range-fuel shares + CEUD appliance stock (gas range share in AB ≫ QC) |
| `Refrigerateur_Nombre`, `Congelateur_Nombre` | **B** | SHEU-2015 / CEUD appliance stock per household (AB freezer ownership higher than QC); rescale QC CPT margins |
| `LaveLinge_Type`, `SecheLinge_Presence`, `LaveVaisselle_Presence` | **B/D** | near-universal in detached; rescale with SHEU margins, low impact |
| `Eclairage_LED` | **B/C** | HES lighting tables (province); else keep QC (converging nationally) + MC |
| `Vehicule_Presence`, `Vehicule_BornePresence` | **B** | StatCan ZEV registrations for AB (EV share of fleet in AB ≪ QC — this matters, QC probabilities materially overstate Calgary EV load) scaled to per-household prevalence; charger-presence conditional kept from QC |
| `Spa_Presence` … `Spa_Utilisation_*` (5 nodes) | **C** | no AB microdata; hot-tub prevalence from Calgary permit counts (rough marginal) or retain QC prevalence ±50 % MC band; usage conditionals kept |
| `Piscine_Presence` … `Piscine_ChaufType` (6 nodes) | **C** | Calgary outdoor-pool prevalence is far below QC (climate + lot size): pool-permit counts / aerial-survey studies as marginal anchor (likely ≤1–2 % of detached vs ~20 %+ QC); conditionals kept; MC band |
| `Type_Batiment`, remaining structural derivations | — | deterministic children, follow automatically |

### 3.2 Stage-2 housing-characteristics CSVs (names & option labels unchanged)

| CSV | Tier | Alberta source → method |
|---|---|---|
| `Infiltration.csv` (Type_Logement × An_Construction → ACH50 bins) | **A — best data in the whole exercise** | EnerGuide `AIR50P` is a *measured blower-door* value: bin per (type, vintage) crosstab directly. Calgary pre-1960 stock leakier, post-2016 (9.36 code) much tighter |
| `Insulation Ceiling / Wall / Foundation Wall / Floor / Slab.csv` | **A** | EnerGuide `CEILINS`/`MAINWALLINS`/`FNDWALLINS` (RSI) → map each record to the *nearest existing `QC_R*` option label* (labels kept verbatim per requirement), crosstab by (type, vintage) |
| `Windows.csv` | **A/B** | EnerGuide `WINDOWCODE`/`NUMWINU105`/`NUMWINU122`/`NUMWINESTAR` → glazing-type shares by (type, vintage); fall back to vintage priors (double-clear dominant 1970–2000, low-E post-2010) |
| `HVAC Heating Efficiency.csv` (fuel × system → 38 equipment options) | **A** | EnerGuide `FURSSEFF`/`HEATAFUE` distribution *within* each (fuel, system) row → weights over the existing AFUE/HSPF option labels (e.g. gas furnace split ~ condensing 92–96 % AFUE dominates post-2010 — QC's `Fuel Furnace, 80% AFUE`=1.0 row is wrong for Calgary's newer furnace fleet) |
| `ModeConsigne.csv` + `Heating Setpoint.csv` + `Basement/Garage Heating Setpoint.csv` | **A/B** | EnerGuide `TMAIN` & `ThermostatHeatingNighttime` give (day, night) pairs: derive setback-mode shares (`Constant` vs `Baisse de nuit uniquement`…) and re-weight the 677 setpoint-triple options nearest to observed (day,day,night) triples; `PROGSMARTTHERMOSTAT` + HES thermostat tables corroborate |
| `Cooling Setpoint.csv` | **B** | EnerGuide `ThermostatCooling` (sparse) + HES; else shift QC distribution +0/+1 °C, MC band |
| `Has PV.csv`, `PV System Size.csv`, `PV Orientation.csv`, `Battery.csv` | **B** | Marginal from AUC/ENMAX residential microgeneration counts ÷ Calgary dwellings; size distribution from EnerGuide `KWPV`>0 records; orientation keep generic |
| `Geometry Foundation Type.csv`, `Geometry Stories.csv`, `Geometry Building *` | **A/B** | EnerGuide `FNDTYPE`/`STOREYS` for low-rise; multifamily unit-count structure from census/BenchmarkYYC new-buildings storeys |
| `Vacancy Status.csv` | **B** | CMHC Calgary rental vacancy + census unoccupied-dwelling share (replace uniform 0.98/0.02) |
| `Roof Material.csv`, `Plug Load.csv`, `Radiant Barrier.csv` | **C/D** | asphalt-shingle dominance already ~ true for Calgary; plug-load regression is US-RECS-based (leave; note in limitations) |
| `Usage Level` + appliance usage multipliers, `Refrigerator/Freezer/Dishwasher Efficiency`, `Door *`, `Interior Shading`, `Mechanical/Natural Ventilation`, `* Spot Vent Hour`, `Ceiling Fan`, `Dehumidifier`, `Overhangs`, `HVAC Has Shared System`, `Geometry Attic Type`, `Geometry Wall Exterior Finish`, `Lighting Usage Level`, `Orientation` | **D** | ResStock-generic behavioural/physical defaults, not Québec-specific — leave unchanged |
| `Spa ChaufType.csv` | **C** | follows `Spa_Presence` decision (electric-dominant is fine for AB hot tubs) |

### 3.3 Stage-3 residual constants (`src/utils/sampler/Mapping.py`)

Already Calgary: EPW, UTC −7, DST. Still to review (not probabilities, but bias results):
heat-pump lockout temperatures (Calgary design temp −27 °C → cold-climate ASHP cutoffs), pool-pump
multiplier `0.45 # site web hq`, EV charging kWh constants (HQ studies), DHW 125 °F (fine).

---

## 4. Implementation plan

### Phase 0 — restore & branch hygiene (½ day)
1. `git checkout HEAD -- calgary_adaptation/` (restores the four deleted scripts — they are the
   intended mutation/validation toolkit).
2. Commit the current geography-collapse working-tree changes so data edits are separately diffable.

### Phase 1 — data acquisition: `calgary_adaptation/fetch_alberta_data.py` (1–2 days)
- **EnerGuide**: loop year-resources 2004–2025 via `datastore_search` with
  `filters={"PROVINCE":"AB"}`, `limit=32000` + offset pagination; select only the ~45 needed
  fields via the `fields` parameter to cut payload; cache raw to
  `data/input/alberta/energuide/<year>.parquet`. Expect ~200–400k AB rows total.
- **Calgary Socrata**: pull both `query.csv` endpoints verbatim to `data/input/alberta/benchmarkyyc/`.
- **StatCan/CEUD**: census profile extracts (Calgary CSD), 38-10-0286, HES tables, ZEV
  registrations — small CSVs, commit them with a `SOURCES.md` recording URL + retrieval date +
  licence (Open Government Licence — Canada / City of Calgary OGL).

### Phase 2 — clean & de-bias: `calgary_adaptation/build_alberta_weights.py` (2–3 days)
1. De-duplicate EnerGuide on `HOUSEID` (keep earliest pre-retrofit evaluation per house); split
   new-home (`EVALTYPE`-based) vs existing-stock records.
2. Map EnerGuide categories onto the sampler's existing state vocabularies
   (`TYPEOFHOUSE→Type_Logement`, `YEARBUILT→An_Construction`, RSI→nearest `QC_*` label, etc.) —
   one explicit dictionary per node, unit tests on unmapped values (fail loudly, like
   `reweight_cpt_csv.py` does).
3. **Rake** (IPF) record weights to census margins: `Type_Logement × An_Construction ×
   Mode_Occupation` for Calgary CSD — reuse/adapt `Create_Pond` from `src/utils/euemr/Mapping.py`.
   Output: a weighted Alberta pseudo-survey table, the analogue of the formatted EUEMr CSV.

### Phase 3 — Stage-1 BN rewrite: extend `make_calgary_bn.py` (2 days)
- Replace the blunt `force_node()` uniform overrides with **data-driven conditional CPTs**: for
  each Tier-A node, compute the weighted crosstab over its *existing parents* (same DAG) from the
  pseudo-survey and write it row-by-row into the CPT; Tier-B nodes get IPF-rescaled Québec CPTs
  (keep conditional odds, match Alberta margins); Tier-C nodes untouched.
- Keep writing to `BN_Calgary.XDSL` (non-destructive), then point `run_calgary_batch.py` at it.
- `Bn.yml` needs no edit (states/parents unchanged — only numbers move).

### Phase 4 — Stage-2 CSV rewrite: extend `reweight_cpt_csv.py` (2 days)
- Add a `replace_rows(path, table)` mode: full-row probability replacement from a crosstab keyed
  on the `Dependency=` values, preserving header bytes and option order; `.bak` + row-sum
  assertions retained.
- Apply per the §3.2 table (Infiltration, Insulations, Windows, HVAC Heating Efficiency,
  ModeConsigne/Setpoints, Has PV/size, Foundation Type, Vacancy Status).

### Phase 5 — validation: extend `validate_calgary.py` + `src/Validation_distribution.ipynb` (2 days)
1. **Plumbing asserts** (existing): Calgary EPW everywhere, UTC −7, DST, zero `Bi-energie`.
2. **Distribution asserts** (new): for every replaced CPT, total-variation distance between
   `building-input.csv` marginals (N = 10–50k draws) and the source crosstab < 0.02; chi-square
   spot checks on key conditionals (fuel × vintage, ACH50 × vintage).
3. **Reality checks**: natural-gas share of heating ≈ 85–90 %; median ACH50 by vintage
   monotonically decreasing; PV prevalence ≈ AUC microgen count.
4. **Energy closure** (after simulation): mean site energy per single-detached gas home vs CEUD
   AB Tables 34–41 (GJ/household); simulated `Collective` EUI vs BenchmarkYYC `Multifamily
   Housing` weather-normalized site EUI (GJ/m²).

### Phase 6 — uncertainty & gaps: Monte-Carlo layer (1–2 days, optional but recommended)
For Tier-B/C parameters, quantify what the missing data could do:
- **Dirichlet resampling**: perturb each replaced CPT row `p` with `Dirichlet(n_eff · p)` where
  `n_eff` = the (raked) sample count behind that row; re-run the sampler K times → confidence
  bands on stock composition and (post-simulation) energy.
- **Scenario bounds for Tier C**: pool/spa prevalence {QC value, ½×, ⅕×}, EV prevalence
  {AB-registration value ±50 %} → report sensitivity of city-level load, decide whether sourcing
  better data is worth it.
- If a needed *joint* distribution never materializes (e.g. setpoint triples), fit a parametric
  model to the available margins (e.g. Gaussian copula over day/night setpoints from TMAIN
  moments) and Monte-Carlo-generate the option weights.

### Phase 7 — housekeeping (½ day)
Regenerate `Bn.csv` / `Data_description.csv` (stale geography), document every replaced
probability in a `PROVENANCE.md` (node → source → retrieval date → method → n), commit
`res_ab_e.xlsx` under `data/input/alberta/`.

**Total effort ≈ 10–13 working days.**

---

## 5. Risks & caveats

1. **EnerGuide selection bias** is the main statistical threat — raking to census margins fixes
   composition (type/vintage/tenure) but not within-cell bias (retrofit applicants may be leakier
   than average pre-retrofit homes). Mitigate by comparing pre-2020 vs Greener-Homes-era cohorts.
2. **BenchmarkYYC is not a probability source** — treat it strictly as validation; its residential
   coverage (large multifamily, self-reported GFA) is thin (201 aggregate rows).
3. **Small cells**: some (type × vintage) cells for `Collective` dwellings will be sparse in
   EnerGuide (MURBs are underrepresented) — shrink toward the type-marginal (empirical-Bayes /
   Dirichlet prior) rather than using raw sparse rows.
4. **Name preservation** means some labels become semantically odd for Alberta (`QC_R…` insulation
   tiers, `Bi-energie` at p=0, `An_ConstructionCode` bins named after QC code years). This is
   accepted by design; record it in `PROVENANCE.md` so downstream users aren't confused.
5. **CKAN API limits**: `datastore_search` caps `limit` (32,000); always paginate and verify
   `result.total`; the portal occasionally rate-limits — cache raw pulls, never fetch at sampler
   runtime.
