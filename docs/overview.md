# Overview

## What this models

Utilities and energy planners need to answer questions like *"if 30% of Calgary's gas-heated
detached houses switched to heat pumps, what happens to the winter peak?"*. Answering it needs an
hour-by-hour energy model of every house in the city — but nobody has a measured model of every
house in the city.

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

The project was built for Québec and is being re-targeted to **Calgary, Alberta**. 

- Pull **NRCan EnerGuide** open microdata for Alberta (~351,000 evaluations → 191,621 unique houses →
  73,927 in Calgary) and Calgary's own BenchmarkYYC data.
- Rake that stock to the **2021 census** margins with iterative proportional fitting, so the sample
  matches known dwelling-type and vintage totals.
- Rewrite the affected probability cells into a **new network, `BN_Calgary.XDSL`** — the Québec
  original `BN_EUEMr.XDSL` is never modified.

**No node, state, or option label is ever renamed.** States that are impossible in Alberta (Québec's
`Bi-energie` dual-fuel tariff) get probability zero but stay in the network. This is
deliberate: the deterministic mapper in layer 3 and the downstream column contract both key off those
labels, so renaming would break the simulator.
