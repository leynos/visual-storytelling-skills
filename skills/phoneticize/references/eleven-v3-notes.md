# Eleven v3 — what the engine actually accepts

Engine-specific quirks that affect the phoneticization output. Re-read
this before Phase 5 to make sure the script you emit will actually
render the way the table promises.

Source for the model-specific claims in this file: ElevenLabs official
documentation, "Pronunciation dictionaries" and "Best practices"
guides.

## Phoneme tag support — silently broken on v3

**Phoneme tags only work with `eleven_flash_v2` and
`eleven_monolingual_v1`.** With other models — including v3 — the tags
are silently skipped and the default pronunciation is used. No error,
no warning, just wrong audio.

This is the central design constraint. SSML like:

```xml
I met <phoneme alphabet="ipa" ph="ʃɪˈvɔːn">Siobhán</phoneme> at the bar.
```

…will render on v3 as plain `Siobhán` with whatever default the model
picks for that orthography (typically a clumsy English-letter reading
that bears no resemblance to the Irish pronunciation).

The workaround: respell inline. Replace the printed letters with
letters the model pronounces correctly:

```text
I met shi-VAWN at the bar.
```

This works because the model reads orthography. You're changing what
it reads.

## CMU Arpabet vs IPA

Even on the supported models, ElevenLabs' own guidance recommends CMU
Arpabet over IPA — they describe Arpabet as more "predictable,
consistent, and better overall" for the current generation of voice
models. So if you ever need to fall back to phoneme tags (because the
target engine is `eleven_flash_v2` rather than v3), prefer Arpabet:

```xml
<phoneme alphabet="cmu-arpabet" ph="SH IH V AO N">Siobhán</phoneme>
```

For v3 specifically, this is moot — both alphabets are silently
ignored.

## Non-English support — phoneme tags are English-only

Even on supported models, phoneme tags only work for English. For
Welsh, Gaelic, or any other language, the tags are ignored regardless
of model. Alias-based replacement (text → text) is the only universal
mechanism.

Practical consequence: respelling is the only viable approach for
Celtic-language tokens regardless of which Eleven model targets.
"hlan-ETH-lee" gets close enough to /ɬaˈnɛɬi/ for narration purposes
even though it's a coarse approximation.

## Audio tags

Eleven v3 introduced inline audio tags for delivery — `[whispers]`,
`[laughs]`, `[excited]`, `[sarcastic]`, etc. These are not
phoneticization, but they interact with respellings in one critical
way: don't put a respelt word inside square brackets. The tag parser
treats anything in `[…]` as a stage direction, not as text to render.

```text
GOOD: [excited] I met shi-VAWN at the bar!
BAD:  I met [shi-VAWN] at the bar.       # parsed as a directive
```

## Pause control

Eleven v3 does not support SSML `<break>` tags. For pause control, use
supported audio and expressive tags such as `[pause]`, `[short pause]`,
and `[long pause]`, plus punctuation such as ellipses and sentence/paragraph
structure.

## Capital letters and punctuation as prosody hints

The docs explicitly recommend capital letters, dashes, apostrophes,
and single quotes as nudges for emphasis. The respellings in this
skill rely on the same mechanism:

- Capitals → stress
- Hyphens → syllable boundaries
- Apostrophes → glottal stop or syllable break

Build the respelling to lean *with* these conventions, not against
them. Accidentally capitalising a non-stressed syllable can produce
worse output than leaving the original spelling alone.

## Pronunciation dictionaries (PLS files)

For projects with many recurring tokens, ElevenLabs supports PLS files
(case-sensitive XML) at the project level. On v3, PLS dictionaries
with `<phoneme>` entries are skipped (same constraint as inline
phoneme tags), but `<alias>` entries — text-to-text replacement —
work universally.

A PLS alias dictionary is essentially the same data as the
project allowlist, in the format ElevenLabs expects:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0"
         xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
         alphabet="ipa"
         xml:lang="en-GB">
  <lexeme>
    <grapheme>Siobhán</grapheme>
    <alias>shi-VAWN</alias>
  </lexeme>
  <lexeme>
    <grapheme>df12</grapheme>
    <alias>dee-eff-TWELVE</alias>
  </lexeme>
</lexicon>
```

Suggest exporting the agreed table as a PLS alias dictionary if the
user works on the same scripts repeatedly. The dictionary lives at
the project level in ElevenLabs and gets applied automatically to
every render — no inline substitution needed in the script source.

## Higgsfield MCP — calling conventions

The skill assumes a Higgsfield MCP TTS tool is available. Discover via:

```text
tool_search keywords=["tts", "higgsfield", "speech", "eleven"]
```

The exact tool name and parameter shape are determined by the
Higgsfield MCP server, not by this skill. Typical parameters:

- `text` — the fragment to render
- `voice` or `voice_id` — which voice to use
- `model` or `model_id` — the Eleven model; pass `eleven_v3` (or the
  exact string the tool documents) for v3

If the tool exposes no model selection, the default voice will dictate
the engine version. Check the voice settings in the Higgsfield project
or ElevenLabs dashboard.

If `tool_search` returns nothing, the connector isn't available in
this environment. Surface this to the user and use `suggest_connectors`
to offer the connection. Don't fabricate audio paths — the user needs
to know the rendering didn't happen.

## Failure modes worth knowing

- **Same token, different render across calls.** Eleven v3 outputs are
  not strictly deterministic. If the user says a sample sounds
  different on a re-render, that may be model variance, not your
  respelling. Re-render with the same input to compare.
- **Numbers spoken differently in different contexts.** "2025" might
  be `twenty-twenty-five` mid-sentence and `two thousand twenty-five`
  at the start. If consistency matters, respell the digits as words
  in every occurrence.
- **Punctuation absorbing prosody.** A respelt token at the end of a
  sentence carries the falling intonation of the full stop; the same
  respelling mid-sentence sounds different. Always preview in context.
