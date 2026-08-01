# -*- coding: utf-8 -*-
"""What OpenStudio would actually be handed, produced without running OpenStudio.

`prepare_building` writes the same in.osw the real run does, so the inputs can be
asserted on in milliseconds instead of after a seven-minute batch of failures.
"""

import contextlib
import io
import json
import os

import pandas as pd
import pytest

import config
import validation
from preprocessing import preprocess_data_types, preprocess_data_to_dict
from parallelization import prepare_building


def _prepare_all(csv_path, project_root, monkeypatch, repair=False):
    """Write every building's in.osw under a throwaway project root."""
    monkeypatch.setattr(config, "CURRENT_PATH", str(project_root))
    monkeypatch.setattr(config, "RESULTS_PATH", "results")
    monkeypatch.setattr(config, "OPENSTUDIO_RUNNER", "docker", raising=False)
    monkeypatch.setattr(config, "CONTAINER_WORKSPACE", "/workspace", raising=False)

    data = pd.read_csv(csv_path)
    if repair:
        data, _ = validation.repair(data)

    # preprocess_data_to_dict warns about every argument the CSV omits (~330 a
    # building); the findings that matter are validation.check's, not these.
    with contextlib.redirect_stdout(io.StringIO()):
        data, hpxml_columns = preprocess_data_types(data, config.ARGS_CONSTRAINTS)
        buildings = preprocess_data_to_dict(data, config.ARGS_CONSTRAINTS, hpxml_columns)

    return [prepare_building(building) for building in buildings]


def _osw(building_dir):
    with open(os.path.join(building_dir, "in.osw")) as handle:
        return json.load(handle)


def _arguments(osw, measure):
    for step in osw["steps"]:
        if step["measure_dir_name"] == measure:
            return step["arguments"]
    raise AssertionError("no %s step in the OSW" % measure)


def _paths_in(value):
    """Every string in the OSW that looks like a filesystem path."""
    if isinstance(value, str):
        return [value] if ("/" in value or "\\" in value) else []
    if isinstance(value, dict):
        return [p for v in value.values() for p in _paths_in(v)]
    if isinstance(value, list):
        return [p for v in value for p in _paths_in(v)]
    return []


@pytest.fixture
def prepared(clean_csv, tmp_path, monkeypatch):
    return _prepare_all(clean_csv, tmp_path, monkeypatch)


def test_an_osw_is_written_for_every_building(prepared):
    assert len(prepared) == 3
    for building_dir in prepared:
        assert os.path.isfile(os.path.join(building_dir, "in.osw"))


def test_every_osw_is_valid_json(prepared):
    for building_dir in prepared:
        assert _osw(building_dir)["steps"]


def test_no_osw_path_escapes_into_the_host_filesystem(prepared):
    """The regression that made the devcontainer mandatory: host-absolute paths
    baked into the OSW resolve only when the container *is* the host."""
    for building_dir in prepared:
        for path in _paths_in(_osw(building_dir)):
            assert "\\" not in path, path
            assert not path[1:3] == ":/", path
            if path.startswith("/"):
                assert path.startswith("/workspace"), path


def test_measure_and_weather_paths_point_into_the_mount(prepared):
    osw = _osw(prepared[0])
    assert osw["measure_paths"] == ["/workspace/measures"]
    weather = _arguments(osw, "BuildResidentialHPXML")["weather_station_epw_filepath"]
    assert weather == "/workspace/weather/" + config.WEATHER_EPW_FILENAME


def test_hpxml_paths_are_consistent_across_steps(prepared):
    osw = _osw(prepared[0])
    built = _arguments(osw, "BuildResidentialHPXML")["hpxml_path"]
    schedules = _arguments(osw, "BuildResidentialScheduleFile")
    assert schedules["hpxml_path"] == built
    assert schedules["hpxml_output_path"] == \
        _arguments(osw, "HPXMLtoOpenStudio")["hpxml_path"]


def test_no_building_reaches_openstudio_with_a_rejected_combination(prepared):
    """The exact failure of the Aug 20 and Aug 23 runs, asserted on the inputs."""
    for building_dir in prepared:
        arguments = _arguments(_osw(building_dir), "BuildResidentialHPXML")
        if arguments.get("geometry_unit_type") == "apartment unit":
            assert arguments.get("geometry_foundation_type") not in (
                "ConditionedBasement", "ConditionedCrawlspace")


def test_repaired_stale_csv_produces_simulable_inputs(stale_csv, tmp_path, monkeypatch):
    """End to end over the file that failed twice: after repair, no building
    carries the rejected pairing and the slab arguments survive."""
    prepared = _prepare_all(stale_csv, tmp_path, monkeypatch, repair=True)
    assert len(prepared) == 80

    for building_dir in prepared:
        arguments = _arguments(_osw(building_dir), "BuildResidentialHPXML")
        if arguments.get("geometry_unit_type") == "apartment unit":
            assert arguments.get("geometry_foundation_type") not in (
                "ConditionedBasement", "ConditionedCrawlspace")
        assert "slab_perimeter_insulation_depth" in arguments
        assert "slab_under_insulation_width" in arguments


def test_stale_csv_without_repair_still_carries_the_defect(stale_csv, tmp_path, monkeypatch):
    """Guards the guard: if this ever stops failing, the fixture has changed and
    the tests above no longer prove anything."""
    prepared = _prepare_all(stale_csv, tmp_path, monkeypatch, repair=False)
    offenders = [
        d for d in prepared
        if _arguments(_osw(d), "BuildResidentialHPXML").get("geometry_unit_type") == "apartment unit"
        and _arguments(_osw(d), "BuildResidentialHPXML").get("geometry_foundation_type")
        in ("ConditionedBasement", "ConditionedCrawlspace")
    ]
    assert len(offenders) == 22
