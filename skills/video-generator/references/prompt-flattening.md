# Prompt Flattening

Higgsfield `generate_video` receives one plain prompt string. Shot-specifier prompt files
are structured for humans and tools. Every prompt file therefore needs a model-native
`## Generation Prompt` section.

The source of truth for model-specific flattening is
`skills/shot-specifier/references/model-routing.md`. `video-generator` should normally
use the `## Generation Prompt` already written by `shot-specifier`. Reconstruct it only
when the section is missing and the prompt file has an approved model route.

## Fallback Algorithm

1. Extract the `## Prompt` block and the recommended model from `## Metadata`.
2. Parse top-level tags of the form `[TAG] content`, preserving multi-line content until
   the next tag.
3. Trim whitespace and remove the literal tag labels.
4. Apply the model-specific order from `shot-specifier/references/model-routing.md`.
   - Seedance 2.0: action/reference intent first; style and filmstock late.
   - Kling 3.0: shot/camera structure first; action physics next; style last.
5. Drop empty fields.
6. Append explicit anchor statements:
   - `The start image is the first frame.`
   - `The end image is the final frame.`
   - `Preserve all supplied reference-image identities and layouts throughout.`
   - `No narration.`
7. If a model exposes a prompt-length limit, trim only according to that model's
   priorities. Never trim core action, subject, scene constraints, frame anchors, or
   audio-generation prohibitions.

Stop if the model route is unknown. A generic flattened prompt is not acceptable for
production video generation.

## Prompt File Requirement

Write the flattened text back into each prompt file:

```markdown
## Generation Prompt

{plain text sent directly to generate_video}
```

The `video-generator` skill must use this section for Higgsfield MCP video-generation
calls. The structured `## Prompt` block remains the reviewable source.
