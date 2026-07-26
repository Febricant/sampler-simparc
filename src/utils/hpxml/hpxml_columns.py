# -*- coding: utf-8 -*-
"""Give the sampler export a stable header.

Two things made the header move between runs. ``MapHPXML.doMapping`` assigns
some arguments only inside conditional branches, so the union of keys depended
on what the batch happened to draw; and the Bayesian network's topological
variable order differs between networks, so the sampler-attribute block came out
in a different order for BN_Calgary than for BN_EUEMr. Downstream consumers (the
SimParc runner) cannot be written against a contract that moves, so every export
is reindexed onto the generated lists in :mod:`hpxml_column_list`.

Regenerate those lists with::

    python -m src.utils.hpxml.gen_hpxml_column_list
"""

import warnings

import pandas as pd

from src.utils.hpxml.hpxml_column_list import (
    ARGS_COLUMNS,
    BOOLEAN_COLUMNS,
    HPXML_COLUMNS,
)

_BOOLEAN_COLUMNS = frozenset(BOOLEAN_COLUMNS)


def _reindex(frame, columns, label):
    """Reindex onto ``columns``, keeping anything unexpected rather than losing it."""
    unknown = sorted(set(frame.columns) - set(columns))
    if unknown:
        warnings.warn(
            "%s outside the column contract: %s. "
            "Regenerate with: python -m src.utils.hpxml.gen_hpxml_column_list"
            % (label, ", ".join(unknown)),
            stacklevel=3,
        )
    absent = set(columns) - set(frame.columns)
    frame = frame.reindex(columns=list(columns) + unknown)
    # A blank Boolean would become True under the runner's astype(bool).
    for column in absent & _BOOLEAN_COLUMNS:
        frame[column] = "false"
    return frame


def stabilize_export(dfargs, dfHPXML):
    """Return the combined export frame with a fixed header, in a fixed order."""
    dfargs = _reindex(dfargs, ARGS_COLUMNS, "Sampler attributes")
    dfHPXML = _reindex(dfHPXML, HPXML_COLUMNS, "HPXML arguments")
    return pd.concat([dfargs, dfHPXML], axis=1)
