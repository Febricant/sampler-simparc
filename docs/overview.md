# Overview

## What this models

Utilities and energy planners need to answer questions like *"if 30% of Calgary's gas-heated
detached houses switched to heat pumps, what happens to the winter peak?"*. Answering it needs an
hour-by-hour energy model of every house in the city — but nobody has a measured model of every
house in the city.

The standard workaround, pioneered by NREL's **ResStock**, is to invent one. You take survey and
audit data describing how a region's housing stock is actually distributed — vintages, fuels,
envelope quality, appliances — and draw a synthetic population of some thousands of dwellings whose
*statistics* match the real stock even though no individual dwelling is real. Then you simulate each
synthetic dwelling properly, with a full building-physics engine, and add up the results.

This repository is both halves of that:

- **`sampler/` invents the population.** Given N, it emits N rows, each a complete set of
  OpenStudio-HPXML arguments describing one plausible dwelling.
- **`simparc/` simulates it.** Each row becomes an EnergyPlus run; the results are consolidated into
  parquet datasets.

## Where the probabilities come from

The sampler is a three-layer generator. Each layer narrows a dwelling from a demographic sketch to a
full building description.

1. **A Bayesian network** over ~40 dwelling and occupant variables — dwelling type, construction
   vintage, heating fuel and system, water heating, major appliances, pool/spa, electric vehicles,
   occupancy. It was learned offline from Hydro-Québec's **EUEMr 2022** survey (*Étude sur
   l'Utilisation de l'Énergie chez les Ménages résidentiels*), weighted by the survey's own sampling
   weights. Sampling it draws a coherent household: the network encodes that, say, electric baseboard
   heating and 1970s construction go together in Québec.

2. **~53 conditional probability tables** in ResStock's format, which add the ~52 technical
   attributes the survey never asked about — wall and ceiling R-values, window U-factor and SHGC,
   infiltration rate, HVAC efficiency, setpoints, PV. Each table is conditioned on what the network
   already drew, so a 1970s house gets 1970s insulation.

3. **A deterministic mapper** (`MapHPXML`, ~6,200 lines) that translates the resulting French survey
   and ResStock labels into the ~219 snake_case arguments the OS-HPXML `BuildResidentialHPXML`
   measure actually accepts.

Layers 1 and 2 are *probabilistic and regional* — they are what you replace to move to a new region.
Layer 3 is *mechanical* and largely region-independent.

## The Québec → Calgary migration

The project was built for Québec and is being re-targeted to **Calgary, Alberta**. That matters for
reading almost every file here, because the two regions are still visible side by side.

Québec's stock is overwhelmingly electrically heated; Alberta's is overwhelmingly gas. Re-calibration
therefore had to replace the probabilities without disturbing the structure. The approach taken in
`sampler/calgary_adaptation/`:

- Pull **NRCan EnerGuide** open microdata for Alberta (~351,000 evaluations → 191,621 unique houses →
  73,927 in Calgary) and Calgary's own BenchmarkYYC data.
- Rake that stock to the **2021 census** margins with iterative proportional fitting, so the sample
  matches known dwelling-type and vintage totals.
- Rewrite the affected probability cells into a **new network, `BN_Calgary.XDSL`** — the Québec
  original `BN_EUEMr.XDSL` is never modified.

**No node, state, or option label is ever renamed.** States that are impossible in Alberta (Québec's
`Bi-energie` dual-fuel tariff, for instance) get probability zero but stay in the network. This is
deliberate: the deterministic mapper in layer 3 and the downstream column contract both key off those
labels, so renaming would break the simulator.

`sampler/data/output/building-input.provenance.json` records which probability files produced a given
batch, so "was this Québec or Calgary?" is a lookup rather than an investigation.

## The two halves are one contract

The CSV between them is a **pinned column contract**, not an ad-hoc dump — the exporter reindexes
every run onto a generated column list so downstream code can rely on the header. Getting this wrong
has already caused real failures in both directions. See [data-contract.md](data-contract.md); it is
the most important technical document here.

## Vocabulary

| Term | Meaning |
|---|---|
| **LTE** | *Laboratoire des technologies de l'énergie* — Hydro-Québec's energy research lab. **Not** the telecom standard. |
| **IREQ** | *Institut de recherche d'Hydro-Québec*, the parent institute |
| **SimParc** | *Simulateur de parc (de bâtiments)* — "building-stock simulator" |
| **EUEMr** | *Étude sur l'Utilisation de l'Énergie chez les Ménages résidentiels* — the Québec household energy survey the Bayesian network was learned from |
| **BN** | Bayesian network. Stored as `.XDSL`, the GeNIe/SMILE format; read here with pyAgrum |
| **CPT** | Conditional probability table. Here, the `;`-separated ResStock-format CSVs with a `Dependency=…` / `Option=…` header grammar |
| **ResStock** | NREL's US residential building-stock model, whose sampling format this project borrows |
| **HPXML** | An XML schema for describing homes. **OS-HPXML** is NREL's OpenStudio workflow built on it |
| **OSW** | OpenStudio Workflow — the JSON "recipe" (`in.osw`) listing the measures to run for one building |
| **Measure** | An OpenStudio plugin (usually Ruby) that modifies a model. The four used here are vendored in `simparc/measures/` |
| **EPW** | EnergyPlus Weather file — one year of hourly weather for one location |
| **IPF** | Iterative proportional fitting, a.k.a. raking — reweighting a sample so its margins match known totals |
| **MEUI** | Modelled Energy Use Intensity, kWh/m²/yr |
| **ERS** | EnerGuide Rating System, NRCan's home energy rating |
| **FSA** | Forward Sortation Area — the first three characters of a Canadian postal code |

## Further reading inside the repo

The hand-written notes that predate this documentation set are still the deepest source on specific
topics, and are linked from the relevant pages here:

- `sampler/GENERATOR_REVERSE_ENGINEERING.md` — the fullest account of the generator and the BN nodes
- `sampler/CODEBASE_GUIDELINES.md` — repository architecture and file map
- `sampler/calgary_adaptation/PIPELINE.md` — runtime walkthrough with a flowchart
- `simparc/README.md` — the original bilingual FR/EN description
