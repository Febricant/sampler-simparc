# -*- coding: utf-8 -*-
"""Regenerate ``hpxml_column_list.py``, the stable column contract of the export.

``MapHPXML.doMapping`` assigns some HPXML arguments only inside conditional
branches, so ``pd.DataFrame(list_of_dicts)`` takes the union of whatever the
batch happened to draw: the exported header changes shape and order from one run
to the next. This script pins that contract down.

It samples the Bayesian network enough times to exercise the rare branches,
records which arguments ``doMapping`` can emit, and writes the ordered list to
``hpxml_column_list.py``.

Arguments typed ``Integer`` are deliberately excluded unless every building
supplies one: a padded (blank) Integer column makes the downstream SimParc
runner raise ``IntCastingNaNError`` in ``preprocess_data_types``. ``Boolean``
columns are recorded separately so they can be padded with ``"false"`` rather
than a blank, which pandas' ``astype(bool)`` would turn into ``True``.

Usage (from the repository root)::

    python -m src.utils.hpxml.gen_hpxml_column_list [--samples 400] [--batches 5]
"""

import argparse
import contextlib
import collections
import glob
import io
import os
import re

from src.utils.hpxml.HPXMLArg import HPXMLArguments

OUT_PATH = os.path.join("src", "utils", "hpxml", "hpxml_column_list.py")

# Keys doMapping deletes just before returning (Mapping.py, end of doMapping).
EXCLUDED = {
    "air_leakage_leakiness_description",
    "ceiling_insulation_r",
    "rim_joist_continuous_exterior_r",
    "rim_joist_continuous_interior_r",
    "rim_joist_assembly_interior_r",
    "exterior_finish_r",
}


def candidate_arguments():
    """Every schema argument named anywhere in Mapping.py, in schema order."""
    src = os.path.join("src", "utils", "sampler", "Mapping.py")
    with io.open(src, encoding="utf-8") as fh:
        text = fh.read()
    literals = set(re.findall(r"""['"]([A-Za-z_][A-Za-z0-9_]*)['"]""", text))
    return [k for k in HPXMLArguments.arguments if k in literals and k not in EXCLUDED]


def networks():
    """Every Bayesian network shipped with the repository.

    The contract covers all of them, not just the one the dashboard currently
    defaults to: BN_Calgary reaches 211 arguments and BN_EUEMr 219, so pinning
    the header to one network would make it move again the day the other is
    sampled. A column an individual network never fills is simply blank.
    """
    directory = os.path.join("data", "processed", "bayesian_network")
    return sorted(glob.glob(os.path.join(directory, "*.XDSL")))


def observe(samples, batches):
    """Count how often each key is emitted, over every network."""
    from src.utils.sampler.Sampler import Sampler

    counts = collections.Counter()
    arg_counts = collections.Counter()
    arg_order = {}
    total = 0
    for bn_path in networks():
        for _ in range(batches):
            sampler = Sampler(bn_path)
            with contextlib.redirect_stdout(io.StringIO()):
                sampler.run_parallel(samples, ev={})
            for dct in sampler.lst_dct_HPXML:
                total += 1
                counts.update(dct.keys())
            for dct in sampler.lst_dct_args:
                arg_counts.update(dct.keys())
                for key in dct:
                    arg_order.setdefault(key, len(arg_order))
    return counts, total, arg_counts, arg_order


def build(samples, batches):
    schema = HPXMLArguments.arguments
    counts, total, arg_counts, arg_order = observe(samples, batches)

    columns, booleans = [], []
    for key in candidate_arguments():
        if not counts[key]:
            continue  # doMapping never populates it -- do not ship a dead column
        arg_type = schema[key].get("Type")
        if arg_type == "Integer" and counts[key] < total:
            continue  # a blank Integer would crash the downstream runner
        columns.append(key)
        if arg_type == "Boolean":
            booleans.append(key)

    # Keys doMapping emits that predate the current schema transcription. They
    # are not measure arguments, so the runner carries them as metadata.
    extras = sorted(k for k in counts if k not in schema)

    # The sampler-attribute block. Its membership is the same for every network,
    # but the BN's topological variable order is not, so pin the order too.
    args_columns = sorted(arg_counts, key=lambda k: arg_order[k])
    return columns + extras, booleans, args_columns, total


def render(columns, booleans, args_columns, total, samples, batches):
    def block(name, values):
        body = "".join('    "%s",\n' % v for v in values)
        return "%s = [\n%s]\n" % (name, body)

    header = (
        "# -*- coding: utf-8 -*-\n"
        '"""Stable column contract for the sampler export.\n\n'
        "GENERATED FILE -- do not edit by hand. Regenerate with::\n\n"
        "    python -m src.utils.hpxml.gen_hpxml_column_list\n\n"
        "Observed over %d buildings (%d batches of %d per network).\n"
        '"""\n\n' % (total, batches, samples)
    )
    return (
        header
        + block("HPXML_COLUMNS", columns)
        + '\n# Padded with "false" rather than a blank: pandas casts a blank'
          " Boolean to True.\n"
        + block("BOOLEAN_COLUMNS", booleans)
        + "\n# The sampler-attribute block, pinned because the BN's topological\n"
          "# variable order differs between networks.\n"
        + block("ARGS_COLUMNS", args_columns)
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=400, help="buildings per batch")
    parser.add_argument("--batches", type=int, default=5, help="number of batches")
    args = parser.parse_args()

    columns, booleans, args_columns, total = build(args.samples, args.batches)
    with io.open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(render(columns, booleans, args_columns, total, args.samples, args.batches))
    print("wrote %s: %d HPXML + %d sampler columns (%d boolean) from %d buildings"
          % (OUT_PATH, len(columns), len(args_columns), len(booleans), total))


if __name__ == "__main__":
    main()
