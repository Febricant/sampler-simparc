# Architecture

Two programs joined by a CSV. This page maps each one, then the seam between them.

A distinction worth holding onto throughout: the *probability data* — the Bayesian network and the
conditional probability tables — is **built offline** by notebooks and calibration scripts, and only
**read** at runtime. The sampler you run day to day does not learn anything; it draws from artefacts
that were prepared earlier.

---

## Stage 1 — the sampler

### Build time (occasional)

```
EUEMr 2022 survey (.xlsx)
   └─► src/utils/euemr/Mapping.py          recode survey codes (QA4, QC1R, ...) into
   │                                       French labels; compute sampling weights
   └─► src/utils/euemr/EUEMR_bn_generator.py
          └─► data/processed/bayesian_network/BN_EUEMr.XDSL   (+ Bn.yml describing it)

Parametres_ValeursRegionalisees_v2.xlsx
   └─► src/utils/Create_housing_characteristics.ipynb
          └─► data/processed/housing_characteristics/*.csv    (~53 CPTs)

data/hpxml/measure.xml
   └─► src/utils/hpxml/ParseHPXMLinputs.py
          └─► src/utils/hpxml/HPXMLArg.py                     (generated, ~4,300 lines)
```

The Calgary re-calibration inserts itself here, reading the EnerGuide and census data and emitting
`BN_Calgary.XDSL` plus reweighted CPTs. See [calgary-recalibration.md](calgary-recalibration.md).

### Run time (every sample)

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

Two implementation details that look odd until explained:

- **`Sampler.__getstate__` drops the network before pickling.** `run_parallel` uses the loky process
  backend, so `self` is pickled to each worker. pyAgrum cannot *un*pickle a discrete variable that has
  only one label, and `Territoire_HQ` is degenerate at `{Calgary}` after the re-calibration — workers
  died with `BrokenProcessPool`. The workers only ever run the CPT sampling and HPXML mapping, which
  never touch the network (network sampling has already finished in the parent), so dropping it is
  both correct and smaller.
- **Sampling loops rather than drawing once.** Evidence makes rejection sampling lossy, so
  `GUM_Sampling` keeps drawing, scaling its request by the observed yield, until it has N rows.

---

## Stage 2 — SimParc

Flat module layout, no packages; every module imports `config` directly, and `config` is effectively a
global singleton. `config.ARGS_CONSTRAINTS` is computed **at import time** by parsing
`measures/BuildResidentialHPXML/measure.xml` — the vendored measure XML *is* the argument schema,
about 330 arguments of it.

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
     ▼  the OpenStudio CLI executes in.osw — four measures in sequence:
        1. BuildResidentialHPXML        → built.xml
        2. BuildResidentialScheduleFile → stochastic.csv, built-stochastic-schedules.xml
        3. HPXMLtoOpenStudio            → in.osm → in.idf → EnergyPlus runs
        4. ReportSimulationOutput       → run/results_annual.csv, run/results_timeseries.csv
     ▼
   postprocessing.postprocess_results   (Dask again)
        Read results/<id>/out.osw for status / last step / failure message
        ├─ Success → annual results merged into the row  → results/metadata.parquet
        │            timeseries reshaped (2-level header) → results/timeseries.parquet
        └─ Failure → the row, cast to string             → results/errors.parquet
```

A fifth measure, `ModifyStochasticFilePython`, is vendored but currently commented out in
`building.py`.

### Why `osrunner.py` exists

It is the whole cross-platform story in one module, and it is worth reading before changing anything
about paths.

- `to_container_path()` maps `C:\...\simparc\results\10` to `/workspace/results/10`, and **raises**
  for any path outside the project — the container cannot see those, and failing loudly beats handing
  OpenStudio a path it will silently misresolve.
- `openstudio_command()` returns an **argv list**, executed without a shell. That is deliberate: a
  project directory containing a space needs no quoting, and Git Bash cannot mangle `/workspace` into
  a Windows path on the way through.
- `resolve()` is called once per batch from `main.py` and actually runs `openstudio --version`, so a
  misconfiguration appears immediately instead of as N identical worker failures.
- Detection is memoised at module level, and a native binary beats Docker under `"auto"` so the dev
  container keeps working.

### Idempotent results

All three parquet datasets are hive-partitioned by `building_id` and written with
`existing_data_behavior='delete_matching'`. Re-running a subset of buildings replaces exactly those
partitions and leaves the rest alone.

### One more safety valve

`main.py::performance_report_or_nothing` wraps Dask's `performance_report`. The report is rendered by
bokeh when the context exits, so a missing or broken bokeh would otherwise raise *after* every
simulation had completed — discarding a finished batch and the post-processing that should have
followed. The report is a diagnostic; the run is the result.

---

## The seam

```
sampler/src/utils/hpxml/hpxml_column_list.py     the contract, generated
              │
              ├── sampler writes CSVs reindexed onto it
              │
              └── simparc/preprocessing.py reads them against measure.xml
```

This is the coupling the monorepo exists to make visible. The sampler encodes knowledge of SimParc's
internals — one of its generator comments explains that Integer-typed arguments are excluded from the
export precisely because a padded blank would make SimParc's `preprocess_data_types` raise
`IntCastingNaNError`. That is a cross-repository invariant that nothing could test while the two
halves lived apart.

Read [data-contract.md](data-contract.md) next.

## Where the same logic lives twice

Three files parse the same `measure.xml` into an argument schema, and they have diverged:

| File | Emits |
|---|---|
| `sampler/src/utils/hpxml/ParseHPXMLinputs.py` | `HPXMLArg.py`, a generated class |
| `simparc/ParseHPXMLinputs/ParseHPXMLinputs.py` | `HPXMLinputs.csv` |
| `simparc/hpxml_input_schema.py` | `ARGS_CONSTRAINTS`, in memory at import |

All three copies of `measure.xml` in the tree are byte-identical once line endings are normalised, so
the schema itself is consistent; it is the three *parsers* that have diverged. See
[known-issues.md](known-issues.md).
