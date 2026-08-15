# sampler-simparc

A two-stage pipeline for **residential building-stock energy modelling**. Stage one invents a
population of plausible dwellings; stage two simulates the annual energy use of every one of them.

```
                sampler/                                    simparc/
  ┌──────────────────────────────────┐      ┌────────────────────────────────────┐
  │  Bayesian network  (.XDSL)       │      │  validate + type against the       │
  │  + ~53 conditional prob. tables  │      │  OS-HPXML measure schema           │
  │  + deterministic HPXML mapper    │      │  → one in.osw per dwelling         │
  │                                  │ CSV  │  → OpenStudio-HPXML / EnergyPlus   │
  │  N synthetic dwellings,          ├─────►│  → Dask fan-out                    │
  │  ~219 OS-HPXML arguments each    │      │  → metadata + timeseries parquet   │
  └──────────────────────────────────┘      └────────────────────────────────────┘
      LTE-Sampler-Residential                    SimParc (Simulateur de parc)
```

The two halves used to live in separate repositories and drifted apart — the CSV they exchange is a
pinned contract with no shared test, and the schema file that defines it existed in two different
versions. They are one repository now.

> **"LTE" is not the telecom standard.** It stands for *Laboratoire des technologies de l'énergie*,
> Hydro-Québec's energy-technology research lab (IREQ). There is no radio hardware anywhere in this
> project.

## Quickstart

```bash
uv sync                       # provisions both subprojects from one lock file
python pipeline.py 10         # sample 10 dwellings, then check them
python pipeline.py 10 --simulate    # ... and actually simulate them
```

`pipeline.py` runs both stages in order. Without `--simulate` it stops after a dry run, which writes
every OpenStudio input file but runs nothing — that needs neither Docker nor OpenStudio, so it is the
fastest way to confirm a working checkout. A real simulation needs OpenStudio 3.9.0; see
[docs/install.md](docs/install.md).

The stages also run independently, which is what you want while working on either one:

```bash
cd sampler
uv run python -m src.utils.sampler.Sampler \
    data/processed/bayesian_network/BN_Calgary.XDSL 10 ../out/sample.csv

cd ../simparc
uv run python main.py ../out/sample.csv --dry-run
```

## Documentation

| Document | Read it for |
|---|---|
| [docs/overview.md](docs/overview.md) | What this models, why, and the vocabulary. **Start here.** |
| [docs/install.md](docs/install.md) | Runtime requirements and the three ways to supply OpenStudio |
| [docs/running.md](docs/running.md) | Every command, with arguments |
| [docs/architecture.md](docs/architecture.md) | Module map and data flow through both stages |

## Repository layout

```
sampler/     LTE-Sampler-Residential — the dwelling generator (Python 3.11, pyAgrum, Streamlit)
simparc/     SimParc — the simulator (Python 3.11, Dask, OpenStudio-HPXML)
docs/        documentation for both
```

Both subtrees keep their original commit history. `simparc/` additionally carries its own bilingual
FR/EN `README.md` and licence files from the upstream `Archetype-QC/SimParc` project; those are
preserved as-is.

## Status

Actively under development, and the numbers it produces are not validated for any external use. The
liability disclaimer in [simparc/README.md](simparc/README.md) applies to the whole repository.
