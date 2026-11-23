"""uxrops command line.

Exit codes: 0 pass, 1 check failure, 2 usage or input error.
"""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .common import Findings, digest, load_json, print_findings
from .documents import load_document
from .project import PROJECT_FILE, ProjectError, compute_status, format_table, load_project, mark_stale, record
from .report import check_documents
from .scaffold import init_study
from .verify import load_study, verify


def _study_paths(args):
    folder = Path(args.study)
    if folder.is_dir():
        return folder / "study-manifest.json", folder / "evidence-ledger.json"
    raise SystemExit(f"Not a study folder: {folder}")


def cmd_hash(args):
    code = 0
    for source in args.files:
        try:
            value = digest(source)
        except OSError as exc:
            print(f"Cannot read source: {exc}", file=sys.stderr)
            code = 1
            continue
        print(value if len(args.files) == 1 else f"{value}  {source}")
    return code


def cmd_verify(args):
    if args.ledger is None:
        manifest, ledger = _study_paths(argparse.Namespace(study=args.manifest))
    else:
        manifest, ledger = Path(args.manifest), Path(args.ledger)
    findings = verify(manifest, ledger, normalize=args.normalize)
    return print_findings(findings, args.format, args.strict)


def cmd_check_report(args):
    manifest = Path(args.manifest) if args.manifest else Path(args.study) / "study-manifest.json"
    ledger = Path(args.ledger) if args.ledger else Path(args.study) / "evidence-ledger.json"
    findings = Findings()
    study = load_study(manifest, ledger, findings, normalize=args.normalize)
    if study is None:
        return print_findings(findings, args.format, args.strict)
    style = {}
    project = Path(args.project) if args.project else manifest.resolve().parent / PROJECT_FILE
    if project.is_file():
        try:
            style = load_json(project).get("style") or {}
        except (OSError, ValueError):
            findings.warn(f"Cannot read style settings from {project}.")
    documents = []
    for path in args.documents:
        try:
            documents.append(load_document(path))
        except (OSError, ValueError, KeyError) as exc:
            findings.error(f"Cannot read document {path}: {exc}")
    check_documents(study, documents, findings, min_words=args.min_words, style=style)
    return print_findings(findings, args.format, args.strict)


def cmd_status(args):
    try:
        path, data = load_project(args.project)
        results, _ = compute_status(path, data)
        changed = mark_stale(path, data, results) if args.mark_stale else []
    except ProjectError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps({"project": str(path), "artifacts": results, "marked_stale": changed}, indent=2))
    else:
        print(format_table(results, markdown=args.format == "markdown"))
        if changed:
            print(f"\nMarked stale in {path.name}: {', '.join(changed)}")
    return 0 if all(r["state"] in ("ok", "planned") for r in results) else 1


def cmd_record(args):
    try:
        path, data = load_project(args.project)
        artifact = record(path, data, args.artifact, status=args.status, allow_stale_inputs=args.allow_stale_inputs)
    except ProjectError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Recorded {args.artifact}: {len(artifact['recorded']['files'])} file(s), "
          f"{len(artifact['recorded']['inputs'])} input file(s), status '{artifact.get('status')}'.")
    return 0


def cmd_init(args):
    created, skipped = init_study(args.folder, study=args.name, method=args.method)
    for name in created:
        print(f"created  {name}")
    for name in skipped:
        print(f"kept     {name} (already exists)")
    print("Store real study folders in approved restricted storage; this command sets no access control.")
    return 0


def cmd_docx(args):
    from .markdown_docx import convert

    try:
        convert(args.input, args.output)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {Path(args.output).resolve()}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="uxrops", description="Mechanical checks and tools for UXR Ops studies.")
    parser.add_argument("--version", action="version", version=f"uxrops {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def output_options(p):
        p.add_argument("--format", choices=("text", "json"), default="text")
        p.add_argument("--strict", action="store_true", help="treat warnings as failures")
        p.add_argument("--normalize", action="store_true",
                       help="ignore curly vs straight quotes, ellipsis form and whitespace when matching excerpts")

    p = sub.add_parser("init", help="create a study folder skeleton (never overwrites)")
    p.add_argument("folder")
    p.add_argument("--name", help="study name (default: folder name)")
    p.add_argument("--method", default="To be decided")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("hash", help="print SHA-256 of source files")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_hash)

    p = sub.add_parser("verify", help="verify manifest and evidence ledger (pass a study folder or both files)")
    p.add_argument("manifest", help="study-manifest.json, or the study folder")
    p.add_argument("ledger", nargs="?")
    output_options(p)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("check-report", help="check analysis, Word or PowerPoint outputs against the ledger")
    p.add_argument("documents", nargs="+", help=".md, .txt, .docx or .pptx files")
    p.add_argument("--study", default=".", help="study folder (default: current folder)")
    p.add_argument("--manifest")
    p.add_argument("--ledger")
    p.add_argument("--project", help=f"{PROJECT_FILE} for style settings (default: next to the manifest)")
    p.add_argument("--min-words", type=int, default=4, help="shortest quotation to check (default 4 words)")
    output_options(p)
    p.set_defaults(func=cmd_check_report)

    p = sub.add_parser("status", help="show artifact freshness from uxr-project.json")
    p.add_argument("project", nargs="?", default=".", help=f"{PROJECT_FILE} or the study folder")
    p.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    p.add_argument("--mark-stale", action="store_true", help="set declared status to 'stale' where needed")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("record", help="record current hashes after reviewing an artifact")
    p.add_argument("artifact")
    p.add_argument("--project", default=".", help=f"{PROJECT_FILE} or the study folder")
    p.add_argument("--status", help="also set the declared status, e.g. reviewed")
    p.add_argument("--allow-stale-inputs", action="store_true")
    p.set_defaults(func=cmd_record)

    p = sub.add_parser("docx", help="convert Markdown to Word (needs python-docx)")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(func=cmd_docx)
    return parser


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")  # curly quotes on legacy Windows consoles
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
