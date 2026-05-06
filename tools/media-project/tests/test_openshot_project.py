"""Unit and snapshot tests for OpenShot project packaging."""

from __future__ import annotations

import pathlib
import typing as typ

import msgspec.json as msjson
import pytest

from media_project.openshot_project import (
    InputValidationError,
    OutputExistsError,
    PackageRequest,
    ProjectSettings,
    build_timeline_clips,
    package_openshot_project,
)
from tests.fixtures import create_story_project

if typ.TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion


def test_build_timeline_clips_uses_cumulative_positions(tmp_path: pathlib.Path) -> None:
    """Timeline positions are computed from ordered clip durations."""
    create_story_project(tmp_path)

    clips = build_timeline_clips(_request(tmp_path))

    assert [clip.shot_id for clip in clips] == ["S01_SH001", "S01_SH002", "S01_SH003"]
    assert [str(clip.position_seconds) for clip in clips] == ["0", "2.5", "5.75"]


def test_missing_media_fails_with_shot_and_path(tmp_path: pathlib.Path) -> None:
    """A missing selected media path is rejected before output is written."""
    create_story_project(tmp_path)
    missing_path = tmp_path / "generated" / "clips" / "s01_sh002_take1.mp4"
    missing_path.unlink()

    with pytest.raises(
        InputValidationError,
        match=r"Missing media for shot S01_SH002: generated/clips/s01_sh002_take1.mp4",
    ):
        package_openshot_project(_request(tmp_path))


def test_unaccepted_review_state_fails(tmp_path: pathlib.Path) -> None:
    """Required shots must be accepted, approved, final, or selected."""
    create_story_project(tmp_path)
    log_path = tmp_path / "generated" / "generation_log.md"
    log_path.write_text(
        log_path.read_text(encoding="utf-8").replace(
            "| accepted | hash-001 |",
            "| needs review | hash-001 |",
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        InputValidationError,
        match="Shot S01_SH001 has unaccepted review state: needs_review",
    ):
        package_openshot_project(_request(tmp_path))


def test_duplicate_generation_log_rows_fail(tmp_path: pathlib.Path) -> None:
    """A selected clip must bind to exactly one generation log row."""
    create_story_project(tmp_path)
    log_path = tmp_path / "generated" / "generation_log.md"
    lines = log_path.read_text(encoding="utf-8").splitlines()
    lines.append(next(line for line in lines if line.startswith("| S01_SH001 |")))
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(
        InputValidationError,
        match=(
            r"Multiple generation log rows match shot S01_SH001 "
            r"sub-clip A clip generated/clips/s01_sh001_take2.mp4\."
        ),
    ):
        package_openshot_project(_request(tmp_path))


def test_selected_clip_parent_traversal_fails(tmp_path: pathlib.Path) -> None:
    """Selected clip metadata cannot point outside the project root."""
    create_story_project(tmp_path)
    _replace_in_generated_tables(
        tmp_path,
        "generated/clips/s01_sh001_take2.mp4",
        "../outside.mp4",
    )

    with pytest.raises(
        InputValidationError,
        match=r"Selected clip path for shot S01_SH001 must stay inside the project",
    ):
        package_openshot_project(_request(tmp_path))


def test_output_requires_force_to_overwrite(tmp_path: pathlib.Path) -> None:
    """The packaging command does not overwrite existing outputs by default."""
    create_story_project(tmp_path)
    output = tmp_path / "generated" / "media-project" / "story.osp"
    output.parent.mkdir(parents=True)
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(OutputExistsError, match=f"Output already exists: {output}"):
        package_openshot_project(_request(tmp_path))


def test_project_and_sidecar_json_match_snapshot(
    tmp_path: pathlib.Path,
    snapshot: SnapshotAssertion,
) -> None:
    """Project and sidecar JSON remain deterministic for the fixture."""
    create_story_project(tmp_path)
    request = _request(tmp_path)

    package_openshot_project(request)

    payload = {
        "openshot": msjson.decode(request.output.read_bytes()),
        "sidecar": msjson.decode(request.sidecar.read_bytes()),
    }
    assert payload == snapshot


def test_openshot_asset_paths_are_relative_to_project_file(
    tmp_path: pathlib.Path,
) -> None:
    """OpenShot asset paths are relative to the saved .osp location."""
    create_story_project(tmp_path)
    request = _request(tmp_path)

    package_openshot_project(request)

    project = msjson.decode(request.output.read_bytes())
    assert [file_entry["path"] for file_entry in project["files"]] == [
        "../clips/s01_sh001_take2.mp4",
        "../clips/s01_sh002_take1.mp4",
        "../clips/s01_sh003_take3.mp4",
    ]
    assert [clip["filepath"] for clip in project["clips"]] == [
        "../clips/s01_sh001_take2.mp4",
        "../clips/s01_sh002_take1.mp4",
        "../clips/s01_sh003_take3.mp4",
    ]


def _replace_in_generated_tables(
    root: pathlib.Path,
    old_value: str,
    new_value: str,
) -> None:
    for path in (
        root / "generated" / "assembly_order.md",
        root / "generated" / "generation_log.md",
    ):
        path.write_text(
            path.read_text(encoding="utf-8").replace(old_value, new_value),
            encoding="utf-8",
        )


def _request(root: pathlib.Path) -> PackageRequest:
    return PackageRequest(
        project_root=root,
        assembly_order=pathlib.Path("generated/assembly_order.md"),
        generation_log=pathlib.Path("generated/generation_log.md"),
        output=root / "generated" / "media-project" / "story.osp",
        sidecar=root / "generated" / "media-project" / "media-project.json",
        source_manifest=pathlib.Path("prompts/manifest.md"),
        project_name="snapshot-story",
        force=False,
        settings=ProjectSettings(),
    )
