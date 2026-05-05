# Video Model Routing

Read this before Phase 7 (Video Prompt Assembly). Covers how to route individual shots
to the appropriate video generation model.

> **Scope and confidence note**
> This routing guidance synthesises current official documentation, creator tests,
> comparison write-ups, and recurring user reports as at early May 2026. The evidence
> log is at `notes/model-routing-online-evidence-log.md`. Treat this document as
> reconnaissance, not law: use it to narrow the search space and set defaults, then
> confirm any expensive or identity-critical rule with direct tests on *The Strawberry
> Bunkers of Lewis* reference material. Confidence labels refer to the quality of the
> public evidence, not to any universal truth about the models.
>
> **Unresolved questions still requiring direct tests** are flagged explicitly below.
> The research brief with the full test protocol remains at
> `notes/further-research-video-model-routing.md`.

---

## Top-Line Synthesis

Three findings matter most for this production.

1. **Seedance 2.0 appears strongest when references must carry the shot**: identity,
   look, lighting, and asset continuity. It is multimodal, anchor-heavy, and performs
   best in single-character action, dialogue-adjacent close-ups, product/prop
   image-to-video, and shots where audio sync matters.
   When routing a shot to `seedance_2_0`, load `seedance-2-deep-dive` before writing the
   final prompt and manifest row.

2. **Kling 3.0 appears strongest when the shot needs explicit scene structure, camera
   logic, or motion transfer**: multi-shot sequences, aerials with clean geometric
   anchors, photorealistic exteriors, and any shot where you can drive motion from a
   reference video. Kling Motion Control, not plain text prompting, is the strongest
   public case for difficult human or physical action.
   When routing a shot to `kling3_0`, load `kling-3-0-deep-dive` before writing the
   final prompt and manifest row.

3. **Neither model is trustworthy for generated UI or exact on-screen text**: bake
   critical screens into the reference frame and animate minimally instead.

Three surprises from the public evidence:

- Public evidence for machine-vision aesthetics is much thinner than public evidence for
  cinematic action; prompt vocabulary alone (`digital-flat`, `machine vision`) has not
  been reliably shown to suppress cinematic defaults. This remains the least settled
  routing problem.
- Seedance 2.0 now has confirmed 1080p support on current surfaces, despite early
  reviews anchoring it to 720p.
- Concise, well-structured prompts have outperformed sprawling ones in large-sample
  Seedance 2.0 creator tests — counter to the usual "more words = more control"
  folk wisdom.

---

## Available Models (Higgsfield)

| Model ID | Provider | Type | Key Characteristics |
|----------|---------|------|---------------------|
| `seedance_2_0` | Bytedance | Video | Reference-driven; consistent subject identity; multimodal input (up to 12 assets, `@`-tagged roles); first-frame and first-plus-last-frame image-to-video; return-last-frame support; 2–15 s; 480p/720p/1080p; native audio/lip-sync |
| `seedance_1_5` | Bytedance | Video | Accepts references but weights them less heavily than 2.0; explicit camera-move prompting; 4/8/12 s; secondary/legacy only |
| `kling3_0` | Kling | Video | Multi-shot structure (2–6 scenes with per-scene duration); Motion Control (motion transfer from driving clip); Elements (cross-shot identity consistency); audio generation; 3–15 s; 720p/1080p |
| `marketing_studio_video` | Higgsfield | Video | Commercial/product/ads; URL-driven; see `show_marketing_studio` tool |

**Available-but-unrouted:** Current Higgsfield/MCP surfaces also expose Veo 3.1, Sora 2,
Wan 2.6/2.7, Kling o1, and traces of Kling 2.6 and Hailuo 02. No high-value comparative
evidence has been gathered for these models against *The Strawberry Bunkers of Lewis*
material. Route only when a separate evidence pass has been completed.

---

## Shot-Type Routing

| Shot type | Primary | Secondary / fallback | Confidence | Working rule |
|-----------|---------|---------------------|------------|--------------|
| Consistent subject action | `seedance_2_0` | `kling3_0` Motion Control, then plain `kling3_0` | Medium | Default to Seedance 2.0 when references define the subject. If you have a usable driving clip, jump straight to Kling Motion Control. |
| Landscape establishing | `kling3_0` | `seedance_2_0` | Medium | Use Kling for wide exteriors; anchor the move to a simple geometric centre if possible. Fall back to Seedance when multiple visual references matter more than environment realism. |
| Machine vision / drone POV | `kling3_0` experimental | `seedance_2_0` experimental | **Low — unresolved** | Reference-led and post-led. Use explicit camera negatives, clean visual refs, and expect retries. See open questions below. |
| Interior dialogue CU (speaking) | `seedance_2_0` | `kling3_0` | Medium | Seedance's audio-visual sync and single-character continuity give it the stronger public case when the character speaks. |
| Interior dialogue CU (silent) | `kling3_0` | `seedance_2_0` | Medium | Kling is cleaner for locked close-ups and photoreal facial motion when there is no lip-sync requirement. |
| Insert / ECU detail | `seedance_2_0` (baked first frame) | `kling3_0` (non-text macro only) | Low–medium | Never ask either model to invent critical UI copy. Animate a prepared plate instead. |
| Multi-beat sequence | `kling3_0` multi-shot | `seedance_2_0` | Medium | Use Kling when narrative order and shot coverage matter more than pure action energy. |
| Pre-dawn low-light exterior | `kling3_0` | `seedance_2_0` | Low–medium | Start on Kling with strong refs. Fall back to Seedance only if the shot needs more explicit asset conditioning. |

---

## Cross-Cutting Rules

### Anchoring

Use **start frame by default**. Add **end frame only** when the final composition,
transformation, or explicit transition design matters more than organic mid-clip motion.

- Seedance's first-plus-last-frame mode is best when opening and closing states are
  already designed; all-in-one reference mode is better for exploration.
- Kling start/end frames are most useful for transitions and morph-like changes.
- Dual-anchor interpolation on complex organic movement is not yet reliably demonstrated
  in the public test corpus — treat it as provisional.

### Prompting

Assume **camera language and action structure matter more than decorative cine-jargon**.

- Seedance responds well to clear, concise prompts that stay precise; short well-
  structured prompts have outperformed long ones in public large-sample tests. Explicit
  negatives for camera logic work. "No cuts, no zoom" helps keep POV locked.
- Kling responds well to shot labels, camera movement specification, scene-by-scene
  structure, and camera language phrasing. Multi-shot generation should specify timing
  and scene boundaries explicitly.
- Niche tokens such as `digital-flat` or `machine vision` have not been shown to
  reliably suppress cinematic bias by themselves; that is an inference from what
  successful public prompts actually contain, not a confirmed rule.

### Model-Native Prompt Flattening

Phase 7 prompt files keep structured `[TAG]` blocks for review, but each file must also
include a plain `## Generation Prompt` for `video-generator`. Build that plain prompt
with the model-specific order below. Do not use one generic ordering across models.

**Common inputs:** `[STYLE]`, `[FILMSTOCK]`, `[SCENE]`, `[FRAMING]`, `[PACING]`,
`[ACTION]`, `[SUBJECT]`, `[AUDIO]`, `[DURATION]`, reference roles, duration, aspect
ratio, resolution, and audio-generation preferences.

#### Seedance 2.0 Flattening

Use when `Recommended model` is `seedance_2_0`.

1. Start with `[ACTION]`: the physical transition, movement trajectory, state changes,
   and what persists from start to end.
2. Add `[SUBJECT]` only for identity-critical traits not fully carried by references.
3. Add reference-purpose sentences: which uploaded image/audio/video is responsible for
   subject identity, location, style, motion, or rhythm.
4. Add `[SCENE]` constraints, keeping location negatives and continuity rules concrete.
5. Add `[FRAMING]`, `[PACING]`, and `[DURATION]`.
6. Add `[AUDIO]` as generation preferences, always including `No narration.`
7. Add `[STYLE]` and `[FILMSTOCK]` last and keep them concise; references should carry
   most style weight.
8. Append anchor statements: `The start image is the first frame. The end image is the
   final frame. Preserve all supplied reference-image identities and layouts throughout.`

If the prompt must be shortened, trim `[FILMSTOCK]`, then decorative `[STYLE]`, then
non-critical `[PACING]`. Never trim `[ACTION]`, `[SUBJECT]`, reference-purpose
sentences, frame anchors, or audio prohibitions.

#### Kling 3.0 Flattening

Use when `Recommended model` is `kling3_0`.

1. Start with scene context and shot structure. For multi-shot work, use labelled blocks:
   `Shot 1 (0-5s): ...`, `Shot 2 (5-10s): ...`.
2. Put `[FRAMING]` and camera behaviour early, including camera endpoint or where the
   camera settles.
3. Add `[ACTION]` with physically plausible motion, timing markers, and subject-camera
   relationship.
4. Add `[SUBJECT]` and any Elements or Motion Control reference plan.
5. Add `[SCENE]` constraints and baked-frame/text/UI notes.
6. Add `[AUDIO]` with speaker labels only when on-screen lip-sync is required; otherwise
   state ambient/sfx preferences and `No narration.`
7. Add one compact `[STYLE]` / `[FILMSTOCK]` line last.
8. Append anchor statements for start/end frames and reference preservation.

If the prompt must be shortened, trim decorative style first, then extra texture, then
non-critical atmosphere. Never trim shot labels, camera movement, action physics, frame
anchors, speaker attribution, or audio prohibitions.

#### DoP / Cinema Route Flattening

Use only when the manifest explicitly approves a Higgsfield DoP/Cinema route and the live
MCP schema exposes it. Start with how the image evolves from the start frame, then camera
treatment, endpoint, environment motion, and style. Keep action simple and do not add
new identity details unsupported by references.

#### Unapproved / Unknown Routes

Stop. Do not invent a generic flattened prompt for an unrouted model.

### References

Assume **Seedance 2.0 weights references heavily** and **Kling 3.0 wants fewer, cleaner
identity elements**.

- Seedance 2.0: multimodal, up to 12 assets, explicit `@`-tagged role assignment. For
  human characters: neutral front-facing close-up, full-body image, and one extra angle
  (45° or profile). Group assets for each actor separately.
- Kling Elements and Motion Control: 2–3 clean identity images for Elements; add a
  driving video clip for Motion Control when you need precise motion. Avoid overloading
  the model.

### Duration

Cap expectations harder than the marketing. Both surfaces allow up to ~15 s, but
coherence degrades beyond 8–10 s for identity- or action-critical work, especially with
multiple subjects.

| Use case | Target duration |
|----------|----------------|
| Close-ups, inserts, identity-critical shots | 4–6 s |
| Simple continuous movement | 6–8 s |
| Landscape, one-vector camera moves | 8–10 s |
| Hero-shot experiments, structured multi-shot | up to 15 s |

### Fast vs. Standard Mode (Seedance 2.0)

**Draft in fast, keepers in standard.** Fast roughly halves cost and latency; public
comparative testing is not yet strong enough to set a more aggressive rule. Treat any
claim of fast/standard parity as provisional until direct tests are run on this
production's specific shot categories.

### Cost Scenario (Planning Only)

These are scenario maths using published rates and reported retry behaviour — not quotes.

- **Seedance 2.0 API floor:** approx. $0.39–$0.86 per video (ModelArk pricing, duration-
  dependent).
- **Kling standard no-audio API floor:** approx. $0.084 per second; ~$0.21 for 5 s,
  ~$0.42 for 10 s. Pro/native-audio variants cost more.
- **Retry dominates nominal cost.** A 60-shot Seedance-heavy plan at public API floor
  lands ~$23–$52 before retries; a 60-shot Kling-standard plan lands ~$13–$25. Fold in
  plausible creator-reported retry multipliers and realistic floors become roughly
  $35–$104 (Seedance-heavy) and $19–$63 (Kling-heavy).
- On Higgsfield's plan pages, Kling 3.0 equates to roughly 8.7 credits per video; per-
  clip plan maths for Seedance 2.0 are less explicit on public surfaces.

---

## Model-Specific Guidance

### Seedance 2.0 — Primary

**Recommended use:** Primary.
**Confidence:** Medium.

**Known strengths:** Reference-heavy continuity; single-subject action; multimodal anchor
workflows; dialogue-adjacent close-ups; product- and prop-led image-to-video; shots where
audio sync matters.

**Known failure modes:** Small text and UI generation; micro-hand interactions; busy
multi-character compositions; occasional over-cinematic bias; coherence drift in clips
over 10 s.

**Prompting:** Keep prompts clear and structured; let references do identity work; use
explicit negatives for camera logic; prefer short, controlled clip durations.
For detailed Seedance-native multimodal prompt structure, reference-file prioritisation,
duration/aspect defaults, settings sweeps, and troubleshooting, use the
`seedance-2-deep-dive` skill.

**References:** Front-facing close-up + full-body + one extra angle for humans; hero prop
or environment plate + optional motion reference for non-human shots.

**Duration:** 4–8 s by default; 10 s only with simple motion; longer only for hero tests.

**Fallback:** `kling3_0`.

---

### Seedance 1.5 — Secondary / Legacy

**Recommended use:** Secondary / legacy only.
**Confidence:** Low.

**Known strengths:** Explicit camera-move prompting; native audio/video positioning from
early reviews.

**Known weaknesses:** Lighter reference weighting than 2.0; no high-value public evidence
shows a category where 1.5 clearly beats 2.0 for this production.

**Use only when:** The specific access surface exposes a materially cheaper or more
available route, or if direct tests show its looser reference behaviour helps a low-risk
shot.

**Fallback:** `seedance_2_0`.

---

### Kling 3.0 — Primary

**Recommended use:** Primary.
**Confidence:** Medium.

**Known strengths:** Multi-shot structure with per-scene timing; camera-language response;
realistic photographic exteriors; aerials with clean geometric anchors; Elements for
cross-shot identity consistency; Motion Control for difficult choreography and physical
action.

**Known failure modes:** Lip-sync inconsistency; colour shifts between cuts; character
drift with larger casts or longer sequences; weak text/UI generation.

**Prompting:** Think in shots, timing, scene boundaries, and camera moves. For difficult
physical action, prefer Motion Control over plain prompting — the public case for Motion
Control is materially stronger than for text-only generation in action categories.
For detailed Kling-native scene structure, camera language, Elements and Motion Control
planning, native audio/dialogue syntax, product prompt anatomy, and troubleshooting, use
the `kling-3-0-deep-dive` skill.

**References:** 2–3 clean identity images for Elements; driving clip for Motion Control;
avoid overloading the model.

**Duration:** 3–5 s per shot in multi-shot mode; longer only for one-vector moves or
simple establishing footage.

**Fallback:** `seedance_2_0`.

---

## Priority-Shot Routing for This Production

| Shot | First model | Fallback | End frame | Reference strategy | Expected risks | Retry estimate | Confidence |
|------|------------|----------|-----------|-------------------|----------------|----------------|------------|
| `S11_SH001` Gannet on cradle, pre-dawn static | `kling3_0` | `seedance_2_0` | Usually no | Environment plate + precise static/wide camera instruction; limit motion to rain, halo, atmosphere | Low-light mush; over-dramatic bloom; cinematic texture creep | 2–4 | Medium-low |
| `S11_SH002` Rotor spin-up and vertical lift | `seedance_2_0` | `kling3_0` Motion Control if a driving clip is available | Start-only first; add end only if final altitude/composition matters | Strong start frame; clean prop geometry; short duration; single action arc | Rotor deformation; unstable lift path; wandering mid-clip if end frame over-constrains | 2–5 | Medium |
| `S12_SH001` Minch crossing drone POV | `kling3_0` experimental | `seedance_2_0` experimental | Only if final framing matters more than natural travel | Hard visual refs for display character, horizon, exposure, stabilisation; camera-language negatives over style poetry | Cine look creeping in; drift; fake handheld; unwanted bloom/grain | 3–6 | **Low** |
| `S08_SH001` Switch arriving at console | `seedance_2_0` | `kling3_0` | Usually no | Character close-up + full-body + extra angle; keep move simple and duration short | Face drift; hand-console interaction errors; overactive mouth motion | 2–4 | Medium |
| `S05_SH001` Bunker interior establishing | `seedance_2_0` | `kling3_0` | No | Feed production-design references aggressively; keep movement minimal | Warm lighting collapsing to generic cinema; prop hybridisation; soft detail | 2–4 | Medium |
| `S14_SH001` Gannet icon vanishing from screen | `seedance_2_0` (baked screen plate) | `kling3_0` (baked screen plate) | Possibly — if the final UI state matters | Build UI precisely in first frame; ask only for limited motion/change | Garbled text; UI mutation; unnecessary camera motion | 1–3 if plate-led; much worse if text is generated natively | Medium |

---

## Open Questions — Direct Tests Required

These questions cannot be resolved from public evidence alone:

1. **Machine-vision / drone-POV aesthetic.** Can either model produce a convincing
   machine-vision look without reverting to glossy cinema, given only prompt vocabulary
   and visual references? Test one aerial plate on `kling3_0` and one on `seedance_2_0`
   using the same Lewis references and a strict "no handheld / no cuts / fixed exposure /
   clean digital image" prompt block.

2. **Dual-anchor reliability on Seedance 2.0.** Does first-plus-last-frame generation
   arrive at the end frame gracefully for organic physical motion (e.g., the gannet lift
   in `S11_SH002`), or does it honour it only loosely?

3. **Seedance 2.0 fast mode quality delta.** Is fast mode adequate for draft-quality
   reference generation on this production's specific shot categories?

4. **Kling 3.0 for pre-dawn low-light exteriors.** Does it genuinely outperform Seedance
   2.0 on Lewis references at low light, or does cinematic grain still dominate?

5. **Seedance 2.0 `genre` parameter.** Does any exposed `genre` control (`drama`, `epic`,
   `action`, `auto`) materially affect routing for documentary-adjacent shots on the
   actual Higgsfield/MCP surface used for this production?

Update this document and the evidence log as each question is answered by direct test.

---

## Logging Requirements

For every video generation call, log in `generated/generation_log.md`:

- Shot ID
- Date
- Model used
- Job ID (critical — this is the only retrieval handle)
- Duration
- Status
- Take number
- Routing rationale (why this model was chosen; which rule in this document was applied)
- Result quality notes

The routing rationale in the log is the primary mechanism for building empirical evidence
to update and confirm the rules in this document. Do not skip it.

---

## Updating This Document

When direct tests (see `notes/further-research-video-model-routing.md`) produce confirmed
routing rules:

1. Move confirmed findings from the open questions section to the relevant routing table
   or cross-cutting rules section.
2. Update confidence ratings.
3. Record the source (test session date, shot IDs tested) for each confirmed rule.
4. Add a new entry to `notes/model-routing-online-evidence-log.md`.
