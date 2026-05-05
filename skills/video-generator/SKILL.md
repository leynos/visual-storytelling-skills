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

## Read Before Running

- For model choice and duration limits, read
  [references/model-routing.md](./references/model-routing.md).
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

## Workflow

1. **Audit manifest.** Confirm every shot has `recommended_model`, `aspect_ratio`,
   `resolution`, `duration`, `generation_strategy`, `prompt_file`, `start_image`, and
   `end_image`. Halt if any required field is missing.
2. **Validate constraints.** Check model duration, supported resolution, aspect ratio,
   and media-role support before upload. Do not discover invalid clips after submission.
3. **Flatten prompts.** Use the existing `## Generation Prompt` when present. If absent,
   produce it using `references/prompt-flattening.md`, write it back to the prompt file,
   then continue.
4. **Decompose key-frame shots.** For any shot with key frames, use
   `references/key-frame-decomposition.md` to create sub-clips with only `start_image`
   and `end_image` roles. Validate each sub-clip duration against the chosen model.
5. **Prepare MCP media inputs.** Resolve relative paths from the project root and use
   the connected Higgsfield MCP's upload or history/input mechanism for each required
   media file. Cache the returned media handle, UUID, URL, or generation-history ID in
   `generated/media_manifest.md`.
6. **Submit generation jobs.** Call the connected Higgsfield MCP video-generation tool
   (`generate_video` or the current tool-surface equivalent) with the model-native
   prompt string, validated model parameters, and media handles in their roles.
7. **Log immediately.** Append a row to `generated/generation_log.md` as soon as the API
   returns a job ID. An unlogged job is a lost job.
8. **Poll and download.** Poll with backoff until a terminal status. Download successful
   clips to `generated/{shot_id}/v{take}.mp4` or
   `generated/{shot_id}/{subclip_id}_v{take}.mp4`.
9. **Resume safely.** On rerun, skip completed rows with a local output path unless the
   user requests a retake.
10. **Write assembly order.** Update `generated/assembly_order.md` with selected takes
    and sub-clip order for final editing.

## Higgsfield MCP Contract

The public Higgsfield MCP page describes MCP as the agent interface for image and video
generation and says generation runs asynchronously with polling. The exact local MCP
tool names and parameter schema may vary by connector version, so inspect the connected
tool surface before submitting jobs.

Prefer the MCP tool surface over direct SDK/API calls. The official SDK evidence is
fallback context only, useful for understanding status values, upload concepts, and
polling behaviour when the MCP schema is sparse.

Map the manifest and media cache to the connected MCP schema. The expected logical shape
is:

```text
generate_video(
  model={recommended_model},
  prompt={generation_prompt},
  aspect_ratio={aspect_ratio},
  duration={duration_seconds},
  resolution={resolution},
  genre={genre_or_mood_if_supported},
  media=[
    {value: start_media_handle, role: "start_image"},
    {value: end_media_handle, role: "end_image"},
    {value: style_or_subject_media_handle, role: "image"}
  ]
)
```

Only include roles supported by the selected model and current MCP tool surface. If a
required role is unavailable, stop and report the blocker rather than silently changing
the generation strategy.
