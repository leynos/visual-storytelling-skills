# Cinematography Specification Reference

Read this file before beginning Phase 2 (Creative Pillars). It defines the technical
cinematographic characteristics that govern the visual pipeline.

---

## Table of Contents

1. [Format and Filmstock](#1-format-and-filmstock)
2. [Grain Structure](#2-grain-structure)
3. [Colour Process](#3-colour-process)
4. [Colour Timing](#4-colour-timing)
5. [Grading Rules](#5-grading-rules)
6. [Lens Language](#6-lens-language)
7. [Depth of Field](#7-depth-of-field)
8. [Shutter Behaviour](#8-shutter-behaviour)
9. [Camera Motion Grammar](#9-camera-motion-grammar)
10. [Specification Template](#10-specification-template)
11. [Examples](#11-examples)

---

## 1. Format and Filmstock

Define the physical (or emulated) capture medium. This anchors grain, dynamic range,
colour science, and aspect ratio decisions.

| Field | What to Specify | Examples |
|-------|-----------------|---------|
| **Gauge** | Film gauge or digital sensor equivalent | Super 8, 16 mm, 35 mm, 65 mm, "RED Monstro equivalent" |
| **Stock / sensor** | Named stock or sensor family | Kodak Vision3 500T, Fuji Eterna Vivid 160, "ARRI ALEXA LF equivalent" |
| **Native aspect ratio** | Width:height | 1.33:1, 1.66:1, 1.85:1, 2.39:1 (anamorphic), 16:9 |
| **Target resolution** | Generation resolution | 16:9 (1280×720) or 9:16 (720×1280) for AI generation |
| **Exposure latitude** | Shadow/highlight recovery behaviour | "Generous highlight rolloff, crushed blacks" |

### Choosing a Stock

The stock choice communicates before a single frame is composed:

- **Kodachrome 64** — Saturated, contrasty; reds and greens pop; nostalgia anchor
- **Ektachrome 100** — Cooler, finer grain; blues and greens; documentary feel
- **Vision3 500T** — Tungsten-balanced; versatile; modern cinema standard
- **Vision3 250D** — Daylight-balanced; rich skin tones; fine grain
- **Fuji Eterna 250D** — Slightly desaturated; green-tinged shadows; contemplative
- **CineStill 800T** — Halation around highlights; neon-friendly; nocturnal urban
- **Tri-X 400** — Black-and-white; high contrast; photojournalism grit
- **Digital clean** — No grain emulation; specify sensor colour science instead

When specifying for AI generation, describe the **visual characteristics** rather than
just naming the stock. The generation model does not inherently know "Vision3 500T" —
it needs "moderate fine grain, warm highlights, slightly desaturated shadows with teal
undertone, gentle highlight rolloff."

---

## 2. Grain Structure

Grain is not noise. It is texture with character.

| Field | What to Specify |
|-------|-----------------|
| **Size** | Fine / medium / coarse |
| **Distribution** | Even / concentrated in shadows / concentrated in midtones |
| **Character** | Organic (clumpy, irregular) / digital (uniform, pixel-level) |
| **Response to exposure** | More grain in underexposure / consistent / less grain in highlights |
| **Colour grain** | Monochrome grain on colour image / colour-channel grain (R/G/B shift) |

### Grain and Storytelling

Grain serves narrative function:

- **Fine, consistent** — professional, controlled, institutional
- **Coarse, shadow-heavy** — gritty, documentary, under-resourced
- **Variable (shifts with exposure)** — organic, handmade, period
- **Absent (digital clean)** — clinical, surveillance, synthetic

Specify any **per-scene grain variation** if the story calls for it (e.g., flashback
sequences shot on a different stock).

---

## 3. Colour Process

Define the photochemical or digital colour pipeline.

| Process | Visual Character |
|---------|-----------------|
| **Kodachrome (K-14)** | Dense saturation, warm, contrasty, archival feel |
| **Ektachrome (E-6)** | Cooler, accurate, moderate saturation |
| **Cross-processed E-6 in C-41** | Shifted greens/cyans, high contrast, fashion/music-video look |
| **Bleach bypass** | Desaturated, high contrast, retained silver; gritty |
| **ENR (Technicolor)** | Retained silver; dark, contrasty; Spielberg/Kaminski look |
| **Two-strip Technicolor** | Red-cyan palette only; period silent-film or stylised |
| **Three-strip Technicolor** | Hyper-saturated, poster-like; classic Hollywood |
| **Digital LOG + LUT** | Specify LUT family (ACES, Rec.709, custom) and characteristics |

For AI generation, describe the **output appearance**: "Desaturated midtones, warm
shadows pulling toward amber, cool highlights with cyan edge, moderate contrast with
lifted blacks."

---

## 4. Colour Timing

Colour timing (or colour grading in digital parlance) defines the overall and
scene-specific colour bias.

### Global Timing

| Field | What to Specify |
|-------|-----------------|
| **Overall bias** | Cool / warm / neutral / cross-processed |
| **Shadow colour** | Teal, blue, green, amber, or neutral |
| **Midtone colour** | Usually neutral; note any warming or cooling |
| **Highlight colour** | Warm, cool, or neutral |
| **Saturation tendency** | Pulled (desaturated) / pushed (vivid) / selective (saturate one hue) |

### Scene-Specific Timing Rules

Map timing overrides to narrative conditions:

```
* **Interior / artificial light:** Push warmth +15%; amber shadows
* **Exterior / overcast:** Cool bias; blue-grey shadows; desaturate greens
* **Night / streetlight:** Sodium-orange highlights; deep teal shadows
* **Flashback / memory:** Shift toward {process}; increase grain one stop
* **Digital / interface:** Remove timing; flat, clinical, cold blue
```

### Timing and Emotion

Colour timing is emotional infrastructure. Be explicit about which emotions map to
which shifts. Avoid vague instructions ("make it feel sad") — specify the measurable
parameter ("Cool the midtones 10%; shift shadows from neutral to blue-grey; reduce
saturation 20%").

---

## 5. Grading Rules

Grading operates on the tone curve — where black sits, where white sits, and how the
midtones distribute between them.

| Parameter | What to Specify |
|-----------|-----------------|
| **Blacks** | Crushed (0–5 IRE) / lifted (10–15 IRE) / milky (20+ IRE) |
| **Shadows** | Dense / open / coloured |
| **Midtones** | Contrasty / flat / S-curve |
| **Highlights** | Clipped hard / gentle rolloff / blown (intentional) |
| **Overall contrast** | Low / medium / high / varies by scene type |

### Grading and Period

Period-appropriate grading matters for historical accuracy:

- **Pre-1960s:** Higher contrast, crushed blacks, less shadow detail
- **1960s–70s:** Flatter, more pastel, lifted blacks
- **1980s:** Warm, slightly blown highlights, dense shadows
- **1990s:** Bleach bypass influence, desaturated, high contrast
- **2000s–present:** Digital precision; variable by genre

---

## 6. Lens Language

Lens choice shapes how the audience perceives space, intimacy, and reality.

| Field | What to Specify |
|-------|-----------------|
| **Type** | Primes / zooms / anamorphic / spherical |
| **Focal length range** | e.g. "28 mm – 85 mm; never wider than 24 mm" |
| **Anamorphic?** | Yes/no; if yes: oval bokeh, horizontal flare, 2× squeeze |
| **Characteristic aberrations** | Halation, chromatic aberration, barrel distortion, flare behaviour |
| **Bokeh** | Shape (circular, cat's-eye, lemon, hexagonal) and quality (smooth, busy, swirly) |
| **Vintage vs modern** | Clean modern coatings vs character from uncoated/single-coated glass |
| **Era emulation** | If aping a specific lens set (e.g. "Cooke Speed Panchros", "Panavision C-Series") |

### Focal Length and Psychology

| Range | Psychological Effect |
|-------|---------------------|
| 14–24 mm | Distortion, alienation, environmental dominance, vertigo |
| 28–35 mm | Observational, documentary, "being there" |
| 40–50 mm | Neutral, human-eye equivalent, honest |
| 65–85 mm | Portrait, intimacy, facial detail, shallow DOF |
| 100–200 mm | Compression, surveillance, voyeurism, detachment |
| 200 mm+ | Extreme compression, telephoto stacking, flatness |

### Lens Rules for AI Prompting

When writing prompts for AI image generation, describe the **visual effect** of the
lens, not the lens itself:

- ✓ "Shallow depth of field with soft oval bokeh in background; slight barrel distortion at frame edges; warm halation around practical light sources"
- ✗ "Shot on Cooke S4 50mm T2.0" (the model does not know this lens)

---

## 7. Depth of Field

| Context | DOF Rule |
|---------|----------|
| **Dialogue close-ups** | {Shallow / moderate — specify} |
| **Establishing wides** | {Deep / moderate — specify} |
| **Insert / detail shots** | {Very shallow / moderate — specify} |
| **Action sequences** | {Deep (keep everything sharp) / rack focus (specify triggers)} |
| **POV shots** | {Emulate human eye: centre-sharp, peripheral soft} |

### Rack Focus Conventions

If using rack focus, specify the trigger and direction:

```
Rack focus from {subject A} to {subject B} when {narrative trigger}.
```

---

## 8. Shutter Behaviour

| Field | What to Specify |
|-------|-----------------|
| **Default shutter angle** | 180° (standard motion blur) / narrower (sharper, strobe-like) / wider (dreamier) |
| **Override rules** | When to deviate (e.g. "Action: 90° shutter for staccato movement") |
| **Narrative function** | What the shutter variation communicates |

---

## 9. Camera Motion Grammar

Define how the camera moves in different narrative contexts.

| Context | Motion Rule |
|---------|-------------|
| **Observation / routine** | {e.g. "Locked tripod or slow pan; no handheld"} |
| **Tension / pursuit** | {e.g. "Steadicam or dolly; smooth but urgent"} |
| **Chaos / breakdown** | {e.g. "Handheld; intentional instability; whip pans allowed"} |
| **Intimacy / confession** | {e.g. "Static CU; no movement; hold uncomfortable duration"} |
| **Establishing / geography** | {e.g. "Crane or high-angle dolly; slow, measured"} |
| **Machine / interface vision** | {e.g. "Locked digital; no human motion characteristics"} |

### Motion and Duration

Camera motion must be physically achievable within the shot duration. Reference table:

| Motion Type | Physical Constraint |
|-------------|--------------------|
| Pan / tilt | Camera fixed to tripod head; content within rotational range |
| Dolly / tracking | Content physically traversable at the described speed within duration |
| Crane | Vertical range + lateral range achievable in duration |
| Arc | Subject stays centred; environment must allow orbit path |
| Zoom | Optical zoom range (not to be confused with dolly) |
| Handheld | As dolly but with permitted irregularity |
| Steadicam | As dolly but smoother; limited speed |

### Common Motion Mistakes

| Mistake | Correction |
|---------|------------|
| "Pan from corridor entrance to middle" | Use "dolly forward" (pan is rotation, not translation) |
| First: room A, Last: room B (single shot) | Split into two shots or use a long dolly |
| 6-second shot covering 100 metres | Extend duration or reduce distance |
| "Zoom and dolly simultaneously" | Permitted (Hitchcock zoom) but specify both vectors |

---

## 10. Specification Template

Use this template in the scene inventory document under Creative Pillars § 2.3:

```markdown
#### 2.3 Cinematography Specification

* **Format:** {Gauge / sensor equivalent}
* **Stock / sensor:** {Named stock or sensor family}
* **Aspect ratio:** {Width:height}
* **Generation resolution:** {e.g. 16:9}

* **Grain:**
  * Size: {fine / medium / coarse}
  * Distribution: {even / shadow-heavy / midtone}
  * Character: {organic / digital}
  * Exposure response: {description}

* **Colour process:** {Named process or description}

* **Colour timing:**
  * Overall bias: {cool / warm / neutral}
  * Shadows: {colour}
  * Midtones: {colour}
  * Highlights: {colour}
  * Saturation: {pulled / pushed / selective}
  * Scene-specific overrides:
    * {Condition}: {timing adjustment}
    * {Condition}: {timing adjustment}

* **Grading:**
  * Blacks: {crushed / lifted / milky}
  * Contrast: {low / medium / high}
  * Highlight rolloff: {hard / gentle / blown}
  * Shadow detail: {preserved / crushed}

* **Lens language:**
  * Type: {primes / zooms / anamorphic / spherical}
  * Focal range: {range}
  * Aberrations: {halation, flare, bokeh shape}
  * Vintage/modern: {description}

* **Depth of field rules:**
  * {Context}: {rule}
  * {Context}: {rule}

* **Shutter:** {Default angle; overrides}

* **Camera motion grammar:**
  * {Context}: {motion rule}
  * {Context}: {motion rule}
```

---

## 11. Examples

### Example A: British Social Realism (Ken Loach register)

```
* Format: 16 mm (emulated)
* Stock: Kodak Vision3 250D
* Aspect ratio: 1.85:1
* Grain: Medium, organic, shadow-concentrated; more grain in underexposure
* Colour process: Standard C-41; slight desaturation in post
* Colour timing: Cool overall; grey-green shadows; neutral midtones; flat highlights
* Grading: Lifted blacks (10 IRE); low-medium contrast; gentle highlight rolloff
* Lens language: Spherical primes, 28–65 mm; no wider than 24 mm; clean modern coatings
* DOF: Moderate throughout; deep focus for establishing shots
* Shutter: 180° default; no overrides
* Camera motion: Handheld (observational); Steadicam for walk-and-talk; no crane
```

### Example B: Neon Noir (Refn / Winding register)

```
* Format: 35 mm anamorphic (emulated)
* Stock: CineStill 800T equivalent
* Aspect ratio: 2.39:1
* Grain: Fine to medium, even; colour-channel grain visible in shadows
* Colour process: Cross-process influence; pushed one stop
* Colour timing: Cool teal shadows, warm amber/sodium highlights; deep saturation in neon hues; desaturated skin tones
* Grading: Crushed blacks (0–3 IRE); high contrast; blown neon highlights (intentional)
* Lens language: Anamorphic primes, 40–75 mm; oval bokeh; horizontal flare from practicals; heavy halation on neon sources
* DOF: Very shallow for close-ups; deep for establishing neon environments
* Shutter: 180° default; 90° for violence sequences
* Camera motion: Slow dolly and Steadicam (prowling); locked tripod for confrontation; no handheld
```

### Example C: Digital Surveillance / Institutional

```
* Format: Digital (mixed; CCTV + body-cam + desktop capture)
* Stock: Various low-quality sensors; CCTV is 1/3" CCD equivalent
* Aspect ratio: Mixed (4:3 for CCTV; 16:9 for body-cam; variable for desktop)
* Grain: Digital noise; heavy in shadows; compression artefacts (blocking, banding)
* Colour process: None (raw sensor output); white balance often wrong
* Colour timing: Flat; institutional fluorescent green-cast; no deliberate grading
* Grading: None (intentional absence); auto-exposure artefacts
* Lens language: Wide fixed lenses (2.8 mm for CCTV — extreme barrel distortion); no DOF control
* DOF: Deep throughout (small sensors, wide lenses)
* Shutter: Electronic rolling shutter (wobble on body-cam); fixed exposure on CCTV
* Camera motion: Fixed (CCTV); body-mounted (body-cam); screencast cursor (desktop)
```
