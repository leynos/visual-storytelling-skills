# Nano Banana Frameworks

Use these compact frameworks to choose the right prompt shape without loading a giant prompt bank.

## 1. Simple Generation

Use for one-subject or one-scene requests.

Formula:

`[Subject] + [Action/state] in [Setting], [Composition], [Lighting/mood], [Style/quality]`

Example:

`A tuxedo cat perched on a New York fire escape at dusk, medium-wide shot from street level, warm storefront spill light with cool evening sky, cinematic photoreal editorial style.`

## 2. Structured Blueprint Prompt

Use for posters, covers, dashboards, brand boards, magazine layouts, and infographics.

Structure:

- Goal
- Canvas/anchors
- Main subject blocks
- Typography blocks
- Color/material system
- Lighting/rendering
- Constraints

Template:

```text
Create [artifact type].

Canvas:
- Aspect ratio: [ratio]
- Layout anchors: [top / center / footer / left column / right column]

Subject blocks:
- [Block name]: [content, placement, scale]

Typography:
- Headline text: "[exact text]"
- Placement: [where]
- Typographic character: [bold condensed / elegant serif / technical mono]

Visual system:
- Palette: [colors]
- Materials/textures: [paper, acrylic, matte ceramic, grain, etc.]

Lighting/rendering:
- [lighting and finish]

Constraints:
- Keep [specific element] fixed
- Leave [region] clean
- Preserve readability and spacing
```

## 3. JSON-Like Constraint Prompt

Use when the request has many simultaneous rules, multiple references, or precise logic.

Guidance:

- Use plain English keys.
- Keep keys semantic, not technical.
- Group by subject, environment, camera, layout, and constraints.

Template:

```json
{
  "goal": "Create ...",
  "references": {
    "image_a": "identity",
    "image_b": "pose",
    "image_c": "lighting and palette"
  },
  "subject": {
    "identity_rule": "preserve facial structure exactly",
    "wardrobe": "..."
  },
  "environment": {
    "setting": "...",
    "details": ["...", "..."]
  },
  "camera": {
    "framing": "...",
    "lens": "...",
    "angle": "..."
  },
  "constraints": [
    "Keep text readable",
    "Do not alter subject identity",
    "Use empty name plates for later editing"
  ]
}
```

## 4. Edit-First Prompt

Use for `edit_image` or conversational refinement after a near-hit.

Template:

```text
Preserve: [identity / pose / wardrobe / composition / lighting direction / background elements].
Change only: [targeted change].
Match existing: [perspective / shadows / color temperature / texture].
Do not alter: [critical locked elements].
```

Example:

`Preserve subject identity, outfit, pose, and camera framing. Change only the background to a minimalist concrete studio wall. Match existing shadow direction and lens perspective. Do not alter skin tone, facial expression, or hand position.`

## 5. Reference Role Assignment

Use this pattern when several images are provided.

- `Image A`: identity or character
- `Image B`: pose or gesture
- `Image C`: wardrobe/material details
- `Image D`: environment/background
- `Image E`: lighting/color grade

Prompt pattern:

`Use Image A for facial identity, Image B for pose, and Image C for wardrobe materials. Place the subject in the environment style of Image D with the lighting palette of Image E.`

## 6. Text Rendering Pattern

Use when text must appear inside the image.

- Put exact text in quotes.
- State placement clearly.
- State typographic character, not just "nice font".
- Keep text short unless dense poster output is required.

Template:

```text
The image includes the exact text "[TEXT]".
Place it [location].
Render it in [font character].
Keep spacing, alignment, and readability clean.
```

## 7. Logic and Enumeration Pattern

Use for counts, rows, diagrams, or spatial logic.

- State exact count.
- State arrangement.
- State relational constraints.
- State what qualifies each item.

Template:

```text
Show exactly [N] items arranged as [layout].
Each item must satisfy [rule].
Keep [row / cluster / center] balanced and clearly separated.
```

## 8. Tool-to-Task Mapping

- `generate_image`: blank-canvas creation, posters, product shots, diagrams.
- `edit_image`: local object swaps, background replacement, text changes, cleanup.
- `character_consistency`: same character across scenes or storyboard frames.
- `multi_image_fusion`: merge identity, product, pose, or style references.
