#!/usr/bin/env python
"""Run both stages of the pipeline with one command.

    python pipeline.py 100                  sample 100 dwellings, then dry-run them
    python pipeline.py 100 --simulate       ... and actually simulate them
    python pipeline.py --csv out/sample.csv --simulate    skip sampling

The two stages each need their own working directory: simparc/config.py parses
measure.xml through a relative path at import time, and several sampler modules
resolve data files relative to themselves. So this driver does not import
either one -- it runs each as a subprocess from its own directory, which is
also what keeps a failure in one stage from taking down the other.
"""

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SAMPLER = os.path.join(ROOT, "sampler")
SIMPARC = os.path.join(ROOT, "simparc")
DEFAULT_BN = os.path.join("data", "processed", "bayesian_network", "BN_Calgary.XDSL")


def run(argv, cwd, what):
    """Run a stage, echoing the command so a failure can be reproduced by hand."""
    print("\n=== %s ===" % what)
    print("    $ %s   (in %s)" % (" ".join(argv), os.path.relpath(cwd, ROOT)))
    # The child writes straight to the terminal, so flush first or these
    # banners surface after the output they are meant to introduce.
    sys.stdout.flush()
    completed = subprocess.run(argv, cwd=cwd)
    if completed.returncode != 0:
        raise SystemExit("\n%s failed (exit %d)." % (what, completed.returncode))


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description="Sample a building stock, then simulate it.")
    parser.add_argument("count", type=int, nargs="?",
                        help="number of dwellings to sample")
    parser.add_argument("--csv", metavar="PATH",
                        help="use this existing sample instead of drawing a new one")
    parser.add_argument("--bn", default=DEFAULT_BN,
                        help="Bayesian network to sample, relative to sampler/ "
                             "(default: %(default)s)")
    parser.add_argument("--evidence", metavar="JSON",
                        help="condition the draw, e.g. '{\"Type_Logement\": \"...\"}'")
    parser.add_argument("--out", default=os.path.join("out", "sample.csv"),
                        help="where to write the sample, relative to the repository "
                             "root (default: %(default)s)")
    parser.add_argument("--simulate", action="store_true",
                        help="run the real simulation. Without this the second "
                             "stage stops at --dry-run, which needs no OpenStudio.")
    parser.add_argument("--limit", type=int, metavar="N",
                        help="only simulate the first N buildings")
    parser.add_argument("--serial", action="store_true",
                        help="simulate one at a time instead of through dask")
    parser.add_argument("--repair", action="store_true",
                        help="let SimParc repair validation findings instead of refusing")
    args = parser.parse_args(argv)

    if args.csv is None and args.count is None:
        parser.error("give a dwelling count to sample, or --csv to reuse a sample")
    if args.csv is not None and args.count is not None:
        parser.error("give either a dwelling count or --csv, not both")
    return args


def main(argv=None):
    args = parse_arguments(argv)

    # Stage 1 -- sample, unless an existing CSV was supplied.
    if args.csv is not None:
        csv_path = os.path.abspath(args.csv)
        if not os.path.isfile(csv_path):
            raise SystemExit("no such file: %s" % csv_path)
        print("Using existing sample: %s" % csv_path)
    else:
        csv_path = os.path.abspath(os.path.join(ROOT, args.out))
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        sample_cmd = [sys.executable, "-m", "src.utils.sampler.Sampler",
                      args.bn, str(args.count), csv_path]
        if args.evidence:
            sample_cmd += ["-ev", args.evidence]
        run(sample_cmd, SAMPLER, "Stage 1: sampling %d dwelling(s)" % args.count)

        if not os.path.isfile(csv_path):
            raise SystemExit("the sampler reported success but wrote no %s" % csv_path)

    # Stage 2 -- simulate. Always dry-run first: it is seconds, needs neither
    # Docker nor dask, and catches the input problems that would otherwise fail
    # once per building.
    simulate_cmd = [sys.executable, "main.py", csv_path]
    if args.repair:
        simulate_cmd.append("--repair")
    if args.limit:
        simulate_cmd += ["--limit", str(args.limit)]

    run(simulate_cmd + ["--dry-run"], SIMPARC, "Stage 2a: checking the inputs (dry run)")

    if not args.simulate:
        print("\nDry run only. Re-run with --simulate to run the simulations.")
        return 0

    if args.serial:
        simulate_cmd.append("--serial")
    run(simulate_cmd, SIMPARC, "Stage 2b: simulating")

    print("\nDone. Results are under %s"
          % os.path.join("simparc", "results"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
