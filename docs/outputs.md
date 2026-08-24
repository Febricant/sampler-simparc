# Outputs and disk

The headline, before anything else:

> At default settings a batch produces about **156 MB per building**, measured. Eighty buildings is
> roughly **12 GB**; a thousand-building run needs about **150 GB**. This is not something you start
> without checking free space first.
>
> On a 12-core Windows host with the Docker runner, one building takes about **27 seconds** wall
> clock, so the batch is disk-bound long before it is CPU-bound.

This is not accidental bloat — it is `TIMESERIES_FREQUENCY = "timestep"` at a 15-minute timestep
(35,040 rows per variable per building) plus `DEBUG_MODE = True` (a full OSM and IDF per building).
Both are useful while developing and expensive in bulk. See [configuration.md](configuration.md).

## Sampler outputs

Written to `sampler/data/output/`:

| File | Contents |
|---|---|
| `building-input.csv` | 97 human-readable sampler attributes, one row per dwelling |
| `building-mapping.csv` | 219 OS-HPXML measure arguments, one row per dwelling |
| `building-test.csv` | The two concatenated — 316 columns. This is what you feed SimParc. |
| `building-input.provenance.json` | Run receipt: SHA-256 of every probability file used, the git commit, and row counts |

These are small — a thousand dwellings is a few MB.

The provenance file is the thing to reach for when you are unsure what a CSV represents. It answers
"was this drawn from the Québec or the Calgary probabilities, and at which commit?" without inferring
it from the data.

The Calgary analysis branch additionally writes `calgary_energy_profile.csv`,
`calgary_fsa_energy_profile.csv`, `calgary_fsa_weather_profile.csv`,
`energuide_vs_quebec_crosswalk.csv` and `calgary_bn_targets.json`, plus figures under
`calgary_adaptation/figures/`.

## SimParc outputs

Everything lands under `simparc/results/`, which is gitignored.

### Per building

```
results/<building_id>/
├── in.osw                            the workflow handed to OpenStudio
├── out.osw                           what came back: status, last step, errors
├── built.xml                         the generated HPXML
├── built-stochastic-schedules.xml
├── stochastic.csv                    generated occupancy schedules
├── generated_files/
├── reports/
└── run/
    ├── in.osm, in.idf                the OpenStudio and EnergyPlus models  (DEBUG_MODE)
    ├── eplusout.sql / .eso / .csv / .json / .msgpack   raw EnergyPlus output
    ├── results_annual.csv
    ├── results_timeseries.csv
    └── data_point.zip
```

`out.osw` is where to look when a building fails; post-processing reads `status`, the last step
reached, and `step_errors` from it.

### Consolidated datasets

Post-processing folds every run into three hive-partitioned parquet datasets, all partitioned by
`building_id`:

| Dataset | One row per | Contents |
|---|---|---|
| `results/metadata.parquet` | building | The input row plus its annual results — consumption by fuel and end use, peaks, loads, unmet hours, HVAC summary |
| `results/timeseries.parquet` | building × timestamp | The timeseries series selected in `config.py`, reshaped from a two-level header |
| `results/errors.parquet` | failed building | The input row, **entirely cast to string** |

Two details that matter in practice:

- **Errors are stringified deliberately.** A column that holds a number for one failure and blank or
  free text for another gives the partitions conflicting types, and `errors.parquet` then cannot be
  read as a single dataset. Casting everything to string keeps it readable.
- **Writes are idempotent.** All three use `existing_data_behavior='delete_matching'`, so re-running a
  subset of buildings replaces exactly those partitions and leaves the others untouched. Re-running
  after fixing a handful of failures is safe and cheap.

Reading them back:

```python
import pandas as pd
annual = pd.read_parquet("results/metadata.parquet")
ts     = pd.read_parquet("results/timeseries.parquet",
                         filters=[("building_id", "in", [1, 2, 3])])
```

Use `filters=` on the timeseries dataset. It is the large one, and partition pruning is the difference
between reading three buildings and reading all of them.

### Dask reports

`dask-report-baseline.html`, `dask-report-upgrades.html` and `dask-report-postprocessing.html` land in
the working directory. They are diagnostics — worth opening when a batch was slower than expected,
safe to delete, and gitignored. They need `bokeh`; if it is missing the run still completes and
prints a note, because the report must never be able to discard a finished batch.

## Keeping the size down

In rough order of effect:

1. `TIMESERIES_FREQUENCY = "hourly"` — about a fourfold cut. `"none"` removes timeseries entirely if
   you only need annual totals.
2. `DEBUG_MODE = False` — drops the per-building OSM and IDF.
3. Turn off `INCLUDE_TIMESERIES_*` categories you are not analysing.
4. Once `metadata.parquet` and `timeseries.parquet` are written, the per-building `results/<id>/`
   directories are re-derivable and can be deleted. Keep `out.osw` for any building you might need to
   diagnose.

Use `--limit N` to size a run empirically before committing to the full batch.
