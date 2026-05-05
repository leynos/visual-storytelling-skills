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
| 2 | Creative Pillars | Visual aesthetic + storytelling style + **cinematography specification** + **prompt keyword library** |
| 3 | Narrative Spine | Structure, themes, turnpoints |
| 4 | Character Bible | Character entries with **reference-image specifications** |
| 5 | Locations Bible | Location entries with **multi-angle, multi-condition scouting specs** |
| 6 | Props Bible | Props with physical descriptions and ref-image specs |
| 7 | Scene Inventory | Per-scene breakdowns |
| 8 | Continuity Inventory | Character/location/prop state tracking across scenes |
| 9 | Shot Lists | Shot tables with full cinematography fields and duration budgets |
| 10 | Thematic Image Plan | Key narrative-beat images |
| 11 | Reference Image Generation | All character, location, and prop reference images with **video role manifest** |
| 12 | Shot-Frame Generation | Start frame, end frame, and key frames per shot |
| 13 | Consistency Verification | Vision-based QA pass; flag failures |
| 14 | Video Prompt Assembly | Complete prompt per shot, ready for generation |
| 15 | Output Assembly | Final compiled document + asset manifest |

> **Read order for reference files:** Before starting Phase 2, read
> `references/cinematography-specification.md`. Before Phase 8, read
> `references/continuity-inventory.md`. Before Phase 11, read
> `references/reference-image-guide.md`. Before Phase 14, read
> `references/video-prompt-guide.md`. The consistency verification procedure in Phase 13
> is defined in `references/consistency-verification.md`. The prompt keyword library
> format is defined in `references/prompt-keyword-library.md`.
> **Downstream skill:** When full per-shot storyboarding, detailed actor/camera/lighting
> direction, model routing, and asset-pipeline management are required, hand off to the
> `shot-specifier` skill. That skill takes the scene inventory and reference images
> produced here as its input.

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

```text
**Name:** {Evocative 2–4 word title}
**Definition:** {One sentence capturing look and feel}
```

Specify: Palette (3–5 named colours), Lighting rules, Texture rules, Camera grammar,
Warmth rules. See `templates/scene-inventory-template.md` for field structure.

### 2.2 Storytelling Style

```text
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

### 2.4 Prompt Keyword Library

> **Prerequisite:** Read `references/prompt-keyword-library.md` before this sub-phase.

Immediately after completing the cinematography specification, derive a **project-level
prompt keyword library**: a canonical vocabulary of adjective phrases and art-direction
terms that reliably translate each style parameter into language video and image
generation models respond to consistently.

This library is **infrastructure**, not decoration. Every video prompt written in Phase 14
must draw from it rather than re-inventing style language shot by shot. Inconsistent
style vocabulary across shots produces visible tonal drift even when the underlying spec
is correct.

Write the library as a section in the scene inventory document and also as a standalone
file at `{project_name}_prompt_keywords.md`.

```text
### Prompt Keyword Library

* **Global style phrase:** {1–2 sentences encoding filmstock, grain, colour process}
  * Example: "35 mm print, Kodak Vision3 250D characteristics, organic fine-to-medium grain,
    accurate daylight balance, slightly desaturated shadows, gentle highlight rolloff"

* **Per-location-type vocabulary:**
  * {Location type}: {canonical phrase set for colour, light, texture, atmosphere}
    * Example exterior: "flat pewter Atlantic overcast, wet peat surfaces, no hard shadows,
      lifted blacks, fence posts leaning in wind"
    * Example interior warm: "warm amber grow-light, artificial June, high humidity haze,
      strawberry scarlet at full vibrancy"

* **Per-lighting-condition vocabulary:**
  * {Condition name}: {phrase set}
    * Example pre-dawn: "sodium-orange practicals, deep grey-blue surround, rain halos
      around light sources, near-dark ground plane"

* **Global negative constraints:** {what must never appear in prompts}
  * Example: "no trees, no dual carriageways, no US road markings, no hard shadows,
    no blue sky, no bright saturated colours except strawberry scarlet"

* **Selective saturation rules:** {objects exempt from global desaturation}
  * Example: "strawberry scarlet is exempt from the global 15–20% desaturation pass;
    push selectively against every other desaturated element"

* **POV-specific overrides:** {e.g. machine-vision shots that require no grain}
  * Example drone POV: "digital-flat, no grain, deep focus throughout, gimbal-stabilised,
    machine vision — no organic camera movement"
```

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

```text
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

```text
* **Reference image requirements:**
  * Reference priority: required-before-Phase-12 / incidental
    (required-before-Phase-12: prop appears prominently on screen across multiple shots
     and its visual identity is story-critical — a named vehicle, weapon, device, or
     object whose appearance the audience will track. Generate before any location or
     scene image that includes it. incidental: prop appears briefly or in background;
     standard Phase 11 timing applies.)
  * Primary: {Object on white background, ¾ angle}
  * Detail: {Any specific detail the camera will see in ECU/INS}
  * In-context: {Object in its typical environment, if context matters}
  * State variants: {If prop changes condition across the story}
```

---

## Phase 7: Scene Inventory

For each scene (new scene on location change, significant time passage, POV shift, or
mode change):

```text
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

### Duration Budget (do this first)

Before decomposing each scene into individual shots, establish a **duration budget**:

1. Estimate the total desired screen time for the scene in seconds.
2. Divide into clips: clips must be 4, 6, or 8 seconds each.
3. Record the budget before writing individual shot rows — it prevents collapsing
   multi-beat scenes into a single over-stuffed clip.

```text
* **Scene duration budget:** {total seconds}
* **Clip count:** {N clips}
* **Per-clip targets:** {e.g. SH001: 8s, SH002: 6s, SH003: 4s}
```

> **Common error:** SC-11-style launch sequences feel like one shot but contain at least
> three distinct clips (pre-launch static, rotor spin-up and lift, forward flight
> receding). Budget before decomposing, not after.

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

```text
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

### 11.1 Style Anchor

Generate 1–2 style-anchor images that establish the global look (filmstock, grain,
palette, lighting). These become the visual-style reference for everything that follows.

### 11.2 Character References

For each character, generate in order:

1. **Primary reference** (no prior refs; full visual-style spec in prompt + white bg)
2. **Additional angles/expressions/wardrobe** (primary ref as input reference)

### 11.3 Prop References

> **Order rationale:** Props are generated before locations because location shots often
> contain key props in frame. Without a locked prop reference, each location image will
> independently invent the prop's appearance — producing the failure mode where the same
> aircraft looks like three different vehicles across a sequence.

For each prop with `reference priority: required-before-Phase-12`:

1. **Primary reference** (white background, ¾ angle, style spec in prompt)
2. **Detail / state variants** (primary ref as input)

Then, after locations are complete (11.4), generate refs for `incidental` props in the
same pattern.

### 11.4 Location Scouting References

For each location, generate across the scouting matrix:

1. **Primary establishing shot** (no prior refs; full style spec in prompt)
2. **Additional angles** (primary ref as input)
3. **Lighting/weather/condition variants** (primary ref as input; describe the changed conditions)

### Generation Rules

- Every prompt ends with `"no text, no watermarks, no logos, no labels, no annotations"`
- Additional refs always use the primary ref as a reference image input
- Prompts for additional angles carry forward the style spec in abbreviated form
- All images use the aspect ratio defined in the cinematography specification
- File naming: `ref_{category}_{name}_{variant}.png`
  - e.g. `ref_char_miette_primary.png`, `ref_loc_control-room_dusk-rain.png`

### 11.5 Video Role Manifest

After generating all reference images, produce a **video role manifest** that declares
the intended role of each image when used as a video generation input. This is distinct
from the reference image manifest (which tracks what exists); the video role manifest
tells downstream tools and the shot-specifier skill how to use each image.

```markdown
## Video Role Manifest

| Ref ID | File | Video Role | Used In Shots | Notes |
|--------|------|------------|---------------|-------|
| LOC-launch-01 | refs/locations/launch-strip/low-pre-dawn-rain.png | start_image | S11_SH001 | Pre-launch static |
| LOC-launch-03 | refs/locations/launch-strip/gannet-vertical-lift.png | end_image | S11_SH002 | Mid-lift anchor |
| PROP-gannet-01 | refs/props/gannet-uav/primary.png | image | S11_SH001, S11_SH002 | Subject consistency ref |
| CHAR-switch-01 | refs/characters/switch/primary.png | image | S08_SH001 | Identity anchor |
| style/style_anchor_01.png | refs/style/style_anchor_01.png | image | all | Global style ref |
```

Video role values:

- `start_image` — anchors the first frame of the clip
- `end_image` — anchors the last frame of the clip
- `image` — subject/style consistency reference (visible in clip but not a frame anchor)
- `video` — reference video for motion style
- `audio` — reference audio track

---

## Phase 12: Shot-Frame Generation

> **Prerequisite:** Phase 11 complete. All reference images available.

### Pre-Generation Reference Check (per shot)

Before generating any frame for a shot, answer these three questions explicitly:

1. Does a canonical reference image exist for **every named character** present in this shot?
2. Does a canonical reference image exist for **every required-before-Phase-12 prop** visible in this shot?
3. Does a canonical reference image exist for **the specific location variant** (angle × lighting condition) this shot requires?

If any answer is no, generate that reference now using the Phase 11 procedure before
proceeding. Do not skip this check. The failure mode it prevents: a scene frame generated
before the prop's primary reference exists, where the model independently invents the
prop's appearance — producing a visually different object from all other shots.

For every shot in every sequence, generate:

1. **Start frame** — using appropriate character, location, and prop references
2. **End frame** — derived from start frame (edit or generate, per shot spec)
3. **Key frames** — any intermediate states specified in the shot list

### Start Frame Generation

- Tool: `generate_image`
- References: relevant character ref(s) + location ref (matching lighting/weather) + prop ref(s)
- Prompt includes: visual style (brief), scene environment, framing, visible content, subject appearance + outfit
- Draw style vocabulary from the **prompt keyword library** produced in Phase 2.4
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
| **Cross-shot prop identity** | For each named prop: gather all frames containing it and view them together | The prop looks like a different physical object across shots — different construction, silhouette, or type entirely |
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

```text
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

### Style Language Rule

Every `[STYLE]` and `[FILMSTOCK]` field **must draw from the prompt keyword library**
(Phase 2.4). Do not invent new style vocabulary at this phase. Consistency across shots
depends on using the same canonical phrases.

### Continuity Constraint Injection

Before finalising each prompt, check the location bible's continuity constraints for
that location and inject any that are relevant. Common constraints to inject:

- Negative space rules ("no trees", "left-hand traffic")
- Colour exclusions ("no blue sky", "no hard shadows outside")
- Signature prop requirements ("rubber duck on console throughout")

These constraints are in the location bible but are easy to omit when writing prompts
shot by shot. The video role manifest ensures reference images carry visual consistency;
the injected text constraints carry the rules that images cannot enforce.

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
2. Creative Pillars (including Cinematography Specification and Prompt Keyword Library)
3. Narrative Spine
4. Character Bible (with reference image manifest)
5. Locations Bible (with scouting matrix and reference image manifest)
6. Props Bible (with reference image manifest)
7. Scene Inventory
8. Continuity Inventory
9. Style Frames Audit
10. Storyboard Specification (sequence map + shot lists with frame specs and duration budgets)
11. Thematic Image Plan
12. Consistency Report
13. Video Prompt Manifest
14. Continuity & Anachronism Log
15. Asset Manifest (all generated images, organized by category)

### Output Files

```text
{project_name}/
├── {project_name}_scene_inventory.md
├── {project_name}_continuity_inventory.md
├── {project_name}_prompt_keywords.md
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
| `references/prompt-keyword-library.md` | Phase 2.4 | How to construct and use a project-level prompt vocabulary library |
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

**Budget Before Decomposing.** Establish a clip-duration budget for each scene before
writing individual shot rows. Multi-beat scenes collapsed into a single oversized clip
produce rushed, incoherent video. Three clips of 6s each is almost always better than
one clip of 18s.

**Prompt Vocabulary is Production Infrastructure.** The prompt keyword library is not
optional polish — it is the mechanism that keeps visual style consistent across dozens of
independently generated clips. Style vocabulary invented ad hoc per shot produces tonal
drift. Build the library once in Phase 2.4 and use it for every prompt in Phase 14.

**Inject Continuity Constraints into Prompts.** Location bibles contain negative space
rules, colour exclusions, and signature prop requirements. These must be explicitly
carried into each video prompt; reference images enforce visual consistency but cannot
enforce textual rules ("no trees", "left-hand traffic", "no blue sky outside").

**Evocative Naming.** "Bruise Blue" not "#2B4F6E". "Kodachrome Sunday" not "warm LUT."

**Function Over Description.** State narrative function for every element.

**Sound as Character.** Audio beds, punctuations, and silence matter as much as visuals.

**Reference Images are Non-Negotiable.** Never generate shot frames without reference
images. Never generate additional refs without using the primary as a reference input.

**References First, Always.** Lock canonical reference images for every named character,
every required-before-Phase-12 prop, and every key location before generating any composite
scene or storyboard frame. The generation order is: style anchor → characters →
required-before-Phase-12 props → locations → incidental props. Never generate a location image
that contains a named prop until that prop's primary reference is locked. Skipping this
produces the category error where the same object — a vehicle, a device, a named weapon —
looks like a completely different thing in every shot it appears.

**Start and End Frames for Every Shot.** No exceptions. The video model needs both
anchors to interpolate convincingly.

**Verify Before Prompting.** Run the consistency pass (Phase 13) before assembling
video prompts (Phase 14). Catching a face swap now costs one regeneration; catching it
after video generation costs the entire shot.
