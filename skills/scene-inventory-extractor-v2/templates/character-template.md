# Character Bible Templates

Templates for different character types in scene inventory extraction. Each template
now includes reference image specifications for the visual asset pipeline.

---

## Primary Character Template

Use for protagonists and major characters who drive the narrative.

```markdown
#### {Character Name} (primary)

* **Role in story:** {Function in narrative — what they do, not who they are}
* **Look (age band, silhouette, facial/energy notes):** {Filmable physical description: posture, energy, distinguishing features}
* **Wardrobe (period-anchored):**
  * {Primary outfit with specific details}
  * {Secondary outfit or accessories}
  * {Condition notes: worn, pristine, stained, etc.}
* **Behavioural tells:**
  * {Physical habit 1 — concrete, filmable action}
  * {Physical habit 2 — micro-expression or gesture}
  * {Habit 3 — how they interact with objects/space}
* **Inner conflict:** {What they want vs. what they do — stated as tension, not psychology}
* **Arc (start → pivot → end):**
  * Start: {Initial state — concrete, observable}
  * Pivot: {What changes — specific event or realization}
  * End: {Final state — observable change from start}
* **Voice notes (if audio is in scope):**
  * {Accent/dialect specifics}
  * {Speech patterns, rhythm, vocabulary}
  * {Emotional range notes}
* **Key props:**
  * {Objects physically associated with character}
* **Continuity state chain:**
  * Wardrobe continuity by scene: {Scene-by-scene outfit state}
  * Carried items by scene: {Phone, bag, folder, mug, cigarette, etc.}
  * Body-state continuity: {Mud, blood, wet hair, fatigue, tears, makeup damage}
  * Pocket / hand continuity risks: {Which hand, where stowed, when removed}

* **Reference image requirements:**
  * Primary: Full body, front-facing, neutral pose, white background — includes full wardrobe detail
  * Face detail: Head-and-shoulders, ¾ angle — captures facial features for consistency
  * Expression set: {List each expression the story demands: e.g. concern, anger, relief, exhaustion}
  * Wardrobe variants: {Each distinct outfit change in the story, described: e.g. "Work coveralls", "Evening wear at restaurant"}
  * Action poses: {Signature physical actions: e.g. "Typing at console", "Running", "Carrying prop X"}

* **Reference image generation notes:**
  * Primary prompt emphasis: {Key visual features that must be locked: e.g. "scar above left eye", "always slightly hunched posture", "calloused hands"}
  * Consistency anchors: {What to check in every generated image: e.g. "hair colour, nose shape, shoulder width"}
```

---

## Secondary/Functional Character Template

Use for supporting characters with specific narrative functions.

```markdown
#### {Character Name} (functional)

* **Role in story:** {Specific function: pressure, contrast, information delivery}
* **Look:** {Brief physical description — enough to cast/design}
* **Wardrobe:** {Key clothing items; period-appropriate}
* **Behavioural tells:** {1–2 defining habits or gestures}
* **Inner conflict:** {If relevant; often "Not foregrounded; function is {X}"}
* **Arc:** {Usually "Static" — they don't change}
* **Voice notes:** {If applicable; often technical notes like "radio compression"}
* **Key props:** {Objects they use or carry}
* **Continuity state chain:**
  * Wardrobe continuity by scene: {Only if it materially changes}
  * Carried items by scene: {What they enter, handle, and leave with}
  * Body-state continuity: {Visible condition shifts}
  * Pocket / hand continuity risks: {If on-camera}

* **Reference image requirements:**
  * Primary: Full body, front-facing, neutral pose, white background
  * Face detail: Head-and-shoulders, ¾ angle
  * {Additional only if the shot list demands specific framings not covered by primary + face}

* **Consistency anchors:** {2–3 key features to verify: e.g. "uniform colour, badge position, beard length"}
```

---

## Interface/Digital Presence Template

Use for characters existing primarily as UI elements, accounts, or digital presences.

```markdown
#### {Character/Account Name} (interface presence)

* **Role in story:** {Narrative function — catalyst, pressure, information source}
* **Look:** {UI appearance: colours, typography, avatar style, layout}
* **Wardrobe:** N/A
* **Behavioural tells:** {Communication patterns: frequency, tone, timing}
* **Inner conflict:** {Usually "Unknown; keep ambiguous"}
* **Arc:** {How their presence changes: ambient → direct, rare → frequent}
* **Voice notes:** {If ever vocalized; often "None — text only on screen"}
* **Key props:** {UI elements: notification badges, post formats, DM interfaces}

* **Reference image requirements:**
  * UI screenshot: Full-frame mockup of the interface as it appears in the story
  * Avatar detail: Close-up of avatar/icon if applicable
  * State variants: {If the UI changes across the story: e.g. "notification count escalating", "interface degraded"}

* **Consistency anchors:** {Font, colour scheme, avatar, layout grid}
```

---

## Voice-Only Character Template

Use for characters heard but not seen.

```markdown
#### {Character Name} (voice-only)

* **Role in story:** {Function — institutional voice, remote presence}
* **Look:** {If ever shown: brief description; often "Not shown"}
* **Wardrobe:** {If shown; often N/A}
* **Behavioural tells:** {Audio tells: eating while talking, distraction, compression}
* **Inner conflict:** {Usually minimal}
* **Arc:** {Usually "Static"}
* **Voice notes:** {Critical: accent, compression, background noise, emotional range}
* **Key props:** {Communication device: radio, phone, intercom}

* **Reference image requirements:** None (unless briefly shown; if so, primary only)
```

---

## Collective/Group Character Template

Use for groups functioning as a single narrative unit.

```markdown
#### {Group Name} ({number} people; {descriptor})

* **Role in story:** {Collective function — labour, opposition, chorus}
* **Look:** {Shared visual characteristics; individual variation notes}
* **Wardrobe:** {Uniform or shared clothing elements}
* **Behavioural tells:** {Shared behaviours; brief exchanges; group dynamics}
* **Inner conflict:** {Usually "Not foregrounded; they embody {X}"}
* **Arc:** {Usually "Static" as a group}
* **Voice notes:** {Shared speech patterns}
* **Key props:** {Shared tools or objects}
* **Continuity state chain:**
  * Wardrobe continuity by scene: {Uniform state or meaningful variation}
  * Carried items by scene: {Shared tools, bags, equipment}
  * Body-state continuity: {Weathering, dirt, injuries, fatigue markers}
  * Pocket / hand continuity risks: {Only if continuity-sensitive on camera}

* **Reference image requirements:**
  * Representative figure: Full body, front-facing, neutral pose, white background — shows the "type"
  * Variation figures (2–3): Showing diversity within the group (different builds, ages, etc.)
  * {Group shot only if the shot list requires the group as a composed unit}

* **Consistency anchors:** {Uniform details, shared equipment, build range}
```

---

## Character Extraction Checklist

| Check | Question |
|-------|----------|
| **Completeness** | All named characters captured? |
| **Unnamed presences** | Functional characters without names (e.g., "the supervisor")? |
| **Digital presences** | Accounts, interfaces, systems functioning as characters? |
| **Groups** | Collectives treated as single characters? |
| **Role clarity** | Each character's narrative function clearly stated? |
| **Filmable details** | Descriptions concrete and observable, not psychological? |
| **Props linkage** | Character-associated props listed? |
| **Continuity chain** | Wardrobe, carried items, body state, and hand/pocket risks tracked by scene? |
| **Arc verification** | Primary characters have clear start/pivot/end? |
| **Ref image specs** | Reference image requirements defined per character weight? |
| **Consistency anchors** | Key features to verify listed for each on-screen character? |

---

## Language Guidelines

**Operational language:**
- ✓ "Clears warnings on reflex"
- ✓ "Jaw tightens at bad news"
- ✗ "Feels frustrated by the system"
- ✗ "Experiences existential dread"

**Specific physicality:**
- ✓ "Mid-30s; tired posture; alert eyes"
- ✓ "Rubs eyes hard at threshold moments"
- ✗ "Looks tired"
- ✗ "Seems stressed"

**Function, not identity:**
- ✓ "Institutional boredom; pushes procedure"
- ✓ "Recruitment pressure; reframes her agency"
- ✗ "The villain"
- ✗ "A mysterious figure"
