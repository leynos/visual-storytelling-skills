# Detection heuristics

The patterns the regex helper applies, plus the semantic checks only
the agent can do. Run both — neither catches everything alone.

## Categories

| Code | Meaning | Examples |
|---|---|---|
| `NAM` | Proper noun (person/place) | Siobhán, Featherstonehaugh, Worcester, Reykjavík, Gdańsk |
| `CEL` | Gaelic / Welsh word | Llanfair, sláinte, cymru, Eilidh |
| `BRA` | Brand / product name | df12, Nginx, Xiaomi, IKEA, iPhone |
| `MOD` | Electronic model name with embedded numerics | Atari 2600, Z80, ESP32, RTX 4090 |
| `ART` | Term of art / acronym | SaaS, OAuth, JWT, JSON, CRUD, kubectl |
| `DOC` | Document specifier | ADR-0012, RFC 2119, ISO 27001, IEEE-754 |
| `OTH` | Other (rare diacritics, obscure jargon) | naïve, façade |

## Regex passes (deterministic)

These run inside `scripts/extract_candidates.py`. Each pass emits
candidates with a category guess. More-specific passes run first so
their categorisation wins on overlap.

### 1. Document specifiers

```regex
\b([A-Z]{2,6})[-_/\s](\d{2,})\b
```

Matches `ADR-0012`, `RFC 2119`, `ISO/IEC 27001`, `IEEE-754`. The separator is
required; compact model names such as `ESP32` and `Z80` fall through to the
alphanumeric brand / model pass. Always `DOC`.

### 2. Welsh / Gaelic markers

Distinctive Celtic patterns the model will mangle:

- Welsh: word-initial `ll`, `rh`, or `dd` followed by a vowel; Welsh
  circumflexes `ŵ`, `ŷ`, `â`, `ê`, `î`, `ô`, `û`
- Irish/Scottish lenition: `mh`, `bh`, `dh`, `fh`, or `gh` followed by an
  accented Irish vowel (`á`, `é`, `í`, `ó`, `ú`)

Always `CEL`.

Note: `th`, `sh`, `ch`, `ph` appear in ordinary English and are not
flagged on their own. Only the combinations above with vowel adjacency
or Celtic diacritics trigger.

### 3. Alphanumeric brand / model

```regex
\b([a-z][a-zA-Z]*\d+[a-zA-Z0-9]*|[a-z]+\d+[a-zA-Z0-9]*|[A-Z][a-zA-Z]*\d+[a-zA-Z0-9]*|\d+[a-zA-Z]+\d*)\b
```

Matches `df12`, `mxd2`, `Z80`, `RTX4090`, `iPhone15`, `iPad3`, `2600AD`.

- Lower-camel + numeric suffix → `BRA` (iPhone15, iPad3)
- Opens lowercase + digit → `BRA` (df12, mxd2)
- Opens uppercase → `MOD` (Z80, RTX4090)
- Opens with digit → `MOD` (2600AD)

### 4. CamelCase / mixed-case acronyms

```regex
\b([A-Z][a-z]*[A-Z][A-Za-z]*)\b
```

Matches `SaaS`, `OAuth`, `JavaScript`, `PostgreSQL`. Almost always `ART`.

### 5. Lower-camel brand

```regex
\b([a-z][a-z]*[A-Z][A-Za-z]*)\b
```

Matches `iPhone`, `eBay`, `kubectl` (when capitalised mid-word).
Category `BRA`.

### 6. Diacritic markers

Any token containing characters in the Latin Extended ranges
(`\u00c0-\u024f`, `\u1e00-\u1eff`). Default category `NAM` for
title-case tokens, `OTH` otherwise.

### 7. All-caps acronyms

```regex
\b([A-Z]{2,8})\b
```

Filtered against `COMMON_ALL_CAPS` (`I`, `OK`, `USA`, `UK`, etc.).
Category `ART`.

### 8. Title-case proper nouns

```regex
\b([A-Z][a-záéíóúäëïöüÿñç]{3,})\b
```

Filtered against `COMMON_TITLE_CASE` (months, weekdays, common
country/city names) and against sentence-initial position when the
token also appears lowercase elsewhere in the script. Category `NAM`.

## Semantic checks (agent does this)

The regex is fast but blind. It misses tokens whose pronunciation is
non-obvious despite an ordinary surface form. Pay attention to:

### English place names with silent letters

- Worcester → `WUSS-ter`
- Leicester → `LESS-ter`
- Featherstonehaugh → `FAN-shaw`
- Cholmondeley → `CHUM-lee`
- Magdalene (the Cambridge college) → `MAUD-lin`

The regex flags these as `NAM` based on title-case but won't know they
need respelling. The agent must recognise them.

### Loanwords with retained pronunciation

- lingerie → `LON-zhuh-ray`
- pho → `fuh` (not `foh`)
- façade → `fuh-SAHD`
- chaise longue → `shez LONG`

If the source script has stripped the diacritics (`facade` instead of
`façade`), the regex will miss them entirely. Read carefully.

### Programmer jargon with contested pronunciation

- Nginx → `engine-ex` (no consensus, but the project is firm)
- kubectl → `cube-cuttle`, `cube-control`, or `kube-C-T-L` — house
  styles vary; ask
- YAML → `YAM-ul` (per the spec) or `yay-mul` (regional)
- GIF → `gif` (hard g, per dictionaries) or `jif` (per the inventor) —
  contested; ask

### SQL and friends

- SQL → `S-Q-L` (letter-spelt) or `SEE-kwul` (as "sequel") — both are
  defensible; the user will have a preference
- NaN → `nan` (rhymes with "ran") or `N-A-N`
- JSON → `JAY-sahn` or `J-S-O-N`

### Multi-token model names

The regex catches `Atari` (NAM) and `2600` (no match, plain digits)
separately. Merge them by hand into a single candidate `Atari 2600`
with category `MOD`. Same for `RFC 2119`, `Section 230`, `Apollo 11`.

## Heuristic adjustments

- A title-case word at sentence start is **not** automatically a
  proper noun. Check whether it appears mid-sentence elsewhere
  lowercase (`The` does, `Siobhán` doesn't).
- All-caps inside possessives stay flagged: strip `'s` before matching
  (`the FBI's` → `FBI`).
- Hyphenated tokens: split on `-` and check each part separately, but
  keep the hyphenated form as the lemma in the table.
- Plain numbers without alphabetic context don't get flagged. `The
  year was 1995` is fine. `the Z80 chip` is not.

## Project allowlist

After the user agrees a respelling, save it for future runs of the
same project. Recommended location:

```text
references/project-pronunciations.json
```

Format:

```json
{
  "df12":     {"respelling": "dee-eff-TWELVE", "ipa": "diːˌɛfˈtwɛlv"},
  "Siobhán":  {"respelling": "shi-VAWN",        "ipa": "ʃɪˈvɔːn"},
  "Llanelli": {"respelling": "hlan-ETH-lee",    "ipa": "ɬaˈnɛɬi"}
}
```

On future runs, candidates already in the project allowlist skip
Phase 3 (TTS preview) and go straight to `accepted`. Pass the
allowlist path to the helper:

```bash
python scripts/extract_candidates.py script.txt \
    --allowlist references/project-pronunciations.json
```

The helper drops allowlisted lemmas from the candidate list entirely.
