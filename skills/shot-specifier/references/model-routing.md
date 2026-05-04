# Video Model Routing

Read this before Phase 7 (Video Prompt Assembly). Covers how to route individual shots
to the appropriate video generation model.

> **Note:** This document is a working stub. Full empirical routing guidance requires
> systematic research. The research brief is at:
> `notes/further-research-video-model-routing.md`
>
> As the research is completed, update this document with confirmed routing rules,
> per-model prompt vocabulary guidance, and known failure modes. Until then, use the
> working heuristics below and log all model choices with rationale in the generation
> log so patterns can be established retrospectively.

---

## Available Models (Higgsfield)

| Model ID | Provider | Type | Key Characteristics |
|----------|---------|------|---------------------|
| `seedance_2_0` | Bytedance | Video | Reference-driven; consistent subject identity across frames; supports start/end frame anchoring; image/video/audio references; 4–15s; up to 1080p |
| `seedance_1_5` | Bytedance | Video | Reliable motion, improved quality over earlier versions; start/end frame support; 4/8/12s |
| `kling3_0` | Kling | Video | Multi-shot; audio generation; motion transfer; see model spec for full capabilities |
| `marketing_studio_video` | Higgsfield | Video | Commercial/product/ads; URL-driven; see show_marketing_studio tool |

---

## Working Routing Heuristics

These are first-pass heuristics based on limited empirical testing. Treat them as
starting hypotheses, not confirmed rules. Log deviations and results.

### Use `seedance_2_0` when:

- The shot requires **consistent subject identity** across the clip (a specific UAV,
  a specific character, a specific prop that must look the same throughout)
- Start and end frames are available as reference anchors
- The shot involves reference-driven subject motion (take-off, landing, character
  performing a specific action)
- Audio reference is available and needed to drive the clip

### Use `seedance_1_5` when:

- Consistent identity is important but `seedance_2_0` is not available or produces
  artefacts for this shot type
- Shot requires reliable motion on a simpler subject
- Durations of exactly 4, 8, or 12 seconds are required

### Prefer `kling3_0` when:

- The shot requires multi-shot sequencing within a single generation call
- Audio generation from the model is required
- Motion transfer from a reference clip is the primary input

### Machine Vision / Drone POV Shots

The optimal model for clean digital machine-vision shots (drone POV, telemetry screens,
surveillance feeds) has not yet been empirically confirmed. See the research brief.
Working hypothesis: `seedance_2_0` can handle these if the prompt explicitly suppresses
grain and organic movement using the POV override vocabulary from the keyword library.
Confirm this hypothesis and update.

---

## Shot-Type Routing Table (Working)

| Shot Type | Preferred Model | Rationale | Confidence |
|-----------|----------------|-----------|------------|
| Consistent subject action (UAV lift-off, character entering room) | `seedance_2_0` | Strong start/end frame anchoring; identity consistency | Tested once |
| Aerial establishing / landscape | `seedance_2_0` | Start frame anchoring; environmental motion | Untested |
| Drone POV / machine vision | `seedance_2_0` with POV override | Hypothesis only | Untested |
| Dialogue CU with character identity | `seedance_2_0` | Character consistency features | Untested |
| Multi-shot sequence | `kling3_0` | Multi-shot capability | Untested |
| Insert / detail shot | `seedance_1_5` or `seedance_2_0` | Short duration; simple subject | Untested |
| Product / commercial | `marketing_studio_video` | Designed for this use case | N/A |

---

## Model Prompt Vocabulary Differences

Video models do not all interpret the same prompt vocabulary the same way. Known
differences (expand as research is completed):

- `seedance_2_0` responds to filmstock and grain vocabulary in the prompt, but the
  degree of control is uncertain — the start frame images may dominate over textual
  style instructions.
- POV override vocabulary ("digital-flat, no grain, gimbal-stabilised") has not been
  confirmed to suppress grain in `seedance_2_0`; verify and update.

---

## Logging Requirements

For every video generation call, log in `generated/generation_log.md`:

- Shot ID
- Date
- Model used
- Job ID (critical — this is the only retrieval handle)
- Duration
- Status
- Take number
- Routing rationale (why this model was chosen)
- Result quality notes

The routing rationale in the log is the primary mechanism for building empirical evidence
for future routing decisions. Do not skip it.

---

## Updating This Document

When research (see `notes/further-research-video-model-routing.md`) produces confirmed
routing rules:

1. Move confirmed rules from the "Working" sections to a "Confirmed" section
2. Update confidence ratings in the shot-type routing table
3. Document any model-specific prompt vocabulary differences
4. Log the source (research session, test generation) for each confirmed rule
