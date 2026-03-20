---
name: scene-inventory-extractor
description: >
  End-to-end production-prep workflow: extracts comprehensive scene inventories from
  narrative writing, extracts continuity inventory and reset-critical state before prompt
  writing, generates all reference images (characters, locations under multiple
  angles/conditions, props), produces start/end/keyframe shot references with consistency
  verification, and assembles complete video prompts for every shot. Use when analysing
  stories, scripts, or prose to create production-ready scene breakdowns with full visual
  asset pipelines. Also trigger when the user mentions "scene breakdown", "shot list",
  "character bible", "location bible", "continuity inventory", "reference images",
  "video prompts", "storyboarding", or any request to prepare narrative material for AI
  video generation. This skill expects access to an image-generation MCP and vision
  capabilities.
---

# Scene Inventory Extractor

Systematic workflow for extracting comprehensive scene inventories from narrative source
material and preparing every visual asset required for AI video generation. Continuity is
a first-class deliverable: extract story-state, dressing-state, and object-state before
writing prompts so a crew can reset scenes accurately when production shoots out of
order.

## Execution Context

This skill is designed for a command-line agent with:

- **Image generation MCP** (e.g. `generate_image`, `generate_image_variation`)
- **Vision capabilities** (ability to inspect generated images for consistency)
- **File system access** (structured output directories)

All image generation and verification runs **silently** — no user confirmation gates
during generation phases. Halt only on consistency failures that require human judgement.

## Workflow Overview

| Phase | Name | Output |
|-------|------|--------|
| 1 | Source Analysis | Annotated reading notes |
| 2 | Creative Pillars | Visual aesthetic + storytelling style + **cinematography specification** |
| 3 | Narrative Spine | Structure, themes, turnpoints |
| 4 | Character Bible | Character entries with **reference-image specifications** |
| 5 | Locations Bible | Location entries with **multi-angle, multi-condition scouting specs** |
| 6 | Props Bible | Props with physical descriptions and ref-image specs |
| 7 | Scene Inventory | Per-scene breakdowns |
| 8 | Continuity Inventory | Character/location/prop state tracking across scenes |
| 9 | Shot Lists | Shot tables with full cinematography fields |
| 10 | Thematic Image Plan | Key narrative-beat images |
| 11 | Reference Image Generation | All character, location, and prop reference images |
| 12 | Shot-Frame Generation | Start frame, end frame, and key frames per shot |
| 13 | Consistency Verification | Vision-based QA pass; flag failures |
| 14 | Video Prompt Assembly | Complete prompt per shot, ready for generation |
| 15 | Output Assembly | Final compiled document + asset manifest |

> **Read order for reference files:** Before starting Phase 2, read
> `references/cinematography-specification.md`. Before Phase 8, read
> `references/continuity-inventory.md`. Before Phase 11, read
> `references/reference-image-guide.md`. Before Phase 14, read
> `references/video-prompt-guide.md`. The consistency verification procedure in Phase 13
> is defined in `references/consistency-verification.md`.

---

## Phase 1: Source Analysis

Read the source material twice. First pass: absorb narrative arc, tone, world. Second
pass: extract with pen in hand.

### First-Pass Questions

- What is the dominant visual mood? Name it.
- Where does the camera naturally want to be? (Observational? Intimate? Surveillance?)
- What objects carry narrative weight?
- What spaces define the world?
- Who moves through this world and how do they move?
- What is the **light** doing? (Time of day, weather, artificial sources)
- What is the **sound** doing? (Ambient beds, punctuations, silence)

---

## Phase 2: Creative Pillars

> **Prerequisite:** Read `references/cinematography-specification.md` before this phase.

Extract and name the visual, storytelling, and cinematographic approaches.

### 2.1 Visual Aesthetic

```
**Name:** {Evocative 2–4 word title}
**Definition:** {One sentence capturing look and feel}
```

Specify: Palette (3–5 named colours), Lighting rules, Texture rules, Camera grammar,
Warmth rules. See `templates/scene-inventory-template.md` for field structure.

### 2.2 Storytelling Style

```
**Name:** {Evocative 2–4 word title}
**Definition:** {One sentence capturing narrative approach}
```

Specify: Narrative rules, Rhythm rules, Scale rules.

### 2.3 Cinematography Specification

This is **new territory** relative to pure script breakdown. Define the physical and
post-production characteristics of the image pipeline:

| Element | What to Define |
|---------|----------------|
| **Format / filmstock** | Gauge (Super 8, 16 mm, 35 mm, 65 mm, digital sensor equivalent), aspect ratio, native resolution |
| **Grain structure** | Fine/medium/coarse; organic vs digital noise; grain response to exposure |
| **Colour process** | Photochemical reference (Kodachrome, Ektachrome, Vision3 500T) or digital LUT family |
| **Colour timing** | Overall bias (cool, warm, cross-processed); scene-specific timing rules |
| **Grading rules** | Lift/gamma/gain tendencies; crush blacks or preserve shadow detail; highlight rolloff |
| **Lens language** | Primes vs zooms; focal length range; anamorphic vs spherical; characteristic aberrations (halation, flare, bokeh shape) |
| **Depth of field rules** | When shallow, when deep; rack-focus conventions |
| **Shutter behaviour** | Shutter angle/speed rules (180° default, or intentional motion blur/strobing) |

Full specification format and examples are in `references/cinematography-specification.md`.

---

## Phase 3: Narrative Spine

Document timeframe, structural approach, operational themes (4–6), and key turnpoints
(3–7). Themes must be operational: "Signature authority: who gets to update 'reality'"
not "The loneliness of modern existence."

---

## Phase 4: Character Bible

For each character, extract using the appropriate template from
`templates/character-template.md` (primary / functional / interface / voice-only /
collective).

**Addition — Reference Image Specification per character:**

For every character who appears on screen, append:

```
* **Reference image requirements:**
  * Primary: {Full body, neutral pose, front-facing, white background}
  * Face detail: {Head-and-shoulders, ¾ angle}
  * Expression set: {List key expressions needed by the story}
  * Wardrobe variants: {Each distinct outfit as a separate ref}
  * Action poses: {Any signature physical action}
```

Match detail to narrative weight: primary characters get full sets; functional characters
get primary + face; collectives get a representative figure.

Also record a continuity state chain per recurring on-screen character: wardrobe by
scene, carried items by scene, body-state continuity, and pocket / hand continuity
risks. "Same outfit" is not enough when carried objects or physical condition change.

---

## Phase 5: Locations Bible

> **Critical:** Locations receive the most comprehensive reference-image coverage. Each
> location that appears in more than one scene, or whose atmosphere shifts across the
> story, requires **multi-angle, multi-condition scouting**.

For each location, extract using `templates/location-template.md`.

### Scouting Specification

For each location, define:

| Scouting Dimension | What to Specify |
|--------------------|-----------------|
| **Angles** | Establishing wide, interior/working angle, character-entry POV, signature detail insert |
| **Lighting conditions** | Each distinct time-of-day or artificial-light state the story requires |
| **Weather conditions** | Each weather state the story requires (if exterior or weather-visible) |
| **Seasonal state** | If the story spans seasons and this location appears across them |
| **Narrative state** | If the location degrades, transforms, or is altered by story events |

The scouting matrix is: `angles × (lighting conditions × weather conditions × seasonal/narrative states)`. Generate the full cross-product only where the story **actually visits** that combination. Do not generate speculative combinations.

For recurring locations, add a continuity chain across appearances: first-appearance
state, subsequent appearance changes, and non-negotiable anchors that must never drift.

---

## Phase 6: Props Bible

For each significant prop (passes the significance test: narrative weight, multi-scene,
character-defining, symbolic, or physically interacted with on camera), extract physical
description, narrative function, sequence appearances.

For continuity, also record custody, state progression, set-down / pickup moments, and
scene exit status.

**Addition — Reference Image Specification per prop:**

```
* **Reference image requirements:**
  * Primary: {Object on white background, ¾ angle}
  * Detail: {Any specific detail the camera will see in ECU/INS}
  * In-context: {Object in its typical environment, if context matters}
  * State variants: {If prop changes condition across the story}
```

---

## Phase 7: Scene Inventory

For each scene (new scene on location change, significant time passage, POV shift, or
mode change):

```
#### SC-{XX}

* **Scene ID:** SC-{XX}
* **Location:** {Location name}
* **Time:** {Time of day; weather; season}
* **Lighting condition key:** {Maps to scouting matrix entry}
* **Characters present:** {Who}
* **Objective / tension:** {What's at stake}
* **What changes:** {State shift by scene end}
* **Key sensory notes:** {Smell/sound/temperature}
* **Transitions in/out:** In: {from}. Out: {to}.
* **Continuity dressing notes:**
  * Fixed location anchors: {architecture, furniture, installed fixtures}
  * Movable dressing: {objects that can shift position}
  * Character-carried items: {by character}
  * Consumables / depletion states: {food, drink, cigarettes, fuel, paper stacks}
  * Weather / dirt / damage state: {mud, blood, sweat, rain, soot, wrinkles}
  * Reset-sensitive details: {what must match across coverage and return visits}
```

---

## Phase 8: Continuity Inventory

> **Prerequisite:** Read `references/continuity-inventory.md` before this phase.

Write a separate continuity deliverable at `{project_name}_continuity_inventory.md`.
Continuity extraction is pre-generation story/state tracking, not post-generation image
QA.

Assume scenes will be shot out of order. Extract continuity so that a separate crew,
working days later, can restore the exact character, prop, and dressing state without
re-reading the source material.

---

## Phase 9: Shot Lists

Create shot tables for each sequence. Use the expanded format from
`templates/shot-list-template.md`, which now includes cinematography columns.

### Expanded Shot Table Columns

| Column | Content |
|--------|---------|
| **Shot ID** | `S{XX}_SH{XXX}` |
| **Frame** | XW / W / M / CU / ECU / POV / INS / OTS |
| **Lens** | Focal length + type (e.g. "40 mm anamorphic") |
| **Camera motion** | static / pan / tilt / dolly / zoom / crane / arc / handheld / Steadicam |
| **Visual action** | Concrete, filmable description |
| **Audio bed / notes** | What we hear; drops; motifs |
| **Narrative function** | Why this shot exists |
| **Continuity flags** | Constraints to maintain |
| **Duration** | 4 / 6 / 8 seconds |
| **Pacing** | slow / moderate / fast |
| **Clip boundary** | continuous / scene_cut (with next shot) |
| **Grain / grade note** | Any per-shot override from global cinematography spec |

### Per-Shot Frame Specification

For each shot, also record (these feed Phase 12):

```
* **Start frame:** {Framing + visible content + subject state}
* **End frame:** {Framing + visible content + subject state}
* **Key frames (if any):** {Intermediate states the interpolation must pass through}
* **Interpolatable change:** {What changes between start and end — position, pose, state, composition}
* **End-frame derivation:** edit-from-start / generate-new (see decision table in references/reference-image-guide.md)
```

> **[CRITICAL]** The end frame must show **interpolatable change** from the start frame:
> subject position/pose, subject state, or composition shift. Subtle-only changes
> (lighting, background) while the subject stays static cause unnatural video motion.

---

## Phase 10: Thematic Image Plan

Identify 8–12 key images capturing narrative beats. Specification format unchanged — see
template. These images serve double duty: editorial illustration and generation
quality-gate (if the pipeline cannot produce a convincing thematic image, it flags a
capability gap before committing to full shot generation).

---

## Phase 11: Reference Image Generation

> **Prerequisite:** Read `references/reference-image-guide.md` before this phase.

Generate all reference images silently. Order matters:

### 10.1 Style Anchor

Generate 1–2 style-anchor images that establish the global look (filmstock, grain,
palette, lighting). These become the visual-style reference for everything that follows.

### 10.2 Character References

For each character, generate in order:
1. **Primary reference** (no prior refs; full visual-style spec in prompt + white bg)
2. **Additional angles/expressions/wardrobe** (primary ref as input reference)

### 10.3 Location Scouting References

For each location, generate across the scouting matrix:
1. **Primary establishing shot** (no prior refs; full style spec in prompt)
2. **Additional angles** (primary ref as input)
3. **Lighting/weather/condition variants** (primary ref as input; describe the changed conditions)

### 10.4 Prop References

For each prop requiring references:
1. **Primary reference** (white background, ¾ angle, style spec in prompt)
2. **Detail / state variants** (primary ref as input)

### Generation Rules

- Every prompt ends with `"no text, no watermarks, no logos, no labels, no annotations"`
- Additional refs always use the primary ref as a reference image input
- Prompts for additional angles carry forward the style spec in abbreviated form
- All images use the aspect ratio defined in the cinematography specification
- File naming: `ref_{category}_{name}_{variant}.png`
  - e.g. `ref_char_miette_primary.png`, `ref_loc_control-room_dusk-rain.png`

---

## Phase 12: Shot-Frame Generation

> **Prerequisite:** Phase 11 complete. All reference images available.

For every shot in every sequence, generate:

1. **Start frame** — using appropriate character, location, and prop references
2. **End frame** — derived from start frame (edit or generate, per shot spec)
3. **Key frames** — any intermediate states specified in the shot list

### Start Frame Generation

- Tool: `generate_image`
- References: relevant character ref(s) + location ref (matching lighting/weather) + prop ref(s)
- Prompt includes: visual style (brief), scene environment, framing, visible content, subject appearance + outfit
- Aspect ratio: from cinematography specification
- Prompt ends with: `"no text, no watermarks, no logos, no annotations"`

### End Frame Generation

**If edit-from-start:**
- Tool: `generate_image_variation`
- References: [start_frame, relevant Phase 11 refs]
- Prompt: "Edit this image: {changes only}" — do NOT repeat unchanged elements

**If generate-new:**
- Tool: `generate_image`
- References: [start_frame (as scene ref), relevant Phase 11 refs]
- Prompt includes: visual style, end-frame framing + visible content, subject end state, "Same location/environment as reference"

### Key Frame Generation

For each specified key frame, generate as for start frame but with the intermediate
state description, using start frame and relevant refs as references.

### File Naming

`shot_{shot_id}_{frame_type}.png` — e.g. `shot_S01_SH003_start.png`,
`shot_S01_SH003_end.png`, `shot_S01_SH003_key01.png`

---

## Phase 13: Consistency Verification

> **Prerequisite:** Read `references/consistency-verification.md`.

After generating all shot frames, run a vision-based consistency pass. For each shot:

| Check | Method | Flag if |
|-------|--------|---------|
| **Start–end interpolatability** | Compare start and end frames | Subject static; only lighting/bg changed |
| **Character consistency** | Compare against character primary ref | Face, outfit, proportions diverge |
| **Location consistency** | Compare against location ref (same condition) | Architecture, materials, layout diverge |
| **Prop consistency** | Compare against prop primary ref | Object shape, colour, detail diverge |
| **Intra-shot lighting** | Compare start, key, end frames | Lighting direction or colour-temp contradicts |
| **Cross-shot continuity** | Compare end frame of shot N with start frame of shot N+1 (if continuous) | Discontinuity in subject position, wardrobe, environment |

Output a **Consistency Report** listing every flagged issue with severity (BLOCK /
WARN), the shot ID, the check that failed, and a description. BLOCK-level issues must
be resolved (regenerate the offending frame) before proceeding to Phase 14. WARN-level
issues are logged for human review.

---

## Phase 14: Video Prompt Assembly

> **Prerequisite:** Read `references/video-prompt-guide.md`. Phase 13 complete with no
> unresolved BLOCK issues.

For every shot, assemble a complete video prompt. The prompt is the **sole input** to
the video generation model alongside the keyframe images; it must be self-contained.

### Video Prompt Structure

```
[STYLE] {Visual style — brief}
[FILMSTOCK] {Format, grain, colour process — brief}
[SCENE] {Environment description}
[FRAMING] {Shot size + angle + lens + camera motion}
[PACING] {slow / moderate / fast}
[ACTION] {transition_description — 2–4 sentences minimum, see requirements below}
[SUBJECT] {Subject appearance — key features for consistency}
[AUDIO] {On-screen dialogue / sound effects / embedded BGM or "No background music."}
[DURATION] {4 / 6 / 8 seconds}
```

### transition_description Requirements

This field directly drives the video model. Must include:

1. **Subject appearance** — key visual features that must remain consistent
2. **Movement trajectory** — how subject/camera moves through space and time
3. **State changes** — how objects/environment change over the duration
4. **Existence statements** — what is present throughout (prevents pop-in/pop-out)

Minimum 2–4 sentences. One-line descriptions are **insufficient**.

### Physical Consistency Check

Verify that the described motion is physically achievable within the shot duration.
See `references/video-prompt-guide.md` for the constraint table.

### Output

Write all video prompts to `prompts/shot_{shot_id}_prompt.md`. Include the file paths
to the associated start frame, end frame, and any key frames.

---

## Phase 15: Output Assembly

Compile the final scene inventory document using `templates/scene-inventory-template.md`.

### Document Structure

1. Header (title, version, date, logline, scope)
2. Creative Pillars (including Cinematography Specification)
3. Narrative Spine
4. Character Bible (with reference image manifest)
5. Locations Bible (with scouting matrix and reference image manifest)
6. Props Bible (with reference image manifest)
7. Scene Inventory
8. Continuity Inventory
9. Style Frames Audit
10. Storyboard Specification (sequence map + shot lists with frame specs)
11. Thematic Image Plan
12. Consistency Report
13. Video Prompt Manifest
14. Continuity & Anachronism Log
15. Asset Manifest (all generated images, organized by category)

### Output Files

```
{project_name}/
├── {project_name}_scene_inventory.md
├── {project_name}_continuity_inventory.md
├── refs/
│   ├── style/
│   ├── characters/
│   ├── locations/
│   └── props/
├── shots/
│   └── {shot_id}/
│       ├── start.png
│       ├── end.png
│       └── key{NN}.png (if any)
├── prompts/
│   └── shot_{shot_id}_prompt.md
└── reports/
    └── consistency_report.md
```

---

## Reference Files

| File | Read Before | Contents |
|------|-------------|----------|
| `references/cinematography-specification.md` | Phase 2 | Filmstock, grain, grading, colour timing, lenswork specification format and examples |
| `references/continuity-inventory.md` | Phase 8 | Continuity extraction rules, separate deliverable structure, checklist, reset-focused logging guidance |
| `references/reference-image-guide.md` | Phase 11 | Generation order, prompting rules, scouting matrix execution, edit-vs-generate decision table |
| `references/video-prompt-guide.md` | Phase 14 | Prompt structure, transition_description examples, physical consistency constraints, audio handling |
| `references/consistency-verification.md` | Phase 13 | Vision-based QA procedures, severity classification, regeneration protocol |
| `references/extraction-checklist.md` | Any time | Full extraction checklist for QA |

## Templates

| File | Used In |
|------|---------|
| `templates/scene-inventory-template.md` | Phase 15 |
| `templates/character-template.md` | Phase 4 |
| `templates/location-template.md` | Phase 5 |
| `templates/shot-list-template.md` | Phase 9 |

## Best Practices

**Read Twice, Extract Once.** Complete a full read before extraction.

**Operational Language.** Concrete, filmable. "Jaw tightens" not "feels tension."

**Constraint-First.** For every element: what must NOT appear, as well as what must.

**Continuity First.** Extract narrative and physical continuity before prompt writing.
Post-generation consistency verification is a later QA step, not a substitute.

**Out-of-Order Production Reality.** The continuity inventory must let another crew
restore exact dressing, object state, and carry chains days later without re-reading the
source.

**Mundane Objects Count.** Track all handled objects, not just hero props. If a mug, pen,
phone, keyring, utensil, paper stack, cigarette, badge, bag, or desk object can move or
change state, it belongs in continuity tracking.

**Evocative Naming.** "Bruise Blue" not "#2B4F6E". "Kodachrome Sunday" not "warm LUT."

**Function Over Description.** State narrative function for every element.

**Sound as Character.** Audio beds, punctuations, and silence matter as much as visuals.

**Reference Images are Non-Negotiable.** Never generate shot frames without reference
images. Never generate additional refs without using the primary as a reference input.

**Start and End Frames for Every Shot.** No exceptions. The video model needs both
anchors to interpolate convincingly.

**Verify Before Prompting.** Run the consistency pass (Phase 13) before assembling
video prompts (Phase 14). Catching a face swap now costs one regeneration; catching it
after video generation costs the entire shot.
