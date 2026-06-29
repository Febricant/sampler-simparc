"""
run_calgary_batch.py  --  Task 2 (generate the three named output CSVs)

The CLI entry point (python -m src.utils.sampler.Sampler ...) writes a single
COMBINED csv. This driver uses the same Sampler API but writes the three files
the notebook produces, so you get building-mapping.csv explicitly:

    data/output/building-input.csv    (human-readable draws  -> 97 cols)
    data/output/building-mapping.csv  (HPXML measure args    -> ~219 cols)
    data/output/building-test.csv     (the two concatenated  -> ~316 cols)

For Task 2 keep BN = BN_EUEMr.XDSL (Quebec distributions) so you are testing the
Calgary *plumbing* (EPW / UTC / Bi-energie patch), not the data. Switch to
BN_Calgary.XDSL after running make_calgary_bn.py.

Run:
    python calgary_adaptation/run_calgary_batch.py
"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

import pandas as pd  # noqa: E402
from src.utils.sampler.Sampler import Sampler  # noqa: E402

BN = os.path.join(PROJECT_DIR, "data", "processed", "bayesian_network", "BN_EUEMr.XDSL")
OUT = os.path.join(PROJECT_DIR, "data", "output")
N = 1000

if __name__ == "__main__":
    s = Sampler(BN).run_parallel(N, ev={})          # run_parallel REQUIRES ev=

    pd.DataFrame(s.lst_dct_args).to_csv(os.path.join(OUT, "building-input.csv"), index=False)
    pd.DataFrame(s.lst_dct_HPXML).to_csv(os.path.join(OUT, "building-mapping.csv"), index=False)
    s.to_df().to_csv(os.path.join(OUT, "building-test.csv"), index=False)

    print(f"Wrote building-input.csv / building-mapping.csv / building-test.csv "
          f"({N} dwellings) to {OUT}")
