"""Unit and snapshot tests for OpenShot project packaging."""

from __future__ import annotations

import decimal
import pathlib
import typing as typ

import msgspec.json as msjson
import pytest

from media_project.openshot_project import (
    InputValidationError,
    MediaProbe,
    OutputExistsError,
    PackageRequest,
    ProjectSettings,
    Ratio,
    build_timeline_clips,
    package_openshot_project,
)
from tests.fixtures import create_story_project

if typ.TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion


def test_build_timeline_clips_uses_cumulative_positions(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Timeline positions are computed from ordered clip durations."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)

    clips = build_timeline_clips(_request(tmp_path))

    assert [clip.shot_id for clip in clips] == ["S01_SH001", "S01_SH002", "S01_SH003"]
    assert [str(clip.position_seconds) for clip in clips] == ["0", "2.5", "5.75"]


def test_missing_ffprobe_hard_stops_before_reading_inputs(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Packaging refuses to run without ffprobe reader metadata support."""
    monkeypatch.setattr("shutil.which", lambda _name: None)

    with pytest.raises(
        InputValidationError,
        match="ffprobe is required to populate OpenShot FFmpegReader metadata",
    ):
        package_openshot_project(_request(tmp_path))


def test_missing_media_fails_with_shot_and_path(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing selected media path is rejected before output is written."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
    missing_path = tmp_path / "generated" / "clips" / "s01_sh002_take1.mp4"
    missing_path.unlink()

    with pytest.raises(
        InputValidationError,
        match=r"Missing media for shot S01_SH002: generated/clips/s01_sh002_take1.mp4",
    ):
        package_openshot_project(_request(tmp_path))


def test_unaccepted_review_state_fails(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Required shots must be accepted, approved, final, or selected."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
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


def test_duplicate_generation_log_rows_fail(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A selected clip must bind to exactly one generation log row."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
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


def test_selected_clip_parent_traversal_fails(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Selected clip metadata cannot point outside the project root."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
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


def test_output_requires_force_to_overwrite(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The packaging command does not overwrite existing outputs by default."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
    output = tmp_path / "generated" / "media-project" / "story.osp"
    output.parent.mkdir(parents=True)
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(OutputExistsError, match=f"Output already exists: {output}"):
        package_openshot_project(_request(tmp_path))


def test_project_and_sidecar_json_match_snapshot(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    snapshot: SnapshotAssertion,
) -> None:
    """Project and sidecar JSON remain deterministic for the fixture."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
    request = _request(tmp_path)

    package_openshot_project(request)

    payload = {
        "openshot": _openshot_summary(msjson.decode(request.output.read_bytes())),
        "sidecar": msjson.decode(request.sidecar.read_bytes()),
    }
    assert payload == snapshot


def test_openshot_asset_paths_are_relative_to_project_file(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OpenShot asset paths are relative to the saved .osp location."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
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


def test_openshot_project_uses_full_reader_and_keyframe_shapes(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generated OpenShot JSON contains playback-ready reader metadata."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
    request = _request(tmp_path)

    package_openshot_project(request)

    project = msjson.decode(request.output.read_bytes())
    first_file = project["files"][0]
    first_clip = project["clips"][0]
    assert first_file["type"] == "FFmpegReader"
    assert first_file["duration_strategy"] == "VideoPreferred"
    assert first_file["path"] == "../clips/s01_sh001_take2.mp4"
    assert first_clip["reader"]["type"] == "FFmpegReader"
    assert first_clip["reader"]["id"] == first_clip["file_id"]
    assert first_clip["gravity"] == 4
    assert first_clip["scale"] == 1
    assert first_clip["layer"] == 1_000_000
    assert project["layers"][0]["number"] == 1_000_000
    assert first_clip["alpha"]["Points"][0]["co"] == {"X": 1.0, "Y": 1.0}
    assert first_clip["volume"]["Points"][0]["co"] == {"X": 1.0, "Y": 0.0}
    assert project["width"] == 1920
    assert project["height"] == 1080


def test_assembly_order_alias_columns_are_supported(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Older assembly-order column names remain accepted during transition."""
    create_story_project(tmp_path)
    _stub_probe(monkeypatch)
    assembly_path = tmp_path / "generated" / "assembly_order.md"
    assembly_path.write_text(
        assembly_path
        .read_text(encoding="utf-8")
        .replace("Selected clip", "File")
        .replace("Boundary after", "Boundary (next)"),
        encoding="utf-8",
    )
    request = _request(tmp_path)

    package_openshot_project(request)

    project = msjson.decode(request.output.read_bytes())
    assert project["clips"][1]["metadata"]["clip_boundary"] == "dissolve"


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


def _openshot_summary(project: dict[str, typ.Any]) -> dict[str, typ.Any]:
    return {
        "height": project["height"],
        "id": project["id"],
        "width": project["width"],
        "layers": project["layers"],
        "files": [
            {
                "duration": file_entry["duration"],
                "id": file_entry["id"],
                "path": file_entry["path"],
                "type": file_entry["type"],
            }
            for file_entry in project["files"]
        ],
        "clips": [
            {
                "duration": clip["duration"],
                "file_id": clip["file_id"],
                "gravity": clip["gravity"],
                "id": clip["id"],
                "layer": clip["layer"],
                "metadata": clip["metadata"],
                "position": clip["position"],
                "reader_type": clip["reader"]["type"],
                "scale": clip["scale"],
                "volume": clip["volume"]["Points"][0]["co"]["Y"],
            }
            for clip in project["clips"]
        ],
    }


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


def _stub_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "media_project.openshot_project._require_ffprobe",
        lambda: pathlib.Path("/usr/bin/ffprobe"),
    )
    monkeypatch.setattr("media_project.openshot_project._probe_media", _fake_probe)


def _fake_probe(
    _ffprobe_path: pathlib.Path,
    _source_clip_path: pathlib.Path,
    project_clip_path: pathlib.PurePosixPath,
    _shot_id: str,
) -> MediaProbe:
    durations = {
        "s01_sh001_take2.mp4": "2.5",
        "s01_sh002_take1.mp4": "3.25",
        "s01_sh003_take3.mp4": "1.75",
    }
    duration = durations[project_clip_path.name]
    return MediaProbe(
        path=project_clip_path,
        duration=decimal.Decimal(duration),
        file_size=10240,
        fps=Ratio(num=24, den=1),
        width=1920,
        height=1080,
        display_ratio=Ratio(num=16, den=9),
        pixel_format=0,
        pixel_ratio=Ratio(num=1, den=1),
        video_length=int(decimal.Decimal(duration) * 24),
        vcodec="h264",
        video_stream_index=0,
        video_timebase=Ratio(num=1, den=12288),
        video_bit_rate=8_000_000,
        has_audio=True,
        acodec="aac",
        audio_stream_index=1,
        audio_timebase=Ratio(num=1, den=44100),
        audio_bit_rate=128_000,
        sample_rate=44100,
        channels=2,
        channel_layout=3,
        metadata={"major_brand": "isom"},
    )
