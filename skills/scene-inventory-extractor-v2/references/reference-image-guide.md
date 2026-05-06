# Reference Image Generation Guide

Read this file before beginning Phase 11 (Reference Image Generation). It defines
generation order, prompting rules, the location scouting matrix, and the
edit-vs-generate decision table for shot frames.

---

## Table of Contents

1. [Principles](#1-principles)
2. [Style Anchor Generation](#2-style-anchor-generation)
3. [Character Reference Generation](#3-character-reference-generation)
4. [Location Scouting Matrix](#4-location-scouting-matrix)
5. [Prop Reference Generation](#5-prop-reference-generation)
6. [Prompt Construction Rules](#6-prompt-construction-rules)
7. [Edit vs Generate Decision Table](#7-edit-vs-generate-decision-table)
8. [Shot Frame Generation Procedure](#8-shot-frame-generation-procedure)
9. [File Organisation](#9-file-organisation)

---

## 1. Principles

**Reference images are the single most important determinant of visual consistency.**
Every shortcut here cascades into compounding errors downstream.

1. **Never generate a shot frame without reference images.** No exceptions.
2. **Never generate an additional reference without using the primary as input.**
3. **Generate the minimum cross-product that the story actually requires** — not every
   conceivable angle, but every angle the camera will actually see.
4. **Describe the visual effect, not the equipment.** "Shallow depth of field with soft
   oval bokeh" not "shot on Cooke S4 50mm."
5. **Every prompt ends with the artefact-suppression string:**
   `"no text, no watermarks, no logos, no labels, no annotations"`
6. **White background for character and prop primary references.** Location references
   use their actual environment.

---

## 2. Style Anchor Generation

Generate 1–2 style-anchor images before any character, location, or prop references.
These establish the global look and become the visual-style reference for everything
that follows.

### Style Anchor Prompt Template

```text
{Full visual style specification from Phase 2}
{Full cinematography specification — filmstock, grain, colour process, timing, grading}
{A representative scene from the story: describe environment, lighting, atmosphere}
{Aspect ratio}
Cinematic still frame. No text, no watermarks, no logos, no labels, no annotations.
```

### Purpose

The style anchor:

- Validates that the visual style specification produces the intended look
- Provides a concrete reference for the agent to compare subsequent generations against
- Anchors the grain, colour timing, and lighting rules in a generated image

If the style anchor does not match the intended look, revise the visual style and
cinematography specifications before proceeding.

---

## 3. Character Reference Generation

### Coverage Requirements by Character Weight

| Character Type | Required References |
|----------------|-------------------|
| **Primary** | Full body (front, neutral pose) · Face ¾ angle · Each distinct outfit · Each key expression the story requires · Each signature action pose |
| **Functional** | Full body (front, neutral pose) · Face ¾ angle |
| **Interface presence** | UI screenshot (full frame) · Avatar detail (if applicable) |
| **Voice-only** | None (unless briefly shown) |
| **Collective** | Representative figure (full body) · 2–3 variant figures showing diversity within the group |

### Generation Order (per character)

1. **Primary reference** (no prior refs as input)
   - Prompt: Full visual style spec + full character description + "full body, front-facing, neutral pose, white background"
   - This is the identity anchor for this character

2. **Face detail** (primary ref as input)
   - Prompt: "Head and shoulders, three-quarter angle, same character" + expression if needed

3. **Additional variants** (primary ref as input; each generated individually)
   - Outfit changes: describe the new outfit; reference the primary for face/body consistency
   - Expression set: describe each expression; reference primary for identity
   - Action poses: describe the pose; reference primary for identity and outfit

### Critical Rules

- The primary reference prompt must include the **full visual style specification** and
  the **full character description** (age, build, complexion, hair, distinguishing
  features, wardrobe). Abbreviation at this stage means the character will drift across
  subsequent generations.
- Additional references carry forward the style spec in **abbreviated form** (the
  reference image itself carries most of the style information).
- Never batch-generate multiple characters in a single image. One character per image.

---

## 4. Location Scouting Matrix

Locations receive the most intensive reference-image coverage because they appear in
many shots and must remain consistent across varying conditions.

### Building the Matrix

For each location, enumerate:

1. **Required angles** — every distinct camera position the shot list demands
2. **Required lighting conditions** — every distinct light state the scenes demand
3. **Required weather conditions** — every distinct weather state (if exterior or
   weather-visible interior)
4. **Required narrative states** — if the location changes over the story (damage,
   redecoration, seasonal change)

Then build the matrix:

```text
Location: Control Room
Angles: Establishing wide (door POV), Console CU, Overhead, Window detail
Lighting: Day (fluorescent), Night (monitors only), Emergency (red warning)
Weather: N/A (interior)
Narrative state: Normal, Post-incident (broken monitors, scattered paper)

Required images:
  Establishing wide × Day          ← primary reference
  Establishing wide × Night
  Establishing wide × Emergency
  Establishing wide × Post-incident
  Console CU × Day
  Console CU × Night
  Console CU × Emergency
  Overhead × Day
  Window detail × Day
  Window detail × Night
```

Only generate combinations that the shot list actually visits. If the console is never
shown under emergency lighting, omit that combination.

### Generation Order (per location)

1. **Primary establishing shot** (no prior refs)
   - Prompt: Full visual style spec + full location description + lighting/weather for
     the most common condition + "establishing wide shot, cinematic"

2. **Additional angles** (primary as input)
   - Prompt: "Same location, {new angle description}, {same lighting condition}"

3. **Lighting/weather variants** (primary as input)
   - Prompt: "Same location, same angle as reference, but now {new condition: dusk,
     rain, emergency red lighting}" — describe the changed conditions fully

4. **Narrative state variants** (primary as input)
   - Prompt: "Same location, same angle, but now {description of damage/change}"

### Consistency Enforcement

When generating a variant, the prompt must include an explicit **anchor statement**
binding it to the primary: "This is the same room shown in the reference image.
Architecture, materials, proportions, and layout are identical. Only the {lighting /
weather / condition} has changed."

---

## 5. Prop Reference Generation

### Coverage Requirements

| Prop Weight | Required References |
|-------------|-------------------|
| **Story-critical** (carries narrative, appears in multiple scenes) | Primary (¾ angle, white bg) · Detail insert (any specific detail seen in ECU) · In-context (in its typical environment) · State variants (if it changes) |
| **Supporting** (defines character or location) | Primary (¾ angle, white bg) |
| **Recurring visual element** (object, fixture, interface, machinery, furniture layout, or set dressing that appears in more than two shots and would be noticed if it changed) | Locked primary reference, usually in-context; generate before any location or shot frame where it appears |
| **Background** (visible but not foregrounded and not recurring) | None (location reference covers it) |

Recurring visual elements are not optional background. If the audience recognizes a
monitor-bank layout, inspection robot, grow-light strip arrangement, cargo pod, cabinet,
signage cluster, or workstation layout when it returns, give it its own locked reference
and pass that reference whenever visible.

### Generation Order

1. **Primary** (no prior refs) — full style spec + physical description + white bg
2. **Detail / state / context variants** (primary as input)

---

## 6. Prompt Construction Rules

### Reference Image Prompts (Phase 11)

**Primary references** (no input reference image):

```text
{Full visual style specification}
{Full cinematography specification (filmstock, grain, colour, grading) — as visual description}
{Full subject description}
{Background: white (character/prop) or environment description (location)}
{Framing: full body / establishing wide / ¾ angle / etc.}
{Aspect ratio}
No text, no watermarks, no logos, no labels, no annotations.
```

**Additional references** (primary ref as input):

```text
{Abbreviated style spec — 1 sentence}
{Subject description — focus on what's new or different}
{New angle / condition / state description}
{Anchor statement if location: "Same environment as reference; only {X} has changed."}
{Aspect ratio}
No text, no watermarks, no logos, no labels, no annotations.
```

### Shot Frame Prompts (Phase 12)

**Start frame:**

```text
{Abbreviated visual style — 1 sentence}
{Filmstock/grain/grading — 1 sentence visual description}
{Scene environment — from scene inventory}
{Framing: shot size + angle + lens effect description}
{Visible content — from shot list start-frame specification}
{Subject appearance + outfit — from character bible}
{Aspect ratio}
No text, no watermarks, no logos, no annotations.
```

References to attach: character ref(s) + location ref (matching condition) + prop ref(s)

**End frame (edit mode):**

```text
Edit this image: {describe only what changes — subject position, pose, expression,
or composition shift}. Everything else remains identical.
```

References to attach: [start_frame, relevant Phase 11 refs]

**End frame (generate mode):**

```text
{Abbreviated visual style — 1 sentence}
{End-frame framing + visible content — from shot list}
{Subject appearance and end state}
Same location and environment as reference image. Same lighting direction, colour
temperature, and depth of field.
{Aspect ratio}
No text, no watermarks, no logos, no annotations.
```

References to attach: [start_frame (as scene ref), relevant Phase 11 refs]

**Key frames:**

As for start frame, but describing the intermediate state. Attach start frame and
relevant refs.

---

## 7. Edit vs Generate Decision Table

Use this table to decide whether the end frame should be derived by editing the start
frame or generated independently.

| Camera Motion | Start and End Share Most Content? | End-Frame Method |
|---------------|----------------------------------|-----------------|
| Static | Yes | **Edit** |
| Small pan/tilt | Yes (overlapping field of view) | **Edit** |
| Zoom (in or out) | Yes (same subject, different framing) | **Edit** |
| Large pan | No (different field of view) | **Generate** |
| Dolly / tracking | No (different spatial position) | **Generate** |
| Crane | No (different height + angle) | **Generate** |
| Arc | Partial (subject centred, bg changes) | **Generate** |
| Handheld (small movement) | Yes | **Edit** |
| Handheld (large movement) | No | **Generate** |

**Rule of thumb:** If you could achieve the transition by cropping and repositioning
within the start frame, use edit. If the camera has moved to reveal substantially new
visual information, generate.

---

## 8. Shot Frame Generation Procedure

For each shot in the shot list, execute in order:

### Step 1: Gather References

Identify and collect:

- Character reference(s) matching the character(s) in this shot (correct outfit variant)
- Location reference matching this shot's lighting/weather/narrative condition
- Prop reference(s) for any visible props
- Recurring visual element reference(s) for any visible fixtures, layouts, interfaces,
  machinery, or set-dressing elements that appear in more than two shots

Hard stop before any frame generation: if `gemini-3-pro-image-preview` is unavailable
through nanobanana MCP, or if any continuity-critical `referenceImagePaths` are missing,
abort immediately. Continuity-critical references include character identity refs,
location refs, required prop refs, recurring visual element refs, and style anchors
when the shot depends on them. Do not fall back to another model or relax reference
constraints. `scene-inventory-extractor-v2` must produce the scene pack, continuity
inventory, prompt keyword library, recurring visual element definitions, and reference
images before handing off to `shot-specifier`.

### Step 2: Generate Start Frame

- Tool:
  - `character_consistency` for character-centric shots
  - `generate_image` for environment or prop-led shots
- Model: `gemini-3-pro-image-preview`
- `referenceImagePaths`:
  - Character-centric: [character identity ref, location ref, required prop refs, style
    anchor when available, recurring visual element refs when visible]
  - Environment or prop-led: [location ref, required prop refs, recurring visual element
    refs, style anchor when available], adding character refs only for visible named
    characters whose identity must be constrained
- Before calling nanobanana MCP, verify `gemini-3-pro-image-preview` availability and
  validate every listed continuity-critical `referenceImagePaths` entry exists.
- Prompt: see §6 Shot Frame Prompts — Start frame
- Save as `shot_{shot_id}_start.png`

### Step 3: Generate End Frame

- Determine edit or generate from §7 decision table
- If **edit**: Tool nanobanana MCP `edit_image`; model
  `gemini-3-pro-image-preview`; `referenceImagePaths` [start_frame + only refs needed
  for the described change]
- If **generate**: Tool nanobanana MCP `generate_image`; model
  `gemini-3-pro-image-preview`; `referenceImagePaths` [start_frame + location ref +
  required prop refs + recurring visual element refs + style anchor when available]
- Before calling nanobanana MCP, verify `gemini-3-pro-image-preview` availability and
  validate every listed continuity-critical `referenceImagePaths` entry exists.
- End frames derived from start frames should use `edit_image` so character, location,
  prop, and style consistency inherit from the start frame naturally.
- Save as `shot_{shot_id}_end.png`

### Step 4: Generate Key Frames (if specified)

For each key frame in order:

- Tool:
  - `character_consistency` for character-centric key frames
  - `generate_image` for environment or prop-led key frames
  - `edit_image` when the key frame is derived from the start frame by a limited pose,
    expression, object-state, or camera-position change
- Model: `gemini-3-pro-image-preview`
- `referenceImagePaths`:
  - Character-centric: [character identity ref, start_frame, matching location ref,
    required prop refs, recurring visual element refs, style anchor when available]
  - Environment or prop-led: [start_frame, matching location ref, required prop refs,
    recurring visual element refs, style anchor when available]
  - Edit-derived: [start_frame, only refs needed for the described change]
- Before calling nanobanana MCP, verify `gemini-3-pro-image-preview` availability and
  validate every listed continuity-critical `referenceImagePaths` entry exists.
- Prompt: intermediate state description
- Save as `shot_{shot_id}_key{NN}.png`

### Step 5: Immediate Visual Check

Using vision capabilities, compare start and end frames:

- Is there clear, interpolatable change? (If not → regenerate end frame with stronger change description)
- Are character features consistent? (If not → regenerate with stronger identity anchoring)
- Is lighting direction consistent? (If not → regenerate with explicit lighting direction in prompt)

Log any issues for the full consistency pass in Phase 13.

---

## 9. File Organisation

```text
{project_name}/
├── refs/
│   ├── style/
│   │   └── style_anchor_{NN}.png
│   ├── characters/
│   │   └── {character_name}/
│   │       ├── primary.png
│   │       ├── face_detail.png
│   │       ├── outfit_{variant}.png
│   │       ├── expression_{name}.png
│   │       └── pose_{name}.png
│   ├── locations/
│   │   └── {location_name}/
│   │       ├── establishing_{condition}.png
│   │       ├── {angle}_{condition}.png
│   │       └── ...
│   ├── props/
│   │   └── {prop_name}/
│   │       ├── primary.png
│   │       ├── detail.png
│   │       └── state_{variant}.png
│   └── recurring-elements/
│       └── {element_name}/
│           ├── primary.png
│           ├── detail.png
│           └── state_{variant}.png
├── shots/
│   └── {shot_id}/
│       ├── start.png
│       ├── end.png
│       └── key{NN}.png
└── ...
```

Use lowercase, hyphen-separated names throughout. No spaces in filenames.
Recurring visual element assets are canonical locked references reused across
characters, locations, props, and every shot where the element appears; do not mix them
into `refs/props/`.
