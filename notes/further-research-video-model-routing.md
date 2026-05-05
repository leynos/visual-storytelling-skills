# Further Research: Video Model Routing

**Purpose:** Establish empirical routing rules for assigning shots to specific video
generation models. Results should be used to update
`skills/shot-specifier/references/model-routing.md`.

**Background:** During the first experimental generation pass on *The Strawberry Bunkers
of Lewis* (2026-05-04), SC-11 (the gannet launch) was generated as a single clip using
Seedance 2.0 with start/end frame anchoring. The result was functional but several
routing questions remain unresolved. The current `model-routing.md` contains only
first-pass heuristics. This document sets out what needs to be tested and why.

---

## Models to Evaluate

Test against all models currently available via the Higgsfield MCP:

| Model ID | Provider | Notes |
|----------|---------|-------|
| `seedance_2_0` | Bytedance | Primary test subject; used in first experiment |
| `seedance_1_5` | Bytedance | Compare quality/motion vs 2.0 |
| `kling3_0` | Kling | Multi-shot and audio capabilities |

Include any additional models available at the time of research that were not listed
above.

---

## Research Questions

### 1. Shot-Type Strengths and Weaknesses

For each of the following shot types, which model produces the best result, and what
are the characteristic failure modes of each model?

| Shot Type | Description | Key Quality Criteria |
|-----------|-------------|---------------------|
| Consistent subject action | UAV taking off; character walking; door opening | Subject identity consistency; motion realism; anchor fidelity |
| Landscape establishing | Wide moor, sea, exterior — no characters | Environmental motion (wind, rain, waves); atmosphere fidelity |
| Machine vision / drone POV | Aerial shot rendered as digital-flat, no grain | Absence of film grain; gimbal stability; digital precision |
| Interior dialogue CU | Character at console; talking head | Face consistency; lighting consistency |
| Insert / ECU detail | Strawberry close-up; console detail; blinking light | Sharpness; depth of field; minimal unnecessary motion |
| Multi-beat sequence | Complex action with setup + event + reaction | Narrative coherence across the clip; timing |
| Pre-dawn low-light exterior | Near-dark; practical lights; rain halos | Correct light handling; no blown highlights; visible rain |

### 2. Start/End Frame Anchoring Behaviour

- How faithfully does each model reproduce the start frame as the first frame of the
  generated clip?
- How faithfully does it reproduce the end frame as the final frame?
- What is the transition quality between the two anchors?
- Does providing only a start frame (no end frame) produce better or worse results for
  simple motion shots?
- What is the practical quality gain from providing an end frame vs not providing one?

### 3. Prompt Vocabulary Effectiveness

- To what degree do filmstock and grain vocabulary in the text prompt influence the
  output, vs the start/end frame images dominating?
- For machine-vision shots, does the POV override vocabulary ("digital-flat, no grain,
  gimbal-stabilised") reliably suppress organic grain and movement, or does the model
  default to its prior?
- Are there model-specific vocabulary terms that work particularly well or poorly?
- Does prompt length matter? Is a very short prompt + strong reference images better
  than a detailed prompt + same references?

### 4. Reference Image Influence

- How does the number of reference images affect output quality? At what point does
  adding more references produce averaging artefacts?
- What is the optimal reference image set for: (a) shots with no human subjects; (b)
  shots with one character; (c) shots with multiple characters?
- Does the `image` role (consistency reference, not frame anchor) meaningfully influence
  output, or does the model weight it much lower than `start_image`/`end_image`?

### 5. Duration and Motion Quality

- Does clip duration (4s vs 8s vs 15s) affect subject identity consistency?
- Are very short clips (4s) more or less reliable than longer clips for complex actions?
- At what clip duration does motion quality degrade?

### 6. Model-Specific Parameters

For `seedance_2_0`:

- Does `genre` selection (auto / action / horror / drama / epic) meaningfully change the
  output for non-genre material (e.g., documentary-style shots)?
- Does `mode` (std vs fast) meaningfully affect quality, or only speed?

For `kling3_0`:

- How does multi-shot mode work? What constraints apply?
- Is audio generation reliable enough for on-screen sound effects?
- How does motion transfer from a reference video work in practice?

### 7. Cost-Quality Tradeoff

- What is the cost per clip for each model at each duration?
- For the full shot list of a ~20-scene production, what is the expected total cost
  under different routing strategies?
- At what cost per shot does the quality gain from using a more expensive model
  become justified for different shot types?

---

## Test Protocol

### Test Set

Run each test using source material from *The Strawberry Bunkers of Lewis* where
possible, to maintain relevance to the production context. Use scene inventory shots
where reference images already exist.

Priority test shots:

1. **S11_SH001** — Gannet on cradle, pre-dawn static (establishing)
2. **S11_SH002** — Rotor spin-up and vertical lift (action with consistent subject)
3. **S12_SH001** — Minch crossing drone POV (machine vision)
4. **S08_SH001** — Switch arriving at console (character interior)
5. **S05_SH001** — Bunker interior establishing (warm interior establishing)
6. **S14_SH001** — Gannet icon vanishing from screen (screen content + reaction)

### Test Variables

For each shot, test:

- All available models
- With and without end frame
- With strong vs minimal text prompt
- With global negative constraints vs without

### Recording Results

For each test, record:

- Model used
- Parameters used (duration, resolution, mode, genre)
- Reference images provided and their roles
- Prompt text (verbatim)
- Job ID
- Qualitative assessment: subject identity (1–5), motion quality (1–5), style fidelity
  (1–5), anchor fidelity (1–5), overall (1–5)
- Specific failures noted
- Notes on what would improve the result

Record results in a structured log file alongside this document:
`notes/model-routing-test-log.md`

---

## Expected Outputs

At the end of this research, produce:

1. **Updated `skills/shot-specifier/references/model-routing.md`** with:
   - Confirmed routing rules replacing the working heuristics
   - Updated shot-type routing table with confirmed model choices and confidence ratings
   - Model-specific prompt vocabulary notes
   - Known failure modes per model per shot type

2. **`notes/model-routing-test-log.md`** with all test results

3. **A brief summary** of the three most important findings and the three biggest
   surprises, written directly into the introduction of the updated `model-routing.md`

---

## Prioritisation

If research time is limited, prioritise in this order:

1. Machine vision / drone POV shots — this is the highest-uncertainty routing question
   because it requires suppressing the model's default cinematic aesthetics
2. Character identity consistency across multi-shot sequences — this is the most
   expensive failure mode (if character drift occurs, the entire sequence must be reshot)
3. Start/end frame anchoring behaviour — understanding how faithfully anchors are
   reproduced determines how much storyboard investment is warranted
4. Prompt vocabulary effectiveness — this determines whether the prompt keyword library
   approach is actually doing work, or whether the images dominate
