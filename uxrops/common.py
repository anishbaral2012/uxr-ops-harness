"""Shared helpers: hashing, JSON loading, safe paths, atomic writes, findings."""

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

PASS_MESSAGE = "PASS: mechanical checks only; researcher review remains required."


def digest(path):
    """SHA-256 of the exact bytes on disk."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    # utf-8-sig tolerates the byte-order mark some Windows editors write.
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def resolve_inside(root, rel):
    """Resolve `rel` against `root`; raise ValueError if it escapes `root`."""
    root = Path(root).resolve()
    if not isinstance(rel, str) or not rel.strip():
        raise ValueError("missing path")
    if Path(rel).is_absolute():
        raise ValueError("path must be relative to the study folder")
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError("path must stay inside the study folder")
    return path


def atomic_write_text(path, text):
    """Write to a temporary file in the same folder, then replace the target."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def dump_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


@dataclass
class Findings:
    """Errors fail a check; warnings need researcher attention but do not fail by default."""

    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def error(self, message):
        self.errors.append(message)

    def warn(self, message):
        self.warnings.append(message)

    def extend(self, other):
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def ok(self, strict=False):
        return not self.errors and not (strict and self.warnings)

    def as_dict(self, strict=False):
        data = asdict(self)
        data["ok"] = self.ok(strict)
        data["strict"] = strict
        return data


def print_findings(findings, fmt="text", strict=False, pass_message=PASS_MESSAGE):
    """Print findings and return the process exit code (0 pass, 1 fail)."""
    if fmt == "json":
        print(json.dumps(findings.as_dict(strict), indent=2, ensure_ascii=False))
    else:
        for message in findings.errors:
            print(f"FAIL: {message}")
        for message in findings.warnings:
            print(f"WARN: {message}")
        if findings.ok(strict):
            suffix = f" ({len(findings.warnings)} warning(s) to review)" if findings.warnings else ""
            print(pass_message + suffix)
        elif strict and not findings.errors:
            print("FAIL: warnings are treated as failures because --strict was given.")
    return 0 if findings.ok(strict) else 1
