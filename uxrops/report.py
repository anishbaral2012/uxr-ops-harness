"""Check report documents (analysis, Word report, deck) against the verified ledger.

Checks:
- every quotation of four or more words is found in a registered source, and in the ledger;
- a source ID or participant code written just after a quotation matches where it was found;
- theme and research question IDs in the document exist in the ledger;
- every ledger theme appears in each document (warning);
- an "N of M" count near a theme matches its supporting participants (warning);
- optional style rule from uxr-project.json: no mid-sentence dashes outside quotations (warning).
"""

import re

from .textmatch import fold, find_quote

QUOTE_RE = re.compile(r"[“\"]([^“”\"\n]+?)[”\"]")
THEME_ID_RE = re.compile(r"\bT\d+\b")
RQ_ID_RE = re.compile(r"\bRQ\d+\b")
PARTICIPANT_RE = re.compile(r"\bP[1-9][0-9]*\b")
DASH_RE = re.compile(r"\w[ \t]*[—–][ \t]*\w|\w[ \t]+-[ \t]+\w")
NUMBER_WORDS = {
    word: value for value, word in enumerate(
        "zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
    )
}
_NUM = r"(\d+|" + "|".join(NUMBER_WORDS) + r")"
COUNT_RE = re.compile(r"\b" + _NUM + r"\s+(?:of|out of)\s+" + _NUM + r"\b", re.IGNORECASE)
ATTRIBUTION_WINDOW = 160


def _number(token):
    token = token.lower()
    return int(token) if token.isdigit() else NUMBER_WORDS[token]


def _preview(text, words=8):
    parts = text.split()
    return " ".join(parts[:words]) + (" …" if len(parts) > words else "")


def _ledger_excerpts(study):
    excerpts = []
    for theme in study.themes:
        if not isinstance(theme, dict):
            continue
        for item in theme.get("evidence") or []:
            if not isinstance(item, dict):
                continue
            for name in ("quote", "display_quote"):
                if isinstance(item.get(name), str) and item[name].strip():
                    excerpts.append((item.get("source_id"), item[name]))
    return excerpts


def _check_quotes(study, doc, findings, min_words):
    excerpts = _ledger_excerpts(study)
    known_sources = [s for s in study.sources.values() if s.text is not None]
    source_id_re = re.compile(r"\b(" + "|".join(re.escape(s) for s in sorted(study.sources, key=len, reverse=True)) + r")\b") if study.sources else None
    for section in doc.sections:
        quotes = list(QUOTE_RE.finditer(section.text))
        for index, match in enumerate(quotes):
            quote = match.group(1).strip()
            if len(quote.split()) < min_words:
                continue
            where = f"{doc.name} ({section.title})"
            found_in = [s for s in known_sources if find_quote(quote, s.text, normalize=True)]
            if not found_in:
                findings.error(f"{where}: quotation not found in any registered source: “{_preview(quote)}”.")
                continue
            in_ledger = any(
                find_quote(quote, text, normalize=True) or fold(text)[0].strip() in fold(quote)[0]
                for sid, text in excerpts if sid in {s.id for s in found_in}
            )
            if not in_ledger:
                ids = ", ".join(s.id for s in found_in)
                findings.warn(f"{where}: quotation from {ids} is not recorded in the evidence ledger: “{_preview(quote)}”.")
            # Attribution: text after the quotation, up to the next quotation.
            limit = quotes[index + 1].start() if index + 1 < len(quotes) else len(section.text)
            tail = section.text[match.end():min(limit, match.end() + ATTRIBUTION_WINDOW)]
            cited_source = source_id_re.search(tail) if source_id_re else None
            if cited_source and cited_source.group(1) not in {s.id for s in found_in}:
                actual = ", ".join(s.id for s in found_in)
                findings.error(f"{where}: quotation attributed to {cited_source.group(1)} but found in {actual}: “{_preview(quote)}”.")
            cited_participant = PARTICIPANT_RE.search(tail)
            if cited_participant and cited_participant.group(0) not in {s.participant for s in found_in}:
                actual = ", ".join(sorted({str(s.participant) for s in found_in}))
                findings.error(f"{where}: quotation attributed to {cited_participant.group(0)} but it comes from {actual}: “{_preview(quote)}”.")


def _check_ids(study, doc, findings):
    text = doc.text
    themes = study.theme_ids()
    for tid in sorted(set(THEME_ID_RE.findall(text)) - themes):
        findings.error(f"{doc.name}: mentions theme {tid}, which is not in the evidence ledger.")
    for tid in sorted(themes - set(THEME_ID_RE.findall(text))):
        findings.warn(f"{doc.name}: ledger theme {tid} does not appear in this document.")
    rqs = set(RQ_ID_RE.findall(text))
    if rqs and not study.research_questions:
        findings.warn(f"{doc.name}: mentions research questions but the ledger defines none; add research_questions to the ledger.")
    elif study.research_questions:
        for rid in sorted(rqs - set(study.research_questions)):
            findings.error(f"{doc.name}: mentions {rid}, which is not in the ledger's research questions.")


def _check_counts(study, doc, findings):
    supporting = {
        t["id"]: len(t.get("supporting_participants") or [])
        for t in study.themes if isinstance(t, dict) and isinstance(t.get("id"), str)
    }
    for section in doc.sections:
        ids = set(THEME_ID_RE.findall(section.title if doc.kind != "pptx" else section.text)) & set(supporting)
        if len(ids) != 1:
            continue
        tid = ids.pop()
        counts = [(_number(a), _number(b)) for a, b in COUNT_RE.findall(section.text)]
        if counts and not any(n == supporting[tid] for n, _ in counts):
            shown = ", ".join(f"{n} of {m}" for n, m in counts)
            findings.warn(
                f"{doc.name} ({section.title}): counts for {tid} ({shown}) do not include its "
                f"{supporting[tid]} supporting participant(s) in the ledger."
            )


def _check_style(doc, style, findings):
    if not style.get("avoid_mid_sentence_dashes"):
        return
    hits = []
    for section in doc.sections:
        prose = QUOTE_RE.sub(" ", section.text)
        prose = "\n".join(line for line in prose.splitlines() if not line.lstrip().startswith("|"))
        count = len(DASH_RE.findall(prose))
        if count:
            hits.append(f"{section.title} ({count})")
    if hits:
        findings.warn(f"{doc.name}: mid-sentence dashes outside quotations, against the study style: {', '.join(hits[:5])}.")


def check_documents(study, documents, findings, min_words=4, style=None):
    for doc in documents:
        _check_quotes(study, doc, findings, min_words)
        _check_ids(study, doc, findings)
        _check_counts(study, doc, findings)
        _check_style(doc, style or {}, findings)
