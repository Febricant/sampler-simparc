# -*- coding: utf-8 -*-
"""Decide how to invoke OpenStudio, and translate paths for it.

SimParc used to assume it was running *inside* the devcontainer: the OSW files
carried host-absolute paths, which resolve only because the container's
filesystem is the project's filesystem. That made VS Code plus a devcontainer a
hard requirement for running anything.

Two things are needed to lift it:

``openstudio_command``
    builds the argv list for a run. ``docker`` shells out to the image that
    already carries OpenStudio 3.9.0, so the pipeline runs from an ordinary
    Windows shell; ``native`` calls an installed binary directly.

``to_container_path``
    rewrites a path the OSW will be read *by OpenStudio* into the filesystem
    OpenStudio will see. Under ``docker`` the project is bind-mounted at
    ``config.CONTAINER_WORKSPACE``, so ``C:\\...\\SimParc\\results\\10`` has to be
    written into the OSW as ``/workspace/results/10``. The OSW file itself is
    still written to the host path -- only its *contents* are translated.

Nothing here imports dask or pandas, so it stays cheap to unit-test.
"""

import os
import posixpath
import shutil
import subprocess

import config

DOCKER = "docker"
NATIVE = "native"
AUTO = "auto"

_detected = None


def _detect():
    """Pick a runner from what this machine actually has, or None.

    An OpenStudio binary wins over Docker: inside the dev container openstudio
    is on PATH and docker is not, so preferring the binary keeps the container
    working while a bare host falls through to Docker. Both probes are just PATH
    lookups -- the expensive check that the image really runs stays in
    :func:`resolve`, which is called once per batch rather than once per
    building.
    """
    global _detected
    if _detected is None:
        if native_executable() is not None:
            _detected = NATIVE
        elif shutil.which("docker") is not None:
            _detected = DOCKER
        else:
            _detected = False   # nothing usable; distinct from "not yet probed"
    return _detected or None


def runner():
    """The runner to use: whatever is configured, or auto-detected.

    Falls back to NATIVE when auto-detection finds nothing, so path translation
    stays a no-op and the failure is reported by :func:`resolve` with a message
    covering both options rather than by a confusing path rewrite.
    """
    configured = getattr(config, "OPENSTUDIO_RUNNER", AUTO).strip().lower()
    if configured in (DOCKER, NATIVE):
        return configured
    return _detect() or NATIVE


def native_executable():
    """The OpenStudio binary for the native runner, or None.

    ``config.OPENSTUDIO_EXE`` wins when it points at a real file; otherwise fall
    back to whatever is on PATH, which is the case inside the devcontainer.
    """
    configured = getattr(config, "OPENSTUDIO_EXE", None)
    if configured:
        candidate = configured if os.path.isabs(configured) \
            else os.path.join(config.CURRENT_PATH, configured)
        if os.path.isfile(candidate):
            return candidate
    return shutil.which("openstudio")


def to_container_path(host_path):
    """Translate a host path into the path OpenStudio will resolve.

    Under the native runner OpenStudio shares our filesystem, so the path is
    only normalised. Under docker it is rewritten relative to the bind mount.
    Raises ValueError for a path outside the project, which the container would
    not be able to see.
    """
    absolute = os.path.abspath(host_path)
    if runner() != DOCKER:
        return absolute

    relative = os.path.relpath(absolute, config.CURRENT_PATH)
    if relative == os.curdir:
        return config.CONTAINER_WORKSPACE
    if relative.startswith(os.pardir):
        raise ValueError(
            "%s is outside the project directory (%s), so it will not exist "
            "inside the container. Keep simulation inputs under the project."
            % (absolute, config.CURRENT_PATH))
    return posixpath.join(config.CONTAINER_WORKSPACE, relative.replace(os.sep, "/"))


def openstudio_command(osw_path):
    """argv for running ``osw_path`` (a container path under the docker runner).

    Returned as a list and executed without a shell, so a project directory
    containing spaces needs no quoting and Git Bash cannot mangle ``/workspace``
    into a Windows path.
    """
    if runner() == DOCKER:
        return [
            "docker", "run", "--rm",
            "-v", "%s:%s" % (config.CURRENT_PATH, config.CONTAINER_WORKSPACE),
            "-w", config.CONTAINER_WORKSPACE,
            "--entrypoint", "openstudio",
            config.DOCKER_IMAGE,
            "run", "-w", osw_path,
        ]
    executable = native_executable()
    if executable is None:
        raise RuntimeError(_unavailable_message())
    return [executable, "run", "-w", osw_path]


def _unavailable_message():
    configured = getattr(config, "OPENSTUDIO_RUNNER", AUTO).strip().lower()

    if configured not in (DOCKER, NATIVE) and _detect() is None:
        return (
            "No way to run OpenStudio was found.\n"
            "  'openstudio' is not on PATH and config.OPENSTUDIO_EXE (%r) does "
            "not point at a binary,\n"
            "  and 'docker' is not on PATH either.\n"
            "  install OpenStudio 3.9.0, or install Docker and build the %s image."
            % (getattr(config, "OPENSTUDIO_EXE", None), config.DOCKER_IMAGE))

    if runner() == DOCKER:
        return (
            "OPENSTUDIO_RUNNER is 'docker' but the image %r is not runnable.\n"
            "  check:  docker run --rm --entrypoint openstudio %s --version\n"
            "  or set config.OPENSTUDIO_RUNNER = 'native' (or 'auto') and point "
            "config.OPENSTUDIO_EXE at an installed openstudio binary."
            % (config.DOCKER_IMAGE, config.DOCKER_IMAGE))
    return (
        "OPENSTUDIO_RUNNER is 'native' but no OpenStudio binary was found.\n"
        "  looked at config.OPENSTUDIO_EXE (%r) and 'openstudio' on PATH.\n"
        "  install OpenStudio 3.9.0, or set config.OPENSTUDIO_RUNNER = 'docker'."
        % (getattr(config, "OPENSTUDIO_EXE", None),))


def resolve():
    """Check the runner works, once, before any simulation is dispatched.

    Returns a human-readable description. Raises RuntimeError with the fix
    spelled out, so a misconfiguration surfaces here rather than as 80 identical
    failures inside Dask workers.
    """
    configured = getattr(config, "OPENSTUDIO_RUNNER", AUTO).strip().lower()
    how = "configured" if configured in (DOCKER, NATIVE) else "auto-detected"

    if runner() == DOCKER:
        try:
            completed = subprocess.run(
                ["docker", "run", "--rm", "--entrypoint", "openstudio",
                 config.DOCKER_IMAGE, "--version"],
                capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError) as exc:
            raise RuntimeError("%s\n  (%s)" % (_unavailable_message(), exc))
        if completed.returncode != 0:
            raise RuntimeError("%s\n  %s"
                               % (_unavailable_message(),
                                  (completed.stderr or "").strip()))
        return "docker (%s) image %s, OpenStudio %s" % (
            how, config.DOCKER_IMAGE, completed.stdout.strip())

    executable = native_executable()
    if executable is None:
        raise RuntimeError(_unavailable_message())
    return "native (%s) OpenStudio at %s" % (how, executable)
