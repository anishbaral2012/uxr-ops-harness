import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from uxrops.common import Findings  # noqa: E402
from uxrops.documents import load_document  # noqa: E402
from uxrops.report import check_documents  # noqa: E402
from uxrops.verify import load_study  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "mini-study"
UXROPS = ROOT / "scripts" / "uxrops.py"

SLIDE = """<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:cSld><p:spTree>{shapes}</p:spTree></p:cSld></p:sld>"""
SHAPE = "<p:sp><p:txBody><a:p><a:r><a:t>{}</a:t></a:r></a:p></p:txBody></p:sp>"
DOCX = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{}</w:body></w:document>"""
PARA = '<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t>{text}</w:t></w:r></w:p>'


def write_pptx(path, slides):
    with zipfile.ZipFile(path, "w") as archive:
        for number, texts in enumerate(slides, 1):
            shapes = "".join(SHAPE.format(t) for t in texts)
            archive.writestr(f"ppt/slides/slide{number}.xml", SLIDE.format(shapes=shapes))


def write_docx(path, paragraphs):
    body = "".join(PARA.format(style=style, text=text) for style, text in paragraphs)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", DOCX.format(body))


class ReportCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.study_dir = self.tmp / "study"
        shutil.copytree(FIXTURE, self.study_dir)

    def run_check(self, *docs, style=None):
        findings = Findings()
        study = load_study(self.study_dir / "study-manifest.json", self.study_dir / "evidence-ledger.json", findings)
        check_documents(study, [load_document(d) for d in docs], findings, style=style)
        return findings

    def doc(self, name, text):
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_fixture_analysis_passes(self):
        findings = self.run_check(self.study_dir / "analysis.md")
        self.assertEqual(findings.errors, [])

    def test_quote_not_in_any_source_fails(self):
        doc = self.doc("a.md", "## T1 x\n\n“I never checked my bank app at all.” (P1, S1 line 4)\n## T2 y\n")
        self.assertIn("not found in any registered source", " ".join(self.run_check(doc).errors))

    def test_misattributed_quote_fails(self):
        doc = self.doc("a.md", "## T1 x\n\n\"The clerk printed a receipt right away\" (P1, S1 line 3)\n## T2 y\n")
        errors = " ".join(self.run_check(doc).errors)
        self.assertIn("attributed to S1 but found in S3", errors)
        self.assertIn("attributed to P1 but it comes from P2", errors)

    def test_quote_missing_from_ledger_warns(self):
        doc = self.doc("a.md", "## T1 x\n\n“I saved the receipt email in a folder” (P1, S2 line 2)\n## T2 y\n")
        findings = self.run_check(doc)
        self.assertEqual(findings.errors, [])
        self.assertIn("not recorded in the evidence ledger", " ".join(findings.warnings))

    def test_unknown_ids_fail_and_missing_themes_warn(self):
        doc = self.doc("a.md", "## T1 x\n\nSee T4 and RQ7.\n")
        findings = self.run_check(doc)
        errors = " ".join(findings.errors)
        self.assertIn("theme T4", errors)
        self.assertIn("RQ7", errors)
        self.assertIn("ledger theme T2 does not appear", " ".join(findings.warnings))

    def test_count_mismatch_warns(self):
        doc = self.doc("a.md", "## T1 x\n\nThree of five participants did this.\n## T2 y\n")
        self.assertIn("do not include its 2 supporting", " ".join(self.run_check(doc).warnings))

    def test_style_dash_rule(self):
        doc = self.doc("a.md", "## T1 x\n\nThe flow worked — mostly.\n\n“I wasn't sure — ok”\n## T2 y\n")
        self.assertIn("mid-sentence dashes", " ".join(self.run_check(doc, style={"avoid_mid_sentence_dashes": True}).warnings))
        self.assertNotIn("mid-sentence dashes", " ".join(self.run_check(doc).warnings))

    def test_pptx_quotes_and_attribution(self):
        deck = self.tmp / "deck.pptx"
        write_pptx(deck, [
            ["T1 proof of payment", "“The clerk printed a receipt right away, so I knew it was done.”", "P1, resident, S3 00:02:45", "2 of 2"],
            ["T2 distrust"],
        ])
        errors = " ".join(self.run_check(deck).errors)
        self.assertIn("deck.pptx (slide 1): quotation attributed to P1 but it comes from P2", errors)

    def test_docx_sections(self):
        report = self.tmp / "report.docx"
        write_docx(report, [
            ("Heading1", "T1 Residents looked for proof"),
            ("Normal", "“I wasn't sure the payment went through, so I checked my bank app twice.” P1, S1 line 4"),
            ("Normal", "Two of two participants."),
            ("Heading1", "T2 Distrust"),
        ])
        findings = self.run_check(report)
        self.assertEqual(findings.errors, [])
        self.assertNotIn("do not include", " ".join(findings.warnings))

    def test_cli_reads_style_from_project_file(self):
        (self.study_dir / "uxr-project.json").write_text(
            json.dumps({"artifacts": {}, "style": {"avoid_mid_sentence_dashes": True}}), encoding="utf-8")
        doc = self.doc("a.md", "## T1 x\n\nIt worked — mostly. T2.\n")
        result = subprocess.run(
            [sys.executable, str(UXROPS), "check-report", "--study", str(self.study_dir), str(doc), "--format", "json"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mid-sentence dashes", result.stdout)


if __name__ == "__main__":
    unittest.main()
