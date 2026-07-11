# Phase 2b Methodology — Correcting Selection Bias in the EnerGuide Sample via Iterative Proportional Fitting

*Technical companion to `calgary_adaptation/build_alberta_weights.py` (commit `f24f2a5`).
Prepared for review; academic audience.*

---

## 1. The Problem: Two Distinct Flaws

### 1.1 The data flaw — non-probability sampling

The NRCan EnerGuide Rating System dataset (191,618 unique Alberta houses after
de-duplication) is administrative, not a designed survey. Households enter it by
self-selection through two channels — retrofit-grant applications (e.g. Canada
Greener Homes) and voluntary new-home labelling — and each channel recruits a
non-representative slice of the stock:

| Margin | EnerGuide sample | Calgary 2021 census | Distortion |
|---|---|---|---|
| Single-detached | 90.3 % (existing cohort) | ~55 % | grant programs target owners of detached homes |
| Apartments (`Collective`) | 0.06 % | ~27 % | MURBs rarely pursue unit-level evaluations |
| Built ≥ 2020 | 16.9 % | ~2.4 % | new-home labelling floods recent vintages |
| Tenure | **not recorded at all** | 70.9 % owner | structurally missing variable |

Left uncorrected, any distribution computed from this sample would describe
*grant applicants and new-home builders*, not Calgary's housing stock.

### 1.2 The codebase flaw — direct post-stratification cannot survive sparsity

The inherited Hydro-Québec pipeline corrects its survey with `Create_Pond`
(`src/utils/euemr/Mapping.py:723`): a **direct post-stratification** that
computes, for every *joint* cell of Vintage × Territoire × Typology × Fuel,

```
PONDNew(cell) = target_share(cell) / sample_share(cell)
```

This is mathematically sound *only when every joint cell with target mass also
has sample mass*. That held for EUEMr — a designed, professionally weighted
probability survey needing modest correction. It fails structurally on our
data: with 218 apartment records spread across 9 vintage bins × 2 tenure
states, most apartment joint cells (e.g. "1950s renter-occupied apartment")
contain **zero** sample records while carrying non-zero census mass. The ratio
is then division by zero; near-empty cells produce unbounded weights. The
method, not the implementation, is what breaks.

---

## 2. The Solution: Iterative Proportional Fitting (Raking)

### 2.1 What changed mathematically

IPF replaces the joint-cell requirement with a far weaker one. Rather than
matching the full contingency table in one shot, it cycles through the margins
— `Type_Logement`, `An_Construction`, `Mode_Occupation` — and applies the same
target/sample ratio idea *one margin at a time*:

```
for each margin m:
    w_i  ←  w_i · target_share_m(c_i) / current_weighted_share_m(c_i)
```

repeating until every margin agrees with its target (convergence criterion:
max absolute deviation < 10⁻⁷). This is the classical Deming–Stephan raking
procedure; its fixed point is the weight set that satisfies all marginal
constraints while staying minimally divergent (in the Kullback–Leibler sense)
from the starting weights — i.e. the *least-informative* correction consistent
with the census.

**Why this fixes the divide-by-zero:** IPF only ever divides by the current
weighted share of a *marginal category*. A margin category is empty only if the
sample contains no records of that category at all — support is needed per
category (218 apartments suffice), not per joint cell (1950s renter apartments
may be empty). The joint structure inside the constraints is inherited from the
observed data rather than demanded from a target file.

**Residual edge case, handled explicitly:** if a target category truly has zero
sample support, no weighting scheme can populate it. The implementation drops
such categories from the margin, renormalizes, and prints the abandoned census
mass — a loud, quantified admission instead of a crash or a silent NaN. (Not
triggered on the current pull; every category has support.)

### 2.2 Outcome

All three margins converge to |error| ≈ 10⁻⁹: detached corrected 84.1 % → 55.2 %,
apartments 0.1 % → 27.1 %, ≥ 2020 vintage 16.9 % → 2.4 %, tenure pinned at
70.9/29.1. Weights are normalized to mean 1 and stored as `POND_AB`,
mirroring the role of `POND1`/`PONDNew` in the Québec pipeline so downstream
CPT construction consumes them identically.

---

## 3. Architectural Considerations

### 3.1 Weight trimming with re-raking — bounding single-record influence

*The risk being managed:* raking a category that is 0.1 % of the sample up to
27.1 % of the population multiplies those records' weights by ≈ 260× on
average; records that are simultaneously rare on several margins compound
multiplicatively. Untrimmed, a handful of rows would dominate every weighted
statistic — the estimator's variance explodes even though its margins are
exact. This is the textbook bias–variance trade-off of survey calibration.

*The mechanism:* after convergence, weights above **500× the mean** are capped,
then the IPF is **re-run on the capped weights** (up to 10 trim-and-re-rake
rounds). Re-raking matters: a naive cap would silently break the margins;
re-raking redistributes the trimmed mass across the remaining records of the
same categories, restoring the constraints.

*Why 500×:* the cap must sit above the ≈ 260× systematic factor the apartment
margin legitimately requires (a tighter, conventional cap of 10–50× would make
the 27 % apartment target unreachable) yet low enough to stop compounding
outliers. On the current data, 42 records rest at the cap and the margins still
close to ~10⁻⁹ — the cap cost essentially nothing while bounding worst-case
influence.

*Engineering posture:* the trade is surfaced, not hidden — the run reports how
many rows sit at the cap and the residual margin error, so the trimming's cost
is measured on every build.

### 3.2 Imputed tenure — a synthetic margin, declared as such

`Mode_Occupation` is both a Bayesian-network node and a census raking
dimension, but EnerGuide records no tenure. Three options existed:

- **Drop the margin** — leaves every tenure-conditioned CPT downstream with no
  weighting basis; rejected.
- **Assign tenure marginally at random (70.9/29.1)** — destroys the strong
  real-world tenure × dwelling-type association (87 % of detached homes are
  owner-occupied vs 38 % of apartments); rejected.
- **Impute conditionally on dwelling type** from census owner-shares
  P(owner | type), then let IPF pin the marginal exactly — **chosen**.

The statistical justification: the imputation injects *census* structure, not
fabricated EnerGuide signal. The resulting column reproduces the census joint
distribution of tenure × type by construction, which is precisely the object
the raking constraints need to be mutually coherent (raking three margins whose
sample joint structure contradicts the targets converges slowly or
oscillates). A fixed RNG seed makes every build byte-reproducible.

The essential caveat is honesty of provenance, and it is written into the code:
`Mode_Occupation` carries **zero observational content from EnerGuide**. It is
valid as a weighting dimension and as BN conditioning structure inherited from
census; it must never be analyzed as observed Alberta tenure data.

### 3.3 Diagnostics as first-class outputs

Every run prints the convergence proof (target vs achieved vs unweighted, per
margin) and **Kish effective sample sizes**, n_eff = (Σw)²/Σw², overall and per
dwelling type. Current values: overall n_eff = 1,883 (1.0 % of the nominal
191,618), n_eff[Collective] = 140, n_eff[Triplex] = 58. This follows the
codebase's established fail-loudly philosophy (cf. the KeyError-on-unknown-state
convention in `make_calgary_bn.py`): the cost of the correction is quantified
on every execution, so nobody can mistake margin-perfect output for
information-rich output. The design effect n/n_eff directly scales the
uncertainty that Phase 6's Dirichlet resampling will attach to each CPT row.

---

## 4. The Remaining Risk: The Electric-Apartment Blindspot

### 4.1 Why it occurs mathematically

Raking corrects **composition across the constrained margins**; it cannot
correct **within-category distributions of unconstrained variables**. The
weighted conditional for heating fuel among apartments is

```
P̂(fuel = electric | Collective) = Σ_{i ∈ Collective} w_i · 1[fuel_i = electric] / Σ_{i ∈ Collective} w_i
```

— a weighted average over the *observed* 218 apartment records. If (as here)
essentially every sampled apartment is gas-heated, the numerator is ~0 for
electricity **regardless of the weights**: reweighting rescales existing
records; it cannot conjure support the sample never contained. Hence the raked
table still reports ≈ 99 % gas overall, and apartments specifically remain
gas-heated in defiance of Calgary's sizable electric-baseboard MURB stock.

### 4.2 Why raking's assumptions are violated here

Post-stratification removes selection bias only under a *missing-at-random*
condition: within each raking cell, participants must be exchangeable with
non-participants. For apartment heating fuel that fails — the mechanism that
brings an Alberta MURB into EnerGuide (gas-billed retrofit economics,
whole-building HOT2000 evaluations) is itself correlated with being
gas-heated. Selection is **non-ignorable conditional on our margins**, so no
choice of weights on these 218 records can recover the true fuel split.

### 4.3 The Phase 3 consequence

This is why the plan (ALBERTA_RECALIBRATION_PLAN.md §3.1, §5.3) demotes the
`Collective` rows of `Source_Energie_Chauf` from Tier A (microdata-derived) to
Tier B (externally constrained): when Phase 3 writes the BN's fuel CPT, the
apartment-conditional rows must be **programmatically overridden** with
external margins — StatCan 38-10-0286 (primary heating systems and energy
type) and NRCan CEUD Alberta Tables 21–25 (heating-system stock) — rather than
taken from the raked table. The same guard applies to any node whose
within-Collective distribution the sample cannot support (n_eff = 140 bounds
them all). The general principle for the meeting: **raking fixed what the
sample distorts; it cannot fix what the sample omits — those cells need a
second, independent data source.**
