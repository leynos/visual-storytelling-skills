# Asset Pipeline

Read this before Phase 8. Covers file naming conventions, the generation log format,
and the retake workflow.

---

## Purpose

The asset pipeline ensures that every generated clip can be traced back to its source
shot specification, retaken efficiently, and assembled in the correct order. Without it,
collections of generated .mp4 files become unmanageable after the first day of
generation.

---

## Directory Structure

```text
{project}/
├── scene-pack/
│   └── {project}_scene_inventory.md
├── image_out/                          ← reference images (from scene-inventory-extractor)
│   ├── style/
│   ├── characters/
│   ├── locations/
│   └── props/
├── shots/                              ← storyboard frames (from shot-specifier phase 5)
│   └── {shot_id}/
│       ├── start.png
│       ├── end.png
│       └── key{NN}.png
├── prompts/                            ← video generation prompts
│   ├── {shot_id}_prompt.md
│   └── manifest.md
└── generated/                          ← video generation output
    ├── generation_log.md
    └── {shot_id}/
        ├── v1.mp4                      ← first take
        ├── v2.mp4                      ← retake (if needed)
        └── selected.mp4                ← copy or symlink of chosen take
```

---

## Shot ID Convention

Shot IDs are structured as: `S{scene_number_padded}_SH{shot_number_padded}`

- Scene numbers: two digits, zero-padded — `S01`, `S02`, ... `S21`
- Shot numbers within a scene: three digits, zero-padded — `SH001`, `SH002`, `SH003`

Examples:

- `S11_SH001` — Scene 11, shot 1 (the gannet on the cradle)
- `S11_SH002` — Scene 11, shot 2 (rotor spin-up and lift)
- `S11_SH003` — Scene 11, shot 3 (receding into forward flight)

This naming ensures lexicographic sort order matches assembly order.

---

## File Naming Rules

| File Type | Pattern | Example |
|-----------|---------|---------|
| Start frame | `shots/{shot_id}/start.png` | `shots/S11_SH001/start.png` |
| End frame | `shots/{shot_id}/end.png` | `shots/S11_SH001/end.png` |
| Key frame | `shots/{shot_id}/key{NN}.png` | `shots/S11_SH001/key01.png` |
| Prompt | `prompts/{shot_id}_prompt.md` | `prompts/S11_SH001_prompt.md` |
| Generated clip take | `generated/{shot_id}/v{N}.mp4` | `generated/S11_SH001/v1.mp4` |
| Selected take | `generated/{shot_id}/selected.mp4` | `generated/S11_SH001/selected.mp4` |

Never place generated clips directly in the project root or in a flat directory. The
nested structure is required for multi-shot productions where dozens of clips will be
generated.

---

## Generation Log

Maintain a running log at `generated/generation_log.md`. Add one row immediately after
each video generation API call — before checking the result.

### Format

```markdown
# Generation Log

| Shot ID | Sub-clip | Take | Model | Job ID | Status | Output URL | Local file | File size | Actual resolution | Review | Prompt hash | Notes | Duration seconds | Transition type | Transition duration | Mute generated audio | Forced generated audio | Scene ID | Prompt file | Continuity flags |
|---------|----------|------|-------|--------|--------|------------|------------|-----------|-------------------|--------|-------------|-------|------------------|-----------------|---------------------|----------------------|------------------------|----------|-------------|------------------|
| S11_SH001 | A | v1 | seedance_2_0 | b767b7e1-32c6-48cb-821e-ccd260ff638b | completed | https://example.invalid/video.mp4 | generated/S11_SH001/selected.mp4 | 21MB | 1920x1080 | accepted | sha256:abc123 | Consistent subject identity; start/end anchor | 8 | cut | 0 | false | false | SC-11 | prompts/S11_SH001_prompt.md | eyeline;prop reset |
```

### Required Fields

- **Shot ID:** From the shot spec
- **Sub-clip:** `A` for a single clip, or the decomposed sub-clip ID
- **Take:** v1, v2, etc.
- **Model:** Exact model ID used
- **Job ID:** The UUID returned by the generation API — this is the only retrieval handle
- **Status:** pending / in_progress / completed / failed
- **Output URL:** Provider URL returned by the generation API
- **Local file:** Project-root-relative downloaded clip path
- **File Size:** Size of the downloaded local clip, for capacity planning
- **Actual Resolution:** Pixel dimensions measured from the downloaded clip
- **Review:** required / optional / accepted / retake / blocked
- **Prompt hash:** Hash of the submitted generation prompt
- **Notes:** Any anomalies, quality issues, or decisions made on review
- **Duration seconds:** Decimal clip duration used for editor timeline placement
- **Transition type / duration:** Manifest transition intent for the next boundary
- **Mute / forced generated audio:** Audio state for downstream editor handoff
- **Scene ID, Prompt file, Continuity flags:** Traceability metadata for review

### Why Job IDs Are Critical

The generation API returns a job ID when a clip is submitted. This ID is the only way
to:

- Retrieve the clip URL after generation completes
- Trace a specific clip back to its source shot
- Order a retake if the clip is rejected

If the job ID is not logged immediately, it may be lost. An unlogged job is effectively
an anonymous clip — you can watch it but you cannot manage it.

---

## Retake Workflow

1. Review the generated clip against the shot specification and storyboard frames.
2. Identify the failure: wrong action, wrong style, identity drift, continuity break,
   audio mismatch, etc.
3. Diagnose the cause: prompt vocabulary, insufficient start/end frame anchoring,
   wrong model, bad storyboard frame used as reference.
4. Fix the root cause before regenerating:
   - Update the prompt (draw from keyword library; strengthen action description)
   - Regenerate the storyboard frame if it was the issue
   - Change the model if routing was wrong
5. Generate take v2. Log it.
6. Compare v1 and v2. Select the better take. Copy to `selected.mp4`.
7. Record selection decision in the generation log notes column.

---

## Assembly Order

When assembling clips into a sequence:

- Use the `selected.mp4` files or explicitly selected local take paths, not provider URLs
- Assemble in manifest order, not filesystem order
- Check `clip_boundary` in the manifest: `continuous` means match the cut precisely;
  `scene_cut` allows a hard cut
- Preserve transition type, transition duration, and transition notes for
  `media-project`

The manifest at `prompts/manifest.md` contains the full ordered list with clip
boundaries and transition intent. Use it as the assembly instruction.

## Manifest Path Contract

The manifest must name the exact files that `video-generator` should upload. Use the
canonical shot-specifier frame paths unless a project has explicitly overridden them:

```text
shots/{shot_id}/start.png
shots/{shot_id}/end.png
shots/{shot_id}/key{NN}.png
```

Paths should be project-root-relative for reviewability. Add absolute paths in the media
manifest during upload. Do not rely on `video-generator` to infer alternate
scene-inventory paths from shot IDs; if a non-canonical file is required, put that exact
path in `prompts/manifest.md` and the prompt file's `Reference Audit`.

---

## Archiving

After a production is complete:

- Keep all storyboard frames (`shots/`)
- Keep all prompts (`prompts/`)
- Keep the generation log (`generated/generation_log.md`)
- Keep only the selected takes (`generated/{shot_id}/selected.mp4`) unless storage
  permits keeping all takes
- Do not delete the reference images (`image_out/`) — they are the consistency anchors
  for any future reshoots or extensions
