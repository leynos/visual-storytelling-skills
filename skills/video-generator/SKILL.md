---
name: video-generator
description: >
  Execute production video generation from shot-specifier outputs through the Higgsfield
  Model Context Protocol (MCP). Use when prompts, storyboard frames, media roles, model
  routing, Higgsfield MCP uploads, generate_video calls, status polling, retakes, resume
  behaviour, or final assembly order are needed. Bridges
  structured [TAG] prompt files to model-native plain text prompts, validates model
  duration/aspect constraints, decomposes key-frame shots into supported start/end image
  clips, tracks uploaded media and job IDs, and writes generation logs.
---

# Video Generator

Turns a completed shot-specifier handoff into generated video clips through the
**Higgsfield Model Context Protocol (MCP)**. This skill begins only after
`shot-specifier` Phase 8 has produced prompt files, storyboard frames, model routing,
generation strategies, explicit audio-generation preferences, and
`prompts/manifest.md`. `scene-inventory-extractor-v2` stops at its Phase 13 handoff and
is not a direct input to production video generation.

Do not use this skill for image generation; use `nanobanana` through
`scene-inventory-extractor-v2` or `shot-specifier` for that. Do not backfill missing
scene analysis or shot direction here; hand back to `scene-inventory-extractor-v2` or
`shot-specifier` when upstream fields are absent.

This skill owns the operational gap between "prompt written" and "clip exists on disk":
resolve local paths, upload or register media, cache returned handles, submit jobs, poll
until terminal status, download outputs, record retakes, and write assembly order. A shot
is not complete until a local video file exists or a blocker is recorded.

The job is to be boringly competent: choose an approved Higgsfield video model, pass the
right images in the right roles, submit resumable jobs, and leave enough state that a
later agent can continue without guessing.

## Read Before Running

- For execution validation, live-schema constraints, default overrides, and empirical
  output checks, read [references/model-routing.md](./references/model-routing.md).
  Model choice and model-native prompt ordering are owned upstream by
  `shot-specifier/references/model-routing.md`; do not re-route shots here unless the
  manifest is being explicitly repaired.
- For Seedance 2.0-specific multimodal reference planning, prompt structure, duration
  defaults, quality/speed decisions, and troubleshooting, load `seedance-2-deep-dive`
  whenever a job uses `seedance_2_0`.
- For Kling 3.0-specific shot structure, camera language, Elements, Motion Control,
  native audio/dialogue, product prompting, and troubleshooting, load
  `kling-3-0-deep-dive` whenever a job uses `kling3_0`.
- For converting structured `[TAG]` prompt files into model-native prompt strings, read
  [references/prompt-flattening.md](./references/prompt-flattening.md).
- For shots with key frames, read
  [references/key-frame-decomposition.md](./references/key-frame-decomposition.md).
- For media uploads and job state, read
  [references/media-upload-and-state.md](./references/media-upload-and-state.md).
- For what Firecrawl confirmed about the public Higgsfield MCP and SDK surfaces, read
  [references/higgsfield-mcp-research.md](./references/higgsfield-mcp-research.md).

## Required Inputs

- `prompts/manifest.md` from `shot-specifier` with
  shot order, duration, model routing, prompt file, frame paths, aspect ratio,
  target resolution, resolution parameter, generation strategy, review-gate metadata,
  model-overrides, count, required-reference audit, and explicit audio-generation
  preferences.
- One prompt file per shot containing both the structured `## Prompt` block and a
  `## Generation Prompt` block.
- Start and end frames for every generation clip.
- Key frames only when accompanied by a split plan; Higgsfield video generation accepts
  start and end anchors, not mid-clip key-frame anchors.
- Continuity inventory or the shot-specifier reference audit when available. The
  consistency pass is actionable input: any continuity-critical reference or prompt
  constraint it names must be present in the job or explicitly blocked.

## Tool And Model Rules

Use the connected **Higgsfield MCP** for production video generation. The MCP endpoint
documented by Higgsfield is `https://mcp.higgsfield.ai`; authenticate through the
connector's Higgsfield account flow, then inspect the live MCP tools before submitting
work.

Route to these recommended Higgsfield video models unless the live MCP schema says they
are unavailable:

| Need | Preferred model | Use it for |
|------|-----------------|------------|
| Character identity, multiple references, hero props, recurring visual elements | Seedance 2.0 | Dialogue-adjacent shots, character-centric action, prop details, continuity-sensitive scenes |
| Smooth camera motion with fewer identity constraints | Kling 3.0 | Drone POV, landscape movement, machine-vision travel, forward pushes |
| Cinematic image-to-video when DoP/camera treatment is the main point | Higgsfield DoP or Cinema route when exposed | Polished camera moves from strong start images |
| Provider-specific style or production requirement | Veo route when exposed and approved in the manifest | Only when the manifest names it and the MCP schema supports the needed media roles |

Do not invent model IDs. Translate manifest names such as `seedance_2_0` or `kling3_0`
to the exact IDs exposed by the live MCP tool surface, record that mapping in the
generation log, and stop if no matching model is available.

When the resolved model is Seedance 2.0, apply `seedance-2-deep-dive` before submission:
validate the reference-file plan against live MCP limits, preserve each required
reference's purpose, keep production clips within the planned duration envelope, and
use draft/final quality settings deliberately instead of treating quality as a repair
button.

When the resolved model is Kling 3.0, apply `kling-3-0-deep-dive` before submission:
validate the shot structure, camera endpoint, frame anchors, Elements, Motion Control,
and native-audio plan against live MCP limits, and stop rather than downgrading a
structured Kling job to plain text-to-video.

Do not use a plain text-to-video route for a shot that has required start/end/reference
frames. Use image-to-video, start/end image, or the equivalent MCP mode that actually
accepts those anchors. If the selected model cannot accept the required media roles,
stop and report the missing role instead of dropping images.

## MCP Schema Check

Before the first job in a run, inspect the connected Higgsfield MCP tools and record the
observed contract in `generated/generation_log.md` or `generated/mcp_schema_notes.md`:

- video-generation tool name, such as `generate_video` or the current equivalent;
- model parameter name and accepted model identifiers;
- prompt field name and prompt-length limit if exposed;
- supported media roles, especially `start_image`, `end_image`, and generic reference
  image roles;
- duration, aspect-ratio, resolution, quality, motion, genre, and audio parameters;
- `count` or equivalent multi-output parameter when exposed;
- model-specific default parameters, especially `generate_audio`, `sound`, `cfg_scale`,
  `mode`, `quality`, `genre`, and guidance/reference-adherence controls;
- upload/history tools and the handle type they return;
- status polling tool, terminal statuses, and output-download field.

The logical job shape is a contract target, not a guarantee about exact parameter names:

```text
generate_video(
  model={exact_higgsfield_model_id},
  prompt={generation_prompt},
  aspect_ratio={aspect_ratio},
  duration={duration_seconds},
  resolution={resolution_parameter},
  audio={audio_generation_preferences},
  count={count},
  model_overrides={validated_override_map},
  media=[
    {value: start_media_handle, role: "start_image"},
    {value: end_media_handle, role: "end_image"},
    {value: reference_media_handle, role: "image"}
  ]
)
```

Map this shape to the live MCP schema. Stop on schema mismatch when the mismatch affects
identity, frame anchors, duration, aspect ratio, output resolution, or recoverability.

## Workflow

1. **Audit manifest.** Confirm every shot has `recommended_model`, `aspect_ratio`,
   `target_resolution`, `resolution_parameter`, `duration`, `generation_strategy`,
   `audio_generation_preferences`, `model_overrides`, `count`, `review_gate`,
   `required_refs` or `reference_audit`, `prompt_file`, `start_image`, and
   `end_image`. Halt if any required field is missing.
2. **Inspect Higgsfield MCP.** Load the live MCP schema and confirm the selected model,
   media roles, upload/history path, polling path, and output path exist.
3. **Validate constraints and defaults.** Check model duration, supported resolution,
   aspect ratio, media-role support, and model-specific defaults before upload. Override
   unwanted defaults from `model_overrides` explicitly when the live schema exposes the
   key. If an override key is absent, record it as `unsupported` and classify the impact:
   stop when the unsupported key would break dialogue, narration/post-audio sync,
   identity, required references, or the planned shot contract; proceed with a logged
   note only when the unsupported default is non-critical for this shot class.
4. **Verify model-native prompts.** Use the existing `## Generation Prompt` when
   present. If absent, produce it using the model-specific algorithm in
   `references/prompt-flattening.md`, write it back to the prompt file, then continue.
5. **Verify continuity-critical refs.** Compare the manifest's required refs and the
   prompt file's reference audit against the continuity inventory and Phase 6
   storyboard consistency report when present. Add missing actioned constraints to the
   prompt before continuing. Stop if a continuity-critical character, prop, recurring
   element, location variant, or style anchor cannot be supplied to the chosen model and
   is not demonstrably baked into the start/end storyboard frames.
6. **Decompose key-frame shots.** For any shot with key frames, use
   `references/key-frame-decomposition.md` to create sub-clips with only `start_image`
   and `end_image` roles. Validate each sub-clip duration against the chosen model.
7. **Prepare MCP media inputs.** Resolve relative paths from the project root and use
   the connected Higgsfield MCP's upload or history/input mechanism for each required
   media file. Cache the returned media handle, UUID, URL, or generation-history ID in
   `generated/media_manifest.md`.
8. **Apply audio preferences.** Map each shot's audio-generation preferences to the live
   MCP audio parameters. Narration remains off because it is handled as a separate
   process. If the MCP cannot disable generated audio, use severity-based handling: for
   landscape, environment, atmosphere, or machine-vision shots where generated ambience
   will be muted or is acceptable, proceed only with a log note that audio could not be
   disabled; for dialogue, lip-sync, narration, music-timed, supplied-audio, or
   externally mixed shots, stop because forced generated audio conflicts with the
   production plan.
9. **Plan submission order.** Use the prescriptive batching rules in
   `references/media-upload-and-state.md`: start long or serial-prone Seedance work
   early, fill available plan-level concurrency with Kling or other non-Seedance work,
   and record the queue strategy before a large run.
10. **Submit generation jobs.** Call the connected Higgsfield MCP video-generation tool
   (`generate_video` or the current tool-surface equivalent) with the model-native
   prompt string, validated model parameters, `count` when exposed, and media handles in
   their roles. If `count` is not exposed, submit explicit `v1`, `v2`, ... jobs only
   when the manifest requests multiple takes.
11. **Log immediately.** Append a row to `generated/generation_log.md` as soon as the API
   returns a job ID. An unlogged job is a lost job.
12. **Poll and download.** Poll with backoff until a terminal status. Download successful
   clips to `generated/{shot_id}/v{take}.mp4` or
   `generated/{shot_id}/{subclip_id}_v{take}.mp4`. Do not mark a job complete until this
   local file exists and is recorded in the log.
13. **Verify output file.** Record local file size and actual pixel dimensions. If the
   file is missing, zero-length, unexpectedly tiny, or at dimensions that differ from
   the model route's verified empirical output, mark the take for review or retake.
   Mismatch from the aspirational `target_resolution` alone is review data, not an
   automatic failure when the current live route is known to emit different pixels.
14. **Run review gate.** If the manifest marks the shot `review_gate=required`, stop
   automatic progression after download until the take is reviewed against the shot spec
   and storyboard frames. Landscape or low-risk v1 shots may use `review_gate=optional`.
15. **Resume safely.** On rerun, skip completed rows with a local output path unless the
   user requests a retake.
16. **Write assembly order.** Update `generated/assembly_order.md` with selected takes
    and sub-clip order for final editing.

## Reference Image Discipline

Every job must include the start and end frame handles for that clip. Add generic
reference images only when the live MCP route supports them and the shot manifest marks
them as required:

- character references for character-centric shots;
- location references for environment shots;
- prop references for hero props;
- recurring visual element references for monitor layouts, robots, grow-light rigs,
  cargo pods, bee cabinets, console layouts, signage systems, or other continuity
  objects that appear in more than two shots;
- style references only when they do not crowd out continuity references.

When a model has a reference-count limit, prioritize in this order: start/end anchors,
principal character, active hero prop, recurring visual element, location, style. Stop
if the limit prevents a required identity or continuity reference from being supplied.

Before upload, prove that the required-reference list is complete. The storyboard
consistency report and continuity inventory are not just advisory notes: their outcomes
must be actioned through regenerated frames, added references, prompt constraints, or a
recorded blocker. Do not generate a shot whose manifest omits a continuity-critical
reference named upstream.

When the selected Kling 3.0 route exposes only `start_image` and `end_image`, do not try
to upload generic character, prop, location, or style references. Verify instead that
those continuity requirements were baked into the storyboard frames during
`shot-specifier` Phase 5 and are named in the prompt constraints. Stop only if the
storyboard frames fail to carry a continuity-critical item that no live Kling media role
can supply.

## Stop Conditions

Stop before generation when:

- the Higgsfield MCP is unavailable or unauthenticated;
- the live MCP schema cannot be inspected;
- the recommended model is unavailable;
- required `start_image` or `end_image` roles are unavailable;
- required reference images cannot be passed without exceeding model/tool limits and
  cannot be baked into the start/end storyboard frames;
- duration, aspect ratio, or resolution is unsupported;
- no upload/history mechanism can turn local files into accepted media inputs;
- explicit audio-generation preferences cannot be honoured for dialogue, lip-sync,
  narration/post-audio, supplied-audio, or music-timed shots;
- the model would force generated audio on a landscape, environment, atmosphere, or
  machine-vision shot and the generation log does not record the forced-audio exception;
- model-specific defaults would alter reference adherence, mode, or generation-critical
  quality and the live MCP schema does not expose an override;
- model-specific defaults would alter resolution labels, but actual pixels cannot be
  verified after download;
- the manifest requests `count > 1` but the live schema has no count parameter and the
  operator has not approved equivalent explicit retake jobs;
- a job cannot be logged or resumed.

Do not silently fall back to another provider, another model family, text-only video, or
a reduced reference set. Ask for an explicit production decision instead.
