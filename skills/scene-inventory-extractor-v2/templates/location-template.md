# Location Bible Template

Templates for location entries with multi-angle, multi-condition scouting specifications.

---

## Physical Space Template

Use for real-world environments (buildings, streets, landscapes, interiors).

```markdown
#### {Location Name} ({brief descriptor})

* **Look (materials, architecture, atmosphere):** {Detailed physical description — what defines this space visually}
* **Sound (beds + punctuations):**
  * Bed: {Continuous ambient sound}
  * Punctuations: {Discrete sounds marking moments}
* **Continuity constraints:**
  * Must: {Required elements that define this location}
  * Must not: {Prohibited elements — anachronisms, brands, etc.}
* **Signature motif:** {Visual or audio element that instantly identifies this space}
* **Continuity chain across appearances:**
  * First appearance state: {Baseline dressing and condition}
  * Subsequent appearance changes: {What changes, what persists, why}
  * Non-negotiable anchors: {Elements that must never drift}

* **Scouting specification:**

  * **Required angles:**
    * Establishing wide: {Camera position, e.g. "From entrance doorway, looking in"}
    * Working angle: {Primary shooting position for dialogue/action}
    * Character-entry POV: {What a character sees when entering}
    * Signature detail: {Insert shot of defining detail}
    * {Additional angles as shot list demands}

  * **Required lighting conditions:**
    * {Condition 1}: {Description — e.g. "Day, fluorescent overhead, grey window light"}
    * {Condition 2}: {Description — e.g. "Night, monitors only, blue-cast"}
    * {Condition 3}: {If applicable}

  * **Required weather conditions:** {If exterior or weather-visible}
    * {Condition 1}: {e.g. "Clear sky, harsh shadows"}
    * {Condition 2}: {e.g. "Heavy rain, diffused light, wet surfaces"}

  * **Narrative state variants:** {If the location changes during the story}
    * {State 1}: {Normal / undamaged / pre-event}
    * {State 2}: {Description of change — e.g. "Post-incident: broken monitors, scattered paper, emergency lighting"}

* **Scouting matrix:**

  | Ref ID | Angle | Lighting | Weather | Narrative State | Scene(s) Using |
  |--------|-------|----------|---------|-----------------|----------------|
  | LOC-{name}-01 | Establishing wide | Day | Clear | Normal | SC-01, SC-03 |
  | LOC-{name}-02 | Establishing wide | Night | N/A | Normal | SC-07 |
  | LOC-{name}-03 | Working angle | Day | Clear | Normal | SC-01, SC-02 |
  | LOC-{name}-04 | Working angle | Night | N/A | Post-incident | SC-08 |
  | LOC-{name}-05 | Detail insert | Day | Clear | Normal | SC-02 |

  _{Only include combinations the shot list actually visits.}_

* **Reference image generation notes:**
  * Primary reference (LOC-{name}-01): {Full style spec required; most common condition}
  * Variant generation: {What to emphasise in condition-change prompts}
  * Anchor statement: "Same room/space as reference; architecture, materials, proportions identical. Only {X} has changed."
  * Consistency anchors: {Key structural elements to verify: e.g. "window position, desk layout, ceiling height, door placement"}
```

---

## Vehicle Interior Template

Use for mobile spaces (cars, trains, ships, aircraft, spacecraft).

```markdown
#### {Vehicle Name} ({type})

* **Look:** {Interior materials, dashboard, seats, window view, wear}
* **Sound:**
  * Bed: {Engine, road noise, climate control}
  * Punctuations: {Indicators, alerts, phone, radio}
* **Continuity constraints:**
  * Must: {Dashboard layout, seat configuration, window visibility}
  * Must not: {Modern UI elements if period piece; wrong-hand drive; etc.}
* **Signature motif:** {Defining element — e.g. "cracked windscreen", "dangling air freshener"}
* **Continuity chain across appearances:**
  * First appearance state: {Baseline dashboard, seats, carried clutter}
  * Subsequent appearance changes: {Fuel, weathering, damage, loose objects}
  * Non-negotiable anchors: {Layout details that must never drift}

* **Scouting specification:**

  * **Required angles:**
    * Dashboard POV: {Looking out through windscreen}
    * Driver CU: {From passenger-side, OTS or profile}
    * Rear-view / mirror: {If narratively significant}
    * Exterior establishing: {If the vehicle is seen from outside}

  * **Required conditions:**
    * {Condition 1}: {e.g. "Moving, daytime, city traffic"}
    * {Condition 2}: {e.g. "Parked, night, rain on windscreen"}
    * {Condition 3}: {If applicable}

* **Scouting matrix:**

  | Ref ID | Angle | Condition | Scene(s) Using |
  |--------|-------|-----------|----------------|
  | VEH-{name}-01 | Dashboard POV | Moving, day | SC-01 |
  | VEH-{name}-02 | Driver CU | Parked, night, rain | SC-04 |

* **Consistency anchors:** {Dashboard layout, steering wheel position, seat material, window frame shape}
```

---

## Digital Space Template

Use for UI environments, feeds, interfaces, virtual spaces.

```markdown
#### {Digital Space Name} ({type — app, dashboard, feed, OS desktop, etc.})

* **Look:** {Colour scheme, typography, layout grid, UI density}
* **Sound:**
  * Bed: {Fan hum, digital silence, ambient office if diegetic}
  * Punctuations: {Notification sounds, clicks, error tones}
* **Continuity constraints:**
  * Must: {UI framework, colour scheme, font, grid}
  * Must not: {Real platform logos; recognisable OS chrome unless intentional}
* **Signature motif:** {Defining UI element — e.g. "pulsing notification badge", "loading spinner"}
* **Continuity chain across appearances:**
  * First appearance state: {Baseline layout and counts}
  * Subsequent appearance changes: {Unread counts, errors, popups, escalations}
  * Non-negotiable anchors: {Grid, font, icon family, accent colour}

* **Scouting specification:**

  * **Required views:**
    * Full-screen: {Complete interface as user sees it}
    * Detail inserts: {Specific UI elements the camera focuses on}
    * State variants: {If the interface changes: notifications accumulating, error states, etc.}

* **Scouting matrix:**

  | Ref ID | View | State | Scene(s) Using |
  |--------|------|-------|----------------|
  | DIG-{name}-01 | Full-screen | Normal | SC-02 |
  | DIG-{name}-02 | Notification detail | Escalated | SC-06 |

* **Consistency anchors:** {Layout grid, font family, accent colour, icon set}
```

---

## Stylised / Insert Space Template

Use for abstract, symbolic, or heavily stylised locations.

```markdown
#### {Space Name} ({descriptor — e.g. "dream sequence", "title card environment"})

* **Look:** {Visual rules — what makes this space distinct from reality}
* **Sound:** {If applicable; often silence or processed/abstract audio}
* **Continuity constraints:**
  * Must: {Defining visual rules}
  * Must not: {Elements that break the stylisation}
* **Signature motif:** {Core visual or audio element}
* **Continuity chain across appearances:**
  * First appearance state: {Baseline stylisation}
  * Subsequent appearance changes: {What transforms and what does not}
  * Non-negotiable anchors: {Rules that must never drift}

* **Scouting specification:**

  * **Required views:**
    * Primary: {The establishing view of this stylised space}
    * Variants: {If the space evolves or shifts}

* **Scouting matrix:**

  | Ref ID | View | State | Scene(s) Using |
  |--------|------|-------|----------------|
  | STY-{name}-01 | Primary | Initial | SC-{XX} |

* **Consistency anchors:** {Core visual rules that must not drift}
```

---

## Location Extraction Checklist

| Check | Question |
|-------|----------|
| **Completeness** | All locations in the source captured? |
| **Categorisation** | Each location assigned to correct type (physical / vehicle / digital / stylised)? |
| **Look described** | Materials, architecture, atmosphere filmable? |
| **Sound specified** | Both beds and punctuations noted? |
| **Constraints stated** | Must and must-not elements listed? |
| **Motif identified** | Signature element named? |
| **Continuity chain** | First state, later changes, and non-negotiable anchors recorded for repeated spaces? |
| **Angles enumerated** | Every camera position the shot list needs? |
| **Conditions enumerated** | Every lighting/weather/state the scene inventory requires? |
| **Matrix populated** | Only story-visited combinations included? |
| **Scene mapping** | Each matrix entry linked to the scene(s) that use it? |
| **Consistency anchors** | Key structural elements to verify listed? |
| **No speculative entries** | Matrix does not include combinations the story never visits? |
