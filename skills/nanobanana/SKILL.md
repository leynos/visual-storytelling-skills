---
name: nanobanana
description: "Craft high-precision prompts and edit instructions for Nano Banana image workflows, especially when using the local nanobanana MCP tools for generation, editing, character consistency, or multi-image fusion. Use when the task needs structured prompts, reference-role assignment, layout-heavy image specs, typography-heavy images, iterative edit-first refinement, or reliable model/aspect/output-path choices."
---

# Nanobanana

Use this skill to turn a vague image request into a prompt that Nano Banana can execute reliably, or to refine an existing image/edit request without restarting from scratch.

## Workflow

1. Identify the operation first.

- `generate`: create a new image from text and optional references.
- `edit`: modify an existing image while preserving specified elements.
- `character_consistency`: keep one character stable across scenes.
- `multi_image_fusion`: combine several references into one coherent result.

2. Choose the lowest-complexity prompt shape that fits the ask.

- Use a short natural-language prompt for simple scenes.
- Use a structured block for multi-part layouts, infographics, or scene logic.
- Use JSON-like structure when the user needs many simultaneous constraints or multiple reference roles.

3. Build the prompt in this order.

- Subject: who or what must appear.
- Action/state: what is happening.
- Setting: where it is happening.
- Composition: framing, camera angle, spatial layout.
- Lighting/mood: time of day, light direction, contrast, atmosphere.
- Style/materiality: photoreal, editorial, infographic, matte acrylic, film grain, etc.
- Constraint layer: exact text, counts, positions, identity preservation, what must remain unchanged.

4. Prefer positive, explicit constraints.

- Say what should be present and how it should behave.
- For edits, explicitly state what must remain unchanged.
- For text rendering, quote exact text and specify placement plus typographic character.

5. Use edit-first iteration.

- If the first output is close, preserve the successful parts and request only the delta.
- Example: `Keep composition, subject identity, and wardrobe identical; shift lighting to golden hour and replace background with a foggy bridge.`

## Local MCP Rules

- `mcp__nanobanana__generate_image` is for new images.
- `mcp__nanobanana__edit_image` is for targeted changes to an existing image.
- `mcp__nanobanana__character_consistency` is for repeated scenes with one character reference.
- `mcp__nanobanana__multi_image_fusion` is for combining several references.
- `output_path` must stay inside the tool's allowed repo-local output area. In practice, use a simple filename or relative path; do not pass an absolute path outside `image_out`.

## Model Selection

- Use `gemini-3-pro-image-preview` for the highest-fidelity structured prompting, typography, technical diagrams, and dense layout work.
- Use `gemini-3.1-flash-image-preview` when speed matters or when extra-wide ratios like `4:1`, `1:4`, `8:1`, or `1:8` are required.
- Use `gemini-2.5-flash-image` for fast, simpler iterations when top-end fidelity is not necessary.

## Prompting Patterns

- For simple generation, use the formula in [references/frameworks.md](./references/frameworks.md).
- For structured scene blueprints, multi-reference prompts, and edit instructions, use [references/frameworks.md](./references/frameworks.md).
- For reusable prompt skeletons across posters, product shots, infographics, floor plans, storyboards, and character scenes, use [references/examples.md](./references/examples.md).

## Guardrails

- Do not overstuff the prompt with decorative synonyms when concrete constraints will do.
- For exact counts, rows, layouts, labels, or room sizes, state them numerically and spatially.
- For reference images, assign each image a job such as identity, pose, style, lighting, or environment.
- For text-heavy images, keep each required text string short unless the user explicitly needs a dense poster or infographic.
- When an example from the source material is unsafe, irrelevant, or too verbose for direct reuse, extract the pattern and rewrite it into a safe, shorter template rather than copying it.

## Deliverable Style

- If the user asks for an image, provide a prompt plus suggested model, aspect ratio, and any reference-role mapping.
- If the user asks for an edit, provide the preservation constraints first, then the requested changes.
- If the user asks for multiple options, vary composition and lighting before varying everything else.
