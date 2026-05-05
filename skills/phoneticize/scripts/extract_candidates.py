#!/usr/bin/env python3
"""Extract pronunciation candidates from a TTS script.

Usage:
    python extract_candidates.py <script.txt> [--out candidates.json]
                                              [--allowlist allowlist.json]

Emits candidates as JSON. Each candidate has:
    - lemma:    canonical form for deduping
    - tokens:   list of surface forms encountered (with case/inflection)
    - category: NAM | CEL | BRA | MOD | ART | DOC | OTH
    - positions: character offsets of every occurrence
    - fragment: 5-6 word context around the first occurrence

The categorisation is heuristic. The agent should review the output
and refine it with semantic context the regex cannot see — see
references/detection-heuristics.md for the kinds of tokens this
script will miss (Worcester, Featherstonehaugh, kubectl, etc.).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Allowlists
# ---------------------------------------------------------------------------

COMMON_ALL_CAPS = {
    "I", "A", "OK", "OKAY", "TV", "PM", "AM", "USA", "UK", "EU", "UN",
    "AI", "ML", "OS", "DB", "ID", "OS", "PR", "QA", "QC", "RD",
    "II", "III", "IV", "VI", "VII", "VIII", "IX",  # Roman numerals
}

COMMON_TITLE_CASE = {
    # Days, months
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    # Common geographic
    "England", "Scotland", "Wales", "Ireland", "London", "Edinburgh",
    "America", "Europe", "Asia", "Africa", "Australia",
    "English", "French", "German", "Spanish", "Italian", "Russian",
    # Function words that appear sentence-initially and the regex would
    # otherwise mis-classify as proper nouns. Only words of 4+ letters
    # need listing — shorter words don't match TITLE_CASE_PATTERN anyway.
    "Their", "There", "These", "Those", "This", "That",
    "What", "When", "Where", "Which", "While", "Whose",
    "After", "Before", "During", "Since", "Until", "Within",
    "About", "Above", "Across", "Under", "Over", "Through",
    "Some", "Many", "Most", "Each", "Every", "Both", "Either", "Neither",
    "Here", "There", "Today", "Tomorrow", "Yesterday",
    "Yes", "Also", "Even", "Just", "Only", "Then", "Thus",
    "Would", "Could", "Should", "Might", "Must", "Will", "Shall",
    "Have", "Been", "Were", "Was", "Has", "Had", "Does", "Did",
    "They", "Them", "Such", "Both", "Some",
    # Honorifics — handled separately by sentence context but listed here
    # as a defensive measure
    "Mister", "Missus", "Doctor", "Professor",
}

# ---------------------------------------------------------------------------
# Patterns (more specific first; first-match wins per offset)
# ---------------------------------------------------------------------------

# DOC: ADR-0012, RFC 2119, ISO 27001, IEEE-754
# Separator is mandatory — without it (e.g. ESP32, Z80) the token is a
# model number, not a document specifier; it falls through to ALPHANUM.
DOC_PATTERN = re.compile(r"\b([A-Z]{2,6})[-_/\s](\d{2,})\b")

# Welsh: word-initial Ll/Rh/Dd + vowel, OR Welsh circumflex anywhere.
# Word-initial check is critical — `pulled`, `bell`, `hello` all contain
# `ll` + vowel mid-word but are plain English, not Welsh.
WELSH_PATTERN = re.compile(
    r"\b("
    r"(?:Ll|Rh|Dd|ll|rh|dd)[aeiouwy][A-Za-z]*"  # word-initial digraph
    r"|[A-Za-z]*[\u0175\u0177\u00e2\u00ea\u00ee\u00f4\u00fb][A-Za-z]*"  # circumflex
    r")\b",
    re.UNICODE,
)

# Gaelic: lenition cluster + accented Irish vowel.
# Accented vowels (á/é/í/ó/ú) are the reliable signal — plain English
# vowels after `bh`/`mh` produce too many false positives (`abhor`,
# `mghua`-style false matches in compound words).
GAELIC_PATTERN = re.compile(
    r"\b[A-Za-z]*"
    r"(?:mh|bh|dh|fh|gh)"
    r"[\u00e1\u00e9\u00ed\u00f3\u00fa][A-Za-z]*\b",
    re.IGNORECASE | re.UNICODE,
)

# Alphanumeric brand/model: at least one letter and one digit
ALPHANUM_PATTERN = re.compile(
    r"\b("
    r"[a-z][a-zA-Z]*\d+[a-zA-Z0-9]*"        # iPhone15, iPad3 (lower-camel + numeric suffix)
    r"|[a-z]+\d+[a-zA-Z0-9]*"                 # df12, mxd2 (lowercase start + digit)
    r"|[A-Z][a-zA-Z]*\d+[a-zA-Z0-9]*"         # Z80, RTX4090 (uppercase start)
    r"|\d+[a-zA-Z]+\d*"                        # 2600AD
    r")\b"
)

# CamelCase: capital, optional lowercase, capital, more letters
# Catches SaaS, OAuth, JavaScript, PostgreSQL
MIXED_CAPS_PATTERN = re.compile(r"\b([A-Z][a-z]*[A-Z][A-Za-z]+)\b")

# Lower-camel: lowercase start, internal capital
# Catches iPhone, eBay
LOWER_CAMEL_PATTERN = re.compile(r"\b([a-z][a-z]*[A-Z][A-Za-z]+)\b")

# Diacritic markers (Latin Extended-A, -B, Additional)
DIACRITIC_PATTERN = re.compile(
    r"\b\w*[\u00c0-\u024f\u1e00-\u1eff]\w*\b",
    re.UNICODE,
)

# All-caps acronym
ACRONYM_PATTERN = re.compile(r"\b([A-Z]{2,8})\b")

# Title-case proper noun, 4+ chars
TITLE_CASE_PATTERN = re.compile(
    r"\b([A-Z][a-z\u00c0-\u024f]{3,})\b",
    re.UNICODE,
)

# Sentence-ending punctuation (for sentence-initial title-case detection)
SENTENCE_END = re.compile(r"[.!?]\s+$")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Candidate:
    lemma: str
    category: str
    tokens: list[str] = field(default_factory=list)
    positions: list[int] = field(default_factory=list)
    fragment: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def lemmatise(token: str) -> str:
    """Strip common English inflections for deduping."""
    for suffix in ("'s", "\u2019s", "s'", "\u2019"):
        if token.endswith(suffix):
            return token[: -len(suffix)]
    return token


def context_fragment(text: str, position: int, token_length: int) -> str:
    """Extract a ~5-6 word fragment around a position."""
    # Don't cross newlines — keeps fragments inside a single sentence/line.
    line_start = text.rfind("\n", 0, position) + 1
    line_end = text.find("\n", position + token_length)
    if line_end == -1:
        line_end = len(text)

    before = text[line_start:position]
    after = text[position + token_length : line_end]

    # Take ~3 words on each side; pad if the line is short.
    before_words = before.strip().split()[-3:]
    token_text = text[position : position + token_length]
    after_words = after.strip().split()[:3]

    parts = before_words + [token_text] + after_words
    fragment = " ".join(parts).strip()

    # Add ellipses if we trimmed
    if before.strip().split()[:-3]:
        fragment = "... " + fragment
    if after.strip().split()[3:]:
        fragment = fragment + " ..."

    return fragment


def is_sentence_initial(text: str, position: int) -> bool:
    """True if the token at position is the first word of a sentence."""
    if position == 0:
        return True
    # Look back for sentence-ending punctuation followed by whitespace.
    preceding = text[max(0, position - 4) : position]
    return bool(SENTENCE_END.search(preceding))


def _lowercase_token_set(text: str) -> set[str]:
    """Precompute all lowercase word tokens for O(1) membership tests.

    Mirrors the semantics of the old per-call regex: only retains tokens
    that already appear in all-lowercase form (i.e. not title-case or
    all-caps occurrences).  Building this set once avoids a full-text
    regex scan for every title-case candidate.
    """
    return {
        w
        for w in re.findall(r"\b[A-Za-z\u00c0-\u024f]+\b", text, re.UNICODE)
        if w == w.lower()
    }


def appears_lowercase_elsewhere(token: str, lowercase_tokens: set[str]) -> bool:
    """Heuristic: does the lowercase form appear as a separate word?"""
    lower = token.lower()
    if lower == token:
        return False
    return lower in lowercase_tokens


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def find_candidates(text: str, allowlist: set[str]) -> list[Candidate]:
    """Run all detection passes and merge into deduplicated candidates."""
    found: dict[str, Candidate] = OrderedDict()
    seen_offsets: set[int] = set()
    lowercase_tokens = _lowercase_token_set(text)

    # Order matters: more specific patterns first so they win the category.
    passes: list[tuple[re.Pattern[str], str | None]] = [
        (DOC_PATTERN, "DOC"),
        (WELSH_PATTERN, "CEL"),
        (GAELIC_PATTERN, "CEL"),
        (ALPHANUM_PATTERN, None),       # categorise by shape: BRA or MOD
        (MIXED_CAPS_PATTERN, "ART"),
        (LOWER_CAMEL_PATTERN, "BRA"),
        (DIACRITIC_PATTERN, None),      # NAM if title-case else OTH
        (ACRONYM_PATTERN, "ART"),
        (TITLE_CASE_PATTERN, "NAM"),
    ]

    for pattern, forced_category in passes:
        for match in pattern.finditer(text):
            token = match.group(0)
            start = match.start()

            if start in seen_offsets:
                continue

            lemma = lemmatise(token)
            if lemma in allowlist:
                continue

            # Apply per-category common-word skips.
            if forced_category == "ART" and lemma in COMMON_ALL_CAPS:
                continue
            if forced_category == "NAM" and lemma in COMMON_TITLE_CASE:
                continue

            # Decide category.
            category = forced_category
            if category is None:
                if pattern is ALPHANUM_PATTERN:
                    category = "BRA" if token[0].islower() else "MOD"
                elif pattern is DIACRITIC_PATTERN:
                    category = "NAM" if token[0].isupper() else "OTH"
                else:
                    category = "OTH"

            # Sentence-initial title-case: only flag if the lowercase form
            # is NOT used elsewhere (i.e. it really is a proper noun).
            if (
                pattern is TITLE_CASE_PATTERN
                and is_sentence_initial(text, start)
                and appears_lowercase_elsewhere(token, lowercase_tokens)
            ):
                continue

            seen_offsets.add(start)

            if lemma not in found:
                found[lemma] = Candidate(
                    lemma=lemma,
                    category=category,
                    tokens=[token],
                    positions=[start],
                    fragment=context_fragment(text, start, len(token)),
                )
            else:
                cand = found[lemma]
                if token not in cand.tokens:
                    cand.tokens.append(token)
                cand.positions.append(start)

    return list(found.values())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract pronunciation candidates from a TTS script."
    )
    parser.add_argument(
        "script", type=Path, help="Path to the TTS script (text file, UTF-8)."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("candidates.json"),
        help="Output JSON path (default: candidates.json).",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=None,
        help="JSON file with already-resolved tokens to skip "
        "(keys = lemmas, values = pronunciation entries).",
    )
    args = parser.parse_args(argv)

    if not args.script.exists():
        print(f"error: script not found: {args.script}", file=sys.stderr)
        return 2

    text = args.script.read_text(encoding="utf-8")

    allowlist: set[str] = set()
    if args.allowlist:
        if not args.allowlist.exists():
            print(f"error: allowlist not found: {args.allowlist}", file=sys.stderr)
            return 2
        try:
            data = json.loads(args.allowlist.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"error: invalid allowlist JSON: {exc}", file=sys.stderr)
            return 2
        if isinstance(data, dict):
            allowlist = set(data.keys())
        elif isinstance(data, list):
            allowlist = set(data)
        else:
            print(
                "warning: allowlist must be a JSON object or array; ignoring",
                file=sys.stderr,
            )

    candidates = find_candidates(text, allowlist)

    args.out.write_text(
        json.dumps(
            [asdict(c) for c in candidates],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(
        f"Found {len(candidates)} candidates -> {args.out}",
        file=sys.stderr,
    )

    # Summary by category for quick eyeballing
    by_cat: dict[str, int] = {}
    for c in candidates:
        by_cat[c.category] = by_cat.get(c.category, 0) + 1
    if by_cat:
        summary = ", ".join(
            f"{cat}={count}" for cat, count in sorted(by_cat.items())
        )
        print(f"  by category: {summary}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
