# Known issues and sharp edges

Things that will cost you time if you meet them without warning. Each entry says what happens, why,
and what to do.

## Sampling silently uses one core on small machines

`Sampler._parallel` sets the joblib worker count to `max(os.cpu_count() - 8, 1)`. The `- 8` is meant
to leave headroom on a large workstation, but on a machine with **8 or fewer cores it clamps to 1** —
sampling runs single-threaded with no message saying so.

If a sample is far slower than expected, check your core count first. The value is not exposed as a
setting; changing it means editing `sampler/src/utils/sampler/Sampler.py`.

## `python -m` fails for several `calgary_adaptation` scripts

`weather_profile.py`, `make_presentation.py` and others use bare sibling imports —
`from _shared import ...`, `from calibrate_stock import ...`. Those resolve when the script's own
directory is on `sys.path`, which happens when you run:

```bash
uv run python calgary_adaptation/weather_profile.py     # works
uv run python -m calgary_adaptation.weather_profile     # ModuleNotFoundError
```

Use the first form. `apply_to_sampler.py` is the exception — it inserts the project root on `sys.path`
itself and uses fully-qualified imports.

## The same parsing logic exists three times

Three implementations parse the OS-HPXML `measure.xml` into an argument schema, and they have
diverged:

| File | Lines | Emits |
|---|---|---|
| `sampler/src/utils/hpxml/ParseHPXMLinputs.py` | 99 | `HPXMLArg.py`, a generated class |
| `simparc/ParseHPXMLinputs/ParseHPXMLinputs.py` | 58 | `HPXMLinputs.csv` |
| `simparc/hpxml_input_schema.py` | 85 | `ARGS_CONSTRAINTS`, in memory at import |

A fix to one does not reach the others. Collapsing them into a shared module is the obvious cleanup
and has not been done.

**The schema file itself is *not* skewed.** All three copies of `measure.xml` in the tree
(`sampler/data/hpxml/`, `simparc/measures/BuildResidentialHPXML/`, `simparc/ParseHPXMLinputs/`) are
byte-identical once line endings are normalised. An earlier reading of this repository reported a
version difference between them; that was a CRLF-vs-LF artefact of how the two working trees had been
checked out, not a real divergence. Nothing enforces that they stay in step, though — if you
re-vendor one, re-vendor all three.

## Stale sampler exports carry defects current code does not produce

An older CSV can contain problems the sampler no longer generates. SimParc refuses to run on them
rather than failing inside OpenStudio:

- **Renamed arguments** — `slab_perimeter_depth` → `slab_perimeter_insulation_depth`,
  `slab_under_width` → `slab_under_insulation_width`.
- **An apartment unit on a conditioned basement or crawlspace**, which `BuildResidentialHPXML`
  rejects. The mapper's `AboveApartment` branch was never reached because the argument was empty;
  exports predating that fix still carry the combination.

Run with `--repair` to correct them and write `<input>-repaired.csv`, or regenerate the sample. Two
real batches were lost to the second one before validation was put on the path anything took.

## A missing weather file fails every building

`config.WEATHER_EPW_FILENAME` names a file that must exist in `simparc/weather/`. If it does not,
every simulation in the batch fails identically. The configured Calgary file
(`CAN_AB_Calgary.Intl.AP.718770_CWEC2016.epw`) is committed, so a fresh clone works — it was untracked
at one point, and that is exactly the failure it produced.

The other 48 committed `.epw` files are Québec locations from an earlier phase.

## Every building in a batch gets identical weather

`WEATHER_EPW_FILENAME` is a single file applied to the whole batch. There is no per-building weather
assignment. For a city-scale study this flattens genuine intra-urban variation.

`sampler/calgary_adaptation/weather_profile.py` quantifies that variation across Calgary's FSAs, and
states plainly that it holds **temperature only** and cannot synthesise a full EPW. Treat it as
analysis, not as simulation input.

## Output size surprises people

Roughly **130–140 MB per building** at default settings; 80 buildings is about 12 GB. Driven by
`TIMESERIES_FREQUENCY = "timestep"` and `DEBUG_MODE = True`. See [outputs.md](outputs.md) before a
large run, and use `--limit N` to measure before committing.

## Vendored NREL code carries local patches

`simparc/measures/` contains NREL's OpenStudio-HPXML measures, and at least one file has been modified
locally. Re-vendoring upstream would silently revert it. See [development.md](development.md).

## The pdoc3 API documentation is stale

`sampler/documentation/html/` and `.../markdown/` were last generated in November 2025. They document
four modules that no longer exist (`bn`, `Dashboard_v2`, `EUEMr`, `EUEMRArg`) and omit everything
added since — all of `calgary_adaptation/` and the three `src/utils/hpxml/` contract modules.

They are a docstring dump rather than prose; `Mapping.html` in particular is a 1.2 MB source listing.
Prefer the hand-written documentation. Regenerating is a chore nobody has done:

```bash
cd sampler
uv run python -m pdoc --html --output-dir documentation/html .
```

## Encoding matters on Windows

`Bn.yml` is opened with an explicit `encoding='utf-8'` because a cp1252 default turned accented French
state labels into mojibake, after which pyAgrum rejected them as evidence. Specify the encoding in any
new code that reads the network description files.

Some committed notebooks still contain mojibake in their stored source (`Ex�cution`,
`�chantillonnage`) from having been saved in a cp1252 session. Cosmetic, but confusing to read.

## Dead files

`sampler/utils/` and `sampler/dataStructure/` contain nothing but stale `__pycache__` — the real code
is under `sampler/src/utils/`. `sampler/calgary_adaptation/make_pichart.py` is a two-line stub.
`sampler/.vscode/settings.json` points at another developer's Linux path. None of these break
anything; they just mislead.

## Licensing is unresolved

The sampler has **no licence file**. SimParc has a custom bilingual FR/EN licence that is not a
standard SPDX one, and its code derives from `Archetype-QC/SimParc` plus NREL's OpenStudio-HPXML.

The CPTs under `sampler/data/processed/housing_characteristics/` and `BN_EUEMr.XDSL` are derived from
the EUEMr survey — Hydro-Québec proprietary data. The raw survey CSVs were deliberately removed from
the repository and are gitignored, but the derived tables are committed.

This repository is **private**, which is what makes that acceptable today. Resolve the licensing
before it becomes public.
