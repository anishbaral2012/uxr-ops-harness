#!/usr/bin/env python3
"""
Convert a UXR plan or interview-guide Markdown file to a .docx.

Usage (from anywhere):
    python <harness>/scripts/uxrops.py docx <input.md> <output.docx>

Requires python-docx. Handles the Markdown subset produced by the stage skills:
    - Headings (#, ##, ###)
    - Blockquotes (> ...)              → italic paragraph
    - Bullets (-, *) with one level of indent → List Bullet / List Bullet 2
    - Numbered lists (1. 2. 3.)        → List Number
    - Pipe tables                       → real Word tables
    - Checkbox lines ([ ] / [x])        → ☐ / ☑ glyphs
    - Inline **bold**, *italic*, `code`, [text](url)
    - Horizontal rule (---)             → centered separator paragraph
"""

import re
import sys


# ---------------------------------------------------------------------------
# Inline markup: bold, italic, code, links — applied to a single line.
# ---------------------------------------------------------------------------

INLINE_RE = re.compile(
    r"(\*\*[^*]+\*\*"          # **bold**
    r"|\*[^*\n]+\*"            # *italic*
    r"|`[^`\n]+`"              # `code`
    r"|\[[^\]]+\]\([^)]+\))",  # [text](url)
)


def _docx():
    """Import python-docx lazily so the rest of uxrops works without it."""
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt
    except ImportError as exc:  # pragma: no cover - exercised only without python-docx
        raise RuntimeError(
            "python-docx is required for Word export: pip install python-docx==1.2.0 "
            "(or run through: uv run --with python-docx==1.2.0 ...)"
        ) from exc
    return Document, WD_ALIGN_PARAGRAPH, Inches, Pt


def add_runs(paragraph, text):
    """Split `text` on inline markers and add styled runs to `paragraph`."""
    for chunk in INLINE_RE.split(text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            run = paragraph.add_run(chunk[2:-2])
            run.bold = True
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            run = paragraph.add_run(chunk[1:-1])
            run.italic = True
        elif chunk.startswith("`") and chunk.endswith("`"):
            run = paragraph.add_run(chunk[1:-1])
            run.font.name = "Consolas"
        elif chunk.startswith("[") and "](" in chunk and chunk.endswith(")"):
            label, _, rest = chunk[1:].partition("](")
            url = rest[:-1]
            run = paragraph.add_run(f"{label} ({url})")
            run.font.color.rgb = None  # keep default; full hyperlink XML is overkill here
        else:
            paragraph.add_run(chunk)


# ---------------------------------------------------------------------------
# Checkbox handling: turn "[ ] text" / "[x] text" into "☐ text" / "☑ text".
# ---------------------------------------------------------------------------

CHECKBOX_RE = re.compile(r"^\[( |x|X)\]\s*(.*)$")


def transform_checkbox(text):
    m = CHECKBOX_RE.match(text)
    if not m:
        return None
    mark = "☑" if m.group(1).lower() == "x" else "☐"
    return f"{mark} {m.group(2)}"


# ---------------------------------------------------------------------------
# Table handling: collect a contiguous run of "| ... |" lines and emit a
# Word table. The second row in markdown tables is the "|---|---|" separator;
# treat it as the header divider.
# ---------------------------------------------------------------------------

def is_table_row(line):
    s = line.strip()
    return s.startswith("|") and s.endswith("|")


def is_table_separator(line):
    cells = parse_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-+:?", cell) for cell in cells)


def parse_table_row(line):
    # Pipes escaped by an odd number of backslashes are cell content.
    text = line.strip()[1:-1]
    cells = []
    cell = []
    for char in text:
        if char == "|":
            backslashes = 0
            for previous in reversed(cell):
                if previous != "\\":
                    break
                backslashes += 1
            if backslashes % 2:
                cell.pop()
                cell.append("|")
            else:
                cells.append("".join(cell).strip())
                cell = []
        else:
            cell.append(char)
    cells.append("".join(cell).strip())
    return cells


def emit_table(doc, rows):
    """rows is a list of lists of cell strings; first is header."""
    if not rows:
        return
    columns = len(rows[0])
    for row_number, row in enumerate(rows, 1):
        if len(row) > columns:
            raise ValueError(
                f"Table row {row_number} has {len(row)} cells; header has {columns}. "
                "Escape literal pipes as \\|."
            )
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Light Grid Accent 1"
    for r_idx, row in enumerate(rows):
        for c_idx, cell_text in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = ""  # clear default empty paragraph text
            p = cell.paragraphs[0]
            add_runs(p, cell_text)
            if r_idx == 0:
                for run in p.runs:
                    run.bold = True
    doc.add_paragraph()  # spacer after table


# ---------------------------------------------------------------------------
# Main converter.
# ---------------------------------------------------------------------------

def add_heading(doc, text, level):
    """Headings keep inline formatting instead of showing literal ** or ` marks."""
    heading = doc.add_heading("", level=level)
    add_runs(heading, text)
    return heading


def convert(md_path, out_path):
    Document, WD_ALIGN_PARAGRAPH, Inches, Pt = _docx()
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    with open(md_path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # Skip YAML frontmatter at the top of the file.
        if i == 0 and line.strip() == "---":
            i += 1
            while i < n and lines[i].strip() != "---":
                i += 1
            i += 1
            continue

        stripped = line.strip()

        # Blank line.
        if not stripped:
            i += 1
            continue

        # Horizontal rule.
        if stripped == "---" or stripped == "***":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run("─" * 30)
            run.font.color.rgb = None
            i += 1
            continue

        # Pipe table: collect contiguous table rows, then emit.
        if is_table_row(line):
            table_lines = []
            while i < n and is_table_row(lines[i]):
                table_lines.append(lines[i])
                i += 1
            rows = [parse_table_row(tl) for tl in table_lines if not is_table_separator(tl)]
            emit_table(doc, rows)
            continue

        # Headings.
        if stripped.startswith("# "):
            add_heading(doc, stripped[2:], 1)
            i += 1
            continue
        if stripped.startswith("## "):
            add_heading(doc, stripped[3:], 2)
            i += 1
            continue
        if stripped.startswith("### "):
            add_heading(doc, stripped[4:], 3)
            i += 1
            continue
        if stripped.startswith("#### "):
            add_heading(doc, stripped[5:], 4)
            i += 1
            continue

        # Blockquote.
        if stripped.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            run_text = stripped[2:]
            # Render blockquote contents as italic, but still parse inline markers.
            # We do this by adding runs and forcing italic on every run.
            add_runs(p, run_text)
            for run in p.runs:
                run.italic = True
            i += 1
            continue

        # Bulleted list (with optional indentation).
        bullet_match = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if bullet_match:
            indent_spaces = len(bullet_match.group(1))
            content = bullet_match.group(2)
            level = 1 + min(indent_spaces // 2, 2)  # cap at List Bullet 3
            style_name = "List Bullet" if level == 1 else f"List Bullet {level}"

            # Checkbox inside bullet.
            cb = transform_checkbox(content)
            if cb is not None:
                content = cb

            p = doc.add_paragraph(style=style_name)
            add_runs(p, content)
            i += 1
            continue

        # Numbered list.
        num_match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if num_match:
            p = doc.add_paragraph(style="List Number")
            add_runs(p, num_match.group(1))
            i += 1
            continue

        # Standalone checkbox line (not in a bullet).
        cb = transform_checkbox(stripped)
        if cb is not None:
            p = doc.add_paragraph()
            add_runs(p, cb)
            i += 1
            continue

        # Plain paragraph.
        p = doc.add_paragraph()
        add_runs(p, line)
        i += 1

    doc.save(out_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python markdown_docx.py <input.md> <output.docx>", file=sys.stderr)
        sys.exit(2)
    convert(sys.argv[1], sys.argv[2])
    print(f"Wrote {sys.argv[2]}")
