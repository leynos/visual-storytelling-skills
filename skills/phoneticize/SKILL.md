---
name: phoneticize
description: >
  Build pronunciation tables, generate TTS preview samples, and produce
  phoneticized scripts ready for narration. Use whenever a script is
  intended for text-to-speech rendering and the user wants to catch
  words the engine will mispronounce — proper nouns, Gaelic and Welsh
  names, brand names with idiosyncratic pronunciation (df12, Nginx),
  model names with embedded numerics (Atari 2600, ESP32), terms of art
  and acronyms (SaaS, OAuth, JWT), and document specifiers (ADR-0012,
  RFC 2119). Trigger on phrases like "phoneticize this script",
  "phonetecize this", "phonetize", "prep this for TTS", "build a
  pronunciation table", or any task involving text-to-speech narration
  where pronunciation consistency matters across takes. Drives a phased
  workflow: detect candidates, suggest phonetic respellings, render
  preview samples via the Higgsfield MCP TTS tool with Eleven v3,
  iterate with the user, and emit a final phoneticized script.
---

# Phoneticize — TTS pronunciation prep

A workflow for identifying pronunciation hazards in a TTS script,
agreeing phonetic renderings with the user via audio previews, and
emitting a phoneticized script ready for narration.

## Read first

| Reference | When to read | Path |
|---|---|---|
| Detection heuristics | Before Phase 1 — patterns that find candidates and how to combine them | `references/detection-heuristics.md` |
| Respelling conventions | Before Phase 2 — how to write phonetic respellings that Eleven v3 actually obeys | `references/respelling-conventions.md` |
| Eleven v3 format notes | Before Phase 3 and Phase 5 — what the engine accepts and silently ignores | `references/eleven-v3-notes.md` |

## Governing principles

1. **Preview the fragment, not the word.** TTS prosody depends on
   surrounding context. A respelling that sounds right in isolation
   collapses inside a sentence. Render fragments throughout.

2. **Respelling is the primary output, not SSML.** Eleven v3 silently
   drops `<phoneme>` tags (see `references/eleven-v3-notes.md`). Inline
   respelling — `Siobhán` → `shi-VAWN` directly in the prose — is what
   actually changes the model's output. IPA goes in the table for
   archival precision; respelling goes in the script.

3. **Mark uncertainty, never guess.** A wrong respelling shipped with
   confidence is worse than an explicit `?` the user resolves. When the
   pronunciation isn't obvious, ask.

4. **Stable IDs across iterations.** Each candidate gets a row ID
   (`P01`, `P02`, …) on first pass and keeps it for the lifetime of the
   table. The user references rows by ID; regenerate only the rows
   that changed.

5. **Render once, accept once.** Never re-render an `accepted` row —
   it wastes Higgsfield calls and the user will assume something
   broke when the audio differs subtly between takes.

## Phase 1 — Scan

Combine the regex helper with semantic reading. Neither alone catches
everything: regex misses ordinary-looking words with non-obvious
pronunciation (Worcester, Featherstonehaugh), and an LLM scan alone
will miss tokens deep in long scripts.

### Run the helper

```bash
python scripts/extract_candidates.py path/to/script.txt --out candidates.json
```

The helper applies the patterns documented in
`references/detection-heuristics.md` and emits a JSON list of
deduplicated candidates with category guesses, positions, and context
fragments.

### Add and prune

Read the script. For every candidate the helper found:

- **Confirm the category** — the helper guesses from token shape and
  occasionally gets it wrong (a CamelCase brand name miscategorised
  as ART, etc.)
- **Drop false positives** — title-case words at sentence-initial
  positions that aren't actually proper nouns, common acronyms the
  user clearly already pronounces a particular way

For everything the helper missed:

- English place names with silent letters (Worcester, Cholmondeley,
  Featherstonehaugh)
- Loanwords with retained pronunciation (lingerie, pho, façade)
- Programmer jargon with contested pronunciation (Nginx, kubectl,
  YAML, GIF)
- Multi-token model names — the helper catches `Atari` and `2600`
  separately; merge them by hand into a single candidate `Atari 2600`

### Capture per candidate

For each entry, the table needs:

- **Token**: surface form as it appears (preserve case)
- **Lemma**: canonical form for deduping (`Siobhán's` → `Siobhán`)
- **Category**: `NAM` / `CEL` / `BRA` / `MOD` / `ART` / `DOC` / `OTH`
- **Positions**: every offset where the lemma occurs in the script
- **Original fragment**: 5–6 word snippet around the first occurrence,
  snapped to clause boundaries where possible

## Phase 2 — Suggest respellings

Build the pronunciation table in this exact column order:

| Col | Meaning |
|---|---|
| `ID` | Stable identifier — `P01`, `P02`, … |
| `Token` | The token as it appears in the script |
| `Cat` | NAM / CEL / BRA / MOD / ART / DOC / OTH |
| `Original fragment` | 5–6 word snippet, original spelling |
| `Respelling` | Editable phonetic respelling — see conventions |
| `IPA` | Archive form (optional; fill where confident) |
| `Phoneticized fragment` | Same fragment with the respelling substituted in situ |
| `Sample` | Path to rendered audio (filled in Phase 3) |
| `Status` | `pending` / `accepted` / `revised` |

Respelling rules (full detail in `references/respelling-conventions.md`):

- **Hyphens between syllables**: `shi-VAWN`, never `shivawn`
- **Capitals mark stress**: `shi-VAWN` (stress on second), `LLAN-fair`
  (stress on first)
- **English orthographic conventions, not IPA**: `oo` for /uː/, `ay`
  for /eɪ/, `aw` for /ɔː/. The model reads letters, not symbols.
- **Disambiguate hard consonants**: `kat` not `cat` if the model is
  reading the c soft; `gohl` not `goal` if the g is going wrong
- **Acronyms — letter or word**: decide and commit. `S-Q-L` (letters)
  or `SEE-kwul` (word) — both are valid; pick one and tell the user.
- **Numerics — write them out**: `Atari 2600` →
  `Atari twenty-six hundred`; `ADR-0012` → `A-D-R twelve`. Lose
  leading zeros when speaking.

Mark uncertain rows `?` in the Respelling column. Don't fabricate.

## Phase 3 — Render samples

### Find the tool

If you have not already located the Higgsfield TTS tool, search:

```
tool_search keywords=["tts", "speech", "higgsfield", "eleven"]
```

If nothing matches, surface the gap to the user via
`suggest_connectors` and pause until the connection is in place.

### Render fragments, not words

For each row with status `pending`:

1. Take the **phoneticized fragment** (not the isolated word — context
   matters for prosody and you need to hear the syllable boundaries
   land in surrounding speech)
2. Call the TTS tool with the fragment, requesting `eleven_v3` (or
   whatever string the tool exposes for the v3 model)
3. Save the audio to `samples/<ID>_<lemma_slug>.mp3` —
   e.g. `samples/P01_siobhan.mp3`
4. Fill the `Sample` column with the relative path

Render in sequence, not in parallel. Higgsfield rate limits, and
sequential rendering gives the user deterministic ordering for review.

### Present and pause

Present the table with samples linked. Tell the user the response
shape you expect (acceptance, revision, rejection, addition — see
Phase 4). Then wait. Do not proceed to Phase 5 without explicit
sign-off.

## Phase 4 — Iterate

The user's response will mix four kinds of update:

| Form | Example | Action |
|---|---|---|
| **Acceptance** | "P01, P03, P04 are good" | Mark those rows `accepted`. |
| **Revision** | "P02 should be 'dee-eff-TWELVE' not 'DEE-eff-twelve'" | Update Respelling and Phoneticized fragment, mark `revised`, queue for re-render. |
| **Rejection** | "drop P05, that pronunciation's fine as-is" | Remove the row entirely; the substitution won't happen in Phase 5. |
| **Addition** | "you missed 'Llanelli' in para 3" | Add a new row with the next free ID, mark `pending`, render in the next batch. |

Re-render only `revised` and newly-added `pending` rows. Never
re-render `accepted` rows.

Loop until every remaining row is `accepted`. When the user signs off,
proceed to Phase 5.

## Phase 5 — Emit phoneticized script

### Primary output: `script.respelled.txt`

The original script with respellings substituted inline. This is the
deliverable that goes into Eleven v3.

Substitution rules:

- Every occurrence of every accepted token's lemma → respelling
- Possessives and inflections handled at the surface form:
  `Siobhán's` → `shi-VAWNs`; `df12's` → `dee-eff-TWELVEs`
- Sentence-initial capitalization preserved: `Siobhán arrived` →
  `Shi-VAWN arrived` (capitalize the first letter, keep the stress
  capitals where they were)
- Punctuation preserved exactly
- Multi-occurrence consistency: same lemma → same respelling, every
  time

### Secondary output: `script.ssml.xml`

For engines that honour `<phoneme>` tags — Azure TTS, AWS Polly,
Google Cloud TTS, older Eleven models. Wrap each substituted token in
SSML using the IPA column:

```xml
I met <phoneme alphabet="ipa" ph="ʃɪˈvɔːn">Siobhán</phoneme> at the bar.
```

Skip rows where IPA is empty — emit the bare token, not a malformed
tag. The SSML version is best-effort archival; the primary respelling
is what the user actually narrates from.

### Archive: `pronunciation_table.md`

The final agreed table, saved alongside the scripts. When the user
re-narrates the same content months later, the table lets them
reproduce the voicing without re-running Phase 3. Suggest exporting
the table as an ElevenLabs PLS alias dictionary too — see
`references/eleven-v3-notes.md` for format.

## Output bundle

Final deliverables, presented via `present_files`:

```
output/
├── script.respelled.txt        ← primary: feeds into Eleven v3
├── script.ssml.xml             ← secondary: for SSML-aware engines
├── pronunciation_table.md      ← archive of the agreed table
└── samples/
    ├── P01_siobhan.mp3
    ├── P02_df12.mp3
    └── ...
```

List `script.respelled.txt` first in the `present_files` call — that's
the deliverable the user will reach for most often.
