"""Locate quotations in source text.

A quotation may be verbatim, or edited with the two marks the synthesis rules allow:
an ellipsis (``...`` or ``…``) for a cut and ``[brackets]`` for a clarifying insert.
Each remaining fragment must appear in the source, in order, with short gaps, so an
edited quote cannot be stitched together from distant parts of a transcript.
"""

import difflib
import re
import unicodedata
from dataclasses import dataclass

ELLIPSIS_RE = re.compile(r"\s*(?:\.\.\.|…)\s*")
BRACKET_RE = re.compile(r"\s*\[[^\[\]]*\]\s*")
MAX_GAP = 300          # characters allowed between fragments of an edited quote
MIN_FRAGMENT_CHARS = 8  # an edited quote must keep at least this much source text

FOLD = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"', "″": '"',
    " ": " ", " ": " ", " ": " ",
}


@dataclass
class Match:
    start: int
    end: int
    edited: bool

    def multiline(self, text):
        return "\n" in text[self.start:self.end].strip()


def fold(text):
    """Fold quote marks, ellipses and whitespace; return (folded, index_map).

    index_map[i] is the index in `text` that produced folded character i.
    """
    out, index_map = [], []
    previous_space = False
    for i, char in enumerate(text):
        char = FOLD.get(char, char)
        if char == "…":
            out.extend("...")
            index_map.extend([i, i, i])
            previous_space = False
            continue
        if char.isspace():
            if previous_space:
                continue
            char = " "
            previous_space = True
        else:
            previous_space = False
        out.append(char)
        index_map.append(i)
    return "".join(out), index_map


def fragments(quote, allow_brackets=True):
    parts = ELLIPSIS_RE.split(quote)
    if allow_brackets:
        parts = [piece for part in parts for piece in BRACKET_RE.split(part)]
    return [part.strip() for part in parts if part.strip()]


def has_edit_marks(quote, allow_brackets=True):
    return bool(ELLIPSIS_RE.search(quote) or (allow_brackets and BRACKET_RE.search(quote)))


def _occurrences(needle, haystack, start=0):
    found = []
    index = haystack.find(needle, start)
    while index != -1 and needle:
        found.append(index)
        index = haystack.find(needle, index + 1)
    return found


def find_quote(quote, text, normalize=False, allow_brackets=True, max_gap=MAX_GAP):
    """Return every Match of `quote` in `text`, in `text` coordinates."""
    base = unicodedata.normalize("NFC", text) if normalize else text
    needle = unicodedata.normalize("NFC", quote) if normalize else quote
    if normalize:
        haystack, index_map = fold(base)
        needle = fold(needle)[0]
    else:
        haystack, index_map = base, None

    def to_base(start, end):
        if index_map is None:
            return start, end
        return index_map[start], index_map[end - 1] + 1

    needle = needle.strip()
    if not needle:
        return []
    matches = [Match(*to_base(i, i + len(needle)), edited=False) for i in _occurrences(needle, haystack)]
    if matches or not has_edit_marks(needle, allow_brackets):
        return matches

    parts = fragments(needle, allow_brackets)
    if sum(len(part) for part in parts) < MIN_FRAGMENT_CHARS:
        return []
    for first in _occurrences(parts[0], haystack):
        position = first + len(parts[0])
        for part in parts[1:]:
            nxt = haystack.find(part, position)
            if nxt == -1 or nxt - position > max_gap:
                break
            position = nxt + len(part)
        else:
            matches.append(Match(*to_base(first, position), edited=True))
    return matches


def line_of(text, position):
    return text.count("\n", 0, position) + 1


def closest_line(quote, text):
    """Best-matching line for a missing quote: (line number, similarity 0..1)."""
    target = fold(quote)[0].strip().lower()
    best = (None, 0.0)
    for number, line in enumerate(text.splitlines(), 1):
        candidate = fold(line)[0].strip().lower()
        if not candidate:
            continue
        matcher = difflib.SequenceMatcher(None, target, candidate, autojunk=False)
        # Share of the quote's characters that align with this line.
        blocks = sum(block.size for block in matcher.get_matching_blocks())
        ratio = blocks / max(len(target), 1)
        if ratio > best[1]:
            best = (number, ratio)
    return best
