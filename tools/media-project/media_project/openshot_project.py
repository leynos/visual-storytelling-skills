"""Build deterministic OpenShot project files from generated media metadata."""

from __future__ import annotations

import dataclasses as dc
import decimal
import hashlib
import itertools
import os
import pathlib
import typing as typ

import msgspec.json as msjson

from media_project.markdown_tables import read_first_table

type JsonValue = (
    bool | int | float | str | list[JsonValue] | dict[str, JsonValue] | None
)

ACCEPTED_REVIEW_STATES = frozenset({"accepted", "approved", "final", "selected"})
COMPLETED_STATUSES = frozenset({"complete", "completed", "success", "succeeded"})
DEFAULT_CHANNEL_LAYOUT = 3
DEFAULT_TRACK_LAYER = 1


class MediaProjectError(Exception):
    """Base exception for media-project packaging failures."""


class InputValidationError(MediaProjectError):
    """Raised when source generation metadata is incomplete or unsafe."""


class OutputExistsError(MediaProjectError):
    """Raised when the output path exists and overwrite was not allowed."""


@dc.dataclass(frozen=True)
class ProjectSettings:
    """OpenShot timeline settings used for generated project JSON."""

    width: int = 1344
    height: int = 768
    fps_num: int = 24
    fps_den: int = 1
    sample_rate: int = 44100
    channels: int = 2
    channel_layout: int = DEFAULT_CHANNEL_LAYOUT


@dc.dataclass(frozen=True)
class PackageRequest:
    """Input and output paths for one OpenShot packaging run."""

    project_root: pathlib.Path
    assembly_order: pathlib.Path
    generation_log: pathlib.Path
    output: pathlib.Path
    sidecar: pathlib.Path
    source_manifest: pathlib.Path | None
    project_name: str
    force: bool
    settings: ProjectSettings


@dc.dataclass(frozen=True)
class TimelineClip:
    """A selected generated clip placed on the OpenShot timeline."""

    shot_id: str
    scene_id: str
    subclip_id: str
    order_index: int
    source_clip_path: pathlib.Path
    source_clip_project_path: pathlib.PurePosixPath
    project_clip_path: pathlib.PurePosixPath
    take_id: str
    duration_seconds: decimal.Decimal
    position_seconds: decimal.Decimal
    transition_type: str
    transition_duration: decimal.Decimal
    transition_description: str
    clip_boundary: str
    review_state: str
    status: str
    mute_generated_audio: bool
    forced_generated_audio: bool
    recommended_model: str
    job_ids: list[str]
    actual_file_size: str
    actual_resolution: str
    prompt_hash: str
    prompt_file: str
    continuity_flags: list[str]
    notes: str


def package_openshot_project(request: PackageRequest) -> None:
    """Write deterministic OpenShot project and sidecar JSON files."""
    if request.output.exists() and not request.force:
        msg = f"Output already exists: {request.output}"
        raise OutputExistsError(msg)
    if request.sidecar.exists() and not request.force:
        msg = f"Sidecar already exists: {request.sidecar}"
        raise OutputExistsError(msg)

    clips = build_timeline_clips(request)
    project_id = _project_id(request.project_name, clips)
    project = _openshot_project(project_id, request, clips)
    sidecar = _sidecar_metadata(project_id, request, clips)
    _write_json(request.output, project)
    _write_json(request.sidecar, sidecar)


def build_timeline_clips(request: PackageRequest) -> list[TimelineClip]:
    """Parse inputs, validate selected media, and compute clip positions."""
    assembly_rows = _read_table(request.project_root / request.assembly_order)
    generation_rows = _read_table(request.project_root / request.generation_log)

    clips: list[TimelineClip] = []
    position = decimal.Decimal(0)
    for assembly_row in sorted(assembly_rows, key=_order_value):
        log_row = _matching_generation_row(assembly_row, generation_rows)
        clip = _timeline_clip(request, assembly_row, log_row, position)
        clips.append(clip)
        position += clip.duration_seconds
    return clips


def _read_table(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        msg = f"Required metadata file does not exist: {path}"
        raise InputValidationError(msg)
    return read_first_table(path.read_text(encoding="utf-8"))


def _order_value(row: dict[str, str]) -> int:
    value = row.get("order", "")
    try:
        return int(value)
    except ValueError as exc:
        msg = f"Invalid assembly order value: {value!r}"
        raise InputValidationError(msg) from exc


def _matching_generation_row(
    assembly_row: dict[str, str],
    generation_rows: list[dict[str, str]],
) -> dict[str, str]:
    shot_id = _required(assembly_row, "shot_id")
    subclip_id = _required(assembly_row, "sub_clip")
    selected_clip = _required(assembly_row, "selected_clip")
    matches = [
        row
        for row in generation_rows
        if row.get("shot_id") == shot_id
        and row.get("sub_clip") == subclip_id
        and _same_clip(row.get("local_file", ""), selected_clip)
    ]
    if not matches:
        msg = f"No generation log row matches shot {shot_id} clip {selected_clip}."
        raise InputValidationError(msg)
    return matches[0]


def _timeline_clip(
    request: PackageRequest,
    assembly_row: dict[str, str],
    log_row: dict[str, str],
    position: decimal.Decimal,
) -> TimelineClip:
    shot_id = _required(assembly_row, "shot_id")
    selected_clip = pathlib.Path(_required(assembly_row, "selected_clip"))
    source_clip_path = request.project_root / selected_clip
    if not source_clip_path.exists():
        msg = f"Missing media for shot {shot_id}: {selected_clip}"
        raise InputValidationError(msg)

    review_state = _normalise_state(log_row.get("review", ""))
    if review_state not in ACCEPTED_REVIEW_STATES:
        msg = f"Shot {shot_id} has unaccepted review state: {review_state or '<empty>'}"
        raise InputValidationError(msg)

    status = _normalise_state(log_row.get("status", ""))
    if status not in COMPLETED_STATUSES:
        msg = f"Shot {shot_id} has incomplete generation status: {status or '<empty>'}"
        raise InputValidationError(msg)

    duration_seconds = _required_decimal(log_row, "duration_seconds", shot_id)
    return TimelineClip(
        shot_id=shot_id,
        scene_id=log_row.get("scene_id", ""),
        subclip_id=_required(assembly_row, "sub_clip"),
        order_index=_order_value(assembly_row),
        source_clip_path=source_clip_path,
        source_clip_project_path=pathlib.PurePosixPath(selected_clip.as_posix()),
        project_clip_path=_path_relative_to_output(source_clip_path, request.output),
        take_id=log_row.get("take", ""),
        duration_seconds=duration_seconds,
        position_seconds=position,
        transition_type=_transition_type(assembly_row, log_row),
        transition_duration=_optional_decimal(log_row.get("transition_duration")),
        transition_description=assembly_row.get("notes", "")
        or log_row.get("notes", ""),
        clip_boundary=assembly_row.get("boundary_after", ""),
        review_state=review_state,
        status=status,
        mute_generated_audio=_bool_value(log_row.get("mute_generated_audio", "")),
        forced_generated_audio=_bool_value(log_row.get("forced_generated_audio", "")),
        recommended_model=log_row.get("model", ""),
        job_ids=_split_values(log_row.get("job_id", "")),
        actual_file_size=log_row.get("file_size", ""),
        actual_resolution=log_row.get("actual_resolution", ""),
        prompt_hash=log_row.get("prompt_hash", ""),
        prompt_file=log_row.get("prompt_file", ""),
        continuity_flags=_split_values(log_row.get("continuity_flags", "")),
        notes=log_row.get("notes", ""),
    )


def _openshot_project(
    project_id: str,
    request: PackageRequest,
    clips: list[TimelineClip],
) -> dict[str, JsonValue]:
    return {
        "channels": request.settings.channels,
        "channel_layout": request.settings.channel_layout,
        "clips": list(itertools.starmap(_openshot_clip, enumerate(clips, 1))),
        "effects": [],
        "exports": [],
        "files": list(itertools.starmap(_openshot_file, enumerate(clips, 1))),
        "fps_den": request.settings.fps_den,
        "fps_num": request.settings.fps_num,
        "height": request.settings.height,
        "id": project_id,
        "markers": [],
        "metadata": {
            "generator": "media-project",
            "project_name": request.project_name,
            "source_assembly_order": request.assembly_order.as_posix(),
            "source_generation_log": request.generation_log.as_posix(),
            "source_manifest": _optional_path(request.source_manifest),
        },
        "sample_rate": request.settings.sample_rate,
        "version": {
            "format": "openshot-json",
            "media_project": "0.1.0",
        },
        "width": request.settings.width,
    }


def _openshot_file(index: int, clip: TimelineClip) -> dict[str, JsonValue]:
    return {
        "duration": _json_number(clip.duration_seconds),
        "id": _stable_id("file", index),
        "media_type": "video",
        "path": clip.project_clip_path.as_posix(),
    }


def _openshot_clip(index: int, clip: TimelineClip) -> dict[str, JsonValue]:
    duration = _json_number(clip.duration_seconds)
    return {
        "alpha": 1.0,
        "duration": duration,
        "end": duration,
        "file_id": _stable_id("file", index),
        "filepath": clip.project_clip_path.as_posix(),
        "gravity": "center",
        "id": _stable_id("clip", index),
        "layer": DEFAULT_TRACK_LAYER,
        "metadata": {
            "clip_boundary": clip.clip_boundary,
            "review_state": clip.review_state,
            "shot_id": clip.shot_id,
            "transition_after": clip.transition_type,
            "transition_description": clip.transition_description,
        },
        "position": _json_number(clip.position_seconds),
        "scale": "fit",
        "start": 0.0,
        "volume": 0.0 if clip.mute_generated_audio else 1.0,
    }


def _sidecar_metadata(
    project_id: str,
    request: PackageRequest,
    clips: list[TimelineClip],
) -> dict[str, JsonValue]:
    return {
        "project_id": project_id,
        "project_name": request.project_name,
        "source_assembly_order": request.assembly_order.as_posix(),
        "source_generation_log": request.generation_log.as_posix(),
        "source_manifest": _optional_path(request.source_manifest),
        "clips": [_sidecar_clip(clip) for clip in clips],
    }


def _sidecar_clip(clip: TimelineClip) -> dict[str, JsonValue]:
    return typ.cast(
        "dict[str, JsonValue]",
        {
            "actual_file_size": clip.actual_file_size,
            "actual_resolution": clip.actual_resolution,
            "audio_generation_prefs": {
                "forced_generated_audio": clip.forced_generated_audio,
                "mute_generated_audio": clip.mute_generated_audio,
            },
            "baked_frame_refs": [],
            "clip_boundary": clip.clip_boundary,
            "continuity_flags": clip.continuity_flags,
            "duration_seconds_effective": _decimal_string(clip.duration_seconds),
            "end_frame_path": "",
            "generation_strategy": "",
            "job_ids": clip.job_ids,
            "order_index": clip.order_index,
            "position_seconds": _decimal_string(clip.position_seconds),
            "prompt_file": clip.prompt_file,
            "prompt_hash": clip.prompt_hash,
            "recommended_model": clip.recommended_model,
            "required_refs": [],
            "review_state": clip.review_state,
            "scene_id": clip.scene_id,
            "shot_id": clip.shot_id,
            "source_clip_path": clip.source_clip_project_path.as_posix(),
            "start_frame_path": "",
            "subclip_id": clip.subclip_id,
            "take_id": clip.take_id,
            "transition_description": clip.transition_description,
            "transition_duration": _decimal_string(clip.transition_duration),
            "transition_type": clip.transition_type,
        },
    )


def _write_json(path: pathlib.Path, payload: dict[str, JsonValue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(msjson.encode(payload, order="deterministic") + b"\n")


def _required(row: dict[str, str], name: str) -> str:
    value = row.get(name, "").strip()
    if not value:
        msg = f"Required metadata field is empty: {name}"
        raise InputValidationError(msg)
    return value


def _required_decimal(
    row: dict[str, str],
    name: str,
    shot_id: str,
) -> decimal.Decimal:
    value = row.get(name, "")
    if not value:
        msg = f"Shot {shot_id} is missing duration_seconds metadata."
        raise InputValidationError(msg)
    return _decimal_value(value, f"Shot {shot_id} has invalid duration_seconds")


def _optional_decimal(value: str | None) -> decimal.Decimal:
    if not value:
        return decimal.Decimal(0)
    return _decimal_value(value, "Invalid transition duration")


def _decimal_value(value: str, message: str) -> decimal.Decimal:
    try:
        parsed = decimal.Decimal(value)
    except decimal.InvalidOperation as exc:
        raise InputValidationError(message) from exc
    if parsed < decimal.Decimal(0):
        msg = f"{message}: {value}"
        raise InputValidationError(msg)
    return parsed


def _decimal_string(value: decimal.Decimal) -> str:
    return format(value.normalize(), "f")


def _json_number(value: decimal.Decimal) -> float:
    return float(value)


def _same_clip(log_clip: str, selected_clip: str) -> bool:
    return (
        pathlib.PurePosixPath(log_clip).as_posix()
        == pathlib.PurePosixPath(
            selected_clip,
        ).as_posix()
    )


def _path_relative_to_output(
    source_clip_path: pathlib.Path,
    output_path: pathlib.Path,
) -> pathlib.PurePosixPath:
    relative_path = os.path.relpath(source_clip_path, output_path.parent)
    return pathlib.PurePosixPath(pathlib.Path(relative_path).as_posix())


def _normalise_state(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _transition_type(
    assembly_row: dict[str, str],
    log_row: dict[str, str],
) -> str:
    value = log_row.get("transition_type", "") or assembly_row.get("boundary_after", "")
    transition = _normalise_state(value)
    if transition in {"", "hard_cut", "cut"}:
        return "cut"
    if transition in {"dissolve", "cross_dissolve", "fade"}:
        return "dissolve"
    return transition


def _bool_value(value: str) -> bool:
    return _normalise_state(value) in {"1", "true", "yes", "y", "on"}


def _split_values(value: str) -> list[str]:
    return [item.strip() for item in re_split_commas(value) if item.strip()]


def re_split_commas(value: str) -> list[str]:
    """Split comma and semicolon separated metadata values."""
    return value.replace(";", ",").split(",")


def _stable_id(prefix: str, index: int) -> str:
    return f"{prefix}-{index:03d}"


def _project_id(project_name: str, clips: list[TimelineClip]) -> str:
    digest = hashlib.sha256()
    digest.update(project_name.encode())
    for clip in clips:
        digest.update(clip.shot_id.encode())
        digest.update(clip.source_clip_project_path.as_posix().encode())
    return digest.hexdigest()[:16]


def _optional_path(path: pathlib.Path | None) -> str:
    if path is None:
        return ""
    return path.as_posix()
