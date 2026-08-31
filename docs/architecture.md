# Architecture

Two programs joined by a CSV. This page maps each one, and the connection betwwen them.

---

## Stage 1 — the sampler

The Calgary re-calibration inserts itself here, reading the EnerGuide and census data and creating
`BN_Calgary.XDSL`. [calgary-recalibration.md](calgary-recalibration.md).

### Run time

```
BN_Calgary.XDSL  (or BN_EUEMr.XDSL)
        │
        ▼  sampler/bayesian_network.py — loads the network; reads Bn.yml as UTF-8
   Sampler.GUM_Sampling(N, evidence)
        │      pyAgrum BNDatabaseGenerator, topological variable order.
        │      Loops, drawing more, until N rows satisfy the evidence.
        ▼
   Sampler.run_parallel  ── joblib/loky, work split into chunks
        │
        ├─ resstock_args_sampling
        │     For each of ~52 attributes: filter its CPT by the Dependency=
        │     columns using what has been drawn so far, normalise the Option=
        │     row into a pmf, and draw from it. Later attributes can depend on
        │     earlier ones, so order matters.
        │     Then HConsignes() adds stochastic heating-setback hours H1–H4.
        │
        └─ MapHPXML().run  ── ~6,200 lines of deterministic translation from
              French/ResStock labels to snake_case OS-HPXML arguments.
              Hardcodes the Calgary weather file, UTC−7 and DST.
        ▼
   stabilize_export  ── reindex onto the pinned column contract; pad booleans
        ▼
   building-input.csv (97 cols) │ building-mapping.csv (219) │ building-test.csv (both)
```

---

## Stage 2 — SimParc

```
buildings.csv
     │
     ▼  main.py::load_input
   validation.report / .repair / .preprocessing_succeeds
     │      Refuses, non-zero, anything OpenStudio would reject.
     │      --repair fixes the known stale-export defects instead.
     ▼
   preprocessing.preprocess_data_types
     │      Cast each column to the type measure.xml declares.
     │      Assign building_id = 1..N. Pad every missing HPXML argument with None.
     ▼
   upgrading.apply_upgrades            ← config.UPGRADE_SETTINGS (None by default)
     │      Filter → sample by adoption rate → scale the improved properties →
     │      clone as building_id + "_SetOfMeasuresN"
     ▼
   preprocessing.preprocess_data_to_dict
     │      Split each row into recognised measure arguments vs carried metadata.
     │      Drop invalid Choice values and NaNs.
     ▼
 ┌── dask LocalCluster ── or --serial ── or stop here for --dry-run ──────────┐
 │  parallelization.batch_building_simulation                                 │
 │    ├─ prepare_building                                                     │
 │    │     mkdir results/<building_id>/                                      │
 │    │     inject hpxml_path, weather file, timestep, run period —           │
 │    │     every path through osrunner.to_container_path                     │
 │    │     Building(...).create_osw() → results/<id>/in.osw                  │
 │    └─ run_building                                                         │
 │          subprocess.run(osrunner.openstudio_command(osw))                  │
 └────────────────────────────────────────────────────────────────────────────┘
     │
     ▼  the OpenStudio CLI executes in.osw:
        1. BuildResidentialHPXML        → built.xml
        2. BuildResidentialScheduleFile → stochastic.csv, built-stochastic-schedules.xml
        3. HPXMLtoOpenStudio            → in.osm → in.idf → EnergyPlus runs
        4. ReportSimulationOutput       → run/results_annual.csv, run/results_timeseries.csv
     ▼
   postprocessing.postprocess_results
        Read results/<id>/out.osw for status / last step / failure message
        ├─ Success → annual results merged into the row  → results/metadata.parquet
        │            timeseries reshaped (2-level header) → results/timeseries.parquet
        └─ Failure → the row, cast to string             → results/errors.parquet
```
---

## The connection

```
sampler/src/utils/hpxml/hpxml_column_list.py     the contract, generated
              │
              ├── sampler writes CSVs reindexed onto it
              │
              └── simparc/preprocessing.py reads them against measure.xml
```
