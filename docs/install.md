# Installation and runtime

## What you need

| | Required for | Notes |
|---|---|---|
| **Python 3.11** | everything | Both subprojects declare `requires-python = ">=3.11"` and pin `3.11` in `.python-version`. |
| **uv** | everything | The whole workspace resolves from one lock file. [Install instructions](https://docs.astral.sh/uv/getting-started/installation/). |
| **OpenStudio 3.9.0** | running simulations | Either a native SDK install or the Docker image. Not needed for `--dry-run`. |
| **Docker** | one of the OpenStudio options; the `slow` tests | Optional if you install the SDK natively. |
| **Graphviz** | rendering the network in the dashboard | Optional. The code degrades gracefully without it. |

There is **no hardware requirement** — no SDR, no serial devices, no GPU. What the pipeline consumes
is CPU cores and, above all, disk. Read [outputs.md](outputs.md) before a large run.

## Setting up the environment

From the repository root:

```bash
uv sync
```

That provisions **both** subprojects from the single root `uv.lock`. The root `pyproject.toml`
declares a uv workspace whose members are `sampler` and `simparc`; you do not sync them separately.

Run commands with `uv run` from inside the relevant subdirectory:

```bash
cd sampler  && uv run python -m src.utils.sampler.Sampler --help
cd simparc  && uv run python main.py --help
```

**Both tools must run from their own subdirectory.** This is not a style preference — `simparc/config.py`
computes its argument schema *at import time* from the relative path
`measures/BuildResidentialHPXML/measure.xml`, and several sampler modules resolve data files relative
to their own location. Importing either from the wrong working directory fails.

> If you find a `.venv/` inside `sampler/` or `simparc/` from an earlier setup, ignore it. Those are
> **Linux** virtualenvs built inside the dev container and are unusable from a Windows host. The
> workspace venv that `uv sync` creates at the repository root is the one that matters.

## Supplying OpenStudio

Everything past `--dry-run` needs the OpenStudio CLI, which bundles EnergyPlus. `simparc/osrunner.py`
abstracts over how it is invoked, selected by `OPENSTUDIO_RUNNER` in `simparc/config.py`:

| Setting | Behaviour |
|---|---|
| `"auto"` *(default)* | Use a native `openstudio` binary if one is on `PATH`, otherwise fall back to Docker. A native binary deliberately wins, so the dev container — which has `openstudio` on `PATH` but no Docker inside it — keeps working. |
| `"docker"` | Always shell out to `DOCKER_IMAGE` (default `simparc-dev:latest`), with the project bind-mounted at `/workspace`. Works from an ordinary Windows shell. |
| `"native"` | Always call an installed binary — `OPENSTUDIO_EXE` if set, else whatever is on `PATH`. |

The runner is resolved **once per batch**, from `main.py`, and actually executes `openstudio --version`.
A misconfiguration surfaces immediately instead of as N identical failures inside Dask workers.

### Option A — Dev container (most reproducible)

Install Docker and VS Code with the [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
extension, then open `simparc/` in the container. It builds from `nrel/openstudio:3.9.0`, so
OpenStudio is already present, and `postCreateCommand` runs `uv sync`.

### Option B — Docker without VS Code

**This is the path that is known to work on Windows**, and it needs no configuration change at all.
Build the image once:

```bash
cd simparc
docker build -t simparc-dev:latest -f .devcontainer/Dockerfile .devcontainer
```

The image is about **4.4 GB** — it is `nrel/openstudio:3.9.0` with Python, pip and uv layered on. The
build context above is `.devcontainer` rather than `.`, because the Dockerfile has no `COPY` step and
`simparc/` has no `.dockerignore`; using `.` uploads the weather files, the vendored measures and any
existing `results/` for nothing.

Leave `OPENSTUDIO_RUNNER` at its default `"auto"`. With no native `openstudio` on `PATH` it falls
through to Docker on its own. Confirm before running a batch:

```bash
uv run python -c "import osrunner; print(osrunner.resolve())"
# docker (auto-detected) image simparc-dev:latest, OpenStudio 3.9.0+c77fbb9569
```

Docker Desktop must actually be **running**, not merely installed — if the daemon is down, `docker`
commands fail with a named-pipe error and `resolve()` reports no runner.

Because the container only sees what is bind-mounted, **simulation inputs must live under the project
directory**. `osrunner.to_container_path()` raises `ValueError` for anything outside it rather than
silently handing OpenStudio a path it cannot resolve. Commands are built as argv lists and executed
without a shell, so a project path containing spaces needs no quoting.

### Option C — Native SDK

Install the [OpenStudio 3.9.0 SDK](https://github.com/NREL/OpenStudio/releases/tag/v3.9.0). If
`openstudio` lands on your `PATH`, the default `"auto"` picks it up with no configuration. Otherwise
set `OPENSTUDIO_EXE` in `config.py` (a relative path is resolved against the project root).

> Older instructions in `simparc/README.md` tell you to hand-edit a line number in
> `parallelization.py` and a path in `config.py`. That advice predates `osrunner.py` and no longer
> applies.

## Data that is not in git

A clone gives you everything needed to **sample and simulate**: the Bayesian networks, the
conditional probability tables, and the weather file are all committed. Two large directories are
deliberately not, because they are bulk source data rather than code:

| Directory | Size | Needed for |
|---|---|---|
| `sampler/data/input/alberta/{energuide,census,benchmarkyyc}` | 517 MB | Re-deriving the Calgary targets — `fetch_data.py`, `calibrate_stock.py`, `derive_targets.py`, `energy_profile.py` |
| `sampler/22e393a6216edb1d2f9c7f83062bd235/` | 100 MB | `weather_profile.py` only |

Without them you can still sample from `BN_Calgary.XDSL` and run the full pipeline. What you cannot
do is re-run the re-calibration from its raw sources.

To obtain them:

- **The Alberta data is re-fetchable.** `uv run python calgary_adaptation/fetch_data.py` pulls it from
  open.canada.ca and data.calgary.ca. No API key; it takes a while.
- **The NSRDB export is not.** The directory is named after an NREL request hash and was downloaded
  out of band. If you have a copy, keep it — treat re-obtaining it as a manual task, not a command.

Both are gitignored, so dropping them into place is all that is required.

## Verifying the installation

Fastest meaningful check, needing neither Docker nor OpenStudio:

```bash
cd simparc
uv run python main.py smoke-test.csv --dry-run   # writes 3 in.osw files
uv run python -m pytest                          # 34 fast tests
```

`pytest -m slow` adds two tests that run one building end-to-end through Docker. They **skip** rather
than fail when the image is missing, so read the result: "2 skipped" means Docker is not set up, not
that everything is fine. On a 12-core host with the image already built they take about 30 seconds.

To confirm the whole chain including post-processing and the parquet output:

```bash
uv run python main.py smoke-test.csv --limit 1 --serial
```

That writes `results/1/out.osw` with `completed_status: Success`, plus `results/metadata.parquet` and
`results/timeseries.parquet` (35,040 rows — a full year at the 15-minute timestep).

## Platform notes

The Python code is platform-agnostic — there is no `sys.platform` or `os.name` branching anywhere,
and paths go through `pathlib` / `os.path`. It is known to run on Windows, Linux and inside Docker.

One Windows-specific trap is already handled and worth knowing about: `Bn.yml` is opened with an
explicit `encoding='utf-8'` because a cp1252 default turned accented French state labels into
mojibake, after which pyAgrum rejected them as evidence. If you write new code that reads the network
description files, specify the encoding.

`pyagrum` ships compiled aGrUM bindings; `uv sync` installs a wheel and needs no compiler. Graphviz is
a separate system package, needed only for network visualisation in the dashboard.
