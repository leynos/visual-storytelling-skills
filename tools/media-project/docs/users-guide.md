# media-project Users' Guide

`media-project` packages generated visual storytelling clips into editor
project files. The first supported target is OpenShot project JSON (`.osp`).

## Inputs

Run the command from the generated tool environment after `video-generator` has
produced these project-root-relative files:

- `generated/assembly_order.md`
- `generated/generation_log.md`
- the selected local video files named by both tables

`ffprobe` must be installed and available on `PATH`. The command probes every
selected local video with
`ffprobe -print_format json -show_format -show_streams` and uses that metadata
to populate OpenShot `FFmpegReader` objects. If `ffprobe` is missing, packaging
stops before writing outputs.

`generated/assembly_order.md` must contain these columns:

| Column           | Purpose                                                |
| ---------------- | ------------------------------------------------------ |
| `Order`          | Final timeline order. Never uses filesystem order.     |
| `Shot ID`        | Stable shot identifier.                                |
| `Sub-clip`       | Sub-clip identifier for decomposed shots.              |
| `Selected clip`  | Project-root-relative path to the selected video file. |
| `Boundary after` | Cut or transition intent after the clip.               |
| `Notes`          | Editable transition or review notes.                   |

`generated/generation_log.md` must contain the current video-generator columns
plus `Duration seconds`. The OpenShot packager also preserves optional columns
when present: `Transition type`, `Transition duration`, `Mute generated audio`,
`Forced generated audio`, `Scene ID`, `Prompt file`, and `Continuity flags`.

Accepted review states are `accepted`, `approved`, `final`, and `selected`.
Completed generation statuses are `complete`, `completed`, `success`, and
`succeeded`.

## Command

```bash
uv run media-project package-openshot \
  --project-root /path/to/story-project \
  --assembly-order generated/assembly_order.md \
  --generation-log generated/generation_log.md \
  --manifest prompts/manifest.md \
  --output generated/media-project/project.osp \
  --sidecar generated/media-project/media-project.json
```

By default, the command refuses to overwrite an existing `.osp` or sidecar.
Pass `--force` only when replacing those generated files is intentional.

The default timeline settings are explicit and can be overridden:

| Option             | Default |
| ------------------ | ------- |
| `--width`          | `1920`  |
| `--height`         | `1080`  |
| `--fps-num`        | `24`    |
| `--fps-den`        | `1`     |
| `--sample-rate`    | `44100` |
| `--channels`       | `2`     |
| `--channel-layout` | `3`     |

## Outputs

The `.osp` file contains ordered file entries, timeline clip entries, relative
file paths, clip positions, probed media durations, volume curves, full
`FFmpegReader` metadata for playback, and editable metadata for review and
transition intent. File entries and clip reader entries both contain the probed
reader metadata so libopenshot can initialise the selected videos for playback.

The sidecar JSON preserves production metadata for downstream review:

- shot, scene, sub-clip, take, and order identifiers;
- source clip path, effective duration, and computed timeline position;
- transition type, transition duration, clip boundary, and notes;
- audio-generation intent, including forced generated audio and downstream mute
  intent;
- model, job ID, file size, actual resolution, prompt hash, prompt file,
  continuity flags, and review state.

`cut` clips are written as adjacent timeline clips. `dissolve` intent is
preserved as metadata until a known-good OpenShot transition-effect JSON shape
has been verified by a manual OpenShot smoke test.
