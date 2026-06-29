"""
reweight_cpt_csv.py  --  Task 3 (grammar-preserving CPT CSV reweighter)

Standalone utility that mutates the ;-separated ResStock-style CPT CSVs in
data/processed/housing_characteristics/ while STRICTLY preserving the header
grammar (Dependency=... / Option=...).  It only rewrites `Option=` cells, can
restrict which rows it touches via a `where` filter on `Dependency=` values, and
renormalizes every modified row so its Option weights sum to 1.0.

Parsing is done with a plain split(';')/join(';') (no pandas) so the header and
all non-Option columns are preserved byte-for-byte and no duplicate-column
renaming or float reformatting is introduced.

IMPORTANT
  * Heating *fuel* (Source_Energie_Chauf) and heating *system* (Chauffage_Logement)
    are NOT in this folder -- they are Bayesian-network nodes. Use make_calgary_bn.py
    for those. This tool is for the CSV-resident attributes, e.g.
    'HVAC Heating Efficiency.csv' (equipment/efficiency WITHIN a chosen system).
  * Mutation is IN PLACE and writes a one-time .bak alongside the file. Run the
    Task-2 plumbing test on the original Quebec CSVs FIRST, then run this.

Run the demo:
    python calgary_adaptation/reweight_cpt_csv.py
"""

import os
import shutil

SEP = ";"


def reweight_cpt(path, boosts, where=None, backup=True, encoding="utf-8"):
    """
    path    : full path to a housing_characteristics CPT CSV.
    boosts  : {option_value: target_weight}. `option_value` is the text AFTER
              'Option='. Sum of target weights must be in [0, 1].
    where   : optional {dependency_name: required_value} row filter, where
              `dependency_name` is the text AFTER 'Dependency='. Only matching
              rows are reweighted; others are passed through untouched.
    backup  : write `<path>.bak` once before overwriting.
    """
    where = where or {}

    with open(path, encoding=encoding) as f:
        lines = f.read().splitlines()
    header = lines[0].split(SEP)

    opt_idx = {h[len("Option="):]: i for i, h in enumerate(header) if h.startswith("Option=")}
    dep_idx = {h[len("Dependency="):]: i for i, h in enumerate(header) if h.startswith("Dependency=")}

    # Fail loudly on bad targets instead of silently doing nothing.
    for opt in boosts:
        if opt not in opt_idx:
            raise KeyError(f"Option '{opt}' not found in {os.path.basename(path)}.\n"
                           f"Available options: {list(opt_idx)}")
    for dep in where:
        if dep not in dep_idx:
            raise KeyError(f"Dependency '{dep}' not found in {os.path.basename(path)}.\n"
                           f"Available dependencies: {list(dep_idx)}")
    target_sum = sum(boosts.values())
    if not (0.0 <= target_sum <= 1.0):
        raise ValueError(f"Sum of boost weights must be in [0, 1]; got {target_sum}")

    out = [lines[0]]
    n_changed = 0

    for line in lines[1:]:
        if not line.strip():                       # preserve blank/trailing lines
            out.append(line)
            continue

        cells = line.split(SEP)

        # Row filter: skip rows whose Dependency values don't match `where`.
        if any(cells[dep_idx[d]].strip() != v for d, v in where.items()):
            out.append(line)
            continue

        # Read current Option weights (blank -> 0).
        cur = {}
        for opt, i in opt_idx.items():
            c = cells[i].strip()
            cur[opt] = float(c) if c not in ("", "nan") else 0.0

        free = [o for o in opt_idx if o not in boosts]
        free_mass = sum(cur[o] for o in free)
        remaining = 1.0 - target_sum

        new = {}
        for o in opt_idx:
            if o in boosts:
                new[o] = boosts[o]
            elif free_mass > 0:                    # keep relative shape of the rest
                new[o] = cur[o] / free_mass * remaining
            else:                                  # nothing to scale -> spread evenly
                new[o] = remaining / len(free) if free else 0.0

        s = sum(new.values())                      # exact renormalization to 1.0
        for o, i in opt_idx.items():
            cells[i] = repr(new[o] / s)

        assert abs(sum(float(cells[i]) for i in opt_idx.values()) - 1.0) < 1e-9
        out.append(SEP.join(cells))
        n_changed += 1

    if backup and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding=encoding, newline="") as f:
        f.write("\n".join(out) + "\n")

    print(f"{os.path.basename(path)}: reweighted {n_changed} row(s) "
          f"(where={where or 'ALL rows'}); boosted {boosts}.")


if __name__ == "__main__":
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    HC = os.path.join(PROJECT_DIR, "data", "processed", "housing_characteristics")

    # Demo: within the natural-gas rows of the HVAC efficiency table, make the
    # 80%-AFUE gas furnace the dominant equipment draw (Calgary forced-air).
    # 'Fuel Furnace, 80% AFUE' is a real Option= column in that file.
    reweight_cpt(
        os.path.join(HC, "HVAC Heating Efficiency.csv"),
        boosts={"Fuel Furnace, 80% AFUE": 0.85},
        where={"Source_Energie_Chauf": "Gaz naturel"},
    )
