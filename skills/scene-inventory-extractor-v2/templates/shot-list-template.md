# Shot List Template

Template and guidelines for creating shot lists with full cinematography specifications,
start/end frame definitions, and video-prompt-ready fields.

---

## Sequence Header Format

```markdown
##### Sequence S{XX} — "{Evocative Title}"
```

The title should be operational, capturing what the sequence accomplishes narratively.

---

## Shot Table Structure (Expanded)

The expanded table splits across two linked sections per shot: the **shot table row**
(for the overview) and the **shot detail block** (for frame specifications and prompt
preparation).

### Shot Table Row

| Column | Purpose | Values |
|--------|---------|--------|
| **Shot ID** | Unique identifier | `S{XX}_SH{XXX}` |
| **Frame** | Shot size | XW / W / M / CU / ECU / POV / INS / OTS |
| **Lens** | Focal length + type | e.g. "50 mm spherical", "40 mm anamorphic" |
| **Motion** | Camera movement | static / pan / tilt / dolly / zoom / crane / arc / handheld / Steadicam |
| **Visual action** | What we see | Concrete, filmable, present tense |
| **Audio** | What we hear | Beds + punctuations + technical notes |
| **Function** | Why shot exists | Single phrase |
| **Continuity** | Constraints | Must/must-not |
| **Duration** | Shot length | 4 / 6 / 8 seconds |
| **Pacing** | Rhythm feel | slow / moderate / fast |
| **Boundary** | Clip boundary to next | continuous / scene_cut |
| **Grade note** | Per-shot override | If different from global cinematography spec |

### Shot Detail Block

Immediately following the table (or linked by Shot ID), provide for each shot:

```markdown
**{Shot ID} — Frame Specification**

* **Start frame:**
  * Framing: {Shot size + angle + lens effect}
  * Visible content: {What is in frame — subjects, objects, environment}
  * Subject state: {Pose, expression, position in frame}
  * Lighting: {Condition key from location scouting matrix}

* **End frame:**
  * Framing: {Shot size + angle — may differ if camera moves}
  * Visible content: {What is in frame at end}
  * Subject state: {New pose, expression, position}
  * Lighting: {Same unless explicitly changing}

* **Key frames (if any):**
  * Key 01 ({timing}): {Intermediate state description}
  * Key 02 ({timing}): {Intermediate state description}

* **Interpolatable change:** {What changes between start and end — position, pose, state, composition}
* **End-frame derivation:** {edit-from-start / generate-new}

* **Reference images to use:**
  * Character: {refs/characters/{name}/{variant}.png}
  * Location: {refs/locations/{name}/{condition}.png}
  * Props: {refs/props/{name}/{variant}.png}

* **Transition description (for video prompt):**
  {2–4 sentence description including subject appearance, movement trajectory,
  state changes, and existence statements. This text feeds directly into the
  [ACTION] field of the video prompt.}
```

---

## Frame Type Codes

| Code | Full Name | Description | Typical Use |
|------|-----------|-------------|-------------|
| **XW** | Extreme Wide | Full geography; figures small | Establishing; scale |
| **W** | Wide | Full environment; figures recognisable | Scene geography; groups |
| **M** | Medium | Waist-up | Dialogue; interaction |
| **CU** | Close-Up | Head and shoulders | Emotion; reaction |
| **ECU** | Extreme Close-Up | Single feature | Tension; detail; decision |
| **INS** | Insert | Object or detail | Props; UI; evidence |
| **POV** | Point of View | Character's literal vision | Subjective; machine vision |
| **OTS** | Over the Shoulder | Behind character | Dialogue; screen viewing |

---

## Camera Motion Reference

| Motion | Mechanism | Physical Constraint |
|--------|-----------|-------------------|
| **Static** | Locked tripod | No movement |
| **Pan** | Tripod head rotation (horizontal) | Fixed position; rotation only |
| **Tilt** | Tripod head rotation (vertical) | Fixed position; rotation only |
| **Dolly** | Camera translates forward/backward | Rails or smooth surface |
| **Tracking** | Camera translates laterally | Parallel to subject movement |
| **Crane** | Camera rises/falls | Vertical + optional lateral |
| **Arc** | Camera orbits subject | Circular path around fixed point |
| **Zoom** | Focal length change (no spatial translation) | Optical; do not confuse with dolly |
| **Handheld** | Operator-held | Walking speed; permitted shake |
| **Steadicam** | Stabilised operator rig | Walking speed; smooth |

### Edit vs Generate Decision

| Motion | Start/End Share Content? | End-Frame Derivation |
|--------|--------------------------|---------------------|
| Static | Yes | edit-from-start |
| Small pan/tilt | Yes | edit-from-start |
| Zoom | Yes | edit-from-start |
| Large pan | No | generate-new |
| Dolly/tracking | No | generate-new |
| Crane | No | generate-new |
| Arc | Partial | generate-new |
| Handheld (small) | Yes | edit-from-start |
| Handheld (large) | No | generate-new |

---

## Visual Action Guidelines

Descriptions must answer "What does the camera see?" — not "What does the character feel?"

**Effective:**

- "Rain beads crawling down windscreen; wipers half-hearted"
- "Hand taps dash twice; boot loop spins on monitor"
- "Football sticker half-covering fiducial marker; confidence overlay flickers"

**Ineffective (rewrite these):**

- "Miette feels frustrated" → What does the camera see?
- "The atmosphere is tense" → What visual detail creates tension?
- "Something important happens" → What specific action?

---

## Audio Notes Guidelines

Specify beds (continuous) and punctuations (discrete). Include technical notes.

**Components:**

- **Bed:** continuous environmental sound
- **Punctuation:** discrete sounds marking moments
- **Technical:** compression, distance, processing

**Examples:**

- "Rain roof + distant road wash" (bed + ambient)
- "Cabin hum; tiny boot chime" (bed + punctuation)
- "Tinny radio compression; background office chatter" (technical + bed)

---

## Narrative Function Categories

| Category | Description |
|----------|-------------|
| **Establish** | Sets up world, character, or situation |
| **Introduce** | Brings new element into story |
| **Show** | Demonstrates something already introduced |
| **Characterise** | Reveals character through action |
| **Escalate** | Increases tension or stakes |
| **Resolve** | Concludes or answers earlier setup |
| **Transition** | Bridges between scenes or states |
| **Punctuate** | Provides rhythmic beat or visual rest |

---

## Continuity Flags Guidelines

State constraints as must/must-not:

- "Avoid modern car UI reflections"
- "UI must be generic/fictional"
- "UK road markings; left-hand traffic"
- "No recognisable platform logos"
- "Same outfit as SC-01 (no change in scene interval)"

---

## Match-Cut Opportunities

Note visual rhymes between shots at the end of each sequence:

```markdown
**Match-cut opportunity (S{XX}):** {Element A} → {Element B} ({similarity}).
```

**Examples:**

- "Rain streaks on windscreen → vertical scanline flicker on drone feed (directionality)"
- "Coffee ring stain → heatmap circular pattern (shape echo)"
- "Phone crack lines → map grid lines (geometry)"

---

## Complete Example

```markdown
##### Sequence S01 — "Work is the world"

| Shot ID | Frame | Lens | Motion | Visual action | Audio | Function | Continuity | Dur | Pace | Boundary | Grade |
|---------|-------|------|--------|--------------|-------|----------|------------|-----|------|----------|-------|
| S01_SH001 | INS | 85mm sph | static | Rain beads on windscreen; wipers half-hearted | Rain roof + road wash | Establish weather baseline | No modern UI reflections | 4s | slow | continuous | — |
| S01_SH002 | CU | 50mm sph | static | Hand taps dash; Waythru boot loop on screen | Cabin hum; boot chime | Put us in labour-space | UI must be generic | 6s | moderate | continuous | — |
| S01_SH003 | ECU | 40mm ana | slow dolly in | Monitor grid: four feeds + GIS queue | Rotor whine (faint); UI click | Establish multi-feed grammar | No recognisable logos | 6s | slow | scene_cut | Slight cool push |

**S01_SH001 — Frame Specification**

* **Start frame:**
  * Framing: Insert, macro, tight on glass surface, 85mm
  * Visible content: Windscreen glass with rain beads; blurred wipers mid-sweep; indistinct road beyond
  * Subject state: Rain static (beads forming); wiper at left of frame
  * Lighting: Day, overcast, diffused grey

* **End frame:**
  * Framing: Same
  * Visible content: More rain accumulated; wiper now at right of frame (completed one sweep)
  * Subject state: Rain heavier; wiper has moved
  * Lighting: Same

* **Key frames:** None
* **Interpolatable change:** Wiper position moves from left to right; rain accumulation increases
* **End-frame derivation:** edit-from-start

* **Reference images to use:**
  * Location: refs/locations/car-interior/dashboard-day-rain.png

* **Transition description:**
  Rain beads cling to the windscreen glass throughout, slowly accumulating from scattered drops to
  dense rivulets. A single wiper blade sweeps steadily from the left edge of frame to the right
  over four seconds, smearing the water into brief clear arcs that immediately re-bead. The road
  beyond the glass remains a diffused grey blur. The glass surface, dashboard edge at bottom of
  frame, and rubber wiper blade are present throughout.

**Match-cut opportunity (S01):** Rain streaks on windscreen → vertical scanline flicker on drone feed (same directionality).
```

---

## Quality Checklist

| Check | Question |
|-------|----------|
| **Coverage** | Sequence covers all narrative beats? |
| **Variety** | Appropriate mix of shot types? |
| **Rhythm** | Shot types create appropriate pacing? |
| **Concreteness** | All visual actions filmable? |
| **Audio** | Every shot has audio guidance? |
| **Function** | Every shot's purpose clear? |
| **Continuity** | All constraints flagged? |
| **Lens** | Focal length specified and appropriate? |
| **Motion** | Camera motion specified and physically achievable? |
| **Duration** | 4, 6, or 8 seconds; appropriate to action? |
| **Start/end frames** | Both fully described for every shot? |
| **Interpolatable change** | End frame differs from start in position/pose/state/composition? |
| **Edit vs generate** | Derivation method correct per decision table? |
| **References listed** | Correct character, location, prop refs identified? |
| **Transition description** | ≥ 2 sentences with all four components? |
| **Boundaries** | Continuous boundaries match adjacent shot start frames? |
| **Match-cuts** | Visual rhymes identified? |
