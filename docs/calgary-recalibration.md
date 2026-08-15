# The Calgary re-calibration

The pipeline was built for Québec and is being re-targeted to Calgary, Alberta. This page is a map of
that work; the detailed methodology lives in notes written alongside the code, linked below.

## The problem

Québec's housing stock is overwhelmingly **electrically heated**. Alberta's is overwhelmingly
**gas heated**. A Bayesian network learned from a Québec survey encodes that association everywhere —
not just in the heating-fuel node, but in everything correlated with it.

So the probabilities had to change while the structure stayed put. The constraint that shaped the
whole approach:

> **No node, state, or option label is ever renamed.** States impossible in Alberta — Québec's
> `Bi-energie` dual-fuel tariff, for instance — receive probability zero but remain in the network.

That is not tidiness. The deterministic HPXML mapper and the downstream column contract both key off
those exact labels, so a rename propagates into the simulator and breaks it. Changing only the numbers
keeps every consumer working.

The Québec network `BN_EUEMr.XDSL` is **never modified**. Calibration writes a new
`BN_Calgary.XDSL` beside it.

## Where the numbers come from

| Source | Used for |
|---|---|
| **NRCan EnerGuide** open microdata for Alberta | The primary stock description: vintage, dwelling type, envelope, airtightness, heating and water-heating systems, ERS ratings |
| **2021 Census** (profile + FSA boundaries) | Margins to rake against, so the sample matches known dwelling-type and vintage totals |
| **BenchmarkYYC** (City of Calgary) | Supplementary Calgary building data |
| **NSRDB** | Per-neighbourhood weather and degree days |

EnerGuide narrows from about 351,000 Alberta evaluations to 191,621 unique houses (one row per
`HOUSEID`, preferring the most informative evaluation type) to 73,927 in Calgary.

All sources are open data under the Open Government Licence; none needs an API key. Provenance and
licence terms are logged in `sampler/data/input/alberta/SOURCES.md`.

## The five branches

`sampler/calgary_adaptation/` runs as five independent branches that meet at the join step. The
runtime walkthrough with a flowchart is in
[`sampler/calgary_adaptation/PIPELINE.md`](../sampler/calgary_adaptation/PIPELINE.md).

| Branch | Script | Produces |
|---|---|---|
| 1 — acquire | `fetch_data.py` | Raw EnerGuide and BenchmarkYYC data under `data/input/alberta/` |
| 2 — calibrate | `calibrate_stock.py` | De-duplicated stock, mapped into the network's vocabulary, IPF-raked to census margins → `alberta_stock_mapped.parquet` |
| 3 — energy profile | `energy_profile.py` | Calgary MEUI (~146 kWh/m²/yr) with a post-stratified weighted bootstrap CI, figures 01–25, FSA choropleth |
| 4 — weather | `weather_profile.py` | Per-FSA degree days from the NSRDB grid, by point-in-polygon |
| 5 — schema | `compare_schema.py` | A 97-column crosswalk classifying each Québec input as direct / imputed / keep-qc / resstock / derived / set-calgary |

Then the join, all through `apply_to_sampler.py`:

```
derive_targets.py   → calgary_bn_targets.json     (target CPT cells + support counts)
apply_to_sampler.py bn   → BN_Calgary.XDSL        (rewrite the affected probabilities)
                    cpt  → reweighted CPT tables  (grammar-preserving; one-time .bak)
                    batch → 1,000 dwellings + provenance
                    validate → assertions
                    docs → PROVENANCE.md
```

Branch 2's mapper **fails loudly on an unmapped EnerGuide category** rather than silently bucketing
it, so a vocabulary drift in the source data surfaces as an error instead of a quiet distortion.

Branch 4 is worth a caveat it states about itself: it carries **temperature only** and cannot
synthesise a full EPW. Simulations still use the single Calgary weather file. The per-FSA profile is
analysis, not simulation input.

## Checking that it worked

`apply_to_sampler.py validate` runs two independent groups, and the distinction is the important part:

- **(a) Plumbing** — Calgary weather file, UTC−7, DST on, zero `Bi-energie`. These are hardcoded in
  `Mapping.py` and pass regardless of which network produced the sample. They **prove nothing about
  the calibration**.
- **(b) Calibration** — the drawn heating-fuel and heating-system shares match the Calgary targets
  within Monte-Carlo tolerance, and the fuel propagated correctly into the HPXML arguments.

Only group (b) distinguishes a Calgary run from a Québec one. If you are verifying the
re-calibration, that is the group to read.

## Reproducing it

```bash
cd sampler
uv run python calgary_adaptation/fetch_data.py        # needs network; downloads a lot
uv run python calgary_adaptation/apply_to_sampler.py all
```

`all` chains `targets → bn → cpt → coverage → batch → validate → docs`. `batch` is the slow step.
`coverage` runs first as a cheap pre-flight so a table problem fails in seconds rather than minutes
into the batch.

The downloaded data is large — roughly 517 MB, gitignored — and is re-fetchable rather than vendored.

## Detailed methodology

Written alongside the code, and more specific than this page:

| Note | Covers |
|---|---|
| [`PIPELINE.md`](../sampler/calgary_adaptation/PIPELINE.md) | Runtime walkthrough of all five branches, with a flowchart |
| [`PHASE2B_METHODOLOGY.md`](../sampler/calgary_adaptation/PHASE2B_METHODOLOGY.md) | Why IPF raking, and against which margins |
| [`ENERGY_PROFILE_METHODOLOGY.md`](../sampler/calgary_adaptation/ENERGY_PROFILE_METHODOLOGY.md) | The weighted bootstrap behind the MEUI estimate |
| [`AREA_ENERGY_PROFILE_METHODOLOGY.md`](../sampler/calgary_adaptation/AREA_ENERGY_PROFILE_METHODOLOGY.md) | The per-FSA variant |
| [`PROVENANCE.md`](../sampler/calgary_adaptation/PROVENANCE.md) | **Auto-generated.** Per node: Calgary, Québec, or structural; source; support counts. Regenerate with `apply_to_sampler.py docs`. |
| [`SOURCES.md`](../sampler/data/input/alberta/SOURCES.md) | Data provenance and licence terms |
| [`GENERATOR_REVERSE_ENGINEERING.md`](../sampler/GENERATOR_REVERSE_ENGINEERING.md) | The generator itself, including an assessment of what was portable to Alberta |

`sampler/ALBERTA_RECALIBRATION_PLAN.md` is the original plan. It is **historical** — it carries its
own banner noting that its script names predate a later cleanup, and several have since been merged
into `apply_to_sampler.py`. Read it for intent, not for commands.
