import importlib.util
import tempfile
import unittest
from pathlib import Path

try:
    from docx import Document
except ImportError:
    Document = None

SCRIPT = Path(__file__).resolve().parents[1] / "uxr-interview-questions" / "references" / "md-to-docx.py"


@unittest.skipIf(Document is None, "python-docx is not installed")
class MarkdownConversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("md_to_docx", SCRIPT)
        cls.converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.converter)

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

    def test_empty_row_is_not_a_separator(self):
        self.assertFalse(self.converter.is_table_separator("| | |"))


if __name__ == "__main__":
    unittest.main()
