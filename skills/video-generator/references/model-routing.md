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
| `resolution` | Machine parameter, e.g. `1080p` |
| `generation_strategy` | `single_clip`, `split_at_keyframe`, or `merge_keyframe_motion` |

## Routing Defaults

| Shot type | Default model | Reason |
|-----------|---------------|--------|
| Character-centric action or dialogue-adjacent shot | `seedance_2_0` | Strongest default for identity and reference preservation |
| Complex action or large pose interpolation | `seedance_2_0` at `1080p` | Better fit for reference-heavy interpolation |
| Landscape establishing or smooth pan | `seedance_2_0` or `kling3_0` | Use Seedance when visual refs dominate; Kling when camera path dominates |
| Drone or machine-vision POV | `kling3_0` or `seedance_2_0` | Experimental; choose based on whether camera motion or visual refs dominate |
| Static CU or minimal motion insert | `seedance_2_0` unless a cheaper validated model is specified | Low motion; references still protect identity |
| Product, prop, or recurring-element detail | `seedance_2_0` | Reference fidelity matters more than motion richness |

## Constraint Table

| Model | Duration | Resolution | Image roles |
|-------|----------|------------|-------------|
| `seedance_2_0` | 4-15 s for this workflow | `480p`, `720p`, `1080p` | `start_image`, `end_image`, `image` |
| `kling3_0` | 3-15 s for this workflow | `720p`, `1080p` | `start_image`, `end_image`, `image`; motion-control variants may differ |

Firecrawl evidence confirms the public Higgsfield MCP markets Seedance, Kling, and Veo
for video, videos up to 15 seconds, asynchronous generation, and model selection by the
agent. It does not expose a full machine-readable parameter schema. If the live MCP tool
reports narrower limits or different parameter names, obey the tool and update the
manifest before submission. Do not submit an invalid duration and wait for the provider
to reject it.

## Key-Frame Rule

No current Higgsfield route in this workflow accepts mid-clip key-frame anchors. Any shot
with key frames must be routed through `split_at_keyframe` or explicitly marked
`merge_keyframe_motion` with a rationale.
