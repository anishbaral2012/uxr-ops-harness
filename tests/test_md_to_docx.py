import sys
import tempfile
import unittest
from pathlib import Path

try:
    from docx import Document
except ImportError:
    Document = None

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from uxrops import markdown_docx  # noqa: E402


@unittest.skipIf(Document is None, "python-docx is not installed")
class MarkdownConversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converter = markdown_docx

    def test_escaped_pipe_survives_in_a_table_cell(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "guide.md"
            out = Path(tmp) / "guide.docx"
            source.write_text(
                "| Hypothesis | Questions |\n| --- | --- |\n| A \\| B | Q1 |\n",
                encoding="utf-8",
            )
            self.converter.convert(source, out)
            table = Document(out).tables[0]
            self.assertEqual([cell.text for cell in table.rows[1].cells], ["A | B", "Q1"])

    def test_extra_columns_fail_with_a_useful_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "guide.md"
            source.write_text("| A | B |\n| --- | --- |\n| 1 | 2 | 3 |\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "header has 2"):
                self.converter.convert(source, Path(tmp) / "guide.docx")

    def test_heading_inline_formatting_is_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "guide.md"
            out = Path(tmp) / "guide.docx"
            source.write_text("## Warm-up `[~5 min]` and **core**\n", encoding="utf-8")
            self.converter.convert(source, out)
            heading = Document(out).paragraphs[0]
            self.assertEqual(heading.text, "Warm-up [~5 min] and core")
            self.assertTrue(any(run.bold for run in heading.runs))

    def test_empty_row_is_not_a_separator(self):
        self.assertFalse(self.converter.is_table_separator("| | |"))


if __name__ == "__main__":
    unittest.main()
