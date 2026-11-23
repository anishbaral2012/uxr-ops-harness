"""Check that an evidence locator points at where the excerpt actually is.

Supported forms (case-insensitive, anywhere in the locator string):
  line 12 | lines 12-14 | L12            -> 1-based line numbers
  paragraph 3 | para 3-4 | ¶3            -> blank-line separated blocks (or lines,
                                            when the source has no blank lines)
  00:12:34 | 12:34 | 00:12:30-00:13:10  -> the timestamp segment containing the excerpt
Anything else is reported as not machine-checkable.
"""

import re

from .textmatch import line_of

_RANGE = r"(\d+)(?:\s*(?:-|–|to)\s*(\d+))?"
LINE_RE = re.compile(r"\b(?:lines?|ll?\.?)\s*" + _RANGE + r"\b", re.IGNORECASE)
PARA_RE = re.compile(r"(?:\b(?:paragraphs?|paras?)|¶)\s*" + _RANGE + r"\b", re.IGNORECASE)
_TS = r"\d{1,2}:\d{2}(?::\d{2})?"
TS_RANGE_RE = re.compile(r"(?<![\d:])(" + _TS + r")(?:\s*(?:-|–|to)\s*(" + _TS + r"))?(?![\d:])")
TS_RE = re.compile(r"(?<![\d:])" + _TS + r"(?![\d:])")


def seconds(stamp):
    total = 0
    for part in stamp.split(":"):
        total = total * 60 + int(part)
    return total


def _bounds(match):
    first = int(match.group(1))
    last = int(match.group(2)) if match.group(2) else first
    return first, max(first, last)


def paragraph_starts(text):
    """Start offsets of numbered paragraphs."""
    separator = r"\n(?:[ \t]*\n)+" if re.search(r"\n[ \t]*\n", text) else r"\n"
    starts, position = [], 0
    for match in re.finditer(separator, text):
        if text[position:match.start()].strip():
            starts.append(position)
        position = match.end()
    if text[position:].strip():
        starts.append(position)
    return starts


def paragraph_of(starts, position):
    number = 0
    for index, start in enumerate(starts, 1):
        if start <= position:
            number = index
        else:
            break
    return number


def check(locator, text, matches):
    """Return (status, detail): status is 'ok', 'mismatch' or 'unchecked'."""
    if not matches:
        return "unchecked", "excerpt not located"

    found = LINE_RE.search(locator)
    if found:
        first, last = _bounds(found)
        spans = [(line_of(text, m.start), line_of(text, max(m.start, m.end - 1))) for m in matches]
        if any(first <= a and b <= last for a, b in spans):
            return "ok", ""
        where = ", ".join(f"line {a}" if a == b else f"lines {a}-{b}" for a, b in spans)
        return "mismatch", f"locator '{locator}' but excerpt is at {where}"

    found = PARA_RE.search(locator)
    if found:
        first, last = _bounds(found)
        starts = paragraph_starts(text)
        numbers = [paragraph_of(starts, m.start) for m in matches]
        if any(first <= n <= last for n in numbers):
            return "ok", ""
        where = ", ".join(f"paragraph {n}" for n in numbers)
        return "mismatch", f"locator '{locator}' but excerpt is in {where}"

    found = TS_RANGE_RE.search(locator)
    if found:
        start = seconds(found.group(1))
        end = seconds(found.group(2)) if found.group(2) else start
        stamps = [(m.start(), seconds(m.group(0))) for m in TS_RE.finditer(text)]
        if not stamps:
            return "unchecked", f"timestamp locator '{locator}' but the source has no timestamps"
        for match in matches:
            before = [sec for pos, sec in stamps if pos <= match.start]
            after = [sec for pos, sec in stamps if pos > match.start]
            segment_start = before[-1] if before else 0
            segment_end = after[0] if after else float("inf")
            if segment_start <= end and start < max(segment_end, segment_start + 1):
                return "ok", ""
        return "mismatch", f"locator '{locator}' does not cover the timestamp segment containing the excerpt"

    return "unchecked", f"locator '{locator}' is not machine-checkable (use line, paragraph or timestamp)"
