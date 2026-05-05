# Respelling conventions

How to write phonetic respellings the TTS engine will actually obey.
Optimised for Eleven v3, which interprets text orthographically rather
than parsing phoneme tags.

## Why respelling, not IPA

Eleven v3 silently drops SSML `<phoneme>` tags. Documented support is
limited to `eleven_flash_v2` and `eleven_monolingual_v1`; on every
other model, including v3, the tags are ignored and the word renders
with the default pronunciation.

Respelling — replacing the printed letters with letters the model
already knows how to pronounce — is what actually changes the output.
The model reads orthography. Change the orthography, change the read.

IPA goes in the IPA column for archival precision and for engines that
honour `<phoneme>` tags. The respelling is what gets substituted into
the production script.

## Style rules

### 1. Hyphens between syllables

Always. The hyphen forces the model to treat each chunk as a discrete
syllable; without it, syllables fuse and stress drifts.

```text
Siobhán       → shi-VAWN
sláinte       → SLAWN-cha
Llanfair      → HLAN-vair
caffeinated   → ka-FEEN-ay-ted
```

### 2. Capitalization marks stress

Stressed syllable in `ALL CAPS`. Unstressed lowercase.

```text
shi-VAWN          (Siobhán — stress on second)
LLAN-fair         (Welsh — stress always penultimate)
ka-FEEN-ay-ted    (caffeinated — stress on the second)
```

For monosyllables, no caps needed unless the engine is
mispronouncing something specific:

```text
sass        (SaaS — single-syllable, no stress markup needed)
nan         (NaN — same)
```

### 3. English orthographic conventions, not IPA

The model is trained on English text. Use letter combinations it
already knows:

| Sound | IPA | Respell as |
|---|---|---|
| Long a (face) | /eɪ/ | `ay`, `ai` |
| Long e (fleece) | /iː/ | `ee`, `ea` |
| Long i (price) | /aɪ/ | `eye`, `igh`, `y` |
| Long o (goat) | /oʊ/ | `oh`, `oa` |
| Long u (goose) | /uː/ | `oo`, `ew` |
| Schwa | /ə/ | `uh`, `a` |
| /ɔː/ (thought) | /ɔː/ | `aw`, `or` |
| /ʃ/ (sh) | /ʃ/ | `sh` |
| /tʃ/ (ch) | /tʃ/ | `ch` |
| /ʒ/ (s in measure) | /ʒ/ | `zh` |
| /ŋ/ (sing) | /ŋ/ | `ng` |

Avoid spellings the model might over-correct: `nyu` for "new" can
trip the model into pronouncing the `y`; use `noo` instead. `wun` for
"one" risks being read literally; "won" is safer.

### 4. Disambiguate hard consonants

Standard English makes `c` and `g` ambiguous. When the model is
mispronouncing, force the hand:

```text
cat   → kat        (avoids c being read /s/)
goal  → gohl       (avoids g being read /dʒ/)
geo-  → JEE-oh     (forces the soft g)
ceres → SEE-reez   (forces the soft c)
```

### 5. Numerics in model names — write them out

The model's number-handling is inconsistent and depends heavily on
context. Spell digits as words:

```text
Atari 2600   → Atari twenty-six hundred
             (or "two thousand six hundred" if the user prefers)
Z80          → Z eighty
ESP32        → E-S-P thirty-two
RTX 4090     → R-T-X forty-ninety
              (or "forty oh-ninety" / "four thousand ninety")
ADR-0012     → A-D-R twelve         (drop the leading zeros when speaking)
RFC 2119     → R-F-C twenty-one nineteen
ISO 27001    → I-S-O twenty-seven thousand one
              (or "two-seven-oh-oh-one" if the user prefers digit-by-digit)
```

When in doubt, ask the user how they want a specific number read. Year
numbers (`1995`, `2024`) are usually safe to leave alone — the model
handles them well — but document numbers and model numbers vary.

### 6. Acronyms — letter-spelt or word-spelt

Decide explicitly. Both forms are valid for most acronyms; the user
will have a preference, and the project should commit to one.

| Acronym | Letter-spelt | Word-spelt |
|---|---|---|
| SQL | `S-Q-L` | `SEE-kwul` (as "sequel") |
| JSON | `J-S-O-N` | `JAY-sahn` |
| JWT | `J-W-T` | `JOT` |
| YAML | (rare) | `YAM-ul` |
| SaaS | (never) | `sass` |
| OAuth | (never) | `OH-auth` |
| GIF | (rare) | `gif` (hard g) or `jif` |
| GUI | `G-U-I` | `GOO-ee` |
| WYSIWYG | (never) | `WIZ-ee-wig` |

When the project hasn't decided, put `?` in the Respelling column and
list both candidates in the table notes for the user to pick.

### 7. Surrounding context

Some respellings only work in context. `df12` rendered alone might
work as `dee-eff-twelve`, but in the sentence "df12's stack" it might
need to be `dee-eff-TWELVE's stack` to keep the possessive cleanly
attached. Check the phoneticized fragment in Phase 3 — that's where
context-induced failures show up.

## IPA archive form

For the IPA column, use standard IPA with primary stress marked `ˈ`
before the stressed syllable, secondary `ˌ` where relevant.

```text
Siobhán    ʃɪˈvɔːn
df12       ˌdiːˌɛfˈtwɛlv
Llanelli   ɬaˈnɛɬi          (note ɬ for Welsh ll)
sláinte    ˈsˠl̪ˠaːnʲtʃə
```

Welsh `ll` is /ɬ/, the voiceless lateral fricative — render it `hl`
in the respelling (as in `HLAN-fair`) since most English speakers
approximate `ll` with `hl` and the model follows.

If you're not certain of the IPA, leave the column blank. Don't
fabricate — the audio sample is the ground truth, IPA is the
documentation, and a wrong IPA in the archive will mislead future
runs.

## Worked examples

| Token | Cat | Respelling | IPA | Phoneticized fragment |
|---|---|---|---|---|
| Siobhán | NAM | `shi-VAWN` | ʃɪˈvɔːn | "...met shi-VAWN at the bar" |
| Llanelli | CEL | `hlan-ETH-lee` | ɬaˈnɛɬi | "...drove through hlan-ETH-lee at dusk" |
| Featherstonehaugh | NAM | `FAN-shaw` | ˈfænʃɔː | "...to Mr. FAN-shaw's office" |
| df12 | BRA | `dee-eff-TWELVE` | ˌdiːˌɛfˈtwɛlv | "the dee-eff-TWELVE design system" |
| Atari 2600 | MOD | `Atari twenty-six hundred` | əˈtɑːri ˈtwɛntisɪks ˈhʌndrəd | "the Atari twenty-six hundred shipped in 1977" |
| Z80 | MOD | `Z eighty` | ziːˈeɪti | "...running on a Z eighty" |
| SaaS | ART | `sass` | sæs | "a typical sass deployment" |
| OAuth | ART | `OH-auth` | ˈoʊɔːθ | "the OH-auth flow handles tokens" |
| JWT | ART | `J-W-T` | ˌdʒeɪdʌbljuˈtiː | "...verifies the J-W-T signature" |
| ADR-0012 | DOC | `A-D-R twelve` | ˌeɪdiːɑːr ˈtwɛlv | "see A-D-R twelve for the rationale" |
| RFC 2119 | DOC | `R-F-C twenty-one nineteen` | ˌɑːrɛfsiː ˌtwɛntiwʌn ˈnaɪntiːn | "...as R-F-C twenty-one nineteen specifies" |

## When to prefer alternative-spelling tricks over respelling

Sometimes a single letter trick works better than a full respelling.
The Eleven docs note that capitals, dashes, and apostrophes all push
the model in useful directions. For minor adjustments:

```text
trapezii  → trapezIi      (force emphasis on the ii — capital alone)
read      → re-ad         (force two-syllable reading — dash alone)
the       → THE           (force stress — caps alone)
```

These are surgical interventions, not full phoneticizations. Use them
when a respelling is overkill but the model still mis-renders a word.
