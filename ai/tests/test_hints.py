# pylint: disable=missing-docstring
import unittest
from collections import defaultdict
from ai.services.hints import (
    parse_hints,
)  # Adjust the import based on where parse_hints is located


class TestParseHints(unittest.TestCase):
    def test_empty_hints(self):
        hints = ""
        expected = defaultdict(list)
        self.assertEqual(parse_hints(hints), expected)

    def test_single_page_hint(self):
        hints = "page 1 : test"
        expected = defaultdict(list, {1: ["test"]})
        self.assertEqual(parse_hints(hints), expected)

    def test_page_range_hint(self):
        hints = "pages 1 à 3 : truc specifique"
        expected = defaultdict(
            list,
            {1: ["truc specifique"], 2: ["truc specifique"], 3: ["truc specifique"]},
        )
        self.assertEqual(parse_hints(hints), expected)

    def test_multiple_pages_hint(self):
        hints = "page 1 : test;page 2: foo"
        expected = defaultdict(list, {1: ["test"], 2: ["foo"]})
        self.assertEqual(parse_hints(hints), expected)

    def test_multiple_same_pages_hint(self):
        hints = "page 1 : test;page 1: foo"
        expected = defaultdict(list, {1: ["test", "foo"]})
        self.assertEqual(parse_hints(hints), expected)

    def test_multiple_pages_with_all_hint(self):
        hints = "page 1 : test;page 2: foo;toutes pages: encore"
        expected = defaultdict(list, {1: ["test"], 2: ["foo"], 'all': ["encore"]})
        self.assertEqual(parse_hints(hints), expected)

    def test_all_pages_hint(self):
        hints = "toutes pages: encore truc specifique"
        expected = defaultdict(list, {"all": ["encore truc specifique"]})
        self.assertEqual(parse_hints(hints), expected)

    def test_malformed_hint(self):
        hints = "some incorrect hint format"
        expected = defaultdict(list)
        self.assertEqual(parse_hints(hints), expected)
