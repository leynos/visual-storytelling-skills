---
name: video-generator
description: >
  Execute production video generation from scene-inventory-extractor-v2 or
  shot-specifier outputs through the Higgsfield MCP. Use when prompts, storyboard frames,
  media roles, model routing, Higgsfield MCP uploads, generate_video calls, status
  polling, retakes, resume behaviour, or final assembly order are needed. Bridges
  structured [TAG] prompt files to model-native plain text prompts, validates model
  duration/aspect constraints, decomposes key-frame shots into supported start/end image
  clips, tracks uploaded media and job IDs, and writes generation logs.
---

# Video Generator

Turns a completed scene pack into generated video clips through the **Higgsfield MCP**.
This skill begins after `scene-inventory-extractor-v2` Phase 14 or `shot-specifier`
Phase 7 has produced prompt files, storyboard frames, and `prompts/manifest.md`.

Do not use this skill for image generation; use `nanobanana` through
`scene-inventory-extractor-v2` or `shot-specifier` for that. Do not backfill missing
scene analysis or shot direction here; hand back to `scene-inventory-extractor-v2` or
`shot-specifier` when upstream fields are absent.

The job is to be boringly competent: choose an approved Higgsfield video model, pass the
right images in the right roles, submit resumable jobs, and leave enough state that a
later agent can continue without guessing.

## Read Before Running

- For model choice and duration limits, read
  [references/model-routing.md](./references/model-routing.md).
- For Seedance 2.0-specific multimodal reference planning, prompt structure, duration
  defaults, quality/speed decisions, and troubleshooting, load `seedance-2-deep-dive`
  whenever a job uses `seedance_2_0`.
- For converting structured `[TAG]` prompt files into model-native prompt strings, read
  [references/prompt-flattening.md](./references/prompt-flattening.md).
- For shots with key frames, read
  [references/key-frame-decomposition.md](./references/key-frame-decomposition.md).
- For media uploads and job state, read
  [references/media-upload-and-state.md](./references/media-upload-and-state.md).
- For what Firecrawl confirmed about the public Higgsfield MCP and SDK surfaces, read
  [references/higgsfield-mcp-research.md](./references/higgsfield-mcp-research.md).

## Required Inputs

- `prompts/manifest.md` from `scene-inventory-extractor-v2` or `shot-specifier` with
  shot order, duration, model routing, prompt file, frame paths, aspect ratio,
  resolution, and generation strategy.
- One prompt file per shot containing both the structured `## Prompt` block and a
  `## Generation Prompt` block.
- Start and end frames for every generation clip.
- Key frames only when accompanied by a split plan; Higgsfield video generation accepts
  start and end anchors, not mid-clip key-frame anchors.

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
- upload/history tools and the handle type they return;
- status polling tool, terminal statuses, and output-download field.

The logical job shape is a contract target, not a guarantee about exact parameter names:

```text
generate_video(
  model={exact_higgsfield_model_id},
  prompt={generation_prompt},
  aspect_ratio={aspect_ratio},
  duration={duration_seconds},
  resolution={resolution},
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
   `resolution`, `duration`, `generation_strategy`, `prompt_file`, `start_image`, and
   `end_image`. Halt if any required field is missing.
2. **Inspect Higgsfield MCP.** Load the live MCP schema and confirm the selected model,
   media roles, upload/history path, polling path, and output path exist.
3. **Validate constraints.** Check model duration, supported resolution, aspect ratio,
   and media-role support before upload. Do not discover invalid clips after submission.
4. **Flatten prompts.** Use the existing `## Generation Prompt` when present. If absent,
   produce it using `references/prompt-flattening.md`, write it back to the prompt file,
   then continue.
5. **Decompose key-frame shots.** For any shot with key frames, use
   `references/key-frame-decomposition.md` to create sub-clips with only `start_image`
   and `end_image` roles. Validate each sub-clip duration against the chosen model.
6. **Prepare MCP media inputs.** Resolve relative paths from the project root and use
   the connected Higgsfield MCP's upload or history/input mechanism for each required
   media file. Cache the returned media handle, UUID, URL, or generation-history ID in
   `generated/media_manifest.md`.
7. **Submit generation jobs.** Call the connected Higgsfield MCP video-generation tool
   (`generate_video` or the current tool-surface equivalent) with the model-native
   prompt string, validated model parameters, and media handles in their roles.
8. **Log immediately.** Append a row to `generated/generation_log.md` as soon as the API
   returns a job ID. An unlogged job is a lost job.
9. **Poll and download.** Poll with backoff until a terminal status. Download successful
   clips to `generated/{shot_id}/v{take}.mp4` or
   `generated/{shot_id}/{subclip_id}_v{take}.mp4`.
10. **Resume safely.** On rerun, skip completed rows with a local output path unless the
   user requests a retake.
11. **Write assembly order.** Update `generated/assembly_order.md` with selected takes
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

When a model has a reference-count limit, prioritise in this order: start/end anchors,
principal character, active hero prop, recurring visual element, location, style. Stop
if the limit prevents a required identity or continuity reference from being supplied.

## Stop Conditions

Stop before generation when:

- the Higgsfield MCP is unavailable or unauthenticated;
- the live MCP schema cannot be inspected;
- the recommended model is unavailable;
- required `start_image` or `end_image` roles are unavailable;
- required reference images cannot be passed without exceeding model/tool limits;
- duration, aspect ratio, or resolution is unsupported;
- no upload/history mechanism can turn local files into accepted media inputs;
- a job cannot be logged or resumed.

Do not silently fall back to another provider, another model family, text-only video, or
a reduced reference set. Ask for an explicit production decision instead.
