# -*- coding: utf-8 -*-
"""One building all the way through the real runner.

Slow (minutes) and needs Docker, so it is deselected by default:

    python -m pytest tests -q                  # everything else, seconds
    python -m pytest tests -q -m slow          # this
"""

import contextlib
import io
import json
import os
import shutil
import subprocess

import pandas as pd
import pytest

import config
import osrunner
import validation
from preprocessing import preprocess_data_types, preprocess_data_to_dict
from parallelization import prepare_building, run_building

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def docker_available():
    if shutil.which("docker") is None:
        pytest.skip("docker is not installed")
    probe = subprocess.run(
        ["docker", "image", "inspect", config.DOCKER_IMAGE],
        capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip("docker image %s is not present" % config.DOCKER_IMAGE)


def test_runner_resolves(docker_available):
    description = osrunner.resolve()
    assert "OpenStudio" in description or "3.9" in description


@pytest.fixture
def results_under_project():
    """Somewhere inside the bind mount, so the container can see it.

    pytest's tmp_path lives outside the project, where OpenStudio would not find
    it -- to_container_path rejects exactly that.
    """
    relative = ".pytest-smoke"
    absolute = os.path.join(config.CURRENT_PATH, relative)
    shutil.rmtree(absolute, ignore_errors=True)
    try:
        yield relative
    finally:
        shutil.rmtree(absolute, ignore_errors=True)


def test_one_building_simulates(docker_available, clean_csv, results_under_project,
                                monkeypatch):
    monkeypatch.setattr(config, "RESULTS_PATH", results_under_project)

    data = pd.read_csv(clean_csv).head(1)
    data, _ = validation.repair(data)
    with contextlib.redirect_stdout(io.StringIO()):
        data, hpxml_columns = preprocess_data_types(data, config.ARGS_CONSTRAINTS)
        buildings = preprocess_data_to_dict(data, config.ARGS_CONSTRAINTS, hpxml_columns)

    building_dir = prepare_building(buildings[0])
    assert run_building(building_dir) == 0

    with open(os.path.join(building_dir, "out.osw")) as handle:
        assert json.load(handle)["completed_status"] == "Success"
    assert os.path.isfile(os.path.join(building_dir, "run", "finished.job"))
