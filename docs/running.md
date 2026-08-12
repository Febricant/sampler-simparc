# Running the pipeline

Every command assumes `uv sync` has been run at the repository root, and that you are in the
subdirectory named in the heading. See [install.md](install.md) for why the working directory matters.

## The short version

```bash
cd sampler
uv run python -m src.utils.sampler.Sampler \
    data/processed/bayesian_network/BN_Calgary.XDSL 100 ../out/sample.csv

cd ../simparc
uv run python main.py ../out/sample.csv --dry-run   # inspect, no simulation
uv run python main.py ../out/sample.csv             # simulate (needs OpenStudio)
```

Always `--dry-run` first on a new sample. It writes every `in.osw` and stops, so you see exactly what
OpenStudio would be given, in seconds, without Docker or Dask. A 100-building batch with an input
problem fails 100 times otherwise.

---

## Stage 1 — `sampler/`

### Draw a sample

```
uv run python -m src.utils.sampler.Sampler <bayesian_network.XDSL> <N> <output.csv> [-ev JSON]
```

| Argument | Meaning |
|---|---|
| `bayesian_network_filepath` | Path to the `.XDSL` network. Use `data/processed/bayesian_network/BN_Calgary.XDSL` for Calgary, `BN_EUEMr.XDSL` for the original Québec network. |
| `samples_number` | How many dwellings to generate. |
| `output_file` | Destination `.csv`. |
| `-ev`, `--evidence` | JSON dict of evidence to condition the draw on. |

Conditioning on evidence restricts the draw to a sub-population:

```bash
uv run python -m src.utils.sampler.Sampler \
    data/processed/bayesian_network/BN_Calgary.XDSL 500 ../out/detached.csv \
    -ev "{\"Type_Logement\": \"Maison individuelle\"}"
```

Evidence values must be **exact state labels from the network**. Because the re-calibration never
renames states, the same labels work against either network — states that are impossible in Alberta
simply carry probability zero.

Sampling runs across processes via joblib. The worker count is `max(os.cpu_count() - 8, 1)`, so on a
machine with 8 or fewer cores it silently drops to a single worker — see
[known-issues.md](known-issues.md).

### The dashboard

```bash
uv run streamlit run ui/Dashboard.py
```

A Streamlit app on port 8501 with two pages: an interactive sampler (set N and evidence with widgets,
preview and download the result) and a Bayesian-network explorer. It selects the default network by
importing the same helper the batch pipeline uses, rather than repeating the logic, so the two cannot
disagree about which network is current.

For D-Tale's interactive grid alongside it, launch with `uv run dtale-streamlit run ui/Dashboard.py`.

### The Calgary re-calibration pipeline

One driver with sub-commands:

```
uv run python calgary_adaptation/apply_to_sampler.py [targets|bn|cpt|batch|coverage|validate|docs|all]
```

| Step | Does |
|---|---|
| `targets` | Derive Calgary CPT targets from the audit data into `data/output/calgary_bn_targets.json` |
| `bn` | Rewrite the affected probabilities into `data/processed/bayesian_network/BN_Calgary.XDSL`. Non-destructive: the Québec network is never touched. |
| `cpt` | Reweight the ResStock-style detail tables, preserving their header grammar. Writes a one-time `.bak` per table. |
| `coverage` | Cheap pre-flight over the tables — fails in seconds rather than minutes into `batch` |
| `batch` | Run the sampler for 1,000 dwellings, producing `building-input.csv`, `building-mapping.csv`, `building-test.csv` and `building-input.provenance.json` |
| `validate` | **The default.** Two independent assertion groups — see below. |
| `docs` | Regenerate `calgary_adaptation/PROVENANCE.md` |
| `all` | `targets → bn → cpt → coverage → batch → validate → docs` |

`validate` is worth understanding, because it is candid about its own limits. Group (a) checks
*plumbing* — Calgary weather file, UTC−7, DST on, no `Bi-energie`. Those values are hardcoded in the
mapper and pass whichever network was used, so they prove nothing about the calibration. Group (b)
checks that the drawn heating-fuel and heating-system shares match the Calgary targets within
Monte-Carlo tolerance. **Only group (b) can tell a Calgary run from a Québec one.**

The sampler has no `pytest` suite; `validate` is the de-facto regression test.

### Supporting scripts

| Command | Purpose |
|---|---|
| `uv run python calgary_adaptation/fetch_data.py [--only energuide\|benchmarkyyc] [--years 2020-2025] [--force]` | Download the EnerGuide and BenchmarkYYC open data. **Needs network.** No API key required. |
| `uv run python calgary_adaptation/calibrate_stock.py [combine\|weights\|all]` | De-duplicate, map to network vocabulary, IPF-rake to census margins |
| `uv run python calgary_adaptation/energy_profile.py [all\|city\|area\|map\|describe]` | MEUI bootstrap, figures 01–25, FSA choropleth |
| `uv run python calgary_adaptation/weather_profile.py` | NSRDB grid to per-FSA degree days (offline) |
| `uv run python calgary_adaptation/compare_schema.py` | 97-column crosswalk between the Québec inputs and EnerGuide coverage |
| `uv run python calgary_adaptation/build_alberta_deck.py` / `make_presentation.py` | Rebuild the PowerPoint decks from the pipeline's own CSVs |
| `uv run python -m src.utils.hpxml.gen_hpxml_column_list [--samples 400] [--batches 5]` | Regenerate the exported column contract — see [data-contract.md](data-contract.md) |

Invoke these as `python calgary_adaptation/<script>.py`, **not** `python -m calgary_adaptation.<script>`.
Several use bare sibling imports (`from _shared import ...`) that only resolve the first way.

---

## Stage 2 — `simparc/`

```
uv run python main.py <buildings.csv> [--repair] [--dry-run] [--limit N] [--serial]
```

| Flag | Effect |
|---|---|
| *(none)* | Validate, preprocess, simulate through Dask, then post-process |
| `--dry-run` | Write every `in.osw` and stop. No OpenStudio, no Docker, no Dask. |
| `--repair` | Fix what validation finds instead of refusing, and write `<input>-repaired.csv` next to the input |
| `--limit N` | Only the first N buildings — for a quick trial of a large sample |
| `--serial` | One at a time instead of through Dask. Much slower, far easier to debug. |

SimParc **refuses to start** on an input OpenStudio would reject, printing the findings and exiting
non-zero. That check exists because two separate real runs reached OpenStudio with an apartment unit
on a conditioned basement — a pairing `BuildResidentialHPXML` rejects — and lost the batch. If the
findings are the known stale-export kind, `--repair` corrects them; otherwise regenerate the sample.

To check a CSV without running anything:

```bash
uv run python validate_sampler_csv.py buildings.csv [-o repaired.csv]
```

### Upgrade (retrofit) scenarios

`config.UPGRADE_SETTINGS` is `None` by default. Set it to model retrofits: each named set carries
filters selecting target buildings, an adoption rate, and the improvements to apply — wall
insulation, window U-value and SHGC, air leakage. Every matched building is **cloned**, so both the
baseline and the upgraded variant are simulated and the batch roughly doubles. A worked example is
commented out in `config.py`.

### Tests

```bash
uv run python -m pytest          # 34 fast tests, ~3 s, no Docker
uv run python -m pytest -m slow  # 2 tests, one real simulation via Docker, minutes
```

---

## Both stages together

`pipeline.py` at the repository root chains them, running each from its own directory:

```
python pipeline.py <count> [--simulate] [--evidence JSON] [--bn PATH]
                           [--out PATH] [--limit N] [--serial] [--repair]
python pipeline.py --csv out/sample.csv --simulate      # reuse an existing sample
```

It always dry-runs stage 2 before simulating, and stops there unless `--simulate` is given. Nothing
about it is required — it is a convenience over the two commands below, which remain the way to work
on either stage on its own.

```bash
cd sampler && uv run python -m src.utils.sampler.Sampler \
    data/processed/bayesian_network/BN_Calgary.XDSL 100 ../out/sample.csv
cd ../simparc && uv run python main.py ../out/sample.csv --dry-run
cd ../simparc && uv run python main.py ../out/sample.csv
```

Reading an input CSV from outside `simparc/` is fine — only the paths handed *to OpenStudio* must
live under the project directory, and those are all inside `results/`.

Before launching a real batch, size it: roughly **130–140 MB of output per building** at the default
settings. See [outputs.md](outputs.md) for how to reduce that.
