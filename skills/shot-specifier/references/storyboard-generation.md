# Storyboard Generation Guide

Read this before Phase 5 (Storyboard Generation). Covers nanobanana tool selection,
prompt construction for storyboard frames, reference-role assignment, and the
generate-vs-edit decision.

---

## Tool Selection

Use the nanobanana MCP skill for all storyboard image generation. The nanobanana skill
is documented in `skills/nanobanana/SKILL.md`. Read that skill before using the tools.

### Model Selection

| When | Use |
|------|-----|
| Highest-fidelity storyboard frames; complex scene compositions; typography or text in frame | `gemini-3-pro-image-preview` |
| Speed matters and top-end fidelity is not required; wide aspect ratios (4:1, 8:1) | `gemini-3.1-flash-image-preview` |
| Fast iteration; simple scenes; checking composition before full-quality generation | `gemini-2.5-flash-image` |

For production storyboards that will be used as start/end frames in video generation,
prefer `gemini-3-pro-image-preview` for all character and complex location frames.

### Tool Selection by Operation

| Operation | Tool |
|-----------|------|
| New storyboard frame (no prior frame to build from) | `generate_image` |
| End frame that is a modified version of the start frame | `edit_image` |
| Shot involving a recurring human character across multiple frames | `character_consistency` |
| Frame that combines multiple reference subjects | `multi_image_fusion` |

---

## Reference Completeness Check

Before generating any frame — start, end, or key — answer these three questions for the
specific shot:

1. Does a canonical reference image exist for **every named character** in this shot?
2. Does a canonical reference image exist for **every named prop** visible in this shot?
3. Does a canonical reference image exist for **the specific location variant** (angle ×
   lighting condition) this shot requires?

If any answer is no, generate the missing reference first using the scene inventory's
Phase 11 procedure. Do not proceed with storyboard generation until all three answers
are yes. A missing prop reference is the most common root cause of cross-shot visual
inconsistency: the model invents a different object each time.

---

## Start Frame Prompt Construction

Build the prompt using this order (from nanobanana skill §3):

1. **Subject:** Who or what is in frame; their key identity features
2. **Action/state:** What is happening at this exact moment
3. **Setting:** Location type; environmental details; spatial layout
4. **Composition:** Frame size; camera angle; spatial arrangement
5. **Lighting/mood:** Key source; quality; colour temperature; atmosphere
6. **Style/materiality:** Draw from prompt keyword library — global style phrase,
   location vocabulary, lighting condition vocabulary
7. **Constraint layer:** Negative constraints; exact prop positions; what must remain;
   what must not appear

End every prompt with: `"no text, no watermarks, no logos, no labels, no annotations"`

### Reference Image Assignment

Pass reference images with explicit roles. Assign each a job:

- **Identity:** character primary ref — prevents face drift
- **Pose/action:** character action ref — guides body position
- **Style:** style anchor — enforces filmstock and colour treatment
- **Environment:** location ref matching the shot's lighting condition
- **Prop:** prop primary ref — ensures prop appearance consistency

Do not pass more references than necessary. Too many references can produce averaging
artefacts. The standard set per frame is:

- 1 style ref (always)
- 1 location ref matching the shot's lighting condition (always)
- 1 character ref per named character in frame
- 1 prop ref per named, story-critical prop in frame

The prop ref is mandatory whenever a named prop appears in frame — omitting it gives the
model licence to invent the prop's appearance independently per shot, producing a
different-looking object every time it appears on screen.

---

## End Frame Generation: Edit vs Generate

### Use `edit_image` (edit from start frame) when:

- The end frame shows the same subject in the same location
- The change is: subject position shift, expression change, object state change,
  minor environmental change
- The composition is substantially the same
- More than 60% of the frame is unchanged

**Prompt format for edits:**

```text
Keep all of the following unchanged: {list everything that must stay the same}.
Change only: {exact description of what changes}.
```

State the preserved elements first. This is critical — the model defaults to changing
things when not explicitly told to preserve them.

### Use `generate_image` (generate new) when:

- The end frame is a different camera angle or framing
- The subject has moved significantly through the space
- The lighting condition has changed substantially
- The composition is more than ~40% different

For new end frames, use the start frame as an additional reference image to maintain
scene consistency, but generate from scratch rather than editing.

---

## Character Consistency Across Multiple Shots

When a character appears across multiple shots in the same sequence, use
`character_consistency` for shots 2 onwards:

1. Generate the character's first appearance storyboard frame using `generate_image`
   with the character primary ref.
2. For subsequent appearances: use `character_consistency` with the first storyboard
   frame as the character reference, and a scene prompt describing the new context.

This maintains face and identity consistency more reliably than passing the primary ref
repeatedly, because the first storyboard frame captures the character as they appear in
this production's style (rather than the neutral white-bg reference).

---

## Quality Gates

After generating each storyboard frame, verify before moving on:

| Check | Pass condition | Fail action |
|-------|---------------|-------------|
| Subject identity matches reference | Face, clothing, distinguishing marks consistent | Regenerate with higher-weight identity reference |
| Location matches location ref | Architecture, layout, materials correct | Regenerate with explicit negative constraints for common errors |
| Lighting matches direction spec | Colour temperature, shadow direction, practical sources correct | Edit to correct lighting; or regenerate with more explicit lighting prompt |
| Interpolatable change (start vs end) | Subject or composition has measurably changed | If start and end are too similar, edit end frame to amplify the difference |
| Negative constraints respected | No trees, no forbidden elements, correct traffic direction, etc. | Regenerate with stronger negative constraint prompt |

---

## Common Storyboard Failures and Fixes

| Failure | Likely Cause | Fix |
|---------|-------------|-----|
| Face changes between shots | Character ref weight too low | Use `character_consistency` tool; increase reference weight |
| Location architecture wrong | Location ref not passed or weighted too low | Ensure location ref is always included; add architectural specifics to prompt |
| Grain/filmstock wrong for POV shot | Global style phrase applied to machine-vision shot | Use POV override from keyword library; remove grain terms |
| Unwanted elements in frame | Negative constraints not in prompt | Add explicit negative constraints; repeat the key ones twice |
| Start and end frames look identical | Change too subtle for model | Increase magnitude of described change; or explicitly state the delta in the edit prompt |
| Style drifts across shots | Style vocabulary invented per-shot | Use keyword library phrases verbatim; pass style anchor ref on all shots |
| Named prop looks like a different object across shots | Prop ref not passed, or prop ref did not exist at generation time | Pass prop primary ref on every frame containing the prop; if prop ref was missing, regenerate those frames with the locked ref |
