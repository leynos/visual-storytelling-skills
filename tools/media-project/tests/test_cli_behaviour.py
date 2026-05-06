"""Behavioural tests for the media-project CLI."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys
import typing as typ

import msgspec.json as msjson
from pytest_bdd import given, scenario, then, when

from tests.fixtures import create_story_project

if typ.TYPE_CHECKING:
    import pathlib


@scenario(
    "features/openshot_packaging.feature",
    "Package accepted generated clips into an OpenShot project",
)
def test_package_accepted_generated_clips() -> None:
    """The CLI writes an OpenShot project for accepted generated clips."""


@given(
    "a completed generated media project",
    target_fixture="completed_generated_media_project",
)
def completed_generated_media_project(tmp_path: pathlib.Path) -> pathlib.Path:
    """Create generated media metadata and fake local video files."""
    create_story_project(tmp_path)
    return tmp_path


@when("I run the OpenShot packaging command")
def run_packaging_command(completed_generated_media_project: pathlib.Path) -> None:
    """Invoke the user-facing command with project-root relative defaults."""
    command = [
        sys.executable,
        "-m",
        "media_project.cli",
        "package-openshot",
        "--project-root",
        str(completed_generated_media_project),
        "--project-name",
        "bdd-story",
    ]
    subprocess.run(command, check=True)  # noqa: S603


@then("an OpenShot project and sidecar are written in timeline order")
def project_and_sidecar_are_written(
    completed_generated_media_project: pathlib.Path,
) -> None:
    """Verify the CLI's observable generated files."""
    output = (
        completed_generated_media_project
        / "generated"
        / "media-project"
        / "project.osp"
    )
    sidecar = (
        completed_generated_media_project
        / "generated"
        / "media-project"
        / "media-project.json"
    )

    project = msjson.decode(output.read_bytes())
    metadata = msjson.decode(sidecar.read_bytes())

    assert [clip["shot_id"] for clip in metadata["clips"]] == [
        "S01_SH001",
        "S01_SH002",
        "S01_SH003",
    ]
    assert [clip["position"] for clip in project["clips"]] == [0.0, 2.5, 5.75]
