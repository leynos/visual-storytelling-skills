---
name: shot-specifier
description: >
  Per-shot production specification workflow: takes a completed scene inventory (from
  scene-inventory-extractor-v2) and decomposes every scene into numbered shots with full
  directorial direction — actor position and movement, camera mount and motion, lens,
  lighting setup, practical effects, timing, and clip boundaries. Generates storyboard
  keyframe images via nanobanana, assembles video generation prompts with model routing,
  and maintains an asset pipeline with consistent file naming and a generation manifest.
  Use when a scene inventory exists and the workflow must move from scene descriptions to
  individual, generation-ready clips. Also trigger when the user mentions "shot list",
  "shot breakdown", "storyboard", "video prompt", "model routing", "clip generation",
  or "per-shot direction".
---

# Shot Specifier

Takes a completed scene inventory and reference image set as input and produces
generation-ready shot specifications: numbered shots with full directorial direction,
storyboard keyframes, video prompts, model routing, and an asset pipeline.

This skill is explicitly **expensive**. Generating storyboard images for every shot in
every scene requires many image generation calls. Per-shot video generation is more
expensive still. This cost is the price of consistency and production quality — do not
skip shots or reduce keyframe coverage to save cost unless the user explicitly requests
it.

## Input Requirements

Before beginning, verify the following inputs are available:

| Input | Location | Required? |
|-------|----------|-----------|
| Scene inventory document | `{project}/scene-pack/{project}_scene_inventory.md` | Required |
| Reference images | `{project}/image_out/` or `{project}/refs/` | Required |
| Prompt keyword library | `{project}/{project}_prompt_keywords.md` | Required |
| Continuity inventory | `{project}/{project}_continuity_inventory.md` | Strongly recommended |
| Video role manifest | Section in scene inventory | Required |

If the prompt keyword library or video role manifest are absent, run
`scene-inventory-extractor-v2` phases 2.4 and 11.5 first before proceeding.

## Execution Context

This skill requires:

- **Image generation Model Context Protocol (MCP)** (`nanobanana` tools preferred; see `references/storyboard-generation.md`)
- **Vision capabilities** (for storyboard consistency verification)
- **File system access** (structured output directories)

Generation runs **silently** — no user confirmation gates during storyboard or prompt
phases. Halt only on consistency failures that require human judgement.

## Workflow Overview

| Phase | Name | Output |
|-------|------|--------|
| 1 | Input Audit | Verified inputs; flagged gaps |
| 2 | Shot Decomposition | Numbered shot list per scene with duration budgets |
| 3 | Frame Role Assignment | Video role mapping per shot from reference images |
| 4 | Shot Direction | Full directorial spec per shot |
| 5 | Storyboard Generation | Keyframe images via nanobanana |
| 6 | Storyboard Consistency Check | Vision QA; BLOCK/WARN report |
| 7 | Video Prompt Assembly | Full prompts with model routing |
| 8 | Asset Pipeline | File naming, generation manifest, tracking |

> **Read order:** Before Phase 4, read `references/shot-direction.md`. Before Phase 5,
> read `references/storyboard-generation.md`. Before Phase 7, read
> `references/model-routing.md`. The asset pipeline conventions are in
> `references/asset-pipeline.md`.

---

## Phase 1: Input Audit

1. Locate and confirm the scene inventory document.
2. Inventory all available reference images and note their categories (characters,
   locations, props, style anchors).
3. Load the video role manifest. If absent, derive it from the reference image manifest
   and scouting matrix in the scene inventory.
4. Load the prompt keyword library. If absent, halt and instruct the user to run
   scene-inventory-extractor-v2 Phase 2.4.
5. Load the continuity inventory if present. Flag if absent — continuity gaps will be
   carried forward as WARN items.
6. Record the list of scenes to be processed and their target clip counts.

---

## Phase 2: Shot Decomposition

For each scene in the scene inventory, decompose it into numbered shots.

### Duration Budget

Before writing any shot rows, establish a **duration budget**:

```text
* **Scene ID:** SC-{XX}
* **Scene description:** {brief}
* **Total duration target:** {N} seconds
* **Clip count:** {N} shots
* **Per-clip allocation:** SH001: {N}s, SH002: {N}s, ...
```

**Budget rules:**
- Clips must be 4, 6, or 8 seconds.
- One clip = one action in one location. If the action requires more than 8 seconds,
  split it.
- Multi-beat scenes need multiple clips. A scene with setup + action + reaction is three
  clips minimum.
- Establishing shots: 6–8 seconds. Insert/detail shots: 4 seconds. Dialogue beats: 6
  seconds. Complex action: 8 seconds.

### Shot Row Format

For each shot, record:

```markdown
#### {S{XX}_SH{XXX}}

| Field | Value |
|-------|-------|
| Shot ID | S{XX}_SH{XXX} |
| Frame size | XW / W / M / CU / ECU / POV / INS / OTS |
| Lens | {focal length} mm {spherical/anamorphic} |
| Camera mount | {tripod / Steadicam / handheld / crane / gimbal / drone} |
| Camera motion | {static / pan / tilt / dolly / arc / zoom / rise} |
| Visual action | {Concrete, filmable description} |
| Duration | {4 / 6 / 8} seconds |
| Pacing | {slow / moderate / fast} |
| Clip boundary | {continuous / scene_cut} |
| Start frame ref | {Ref ID from video role manifest} |
| End frame ref | {Ref ID or "generate-new"} |
| Grain/grade override | {override or "global spec"} |
```

---

## Phase 3: Frame Role Assignment

For each shot, assign specific reference images to video model input roles.

Use the video role manifest from the scene inventory as the primary source. Where a
reference image does not yet exist for the required role, flag it as `MISSING` and note
what needs to be generated.

```markdown
### S{XX}_SH{XXX} Frame Roles

| Role | File | Notes |
|------|------|-------|
| start_image | refs/locations/launch-strip/low-pre-dawn-rain.png | Pre-launch state |
| end_image | MISSING — generate in Phase 5 | Gannet mid-lift |
| image (subject ref) | refs/props/gannet-uav/primary.png | Identity anchor |
| image (style ref) | refs/style/style_anchor_01.png | Global look |
```

**Missing role resolution:** If a `start_image` or `end_image` is missing from the
reference library, generate it in Phase 5 (Storyboard Generation) as a storyboard frame,
then promote that generated image to a reference role for the video generation call.

---

## Phase 4: Shot Direction

For each shot, write full directorial direction covering:

### 4.1 Actor Direction

```text
* **Actor(s):** {Who is in frame}
* **Position:** {Where in frame — left/centre/right; near/mid/far; above/below eyeline}
* **Posture/body state:** {Standing, seated, leaning; tension or ease in body}
* **Action:** {Exact physical action — what they do, in what order, at what speed}
* **Eyeline:** {Where they look — at camera, at another character, off-frame}
* **Expression:** {Named expression from character bible or described precisely}
* **Continuity state entering scene:** {Wardrobe, carried items, body state}
* **Continuity state exiting scene:** {Any changes to the above}
```

For shots with no human subjects (establishing shots, drone POV, inserts), mark
actor direction as N/A.

### 4.2 Camera Direction

```text
* **Mount:** {Tripod / Steadicam / handheld / crane / drone gimbal}
* **Starting position:** {Physical location of camera at shot start}
* **Motion path:** {Exact description of camera movement — direction, speed, arc}
* **Ending position:** {Physical location at shot end}
* **Focal length:** {mm}
* **Depth of field:** {Shallow / moderate / deep; what is sharp, what is soft}
* **Shutter:** {180° default or override with reason}
```

### 4.3 Lighting Direction

```text
* **Key source:** {Natural / artificial; direction; quality — hard/soft/diffused}
* **Fill:** {Fill source or none; ratio to key}
* **Practicals:** {Any visible light sources in frame — colour, position, intensity}
* **Colour temperature:** {Draw from prompt keyword library for this location type}
* **Grade note:** {Scene-specific override from global cinematography spec, if any}
```

### 4.4 Effects Direction

```text
* **Practical effects:** {Rain, smoke, steam, dust, water, fire — present/absent}
* **Environmental motion:** {Wind in grasses, ripples on water, steam from vents}
* **Subject effects:** {Rotors spinning, droplets on fuselage, breath condensing}
```

### 4.5 Audio Direction

```text
* **Bed:** {Constant ambient — wind, hum, traffic, crowd}
* **Punctuations:** {Specific sounds at specific moments in the clip}
* **Dialogue:** {Exact words if on-screen lip-sync required; "off-screen" otherwise}
* **Music:** {Diegetic / non-diegetic / none}
```

---

## Phase 5: Storyboard Generation

> **Prerequisite:** Read `references/storyboard-generation.md`.

Generate storyboard keyframe images for every shot. Use the nanobanana MCP tools.

### Pre-Generation Reference Check (per shot)

Before generating any frame for a shot, verify:

1. A canonical reference image exists for every **named character** present in the shot.
2. A canonical reference image exists for every **named prop** visible in the shot.
3. A canonical reference image exists for the **specific location variant** (angle ×
   lighting condition) the shot requires.

If any is missing, generate it now before proceeding. This check is mandatory — a frame
generated without a prop reference will invent the prop's appearance independently,
producing a different-looking object from every other shot in the sequence.

### Generation Order

1. **Start frames** for all shots in the sequence.
2. **End frames** that require generation (not reused from scouting refs).
3. **Key frames** for shots with intermediate states specified.

### Start Frame Prompt Construction

Combine:
- Global style phrase from the prompt keyword library
- Location vocabulary for this shot's location type
- Lighting condition vocabulary for this shot's lighting condition
- Actor direction (position, action, expression, outfit)
- Camera direction (framing, angle, depth of field)
- Effects direction (rain, steam, etc.)
- Global negative constraints

Reference images to pass:
- Location ref matching the lighting condition
- Character ref(s) if human subjects present
- Prop ref(s) if significant props visible

Prompt ending: `"no text, no watermarks, no logos, no labels, no annotations"`

### End Frame Prompt Construction

**If the end frame shows the same subject in a significantly different state:**
- Use `edit_image` (edit from start frame)
- Pass the start frame as a reference
- Describe only what changes; do not repeat unchanged elements

**If the end frame shows a different composition, angle, or subject configuration:**
- Use `generate_image` (generate new)
- Pass the start frame + location ref as references
- Full prompt as for start frame but with end-state description

### File Naming

```text
shots/{shot_id}/start.png
shots/{shot_id}/end.png
shots/{shot_id}/key{NN}.png
```

---

## Phase 6: Storyboard Consistency Check

After generating all storyboard frames, run a vision-based consistency pass.

### Checks

| Check | Method | Flag if |
|-------|--------|---------|
| **Start–end interpolatability** | Compare start and end frames | Subject static; only lighting/bg changed; no interpolatable motion |
| **Character consistency** | Compare against character primary ref | Face, outfit, proportions diverge from reference |
| **Location consistency** | Compare against location ref | Architecture, layout, materials diverge |
| **Prop consistency** | Compare against prop ref | Shape, colour, detail diverge |
| **Cross-shot prop identity** | For each named prop: gather all frames in the sequence that contain it; view them together | The prop looks like a different physical object across shots — different construction, silhouette, or type |
| **Lighting continuity** | Compare start and end frames | Light direction or colour-temp contradicts direction spec |
| **Cross-shot continuity** | Compare end of SH{N} with start of SH{N+1} (if continuous) | Subject position, outfit, or environment jumps |
| **Style consistency** | Compare against style anchor | Grain character, palette, or colour-temp departs from global spec |

### Output

Write a storyboard consistency report:

```text
reports/storyboard_consistency_report.md
```

BLOCK-level issues must be resolved before Phase 7. WARN-level issues are logged for
human review and carried forward as notes in the video prompt.

---

## Phase 7: Video Prompt Assembly

> **Prerequisite:** Read `references/model-routing.md`. Phase 6 complete with no
> unresolved BLOCK issues.

For each shot, assemble a complete video generation prompt.

### Prompt Template

```markdown
# {S{XX}_SH{XXX}} — Video Prompt

## Metadata
- **Shot ID:** S{XX}_SH{XXX}
- **Scene:** SC-{XX} — {scene name}
- **Duration:** {4 / 6 / 8} seconds
- **Pacing:** {slow / moderate / fast}
- **Clip boundary (next):** {continuous / scene_cut}
- **Recommended model:** {model ID — see references/model-routing.md}
- **Model routing rationale:** {1 sentence explaining the routing choice}

## Frames
- **Start frame:** shots/{shot_id}/start.png
- **End frame:** shots/{shot_id}/end.png
- **Key frames:** {paths or "None"}

## Reference Roles
- **start_image:** {file path}
- **end_image:** {file path}
- **image (subject):** {file path(s)}
- **image (style):** refs/style/style_anchor_01.png

## Prompt

[STYLE] {Global style phrase from keyword library}
[FILMSTOCK] {Filmstock phrase from keyword library}
[SCENE] {Location vocabulary + lighting condition vocabulary + global negative constraints}
[FRAMING] {Frame size, lens, camera mount, motion path}
[PACING] {slow / moderate / fast — with clip-specific meaning}
[ACTION] {transition_description — 2–4 sentences; subject appearance, movement trajectory,
         state changes, existence statements}
[SUBJECT] {Subject key visual features for consistency}
[AUDIO] {Audio direction from Phase 4.5}
[DURATION] {4 / 6 / 8 seconds}

## Consistency Notes
- {Any WARN items from storyboard consistency check}
- {Continuity flags from shot list}
```

### Style Language Rule

Every `[STYLE]`, `[FILMSTOCK]`, and `[SCENE]` field copies from the project's prompt
keyword library. No ad hoc vocabulary.

### Continuity Constraint Injection

Before finalising each prompt, check:
- The location bible negative space rules for this location
- The continuity inventory for this scene
- Any WARN items from Phase 6

Inject all applicable constraints into `[SCENE]` or `[ACTION]`.

### Manifest

After writing all prompt files, produce:

```text
prompts/manifest.md
```

```markdown
# Shot Generation Manifest

| Shot ID | Scene | Duration | Model | Start | End | Keys | Prompt File |
|---------|-------|----------|-------|-------|-----|------|-------------|
| S11_SH001 | SC-11 | 8s | seedance_2_0 | shots/S11_SH001/start.png | shots/S11_SH001/end.png | None | prompts/S11_SH001_prompt.md |
```

---

## Phase 8: Asset Pipeline

> **Prerequisite:** Read `references/asset-pipeline.md`.

Maintain a consistent asset pipeline so generated clips can be traced back to their
source shots, retaken efficiently, and assembled in the correct order.

### File Naming Convention

```text
shots/{shot_id}/start.png          — start frame image
shots/{shot_id}/end.png            — end frame image
shots/{shot_id}/key{NN}.png        — key frame(s)
prompts/{shot_id}_prompt.md        — video generation prompt
generated/{shot_id}/v{N}.mp4       — generated video clip (v1 = first take, v2 = retake)
generated/{shot_id}/selected.mp4   — symlink or copy of the selected take
```

### Generation Log

After each video generation call, log:

```markdown
## Generation Log

| Shot ID | Date | Model | Job ID | Duration | Status | Take | Notes |
|---------|------|-------|--------|----------|--------|------|-------|
| S11_SH001 | 2026-05-04 | seedance_2_0 | b767b7e1-... | 8s | completed | v1 | |
```

Write to: `generated/generation_log.md`

This log is essential for:
- Tracing which job ID corresponds to which shot (for retrieval and retakes)
- Identifying shots that need to be regenerated
- Tracking cost across the production

---

## Reference Files

| File | Read Before | Contents |
|------|-------------|----------|
| `references/shot-direction.md` | Phase 4 | Full directorial notation guide: actor, camera, lighting, effects, audio |
| `references/storyboard-generation.md` | Phase 5 | nanobanana usage for storyboards, prompt construction, reference-role assignment |
| `references/model-routing.md` | Phase 7 | Video model selection by shot type; routing criteria; known model characteristics |
| `references/asset-pipeline.md` | Phase 8 | File naming conventions, generation log format, retake workflow |

## Templates

| File | Used In |
|------|---------|
| `templates/shot-spec-template.md` | Phases 2–4 |

## Best Practices

**One Shot, One Action.** Every clip contains one action in one location. If a scene
description contains "and then", split it.

**Budget First, Decompose Second.** Never start writing shot rows without a clip-duration
budget. The budget prevents scene collapse.

**Direction is Concrete.** Actor direction specifies position, action, and eyeline.
"Looks concerned" is not direction. "Holds gaze on the empty screen, jaw still, for
two seconds then turns toward Iain" is direction.

**Storyboards are a Consistency Investment.** Generating storyboard frames before video
generation catches reference drift early. One regenerated storyboard frame costs far
less than one regenerated video clip.

**Copy Keyword Library, Do Not Paraphrase.** Every `[STYLE]`, `[FILMSTOCK]`, and
`[SCENE]` field copies from the prompt keyword library verbatim. Paraphrasing introduces
vocabulary drift.

**Inject Negative Constraints on Every Prompt.** The location bible's negative space
rules (no trees, no US road markings, no blue sky) must appear in every exterior prompt.
The model does not remember previous prompts.

**Log Every Generation Call.** Job IDs are the only way to retrieve or retake a specific
clip. Log them immediately. An unlogged job is a lost job.

**Retakes Are Part of the Pipeline.** Not every first take is the right take. The asset
pipeline distinguishes v1 from v2 from selected. Budget for at least one retake per
complex shot.

**Machine Vision Shots Get Machine Vision Prompts.** Drone POV, surveillance feed,
and telemetry-screen shots must suppress grain, filmstock, and organic movement. Apply
the POV override vocabulary from the keyword library — do not accidentally apply the
film-emulation spec to a shot that is supposed to look like a camera drone.
