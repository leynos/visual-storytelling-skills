---
name: kling-3-0-deep-dive
description: >
  Deep operating guidance for Kling 3.0 video generation. Use when selecting Kling 3.0
  for a shot, designing multi-shot scene structure, writing Kling-native cinematic
  prompts, planning Elements or Motion Control references, using start/end frame
  anchors, handling native audio or dialogue, building product/commercial shots,
  choosing duration/aspect/quality settings, troubleshooting artifacts, or comparing
  Kling 3.0 against Seedance 2.0, Veo, Sora, DoP/Cinema, or other Higgsfield video
  routes. Complements shot-specifier and video-generator by turning Kling 3.0's
  scene-based model behaviour into practical production rules.
---

# Kling 3.0 Deep Dive

Use this skill when `shot-specifier` routes a shot to `kling3_0` or when
`video-generator` is about to submit Kling 3.0 jobs through the Higgsfield Model
Context Protocol (MCP).

Kling 3.0 is best treated as a **scene-directed cinematic video model**. It responds
well to shot labels, camera behaviour, physical motion, clear timing, and simple
subject/environment constraints. Think like a director and camera operator: what is the
shot, what moves, how does the camera react, what does the audience hear, and where does
the shot end?

## Live-Schema Rule

Before any production generation, inspect the live Higgsfield MCP schema through
`video-generator`. Public guides disagree on exact model IDs, quality modes, text
capabilities, Elements support, Motion Control support, native audio options, duration
ranges, and media roles.

Use the limits below as planning defaults only. If the live MCP schema is narrower,
follow the live schema. If the selected Kling route cannot accept the required anchors,
Elements, motion references, or audio parameters, stop and ask for a production
decision.

S01 session 2 observed a narrower Higgsfield MCP surface than public Kling guides
describe: Kling accepted `start_image` and `end_image`, did not expose a generic
reference-image role, did not expose `sound`, did not expose `cfg_scale`, and downloaded
16:9 outputs at `1344x768`. Treat Elements, Motion Control, CFG, sound toggles, and
labelled resolution choices as schema-gated features, not assumptions.

## When Kling 3.0 Is The Right Route

Prefer Kling 3.0 when the shot needs:

- explicit scene structure or 2-6 shot coverage in a single generation;
- clean cinematic camera movement: pans, tracks, dollies, orbits, reveals, drone moves;
- physically grounded movement, environmental interaction, impact, or macro texture;
- landscape establishing shots, machine/drone POV, exteriors, product hero moves, or
  camera-motion-led b-roll;
- start/end frame control or transition shaping;
- Elements or Motion Control when the live tool exposes them;
- native ambient audio, sound effects, or structured dialogue when the scene can be
  labelled unambiguously.

Do not default to Kling 3.0 when the shot's main problem is heavy reference-driven
identity preservation across many generated clips. Seedance 2.0 remains the safer
default when reference images must carry character, prop, or recurring visual element
identity. Also avoid asking Kling to invent exact UI, logos, legal copy, or critical
text. Bake text into a frame or add it in post.

## Planning Defaults

| Decision | Default | Reason |
|----------|---------|--------|
| Single-shot duration | 3-5 s for best quality; 6-8 s for simple one-vector moves | Shorter clips reduce drift and slot cleanly into edits |
| Multi-shot duration | 2-6 scenes, each with explicit duration; total up to live MCP limit | Kling responds strongly to labelled scene structure |
| Upper limit | 15 s only when each beat is timed and physically simple | Long clips need progression, not one overloaded paragraph |
| Aspect ratio | Choose before prompting | Aspect ratio changes composition pressure and camera path |
| 16:9 | Cinematic exteriors, landscapes, horizontal movement, narrative coverage | Gives room for camera logic and environment |
| 9:16 | One subject, product hero, or hook; reserve negative space for overlays | Tall frames punish busy backgrounds |
| 1:1 or 4:5 | Product/feed variants when supported | Keeps products readable and avoids wasted side detail |
| Resolution | Request the manifest's resolution hint when exposed; verify actual pixels after download | S01 current MCP evidence emitted `1344x768` even for 16:9 production shots |
| Quality | Draft in faster tiers; final in high quality after motion and framing are right | High quality is not a fix for bad direction |

## Prompt Structure

Kling prompts should read like production direction, not keyword lists.

Use this default order for a single shot:

```text
Camera + Subject and action physics + Environment + Lighting + Texture + Audio/style
```

Use this default order for structured narrative or dialogue:

```text
Scene + Characters + Action timeline + Camera + Audio and style
```

For product/commercial shots, use:

```text
Environment + Lighting + Camera movement + Product behaviour + Composition constraints
```

Write one to three rich sentences per shot. Specificity matters more than length. If the
prompt becomes a list of competing details, split the shot.

## Multi-Shot Structure

Kling 3.0 should receive labelled shots when the scene has more than one beat or camera
angle. Do not compress a storyboard into one paragraph.

```text
Total: 12 s / 3 shots / 16:9.
Shot 1 (0-4 s): Wide establishing shot...
Shot 2 (4-8 s): Medium tracking shot...
Shot 3 (8-12 s): Close-up reaction...
Audio: ...
Style: ...
```

Each shot needs:

- framing;
- subject and action;
- camera behaviour;
- duration;
- transition or continuity note;
- audio/dialogue if applicable.

Use multi-shot mode when narrative order and coverage matter more than perfect single
identity preservation. For identity-critical characters, combine multi-shot structure
with Elements or clean reference images when the live MCP route supports them.

## Camera And Motion Language

Camera language is a primary control surface for Kling.

Good camera phrases:

- slow dolly push-in;
- tracking shot following from the right;
- low-angle tracking shot;
- overhead bird's-eye view;
- static tripod wide shot;
- handheld shoulder-cam with subtle sway;
- rack focus from foreground hand to background figure;
- FPV drone chase;
- slow orbit right to left;
- top-down macro push-in.

Motion must be physically legible. Replace vague movement with mechanics:

- "walks heel-first with visible weight transfer";
- "fabric moves slowly in a light breeze from frame left";
- "steam rises in thin curls from the cap";
- "camera settles into a static product shot at the end";
- "the bike leans into the curve, sparks from the footpeg grazing asphalt".

Avoid impossible compound actions unless the shot is deliberately surreal. If the action
requires multiple subjects, specific contact, and a complex camera path, split it.

## References, Elements, And Motion Control

Use reference media for the job it is best at:

| Reference type | Use |
|----------------|-----|
| Start image | Lock identity, layout, style, product shape, or first frame |
| End image | Define where the motion resolves or bridge two clips |
| Elements / identity refs | Preserve character, object, product, or mascot across shots |
| Motion reference video | Transfer camera path, choreography, or physical action |
| Style reference | Maintain colour, lighting, and texture across a sequence |

For Elements, use 2-3 clean images per character/object when available: front,
three-quarter, and detail or full-body. Do not overload Elements with many weak references.
If the live route exposes only start/end images, do not list Elements or generic
references as uploadable requirements. Bake the identity, prop, location, and style
requirements into the storyboard start/end frames in `shot-specifier` Phase 5 and make
the Kling prompt preserve what is already visible in those frames.

For Motion Control, use a short driving clip that isolates the motion you actually want.
Describe what to copy and what not to copy:

```text
Use @Video1 for camera movement only: the slow orbit and final push-in. Do not copy its
lighting or background.
```

For image-to-video, lock first, then move. Treat the input frame as the source of truth.
Prompt how the scene evolves from it: subtle subject motion, camera move, lighting
change, environmental motion, or product behaviour.

## Dialogue And Native Audio

When native audio is enabled, dialogue must be attributed. Use stable labels and tone.

```text
The detective slides the folder across the table.
[Character A: Lead Detective, calm threatening voice]: "Then explain this."
Immediately, the suspect leans back, breathing quickens.
[Character B: Prime Suspect, trembling voice]: "That is impossible."
```

Rules:

- define each character early;
- keep character labels unique and consistent;
- describe the visual action before the dialogue;
- assign tone, language, accent, or pace when it matters;
- use temporal connectors: immediately, after a beat, pause, then;
- add ambient audio and specific sound effects as production cues.

Do not rely on pronouns in multi-character dialogue. If lip-sync is critical and the
live Kling route cannot bind voices to characters, stop or route elsewhere.

Narration is handled outside this video-generation workflow. Do not request generated
narration from Kling. If the live route forces generated audio on, proceed only for
ambient/environment shots where the audio will be accepted or muted downstream; stop for
dialogue, lip-sync, supplied-audio, music-timed, or narration/post-audio shots.

## Product And Commercial Prompting

Every strong product prompt needs four components:

1. **Environment:** material surface and background depth.
2. **Lighting:** source, direction, softness, highlights, and what the light hits.
3. **Camera:** one deliberate move and where it ends.
4. **Product behaviour:** steam, pour, condensation, fabric motion, powder, glow, fold,
   unfolding, reflection, or other micro-action.

Examples of useful product constraints:

- "white quartz worktop with subtle veining";
- "soft directional studio light from the left creating a single bottle-edge highlight";
- "backlit liquid creating a warm amber glow";
- "camera starts tight on label texture and pulls back to reveal the full bottle";
- "product occupies the lower third; upper two thirds remain clean negative space";
- "camera settles into a static centered hero frame at the end".

For multi-shot product ads, repeat exact physical product descriptors in every prompt or
use image-to-video / Elements if the route supports it. Do not assume a previous Kling
clip teaches the next job what the product is.

## Text, UI, Logos, And Branding

Public claims about Kling text rendering are mixed and access-surface dependent. This
pipeline treats critical text as unsafe to generate natively.

Use these rules:

- bake logos, labels, UI, legal copy, and screen text into start/end frames;
- keep product/logo motion simple;
- ask Kling to preserve existing text rather than invent new text;
- add overlays in post when readability matters;
- mark any native text generation as experimental and inspect it frame by frame.

## Style Lines

Kling responds to specific light, texture, and colour better than generic "cinematic"
language. Prefer concrete style lines:

- "golden hour side light, long shadows, dust visible in the beam";
- "flickering magenta and cyan neon reflecting across wet pavement";
- "harsh fluorescent overhead light on matte grey walls";
- "single softbox from upper left, controlled specular highlight";
- "35 mm film grain, shallow depth of field, desaturated teal grade";
- "documentary handheld, natural window light, authentic room tone".

Use the same style-bible sentence across a project only after it has tested well. Do not
let decorative style wording crowd out camera, action, and continuity instructions.

## Settings Sweep

When a Kling job fails, change one variable per run.

1. **Camera:** simplify to one camera move and one endpoint.
2. **Duration:** try 3-5 s before testing longer versions.
3. **Shot structure:** split a crowded prompt into labelled shots.
4. **References:** add start image, Elements, or a motion reference only for the missing
   control signal.
5. **Quality:** move to final quality only after composition and motion are correct.
6. **Aspect:** test the destination ratio early, especially for vertical ads.

For expensive jobs, draft in a faster/cheaper mode if exposed, then render the selected
prompt at final quality.

## Failure Rules

| Symptom | Response |
|---------|----------|
| Subject floats or feet slide | Add physical contact and weight-transfer language |
| Hands or fingers morph | Anchor hands to an object; avoid free-floating gestures |
| Product looks cheap | Specify material, one lighting source, highlight behaviour, and micro-action |
| Shot feels muddy | Remove extra subjects, camera moves, or background action |
| Background competes | Add shallow depth of field, clean background, or negative space |
| Camera wanders | Give one move and a final endpoint |
| Multi-character action misaligns | Split into simpler shots or use a motion reference |
| Dialogue speaker confusion | Add character labels, action before dialogue, and timing connectors |
| Text or logo mutates | Bake it into the frame or move it to post |
| Flicker | State one constant light source and simplify reflective surfaces |
| Render stalls near completion | Add an explicit motion endpoint such as "camera settles into a locked final frame" |

## Handoff Rules

`shot-specifier` should use this skill before Phase 7 when a shot is routed to
`kling3_0`. It should emit:

- why Kling 3.0 is the recommended model;
- whether the job is single-shot, multi-shot, image-to-video, start/end transition,
  Elements-led, Motion-Control-led, dialogue/audio-led, product/commercial, or
  machine/drone POV;
- duration and aspect ratio chosen using the defaults above;
- camera motion and final endpoint;
- required reference files with explicit purpose;
- any planned Elements, motion references, native-audio instructions, or text/UI
  safety notes;
- a concise `## Generation Prompt` suitable for the Higgsfield MCP.

`video-generator` should use this skill when submitting Kling 3.0 jobs. It should
validate:

- exact live MCP model ID for Kling 3.0;
- Phase 6 storyboard consistency status before job submission: all BLOCK findings must
  be resolved, all fixable WARN findings must be resolved, and every remaining WARN
  finding must already be converted into an explicit prompt constraint;
- Phase 13 extractor consistency status before handoff: prop consistency against the
  primary ref, cross-shot prop identity, and recurring visual element consistency are
  actionable requirements, not informational notes;
- live duration, resolution, quality, aspect-ratio, and audio support;
- whether the route accepts start/end frames, Elements, generic image references, motion
  references, seeds, quality modes, or Motion Control;
- whether every required frame, Element, reference, or dialogue/audio constraint can be
  supplied.

If the live tool limits prevent the planned camera, frame, Element, motion, or audio
contract from being supplied, stop. Do not silently downgrade to a plain text-to-video
job.
