---
name: media-project
description: Package completed visual storytelling video outputs into OpenShot editor projects with the system-installed media-project command. Use when an agent needs to run or verify a playable .osp handoff, preserve production sidecar metadata, or decide whether a project is ready for OpenShot packaging.
---

# Media-project OpenShot handoff

Use this skill when packaging selected generated clips into an OpenShot project
with the `media-project` command. The command is expected to be installed at
the system tool level before this skill is used, normally with `uv tool
install`.

Do not assume the story project contains the `media-project` source tree. The
story project normally contains only generated media, metadata, prompts, and
editor handoff outputs.

## Hard stop

Before running `media-project package-openshot`, verify both commands exist:

```bash
command -v media-project
command -v ffprobe
```

If `media-project` is absent, stop immediately and report that the command must
be installed system-wide with `uv tool install` before packaging can proceed.
Do not look for repository-local source directories or try to run the command
through a project checkout.

If `ffprobe` is absent, stop immediately. Do not run the packager, do not write
a minimal `.osp`, and do not tell the user the project is packaged. Report that
`ffprobe` is required because OpenShot playback depends on full FFmpeg reader
metadata in both `files[]` and `clips[].reader`.

## Inputs

Only package a project after `video-generator` has produced reviewed local
media and these project-root-relative files:

- `generated/assembly_order.md`
- `generated/generation_log.md`
- every selected local video file named by those tables

Preferred `generated/assembly_order.md` columns are:

| Column | Meaning |
| --- | --- |
| `Order` | Final timeline order. |
| `Shot ID` | Stable shot identifier. |
| `Sub-clip` | Sub-clip identifier. |
| `Selected clip` | Project-root-relative local video path. |
| `Boundary after` | Edit-boundary or transition intent after the clip. |
| `Notes` | Editor handoff notes. |

Some older assembly files may use `File` instead of `Selected clip` or
`Boundary (next)` instead of `Boundary after`. Treat those as compatibility
aliases only when the installed tool version documents support for them.

`Sub-clip` is mandatory even when a shot was not decomposed into separate
sub-clips. The packager matches assembly rows to generation-log rows using
`Shot ID`, `Sub-clip`, and the selected local file path, so the same non-empty
`Sub-clip` value must appear in both tables. For non-decomposed shots, use `-`
as the placeholder in both `generated/assembly_order.md` and
`generated/generation_log.md`; do not leave the cell blank or omit the column.

`generated/generation_log.md` must identify the same selected files and include
completed statuses, accepted review states, duration metadata, model/job
metadata, actual file size, actual resolution, prompt hash, and audio mute
intent. Do not package blocked, missing, incomplete, or unreviewed required
clips.

## Command

Run the already installed command from the story project repository or from any
working directory where project-root paths are clear:

```bash
media-project package-openshot \
  --project-root /path/to/story-project \
  --assembly-order generated/assembly_order.md \
  --generation-log generated/generation_log.md \
  --manifest prompts/manifest.md \
  --output generated/media-project/project.osp \
  --sidecar generated/media-project/media-project.json
```

The command refuses to overwrite existing outputs unless `--force` is passed.
Use `--force` only when replacing the generated `.osp` and sidecar is
intentional.

## Expected `.osp` shape

A playable OpenShot handoff needs full FFmpeg reader metadata. Check generated
projects for these invariants:

- `files[]` entries are full `FFmpegReader` objects, not minimal path records.
- Each `clips[]` entry has a `reader` object with the same media metadata as
  its matching file entry.
- `reader.type` is `FFmpegReader`.
- `reader.duration_strategy` is `VideoPreferred`.
- Reader metadata includes codecs, stream indexes, bit rates, time bases,
  frame count, file size, duration, frame rate, dimensions, display ratio,
  sample rate, channel data, pixel data, and container metadata.
- Clip `gravity` is integer `4`, and clip `scale` is integer `1`.
- Clip `layer` matches an OpenShot layer number such as `1000000`, and the
  project has a matching `layers[]` entry.
- Clip properties such as `alpha`, `volume`, `time`, transforms, audio/video
  flags, and waveform colour are OpenShot keyframe curve objects with
  `Points`, not scalar values.

The sidecar JSON remains the production provenance record. Preserve transition
intent there and in clip metadata; do not invent OpenShot transition effects
unless the tool version explicitly supports them with a verified reference
shape.

## Verification

After packaging, inspect the generated project before handing it off:

```bash
jq '.files[0].type, .clips[0].reader.type, .clips[0].gravity, .clips[0].scale, .clips[0].layer' \
  /path/to/story-project/generated/media-project/project.osp
```

Expected values are:

```plaintext
"FFmpegReader"
"FFmpegReader"
4
1
1000000
```

When OpenShot is available, perform a manual smoke test: open the `.osp`, press
play on the timeline, and verify that at least the first selected clip decodes
and plays rather than merely appearing as a timeline block. If OpenShot is not
available in the current environment, report that the manual smoke test was not
run.
