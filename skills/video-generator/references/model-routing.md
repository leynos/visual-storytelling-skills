# Video Generation Model Routing

Use this when turning prompt manifests into Higgsfield MCP generation jobs. This is the
execution-facing companion to `skills/shot-specifier/references/model-routing.md`.

## Manifest Fields

Every row must include:

| Field | Meaning |
|-------|---------|
| `recommended_model` | Exact Higgsfield model ID |
| `routing_rationale` | One sentence explaining the choice |
| `duration_seconds` | Validated per model |
| `aspect_ratio` | Machine parameter, e.g. `16:9` |
| `target_resolution` | Intended output dimensions, e.g. `1920x1080` |
| `resolution_parameter` | Machine parameter, e.g. `1080p` |
| `generation_strategy` | `single_clip`, `split_at_keyframe`, or `merge_keyframe_motion` |
| `audio_generation_preferences` | `generated`, `none`, or `supplied` plus ambient/sfx/dialogue flags |
| `review_gate` | `required` or `optional` |

## Routing Defaults

| Shot type | Default model | Reason |
|-----------|---------------|--------|
| Character-centric action or dialogue-adjacent shot | `seedance_2_0` | Best default for identity and reference preservation |
| Complex action or large pose interpolation | `seedance_2_0` at `1080p` | Better fit for reference-heavy interpolation |
| Landscape establishing or smooth pan | `seedance_2_0` or `kling3_0` | Use Seedance when visual refs dominate; Kling when camera path dominates |
| Drone or machine-vision POV | `kling3_0` or `seedance_2_0` | Choose based on whether camera motion or visual refs dominate |
| Static CU or minimal motion insert | `seedance_2_0` unless a cheaper validated Higgsfield model is specified | Low motion; references still protect identity |
| Product, prop, or recurring-element detail | `seedance_2_0` | Reference fidelity matters more than motion richness |
| Cinematic camera move from one strong frame | Higgsfield DoP or Cinema route when exposed | Use only when the route accepts the needed anchors |
| Manifest-approved provider-specific shot | Veo route when exposed | Use only when the manifest names it and media roles match |

## Constraint Table

| Model | Duration | Resolution parameter | Image roles |
|-------|----------|----------------------|-------------|
| `seedance_2_0` | 4-15 s for this workflow | `480p`, `720p`, `1080p` | `start_image`, `end_image`, `image` when exposed |
| `kling3_0` | 3-15 s for this workflow | `720p`, `1080p`; verify actual pixels after download | `start_image`, `end_image`, `image` when exposed; motion-control variants may differ |
| Higgsfield DoP/Cinema route | Use live MCP limit | Use live MCP limit | Usually image-to-video; validate start/end support before routing |
| Veo route | Use live MCP limit | Use live MCP limit | Use only when live MCP route accepts required references |

Firecrawl evidence confirms the public Higgsfield MCP markets Seedance, Kling, and Veo
for video, asynchronous generation, and model selection by the agent. The Seedance 2.0
page describes up to 15-second clips and multiple reference assets, but the public MCP
page does not expose a full machine-readable parameter schema. If the live MCP tool
reports narrower limits, different parameter names, or different model IDs, obey the
tool and update the manifest before submission. Do not submit an invalid duration and
wait for the provider to reject it.

When the selected model is `seedance_2_0`, load `seedance-2-deep-dive` before media
upload or job submission. Use it for Seedance-specific reference prioritisation, prompt
shape, duration/aspect defaults, quality/speed choices, and retake triage.

When the selected model is `kling3_0`, load `kling-3-0-deep-dive` before media upload
or job submission. Use it for Kling-specific shot structure, camera language, Elements
and Motion Control planning, native audio/dialogue syntax, product prompting, text/UI
safety, and retake triage.

## Default Parameter Overrides

Do not rely on provider defaults for audio, reference adherence, mode, quality, genre, or
resolution.

| Model | Observed/default behaviour | Execution rule |
|-------|----------------------------|----------------|
| `seedance_2_0` | Higgsfield may set `generate_audio: true` | Set generated audio explicitly from `audio_generation_preferences`; use `none` when silence or post audio is required |
| `kling3_0` | Higgsfield may set `sound: "on"` and `cfg_scale: 0.5` | Set sound explicitly; if CFG/guidance is exposed, use the manifest's reference-adherence intent instead of accepting the default on identity-critical shots |
| All models | Labelled resolution may not equal actual pixel dimensions | Verify downloaded dimensions against `target_resolution` and log any mismatch |

Stop if the live schema cannot honour an explicit audio or reference-adherence
preference on a continuity-critical shot.

## Routing Procedure

1. Read the shot intent, required references, action complexity, duration, and anchor
   images from the manifest.
2. Pick the default model from the routing table.
3. Inspect the live Higgsfield MCP model list or tool schema.
4. Translate the manifest model alias to the exact provider ID.
5. Validate duration, aspect ratio, target resolution, resolution parameter, audio
   preferences, default overrides, and media roles.
6. Record `recommended_model`, `actual_model_id`, and `routing_rationale`.
7. Stop if the chosen model cannot carry every required reference or anchor.

## Key-Frame Rule

No current Higgsfield route in this workflow accepts mid-clip key-frame anchors. Any shot
with key frames must be routed through `split_at_keyframe` or explicitly marked
`merge_keyframe_motion` with a rationale.
