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

## {Project Name}

| Shot ID | Date | Model | Job ID | Duration | Status | Take | Routing Rationale | Notes |
|---------|------|-------|--------|----------|--------|------|-------------------|-------|
| S11_SH001 | 2026-05-04 | seedance_2_0 | b767b7e1-32c6-48cb-821e-ccd260ff638b | 8s | completed | v1 | Consistent subject identity; start/end anchor | |
| S11_SH002 | 2026-05-04 | seedance_2_0 | — | 6s | pending | v1 | | |
```

### Required Fields

- **Shot ID:** From the shot spec
- **Date:** ISO 8601 (YYYY-MM-DD)
- **Model:** Exact model ID used
- **Job ID:** The UUID returned by the generation API — this is the only retrieval handle
- **Duration:** Clip duration in seconds
- **Status:** pending / in_progress / completed / failed
- **Take:** v1, v2, etc.
- **Routing Rationale:** One sentence explaining why this model was chosen for this shot
- **Notes:** Any anomalies, quality issues, or decisions made on review

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

- Use the `selected.mp4` files (not the vN originals)
- Assemble in shot ID order (lexicographic = scene and shot order)
- Check `clip_boundary` in the manifest: `continuous` means match the cut precisely;
  `scene_cut` allows a hard cut

The manifest at `prompts/manifest.md` contains the full ordered list with clip
boundaries. Use it as the assembly instruction.

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
