# Video Generation Model Routing

Use this when turning prompt manifests into Higgsfield MCP generation jobs. This is the
execution-facing companion to `skills/shot-specifier/references/model-routing.md`.

## Source Of Truth Boundary

`skills/shot-specifier/references/model-routing.md` is the single source of truth for:

- shot-type to model routing;
- creative routing rationale;
- model-native prompt flattening order;
- reference-priority intent;
- manifest intent fields emitted by `shot-specifier`.

This file is the single source of truth for:

- validating that a completed manifest can be submitted through the live Higgsfield MCP;
- mapping manifest intent to live schema parameters and exact model IDs;
- runtime default overrides;
- empirical output constraints, file-size checks, and actual-resolution checks.

If the two files appear to disagree, use `shot-specifier` routing for creative intent and
use the live MCP schema for executable parameter validity. Update both files in the same
commit whenever a change crosses that boundary.

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
| `model_overrides` | Explicit key/value overrides for live MCP defaults |
| `count` | Requested take count; default `1`, schema-gated maximum from live MCP |
| `required_refs` | Continuity-critical refs that must reach the generation job |
| `review_gate` | `required` or `optional` |

## Manifest Routing Validation

Do not choose a new model from this file during normal generation. A completed manifest
must already contain `recommended_model`, `routing_rationale`, reference requirements,
duration, audio preferences, and overrides from `shot-specifier`.

Use this file to validate whether that manifest can run:

1. Translate the manifest model alias to the exact live Higgsfield model ID.
2. Validate media roles, duration, aspect ratio, resolution parameter, audio controls,
   count, and default overrides against the live schema.
3. Stop if the model cannot carry required anchors or continuity refs.
4. If rerouting is required, return to `shot-specifier/references/model-routing.md`,
   write a new manifest row, and record the production decision. Do not silently select
   a fallback model inside `video-generator`.

## Constraint Table

| Model | Duration | Resolution parameter | Image roles |
|-------|----------|----------------------|-------------|
| `seedance_2_0` | 4-15 s for this workflow | `480p`, `720p`, `1080p` | `start_image`, `end_image`, `image` when exposed |
| `kling3_0` | 3-15 s for this workflow | `720p`, `1080p`, `4K` when exposed; verify actual pixels after download | `start_image`, `end_image`, `image` when exposed; motion-control variants may differ |
| Higgsfield DoP/Cinema route | Use live MCP limit | Use live MCP limit | Usually image-to-video; validate start/end support before routing |
| Veo route | Use live MCP limit | Use live MCP limit | Use only when live MCP route accepts required references |

Firecrawl evidence confirms Higgsfield markets Seedance, Kling, and Veo on the public
video surface, supports first/last image references, presents Seedance 2.0 as a 1080p
route, presents Kling 3.0 as a 4K route, and advertises plan-level parallel video
generation limits. The public pages do not expose a full machine-readable MCP schema for
`cfg_scale`, per-call `count`, or exact output pixels. If the live MCP tool reports
narrower limits, different parameter names, or different model IDs, obey the tool and
update the manifest before submission. Do not submit an invalid duration and wait for
the provider to reject it.

When the selected model is `seedance_2_0`, load `seedance-2-deep-dive` before media
upload or job submission. Use it for Seedance-specific reference prioritisation, prompt
shape, duration/aspect defaults, quality/speed choices, and retake triage.

When the selected model is `kling3_0`, load `kling-3-0-deep-dive` before media upload
or job submission. Use it for Kling-specific shot structure, camera language, Elements
and Motion Control planning, native audio/dialogue syntax, product prompting, text/UI
safety, and retake triage.

## Empirical Constraints Registry

These values seed validation, not blind submission. Update the generation log whenever
a live job produces different evidence.

| Model | Source | Observed constraint or behaviour | Execution implication |
|-------|--------|----------------------------------|-----------------------|
| `kling3_0` | Firecrawl: Higgsfield AI Video and Kling pages | Public UI exposes `16:9`, `9:16`, `1:1`, start frame, end frame, 5 s default, and `720p`/`1080p`/`4K` choices | Validate the same fields in the MCP schema; do not assume 4K means exact `3840x2160` pixels |
| `kling3_0` | Firecrawl: Higgsfield Kling page | Public page advertises native audio, up to 6 cuts, and up to 15 seconds | Route structured multi-shot or audio-capable shots here only when manifest explicitly requests those features |
| `kling3_0` | S01 observation | One 16:9 request downloaded as `1344x768`; one 8 s landscape take was about 21 MB and took about 90 s | Log actual pixels and file size; mismatch from `target_resolution` triggers review, not silent acceptance |
| `seedance_2_0` | Firecrawl: Higgsfield AI Video page | Public page presents Seedance 2.0 in 1080p and as a first/last-image reference route | Validate `1080p` in live MCP and verify downloaded pixels |
| `seedance_2_0` | S01 observation | Active generation took about 90-180 s plus possible serial queueing; one 6 s clip was about 4.3 MB | Plan queue order explicitly; files below half of the lowest same-model baseline require review |

## Default Parameter Overrides

Do not rely on provider defaults for audio, reference adherence, mode, quality, genre, or
resolution.

| Model | Observed/default behaviour | Execution rule |
|-------|----------------------------|----------------|
| `seedance_2_0` | Higgsfield may set `generate_audio: true` | Set `generate_audio=true` only when `audio_generation_preferences.source=generated`; set `false` for `none` or `supplied` when the schema supports it |
| `seedance_2_0` | Mode, quality, and genre may default silently | Use manifest values. Default to `quality=standard` for final takes, `quality=fast` only for draft tests, and `genre=auto` unless a tested genre is named |
| `kling3_0` | Higgsfield may set `sound: "on"` | Set `sound=on` only when generated ambient/sfx/dialogue are wanted; set `sound=off` for silent or supplied-audio shots |
| `kling3_0` | S01 observed `cfg_scale: 0.5` | If CFG/guidance is exposed, use `0.35-0.45` for reference/identity-critical shots, `0.5` for balanced camera/landscape shots, and `0.55-0.65` for prompt-led surreal/action shots with weaker reference needs; log the accepted value |
| `kling3_0` | Count is user-observed in MCP but not confirmed on public pages | Use `count=1` by default; use `count=2` for review-gated hero or uncertain shots only when live schema exposes count and credit/queue budget allows |
| All models | Labelled resolution may not equal actual pixel dimensions | Verify downloaded dimensions against `target_resolution` and log any mismatch |

Stop if the live schema cannot honour an explicit audio or reference-adherence
preference on a continuity-critical shot.

`model_overrides` in the manifest is the source of truth. If a suggested override key is
not present in the live MCP schema, mark the key unsupported in the log. Continue only if
the unsupported key is non-critical for the shot's identity, audio, and resolution
requirements.

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
