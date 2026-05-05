# Model Routing — Online Evidence Log

This file records the sources used to build and update the routing guidance in
`skills/shot-specifier/references/model-routing.md`. Add a new entry whenever a routing
rule is updated, whether from online research or from direct production tests.

Each entry records: the source, its type and quality rating, what was claimed, and what
production implication was drawn. Entries are ordered by the date the evidence was
reviewed, newest at the top.

---

## 2026-05-05 — Online testimonial review pass

Synthesis document: investigation outcomes provided by research pass dated 2026-05-05.
Full synthesis available in the conversation record for this date.

---

### Seedance 2.0 API reference and current tutorial

- **Author / creator:** Official docs team
- **Platform:** Official documentation
- **Date of source:** 23–26 April 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Seedance 2.0
- **Evidence type:** Official documentation
- **Evidence rating:** High for feature availability; medium for quality claims
- **Raw outputs shown:** No
- **Prompts / settings disclosed:** Partial
- **Failures shown:** No
- **Relevant shot types:** All; especially anchoring and reference-heavy shots
- **Key claims:** 2–15 s duration; 480p/720p/1080p support; multimodal input; first-frame
  and first-plus-last-frame image-to-video modes; return-last-frame support
- **Production implication:** Trust documented constraints and modes. Do not treat the
  docs as proof of aesthetic reliability.

---

### Real-human asset library guidance for Seedance 2.0

- **Author / creator:** Official docs team
- **Platform:** Official documentation
- **Date of source:** 14 April 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Seedance 2.0
- **Evidence type:** Official workflow guidance
- **Evidence rating:** High for reference-image handling guidance
- **Raw outputs shown:** No
- **Prompts / settings disclosed:** Partial
- **Failures shown:** Yes — consistency-check failure discussed procedurally
- **Relevant shot types:** One-character shots; dialogue close-ups; identity-critical work
- **Key claims:** Recommends front-facing neutral close-up plus full-body references;
  consistency checks matter; assets for one actor should stay grouped
- **Production implication:** Character packs should include at least a neutral portrait
  and a full-body image before generation starts.

---

### Seedance 2.0 Hands-On Review — OpenCreator

- **Author / creator:** OpenCreator Team
- **Platform:** Creator / workflow review
- **Date of source:** 23 February 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Seedance 2.0
- **Evidence type:** Hands-on workflow analysis
- **Evidence rating:** Medium-high
- **Raw outputs shown:** Selected examples, not a raw benchmark pack
- **Prompts / settings disclosed:** Partly
- **Failures shown:** Yes, mostly as workflow risks rather than frame-by-frame failures
- **Relevant shot types:** Anchor-led image-to-video; complex motion; talking-head
  alternatives
- **Key claims:** Four-modal input with explicit `@` reference tagging; first-and-last-
  frame mode is better when start and finish are already designed; all-in-one reference
  mode is better for exploration; Seedance's sweet spot is complex motion, multimodal
  control, narrative continuity
- **Production implication:** Use start/end anchors sparingly and deliberately. Do not
  route every shot to Seedance just because the feature list is long.

---

### Seedance 2.0 vs 1.5 Pro direct comparison — Runware

- **Author / creator:** Not clearly surfaced
- **Platform:** Comparison blog
- **Date of source:** 20 February 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Seedance 2.0, Seedance 1.5 Pro
- **Evidence type:** Comparison / workflow note
- **Evidence rating:** Medium
- **Raw outputs shown:** Yes on page (not fully parsed)
- **Prompts / settings disclosed:** Partial
- **Failures shown:** Not clearly
- **Relevant shot types:** Identity and environment continuity
- **Key claims:** 2.0 treats references as anchors; 1.5 accepts references but leans on
  them less heavily
- **Production implication:** Identity-critical routing should favour 2.0, not 1.5.

---

### Is Seedance 2.0 Overhyped? — Curious Refuge (Tyler Smith)

- **Author / creator:** Tyler Smith
- **Platform:** Creator review — Curious Refuge
- **Date of source:** 20 February 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Seedance 2.0; Kling 3.0 in side-by-side examples
- **Evidence type:** Hands-on review with failure discussion
- **Evidence rating:** High among creator tests
- **Raw outputs shown:** Examples shown; not a full raw dataset
- **Prompts / settings disclosed:** Partial
- **Failures shown:** Yes
- **Relevant shot types:** Action; complex VFX; multi-shot continuity; close-up
  performance; detail shots
- **Key claims:** Seedance shines in physics and large motion; beats Kling in the examples
  shown for complex VFX and continuity; weak in fine detail and subtle emotional
  performance
- **Production implication:** Route hero action to Seedance more readily than inserts, UI,
  or subtle acting.

---

### Kling 3.0 Honest Reviews — Curious Refuge

- **Author / creator:** Site staff
- **Platform:** Creator benchmark / review — Curious Refuge
- **Date of source:** 5 February 2026; later February update
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Kling 3.0
- **Evidence type:** Benchmark-style review
- **Evidence rating:** High among creator tests
- **Raw outputs shown:** Yes, but curated
- **Prompts / settings disclosed:** Partial
- **Failures shown:** Yes
- **Relevant shot types:** Aerials; locked close-ups; multi-shot sequences; lip-sync shots
- **Key claims:** Kling is "physics-first"; orbiting aerials work best when the shot has
  one axis and a stable anchor; locked-off close-ups are strong; colour grading can shift
  between cuts; lip-sync and cloning still drift
- **Production implication:** Route clean geometric aerials and structured coverage to
  Kling, but stay wary of speech-heavy close-ups and larger casts.

---

### Kling 3.0 on Higgsfield — Motion Control / Start & End Frames (Mariam Barova)

- **Author / creator:** Mariam Barova
- **Platform:** Official product guide — Higgsfield
- **Date of source:** 3 February 2026; 5 March 2026; 3 September 2025 (start/end article)
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Kling 3.0; Kling Motion Control; Kling start/end frames
- **Evidence type:** Official workflow documentation
- **Evidence rating:** High for feature availability; medium for quality claims
- **Raw outputs shown:** Selected showcase material
- **Prompts / settings disclosed:** Partly
- **Failures shown:** No
- **Relevant shot types:** Multi-beat sequences; motion transfer; transitions
- **Key claims:** 3–15 s duration; 720p/1080p outputs; 2–6 scenes in multi-shot mode;
  audio support; Motion Control workflow; start/end transition design
- **Production implication:** Use Kling when you need planned scene structure or motion
  transfer. Treat the transition language as capability confirmation, not proof of exact
  frame fidelity.

---

### Kling V3 Motion Control raw tests — Wiro AI

- **Author / creator:** WiroBlogAgent
- **Platform:** Raw-test blog — Wiro AI
- **Date of source:** 8 March 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Kling V3 Motion Control
- **Evidence type:** Raw creator tests
- **Evidence rating:** Medium-high
- **Raw outputs shown:** Yes, explicitly "as-is"
- **Prompts / settings disclosed:** Yes
- **Failures shown:** Minor artefacts shown verbally
- **Relevant shot types:** Dance; gesture transfer; fashion motion; motion-led character
  shots
- **Key claims:** Motion follows the driving clip well; fast hand motion still shows edge
  artefacts; identity stays stable across scene changes when prompts stay specific
- **Production implication:** If you can stage or source a drive clip, Motion Control
  deserves priority over plain prompting for hard physical action.

---

### Kling 3.0 Motion Control / Seedance alternatives — Alici AI

- **Author / creator:** Not fully surfaced
- **Platform:** Comparison / tutorial blog — Alici AI
- **Date of source:** March–April 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Kling Motion Control; Seedance 2.0
- **Evidence type:** Side-by-side / practical tutorial
- **Evidence rating:** Medium
- **Raw outputs shown:** Yes on page (not fully parsed)
- **Prompts / settings disclosed:** Moderate
- **Failures shown:** Limited
- **Relevant shot types:** Dance; choreography; motion transfer; camera-led shots
- **Key claims:** Image anchors identity; video anchors body/hand/camera motion;
  video-orientation is better for complex motion; Seedance interprets dance references
  more loosely than Kling
- **Production implication:** For choreographed motion, prefer Kling if you can supply a
  usable motion clip.

---

### Seedance 2.0 Review: 500 Generation Test

- **Author / creator:** Not clearly disclosed
- **Platform:** Creator test / workflow blog
- **Date of source:** 7 April 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Seedance 2.0
- **Evidence type:** Large creator test
- **Evidence rating:** Medium-high
- **Raw outputs shown:** Not fully parsed
- **Prompts / settings disclosed:** Partial
- **Failures shown:** Yes
- **Relevant shot types:** UGC/dialogue; product image-to-video; long-form B-roll;
  multi-character scenes
- **Key claims:** Strong first-try success in single-character and product image-to-video;
  long-form B-roll weakens; negative cues work better than on Seedance 1.x; over-10-
  second clips lose coherence; concise prompts outperform rambling ones
- **Production implication:** Keep Seedance clips short; feed it strong references; use it
  as a precision short-clip engine rather than a long-take engine.

---

### Kling 3.0 review for creative pros — Chase Jarvis

- **Author / creator:** Chase Jarvis
- **Platform:** Creator review
- **Date of source:** 48-hour early review, February 2026
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:** Kling 3.0
- **Evidence type:** Practical creator review
- **Evidence rating:** Medium-high
- **Raw outputs shown:** Selected examples
- **Prompts / settings disclosed:** Partial
- **Failures shown:** Yes
- **Relevant shot types:** Product consistency; start/end transitions; design-heavy edits
- **Key claims:** Elements nailed a consistent product across cuts; realistic movement felt
  more weighted than older Kling; design-heavy / illustrative looks still lag; cost and
  latency remain meaningful
- **Production implication:** Kling deserves first-pass use on photoreal video and
  product-consistency shots, but not on graphic/UI-heavy work.

---

## Template for New Entries

```text
### [Source title] — [Author / organisation]

- **Author / creator:**
- **Platform:**
- **Date of source:**
- **Source URL:** TODO
- **Date accessed:** 2026-05-05
- **Models discussed:**
- **Evidence type:** official documentation | hands-on review | raw test | comparison | tutorial | user report
- **Evidence rating:** high | medium-high | medium | low
- **Raw outputs shown:** yes | no | partial
- **Prompts / settings disclosed:** yes | partial | no
- **Failures shown:** yes | no | limited
- **Relevant shot types:**
- **Key claims:**
- **Production implication:**
```
