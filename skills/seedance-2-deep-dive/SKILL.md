---
name: seedance-2-deep-dive
description: >
  Deep operating guidance for Seedance 2.0 video generation. Use when selecting
  Seedance 2.0 for a shot, designing multimodal references, writing Seedance-native
  prompts, choosing duration/aspect/quality settings, planning batch generations,
  troubleshooting drift or artifacts, or comparing Seedance 2.0 against Kling, Veo,
  Sora, DoP/Cinema, or other Higgsfield video routes. Complements shot-specifier and
  video-generator by turning Seedance 2.0's multimodal model behaviour into practical
  shot-planning and generation rules.
---

# Seedance 2.0 Deep Dive

Use this skill when `shot-specifier` routes a shot to `seedance_2_0` or when
`video-generator` is about to submit Seedance 2.0 jobs through the Higgsfield Model
Context Protocol (MCP).

Seedance 2.0 is best treated as a **constraint-driven multimodal video model**, not a
text-prompt toy. Text describes the new action. Images, video, and audio references
carry identity, style, motion, rhythm, and continuity. The practical skill is deciding
which constraints matter, passing them explicitly, and keeping each clip short enough
that the model does not drift.

## Live-Schema Rule

Before any production generation, inspect the live Higgsfield MCP schema through
`video-generator`. Public guidance and creator reports disagree on exact model IDs,
quality modes, file limits, duration ranges, and reference roles.

Use the limits below as planning defaults only. If the live MCP schema is narrower,
follow the live schema. If the required references cannot be supplied, stop and ask for
a production decision.

S01 session 2 observed that the current Higgsfield MCP accepted a Seedance
`resolution=1080p` input while still downloading `1344x768` video, and auto-enabled
generated audio without exposing a `generate_audio` input key. Treat resolution settings
as schema-gated quality hints until the downloaded pixels prove otherwise. Treat audio
toggles as intent records unless the live schema exposes them.

## When Seedance 2.0 Is The Right Route

Prefer Seedance 2.0 when the shot needs:

- consistent character, costume, product, prop, or recurring visual element identity;
- multiple image references acting as hard creative constraints;
- a short but polished action beat, hook, transformation, product move, or b-roll shot;
- audio-driven pacing from a chosen track, ambience, voice, or sound-effect reference;
- campaign or sequence coherence across many clips;
- image-to-video work from carefully designed start and end frames.

Do not default to Seedance 2.0 when the main requirement is maximum native resolution,
long single-shot duration, low-setup one-off generation, exact on-screen text, complex
hands, or a large multi-character scene with many competing subjects. Consider Kling for
camera-motion-heavy exteriors or motion-control work; consider Veo/native-audio routes
when generated audio is the asset rather than an input constraint.

## Planning Defaults

| Decision | Default | Reason |
|----------|---------|--------|
| Duration | 6-8 s first pass; 4-6 s for identity-critical inserts; keep most clips under 10 s | Drift rises with duration; split long ideas into crisp segments |
| Upper limit | 15 s only for deliberate hero tests or structured multi-shot prompts | Last seconds are more likely to soften, mutate, or lose continuity |
| Aspect ratio | Choose before writing the prompt | Ratio changes composition pressure and what the model emphasises |
| 9:16 | One strong subject, clean background, text safe area if overlays exist | Tall frames push faces and foreground action forward |
| 16:9 | Add background control: simple layout, limited background motion, clear negative space | Wide frames invite extra set detail and artifacts |
| 1:1 or 4:5 | Product, feed, and commercial detail when supported | Keeps product scale readable without excessive background |
| Quality | Draft in fast/medium; final in high only after the shot is coherent | Higher quality sharpens both good detail and bad wobble |
| Resolution | Use the manifest's resolution hint for finals when exposed; verify actual pixels after download | S01 current MCP evidence emitted `1344x768` despite a `1080p` Seedance hint |
| Batch strategy | Build a shot list and reference plan before spending credits | Random exploration burns budget and weakens continuity |

## Multimodal Input Rules

Treat each input as responsible for one job. Avoid overlapping references that ask for
different styles, lighting, faces, or motion in the same slot.

Planning limits commonly reported for Seedance 2.0:

- up to 12 files total across images, videos, and audio;
- up to 9 image references;
- up to 3 video references, with short clips preferred;
- up to 3 audio references, with clean, short clips preferred;
- generated output commonly planned in the 4-15 s range.

Verify those values against the live Higgsfield MCP before generation.

Prioritise file slots in this order:

1. Start and end frame anchors when the workflow requires them.
2. Principal character or product identity.
3. Active hero prop and recurring visual elements.
4. Specific location or set layout.
5. Motion or camera reference video.
6. Audio reference for beat, mood, voice, or ambience.
7. Style reference.
8. Supporting detail references.

If the tool exposes input weights, start here:

| Input | Starting weight | Use |
|-------|-----------------|-----|
| Character/product image | 0.80-0.85 | Exact appearance, costume, object design, brand detail |
| Aesthetic/style image | 0.75-0.80 | Colour, lighting, texture, finish |
| Environment image | 0.60-0.75 | Location layout and atmosphere |
| Motion/camera video | 0.50-0.60 | Camera path, choreography, pacing |
| Audio reference | 0.40-0.50 | Mood, tempo, energy, beat timing |

Raise a weight only when that input is underrepresented. Lower it when it dominates the
shot or pulls the output away from higher-priority continuity.

## Reference Prompting

Use `@` references or the MCP's equivalent media-role syntax with a declared purpose.
Never pass references as an undifferentiated pile.

Bad:

```text
Use @Image1, @Image2, and @Video1 to make this cinematic.
```

Good:

```text
@Image1 for Switch's exact face, hair, and jacket. @Image2 for the control-room monitor
layout and screen colours. @Video1 for the slow handheld push-in only, not its lighting.
```

For character consistency, use the same master character image or small character
package in every shot where the character appears. State that facial features, build,
hair, and costume identity must remain exact. For recurring visual elements, pass the
locked reference every time the element is visible.

## Prompt Structure

For simple image-to-video shots:

```text
Subject + Action + Scene + Camera + Style
```

Keep the prompt concrete. One subject, one action, one place, one camera idea. Use verbs
and timing, not mood labels alone.

For multimodal production shots, use CRAFT:

| Section | Purpose |
|---------|---------|
| Context | Location, time, atmosphere, story situation |
| References | Which media inputs matter and exactly what each controls |
| Action | What subjects do, in physical order |
| Framing | Shot size, lens feel, camera mount, movement, angle |
| Timing | Seconds, beats, cuts, audio sync, ending state |

For multi-shot prompts, specify shot structure up front:

```text
Total: 8 s / 2 shots / 16:9.
Shot 1, 0-4 s: ...
Shot 2, 4-8 s: ...
```

For one continuous shot, say so explicitly and add camera negatives:

```text
Single continuous shot. No cuts, no zoom, no angle changes, natural head movement.
```

## Format Patterns

Use these patterns as starting points, not templates to paste blindly.

| Format | Strong pattern |
|--------|----------------|
| Transformation | Numbered beats with an escalation arc: calm, disruption, transformation, consequence, reset |
| POV | Say the camera is the character's eyes; no cuts; hands visible if needed; natural head movement; concrete body motion |
| Fight or chase | Clear location, clear power mismatch or objective, beat-by-beat choreography, impact timings |
| Product/commercial | Product refs first; simple motion; limited background; lock logo/text in the source image rather than asking the model to invent it |
| B-roll/hook | 3-6 s, one clean visual idea, immediate readable motion, strong first frame |
| Animation/VFX | Timed segments; explicit VFX appearance inline; physics and particles described concretely |
| Audio-synced | Use the audio reference for tempo and mood; mark visual events against seconds or beats |

Narration is handled outside this video-generation workflow. Do not request generated
narration from Seedance. If the live route forces generated audio on and cannot disable
it, proceed only for ambience/sound-effect-friendly atmosphere shots where the audio
will be accepted or muted downstream; stop for dialogue, lip-sync, supplied-audio,
music-timed, or narration/post-audio shots.

## Settings Sweep

When a shot is not working, change one variable per run. Keep prompt, seed, and
references fixed unless that variable is the thing being tested.

1. **Duration:** compare 6 s against 8-10 s. If the shorter clip is cleaner, split the
   shot.
2. **Aspect ratio:** test the target ratio with one line rewritten for composition
   pressure: single subject for 9:16, controlled background for 16:9.
3. **Quality:** raise quality only after the first two seconds are stable.
4. **Reference weights:** increase the missing constraint; reduce the dominant,
   unhelpful one.
5. **Seed:** keep a good seed for refinement; refresh if colour or identity keeps
   drifting despite coherent references.

Stop tweaking settings when the shot concept itself is overloaded. Split, simplify, or
return to `shot-specifier` for a new shot design.

## Failure Rules

| Symptom | Response |
|---------|----------|
| First two seconds wobble | Restart or simplify the opening beat; early instability rarely fixes itself |
| Face, logo, prop, or recurring element changes shape | Split the shot or strengthen the exact reference; do not rely on quality mode |
| Lighting flickers | Anchor one source and one surface; if it persists, shorten or change angle |
| Hands break | Avoid complex gestures; show hands at rest or cut to a separate insert |
| Output feels chaotic | Reduce camera moves, subjects, and beat count; replace frantic language with smooth pacing |
| Motion reference dominates | Lower video-reference weight and restate image references as identity anchors |
| Image style is weak | Increase style/reference image weight and remove conflicting aesthetic language |
| Audio does not drive timing | Use cleaner audio, shorter audio, and explicit second/beat markers |
| Text or UI is wrong | Bake text/UI into the start or end frame; animate minimally |

## Handoff Rules

`shot-specifier` should use this skill before Phase 7 when a shot is routed to
`seedance_2_0`. It should emit:

- why Seedance 2.0 is the recommended model;
- duration and aspect ratio chosen using the defaults above;
- required reference files with explicit purpose;
- any planned motion or audio references;
- whether the prompt is single-shot, multi-shot, POV, transformation, product,
  animation/VFX, or audio-synced;
- a concise `## Generation Prompt` suitable for the Higgsfield MCP.

`video-generator` should use this skill when submitting Seedance 2.0 jobs. It should
validate:

- exact live MCP model ID for Seedance 2.0;
- live duration, resolution, quality, and aspect-ratio support;
- whether the route accepts start/end frames, generic image references, video
  references, audio references, weights, seeds, and quality modes;
- whether every required reference can fit inside the live file limit.

If live tool limits prevent the reference plan from being supplied, stop. Do not drop a
character, prop, recurring visual element, start frame, or end frame to make the call
fit.
