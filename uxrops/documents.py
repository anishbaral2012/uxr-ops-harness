"""Extract text from report documents: Markdown/plain text, Word (.docx) and PowerPoint (.pptx).

Only the Python standard library is used, so checks run without python-docx or Node.
"""

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")


@dataclass
class Section:
    title: str
    text: str


@dataclass
class Document:
    name: str
    sections: list
    extra_text: str = ""  # speaker notes and similar: scanned for IDs, not for quotes
    kind: str = "text"

    @property
    def text(self):
        return "\n".join(s.text for s in self.sections) + "\n" + self.extra_text


def _xml_paragraphs(data, paragraph_tag, text_tag):
    root = ElementTree.fromstring(data)
    paragraphs = []
    for paragraph in root.iter(paragraph_tag):
        paragraphs.append((paragraph, "".join(node.text or "" for node in paragraph.iter(text_tag))))
    return paragraphs


def _numbered(names, pattern):
    found = []
    for name in names:
        match = re.fullmatch(pattern, name)
        if match:
            found.append((int(match.group(1)), name))
    return [name for _, name in sorted(found)]


def load_pptx(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        sections = []
        for number, name in enumerate(_numbered(names, r"ppt/slides/slide(\d+)\.xml"), 1):
            lines = [text for _, text in _xml_paragraphs(archive.read(name), A_NS + "p", A_NS + "t")]
            sections.append(Section(f"slide {number}", "\n".join(line for line in lines if line.strip())))
        notes = []
        for name in _numbered(names, r"ppt/notesSlides/notesSlide(\d+)\.xml"):
            notes.extend(text for _, text in _xml_paragraphs(archive.read(name), A_NS + "p", A_NS + "t"))
    return Document(Path(path).name, sections, "\n".join(notes), kind="pptx")


def load_docx(path):
    with zipfile.ZipFile(path) as archive:
        data = archive.read("word/document.xml")
    sections = [Section("start", "")]
    for paragraph, text in _xml_paragraphs(data, W_NS + "p", W_NS + "t"):
        style = paragraph.find(f"{W_NS}pPr/{W_NS}pStyle")
        value = style.get(W_NS + "val", "") if style is not None else ""
        if value.lower().startswith("heading") or value.lower() == "title":
            sections.append(Section(text, text))
        elif text.strip():
            sections[-1].text += text + "\n"
    return Document(Path(path).name, [s for s in sections if s.text.strip()], kind="docx")


def load_markdown(path):
    sections = [Section("start", "")]
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            sections.append(Section(heading.group(1).strip(), line + "\n"))
        else:
            sections[-1].text += line + "\n"
    return Document(Path(path).name, [s for s in sections if s.text.strip()], kind="markdown")


def load_document(path):
    suffix = Path(path).suffix.lower()
    if suffix == ".pptx":
        return load_pptx(path)
    if suffix == ".docx":
        return load_docx(path)
    return load_markdown(path)
