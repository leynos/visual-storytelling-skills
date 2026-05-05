# 🎬 visual-storytelling-skills

*Agent skills for AI film production — from prose to picture.*

Every story contains a film. These skills find it. This is a collection
of Claude Code skills that walk a narrative from raw prose through
continuity extraction, reference-image generation, shot direction, and
model-routed video-prompt assembly, with a TTS phoneticizer for good
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
- **Narration-ready output**: phoneticize proper nouns, brand names, and
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

```text
/scene-inventory-extractor-v2
```

Hand the resulting inventory to the shot-specifier, which decomposes
every scene into numbered shots with full directorial direction,
storyboard keyframes, and generation-ready video prompts:

```text
/shot-specifier
```

When the prompt manifest and storyboard frames are ready, use the
video-generator to submit clips through the Higgsfield MCP, poll jobs,
download takes, resume interrupted runs, and write assembly order:

```text
/video-generator
```

When the narration script is ready, phoneticize it before sending it to
Eleven v3:

```text
/phoneticize
```

Image-generation tasks throughout the pipeline are handled by the
nanobanana skill, which the other skills call automatically. You can also
invoke it directly for standalone image work:

```text
/nanobanana
```

______________________________________________________________________

## Skills

| Skill | What it does |
|-------|--------------|
| `scene-inventory-extractor-v2` | Reads a script or prose fragment; extracts characters, locations, props, and story state; generates the full reference-image library; produces a continuity inventory for reset-critical scenes. |
| `shot-specifier` | Takes a scene inventory and produces numbered shot specs: actor position and movement, camera mount and motion, lens, lighting, effects, timing, storyboard keyframes, video prompts, and model routing. |
| `video-generator` | Takes the prompt manifest and storyboard frames from the upstream skills; uses the Higgsfield MCP to prepare media, call video generation, poll jobs, download takes, resume interrupted runs, and write assembly order. |
| `nanobanana` | Crafts structured prompts for the Nano Banana image MCP — generation, editing, character consistency, and multi-image fusion. |
| `phoneticize` | Detects pronunciation hazards in TTS scripts; suggests phonetic respellings; previews via Eleven v3 fragments; emits a phoneticized script and an archived pronunciation table. |

Image-generation skills must use the nanobanana MCP with
`model: gemini-3-pro-image-preview`. If that model is unavailable or cannot accept the
required reference or character-consistency images, the workflow stops instead of
falling back to another image model.

______________________________________________________________________

## Learn more

- [Users' guide](docs/users-guide.md) — workflow diagrams and
  architecture overview
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
