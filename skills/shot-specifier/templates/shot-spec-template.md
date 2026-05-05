# Shot Specification Template

One section per shot. Complete all fields. Leave none blank — write "N/A" only when the
field genuinely does not apply (e.g., actor direction for an establishing shot with no
human subjects).

---

## Scene Duration Budget

Complete once per scene before writing individual shot specs.

```text
**Scene ID:** SC-{XX}
**Scene name:** {Brief name}
**Total duration target:** {N} seconds
**Clip count:** {N} shots
**Per-clip allocation:**
  - SH001: {N}s
  - SH002: {N}s
  - SH003: {N}s
  ...
```

---

## Shot Specification: {S{XX}_SH{XXX}}

### Basic Fields

```text
**Shot ID:** S{XX}_SH{XXX}
**Scene:** SC-{XX} — {scene name}
**Frame size:** XW / W / M / CU / ECU / POV / INS / OTS
**Lens:** {focal length} mm {spherical / anamorphic}
**Camera mount:** {tripod / Steadicam / handheld / crane / drone gimbal}
**Camera motion:** {static / pan left-right / tilt up-down / dolly forward-back /
                    arc CW-CCW / rise-fall / zoom in-out}
**Duration:** {4 / 6 / 8} seconds
**Pacing:** {slow / moderate / fast}
**Clip boundary (next):** {continuous / scene_cut}
**Grain / grade override:** {override description or "global spec"}
```

### Frame Roles

```text
**Start frame ref:** {Ref ID or "generate-new in Phase 5"}
**End frame ref:** {Ref ID or "generate-new in Phase 5"}
**Key frames required:** {Yes — N frames / No}
**End frame derivation:** {edit-from-start / generate-new}
**Interpolatable change:** {What changes between start and end}
```

### Actor Direction

```text
**Actor(s):** {Name(s) or "None"}
**Position (start):** {Lateral / depth / vertical}
**Posture / body state:** {Standing, seated, leaning; tension or ease}
**Action:** {Exact physical action with timing and speed}
**Eyeline:** {Where they look and when}
**Expression:** {Named expression or precise description}
**Continuity state entering:** {Wardrobe, carried items, body-state}
**Continuity state exiting:** {Any changes from entering state}
```

### Camera Direction

```text
**Mount:** {See above}
**Starting position:** {Physical camera location}
**Motion path:** {Direction, speed, arc extent}
**Ending position:** {Physical camera location at end}
**Depth of field:** {What is sharp; what is soft; approximate f-stop}
**Shutter:** {180° / override with reason}
```

### Lighting Direction

```text
**Key source:** {Source name, position, quality}
**Fill:** {Source or "none"; ratio to key}
**Practicals in frame:** {List each visible source with colour and intensity}
**Colour temperature:** {Draw from keyword library}
**Grade note:** {Scene-specific override or "global spec"}
```

### Effects Direction

```text
**Rain:** {Present / absent; if present: intensity, direction, visibility}
**Wind:** {Present / absent; if present: which elements move, speed}
**Steam / smoke:** {Present / absent; if present: source, density, behaviour}
**Rotors / mechanical:** {State and appearance}
**Water on surfaces:** {Coverage and surface type}
**Other effects:** {Anything not covered above}
```

### Audio Direction

```text
**Bed:** {Constant ambient — source and character}
**Punctuations:** {Specific sounds at specific moments; format: "[Ns] {sound}"}
**Dialogue:** {Exact words if on-screen; "off-screen" or "none" otherwise}
**Music:** {Diegetic source / "none" / "non-diegetic — handle in post"}
**Audio generation preferences:** ambient={on/off}; sfx={on/off}; dialogue={on/off};
music=off; narration=off; source={generated/none/supplied}; preserve_silence={true/false}
```

### Video Prompt (assembled in Phase 7)

```text
[STYLE] {Copy from keyword library}
[FILMSTOCK] {Copy from keyword library}
[SCENE] {Location + lighting vocabulary + negative constraints — copy from keyword library}
[FRAMING] {Frame size + angle + lens + camera motion}
[PACING] {slow / moderate / fast — with clip-specific meaning}
[ACTION] {2–4 sentences: subject appearance, movement, state changes, existence statements}
[SUBJECT] {Key visual features for consistency}
[AUDIO] {From audio direction above}
[DURATION] {4 / 6 / 8 seconds}
```

### Audio Generation Preferences

```text
**Ambient audio:** {on/off}
**Sound effects:** {on/off}
**On-screen dialogue/lip-sync:** {on/off}
**Music:** off
**Narration:** off
**Audio source:** {generated / none / supplied}
**Preserve silence:** {true/false}
```

### Generation Prompt

```text
{Model-native prompt flattened from the structured tags using
references/model-routing.md. This is the exact prompt for video-generator.}
```

### Model Routing

```text
**Recommended model:** {model ID}
**Routing rationale:** {1 sentence}
**Resolution parameter:** {720p / 1080p / 4K / model-specific equivalent}
**Model overrides:** {key=value list; include audio, mode/quality, cfg/guidance, genre}
**Count:** {1 by default; 2 only when review-gated and schema-supported}
**Required refs:** {semicolon-delimited list of continuity-critical refs}
```

### Consistency Notes

```text
{Any WARN items anticipated; cross-references to continuity inventory; prop positions}
{Action taken: regenerated frame, added reference, injected prompt constraint, or blocker}
```

---

<!-- Duplicate this section for each shot in the scene -->
