"""Build deterministic OpenShot project files from generated media metadata."""

from __future__ import annotations

import dataclasses as dc
import decimal
import hashlib
import itertools
import os
import pathlib
import shutil
import subprocess  # noqa: S404 - ffprobe path is resolved before invocation.
import typing as typ

import msgspec
import msgspec.json as msjson

from media_project.markdown_tables import read_first_table

type JsonValue = (
    bool | int | float | str | list[JsonValue] | dict[str, JsonValue] | None
)

ACCEPTED_REVIEW_STATES = frozenset({"accepted", "approved", "final", "selected"})
COMPLETED_STATUSES = frozenset({"complete", "completed", "success", "succeeded"})
DEFAULT_CHANNEL_LAYOUT = 3
DEFAULT_TRACK_LAYER = 1_000_000
OPENSHOT_GRAVITY_CENTER = 4
OPENSHOT_SCALE_BEST_FIT = 1
OPENSHOT_QT_PROJECT_VERSION = "3.3.0"
LIBOPENSHOT_PROJECT_VERSION = "0.4.0"
PIXEL_FORMATS = {
    "yuv420p": 0,
}


class MediaProjectError(Exception):
    """Base exception for media-project packaging failures."""


class InputValidationError(MediaProjectError):
    """Raised when source generation metadata is incomplete or unsafe."""


class OutputExistsError(MediaProjectError):
    """Raised when the output path exists and overwrite was not allowed."""


@dc.dataclass(frozen=True)
class ProjectSettings:
    """OpenShot timeline settings used for generated project JSON."""

    width: int = 1920
    height: int = 1080
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
    media: MediaProbe


@dc.dataclass(frozen=True)
class Ratio:
    """A libopenshot-style rational value."""

    num: int
    den: int


@dc.dataclass(frozen=True)
class MediaProbe:
    """Media metadata required to initialise OpenShot's FFmpegReader."""

    path: pathlib.PurePosixPath
    duration: decimal.Decimal
    file_size: int
    fps: Ratio
    width: int
    height: int
    display_ratio: Ratio
    pixel_format: int
    pixel_ratio: Ratio
    video_length: int
    vcodec: str
    video_stream_index: int
    video_timebase: Ratio
    video_bit_rate: int
    has_audio: bool
    acodec: str
    audio_stream_index: int
    audio_timebase: Ratio
    audio_bit_rate: int
    sample_rate: int
    channels: int
    channel_layout: int
    metadata: dict[str, str]


@dc.dataclass(frozen=True)
class TimelineBuildContext:
    """Per-clip packaging context that is not part of source metadata."""

    position: decimal.Decimal
    ffprobe_path: pathlib.Path


def package_openshot_project(request: PackageRequest) -> None:
    """Write deterministic OpenShot project and sidecar JSON files."""
    ffprobe_path = _require_ffprobe()
    if request.output.exists() and not request.force:
        msg = f"Output already exists: {request.output}"
        raise OutputExistsError(msg)
    if request.sidecar.exists() and not request.force:
        msg = f"Sidecar already exists: {request.sidecar}"
        raise OutputExistsError(msg)

    clips = build_timeline_clips(request, ffprobe_path=ffprobe_path)
    project_id = _project_id(request.project_name, clips)
    project = _openshot_project(project_id, request, clips)
    sidecar = _sidecar_metadata(project_id, request, clips)
    _write_json(request.output, project)
    _write_json(request.sidecar, sidecar)


def build_timeline_clips(
    request: PackageRequest,
    *,
    ffprobe_path: pathlib.Path | None = None,
) -> list[TimelineClip]:
    """Parse inputs, validate selected media, and compute clip positions."""
    resolved_ffprobe_path = ffprobe_path or _require_ffprobe()
    assembly_rows = _read_table(request.project_root / request.assembly_order)
    generation_rows = _read_table(request.project_root / request.generation_log)

    clips: list[TimelineClip] = []
    position = decimal.Decimal(0)
    for assembly_row in sorted(assembly_rows, key=_order_value):
        log_row = _matching_generation_row(assembly_row, generation_rows)
        clip = _timeline_clip(
            request,
            assembly_row,
            log_row,
            TimelineBuildContext(
                position=position,
                ffprobe_path=resolved_ffprobe_path,
            ),
        )
        clips.append(clip)
        position += clip.duration_seconds
    return clips


def _require_ffprobe() -> pathlib.Path:
    executable = shutil.which("ffprobe")
    if executable is None:
        msg = (
            "ffprobe is required to populate OpenShot FFmpegReader metadata; "
            "install ffprobe before running media-project package-openshot."
        )
        raise InputValidationError(msg)
    return pathlib.Path(executable)


def _read_table(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        msg = f"Required metadata file does not exist: {path}"
        raise InputValidationError(msg)
    return read_first_table(path.read_text(encoding="utf-8"))


def _selected_clip_value(row: dict[str, str]) -> str:
    return _required_alias(row, ("selected_clip", "file"), "selected_clip")


def _boundary_after_value(row: dict[str, str]) -> str:
    return row.get("boundary_after", "") or row.get("boundary_next", "")


def _required_alias(
    row: dict[str, str],
    names: tuple[str, ...],
    preferred_name: str,
) -> str:
    for name in names:
        value = row.get(name, "").strip()
        if value:
            return value
    msg = f"Required metadata field is empty: {preferred_name}"
    raise InputValidationError(msg)


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
    selected_clip = _selected_clip_value(assembly_row)
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
    if len(matches) > 1:
        msg = (
            f"Multiple generation log rows match shot {shot_id} "
            f"sub-clip {subclip_id} clip {selected_clip}."
        )
        raise InputValidationError(msg)
    return matches[0]


def _timeline_clip(
    request: PackageRequest,
    assembly_row: dict[str, str],
    log_row: dict[str, str],
    context: TimelineBuildContext,
) -> TimelineClip:
    shot_id = _required(assembly_row, "shot_id")
    selected_clip = pathlib.Path(_selected_clip_value(assembly_row))
    if selected_clip.is_absolute() or ".." in selected_clip.parts:
        msg = (
            f"Selected clip path for shot {shot_id} must stay inside the "
            f"project: {selected_clip}"
        )
        raise InputValidationError(msg)

    project_root_resolved = request.project_root.resolve()
    source_clip_path = (request.project_root / selected_clip).resolve()
    if project_root_resolved not in source_clip_path.parents:
        msg = (
            f"Selected clip path for shot {shot_id} escapes the project root: "
            f"{selected_clip}"
        )
        raise InputValidationError(msg)
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

    _required_decimal(log_row, "duration_seconds", shot_id)
    media = _probe_media(
        context.ffprobe_path,
        source_clip_path,
        _path_relative_to_output(source_clip_path, request.output),
        shot_id,
    )
    return TimelineClip(
        shot_id=shot_id,
        scene_id=log_row.get("scene_id", ""),
        subclip_id=_required(assembly_row, "sub_clip"),
        order_index=_order_value(assembly_row),
        source_clip_path=source_clip_path,
        source_clip_project_path=pathlib.PurePosixPath(selected_clip.as_posix()),
        project_clip_path=_path_relative_to_output(source_clip_path, request.output),
        take_id=log_row.get("take", ""),
        duration_seconds=media.duration,
        position_seconds=context.position,
        transition_type=_transition_type(assembly_row, log_row),
        transition_duration=_optional_decimal(log_row.get("transition_duration")),
        transition_description=assembly_row.get("notes", "")
        or log_row.get("notes", ""),
        clip_boundary=_boundary_after_value(assembly_row),
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
        media=media,
    )


def _probe_media(
    ffprobe_path: pathlib.Path,
    source_clip_path: pathlib.Path,
    project_clip_path: pathlib.PurePosixPath,
    shot_id: str,
) -> MediaProbe:
    command = [
        str(ffprobe_path),
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(source_clip_path),
    ]
    try:
        result = subprocess.run(  # noqa: S603 - executable is resolved by shutil.which.
            command,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.decode(errors="replace").strip()
        suffix = f": {details}" if details else ""
        msg = f"ffprobe failed for shot {shot_id} media {source_clip_path}{suffix}"
        raise InputValidationError(msg) from exc

    try:
        payload = typ.cast("dict[str, JsonValue]", msjson.decode(result.stdout))
    except msgspec.DecodeError as exc:
        msg = f"ffprobe returned invalid JSON for shot {shot_id}: {source_clip_path}"
        raise InputValidationError(msg) from exc

    return _media_probe_from_payload(
        payload, project_clip_path, source_clip_path, shot_id
    )


def _media_probe_from_payload(
    payload: dict[str, JsonValue],
    project_clip_path: pathlib.PurePosixPath,
    source_clip_path: pathlib.Path,
    shot_id: str,
) -> MediaProbe:
    streams = _list_of_dicts(payload.get("streams"))
    format_data = _dict_value(payload.get("format"))
    video_stream = _first_stream(streams, "video", shot_id)
    audio_stream = _optional_stream(streams, "audio")
    width = _required_int(video_stream, "width", shot_id)
    height = _required_int(video_stream, "height", shot_id)
    duration = _decimal_from_streams(video_stream, format_data, shot_id)
    fps = _ratio_from_text(_required_text(video_stream, "r_frame_rate", shot_id))
    video_length = _optional_int(video_stream.get("nb_frames")) or _frame_count(
        duration,
        fps,
    )
    return MediaProbe(
        path=project_clip_path,
        duration=duration,
        file_size=_optional_int(format_data.get("size"))
        or source_clip_path.stat().st_size,
        fps=fps,
        width=width,
        height=height,
        display_ratio=_aspect_ratio(width, height),
        pixel_format=_pixel_format(_required_text(video_stream, "pix_fmt", shot_id)),
        pixel_ratio=_ratio_from_text(
            str(video_stream.get("sample_aspect_ratio") or "1:1")
        ),
        video_length=video_length,
        vcodec=_required_text(video_stream, "codec_name", shot_id),
        video_stream_index=_required_int(video_stream, "index", shot_id),
        video_timebase=_ratio_from_text(
            _required_text(video_stream, "time_base", shot_id)
        ),
        video_bit_rate=_bit_rate(video_stream, format_data),
        has_audio=audio_stream is not None,
        acodec=_optional_text(audio_stream, "codec_name") if audio_stream else "",
        audio_stream_index=_optional_audio_int(audio_stream, "index", default=-1),
        audio_timebase=_ratio_from_text(
            _optional_text(audio_stream, "time_base") or "1/1",
        ),
        audio_bit_rate=_bit_rate(audio_stream, format_data) if audio_stream else 0,
        sample_rate=_optional_audio_int(audio_stream, "sample_rate"),
        channels=_optional_audio_int(audio_stream, "channels"),
        channel_layout=_channel_layout(audio_stream),
        metadata=_metadata(format_data, video_stream, audio_stream),
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
        "display_ratio": {"den": 9, "num": 16},
        "duration": _json_number(
            sum((clip.duration_seconds for clip in clips), decimal.Decimal(0))
        ),
        "effects": [],
        "export_settings": None,
        "exports": [],
        "files": list(itertools.starmap(_openshot_file, enumerate(clips, 1))),
        "fps": {
            "den": request.settings.fps_den,
            "num": request.settings.fps_num,
        },
        "fps_den": request.settings.fps_den,
        "fps_num": request.settings.fps_num,
        "history": {"redo": [], "undo": []},
        "height": request.settings.height,
        "id": project_id,
        "layers": [_openshot_layer()],
        "markers": [],
        "metadata": {
            "generator": "media-project",
            "project_name": request.project_name,
            "source_assembly_order": request.assembly_order.as_posix(),
            "source_generation_log": request.generation_log.as_posix(),
            "source_manifest": _optional_path(request.source_manifest),
        },
        "pixel_ratio": {"den": 1, "num": 1},
        "playhead_position": 0,
        "profile": _profile_name(request.settings),
        "progress": [],
        "sample_rate": request.settings.sample_rate,
        "scale": 15.0,
        "settings": {},
        "tick_pixels": 100,
        "version": {
            "libopenshot": LIBOPENSHOT_PROJECT_VERSION,
            "openshot-qt": OPENSHOT_QT_PROJECT_VERSION,
        },
        "width": request.settings.width,
    }


def _profile_name(settings: ProjectSettings) -> str:
    return f"HD {settings.height}p {settings.fps_num} fps"


def _openshot_file(index: int, clip: TimelineClip) -> dict[str, JsonValue]:
    return _openshot_reader(_stable_id("file", index), clip.media, image="")


def _openshot_clip(index: int, clip: TimelineClip) -> dict[str, JsonValue]:
    duration = _json_number(clip.duration_seconds)
    file_id = _stable_id("file", index)
    volume = 0.0 if clip.mute_generated_audio else 1.0
    return {
        "alpha": _keyframe(1.0),
        "anchor": 0,
        "channel_filter": _keyframe(-1.0),
        "channel_mapping": _keyframe(-1.0),
        "composite": 0,
        "display": 0,
        "duration": duration,
        "effects": [],
        "end": duration,
        "file_id": file_id,
        "filepath": clip.project_clip_path.as_posix(),
        "gravity": OPENSHOT_GRAVITY_CENTER,
        "has_audio": _keyframe(-1.0 if clip.media.has_audio else 0.0),
        "has_video": _keyframe(-1.0),
        "id": _stable_id("clip", index),
        "layer": DEFAULT_TRACK_LAYER,
        "location_x": _keyframe(0.0),
        "location_y": _keyframe(0.0),
        "metadata": {
            "clip_boundary": clip.clip_boundary,
            "review_state": clip.review_state,
            "shot_id": clip.shot_id,
            "transition_after": clip.transition_type,
            "transition_description": clip.transition_description,
        },
        "mixing": 0,
        "origin_x": _keyframe(0.5),
        "origin_y": _keyframe(0.5),
        "parentObjectId": "",
        "perspective_c1_x": _keyframe(-1.0),
        "perspective_c1_y": _keyframe(-1.0),
        "perspective_c2_x": _keyframe(-1.0),
        "perspective_c2_y": _keyframe(-1.0),
        "perspective_c3_x": _keyframe(-1.0),
        "perspective_c3_y": _keyframe(-1.0),
        "perspective_c4_x": _keyframe(-1.0),
        "perspective_c4_y": _keyframe(-1.0),
        "position": _json_number(clip.position_seconds),
        "reader": _openshot_reader(file_id, clip.media),
        "rotation": _keyframe(0.0),
        "scale": OPENSHOT_SCALE_BEST_FIT,
        "scale_x": _keyframe(1.0),
        "scale_y": _keyframe(1.0),
        "shear_x": _keyframe(0.0),
        "shear_y": _keyframe(0.0),
        "start": 0.0,
        "time": _keyframe(1.0),
        "title": clip.source_clip_path.name,
        "volume": _keyframe(volume),
        "wave_color": _wave_color(),
        "waveform": False,
        "image": "",
    }


def _openshot_layer() -> dict[str, JsonValue]:
    return {
        "id": "L1",
        "label": "Generated Video",
        "lock": False,
        "number": DEFAULT_TRACK_LAYER,
        "y": 0,
    }


def _openshot_reader(
    reader_id: str,
    media: MediaProbe,
    *,
    image: str | None = None,
) -> dict[str, JsonValue]:
    reader = {
        "acodec": media.acodec,
        "audio_bit_rate": media.audio_bit_rate,
        "audio_stream_index": media.audio_stream_index,
        "audio_timebase": _ratio(media.audio_timebase),
        "channel_layout": media.channel_layout,
        "channels": media.channels,
        "display_ratio": _ratio(media.display_ratio),
        "duration": _json_number(media.duration),
        "duration_strategy": "VideoPreferred",
        "file_size": media.file_size,
        "fps": _ratio(media.fps),
        "has_audio": media.has_audio,
        "has_single_image": False,
        "has_video": True,
        "height": media.height,
        "id": reader_id,
        "interlaced_frame": False,
        "media_type": "video",
        "metadata": dict(sorted(media.metadata.items())),
        "path": media.path.as_posix(),
        "pixel_format": media.pixel_format,
        "pixel_ratio": _ratio(media.pixel_ratio),
        "sample_rate": media.sample_rate,
        "top_field_first": True,
        "type": "FFmpegReader",
        "vcodec": media.vcodec,
        "video_bit_rate": media.video_bit_rate,
        "video_length": media.video_length,
        "video_stream_index": media.video_stream_index,
        "video_timebase": _ratio(media.video_timebase),
        "width": media.width,
    }
    if image is not None:
        reader["image"] = image
    return typ.cast("dict[str, JsonValue]", reader)


def _keyframe(value: float) -> dict[str, JsonValue]:
    return {
        "Points": [
            {
                "co": {"X": 1.0, "Y": value},
                "handle_left": {"X": 0.5, "Y": 1.0},
                "handle_right": {"X": 0.5, "Y": 0.0},
                "handle_type": 0,
                "interpolation": 0,
            },
        ],
    }


def _wave_color() -> dict[str, JsonValue]:
    return {
        "alpha": _keyframe(255.0),
        "blue": _keyframe(255.0),
        "green": _keyframe(123.0),
        "red": _keyframe(0.0),
    }


def _ratio(value: Ratio) -> dict[str, JsonValue]:
    return {"den": value.den, "num": value.num}


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


def _list_of_dicts(value: JsonValue) -> list[dict[str, JsonValue]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _dict_value(value: JsonValue) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        return {}
    return value


def _first_stream(
    streams: list[dict[str, JsonValue]],
    codec_type: str,
    shot_id: str,
) -> dict[str, JsonValue]:
    stream = _optional_stream(streams, codec_type)
    if stream is None:
        msg = f"Shot {shot_id} media has no {codec_type} stream."
        raise InputValidationError(msg)
    return stream


def _optional_stream(
    streams: list[dict[str, JsonValue]],
    codec_type: str,
) -> dict[str, JsonValue] | None:
    return next(
        (
            stream
            for stream in streams
            if str(stream.get("codec_type", "")).lower() == codec_type
        ),
        None,
    )


def _required_text(row: dict[str, JsonValue], name: str, shot_id: str) -> str:
    value = row.get(name)
    if value is None or value == "":
        msg = f"Shot {shot_id} ffprobe metadata is missing {name}."
        raise InputValidationError(msg)
    return str(value)


def _optional_text(row: dict[str, JsonValue] | None, name: str) -> str:
    if row is None:
        return ""
    value = row.get(name)
    if value is None:
        return ""
    return str(value)


def _required_int(row: dict[str, JsonValue], name: str, shot_id: str) -> int:
    value = _optional_int(row.get(name))
    if value is None:
        msg = f"Shot {shot_id} ffprobe metadata has invalid {name}."
        raise InputValidationError(msg)
    return value


def _optional_int(value: JsonValue) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _optional_audio_int(
    audio_stream: dict[str, JsonValue] | None,
    name: str,
    *,
    default: int = 0,
) -> int:
    if audio_stream is None:
        return default
    return _optional_int(audio_stream.get(name)) or default


def _decimal_from_streams(
    video_stream: dict[str, JsonValue],
    format_data: dict[str, JsonValue],
    shot_id: str,
) -> decimal.Decimal:
    value = video_stream.get("duration") or format_data.get("duration")
    if value is None:
        msg = f"Shot {shot_id} ffprobe metadata is missing duration."
        raise InputValidationError(msg)
    return _decimal_value(str(value), f"Shot {shot_id} has invalid ffprobe duration")


def _ratio_from_text(value: str) -> Ratio:
    separator = "/" if "/" in value else ":"
    numerator_text, denominator_text = value.split(separator, maxsplit=1)
    numerator = int(numerator_text)
    denominator = int(denominator_text)
    if numerator <= 0 or denominator <= 0:
        msg = f"Invalid ffprobe ratio: {value}"
        raise InputValidationError(msg)
    return Ratio(num=numerator, den=denominator)


def _aspect_ratio(width: int, height: int) -> Ratio:
    divisor = _gcd(width, height)
    return Ratio(num=width // divisor, den=height // divisor)


def _gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return left


def _pixel_format(value: str) -> int:
    pixel_format = PIXEL_FORMATS.get(value)
    if pixel_format is None:
        msg = f"Unsupported ffprobe pixel format for OpenShot mapping: {value}"
        raise InputValidationError(msg)
    return pixel_format


def _bit_rate(
    stream: dict[str, JsonValue] | None,
    format_data: dict[str, JsonValue],
) -> int:
    if stream is None:
        return 0
    return (
        _optional_int(stream.get("bit_rate"))
        or _optional_int(format_data.get("bit_rate"))
        or 0
    )


def _frame_count(duration: decimal.Decimal, fps: Ratio) -> int:
    frames = duration * decimal.Decimal(fps.num) / decimal.Decimal(fps.den)
    return int(frames.to_integral_value(rounding=decimal.ROUND_HALF_UP))


def _channel_layout(audio_stream: dict[str, JsonValue] | None) -> int:
    if audio_stream is None:
        return 0
    layout = _optional_text(audio_stream, "channel_layout").lower()
    if layout == "stereo":
        return DEFAULT_CHANNEL_LAYOUT
    if layout == "mono":
        return 4
    return _optional_int(audio_stream.get("channel_layout")) or DEFAULT_CHANNEL_LAYOUT


def _metadata(
    format_data: dict[str, JsonValue],
    video_stream: dict[str, JsonValue],
    audio_stream: dict[str, JsonValue] | None,
) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for source in (
        _dict_value(format_data.get("tags")),
        _dict_value(video_stream.get("tags")),
        _dict_value(audio_stream.get("tags") if audio_stream else None),
    ):
        metadata.update({key: str(value) for key, value in source.items()})
    return metadata


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
    return [item.strip() for item in _split_commas(value) if item.strip()]


def _split_commas(value: str) -> list[str]:
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
