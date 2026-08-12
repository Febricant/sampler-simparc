# The data contract

The sampler and the simulator exchange one CSV. Its header is a **pinned contract**, not whatever the
run happened to produce. This page explains why that was necessary, what the contract guarantees, and
how to change it safely.

If you read only one technical page here, read this one — every cross-stage failure so far has been a
violation of something on it.

## Why a pinned header

Two independent things made the header move between runs:

1. **`MapHPXML.doMapping` assigns some arguments only inside conditional branches.** Build a DataFrame
   from a list of per-building dicts and pandas takes the union of the keys that happened to appear.
   A batch with no heat pumps produces a narrower CSV than one with heat pumps.
2. **The Bayesian network's topological variable order differs between networks.** The
   sampler-attribute block therefore came out in a different *order* for `BN_Calgary` than for
   `BN_EUEMr`.

As the module docstring puts it: *downstream consumers (the SimParc runner) cannot be written against
a contract that moves.* So every export is reindexed onto generated lists before it is written.

## The shape

`sampler/src/utils/hpxml/hpxml_column_list.py` defines three lists:

| Name | Size | Contents |
|---|---|---|
| `ARGS_COLUMNS` | 97 | Human-readable sampler attributes — the French survey variables and ResStock labels. Carried through for traceability and filtering; SimParc treats them as metadata. |
| `HPXML_COLUMNS` | 219 | The snake_case OS-HPXML measure arguments. **These are what actually reach OpenStudio.** |
| `BOOLEAN_COLUMNS` | 23 | The subset of the above that OS-HPXML types as `Boolean`. |

`stabilize_export()` reindexes each block and concatenates them, giving a 316-column CSV with a fixed
header in a fixed order.

## The three rules

These are invariants, and each exists because breaking it caused a real failure.

### 1. Boolean columns pad with `"false"`, never blank

A missing Boolean is written as the string `"false"`. A blank would reach the runner's `astype(bool)`
and become **`True`** — pandas treats any non-empty object as truthy, and a blank cell read back is
not necessarily empty. Silently flipping a default to `True` across a batch is the kind of bug that
does not announce itself; it just shifts your results.

### 2. Integer columns are excluded unless every building supplies one

A padded, blank Integer column makes SimParc's `preprocess_data_types` raise `IntCastingNaNError` —
you cannot cast NaN to int. Rather than emit a column that breaks the consumer, the generator omits
any Integer argument that is not universally populated.

This is the clearest illustration of why these two projects belong in one repository: it is a rule in
the *producer*, written to satisfy an implementation detail of the *consumer*, with nothing able to
test the pair.

### 3. Unexpected columns warn, they do not disappear

`_reindex` keeps any column outside the contract rather than dropping it, and emits a warning naming
the offenders and the command to regenerate. Losing data silently is worse than carrying an
unexpected column.

## How the contract was generated

`gen_hpxml_column_list.py` does not hand-maintain the lists. It:

1. Scans `Mapping.py` for every schema argument name it mentions, in `measure.xml` schema order,
   minus six keys `doMapping` deletes just before returning.
2. Samples **every network shipped in the repository**, not just the current default, enough times to
   exercise the rare conditional branches. `BN_Calgary` reaches 211 arguments and `BN_EUEMr` 219, so
   pinning against only one would produce a contract that breaks the moment you switch networks.
3. Records which arguments can actually be emitted, and which are typed Boolean or Integer.

Regenerate it after any change to `Mapping.py` or the networks:

```bash
cd sampler
uv run python -m src.utils.hpxml.gen_hpxml_column_list [--samples 400] [--batches 5]
```

Commit the regenerated `hpxml_column_list.py` — it is a source file, not a build artefact.

## Changing the contract safely

Adding or removing an argument touches both stages. The order that works:

1. Change `Mapping.py` in the sampler.
2. Regenerate `hpxml_column_list.py` and check the diff — it tells you exactly what moved.
3. Confirm the argument exists in **SimParc's** `measures/BuildResidentialHPXML/measure.xml`, which is
   the schema SimParc validates against. The sampler's copy under `data/hpxml/` is currently identical,
   but nothing enforces that — if you re-vendor one, re-vendor both and check.
4. Run a small sample end to end with `--dry-run` and inspect a generated `in.osw`.
5. Add a fixture to `simparc/tests/` if the change has a failure mode worth pinning.

## When an export goes stale

An older CSV can carry defects that current code no longer produces. SimParc validates on the way in
rather than trusting the file, and knows about two kinds:

- **Renamed arguments.** `validation.RENAMES` maps `slab_perimeter_depth` →
  `slab_perimeter_insulation_depth` and `slab_under_width` → `slab_under_insulation_width`.
- **Combinations OS-HPXML rejects.** An apartment unit on a `ConditionedBasement` or
  `ConditionedCrawlspace`, which `BuildResidentialHPXML` refuses. Exports made before the mapper's
  `AboveApartment` branch was fixed still carry it.

`--repair` corrects both and writes `<input>-repaired.csv`. `simparc/tests/test_validation.py` and
`test_osw.py` are, in effect, the regression suite for sampler defects — which is the arrangement the
monorepo makes honest.

## Provenance

`sampler/data/output/building-input.provenance.json` records, for each batch, the SHA-256 of every
probability file that fed it plus the git commit. Given a CSV, you can determine whether it came from
the Québec or the Calgary probabilities without guessing from the contents.
