# -*- coding: utf-8 -*-
"""Shared fixtures. Everything here runs without OpenStudio, Docker or dask.

The CSVs live in tests/fixtures/ rather than being read from the project root.
They were read from the root at first, and the regression tests silently turned
into skips the moment the working CSVs were replaced -- exactly when they most
needed to run. A fixture that can go missing is not a regression test.
"""

import os
import sys

import pandas as pd
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
sys.path.insert(0, PROJECT_ROOT)

# The sampler export that failed the Aug 20 and Aug 23 runs, kept verbatim:
# apartment units on conditioned basements, and both the old and new slab
# argument names.
STALE_CSV = os.path.join(FIXTURES, "stale-sampler-export.csv")
# A sample with no findings, for the "must not false-positive" direction.
CLEAN_CSV = os.path.join(FIXTURES, "clean-sample.csv")
# Building 17 has a blank heat_pump_cooling_compressor_type with the feature on.
BLANK_CHOICE_CSV = os.path.join(FIXTURES, "blank-required-choice.csv")

# The buildings that failed both runs, from results/errors.parquet.
# STALE_CSV must keep flagging exactly these.
KNOWN_BAD_BUILDINGS = [2, 7, 9, 10, 14, 16, 17, 19, 22, 24, 25, 30, 34, 37,
                       46, 48, 49, 56, 61, 62, 73, 78]


def _require(path):
    # Not a skip: these ship with the tests, so a missing one is a broken
    # checkout, not an environment without the data.
    assert os.path.isfile(path), "missing test fixture: %s" % path
    return path


@pytest.fixture(scope="session")
def clean_csv():
    return _require(CLEAN_CSV)


@pytest.fixture(scope="session")
def stale_csv():
    return _require(STALE_CSV)


@pytest.fixture(scope="session")
def blank_choice_csv():
    return _require(BLANK_CHOICE_CSV)


@pytest.fixture
def stale_data(stale_csv):
    return pd.read_csv(stale_csv)
