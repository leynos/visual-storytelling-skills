# Shot Direction Guide

Read this before Phase 4 (Shot Direction). Directorial notation for actor, camera,
lighting, effects, and audio. Direction must be concrete and filmable.

---

## Core Principle

Direction specifies **what the camera sees** and **exactly how it gets there**. Vague
emotional language ("she seems worried", "the mood is tense") is not direction. Every
element in the spec must be testable: a crew should be able to read it and know
precisely what to set up.

---

## 1. Actor Direction

### Position Notation

Describe actor position in three dimensions:

- **Lateral:** left-of-frame / centre-frame / right-of-frame
- **Depth:** foreground (fills lower two-thirds) / midground / background
- **Vertical:** below eyeline / at eyeline / above eyeline (camera position relative)

### Action Description Rules

- Use present tense, continuous aspect: "She places her hand on the console"
- Include speed: "slowly", "without hesitation", "abruptly"
- Include timing: "after a two-second hold", "immediately on entering frame"
- Include spatial trajectory: "moves left to right, pausing at the desk"
- State what does NOT change: "her right hand remains on the keyboard throughout"

### Continuity State

Always record the continuity state entering and exiting the shot:

- Wardrobe items worn (every visible layer)
- Carried items (hands, pockets, bags)
- Physical condition (wet, dirty, fatigued, injured)
- Body-state details that can change within a scene (hair loosening, eyeliner smudging,
  jacket buttoning)

### Examples

**Insufficient:**
```
Switch looks worried at her console.
```

**Sufficient:**
```
Switch is seated at her console, centre-frame, slightly left of the rubber duck.
She leans forward toward the screens, right arm extended, fingertips near the
keyboard but not touching. After two seconds she sits back, turning her head
to look toward Iain off-frame right. Her expression throughout: flat attention,
no visible emotion until the head turn, where a slight narrowing of the eyes
occurs. Pink headphones are around her neck, not on her head. Coffee cup is to
her left, not in hand.
```

---

## 2. Camera Direction

### Mount Types and Their Implications

| Mount | Motion Character | Use For |
|-------|-----------------|---------|
| **Tripod** | Perfectly static; pure rotation only (pan/tilt) | Weather, landscape, locked-off reaction shots |
| **Steadicam** | Smooth translation; walking-pace follow; slight float | Following characters through spaces; complex movement without jerkiness |
| **Handheld** | Organic float and micro-shake; observer energy | Intimate dialogue; observational documentary feel; close follow |
| **Crane / jib** | Vertical + lateral translation; smooth rises and sweeps | Establishing reveals; emotional lifts; geography shots |
| **Drone gimbal** | High-precision stabilised; machine precision | Aerial establishing; drone POV; surveillance-feel |

### Motion Path Description

Describe the camera's physical path through space:

- **Pan:** "Camera pans left approximately 30° from the gannet on the cradle to the
  horizon, at a slow, deliberate pace"
- **Dolly:** "Camera dollies forward along the row of grow beds, starting 3 m back from
  the first robot, ending 0.5 m behind it"
- **Tilt:** "Camera tilts up from the wet tarmac to the rising gannet, tracking the
  lift"
- **Arc:** "Camera arcs 90° clockwise around Switch, moving from her front to her left
  profile while she reads the screen"
- **Rise:** "Camera rises from ground level (launch strip surface) to 2 m height, ending
  level with the gannet's nose at the top of its lift"

Always include: start position, end position, speed, and arc extent.

### Focal Length and Depth of Field

Specify together:

```
* 85 mm spherical, f/2.8 — face sharp, control room background soft
* 28 mm spherical, f/11 — deep focus throughout; fence posts, moor, and sky all sharp
* 50 mm spherical, f/5.6 — moderate depth; subject sharp, background readable but soft
```

---

## 3. Lighting Direction

### Key Source

Name the source, its position relative to subject, and its quality:

- "Overhead sodium work light, 45° above subject, hard source, right side"
- "Blue-green monitor glow from below, diffused; main light source in this interior"
- "Overcast ambient; flat, directionless; no key source; even shadow-less illumination"

### Fill and Ratio

- "No fill — key-only; strong shadow on left cheek"
- "Practical desk lamp as fill, warm, low intensity; 5:1 ratio to key"
- "Bounce fill from white console surface; very soft; fills under-chin shadow"

### Practicals (Visible Light Sources)

List every light source visible in frame:

- "Navigation light on gannet wingtip — red, blinking, low intensity"
- "Rubber duck lit from below by monitor glow — blue-green tint on underside"
- "Two wall screens in background, green status displays, casting secondary fill"

### Colour Temperature Notes

Draw from the prompt keyword library. Do not invent new temperature descriptions.

---

## 4. Effects Direction

Be specific about physical phenomena in frame:

| Effect | How to Specify |
|--------|---------------|
| Rain | Intensity (mist / shower / heavy / driving); direction (vertical / lateral); visibility (barely visible / clear streaks / curtains) |
| Steam / smoke | Source (SMR vent / cooking / breath); direction; density; behaviour (rising straight / drifting) |
| Rotors | Spin state (static / ramping up / full speed); blur level; sound implication |
| Water on surfaces | Coverage (dry / damp / pooled / streaming); surface type (glass / metal / tarmac / skin) |
| Wind in environment | Which elements move (grasses / clothing / hair / fence wire); speed |

---

## 5. Audio Direction

Audio direction specifies what the video model should produce in the audio track.
See `video-prompt-guide.md` §5 for full handling rules.

Key distinction:

- **On-screen lip-sync dialogue** → include in `[AUDIO]` with exact words, tone, language
- **On-screen sound effects** → include with source, quality, timing
- **Off-screen narration** → do NOT include; handled separately
- **Non-diegetic music** → do NOT include; end with "No background music."

---

## 6. Direction for Specific Shot Types

### Establishing Shot (XW / W)

- Actor direction: usually absent or background figures; note any that are present
- Camera: locked tripod or slow Steadicam float; no motivated movement
- Key instruction: let weather and environment move; do not motivate the camera

### POV / Machine Vision Shot

- Actor direction: N/A (machine is the camera)
- Camera: gimbal-stabilised, no organic movement, digital precision
- Lighting: no grain, no filmstock characteristics; clean digital
- Specify: altitude, speed, heading

### Dialogue CU / OTS

- Actor direction: most critical here; exact head position, eyeline, micro-expression
- Camera: locked tripod or handheld with minimal movement
- Depth of field: moderate to shallow; background soft enough to read but not distracting

### Action / Motion Shot

- Actor direction: complete physical choreography with timing markers
- Camera: must follow or anticipate the action; specify if camera leads or lags
- Duration: verify the described action fits within the clip duration using the
  physical consistency constraint table in `video-prompt-guide.md` §4
