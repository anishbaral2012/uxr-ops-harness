"""Create a study folder skeleton without overwriting anything."""

from datetime import date
from pathlib import Path

from .common import dump_json
from .project import PROJECT_FILE

GITATTRIBUTES = """\
# Keep every byte exactly as written. Line-ending conversion would change file
# hashes and make the manifest and evidence ledger report drift after checkout.
* -text
"""


def default_project(study, method):
    def artifact(paths, inputs):
        return {"paths": paths, "inputs": inputs, "status": "planned"}

    return {
        "schema_version": 1,
        "study": study,
        "method": method,
        "created": date.today().isoformat(),
        "source_snapshot_date": None,
        "style": {"avoid_mid_sentence_dashes": False},
        "decisions": [],
        "open_questions": [],
        "artifacts": {
            "brief": artifact(["brief.md"], []),
            "plan": artifact(["plan.md"], ["brief"]),
            "guide": artifact(["guide.md"], ["plan"]),
            "sources": artifact(["transcripts/"], []),
            "evidence": artifact(["study-manifest.json", "evidence-ledger.json"], ["plan", "sources"]),
            "analysis": artifact(["analysis.md"], ["plan", "evidence"]),
            "deck": artifact(["deck-content.json", "research-report.pptx"], ["plan", "analysis", "evidence"]),
        },
    }


def init_study(folder, study=None, method="To be decided"):
    """Create missing skeleton files; return (created, skipped) relative paths."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "transcripts").mkdir(exist_ok=True)
    files = {
        PROJECT_FILE: dump_json(default_project(study or folder.resolve().name, method)),
        "study-manifest.json": dump_json({"participants": [], "sources": []}),
        "evidence-ledger.json": dump_json(
            {"source_snapshot": {}, "research_questions": [], "themes": [], "recommendations": []}
        ),
        ".gitattributes": GITATTRIBUTES,
    }
    created, skipped = [], []
    for name, content in files.items():
        path = folder / name
        try:
            with open(path, "x", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
            created.append(name)
        except FileExistsError:
            skipped.append(name)
    return created, skipped
