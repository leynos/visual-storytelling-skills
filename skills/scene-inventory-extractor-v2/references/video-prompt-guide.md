# Video Prompt Assembly Guide

Read this file before beginning Phase 13 (Video Prompt Assembly). It defines prompt
structure, transition_description requirements, physical consistency constraints, and
audio handling.

---

## Table of Contents

1. [Prompt Structure](#1-prompt-structure)
2. [Transition Description Requirements](#2-transition-description-requirements)
3. [Transition Description Examples](#3-transition-description-examples)
4. [Physical Consistency Constraints](#4-physical-consistency-constraints)
5. [Audio in Prompts](#5-audio-in-prompts)
6. [Duration Rules](#6-duration-rules)
7. [Clip Boundary Handling](#7-clip-boundary-handling)
8. [Prompt File Format](#8-prompt-file-format)
9. [Common Mistakes](#9-common-mistakes)

---

## 1. Prompt Structure

Each video prompt is a self-contained specification that, combined with the start frame,
end frame, and any key frames, fully defines what the video model must produce.

### Template

```markdown
# Shot {shot_id} — Video Prompt

## Metadata
- **Shot ID:** {S{XX}_SH{XXX}}
- **Duration:** {4 / 6 / 8} seconds
- **Pacing:** {slow / moderate / fast}
- **Clip boundary (next):** {continuous / scene_cut}

## Frames
- **Start frame:** shots/{shot_id}/start.png
- **End frame:** shots/{shot_id}/end.png
- **Key frames:** {shots/{shot_id}/key01.png, ... or "None"}

## Prompt

[STYLE] {Visual style — 1 sentence}
[FILMSTOCK] {Format, grain character, colour process — 1 sentence describing the look}
[SCENE] {Environment description — where are we, what surrounds us}
[FRAMING] {Shot size + angle + lens effect + camera motion}
[PACING] {slow / moderate / fast — and what that means for this shot}
[ACTION] {transition_description — 2–4 sentences, see §2}
[SUBJECT] {Subject appearance — key features that must remain consistent throughout}
[AUDIO] {See §5}
[DURATION] {4 / 6 / 8 seconds}

## References Used
- Character: refs/characters/{name}/primary.png
- Location: refs/locations/{name}/{condition}.png
- Props: refs/props/{name}/primary.png (if applicable)

## Consistency Notes
- {Any specific consistency concerns for this shot}
- {Cross-reference to consistency report if flagged}
```

---

## 2. Transition Description Requirements

The `[ACTION]` field is the most critical part of the prompt. It directly drives the
video model's interpolation between start and end frames.

### Mandatory Components

| Component | What to Include | Why |
|-----------|-----------------|-----|
| **Subject appearance** | Key visual features (clothing colour, hair, distinguishing marks) | Prevents the model drifting the subject's appearance mid-shot |
| **Movement trajectory** | Direction, speed, path through space | Defines the interpolation vector |
| **State changes** | What opens/closes, appears/disappears, changes expression | Gives the model explicit transition targets |
| **Existence statements** | What is present throughout the entire duration | Prevents objects popping in or out mid-frame |

### Length Requirement

**Minimum 2–4 sentences.** One-line descriptions are insufficient and will produce
unpredictable or static video.

### Writing Style

- Use present tense, continuous aspect: "The woman walks", "The door swings open"
- Be spatially explicit: "from left edge to right edge", "toward camera", "away and to the right"
- State speed: "slowly", "at a moderate pace", "rapidly"
- Include timing cues for multi-event shots: "First... then... finally..."

---

## 3. Transition Description Examples

### Insufficient vs Sufficient

| Insufficient | Sufficient |
|--------------|------------|
| "Person walks across room" | "A woman in a dark blue coat walks steadily from the left edge of frame toward the right, passing a wooden desk at the midpoint. She maintains upright posture throughout, arms at her sides. The desk, chair, and window behind her remain stationary and visible for the full duration." |
| "Door opens" | "The heavy oak door begins closed and flush with the frame. It swings inward slowly, hinge on the left side, revealing the corridor behind it over three seconds. Warm light from the corridor spills onto the dark tile floor, the bright rectangle growing as the door opens wider. The door handle and frame remain fixed in position." |
| "Camera pans right" | "The camera pans slowly from left to right across the control room. We begin facing the left wall where three monitors display green status lights. The pan reveals the central console with its operator seated, then continues to the right wall where a large window shows rain against glass. The overhead fluorescent lighting remains consistent throughout. The pan covers approximately 120 degrees over six seconds." |
| "Light changes" | "The room begins in pre-dawn blue-grey light from the window. Over eight seconds, sunrise light gradually warms the space: first a thin orange line on the far wall, then spreading to fill the room with golden-amber light. The figure sleeping in the bed remains motionless throughout. Furniture, bedding, and wall details stay fixed; only the light colour and intensity change." |

### Complex Multi-Event Shot

```
A man in a grey suit sits at a desk typing. He pauses after two seconds, looks up toward
the doorway at the right edge of frame. A woman in a red dress enters through the doorway,
walking three steps into the room and stopping beside the desk. The man pushes his chair
back slightly. Throughout, the desk, computer monitor, desk lamp, and bookshelf behind
them remain fixed. Office overhead lighting stays consistent. The man's suit jacket and
the woman's dress colour do not change.
```

---

## 4. Physical Consistency Constraints

Before finalising each prompt, verify that the described motion is physically achievable.

### Camera Motion Constraints

| Motion | Physical Constraint | Verification Question |
|--------|--------------------|-----------------------|
| **Pan / tilt** | Camera fixed to tripod; rotation only | Does the described arc stay within a single rotational sweep? |
| **Dolly / tracking** | Camera translates through space | Is the distance traversable at the described speed in the given duration? |
| **Crane** | Camera rises/falls + optional lateral | Is the height change and lateral movement achievable? |
| **Arc** | Camera orbits subject | Does the arc angle + distance fit the duration? Is the path unobstructed? |
| **Zoom** | Optical only; no spatial translation | Are start and end focal lengths within a realistic zoom range? |
| **Steadicam** | As dolly but limited to walking speed | Would a human operator cover this distance in this time? |
| **Handheld** | As Steadicam with permitted irregularity | Same distance check; small movements OK |

### Subject Motion Constraints

| Check | Verification |
|-------|-------------|
| Walking speed | ~1.4 m/s normal; ~2 m/s brisk; ~3.5 m/s jogging |
| Arm movements | Full gesture cycle: ~0.5–1.5 seconds |
| Head turn | Natural: ~0.5–1 second for 90° |
| Standing to sitting | ~1.5–2 seconds |
| Door opening | ~1.5–3 seconds depending on weight and speed |

### Duration vs Action

| Duration | Suitable For |
|----------|-------------|
| **4 seconds** | Single small action, subtle shift, held moment, insert detail |
| **6 seconds** | One complete action, moderate camera move, dialogue beat |
| **8 seconds** | Complex action, multiple subjects, large camera move, establishing |

If the described action does not fit the duration, either extend the duration, reduce
the action, or split into two shots.

---

## 5. Audio in Prompts

### Audio Types and Handling

| Audio Type | Include in Prompt? | Format |
|------------|-------------------|--------|
| **On-screen dialogue** | Yes | `"[Character] says: '{text}'" with tone and language` |
| **On-screen singing** | Yes | `"[Character] sings: '[lyrics]'" with style and language` |
| **Sound effects** | Yes | Source + quality: `"Heavy rain on metal roof; distant thunder"` |
| **Embedded BGM** | Yes (if diegetic or embedded) | Style, BPM, instruments, mood |
| **Separate BGM** | No — end prompt with `"No background music."` | Handled in post |
| **Narration** | No — generated separately per clip via TTS | Handled in post |

### Critical Audio Rules

- **Never use TTS for on-screen dialogue or singing.** The video model generates
  audio with lip sync.
- **Narration is generated clip-by-clip**, not all at once.
- **When mixing**: preserve all audio tracks (video audio + narration + BGM). Overlay,
  never replace. Narration must be clearly audible.

### Audio in Prompt — Example

```
[AUDIO] Heavy rain on corrugated roof (constant bed). At 2 seconds, a phone buzzes
twice on the metal desk (sharp, tinny). Character mutters "Not now" in English,
irritated, under breath. No background music.
```

---

## 6. Duration Rules

Shots must be **4, 6, or 8 seconds**. Each shot contains **one action in one scene**.

### Duration Selection

| Choose | When |
|--------|------|
| **4 seconds** | Insert/detail shots; reaction beats; static or near-static frames; punctuation shots |
| **6 seconds** | Standard action shots; dialogue lines; moderate camera movement; most shots default here |
| **8 seconds** | Complex choreography; large camera moves; establishing/geography; multi-beat actions |

### Splitting Oversized Shots

If a shot description requires more than 8 seconds:
1. Identify the natural mid-point (action completion, beat change, breath)
2. Split into two shots at that point
3. Set the boundary between them to `continuous`
4. The end frame of shot A becomes the start frame of shot B (no regeneration needed)

---

## 7. Clip Boundary Handling

### Continuous Boundary

When `clip_boundary = continuous`:
- The end frame of the current shot IS the start frame of the next shot
- Do not regenerate — reuse the file
- The visual style, lighting, and subject state must match perfectly
- The video prompts for both shots must describe a seamless join

### Scene Cut Boundary

When `clip_boundary = scene_cut`:
- The next shot begins fresh with its own start frame
- No continuity constraint between end of current and start of next
- Location, lighting, time, and subject state may all change

### Field Dependencies

These must be internally consistent across adjacent shots:

| This Shot | Next Shot | Constraint |
|-----------|-----------|------------|
| `clip_boundary = continuous` | `first_frame_reuse = yes` | End frame of this shot = start frame of next |
| `clip_boundary = scene_cut` | `first_frame_reuse = no` | Generate a new start frame |

---

## 8. Prompt File Format

Write one file per shot:

**Filename:** `prompts/shot_{shot_id}_prompt.md`

Contents follow the template in §1. The file must be parseable: a downstream process or
agent will extract the `## Prompt` section as the literal input to the video model, and
the `## Frames` section as the list of image file paths to attach.

### Manifest

After generating all prompt files, produce a manifest:

**Filename:** `prompts/manifest.md`

```markdown
# Video Prompt Manifest

| Shot ID | Duration | Frames | Prompt File | Notes |
|---------|----------|--------|-------------|-------|
| S01_SH001 | 6s | start, end | prompts/shot_S01_SH001_prompt.md | |
| S01_SH002 | 4s | start, end, key01 | prompts/shot_S01_SH002_prompt.md | Continuous from S01_SH001 |
| ... | ... | ... | ... | ... |
```

---

## 9. Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| One-line transition description | Video model produces static or random motion | Expand to 2–4 sentences with all four mandatory components |
| No existence statements | Objects pop in/out mid-shot | Add "X remains visible throughout" for all persistent elements |
| Motion exceeds duration | Unnatural speed or teleporting | Reduce action scope or extend duration |
| Pan described as dolly | Camera stays fixed but content pans as if translating | Use correct motion term (pan = rotation, dolly = translation) |
| Lighting described in action but not in frame specs | Start/end frames don't match the described change | Ensure frame specs and transition description agree |
| Subject appearance omitted from transition | Model changes subject's clothing/features mid-shot | Always restate key visual features in the [SUBJECT] field |
| Audio conflicts with action timing | Dialogue or sound effect at wrong moment | Time-stamp audio cues within the transition description |
| Forgetting "No background music." | Model adds random music | Always end non-BGM prompts with this line |
