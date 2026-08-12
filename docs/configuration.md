# Configuration

## SimParc — `simparc/config.py`

There is no config file format. `config.py` **is** the configuration, as module-level constants, and
every other module imports it directly. Edit the file to change a run.

One consequence worth knowing: `ARGS_CONSTRAINTS` is computed at import time by parsing
`measures/BuildResidentialHPXML/measure.xml` via a **relative** path. `config.py` therefore cannot be
imported from a different working directory.

### Choosing the OpenStudio runner

| Constant | Default | Meaning |
|---|---|---|
| `OPENSTUDIO_RUNNER` | `"auto"` | `"auto"` prefers a native binary and falls back to Docker; `"docker"` always uses the image; `"native"` always calls a binary. See [install.md](install.md). |
| `DOCKER_IMAGE` | `"simparc-dev:latest"` | Image carrying OpenStudio 3.9.0, built from `.devcontainer/Dockerfile` |
| `CONTAINER_WORKSPACE` | `"/workspace"` | Where the project is bind-mounted inside the container |
| `OPENSTUDIO_EXE` | `"openstudio-3.9.0/bin/openstudio"` | Native binary. A relative path resolves against the project root. Unused in the dev container. |

### Location and physics

| Constant | Default | Meaning |
|---|---|---|
| `WEATHER_EPW_FILENAME` | `CAN_AB_Calgary.Intl.AP.718770_CWEC2016.epw` | **Fixed for every building in the batch.** The file must exist in `weather/`. |
| `SIMULATION_TIMESTEP` | `15` | Minutes. Must be an integer divisor of 60. |
| `SIMULATION_RUN_PERIOD` | `"Jan 1 - Dec 31"` | Three-letter month plus day number |
| `ADD_COMPONENT_LOADS` | `False` | Heating/cooling component load breakdown. Off by default because it is slow. |
| `SKIP_VALIDATION` | `False` | Skip HPXML validation for speed |

The single weather file is a real modelling limitation, not an oversight to work around casually:
every dwelling in a batch experiences identical weather. `sampler/calgary_adaptation/weather_profile.py`
derives per-FSA degree-day differences across Calgary and is honest that it holds **temperature only**
and cannot synthesise a full EPW.

### Parallelism

| Constant | Default | Meaning |
|---|---|---|
| `DASK_NUM_WORKERS` | `5` | Workers for the simulation phase |
| `DASK_NUM_WORKERS_POSTPROCESSING` | `5` | Workers for post-processing |

Each worker runs a full EnergyPlus process. Tune to cores and, more often, to disk throughput and RAM
rather than to core count alone.

### Output selection — where your disk goes

`DEBUG_MODE` and `TIMESERIES_FREQUENCY` dominate output size. Everything else is noise by comparison.

| Constant | Default | Effect |
|---|---|---|
| `DEBUG_MODE` | `True` | Emits the OSM, the IDF and extra logs **per building**. Invaluable while debugging, expensive in bulk. |
| `TIMESERIES_FREQUENCY` | `"timestep"` | `"none"`, `"timestep"`, `"hourly"`, `"daily"`, `"monthly"`. At the default 15-minute timestep this is **35,040 rows per building per variable**. |

Dropping to `"hourly"` cuts timeseries volume roughly fourfold; `DEBUG_MODE = False` removes the
per-building model files. Together they are the difference between a batch that fits on a laptop and
one that does not. See [outputs.md](outputs.md).

The `INCLUDE_ANNUAL_*` and `INCLUDE_TIMESERIES_*` flags select which result categories are reported.
Annual flags are cheap — they add columns to one row per building. Timeseries flags are not: each one
adds a full-length series. Enabled timeseries by default are total, fuel and end-use consumptions plus
weather; system-use, emissions, loads, unmet hours, zone temperatures and airflows are off.

| Constant | Default | Meaning |
|---|---|---|
| `TIMESERIES_TIMESTAMP_CONVENTION` | `"start"` | Whether a stamp labels the start or end of its interval |
| `ADD_TIMESERIES_UTC_COLUMN` | `True` | Adds a UTC column |
| `ADD_TIMESERIES_DST_COLUMN` | `False` | Adds a daylight-saving column |
| `USER_OUTPUT_VARIABLES` / `USER_OUTPUT_METERS` | `""` | Comma-separated raw EnergyPlus variables or meters, if you need something the standard report omits |

### Retrofit scenarios

`UPGRADE_SETTINGS` is `None` by default, meaning baseline only. Its structure, with a worked example
commented out in the file:

```python
UPGRADE_SETTINGS = {
    "Set of upgrades 1": {
        "Filters": [("geometry_unit_type", "==", "single-family detached"),
                    ("geometry_unit_num_bedrooms", ">=", 3)],
        "Adoption rate": 0.5,
        "Upgrades": {
            "Wall insulation":   {"improvement_rate": 0.2},
            "Window properties": {"improvement_rate_uvalue": 0.3,
                                  "improvement_rate_shgc": 0.15},
            "Air leakage":       {"improvement_rate": 0.25},
        },
    },
}
```

`Filters` selects candidates, `Adoption rate` samples a fraction of them, and each improvement scales
the relevant property. Matched buildings are **cloned** rather than modified, so baseline and upgraded
variants are both simulated — plan for the batch to roughly double.

---

## The sampler — configuration as data

The sampler has no settings module. What would be configuration elsewhere is *data*, which is why the
provenance file matters.

| Artefact | Role |
|---|---|
| `data/processed/bayesian_network/BN_Calgary.XDSL` | The Calgary network. Built by `apply_to_sampler.py bn`. |
| `data/processed/bayesian_network/BN_EUEMr.XDSL` | The original Québec network. Never modified by the re-calibration. |
| `data/processed/bayesian_network/Bn.yml` | Node descriptions and state lists. **Read as UTF-8** — a cp1252 default corrupts accented state labels and pyAgrum then rejects them as evidence. |
| `data/processed/housing_characteristics/*.csv` | ~53 conditional probability tables in ResStock's `Dependency=` / `Option=` format |
| `data/input/housing_characteristics/options_lookup.tsv` | ResStock option lookup |

Which network gets used is decided by `default_bn()` in `calgary_adaptation/apply_to_sampler.py`:
`BN_Calgary.XDSL` if it has been built, otherwise the Québec original **with a loud warning**. The
dashboard imports that same function rather than reimplementing the rule, so the two cannot drift.

Per-run configuration is passed on the command line — the network path, the sample count, and JSON
evidence via `-ev`. See [running.md](running.md).

### Things that are hardcoded

Worth knowing before you assume a constant is configurable. `MapHPXML` hardcodes the Calgary weather
file, UTC−7 and DST for its output rows. `Sampler._parallel` sets the joblib worker count to
`max(os.cpu_count() - 8, 1)`, which is not exposed and behaves poorly on small machines — see
[known-issues.md](known-issues.md).
