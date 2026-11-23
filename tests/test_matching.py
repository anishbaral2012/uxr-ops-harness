import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uxrops import locators  # noqa: E402
from uxrops.textmatch import closest_line, find_quote  # noqa: E402

TEXT = (
    "Q1 P1: Um, I renewed it on my phone, you know, during lunch.\n"
    "Q2 P1: I wasn't sure it worked.\n"
    "\n"
    "Q3 P1: The receipt came an hour later.\n"
)


class QuoteMatchingTests(unittest.TestCase):
    def test_verbatim_quote(self):
        [match] = find_quote("I wasn't sure it worked.", TEXT)
        self.assertFalse(match.edited)

    def test_ellipsis_cuts_and_bracket_inserts(self):
        self.assertTrue(find_quote("I renewed it on my phone … during lunch.", TEXT))
        self.assertTrue(find_quote("I renewed it on [the app] ... during lunch.", TEXT))

    def test_unmarked_trim_fails(self):
        self.assertEqual(find_quote("I renewed it on my phone during lunch.", TEXT), [])

    def test_fragments_must_be_in_order(self):
        self.assertEqual(find_quote("during lunch … I renewed it", TEXT), [])

    def test_fragments_cannot_be_far_apart(self):
        far = "start of the story " + "x" * 400 + " end of the story"
        self.assertEqual(find_quote("start of the story … end of the story", far), [])

    def test_too_little_source_text_fails(self):
        self.assertEqual(find_quote("I … it … on", TEXT), [])

    def test_brackets_are_literal_in_verbatim_quotes(self):
        text = "P2: I went [laughs] to the counter."
        self.assertTrue(find_quote("I went [laughs] to the counter.", text, allow_brackets=False))

    def test_normalize_folds_quote_marks_and_whitespace(self):
        self.assertEqual(find_quote("I wasn’t  sure it worked.", TEXT), [])
        self.assertTrue(find_quote("I wasn’t  sure it worked.", TEXT, normalize=True))

    def test_edited_match_spanning_lines_is_detectable(self):
        [match] = find_quote("you know, during lunch. … I wasn't sure", TEXT)
        self.assertTrue(match.edited and match.multiline(TEXT))

    def test_closest_line_hint(self):
        line, ratio = closest_line("I was not sure it worked", TEXT)
        self.assertEqual(line, 2)
        self.assertGreater(ratio, 0.8)


class LocatorTests(unittest.TestCase):
    def check(self, locator, quote, text=TEXT):
        return locators.check(locator, text, find_quote(quote, text))[0]

    def test_lines(self):
        self.assertEqual(self.check("line 2", "I wasn't sure"), "ok")
        self.assertEqual(self.check("S1 lines 1-2", "I wasn't sure"), "ok")
        self.assertEqual(self.check("L4", "The receipt came"), "ok")
        self.assertEqual(self.check("line 3", "I wasn't sure"), "mismatch")

    def test_paragraphs(self):
        self.assertEqual(self.check("paragraph 1", "I wasn't sure"), "ok")
        self.assertEqual(self.check("para 2", "The receipt came"), "ok")
        self.assertEqual(self.check("¶2", "I wasn't sure"), "mismatch")

    def test_paragraphs_fall_back_to_lines(self):
        text = "first line here\nsecond line here\n"
        self.assertEqual(self.check("paragraph 2", "second line", text), "ok")

    def test_timestamps(self):
        text = "[00:01:10] P2: I went to the counter.\n[00:02:45] P2: The clerk printed a receipt.\n"
        self.assertEqual(self.check("00:02:45", "The clerk printed", text), "ok")
        self.assertEqual(self.check("00:03:00", "The clerk printed", text), "ok")
        self.assertEqual(self.check("00:01:10-00:02:00", "The clerk printed", text), "mismatch")
        self.assertEqual(self.check("1:15", "I went to the counter", text), "ok")
        self.assertEqual(self.check("00:02:45", "I wasn't sure"), "unchecked")

    def test_free_text_is_unchecked(self):
        self.assertEqual(self.check("near the end", "I wasn't sure"), "unchecked")


if __name__ == "__main__":
    unittest.main()
