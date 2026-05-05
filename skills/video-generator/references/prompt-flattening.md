# Prompt Flattening

Higgsfield `generate_video` receives one plain prompt string. Scene-pack prompt files are
structured for humans and tools. Every prompt file therefore needs a model-native
`## Generation Prompt` section.

## Canonical Order

Flatten the structured tags in this order:

1. `[ACTION]`
2. `[SUBJECT]`
3. `[SCENE]`
4. `[FRAMING]`
5. `[PACING]`
6. `[STYLE]`
7. `[FILMSTOCK]`
8. `[AUDIO]`
9. `[DURATION]`

This order puts motion and subject continuity first, then environment, camera, style,
audio, and duration.

## Algorithm

1. Extract the `## Prompt` block.
2. Parse top-level tags of the form `[TAG] content`, preserving multi-line content until
   the next tag.
3. Trim whitespace and remove the literal tag labels.
4. Concatenate fields in canonical order as short paragraphs separated by a single
   space.
5. Drop empty fields.
6. Append explicit anchor statements:
   - `The start image is the first frame.`
   - `The end image is the final frame.`
   - `Preserve all supplied reference-image identities and layouts throughout.`
7. If a model exposes a prompt-length limit, trim lowest-priority fields first:
   `[AUDIO]`, `[FILMSTOCK]`, `[STYLE]`, then `[PACING]`. Never trim `[ACTION]`,
   `[SUBJECT]`, or core `[SCENE]` constraints.

## Prompt File Requirement

Write the flattened text back into each prompt file:

```markdown
## Generation Prompt

{plain text sent directly to generate_video}
```

The `video-generator` skill must use this section for Higgsfield MCP video-generation
calls. The structured `## Prompt` block remains the reviewable source.
