# Continuity Inventory

Read this before Phase 8. Continuity extraction happens before image generation and
before shot prompts. Treat it as a first-class deliverable, not downstream QA.

## Purpose

Assume scenes will be shot out of order. Extract continuity so a separate crew, working
days later, can restore the exact character, prop, and dressing state without
re-reading the source material.

Continuity extraction is distinct from consistency verification:

- continuity extraction = pre-generation story-state and physical-state tracking
- consistency verification = post-generation image QA

## Hard Rule

Track all objects a character touches, carries, wears, consumes, sets down, pockets,
opens, closes, damages, dirties, lights, reads from, writes with, or moves - including
mundane items such as mugs, pens, paper stacks, phones, cigarettes, keys, bags,
utensils, desk clutter, blankets, folders, and receipts.

If an object could change position, state, fullness, cleanliness, damage, or ownership
between shots or scenes, log it.

## Deliverable

Write a separate file:

`{project_name}_continuity_inventory.md`

This file sits beside `{project_name}_scene_inventory.md` as a core prep deliverable.

## Required Structure

### 1. Scene-by-Scene Continuity Table

Create one entry per scene:

```markdown
#### SC-{XX}

* **Location baseline:** {what must already be true when the crew arrives}
* **Fixed location anchors:** {architecture, furniture, installed fixtures}
* **Movable dressing:** {objects that can drift position}
* **Character-carried items:** {per character}
* **Consumables / depletion:** {food, drink, cigarettes, fuel, paperwork stacks}
* **Weather / dirt / damage state:** {mud, rain, soot, sweat, blood, wrinkles}
* **Object positions:** {desk left/right, chair angle, window status, door status}
* **Hand / pocket risks:** {which hand, where stowed, when removed}
* **Scene exit state:** {what leaves, what stays, what is destroyed}
* **Coverage reset notes:** {details that must match across angles within the same scene}
* **Return-visit notes:** {details that must match when the location is revisited later}
```

### 2. Recurring Location Continuity Chains

For every recurring location, record:

- first appearance state
- subsequent appearance changes
- non-negotiable anchors
- reversible vs irreversible changes

### 3. Character Continuity State Chains

For every recurring on-screen character, record by scene:

- wardrobe continuity
- carried items
- body-state continuity
- pocket / hand continuity risks
- glasses / hats / outerwear on-off transitions

### 4. Prop Custody and State Chains

For each continuity-relevant prop, record:

- custody: who has it when
- state progression: clean to dirty, full to empty, folded to opened, intact to broken
- set-down / pickup moments
- scene exit status

## Continuity Checklist

| Check | Question |
|-------|----------|
| Mundane props | Have all touched or handled objects been logged? |
| Carry chain | Is it clear who carries each item into and out of the scene? |
| State chain | Are fullness, damage, dirt, wetness, and depletion tracked? |
| Repeated locations | Do recurring spaces have baseline and changed states recorded? |
| Repeated characters | Are wardrobe, carried items, and body-state changes tracked by scene? |
| Coverage resets | Could a crew reset this scene correctly between angles using this document alone? |
| Return visits | Could the set be re-dressed correctly if revisited days later in the schedule? |
