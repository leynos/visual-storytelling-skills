# Prompt Keyword Library

Read this before Phase 2.4 (Prompt Keyword Library). It explains why a project-level
vocabulary library is required, what to put in it, how to structure it, and how to use
it during prompt writing.

---

## Why This Exists

Video and image generation models do not receive a grading spec. They receive text.
Technical values — "lifted blacks at 10–12 IRE", "15% global desaturation", "Vision3
250D characteristics" — are partially useful but are not the primary mechanism that
controls how output looks. Natural-language adjective phrases are.

The problem is that style vocabulary invented shot by shot drifts. "Cool grey pre-dawn"
in shot 3 and "cold blue morning" in shot 11 may produce noticeably different colour
temperatures even though the underlying spec is identical. Over a 20-shot production the
accumulation of small vocabulary variations produces visible tonal incoherence.

The prompt keyword library solves this by establishing canonical phrases during Phase 2,
immediately after the cinematography spec is finalized. Every model-routed prompt later
written by `shot-specifier` copies from the library rather than inventing language. The
library is the mechanism that makes the cinematography spec reproducible across
independently generated clips.

---

## What to Include

### 1. Global Style Phrase

A single sentence (or two) encoding the project's filmstock, grain character, and colour
process. This phrase opens every `[STYLE]` and `[FILMSTOCK]` field.

```text
Example:
"35 mm spherical, Kodak Vision3 250D characteristics, fine-to-medium organic grain,
accurate daylight balance, slightly desaturated shadows, gentle highlight rolloff,
standard C-41 process, no cross-processing"
```

Derive this directly from the cinematography specification. Do not paraphrase — copy the
key parameters as they were named in the spec, translated into adjective phrases.

### 2. Per-Location-Type Vocabulary

For each distinct location type in the production (exterior moor, interior bunker, control
room, etc.), write a canonical phrase set covering:

- Dominant colour temperature and cast
- Key light source and quality
- Shadow treatment
- Texture and surface character
- Atmosphere (haze, dust, humidity, rain)
- What must NOT appear (negative constraints)

```text
Example exterior overcast:
"flat pewter Atlantic overcast, no direct sun, wet peat and stone surfaces, fence posts
leaning eastward under wind, diffused ambient with no hard shadows, lifted blacks,
grey-green grass desaturated beyond global spec, no blue sky, no trees"

Example interior warm:
"warm amber-gold grow-light, artificial mid-summer feel, high humidity haze visible in
light shafts, strawberry scarlet at full vibrancy against amber surround, clean concrete
floor, no natural light from windows"
```

### 3. Per-Lighting-Condition Vocabulary

For each named lighting condition in the scouting matrix, write a canonical phrase:

```text
Example pre-dawn sodium:
"near-dark pre-dawn, sodium-orange practicals, deep grey-blue surround, rain halos
visible around point sources, wet tarmac reflecting orange sodium, no ambient daylight"

Example screen glow interior:
"blue-green monitor glow from below, faces underlit by screens, practical desk lights
mid-range, no windows, corrugated metal ceiling overhead"
```

### 4. Global Negative Constraints

A bulleted list of things that must never appear. These are injected into every prompt
to prevent the model defaulting to its training-data biases.

```text
Example:
- no trees (Lewis moor is treeless inland)
- no dual carriageways or modern road markings
- no blue sky (always overcast)
- no hard exterior shadows
- no real software logos on screens
- no US electrical sockets
- no right-hand drive vehicles visible
```

### 5. Selective Saturation and Colour Exemptions

List any objects that are exempt from the global colour treatment:

```text
Example:
- Strawberry scarlet is exempt from the global desaturation pass; maintain full
  vibrancy and push selectively against all surrounding desaturated elements
```

### 6. POV and Camera-Mode Overrides

For any shot type that requires a departure from the global filmstock spec, record the
override vocabulary explicitly:

```text
Example drone / machine-vision POV:
"digital-flat image, no film grain, deep focus throughout, no organic camera movement,
gimbal-stabilised, machine-vision rendering — clean, clinical, no atmospheric haze"
```

This is critical for productions that mix film-emulation exterior shots with machine-POV
digital sequences. If drone POV shots receive the same grain and desaturation prompt as
human-camera shots, the machine-POV distinction collapses.

---

## Format

Write the library as:

1. A section (`### Prompt Keyword Library`) inside the main scene inventory document
   under Creative Pillars
2. A standalone file: `{project_name}_prompt_keywords.md`

The standalone file is what `shot-specifier` should reference during video prompt
assembly. It should be short enough to read in under two minutes.

---

## How to Use During Shot-Specifier Prompt Assembly

For every video prompt assembled by `shot-specifier`:

1. **Open `{project_name}_prompt_keywords.md`** before writing.
2. **Copy the global style phrase** verbatim into `[STYLE]` and `[FILMSTOCK]`.
3. **Select the per-location vocabulary** for this shot's location type and paste into
   `[SCENE]`. Do not rewrite it — copy it.
4. **Select the per-lighting-condition vocabulary** and add to `[SCENE]`.
5. **Inject all applicable global negative constraints** at the end of `[SCENE]` or
   `[ACTION]`.
6. **Apply any POV overrides** if this is a machine-vision or special-mode shot.

If there is an urge to invent a new phrase not in the library, stop. Either the library
is missing that term (update the library first) or the invention is unnecessary. Adding
ad hoc vocabulary mid-production is how tonal drift starts.

---

## Updating the Library

The library is living documentation. If during Phase 12 (shot-frame generation) a phrase
consistently fails to produce the intended result, update the library with a better phrase
and regenerate affected frames. Do not let a known-bad
phrase persist in the library because updating it is inconvenient.

Document changes: add a brief note in the library file explaining what was changed and
why. This is especially important when the change affects phrases already used in
generated prompts, because it signals that those prompts may need regeneration.

---

## Common Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Tonal drift across shots | Style vocabulary invented per-shot rather than drawn from library | Build library in Phase 2.4; use it during `shot-specifier` prompt assembly |
| Grain appearing in drone POV | POV override not applied | Add machine-vision override to all POV shots |
| Forbidden elements appearing | Negative constraints not injected into prompts | Add global negative constraints to every prompt `[SCENE]` field |
| Colour exemptions ignored | Selective saturation rule not stated in prompt | Explicitly name exempt objects in `[ACTION]` or `[SUBJECT]` |
| Library vocabulary produces wrong result | Phrase is ambiguous or incorrect | Test with a style-anchor generation; revise the phrase; update the library |
