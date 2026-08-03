# -*- coding: utf-8 -*-
"""The checks that must stop a bad CSV before it reaches OpenStudio.

The apartment/conditioned-basement pairing shipped twice: it failed 22 of 80
buildings on Aug 20 and again, identically, on Aug 23. These are its regression
tests.
"""

import pandas as pd
import pytest

import validation
from conftest import KNOWN_BAD_BUILDINGS


def test_stale_csv_flags_exactly_the_buildings_that_failed(stale_data):
    findings = validation.check(stale_data)
    assert len(findings.combinations) == 1
    description, rows = findings.combinations[0]
    assert "apartment unit" in description
    assert rows == KNOWN_BAD_BUILDINGS


def test_stale_csv_is_blocking(stale_data):
    assert validation.check(stale_data).blocking is True


def test_stale_csv_names_the_misnamed_slab_columns(stale_data):
    unrecognized = validation.check(stale_data).unrecognized
    assert "slab_perimeter_depth" in unrecognized
    assert "slab_under_width" in unrecognized


def test_repair_clears_every_blocking_finding(stale_data):
    repaired, changes = validation.repair(stale_data)
    assert changes, "repair reported no changes on a CSV known to need them"
    assert validation.check(repaired).blocking is False


def test_repair_resolves_foundations_by_building_level(stale_data):
    repaired, _ = validation.repair(stale_data)
    apartments = repaired[repaired["geometry_unit_type"] == "apartment unit"]
    # No apartment may keep a conditioned foundation...
    assert not apartments["geometry_foundation_type"].isin(
        ["ConditionedBasement", "ConditionedCrawlspace"]).any()
    # ...and a unit with a dwelling below it sits above an apartment, while a
    # bottom-floor unit keeps its basement outside the conditioned volume.
    bad = stale_data.index[
        stale_data["geometry_unit_type"].eq("apartment unit")
        & stale_data["geometry_foundation_type"].isin(
            ["ConditionedBasement", "ConditionedCrawlspace"])]
    for index in bad:
        level = stale_data.loc[index, "Geometry Building Level"]
        expected = "AboveApartment" if level in ("Middle", "Top") \
            else "UnconditionedBasement"
        assert repaired.loc[index, "geometry_foundation_type"] == expected


def test_repair_merges_rather_than_duplicating_a_renamed_column(stale_data):
    """The stale export carries both slab names: the correct one blank and the
    misnamed one populated. Renaming would leave two columns of the same name,
    read_csv would mangle the populated one to "<name>.1", and the repair would
    silently do nothing."""
    assert "slab_perimeter_depth" in stale_data.columns
    assert "slab_perimeter_insulation_depth" in stale_data.columns

    repaired, _ = validation.repair(stale_data)

    for name in ("slab_perimeter_insulation_depth", "slab_under_insulation_width"):
        assert list(repaired.columns).count(name) == 1, "%s duplicated" % name
        assert repaired[name].notna().all(), "%s lost its values" % name
    assert "slab_perimeter_depth" not in repaired.columns
    assert "slab_under_width" not in repaired.columns


def test_repaired_csv_survives_a_round_trip(stale_data, tmp_path):
    """Writing and re-reading must not reintroduce duplicate columns."""
    repaired, _ = validation.repair(stale_data)
    path = tmp_path / "repaired.csv"
    repaired.to_csv(path, index=False)
    reloaded = pd.read_csv(path)

    assert not [c for c in reloaded.columns if c.endswith(".1")]
    assert validation.check(reloaded).blocking is False


def test_clean_csv_has_no_blocking_findings(clean_csv):
    data = pd.read_csv(clean_csv)
    assert validation.check(data).blocking is False


def test_blank_required_choice_is_blocking(blank_choice_csv):
    data = pd.read_csv(blank_choice_csv)
    findings = validation.check(data)
    assert findings.blocking is True
    flagged = {column: rows for column, _, rows in findings.blocking_blanks}
    assert flagged["heat_pump_cooling_compressor_type"] == [17]


def test_repair_is_a_no_op_on_a_clean_csv(clean_csv):
    data = pd.read_csv(clean_csv)
    repaired, changes = validation.repair(data.copy())
    assert changes == []
    pd.testing.assert_frame_equal(repaired, data)


@pytest.mark.parametrize("foundation", ["ConditionedBasement", "ConditionedCrawlspace"])
def test_unsupported_combination_detected_for_both_foundations(foundation):
    data = pd.DataFrame([
        {"geometry_unit_type": "apartment unit", "geometry_foundation_type": foundation},
        {"geometry_unit_type": "single-family detached", "geometry_foundation_type": foundation},
    ])
    assert validation.check_combinations(data) == [
        (validation.UNSUPPORTED_COMBINATIONS[0][0], [1])
    ]
