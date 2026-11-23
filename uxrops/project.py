"""Artifact dependency tracking for a study folder (uxr-project.json).

Each artifact lists its files (`paths`, files or folders), the artifacts it is built from
(`inputs`), and a researcher-declared `status`. `record` stores the hashes of the
artifact's own files and of all its input files at review time. `status` recomputes
them and reports, for each artifact:

  ok          files and inputs match what was recorded
  planned     declared planned and not yet recorded
  unrecorded  files exist but were never recorded
  missing     a declared path does not exist
  modified    the artifact's own files changed since it was recorded
  stale       an input file changed since it was recorded, or an input is not ok
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .common import atomic_write_text, digest, dump_json, load_json, resolve_inside

PROJECT_FILE = "uxr-project.json"
DECLARED = ("planned", "in progress", "review needed", "reviewed", "stale")
HEALTHY = ("ok", "planned")


class ProjectError(Exception):
    pass


def load_project(path):
    path = Path(path)
    if path.is_dir():
        path = path / PROJECT_FILE
    try:
        data = load_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProjectError(f"Cannot read {path}: {exc}") from exc
    artifacts = data.get("artifacts") if isinstance(data, dict) else None
    if not isinstance(artifacts, dict):
        raise ProjectError(f"{path}: 'artifacts' must be an object keyed by artifact ID.")
    for aid, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            raise ProjectError(f"{aid}: expected an object.")
        if not isinstance(artifact.get("paths", []), list) or not isinstance(artifact.get("inputs", []), list):
            raise ProjectError(f"{aid}: 'paths' and 'inputs' must be lists.")
        if artifact.get("status", "planned") not in DECLARED:
            raise ProjectError(f"{aid}: status must be one of {', '.join(DECLARED)}.")
        for dep in artifact.get("inputs", []):
            if dep not in artifacts:
                raise ProjectError(f"{aid}: unknown input artifact '{dep}'.")
    _check_cycles(artifacts)
    return path, data


def _check_cycles(artifacts):
    state = {}

    def visit(aid, trail):
        if state.get(aid) == "done":
            return
        if state.get(aid) == "active":
            raise ProjectError("Dependency cycle: " + " -> ".join(trail + [aid]))
        state[aid] = "active"
        for dep in artifacts[aid].get("inputs", []):
            visit(dep, trail + [aid])
        state[aid] = "done"

    for aid in artifacts:
        visit(aid, [])


def artifact_files(root, artifact):
    """Map of relative path -> sha256 for an artifact's files (folders expand recursively).

    Returns (files, missing_paths).
    """
    files, missing = {}, []
    for rel in artifact.get("paths", []):
        try:
            path = resolve_inside(root, rel)
        except ValueError as exc:
            raise ProjectError(f"{rel}: {exc}") from exc
        if path.is_dir():
            for child in sorted(p for p in path.rglob("*") if p.is_file() and not p.name.startswith(".")):
                files[child.relative_to(root).as_posix()] = digest(child)
        elif path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path)
        else:
            missing.append(rel)
    return files, missing


def _diff(recorded, current):
    changed = sorted(p for p in set(recorded) | set(current) if recorded.get(p) != current.get(p))
    return changed


def compute_status(project_path, data):
    root = Path(project_path).resolve().parent
    artifacts = data["artifacts"]
    current, missing = {}, {}
    for aid, artifact in artifacts.items():
        current[aid], missing[aid] = artifact_files(root, artifact)

    results = {}

    def evaluate(aid):
        if aid in results:
            return results[aid]
        artifact = artifacts[aid]
        declared = artifact.get("status", "planned")
        recorded = artifact.get("recorded")
        reasons = []
        for dep in artifact.get("inputs", []):
            evaluate(dep)
        if recorded is None:
            if declared == "planned" and not current[aid]:
                state = "planned"
            elif missing[aid]:
                state, reasons = "missing", [f"missing {', '.join(missing[aid])}"]
            else:
                state, reasons = "unrecorded", ["never recorded; review it, then run record"]
        elif missing[aid]:
            state, reasons = "missing", [f"missing {', '.join(missing[aid])}"]
        else:
            own = _diff(recorded.get("files", {}), current[aid])
            inputs_now = {}
            for dep in artifact.get("inputs", []):
                inputs_now.update(current[dep])
            changed_inputs = _diff(recorded.get("inputs", {}), inputs_now)
            bad_inputs = [d for d in artifact.get("inputs", []) if results[d]["state"] not in HEALTHY]
            if own:
                state, reasons = "modified", [f"changed since recorded: {', '.join(own[:5])}"]
            elif changed_inputs or bad_inputs:
                state = "stale"
                if changed_inputs:
                    reasons.append(f"input changed: {', '.join(changed_inputs[:5])}")
                if bad_inputs:
                    reasons.append("input not ok: " + ", ".join(f"{d} ({results[d]['state']})" for d in bad_inputs))
            else:
                state = "ok"
        if state == "ok" and declared in ("planned", "in progress", "review needed", "stale"):
            reasons.append(f"declared '{declared}'")
        if state not in HEALTHY and declared == "reviewed":
            reasons.append("declared 'reviewed' but needs re-review")
        results[aid] = {"artifact": aid, "declared": declared, "state": state, "reasons": reasons,
                        "recorded_at": (recorded or {}).get("at")}
        return results[aid]

    for aid in artifacts:
        evaluate(aid)
    return [results[aid] for aid in artifacts], current


def record(project_path, data, aid, status=None, allow_stale_inputs=False, now=None):
    artifacts = data["artifacts"]
    if aid not in artifacts:
        raise ProjectError(f"Unknown artifact '{aid}'. Known: {', '.join(artifacts)}.")
    results, current = compute_status(project_path, data)
    by_id = {r["artifact"]: r for r in results}
    artifact = artifacts[aid]
    if by_id[aid]["state"] == "missing":
        raise ProjectError(f"{aid}: {'; '.join(by_id[aid]['reasons'])}.")
    if not current[aid]:
        raise ProjectError(f"{aid}: no files to record.")
    bad = [d for d in artifact.get("inputs", []) if by_id[d]["state"] not in ("ok",)]
    if bad and not allow_stale_inputs:
        detail = ", ".join(f"{d} ({by_id[d]['state']})" for d in bad)
        raise ProjectError(f"{aid}: inputs are not ok: {detail}. Review and record them first, or pass --allow-stale-inputs.")
    inputs = {}
    for dep in artifact.get("inputs", []):
        inputs.update(current[dep])
    stamp = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    artifact["recorded"] = {"at": stamp, "files": current[aid], "inputs": inputs}
    if status:
        if status not in DECLARED:
            raise ProjectError(f"status must be one of {', '.join(DECLARED)}.")
        artifact["status"] = status
    atomic_write_text(project_path, dump_json(data))
    return artifact


def mark_stale(project_path, data, results):
    """Set declared status to 'stale' for artifacts whose computed state is stale or modified."""
    changed = []
    for result in results:
        artifact = data["artifacts"][result["artifact"]]
        if result["state"] in ("stale", "modified") and artifact.get("status") != "stale":
            artifact["status"] = "stale"
            changed.append(result["artifact"])
    if changed:
        atomic_write_text(project_path, dump_json(data))
    return changed


def format_table(results, markdown=False):
    rows = [(r["artifact"], r["declared"], r["state"], "; ".join(r["reasons"])) for r in results]
    if markdown:
        lines = ["| Artifact | Declared | Computed | Notes |", "|---|---|---|---|"]
        lines += [f"| {a} | {d} | {s} | {n} |" for a, d, s, n in rows]
        return "\n".join(lines)
    widths = [max(len(str(row[i])) for row in rows + [("artifact", "declared", "computed", "")]) for i in range(3)]
    header = ("artifact", "declared", "computed", "notes")
    lines = []
    for row in [header] + rows:
        lines.append("  ".join(str(row[i]).ljust(widths[i]) for i in range(3)) + "  " + row[3])
    return "\n".join(lines)
