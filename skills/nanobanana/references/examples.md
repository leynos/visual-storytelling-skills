# Nano Banana Prompt Patterns and Examples

Use these as short starting points. Expand only the parts the user actually cares about.

## Table of Contents

- Brand and layout systems
- Product and e-commerce
- Portraits and character consistency
- Technical diagrams and infographics
- Architecture and spatial logic
- Storyboards and cinematic sequences
- Editing patterns

## Brand and Layout Systems

### Brand board or cover

```text
Create a brand identity cover for [brand].
Aspect ratio: [ratio].
Header: "[exact text]" at the top.
Footer: logo lockup anchored in the lower right.
Visual language: [shapes, motif, color system].
Mood: futuristic, clean, expressive.
Lighting/finish: matte surfaces with soft neon edge glow.
```

### Dense information poster

```text
Create a high-clarity infographic poster about [topic].
Use a strong top header, 4-7 clearly separated sections, a central illustration, and a dense but readable footer note area.
Mix typographic character intentionally: bold condensed titles, clean serif body, technical mono for labels.
Keep spacing consistent and preserve hierarchy.
```

## Product and E-commerce

### Premium product shot

```text
[Product] on [surface], [camera angle], [lighting], premium commercial photography.
Show precise material detail: [glass, brushed aluminum, matte ceramic, embossed paper].
Use clean negative space and a natural contact shadow.
```

### Product with exact text

```text
Create a clean packaging mockup for [product].
The label includes the exact text "[TEXT]".
Place the product on a neutral studio background with soft side lighting.
Keep typography sharp and centered.
```

## Portraits and Character Consistency

### Professional headshot

```text
Keep the person's facial identity exactly consistent with the reference image.
Dress them in [wardrobe].
Place them against [background].
Shot on an 85mm lens with soft three-point studio lighting, chest-up framing, natural skin texture, subtle catchlights, professional editorial finish.
```

### Character in a new scene

```text
Use Image A for identity with 100% facial consistency.
Place the same character in [new setting], wearing [wardrobe], [shot type], [lighting], [style].
Do not change face shape, skin tone, or core expression.
```

## Technical Diagrams and Infographics

### Technical object breakdown

```text
Create a high-resolution technical breakdown of [object].
Show the full object in dynamic perspective.
Add clean white callout lines, labels, diagram boxes, and a top title reading "[TITLE]".
Use a crisp engineering aesthetic with readable annotation hierarchy.
```

### Educational infographic

```text
Create an educational infographic explaining [topic].
Include labeled components, arrows showing relationships, and a clean textbook-friendly vector style.
Use clear English labels and uncluttered spacing.
```

## Architecture and Spatial Logic

### Floor plan prompt

```text
Create a one-floor architectural plan.
Overall footprint: [dimensions and shape].
Include exactly [room count] rooms with stated dimensions and adjacency rules.
Render as a clean plan diagram with door swings, window placements, and readable room labels.
```

### Layout with numeric constraints

```text
Show exactly [N] subjects arranged as [rows / arc / grid].
Use [specific count] in the front, [specific count] in the middle, and [specific count] in the back.
Each subject must hold or display a unique [qualified item].
```

## Storyboards and Cinematic Sequences

### Contact sheet / storyboard grid

```text
Create a cinematic contact sheet showing [N] keyframes in a single grid.
Maintain strict continuity in subject, wardrobe, environment, and color grade.
Vary only framing, action, and camera movement.
Label each panel with a short keyframe tag in the safe margin.
```

### Single keyframe prompt

```text
[Subject] in [environment], [shot type], [lens], [camera movement feel], [lighting], [grade].
Keep continuity with previous frame: same wardrobe, same location, same time of day.
```

## Editing Patterns

### Background replacement

```text
Preserve subject identity, pose, wardrobe, and lighting direction.
Replace only the background with [new background].
Match perspective and edge lighting exactly.
```

### Local object addition

```text
Preserve the whole image.
Add [object] only in the empty area [location].
Match existing scale, light direction, and shadow softness.
```

### Style transfer with content lock

```text
Keep the exact composition and subject arrangement from the source image.
Re-render it in [target style].
Preserve all major spatial relationships and object counts.
```

## Notes

- Start with the shortest prompt that can still encode the real constraints.
- For local MCP usage, pair the prompt with explicit `model`, `aspectRatio`, and `output_path`.
- Prefer safe, reusable templates over copying long source prompts verbatim.
