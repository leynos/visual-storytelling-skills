"""Behavioural tests for the media-project CLI."""

from __future__ import annotations

import pathlib
import subprocess  # noqa: S404 - test invokes a trusted local Python module.
import sys
import typing as typ

import msgspec.json as msjson
from cmd_mox.comparators import Predicate
from pytest_bdd import given, scenario, then, when

from tests.fixtures import create_story_project

if typ.TYPE_CHECKING:
    from cmd_mox.command_runner import Invocation
    from cmd_mox.controller import CmdMox


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
def run_packaging_command(
    completed_generated_media_project: pathlib.Path,
    cmd_mox: CmdMox,
) -> None:
    """Invoke the user-facing command with project-root relative defaults."""
    cmd_mox.mock("ffprobe").with_matching_args(
        _equals("-v"),
        _equals("error"),
        _equals("-print_format"),
        _equals("json"),
        _equals("-show_format"),
        _equals("-show_streams"),
        Predicate(
            lambda value: (
                pathlib
                .Path(value)
                .resolve()
                .is_relative_to(completed_generated_media_project.resolve())
            ),
        ),
    ).times(3).runs(_ffprobe_response)
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
    subprocess.run(  # noqa: S603 - command is fixed and test-controlled.
        command,
        check=True,
    )


def _equals(expected: str) -> Predicate:
    return Predicate(lambda value: value == expected)


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
    assert project["files"][0]["type"] == "FFmpegReader"
    assert project["clips"][0]["reader"]["type"] == "FFmpegReader"


def _ffprobe_response(invocation: Invocation) -> tuple[str, str, int]:
    path = invocation.args[-1]
    durations = {
        "s01_sh001_take2.mp4": ("2.5", "60"),
        "s01_sh002_take1.mp4": ("3.25", "78"),
        "s01_sh003_take3.mp4": ("1.75", "42"),
    }
    media_name = pathlib.Path(path).name
    duration, frames = next(
        (values for filename, values in durations.items() if media_name == filename),
        ("1", "24"),
    )
    return (_ffprobe_json(duration, frames), "", 0)


def _ffprobe_json(duration: str, frames: str) -> str:
    return f"""
{{
  "streams": [
    {{
      "index": 0,
      "codec_name": "h264",
      "codec_type": "video",
      "width": 1920,
      "height": 1080,
      "pix_fmt": "yuv420p",
      "r_frame_rate": "24/1",
      "time_base": "1/12288",
      "duration": "{duration}",
      "nb_frames": "{frames}",
      "bit_rate": "8000000",
      "sample_aspect_ratio": "1:1"
    }},
    {{
      "index": 1,
      "codec_name": "aac",
      "codec_type": "audio",
      "sample_rate": "44100",
      "channels": 2,
      "channel_layout": "stereo",
      "time_base": "1/44100",
      "bit_rate": "128000",
      "tags": {{"handler_name": "SoundHandler"}}
    }}
  ],
  "format": {{
    "duration": "{duration}",
    "size": "10240",
    "bit_rate": "8128000",
    "tags": {{"major_brand": "isom"}}
  }}
}}
"""
