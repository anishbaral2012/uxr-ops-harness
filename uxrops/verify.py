"""Mechanical checks for a pseudonymous source manifest and its evidence ledger."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import locators
from .common import Findings, digest, load_json, resolve_inside
from .textmatch import closest_line, find_quote

PARTICIPANT_RE = re.compile(r"P[1-9][0-9]*")
HASH_RE = re.compile(r"[0-9a-f]{64}")
POLARITIES = ("support", "contradict", "context")
SENTENCE_RE = re.compile(r"[.!?]+(?:\s|$)")


@dataclass
class Source:
    id: str
    participant: object
    path: object = None
    hash: object = None
    text: object = None


@dataclass
class Study:
    root: Path
    participants: list
    sources: dict
    themes: list
    research_questions: dict = field(default_factory=dict)
    recommendations: list = field(default_factory=list)
    ledger: dict = field(default_factory=dict)

    @property
    def analyzed_participants(self):
        """Participants represented by at least one registered source."""
        return [p for p in self.participants if any(s.participant == p for s in self.sources.values())]

    def theme_ids(self):
        return {t["id"] for t in self.themes if isinstance(t, dict) and isinstance(t.get("id"), str)}


def _not_found_hint(quote, text, normalize, allow_brackets):
    if not normalize and find_quote(quote, text, normalize=True, allow_brackets=allow_brackets):
        return " It matches once quote marks and whitespace are normalized: copy the source text exactly or rerun with --normalize."
    line, ratio = closest_line(quote, text)
    if line and ratio >= 0.6:
        return f" Closest source line is {line} ({ratio:.0%} of characters align)."
    return ""


def load_sources(manifest, root, findings):
    participants = manifest.get("participants")
    if not isinstance(participants, list) or not all(
        isinstance(p, str) and PARTICIPANT_RE.fullmatch(p) for p in participants
    ):
        findings.error("participants must be a list of P-codes such as P1.")
        participants = []
    if len(participants) != len(set(participants)):
        findings.error("Duplicate participant IDs.")
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        findings.error("sources must be a list.")
        sources = []
    if not sources:
        findings.error("At least one research source is required for analysis.")

    known, paths = {}, set()
    for index, entry in enumerate(sources, 1):
        prefix = f"Source {index}"
        if not isinstance(entry, dict):
            findings.error(f"{prefix}: expected an object.")
            continue
        sid = entry.get("id")
        if not isinstance(sid, str) or not sid.strip() or sid in known:
            findings.error(f"{prefix}: missing or duplicate source ID.")
            continue
        source = known[sid] = Source(sid, entry.get("participant_id"))
        if source.participant not in participants:
            findings.error(f"{sid}: unknown participant ID.")
        if not isinstance(entry.get("session_id"), str) or not entry["session_id"].strip():
            findings.error(f"{sid}: missing session ID.")
        rel = entry.get("path")
        if not isinstance(rel, str) or not rel.strip():
            findings.error(f"{sid}: missing source path.")
            continue
        try:
            path = resolve_inside(root, rel)
        except ValueError:
            findings.error(f"{sid}: source path must stay inside the study folder.")
            continue
        if path in paths:
            findings.error(f"{sid}: duplicate source path.")
        paths.add(path)
        try:
            current_hash = digest(path)
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.error(f"{sid}: cannot read UTF-8 source: {exc}")
            continue
        expected = entry.get("sha256")
        if not isinstance(expected, str) or not HASH_RE.fullmatch(expected):
            findings.error(f"{sid}: invalid source hash.")
        elif expected != current_hash:
            findings.error(f"{sid}: source hash drift.")
        source.path, source.hash, source.text = path, current_hash, text

    for participant in participants:
        if not any(s.participant == participant for s in known.values()):
            findings.warn(f"{participant}: listed without any source; exclude from analyzed-participant counts.")
    return participants, known


def _check_excerpt(prefix, sid, source, item, field_name, normalize, findings):
    """Locate item[field_name] in the source; return the matches."""
    quote = item.get(field_name)
    allow_brackets = field_name == "display_quote"
    matches = find_quote(quote, source.text, normalize=normalize, allow_brackets=allow_brackets)
    if not matches:
        label = "excerpt" if field_name == "quote" else "display_quote"
        findings.error(f"{prefix}: {label} not found in {sid}." + _not_found_hint(quote, source.text, normalize, allow_brackets))
        return []
    if all(m.edited and m.multiline(source.text) for m in matches):
        findings.warn(f"{prefix}: edited {field_name} from {sid} spans several lines; confirm it is one utterance.")
    return matches


def check_themes(study, normalize, findings):
    themes = study.themes
    participants = study.participants
    seen = set()
    for index, theme in enumerate(themes, 1):
        prefix = f"Theme {index}"
        if not isinstance(theme, dict):
            findings.error(f"{prefix}: expected an object.")
            continue
        tid = theme.get("id")
        if not isinstance(tid, str) or not tid.strip() or tid in seen:
            findings.error(f"{prefix}: missing or duplicate theme ID.")
        else:
            seen.add(tid)
            prefix = tid
        for name in ("claim", "counter_evidence"):
            if not isinstance(theme.get(name), str) or not theme[name].strip():
                findings.error(f"{prefix}: missing {name}.")
        claimed = theme.get("supporting_participants")
        if not isinstance(claimed, list) or not all(isinstance(p, str) for p in claimed):
            findings.error(f"{prefix}: supporting_participants must be a list of IDs.")
            claimed = []
        if len(set(claimed)) != len(claimed):
            findings.error(f"{prefix}: duplicate supporting participant.")

        if study.research_questions:
            linked = theme.get("research_questions", [])
            if not isinstance(linked, list) or not all(isinstance(r, str) for r in linked):
                findings.error(f"{prefix}: research_questions must be a list of IDs.")
                linked = []
            for rq in linked:
                if rq not in study.research_questions:
                    findings.error(f"{prefix}: unknown research question {rq}.")
            if not linked:
                findings.warn(f"{prefix}: not linked to a research question; label it as an unexpected finding if intended.")

        evidence = theme.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            findings.error(f"{prefix}: evidence must be a nonempty list.")
            evidence = []
        supported = set()
        for item in evidence:
            if not isinstance(item, dict):
                findings.error(f"{prefix}: evidence item must be an object.")
                continue
            sid = item.get("source_id")
            if not isinstance(sid, str) or sid not in study.sources:
                findings.error(f"{prefix}: evidence references an unknown source.")
                continue
            source = study.sources[sid]
            if item.get("source_sha256") != source.hash or source.hash is None:
                findings.error(f"{prefix}: evidence source hash drift for {sid}.")
            for name in ("locator", "quote"):
                if not isinstance(item.get(name), str) or not item[name].strip():
                    findings.error(f"{prefix}: missing evidence {name}.")
            if source.text is not None and isinstance(item.get("quote"), str) and item["quote"].strip():
                matches = _check_excerpt(prefix, sid, source, item, "quote", normalize, findings)
                if matches and isinstance(item.get("locator"), str) and item["locator"].strip():
                    status, detail = locators.check(item["locator"], source.text, matches)
                    if status == "mismatch":
                        findings.error(f"{prefix}: {sid} {detail}.")
                    elif status == "unchecked":
                        findings.warn(f"{prefix}: {sid} {detail}.")
            display = item.get("display_quote")
            if display is not None:
                if not isinstance(display, str) or not display.strip():
                    findings.error(f"{prefix}: display_quote must be nonempty text when present.")
                elif source.text is not None:
                    _check_excerpt(prefix, sid, source, item, "display_quote", normalize, findings)
                    if len(SENTENCE_RE.findall(display.strip())) > 3:
                        findings.warn(f"{prefix}: display_quote from {sid} is longer than three sentences.")
            polarity = item.get("polarity")
            if polarity not in POLARITIES:
                findings.error(f"{prefix}: invalid evidence polarity.")
            elif polarity == "support" and source.participant in participants:
                supported.add(source.participant)
        if not supported:
            findings.error(f"{prefix}: no supporting evidence.")
        if set(claimed) != supported:
            findings.error(f"{prefix}: supporting participant IDs do not match evidence.")
        elif len(supported) == 1:
            findings.warn(f"{prefix}: supported by one participant; report it as a weak signal.")


def load_research_questions(ledger, findings):
    entries = ledger.get("research_questions", [])
    questions = {}
    if not isinstance(entries, list):
        findings.error("research_questions must be a list.")
        return questions
    for index, entry in enumerate(entries, 1):
        rid = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(rid, str) or not rid.strip() or rid in questions:
            findings.error(f"Research question {index}: missing or duplicate ID.")
            continue
        if not isinstance(entry.get("question"), str) or not entry["question"].strip():
            findings.error(f"{rid}: missing question text.")
        questions[rid] = entry
    return questions


def check_coverage(study, findings):
    for rid in study.research_questions:
        if not any(isinstance(t, dict) and rid in (t.get("research_questions") or []) for t in study.themes):
            findings.warn(f"{rid}: no theme addresses this research question; report it as a gap.")
    entries = study.ledger.get("recommendations", [])
    if not isinstance(entries, list):
        findings.error("recommendations must be a list.")
        return
    themes, seen = study.theme_ids(), set()
    for index, entry in enumerate(entries, 1):
        rid = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(rid, str) or not rid.strip() or rid in seen:
            findings.error(f"Recommendation {index}: missing or duplicate ID.")
            continue
        seen.add(rid)
        if not isinstance(entry.get("proposal"), str) or not entry["proposal"].strip():
            findings.error(f"{rid}: missing proposal text.")
        linked = entry.get("theme_ids")
        if not isinstance(linked, list) or not linked:
            findings.error(f"{rid}: a recommendation must name the theme IDs it rests on.")
            continue
        for tid in linked:
            if tid not in themes:
                findings.error(f"{rid}: references unknown theme {tid}.")
    study.recommendations = entries


def load_study(manifest_path, ledger_path, findings, normalize=False):
    """Load and check the study; return a Study, or None when JSON is unreadable."""
    manifest_path, ledger_path = Path(manifest_path), Path(ledger_path)
    try:
        manifest = load_json(manifest_path)
        ledger = load_json(ledger_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        findings.error(f"Cannot read JSON input: {exc}")
        return None
    if not isinstance(manifest, dict) or not isinstance(ledger, dict):
        findings.error("Manifest and ledger must be JSON objects.")
        return None
    themes = ledger.get("themes")
    if not isinstance(themes, list):
        findings.error("themes must be a list.")
        themes = []

    root = manifest_path.resolve().parent
    participants, sources = load_sources(manifest, root, findings)

    snapshot = ledger.get("source_snapshot")
    if not isinstance(snapshot, dict):
        findings.error("source_snapshot must be an object mapping all source IDs to their analysis-time hashes.")
    else:
        if set(snapshot) != set(sources):
            findings.error("source snapshot IDs differ from the current manifest.")
        for sid in set(snapshot).intersection(sources):
            if snapshot[sid] != sources[sid].hash or sources[sid].hash is None:
                findings.error(f"{sid}: source snapshot hash drift.")

    study = Study(root, participants, sources, themes, ledger=ledger)
    study.research_questions = load_research_questions(ledger, findings)
    check_themes(study, normalize, findings)
    check_coverage(study, findings)
    return study


def verify(manifest_path, ledger_path, normalize=False):
    findings = Findings()
    load_study(manifest_path, ledger_path, findings, normalize=normalize)
    return findings
