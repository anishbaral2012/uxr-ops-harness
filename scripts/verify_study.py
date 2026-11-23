#!/usr/bin/env python3
"""Compatibility entry point: `verify_study.py hash|verify ...` now runs `uxrops`.

Prefer `python scripts/uxrops.py verify <study-folder>`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uxrops import verify as _verify  # noqa: E402
from uxrops.cli import main  # noqa: E402
from uxrops.common import digest  # noqa: E402,F401


def verify(manifest_path, ledger_path, normalize=False):
    """Return the list of failure messages (warnings are not included)."""
    return _verify.verify(Path(manifest_path), Path(ledger_path), normalize=normalize).errors


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
