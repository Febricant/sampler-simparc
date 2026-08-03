# -*- coding: utf-8 -*-
"""Path translation and command construction. No Docker required."""

import os

import pytest

import config
import osrunner


@pytest.fixture
def docker(monkeypatch):
    monkeypatch.setattr(config, "OPENSTUDIO_RUNNER", "docker", raising=False)
    monkeypatch.setattr(config, "DOCKER_IMAGE", "simparc-dev:latest", raising=False)
    monkeypatch.setattr(config, "CONTAINER_WORKSPACE", "/workspace", raising=False)


@pytest.fixture
def native(monkeypatch):
    monkeypatch.setattr(config, "OPENSTUDIO_RUNNER", "native", raising=False)


def test_project_subdirectory_maps_onto_the_bind_mount(docker):
    inside = os.path.join(config.CURRENT_PATH, "results", "10")
    assert osrunner.to_container_path(inside) == "/workspace/results/10"


def test_translated_paths_carry_no_windows_separators(docker):
    deep = os.path.join(config.CURRENT_PATH, "results", "10", "run", "in.osw")
    translated = osrunner.to_container_path(deep)
    assert "\\" not in translated
    assert ":" not in translated
    assert translated.startswith("/workspace/")


def test_project_root_maps_to_the_workspace_itself(docker):
    assert osrunner.to_container_path(config.CURRENT_PATH) == "/workspace"


def test_path_outside_the_project_is_rejected(docker):
    """The container cannot see it, so failing here beats a confusing
    'file not found' from inside OpenStudio."""
    outside = os.path.join(os.path.dirname(config.CURRENT_PATH), "elsewhere", "x.epw")
    with pytest.raises(ValueError, match="outside the project"):
        osrunner.to_container_path(outside)


def test_native_runner_keeps_host_paths(native):
    inside = os.path.join(config.CURRENT_PATH, "results", "10")
    assert osrunner.to_container_path(inside) == os.path.abspath(inside)


def test_docker_command_mounts_the_project_and_runs_the_osw(docker):
    command = osrunner.openstudio_command("/workspace/results/10/in.osw")

    assert command[:3] == ["docker", "run", "--rm"]
    assert command[-3:] == ["run", "-w", "/workspace/results/10/in.osw"]
    assert config.DOCKER_IMAGE in command

    mount = command[command.index("-v") + 1]
    host, _, container = mount.rpartition(":")
    assert host == config.CURRENT_PATH
    assert container == "/workspace"


def test_docker_command_is_argv_not_a_shell_string(docker):
    """A project path containing spaces needs no quoting, and Git Bash cannot
    rewrite /workspace into a Windows path, because nothing runs through a shell."""
    command = osrunner.openstudio_command("/workspace/results/1/in.osw")
    assert isinstance(command, list)
    assert all(isinstance(part, str) for part in command)


def test_native_command_calls_the_binary_directly(native, monkeypatch):
    monkeypatch.setattr(osrunner, "native_executable", lambda: "/usr/bin/openstudio")
    assert osrunner.openstudio_command("/x/in.osw") == [
        "/usr/bin/openstudio", "run", "-w", "/x/in.osw"]


def test_missing_native_binary_explains_the_fix(native, monkeypatch):
    monkeypatch.setattr(osrunner, "native_executable", lambda: None)
    with pytest.raises(RuntimeError, match="OPENSTUDIO_RUNNER"):
        osrunner.openstudio_command("/x/in.osw")


# --- auto-detection -------------------------------------------------------
# The default has to work both inside the dev container (openstudio on PATH,
# no docker) and on a bare host (docker, no openstudio).

@pytest.fixture
def auto(monkeypatch):
    monkeypatch.setattr(config, "OPENSTUDIO_RUNNER", "auto", raising=False)
    monkeypatch.setattr(osrunner, "_detected", None)


def _machine(monkeypatch, openstudio=None, docker=None):
    monkeypatch.setattr(osrunner, "native_executable", lambda: openstudio)
    monkeypatch.setattr(osrunner.shutil, "which",
                        lambda name: docker if name == "docker" else None)


def test_auto_picks_native_inside_the_dev_container(auto, monkeypatch):
    """openstudio on PATH, no docker binary -- the case that raised
    FileNotFoundError: 'docker' after the runner defaulted to docker."""
    _machine(monkeypatch, openstudio="/usr/local/openstudio-3.9.0/bin/openstudio")
    assert osrunner.runner() == osrunner.NATIVE
    inside = os.path.join(config.CURRENT_PATH, "results", "10")
    assert osrunner.to_container_path(inside) == os.path.abspath(inside)


def test_auto_picks_docker_on_a_bare_host(auto, monkeypatch):
    _machine(monkeypatch, docker="/usr/bin/docker")
    assert osrunner.runner() == osrunner.DOCKER
    assert osrunner.to_container_path(
        os.path.join(config.CURRENT_PATH, "results", "10")) == "/workspace/results/10"


def test_auto_prefers_a_native_binary_when_both_exist(auto, monkeypatch):
    _machine(monkeypatch, openstudio="/usr/bin/openstudio", docker="/usr/bin/docker")
    assert osrunner.runner() == osrunner.NATIVE


def test_auto_with_nothing_available_names_both_options(auto, monkeypatch):
    _machine(monkeypatch)
    with pytest.raises(RuntimeError) as raised:
        osrunner.openstudio_command("/x/in.osw")
    message = str(raised.value)
    assert "not on PATH" in message
    assert "docker" in message.lower()
    assert "OpenStudio" in message


def test_explicit_setting_overrides_detection(monkeypatch):
    """A machine with openstudio installed can still be forced onto Docker."""
    monkeypatch.setattr(config, "OPENSTUDIO_RUNNER", "docker", raising=False)
    monkeypatch.setattr(osrunner, "_detected", None)
    _machine(monkeypatch, openstudio="/usr/bin/openstudio")
    assert osrunner.runner() == osrunner.DOCKER
