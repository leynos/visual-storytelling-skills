# 🎬 visual-storytelling-skills

*Agent skills for AI film production — from prose to picture.*

Every story contains a film. These skills find it. This is a collection
of Claude Code skills that walk a narrative from raw prose through
continuity extraction, reference-image generation, shot direction, and
model-routed video-prompt assembly, with a TTS phoneticiser for good
measure.

______________________________________________________________________

## Why visual-storytelling-skills?

AI video generation is powerful but fussy. Models want precise prompts,
carefully curated references, continuity-checked assets, and shot
direction that could actually be handed to a camera operator. Doing that
by hand for every shot in a feature is a recipe for RSI and despair.

These skills automate the production-prep pipeline:

- **Continuity first**: extract character, location, and prop state
  *before* a single prompt is written, so scenes shot out of order
  stay coherent.
- **Reference-led generation**: build a complete image asset library
  before touching a video model.
- **Model-aware routing**: route shots between Seedance 2.0, Kling 3.0,
  and whatever arrived last Tuesday based on shot type, reference
  availability, and budget.
- **Narration-ready output**: phoneticise proper nouns, brand names, and
  contested acronyms so your TTS engine does not mangle "Siobhán" or
  "df12".

______________________________________________________________________

## Quick start

### Installation

```bash
git clone https://github.com/df12-productions/visual-storytelling-skills
```

### Typical production run

Start with a script or prose fragment. The scene-inventory-extractor
parses it, extracts characters, locations, and props, and generates your
full reference-image library:

```
/scene-inventory-extractor-v2
```

Hand the resulting inventory to the shot-specifier, which decomposes
every scene into numbered shots with full directorial direction,
storyboard keyframes, and generation-ready video prompts:

```
/shot-specifier
```

When the narration script is ready, phoneticise it before sending it to
Eleven v3:

```
/phoneticize
```

Image-generation tasks throughout the pipeline are handled by the
nanobanana skill, which the other skills call automatically. You can also
invoke it directly for standalone image work:

```
/nanobanana
```

______________________________________________________________________

## Skills

| Skill | What it does |
|-------|--------------|
| `scene-inventory-extractor-v2` | Reads a script or prose fragment; extracts characters, locations, props, and story state; generates the full reference-image library; produces a continuity inventory for reset-critical scenes. |
| `shot-specifier` | Takes a scene inventory and produces numbered shot specs: actor position and movement, camera mount and motion, lens, lighting, effects, timing, storyboard keyframes, video prompts, and model routing. |
| `nanobanana` | Crafts structured prompts for the Nano Banana image MCP — generation, editing, character consistency, and multi-image fusion. |
| `phoneticize` | Detects pronunciation hazards in TTS scripts; suggests phonetic respellings; previews via Eleven v3 fragments; emits a phoneticised script and an archived pronunciation table. |

______________________________________________________________________

## Learn more

- [AGENTS.md](AGENTS.md) — agent workflow guidelines and conventions
- `skills/*/SKILL.md` — full workflow documentation for each skill
- `skills/*/references/` — supporting reference documents loaded
  automatically at the relevant phase of each workflow
- `notes/` — research logs, model-routing evidence, and open questions

______________________________________________________________________

## Licence

ISC — see [LICENSE](LICENSE) for details.

______________________________________________________________________

## Contributing

Contributions welcome. See [AGENTS.md](AGENTS.md) for conventions and
workflow guidelines.
