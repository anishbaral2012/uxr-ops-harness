#!/usr/bin/env python3
"""Check a pseudonymous study manifest and its source-linked evidence ledger."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(manifest_path, ledger_path):
    errors = []

    def fail(message):
        errors.append(message)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"Cannot read JSON input: {exc}"]
    if not isinstance(manifest, dict) or not isinstance(ledger, dict):
        return ["Manifest and ledger must be JSON objects."]
    participants = manifest.get("participants")
    sources = manifest.get("sources")
    themes = ledger.get("themes")
    if not isinstance(participants, list) or not all(
        isinstance(p, str) and re.fullmatch(r"P[1-9][0-9]*", p) for p in participants
    ):
        fail("participants must be a list of P-codes such as P1.")
        participants = []
    if len(participants) != len(set(participants)):
        fail("Duplicate participant IDs.")
    if not isinstance(sources, list):
        fail("sources must be a list.")
        sources = []
    if not sources:
        fail("At least one research source is required for analysis.")
    if not isinstance(themes, list):
        fail("themes must be a list.")
        themes = []

    root = manifest_path.resolve().parent
    known = {}
    paths = set()
    for index, source in enumerate(sources, 1):
        prefix = f"Source {index}"
        if not isinstance(source, dict):
            fail(f"{prefix}: expected an object.")
            continue
        sid = source.get("id")
        if not isinstance(sid, str) or not sid.strip() or sid in known:
            fail(f"{prefix}: missing or duplicate source ID.")
            continue
        known[sid] = {"participant": source.get("participant_id"), "hash": None, "text": None}
        if source.get("participant_id") not in participants:
            fail(f"{sid}: unknown participant ID.")
        if not isinstance(source.get("session_id"), str) or not source["session_id"].strip():
            fail(f"{sid}: missing session ID.")
        rel = source.get("path")
        if not isinstance(rel, str) or not rel.strip():
            fail(f"{sid}: missing source path.")
            continue
        try:
            path = (root / rel).resolve()
            if Path(rel).is_absolute() or not path.is_relative_to(root):
                fail(f"{sid}: source path must stay inside the study folder.")
                continue
            if path in paths:
                fail(f"{sid}: duplicate source path.")
            paths.add(path)
            current_hash = digest(path)
            source_text = path.read_text(encoding="utf-8")
        except (OSError, ValueError, UnicodeError) as exc:
            fail(f"{sid}: cannot read UTF-8 source: {exc}")
            continue
        expected = source.get("sha256")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            fail(f"{sid}: invalid source hash.")
        elif expected != current_hash:
            fail(f"{sid}: source hash drift.")
        known[sid]["hash"] = current_hash
        known[sid]["text"] = source_text

    snapshot = ledger.get("source_snapshot")
    if not isinstance(snapshot, dict):
        fail("source_snapshot must be an object mapping all source IDs to their analysis-time hashes.")
    else:
        if set(snapshot) != set(known):
            fail("source snapshot IDs differ from the current manifest.")
        for sid in set(snapshot).intersection(known):
            if snapshot[sid] != known[sid]["hash"] or known[sid]["hash"] is None:
                fail(f"{sid}: source snapshot hash drift.")

    seen_themes = set()
    for index, theme in enumerate(themes, 1):
        prefix = f"Theme {index}"
        if not isinstance(theme, dict):
            fail(f"{prefix}: expected an object.")
            continue
        tid = theme.get("id")
        if not isinstance(tid, str) or not tid.strip() or tid in seen_themes:
            fail(f"{prefix}: missing or duplicate theme ID.")
        else:
            seen_themes.add(tid)
            prefix = tid
        for field in ("claim", "counter_evidence"):
            if not isinstance(theme.get(field), str) or not theme[field].strip():
                fail(f"{prefix}: missing {field}.")
        claimed = theme.get("supporting_participants")
        if not isinstance(claimed, list) or not all(isinstance(p, str) for p in claimed):
            fail(f"{prefix}: supporting_participants must be a list of IDs.")
            claimed = []
        if len(set(claimed)) != len(claimed):
            fail(f"{prefix}: duplicate supporting participant.")
        evidence = theme.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            fail(f"{prefix}: evidence must be a nonempty list.")
            evidence = []
        supported = set()
        for item in evidence:
            if not isinstance(item, dict):
                fail(f"{prefix}: evidence item must be an object.")
                continue
            sid = item.get("source_id")
            if not isinstance(sid, str) or sid not in known:
                fail(f"{prefix}: evidence references an unknown source.")
                continue
            source = known[sid]
            if item.get("source_sha256") != source["hash"] or source["hash"] is None:
                fail(f"{prefix}: evidence source hash drift for {sid}.")
            for field in ("locator", "quote"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    fail(f"{prefix}: missing evidence {field}.")
            quote = item.get("quote")
            if isinstance(quote, str) and quote.strip() and source["text"] is not None and quote not in source["text"]:
                fail(f"{prefix}: excerpt not found in {sid}.")
            polarity = item.get("polarity")
            if polarity not in ("support", "contradict", "context"):
                fail(f"{prefix}: invalid evidence polarity.")
            elif polarity == "support" and source["participant"] in participants:
                supported.add(source["participant"])
        if not supported:
            fail(f"{prefix}: no supporting evidence.")
        if set(claimed) != supported:
            fail(f"{prefix}: supporting participant IDs do not match evidence.")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hash_parser = sub.add_parser("hash", help="Print SHA-256 for a source file")
    hash_parser.add_argument("source", type=Path)
    verify_parser = sub.add_parser("verify", help="Verify manifest and evidence ledger")
    verify_parser.add_argument("manifest", type=Path)
    verify_parser.add_argument("ledger", type=Path)
    args = parser.parse_args(argv)
    if args.command == "hash":
        try:
            print(digest(args.source))
            return 0
        except OSError as exc:
            print(f"Cannot read source: {exc}", file=sys.stderr)
            return 1
    errors = verify(args.manifest, args.ledger)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: mechanical checks only; researcher review remains required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
