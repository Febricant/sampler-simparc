# Installation and runtime

## What you need

| | Required for | Notes |
|---|---|---|
| **Python 3.11** | everything | Both subprojects declare `requires-python = ">=3.11"` and pin `3.11` in `.python-version`. |
| **uv** | everything | The whole workspace resolves from one lock file. [Install instructions](https://docs.astral.sh/uv/getting-started/installation/). |
| **OpenStudio 3.9.0** | running simulations | Either a native SDK install or the Docker image. Not needed for `--dry-run`. |
| **Docker** | one of the OpenStudio options; the `slow` tests | Optional if you install the SDK natively. |
| **Graphviz** | rendering the network in the dashboard | Optional. The code degrades gracefully without it. |


## Setting up the environment

From the repository root:

```bash
uv sync
```


Run commands with `uv run` from inside the relevant subdirectory:

```bash
cd sampler  && uv run python -m src.utils.sampler.Sampler --help
cd simparc  && uv run python main.py --help
```

> If you find a `.venv/` inside `sampler/` or `simparc/` from an earlier setup, ignore it. Those are
> **Linux** virtualenvs built inside the dev container and are unusable from a Windows host. The
> workspace venv that `uv sync` creates at the repository root is the one that matters.

## Supplying OpenStudio

### Dev container
Install Docker and VS Code with the [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
extension, then open `simparc/` in the container. It builds from `nrel/openstudio:3.9.0`, so
OpenStudio is already present, and `postCreateCommand` runs `uv sync`.

## Data that is not in git

| Directory | Size | Needed for |
|---|---|---|
| `sampler/data/input/alberta/{energuide,census,benchmarkyyc}` | 517 MB | Re-deriving the Calgary targets — `fetch_data.py`, `calibrate_stock.py`, `derive_targets.py`, `energy_profile.py` |
| `sampler/22e393a6216edb1d2f9c7f83062bd235/` | 100 MB | `weather_profile.py` only |

Without them you can still sample from `BN_Calgary.XDSL` and run the program. What you cannot
do is re-run the re-calibration from its raw data.

To obtain them:

- **The Alberta data is re-fetchable.** `uv run python calgary_adaptation/fetch_data.py` pulls it from
  open.canada.ca and data.calgary.ca. No API key; it takes a while.
- **The NSRDB export is not.** The directory is named after an NREL request hash and was downloaded
  out of band. If you have a copy, keep it — treat re-obtaining it as a manual task, not a command.

Both are gitignored, so dropping them into place is all that is required.

## Verifying the installation

```bash
cd simparc
uv run python main.py smoke-test.csv --dry-run   # writes 3 in.osw files
uv run python -m pytest                          # 34 fast tests
```

To confirm the whole runtime including post-processing and the parquet output:

```bash
uv run python main.py smoke-test.csv --limit 1 --serial
```

That writes `results/1/out.osw` with `completed_status: Success`, plus `results/metadata.parquet` and
`results/timeseries.parquet` (35,040 rows — a full year at the 15-minute timestep).