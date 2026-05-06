# Consistency Verification Guide

Read this file before beginning Phase 13 (Consistency Verification). It defines the
vision-based QA procedures for checking generated shot frames against reference images
and against each other.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Severity Classification](#2-severity-classification)
3. [Check Procedures](#3-check-procedures)
4. [Regeneration Protocol](#4-regeneration-protocol)
5. [Report Format](#5-report-format)

---

## 1. Overview

Consistency verification uses the agent's vision capabilities to compare generated shot
frames against reference images and against each other. The goal is to catch and fix
visual inconsistencies before handoff to `shot-specifier` and video generation, where
correction costs an entire shot regeneration.

This pass is mandatory remediation work, not an informational report. The agent must
action the findings before handoff: regenerate or correct BLOCK issues, resolve WARN
issues when the fix is clear, and convert any remaining WARN issue into a concrete
constraint for `shot-specifier`.
BLOCK findings are terminal until fixed. Do not downgrade BLOCK to WARN after retry
exhaustion; either remediate the frame or stop the workflow with the unresolved BLOCK
listed in the consistency report.

Every finding is an action item requiring remediation before handoff. Phase 13 must
enforce per-shot prop consistency against the primary prop reference, cross-shot prop
identity across all frames for each named prop, and recurring visual element
consistency across every shot where the element is visible.

### Verification Pass Order

Execute checks in this order (each subsequent check assumes prior checks have passed):

1. **Intra-shot: Start–end interpolatability** (per shot)
2. **Character consistency** (per shot, per character)
3. **Location consistency** (per shot)
4. **Prop consistency** (per shot, per visible prop)
5. **Recurring visual element consistency** (per shot and across all frames where visible)
6. **Intra-shot lighting coherence** (per shot: start vs key frames vs end)
7. **Cross-shot continuity** (sequential shots with continuous boundary)
8. **Thematic image consistency** (thematic images vs their source scene refs)

---

## 2. Severity Classification

| Severity | Code | Meaning | Action |
|----------|------|---------|--------|
| **BLOCK** | `B` | Inconsistency will produce unusable video or visible continuity error | Must regenerate or correct before handoff |
| **WARN** | `W` | Inconsistency is noticeable but may survive video generation | Resolve when clear; otherwise pass an explicit downstream constraint |

All findings must be recorded as action items. Use **BLOCK** when the issue prevents
handoff; use **WARN** when the issue can be remediated by a concrete downstream
constraint after local fixes are exhausted.

### Classification Rules

| Issue | Default Severity |
|-------|-----------------|
| Subject completely static between start and end (no interpolatable change) | **BLOCK** |
| Character face substantially different from primary reference | **BLOCK** |
| Character outfit wrong (different garment, wrong colour) | **BLOCK** |
| Location architecture/layout contradicts reference | **BLOCK** |
| Prop missing from frame when shot spec requires it | **BLOCK** |
| Lighting direction reversed between start and end | **BLOCK** |
| End frame of shot N incompatible with start frame of shot N+1 (continuous boundary) | **BLOCK** |
| Character face slightly different but recognisable | **WARN** |
| Colour temperature shift between start and end (minor) | **WARN** |
| Background detail inconsistency (minor) | **WARN** |
| Depth of field inconsistency between frames | **WARN** |
| Prop detail variation (minor shape/colour shift) | **WARN** |
| Grain/texture slightly different from style anchor | **WARN** |
| Minor composition drift from specified framing | **WARN** |

---

## 3. Check Procedures

### 3.1 Start–End Interpolatability

**Input:** Start frame and end frame for a single shot.

**Procedure:**

1. Examine both frames side by side (or in sequence)
2. Identify what has changed between them
3. Classify the change type:
   - **Position/pose change**: Subject has moved, changed posture, or shifted orientation → PASS
   - **State change**: Something has opened/closed, appeared/disappeared, changed expression → PASS
   - **Composition change**: Camera motion has shifted the framing → PASS
   - **Only lighting/background changed**: Subject is in identical position and state → FAIL (BLOCK)
   - **No discernible change**: Frames are near-identical → FAIL (BLOCK)

**Failure description format:**

```text
BLOCK: S{XX}_SH{XXX} — Start–end interpolatability failure.
Subject {description} is static between frames; only {what changed} differs.
The video model will produce unnatural motion or a frozen subject.
Regenerate end frame with explicit {position/pose/state} change.
```

### 3.2 Character Consistency

**Input:** Shot frame (start or end) + character primary reference image.

**Procedure:**

1. Compare the character in the shot frame to the primary reference
2. Check each attribute:
   - Face shape, features, skin tone
   - Hair colour, length, style
   - Body proportions and build
   - Outfit (correct garment, correct colour, correct condition)
   - Distinguishing features (scars, tattoos, accessories)
3. Score as PASS / WARN / BLOCK

**Tolerance:** AI image generation produces inherent variation. The standard is: would a
viewer recognize this as the same character? Minor variations in facial angle, slight
colour shifts due to scene lighting, and natural expression changes are acceptable.
Wholesale face changes, wrong hair colour, or incorrect clothing are not.

### 3.3 Location Consistency

**Input:** Shot frame + location reference image (matching condition).

**Procedure:**

1. Compare the environment in the shot to the location reference
2. Check:
   - Architecture and layout (walls, doors, windows in correct positions)
   - Materials and textures (concrete vs brick, wood vs metal)
   - Fixed objects and furniture (desks, monitors, fixtures)
   - Scale and proportion (room size, ceiling height)
3. Score as PASS / WARN / BLOCK

**Note:** Camera angle will differ between the reference and the shot. Focus on
structural consistency, not identical framing.

### 3.4 Prop Consistency

**Input:** Shot frame + prop reference image.

**Procedure:**

1. Identify the prop in the shot frame
2. Compare against the prop reference:
   - Shape and silhouette
   - Colour and material
   - Size relative to other objects
   - Condition/state (if a specific state variant was expected)
3. Score as PASS / WARN / BLOCK

### 3.5 Recurring Visual Element Consistency

**Input:** Shot frame + locked recurring visual element reference image.

Recurring visual elements are objects, fixtures, interfaces, machinery, furniture
layouts, or set dressing that appear in more than two shots and would be noticed if
their appearance changed. Examples include monitor banks, screen colour groupings,
inspection robots, grow-light strip arrays, cargo pods, cabinets, signage clusters, and
workstation layouts.

**Procedure:**

1. Identify each recurring visual element visible in the shot frame.
2. Compare against the locked element reference:
   - Overall layout and silhouette
   - Count and arrangement of repeated parts
   - Colour, screen state, lighting pattern, and material
   - Scale relative to characters and surrounding architecture
3. Gather all frames containing the element and view them together.
4. Score as PASS / WARN / BLOCK if the element appears redesigned, rearranged, or
   materially different across shots.

### 3.6 Intra-Shot Lighting Coherence

**Input:** Start frame, all key frames, and end frame for a single shot.

**Procedure:**

1. Examine the sequence in order
2. Check for consistent:
   - Light direction (shadows should fall the same way unless the action explicitly involves a light-source change)
   - Colour temperature (warm/cool should match unless the action describes a change)
   - Exposure level (brightness should be consistent unless the action describes a change)
   - Specular highlights (position on reflective surfaces)
3. Score as PASS / WARN / BLOCK

**Exception:** If the shot explicitly describes a lighting change (e.g., sunrise, lights
turning on), the change is expected and should be checked for plausibility rather than
consistency.

### 3.7 Cross-Shot Continuity

**Input:** End frame of shot N + start frame of shot N+1 (only when boundary is
`continuous`).

**Procedure:**

1. These frames should be identical or nearly identical (since the start frame of N+1
   reuses the end frame of N)
2. If they are the same file, this check is automatic — PASS
3. If they are different files (error in the pipeline), flag as BLOCK

**Also check for:**

- Subject position/pose matches between end of N and start of N+1
- Wardrobe is the same
- Environment is the same
- Lighting is the same
- Any props are in the same position

### 3.8 Thematic Image Consistency

**Input:** Each thematic image (from Phase 9) + corresponding scene references.

**Procedure:**

1. Compare the thematic image against relevant character, location, and prop references
2. Verify that the thematic image matches the established visual world
3. Flags are WARN only (thematic images are editorial, not generation inputs)

---

## 4. Regeneration Protocol

When a BLOCK issue is found:

### Step 1: Diagnose

Identify the root cause:

- **Prompt insufficiency**: The generation prompt did not adequately describe the
  required element → Fix the prompt and regenerate
- **Reference insufficiency**: The reference image did not adequately constrain the
  generation → Consider generating a better reference first, then regenerate
- **Model limitation**: The generation model cannot achieve the required result with
  current references and prompting → Stop with a terminal error; do not hand off until
  the shot, references, or frame plan is changed and the BLOCK clears

### Step 2: Regenerate

- Regenerate only the failing frame, not the entire shot set
- Use the same references as the original generation
- Modify the prompt based on the diagnosis (add specificity where the failure occurred)
- If the start frame is regenerated, all subsequent frames in that shot (key frames,
  end frame) must also be regenerated (they depend on the start frame)
- If the end frame is regenerated and the next shot has `first_frame_reuse = yes`,
  update the next shot's start frame reference

### Step 3: Re-verify

After regeneration, re-run the relevant checks on the new frame. If the issue persists
after three regeneration attempts, stop with an unresolved BLOCK and report the exact
frame, reference, and check that failed.

### Regeneration Limit

Maximum **3 regeneration attempts** per frame. After three failures:

1. Log the issue as BLOCK with note "Regeneration limit reached"
2. Stop the workflow; do not proceed with the best available frame
3. Include the terminal issue in the consistency report with full details

WARN findings that cannot be fixed locally must remain WARN only when they can be
carried as concrete `shot-specifier` constraints. If a WARN finding blocks handoff, mark
it BLOCK and stop until it is remediated.

---

## 5. Report Format

Output the consistency report as:

**Filename:** `reports/consistency_report.md`

```markdown
# Consistency Report

* **Project:** {project_name}
* **Date:** {date}
* **Total shots checked:** {N}
* **BLOCK issues found:** {N} (resolved: {N}, unresolved: {N})
* **WARN issues found:** {N}

---

## BLOCK Issues

### {Issue ID}: {Shot ID} — {Check Name}

* **Severity:** BLOCK
* **Status:** {Resolved / Unresolved terminal stop}
* **Description:** {What is wrong}
* **Frame(s) affected:** {filename(s)}
* **Reference compared:** {filename}
* **Regeneration attempts:** {N}
* **Resolution:** {What was done to fix it, or why the workflow stopped}

---

## WARN Issues

### {Issue ID}: {Shot ID} — {Check Name}

* **Severity:** WARN
* **Description:** {What is wrong}
* **Frame(s) affected:** {filename(s)}
* **Recommendation:** {Suggested action for human review}

---

## Summary

{Brief narrative summary of overall consistency quality. Note any patterns in failures
(e.g., "Character X's hair colour drifts across night scenes" or "Location Y's window
position is unstable"). Flag any capability gaps that may affect video generation.}
```

### Issue ID Format

`CV-{NNN}` — sequential, starting at CV-001.
