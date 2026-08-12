# Development

## Tests

SimParc has a pytest suite; the sampler does not.

```bash
cd simparc
uv run python -m pytest          # 34 tests, ~3 s, no Docker or Dask
uv run python -m pytest -m slow  # 2 more: one building end-to-end via Docker, minutes
```

`pytest.ini` deselects `slow` by default, so the fast suite is what you get unqualified.

| File | Covers |
|---|---|
| `tests/test_osrunner.py` | Runner selection and path translation into the container |
| `tests/test_osw.py` | The generated `in.osw` — that no path escapes the mount, that HPXML paths agree across steps, that no building reaches OpenStudio in a rejected state |
| `tests/test_validation.py` | Detection and repair of stale-export defects |
| `tests/test_smoke_docker.py` | A real simulation. Marked `slow`. |

Fixtures in `tests/fixtures/` are small CSVs: a clean sample, a stale export carrying the known
defects, and one with a blank required Choice value.

Worth being explicit about what this suite is: **`test_validation.py` and `test_osw.py` are the
regression suite for defects in the sampler.** They live in the consumer because that is where the
symptom appeared. Keeping both projects in one repository is what makes that arrangement honest
rather than accidental — a fix in `sampler/src/utils/sampler/Mapping.py` can now be verified by tests
in `simparc/tests/` in a single change.

The sampler's equivalent is `apply_to_sampler.py validate`, which asserts that a drawn sample matches
the Calgary targets. See [running.md](running.md) for what it does and does not prove.

## Local patches to vendored NREL code

`simparc/measures/` vendors NREL's OpenStudio-HPXML measures. **At least one file is patched locally.
Re-vendoring from upstream would silently revert it, and the symptom would be a physics change, not a
crash.**

`measures/HPXMLtoOpenStudio/resources/hvac.rb`, ground-source heat pumps:

1. **Line ~842** — re-set the plant loop fluid type after creating the vertical ground heat exchanger:

   ```ruby
   plant_loop.setFluidType(hp_ap.fluid_type) # GroundHeatExchangerVertical.addToNode() resets the loop fluid type to Water
   ```

   `addToNode()` resets the loop to Water as a side effect, discarding the glycol mixture set earlier.

2. **Line ~5056** — raise the glycol fraction from 0.2 to 0.3:

   ```ruby
   hp_ap.frac_glycol = 0.3 # E+ built-in property data for 20% glycol only covers 0-125C;
                           # 30% extends below 0C, needed when the ground loop dips below
                           # freezing in cold climates
   ```

   This is a Calgary requirement specifically: EnergyPlus's built-in property data for 20% propylene
   glycol starts at 0 °C, and the Calgary ground loop goes below that.

Before updating any vendored measure, diff the current tree against the upstream release and carry
these forward. If you add another patch, add it here.

## Regenerating generated files

Several files are generated and committed. They are source, not build artefacts — commit the
regenerated version.

| File | Regenerate with | When |
|---|---|---|
| `sampler/src/utils/hpxml/hpxml_column_list.py` | `uv run python -m src.utils.hpxml.gen_hpxml_column_list` | After changing `Mapping.py` or the networks |
| `sampler/src/utils/hpxml/HPXMLArg.py` | `uv run python src/utils/hpxml/ParseHPXMLinputs.py` | After re-vendoring `measure.xml` |
| `sampler/calgary_adaptation/PROVENANCE.md` | `uv run python calgary_adaptation/apply_to_sampler.py docs` | After `bn` or `cpt` |
| `sampler/data/processed/bayesian_network/BN_Calgary.XDSL` | `uv run python calgary_adaptation/apply_to_sampler.py bn` | After changing targets |

The pdoc3 output under `sampler/documentation/` is also generated, and is currently stale — see
[known-issues.md](known-issues.md).

## Repository layout and history

Both projects were imported with `git subtree`, so their full histories are present under their
original paths. `git log` shows commits from both, with original authorship preserved — SimParc's six
upstream commits are attributed to their author.

```
sampler/     LTE-Sampler-Residential
simparc/     SimParc
docs/        this documentation
out/         scratch output from the combined pipeline (gitignored)
```

`simparc/` keeps its own bilingual FR/EN `README.md` and its `LICENSE-EN.txt` / `LICENSE-FR.txt`,
since the code derives from the upstream project and attribution belongs with the subfolder.

### Remotes

`upstream-simparc` points at `https://github.com/Archetype-QC/SimParc.git` for re-vendoring upstream
changes. **Its push URL is deliberately disabled** — fetch from it, never push to it.

### The uv workspace

The root `pyproject.toml` declares `sampler` and `simparc` as workspace members, so one `uv sync` at
the root provisions both from a single `uv.lock`. Add dependencies to the subproject that needs them,
not to the root, then re-run `uv lock`.

`simparc` is marked `package = false`: it has no `[build-system]` and runs as loose scripts importing
each other by bare module name.

## Things to know before changing code

- **Working directory is load-bearing.** `simparc/config.py` parses `measure.xml` via a relative path
  at import time. Both projects must run from their own subdirectory.
- **Paths handed to OpenStudio must stay inside the project.** `osrunner.to_container_path()` raises
  otherwise, because the container cannot see them. Input CSVs read by pandas are exempt.
- **Never rename a Bayesian network node, state, or option label.** The deterministic mapper and the
  column contract key off those exact strings. Re-calibration changes probabilities only.
- **Specify `encoding='utf-8'` when reading network description files.** A cp1252 default corrupts
  accented state labels and pyAgrum then rejects them as evidence.
- **Regenerate the column contract after touching `Mapping.py`**, and read the diff. See
  [data-contract.md](data-contract.md).

## Suggested cleanups

Not done, in rough order of value:

1. Collapse the three `measure.xml` parsers into one shared module — see
   [known-issues.md](known-issues.md).
2. Give the sampler a pytest suite. `stabilize_export` and the CPT sampling are pure functions and
   easy to test.
3. Make the joblib worker count configurable instead of `os.cpu_count() - 8`.
4. Regenerate or delete the stale pdoc3 output.
5. Remove the dead `sampler/utils/`, `sampler/dataStructure/` and `make_pichart.py`.
6. Resolve licensing before the repository could ever be public.
