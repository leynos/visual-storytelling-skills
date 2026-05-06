# Make media-project write playable OpenShot projects

This ExecPlan (execution plan) is a living document. The sections
`Constraints`, `Tolerances`, `Risks`, `Progress`, `Surprises & Discoveries`,
`Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work
proceeds.

Status: COMPLETE

## Purpose / big picture

The `tools/media-project` command currently writes an `.osp` file that OpenShot
can show on the timeline, but the generated clips do not have enough FFmpeg
reader metadata for libopenshot to initialise playback reliably. After this
change, an agent can package completed `video-generator` output into an
OpenShot project that opens and plays in OpenShot because every selected media
file is probed with `ffprobe` and written as a full `FFmpegReader` object in
both `files[]` and each clip's `reader` field.

The observable result is that running `media-project package-openshot` against
a completed visual storytelling project writes a deterministic `.osp` and
sidecar JSON. The `.osp` uses OpenShot-compatible layers, integer gravity and
scale values, keyframe curve objects for animated properties, and file/clip
reader metadata derived from the actual media files rather than from guessed
generation metadata.

## Constraints

The implementation must preserve the existing separation between the `.osp`
editor state and the sidecar production metadata. The sidecar JSON's current
production provenance fields remain the source of review and generation
history; the `.osp` receives only the OpenShot state needed for editing and
playback plus concise clip metadata already present today.

The absence of `ffprobe` is a hard stop. The command must fail before reading or
writing outputs when the executable is unavailable. It must report that
`ffprobe` is required for OpenShot reader metadata and must not silently fall
back to the current minimal project format.

The command must call `ffprobe -print_format json -show_format -show_streams`
for every selected local clip. The implementation may use Python's standard
`subprocess` module rather than adding a runtime dependency. The ffprobe JSON
must be parsed as structured JSON and mapped through explicit helper functions,
not by ad hoc string manipulation.

The `.osp` `files[]` entries must be full `FFmpegReader` dictionaries including
the reader fields demonstrated by
`/data/leynos/Projects/strawberries-of-lewis/reference.osp` and
`/data/leynos/Projects/strawberries-of-lewis/strawberries-of-lewis-S01.osp`.
Each clip must include an equivalent `reader` object, and the clip `file_id`
must match the corresponding file entry `id`.

OpenShot layer numbers must use the OpenShot layer scale, starting with
`1000000`, and the project must include a `layers[]` array with matching layer
records. The initial implementation can keep every generated clip on the first
video layer if no upstream layer metadata is present.

The default project resolution must change from `1344x768` to `1920x1080`.
Width and height command-line overrides must continue to work.

The generated clip defaults must use OpenShot's integer values:
`gravity: 4` for centre and `scale: 1` for best fit. The implementation must
not write the existing string values `center` and `fit`.

Clip-level properties that OpenShot stores as curves must be written in the
OpenShot keyframe shape:

```json
{
  "Points": [
    {
      "co": {"X": 1.0, "Y": 1.0},
      "handle_left": {"X": 0.5, "Y": 1.0},
      "handle_right": {"X": 0.5, "Y": 0.0},
      "handle_type": 0,
      "interpolation": 0
    }
  ]
}
```

The initial implementation must preserve transition intent as metadata only.
It must not generate OpenShot transition effects until a known-good reference
transition object has been captured and tested.

The assembly-order input must align with current `video-generator` output. The
parser must accept `Selected clip` and `Boundary after`; if current field data
uses `File` and `Boundary (next)`, the update must either support those aliases
or update the relevant skill/template in the same change so the pipeline has one
documented contract.

The repository's instructions require gates before commits. Markdown-only plan
and skill changes require the relevant Markdown gates. Python implementation
changes require `make check-fmt`, `make lint`, `make typecheck`, and
`make test` under `tools/media-project`, with output captured through `tee` to
`/tmp`.

## Tolerances

If direct mapping from ffprobe output cannot populate one of OpenShot's required
reader fields without guessing, stop after documenting the missing field, the
available ffprobe fields, and the reference `.osp` values. Do not ship guessed
metadata that may make OpenShot playback unreliable.

If a required OpenShot field varies materially between the two supplied `.osp`
examples and the correct general rule is unclear, stop and ask whether to prefer
the OpenShot-built `reference.osp` value or the hand-built
`strawberries-of-lewis-S01.osp` value.

If adding ffprobe support and OpenShot clip templates changes more than 15
tracked files or more than 1,200 net lines, stop and propose a split into a
reader-metadata commit and a clip-template commit.

If tests need real media files larger than 10 MiB in the repository, stop and
choose a generated fixture strategy instead. Tests may create tiny deterministic
media files at runtime with `ffmpeg` only when `ffmpeg` is present, or unit-test
the mapper with captured ffprobe JSON fixtures.

If `ffprobe` is unavailable in the validation environment, implementation tests
must still cover the hard-stop error path. End-to-end media probing tests may be
skipped with an explicit skip reason, but the production command itself must
continue to hard stop.

## Risks

- Risk: OpenShot's `.osp` schema is reverse-engineered from examples rather
  than documented as a stable interchange contract.
  Severity: high.
  Likelihood: medium.
  Mitigation: Use the two supplied `.osp` files as regression references, keep
  the generated shape close to their common structure, and require a manual
  OpenShot smoke test before marking the plan complete.

- Risk: ffprobe and OpenShot do not use identical enum values for fields such as
  pixel format and display ratio.
  Severity: high.
  Likelihood: medium.
  Mitigation: Capture mapper decisions in small named helpers with unit tests.
  For unclear enum mappings, use the values observed in OpenShot examples only
  when they can be justified from ffprobe output or OpenShot's common defaults.

- Risk: The current fixture media files are plain byte strings named `.mp4`, so
  they cannot exercise ffprobe success paths.
  Severity: medium.
  Likelihood: high.
  Mitigation: Split tests into mapper tests using ffprobe JSON fixtures,
  hard-stop tests for missing `ffprobe`, and, where tools are available,
  runtime-generated sample-media behavioural tests.

- Risk: Duration metadata from generation logs may disagree with probed media
  duration.
  Severity: medium.
  Likelihood: medium.
  Mitigation: Use ffprobe video duration for OpenShot reader and clip timing.
  Preserve generation-log duration in the sidecar when useful, and surface any
  mismatch as sidecar or validation metadata rather than forcing OpenShot to use
  stale timing.

- Risk: Updating the assembly-order contract could break existing generated
  projects.
  Severity: medium.
  Likelihood: medium.
  Mitigation: Support documented aliases during a transition while keeping the
  skill/template output on a single preferred column set.

## Progress

- [x] (2026-05-06T21:06Z) Read repository guidance, confirmed branch
  `media-project-skill`, and verified this is not `main`.
- [x] (2026-05-06T21:06Z) Loaded `leta`, `grepai`, `execplans`, and
  `skill-creator` guidance for this task.
- [x] (2026-05-06T21:06Z) Inspected the current `tools/media-project`
  implementation, tests, documentation, and existing OpenShot packaging plan.
- [x] (2026-05-06T21:06Z) Compared the supplied OpenShot-built and hand-built
  `.osp` files for layer, reader, file, and clip property shapes.
- [x] (2026-05-06T21:06Z) Drafted this implementation plan.
- [x] (2026-05-06T21:14Z) Received explicit approval to implement the planned
  tool update.
- [x] (2026-05-06T21:14Z) Re-checked branch `media-project-skill`, confirmed
  the only unrelated working-tree item is untracked `remove.sh`, and resumed
  from this plan.
- [x] (2026-05-06T21:33Z) Added ffprobe discovery and hard-stop validation.
- [x] (2026-05-06T21:33Z) Added structured ffprobe JSON parsing and reader
  metadata mapping.
- [x] (2026-05-06T21:33Z) Replaced minimal file and clip entries with
  OpenShot-compatible full
  reader, layer, enum, and keyframe-curve structures.
- [x] (2026-05-06T21:28Z) Added deterministic focused tests for ffprobe
  hard-stop behaviour, full reader/keyframe output shape, and CLI packaging via
  `cmd-mox` mocked `ffprobe`.
- [x] (2026-05-06T21:33Z) Aligned assembly-order input handling with
  `video-generator` and added compatibility coverage for `File` and
  `Boundary (next)` aliases.
- [x] (2026-05-06T21:33Z) Updated `tools/media-project` user documentation for
  `ffprobe`, full reader metadata, probed durations, and `1920x1080` defaults.
- [x] (2026-05-06T21:33Z) Ran focused and full tool gates with `tee` logs.
- [x] (2026-05-06T21:33Z) Checked for a local OpenShot executable and recorded
  that the manual smoke test could not be run because `openshot-qt` and
  `openshot` are not installed in this environment.

## Surprises & Discoveries

- Observation: GrepAI is installed, but the `Projects` workspace does not list
  `/data/leynos/Projects/visual-storytelling-skills`.
  Evidence: `grepai workspace status Projects` listed other repositories but
  not this checkout.
  Impact: Exploration used scoped exact/file tooling after the required GrepAI
  availability check.

- Observation: `tools/media-project/media_project/openshot_project.py`
  currently writes minimal file entries with `duration`, `id`, `media_type`,
  and `path`, while clip entries use scalar `alpha` and `volume`, string
  `gravity` and `scale`, and `layer: 1`.
  Evidence: Local inspection of `_openshot_file` and `_openshot_clip`.
  Impact: The implementation must replace the core OpenShot JSON writer rather
  than adding only a reader object.

- Observation: Both supplied `.osp` files use full `FFmpegReader` structures in
  `files[]` and `clips[].reader`, integer `gravity: 4`, integer `scale: 1`,
  OpenShot layer number `1000000`, and keyframe curves for alpha, volume,
  channel filters, transforms, time, and waveform colour.
  Evidence: `jq` inspection of
  `/data/leynos/Projects/strawberries-of-lewis/reference.osp` and
  `/data/leynos/Projects/strawberries-of-lewis/strawberries-of-lewis-S01.osp`.
  Impact: The plan has concrete target structures for tests and implementation.

- Observation: The hand-built project uses `1920x1080` project settings even
  though some clips are `1284x716`, while the OpenShot-built reference uses
  `1280x720`.
  Evidence: `jq` inspection of top-level `width` and `height`.
  Impact: The default should move to `1920x1080` as requested, while keeping
  command-line overrides for smaller projects.

- Observation: On implementation resume, GrepAI was still available but still
  did not list this checkout in the `Projects` workspace.
  Evidence: `grepai version` reported `0.35.0`; `grepai workspace status
  Projects` listed 22 other projects and omitted
  `/data/leynos/Projects/visual-storytelling-skills`.
  Impact: Continue with scoped exact/file tooling for this checkout unless the
  workspace is indexed later.

- Observation: `cmd-mox` was not installed on the ambient shell `PATH`, but it
  is available as a Python package and the tool's scripting standards already
  document the `cmd_mox.pytest_plugin` fixture pattern.
  Evidence: `cmd-mox --help` failed with command not found; `uv add --dev
  cmd-mox` resolved `cmd-mox==0.2.0`, and `uv run python` imported
  `cmd_mox.pytest_plugin`.
  Impact: Add `cmd-mox` as a dev dependency and use its pytest fixture for the
  CLI `ffprobe` subprocess test instead of hand-writing mock binaries.

- Observation: A full OpenShot snapshot became too large once clips carried
  reader metadata and keyframe curves.
  Evidence: The first snapshot update added roughly two thousand lines of
  curve and reader JSON; replacing it with a deterministic summary kept the
  total diff below the plan's 1,200-line tolerance while preserving explicit
  reader/keyframe assertions in unit tests.
  Impact: Keep the broad snapshot focused on stable timeline and sidecar
  summaries, and cover full OpenShot property shape with targeted assertions.

- Observation: No OpenShot executable is installed in this environment.
  Evidence: `command -v openshot-qt || command -v openshot` returned no path.
  Impact: The manual OpenShot smoke test remains unrun here; the final report
  must state this clearly and include the automated evidence instead.

## Decision Log

- Decision: Treat missing `ffprobe` as a command-level hard stop, not as a
  warning or best-effort fallback.
  Rationale: The painful iteration showed that minimal `.osp` files can load
  but fail playback, so generating that shape after detecting no probe support
  would be actively misleading.

- Decision: Preserve dissolve intent as metadata in this update.
  Rationale: OpenShot transition effects are fragile to generate without a
  known-good reference object, while metadata preservation keeps the editor
  handoff useful and honest.

- Decision: Keep all clips on layer `1000000` unless upstream metadata later
  introduces a layer contract.
  Rationale: Both examples establish the OpenShot layer-number scale, and
  single-track assembly is sufficient for current selected-take handoff.

- Decision: Prefer ffprobe-derived media timing for OpenShot reader and clip
  duration fields.
  Rationale: OpenShot playback depends on the actual media stream, while the
  generation log duration is production metadata that may be stale or rounded.

- Decision: Use `cmd-mox` for mocked `ffprobe` subprocess behaviour in
  behavioural tests.
  Rationale: The repository's scripting standards recommend `cmd-mox` for
  external executable tests, and using the fixture keeps mock binaries
  declarative and verified rather than hand-rolled in each test.

- Decision: Use targeted OpenShot shape assertions plus a compact deterministic
  snapshot rather than snapshotting every generated keyframe curve.
  Rationale: The exact full `.osp` remains generated and tested, but storing
  every curve in a snapshot obscures behaviour changes and risks breaching the
  plan's change-size tolerance.

## Implementation plan

First, add tests that lock the intended failure and output shape. Unit tests
should cover the hard-stop error when `ffprobe` is absent, mapper tests should
feed captured ffprobe JSON into the reader builder, and snapshot or behavioural
tests should assert that generated `.osp` `files[]` and `clips[].reader` entries
contain the required reader fields. Existing tests that use fake `.mp4` bytes
must be adapted so they either mock probing or use structured probe fixtures.

Second, introduce a small probing boundary in `tools/media-project`. A helper
should locate `ffprobe`, execute it with
`-print_format json -show_format -show_streams`, parse the result, identify the
primary video stream and optional audio stream, and return a typed internal
description. The helper must reject media with no video stream, missing path,
or ffprobe execution failure with an `InputValidationError` message that names
the affected clip.

Third, build OpenShot reader dictionaries from the probed media. The builder
must populate codec names, stream indexes, bit rates, time bases, video length,
file size, duration, frames per second (FPS), dimensions, display ratio, sample
rate, channel count, channel layout, pixel format, pixel ratio, metadata,
`duration_strategy: "VideoPreferred"`, `type: "FFmpegReader"`, `media_type:
"video"`, and the deterministic file ID. File entries and clip reader entries
should come from the same builder so their reader metadata cannot diverge.

Fourth, replace the clip template with an OpenShot-compatible clip dictionary.
This includes integer `gravity` and `scale`, layer `1000000`, `effects: []`,
`parentObjectId: ""`, `title`, `image`, scalar placement fields, and keyframe
curves for alpha, volume, channel filters, audio/video flags, origins,
locations, scale, rotation, shear, perspective corners, time, and wave colour.
The keyframe curve helper should be shared and tested directly.

Fifth, align input metadata handling. The preferred assembly-order columns
remain `Selected clip` and `Boundary after`, matching the repository template,
but the parser should accept `File` and `Boundary (next)` aliases if confirmed
in current generated projects. Documentation and the media-project usage skill
must state the preferred contract and any accepted aliases.

Sixth, update documentation. `tools/media-project/docs/users-guide.md` should
state that `ffprobe` is required, explain that the tool uses actual media
metadata for OpenShot playback, document the `1920x1080` default, and preserve
the sidecar as production provenance. The new skill under
`skills/media-project/` should direct agents to stop immediately when `ffprobe`
is absent.

Finally, validate sequentially. Run `make check-fmt`, `make lint`,
`make typecheck`, and `make test` inside `tools/media-project`, each through
`tee` into `/tmp`. Run root or tool Markdown gates for changed Markdown files.
Open the generated `.osp` in OpenShot for a manual smoke test when a graphical
OpenShot session is available, or record explicitly that the manual smoke test
could not be run in the current environment.

## Validation

During implementation, use these commands from the repository root unless a
step says otherwise:

```bash
cd tools/media-project
make check-fmt 2>&1 | tee /tmp/check-fmt-visual-storytelling-skills-media-project-skill.out
make lint 2>&1 | tee /tmp/lint-visual-storytelling-skills-media-project-skill.out
make typecheck 2>&1 | tee /tmp/typecheck-visual-storytelling-skills-media-project-skill.out
make test 2>&1 | tee /tmp/test-visual-storytelling-skills-media-project-skill.out
```

For Markdown-only edits, run:

```bash
cd tools/media-project
make markdownlint 2>&1 | tee /tmp/markdownlint-visual-storytelling-skills-media-project-skill.out
make nixie 2>&1 | tee /tmp/nixie-visual-storytelling-skills-media-project-skill.out
```

Also run this from the repository root before committing:

```bash
git diff --check
```

Success means all automated gates pass, the command hard-stops when `ffprobe`
is missing, generated `.osp` files contain full reader metadata in both
`files[]` and `clips[].reader`, and a manual OpenShot smoke test either confirms
timeline playback or is recorded as unavailable with exact environment details.

## Outcomes & Retrospective

Implemented. `media-project package-openshot` now requires `ffprobe`, probes
each selected clip, writes full `FFmpegReader` metadata in `files[]` and
`clips[].reader`, emits OpenShot layer number `1000000`, uses integer
`gravity: 4` and `scale: 1`, writes OpenShot keyframe curve objects for clip
properties, and defaults new projects to `1920x1080`.

Validation completed on 2026-05-06:

- `make check-fmt` passed with log
  `/tmp/check-fmt-media-project-visual-storytelling-skills-media-project-skill.out`.
- `make lint` passed with log
  `/tmp/lint-media-project-visual-storytelling-skills-media-project-skill.out`.
- `make typecheck` passed with log
  `/tmp/typecheck-media-project-visual-storytelling-skills-media-project-skill.out`.
- `make test` passed 12 tests with log
  `/tmp/test-media-project-visual-storytelling-skills-media-project-skill.out`.
- `markdownlint-cli2 docs/execplans/media-project-skill.md
  tools/media-project/docs/users-guide.md` passed with log
  `/tmp/markdownlint-media-project-visual-storytelling-skills-media-project-skill.out`.
- `nixie --no-sandbox docs/execplans/media-project-skill.md
  tools/media-project/docs/users-guide.md` passed with log
  `/tmp/nixie-media-project-visual-storytelling-skills-media-project-skill.out`.

The manual OpenShot smoke test was not run because neither `openshot-qt` nor
`openshot` is installed in this environment.
