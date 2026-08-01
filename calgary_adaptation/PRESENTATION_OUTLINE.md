# Estimating Calgary's Home Energy Use — Presentation Outline

*Plain-English, slide-by-slide. Audience: technical / analysts. Each slide has a
title, talking-point bullets, and speaker notes (intuition first, then the
mechanic). Numbers are pulled from `data/output/*.csv` and the two methodology
docs — all reproducible with fixed seeds.*

*Suggested length: ~19 slides + appendix, ~20–25 min.*

---

## Slide 1 — Title

**Title:** Estimating Calgary's Household Energy Use from Public Data

- A reproducible method built from two open datasets: EnerGuide home audits + the 2021 Census
- Output: an average energy-use intensity for Calgary — *with* a margin of error — and a neighbourhood map
- Everything seeded and scripted; no proprietary data

*Speaker notes:* Set expectations — this is a **method** talk, not just a result. The interesting part is how you get a trustworthy city-wide (and neighbourhood-level) number out of a dataset that was never designed to be representative. Three moving parts: correct the sample, quantify uncertainty, and go spatial.

---

## Slide 2 — The question

**Title:** What are we actually trying to measure?

- "What's the average energy-use intensity of a Calgary home?" — kWh per m² per year
- Two requirements: it must be **representative** of Calgary's stock, and it must come with a **credible uncertainty range**
- A single point estimate with no error bar is not decision-grade

*Speaker notes:* Emphasize the second requirement — anyone can compute an average. The hard, honest part is knowing how much to trust it. Energy-use *intensity* (per m²) rather than total, so we can compare a condo and a mansion on equal footing (we'll revisit why on slide 9).

---

## Slide 3 — Two ingredients, neither sufficient alone

**Title:** We have energy data, and we have population data — separately

- **EnerGuide**: measured/modelled energy for ~191k audited Alberta homes — but a *self-selected* sample
- **Census**: the true housing mix and dwelling counts for every area — but *no* energy numbers
- The whole method is a disciplined way to marry the two

*Speaker notes:* Frame it as a join problem with a twist. EnerGuide knows *energy but not representativeness*; the census knows *representativeness but not energy*. Neither answers the question alone. The census tells us what Calgary looks like; EnerGuide tells us what homes *like that* consume.

---

## Slide 4 — Ingredient 1: EnerGuide

**Title:** EnerGuide — rich energy data, biased sample

- NRCan's EnerGuide Rating System: home energy evaluations, 2004–2025, ~191k unique Alberta houses
- Per-home: fuel use, envelope, modelled intensity (MEUI), and more
- **But** households opt in — mostly retrofit-grant applicants and new-home labelling → a non-random slice

*Speaker notes:* This is administrative data, not a designed survey. People enter it by applying for a retrofit grant or labelling a new build. Both channels recruit a skewed population. That skew is the central problem — if we averaged EnerGuide naively, we'd describe grant applicants, not Calgary.

---

## Slide 5 — The bias, quantified

**Title:** How skewed? Very.

| Housing feature | EnerGuide sample | Calgary census |
|---|---|---|
| Single-detached | ~90% | ~55% |
| Apartments | ~0.06% | ~27% |
| Built ≥ 2020 | ~17% | ~2% |
| Tenure (own/rent) | not recorded | 71% owner |

- Naïve average ≈ "typical grant applicant / new build," not a typical Calgary home
- Apartments and renters are massively under-represented

*Speaker notes:* Walk one row — apartments are 27% of Calgary but essentially absent from EnerGuide (multi-unit buildings rarely do unit-level audits). Any distribution off the raw sample is wrong in a predictable direction. This table is the "why we can't just take the mean" slide.

---

## Slide 6 — Ingredient 2: Census

**Title:** The census gives us the ground truth mix

- 2021 Census: for Calgary (and each sub-area), the housing composition — **dwelling type × period of construction × tenure** — and total dwelling counts
- These are the *target* proportions the sample should match
- No energy data here — that's EnerGuide's job

*Speaker notes:* The census is our anchor to reality. It says "Calgary is 55% single-detached, 27% apartment, X% built before 1960…" We will force our biased sample to agree with these known proportions. The census also gives dwelling *counts*, which matter later when we aggregate neighbourhoods.

---

## Slide 7 — The core idea: "intersect"

**Title:** Reweight the sample so its mix matches Calgary

- Sort every audited home into census "cells" (its type × vintage × tenure)
- Give each home a **weight** so the weighted sample reproduces the census mix
- Over-represented homes get down-weighted; scarce ones (apartments, old homes) get up-weighted

*Speaker notes:* The marbles-in-a-jar analogy. Our jar has 90% blue marbles (detached) but the real jar is 55% blue. We can't add marbles, but we can say "each blue marble counts less, each rare red marble counts more," until the weighted mix matches reality. That reweighting is the heart of the method — statisticians call it post-stratification.

---

## Slide 8 — How the reweighting works: IPF raking

**Title:** Matching several dimensions at once (IPF)

- Census gives each dimension *separately* (a type breakdown, a vintage breakdown, a tenure breakdown) — not one joint table
- **Iterative Proportional Fitting**: nudge the weights to fix type, then vintage, then tenure; repeat until all match simultaneously
- Beats a simple per-type quota, which can only satisfy one dimension

*Speaker notes:* This is the one genuinely technical slide worth dwelling on for analysts. You can't just allocate "55 detached, 27 apartments" because that ignores vintage and tenure. IPF cycles through the margins, rescaling weights each pass, and converges to weights that honor *all* the marginals at once. We reused a single, tested `ipf_rake` implementation everywhere. Weights are capped (trimmed) so no single home dominates.

---

## Slide 9 — What we measure: MEUI

**Title:** Why per-m² intensity, not total energy

- **MEUI** = Modelled Energy Use Intensity, kWh/m²·yr — size-normalized
- Whole-building *total* double-counts apartments: one record = an entire block → weighting toward apartments inflated the total ~2×
- Trade-off: MEUI exists on ~44% of homes (newer ERS evaluations), so the profile leans recent

*Speaker notes:* A concrete trap we hit: when we tried total energy, reweighting toward apartments *doubled* the average — because an apartment "home" in EnerGuide is sometimes the whole building. Per-m² intensity sidesteps that and compares homes fairly. The cost is coverage — MEUI is only recorded on modern evaluations — which we flag as a limitation, not hide.

---

## Slide 10 — From one number to a range: the bootstrap

**Title:** Turning an estimate into an estimate ± uncertainty

- Resample the audited homes (with replacement) thousands of times; recompute the weighted average each time
- The spread of those thousands of averages **is** the 95% confidence interval
- Naïve "draw N and average" gives falsely tight intervals; we resample the real homes and recompute the *weighted* mean, so weight concentration widens the interval honestly
- Report **effective sample size** (Kish n_eff) so thin cells are visible

*Speaker notes:* Intuition: pretend we could re-run the whole audit campaign many times; how much would the answer wobble? The bootstrap simulates that by re-drawing from the homes we have. Key technical point for this audience: a weighted mean resting on a few heavily-weighted homes is *fragile*, and the correct bootstrap exposes that — the interval widens exactly where the effective sample is small (n_eff). We caught and fixed a version that hid this.

---

## Slide 11 — The load-bearing assumption

**Title:** The one assumption everything rests on

- "**Randomly distributed within a cell**": once we know a home's type & vintage, *which* specific audited homes we happened to see is as-good-as-random
- The weights fix *between-cell* imbalance; this assumption asserts no *within-cell* bias remains
- It's an assumption, not a fact — e.g. grant applicants may be worse-than-average homes of their type

*Speaker notes:* Be upfront: this is where the method could be wrong. We correct the fact that apartments are under-sampled, but we *assume* that the apartments we did see are typical apartments. If retrofit applicants systematically differ from their neighbours of the same type/vintage, a residual bias survives. Name it, so the room knows exactly what to challenge. (Inherited from the Hydro-Québec survey methodology this adapts.)

---

## Slide 12 — City-wide result

**Title:** Calgary's average: 146 kWh/m²·yr (95% CI 138–156)

- Point estimate **146.3**, 95% CI **138.1–156.1** (n = 34,207 homes, effective n ≈ 161)
- Strong **vintage gradient**: post-2020 homes ~81 vs oldest homes ~215–228 kWh/m²·yr — roughly a third of the intensity
- Building-code tightening, visible in the data

*Speaker notes:* The headline number. The interval width (~±9) reflects the honest effective sample size, not the raw 34k. The vintage story is the physical sanity check — newer homes use far less, near-monotonically, exactly as codes would predict. If someone doubts the whole method, the vintage gradient is the "it behaves like reality" evidence. *(Figure: 19_meui_bootstrap_distribution.png; 21_meui_by_vintage.png)*

---

## Slide 13 — Going spatial: the recipe

**Title:** Same idea, one census area at a time

- For each **forward sortation area (FSA** — the first 3 postal chars, e.g. T3M):
  1. take *its* housing composition + *its* dwelling count
  2. draw matching EnerGuide homes, average their MEUI
  3. bootstrap for a per-area interval
- Then **aggregate** the areas, weighted by how many dwellings each holds

*Speaker notes:* The user's "get a census area, find its mix, draw that many homes, average, repeat, aggregate." Instead of one city-wide mix, every neighbourhood uses its own. The FSA is the finest geography available — EnerGuide already carries it (in the postal field), 100% coverage. This turns a single number into a map plus a properly-weighted city total.

---

## Slide 14 — Hybrid draw: let neighbourhoods speak when they can

**Title:** From-area where we have data, borrow where we don't

- **From-area** (FSA has ≥100 audited homes): draw the FSA's *own* homes → captures real neighbourhood effects
- **Borrow** (sparse FSAs): draw the city pool, reweighted to that FSA's composition
- 34 of 36 FSAs are from-area; only 2 downtown FSAs borrow
- Assumption made explicit: borrowing assumes **energy ⊥ location | composition**

*Speaker notes:* Data is uneven — some FSAs have thousands of audits, a couple downtown have a handful. Where a neighbourhood is data-rich, we let its actual homes drive the estimate (this can capture built-form or behaviour that composition alone misses). Where it's data-poor, we fall back to "a home like this, anywhere in Calgary." The borrow assumption is stronger — we flag those two FSAs on the map.

---

## Slide 15 — Aggregating the areas

**Title:** Rolling neighbourhoods back into a city number

- Population-weighted: `M = Σ (dwellings_a × mean_a) / Σ dwellings_a`
- **Hybrid** aggregate **143.6** (CI 140.3–146.8) vs **borrow-only** **144.9** (CI 143.3–146.4)
- Borrow-only ≈ the city-wide 146.3 → the **sanity check passes**
- Hybrid − borrow = **−1.3** kWh/m²·yr: the "neighbourhood signal" beyond composition

*Speaker notes:* Two aggregates on purpose. Borrow-only *should* reproduce the city-wide method (it does — 144.9 vs 146.3, differing only by the deliberate simplifications), which validates the spatial machinery. The gap between hybrid and borrow-only isolates what letting real neighbourhoods speak actually adds: here a small −1.3, meaning composition already explains most of the variation — but not all.

---

## Slide 16 — The map

**Title:** Where Calgary uses more energy

- Choropleth of mean MEUI across 36 FSAs (507,840 dwellings ≈ 96.5% of Calgary)
- **Old inner city hot** (T2E ≈ 202), **new suburbs cool** (T3M/T3N/T3P ≈ 97) — nearly 2×
- Per-FSA MEUI correlates **0.73** with the share of pre-1980 dwellings
- Drawn in pure matplotlib (no GIS stack); dashed outlines = borrowed FSAs

*Speaker notes:* The payoff visual. The gradient is geographic now: the historic core (Bridgeland/Inglewood-era stock) glows red, the new fringe is pale. 0.73 correlation with neighbourhood age confirms the spatial signal is driven by building vintage, consistent with the city-wide gradient. Two FSAs are dashed — a visual reminder they rest on the stronger assumption. *(Figure: 24_calgary_meui_map.png; 23_fsa_meui_vs_vintage.png)*

---

## Slide 17 — What could have silently broken it

**Title:** The unglamorous 80%: data quality

- **The `_id` trap** — a per-file row number whose ranges overlap across files; de-duplicating on it would have silently deleted ~29k real records
- **The value-blending bug** — pandas `groupby.first()` pulls each column's first *non-null* independently, quietly mixing a post-retrofit home's fields into a pre-retrofit record — 17,868 homes affected until fixed
- **Geographic contamination** — `CLIENTCITY="Calgary"` includes mislabeled Edmonton (T6W) & rural FSAs; unfiltered, Edmonton's 30k dwellings would have distorted the aggregate weights

*Speaker notes:* For a technical room, this is the credibility slide. None of these throw errors — they produce plausible-but-wrong answers. Each was caught by profiling and sanity checks, not by the code crashing. The lesson: the statistics are the easy part; the defensible result comes from paranoid data hygiene. Great slide for Q&A.

---

## Slide 18 — Limitations

**Title:** What this does *not* claim

- **Coverage**: MEUI on ~44% of homes (newer evaluations) → profile leans toward recently-evaluated stock
- **Within-cell self-selection** (slide 11) is assumed away, not verified
- **Thin cells**: apartments, oldest vintages, and 2 downtown FSAs have wide/fragile intervals
- **Census granularity**: FSA census can't give fine joint type×vintage; tenure dropped in the spatial version
- **No weather/behaviour model** — this is measured/modelled audit intensity, not a simulation

*Speaker notes:* Say these before anyone asks. The honest framing: this is a well-calibrated estimate from imperfect open data, with every approximation logged. It's decision-grade for relative comparisons (which neighbourhoods, which vintages) and for a city average with a real error bar — not a per-building predictor.

---

## Slide 19 — Recap & pipeline

**Title:** Four reproducible stages

1. **Combine** — de-duplicate 20 years of EnerGuide into one clean dataset
2. **Weight** — IPF-rake the Calgary pool to census margins
3. **City profile** — bootstrap → 146.3 kWh/m²·yr (CI 138–156)
4. **Area profile + map** — per-FSA estimate, aggregate, choropleth

- All seeded & scripted; two methodology docs; five figures; two output CSVs
- Re-runnable end-to-end from public sources

*Speaker notes:* Leave them with the shape of the pipeline and the reassurance that it's fully reproducible — fixed seeds, documented sources, one command per stage. Point to the two methodology docs for anyone who wants the full derivation. Close on the dual deliverable: a defensible city number *and* an actionable neighbourhood map.

---

## Appendix (backup slides)

**A1 — Per-FSA table.** All 36 FSAs: `mean_MEUI`, 95% CI, local sample size, effective n, method (from-area/borrow). Source: `data/output/calgary_fsa_energy_profile.csv`.

**A2 — The math.**
- Weighted mean (the estimator): `M = Σ wᵢ yᵢ / Σ wᵢ`
- IPF: cycle each margin, rescale `w ← w × (target_share / current_share)` per category until convergence; trim weights above 500× mean and re-rake
- Bootstrap CI: resample homes with replacement K=5000×, recompute `M`, take the 2.5/97.5 percentiles
- Aggregate: `M_city = Σ (Nₐ · mₐ) / Σ Nₐ`, with N = census dwelling counts
- Effective sample size (Kish): `n_eff = (Σw)² / Σw²`

**A3 — Data sources & licences.**
- NRCan EnerGuide Rating System Open Data (Open Government Licence – Canada)
- StatCan 2021 Census Profile, Forward Sortation Areas — 98-401-X2021013 (StatCan Open Licence)
- StatCan 2021 FSA digital boundary file — lfsa000a21a (map geometry)

**A4 — "Calgary" definition.** FSAs with prefix T2/T3 plus T1Y = 36 areas, 507,840 dwellings (~96.5% of Calgary's ~526k occupied private dwellings); excludes mislabeled Edmonton/Airdrie/rural FSAs.

**A5 — Reproducing.**
```
python calgary_adaptation/fetch_data.py --only census
python calgary_adaptation/calibrate_stock.py
python calgary_adaptation/calibrate_stock.py
python calgary_adaptation/energy_profile.py
python calgary_adaptation/energy_profile.py
python calgary_adaptation/energy_profile.py
```
