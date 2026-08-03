# -*- coding: utf-8 -*-
"""Check a sampler CSV before handing it to ``main.py``, and optionally repair it.

The checks themselves live in :mod:`validation`, so ``main.py`` can refuse a bad
CSV using exactly the same code rather than trusting anyone to remember to run
this first. See that module for what each finding means.

Usage::

    python validate_sampler_csv.py <csv> [-o <out.csv>]

``-o`` writes a repaired copy: measure arguments the sampler misnamed are
renamed, an apartment unit's unsupported conditioned foundation is resolved, and
a dwelling recorded as having no water heater has its whole ``water_heater_*``
group cleared instead of keeping a partial system.
Exits non-zero when a blocking problem is found.
"""

import argparse
import sys

import pandas as pd

import config
import validation


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", help="sampler CSV to check")
    parser.add_argument("-o", "--output", help="write a repaired copy to this path")
    args = parser.parse_args()

    constraints = config.ARGS_CONSTRAINTS
    data = pd.read_csv(args.csv)

    if args.output:
        data, changes = validation.repair(data)
        for change in changes:
            print("   repaired: %s" % change)

    ok = validation.report(args.csv, data, constraints)

    succeeded, message = validation.preprocessing_succeeds(data, constraints)
    if not succeeded:
        print("   BLOCKING - %s" % message)
        return 1
    print("   %s" % message)

    if args.output:
        data.to_csv(args.output, index=False)
        print("   wrote %s" % args.output)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
