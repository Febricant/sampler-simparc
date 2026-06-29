"""
make_calgary_bn.py  --  Task 3 (correct data mutation for fuel & system mix)

Heating *fuel* (`Source_Energie_Chauf`) and heating *system* (`Chauffage_Logement`)
are NODES in the Bayesian network (BN_EUEMr.XDSL), NOT CSVs in
housing_characteristics/.  To make Calgary natural-gas / forced-air dominant you
must rewrite those two CPTs, which is what this script does.

It is non-destructive: it writes a NEW network, BN_Calgary.XDSL, so the original
Quebec BN (used for the Task-2 plumbing test) is preserved.  Point the Sampler at
the new file:

    python -m src.utils.sampler.Sampler \
        data/processed/bayesian_network/BN_Calgary.XDSL 1000 data/output/calgary_1000.csv

Run:
    python calgary_adaptation/make_calgary_bn.py
"""

import os
import sys
import itertools

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

import pyagrum as gum  # noqa: E402

BN_IN = os.path.join(PROJECT_DIR, "data", "processed", "bayesian_network", "BN_EUEMr.XDSL")
BN_OUT = os.path.join(PROJECT_DIR, "data", "processed", "bayesian_network", "BN_Calgary.XDSL")

# ---------------------------------------------------------------------------
# Calgary target distributions.  Keys MUST be the exact BN state labels
# (accents included) or the script raises KeyError (so typos fail loudly).
# Any label NOT listed keeps its *relative* share of the leftover mass.
# ---------------------------------------------------------------------------

# Source_Energie_Chauf states: ['Electricite','Mazout','Gaz naturel','Bi-energie','Bois']
SOURCE_ENERGIE_CHAUF = {
    "Gaz naturel": 0.85,   # Calgary ~85%+ natural gas
    "Electricite": 0.10,
    "Bois":        0.03,
    "Mazout":      0.02,
    "Bi-energie":  0.00,   # Hydro-Quebec-only tariff -> remove entirely
}

# Chauffage_Logement: 20 system combos; force the gas forced-air furnace.
CHAUFFAGE_LOGEMENT = {
    "Système central à air chaud": 0.85,   # forced-air furnace dominant
}


def _retarget(labels, current, targets):
    """Return a probability vector (label order) with `targets` pinned and the
    remaining mass distributed over the other labels in proportion to their
    current weights.  Always renormalized to sum to 1.0."""
    fixed = sum(targets.values())
    if not (0.0 <= fixed <= 1.0 + 1e-9):
        raise ValueError(f"target weights must sum to <= 1.0, got {fixed}")
    remaining = max(0.0, 1.0 - fixed)
    free = [l for l in labels if l not in targets]
    free_mass = sum(current[labels.index(l)] for l in free)

    vec = []
    for l in labels:
        if l in targets:
            vec.append(float(targets[l]))
        elif free_mass > 0:
            vec.append(current[labels.index(l)] / free_mass * remaining)
        else:  # original row had no mass on the free labels -> spread evenly
            vec.append(remaining / len(free) if free else 0.0)
    s = sum(vec)
    return [v / s for v in vec]  # guarantee exact 1.0


def force_node(bn, node, targets):
    """Overwrite every parent-conditioned distribution of `node` with the
    Calgary target, preserving the relative structure of the non-targeted states."""
    var = bn.variable(node)
    labels = list(var.labels())
    for lbl in targets:
        if lbl not in labels:
            raise KeyError(f"'{lbl}' is not a state of '{node}'. States: {labels}")

    cpt = bn.cpt(node)
    parents = [n for n in cpt.names if n != node]

    if not parents:                       # marginal node
        cpt[:] = _retarget(labels, list(cpt.toarray()), targets)
        return 1

    parent_label_lists = [list(bn.variable(p).labels()) for p in parents]
    n = 0
    for combo in itertools.product(*parent_label_lists):
        inst = {p: lbl for p, lbl in zip(parents, combo)}
        current = list(cpt[inst])                     # P(node | this parent combo)
        cpt[inst] = _retarget(labels, current, targets)
        n += 1
    return n


def main():
    bn = gum.loadBN(BN_IN)

    n1 = force_node(bn, "Source_Energie_Chauf", SOURCE_ENERGIE_CHAUF)
    n2 = force_node(bn, "Chauffage_Logement", CHAUFFAGE_LOGEMENT)

    gum.saveBN(bn, BN_OUT)

    print(f"Source_Energie_Chauf : rewrote {n1} conditional rows -> {SOURCE_ENERGIE_CHAUF}")
    print(f"Chauffage_Logement   : rewrote {n2} conditional rows -> {CHAUFFAGE_LOGEMENT}")
    print(f"Saved: {BN_OUT}")
    print("NOTE: this is a blunt, location-uniform override. To keep vintage/territory "
          "structure, make the target dicts a function of the parent combo inside force_node().")


if __name__ == "__main__":
    main()
