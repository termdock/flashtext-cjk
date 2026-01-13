"""Test cases for Issue #10: Cannot find/replace underscore character.

When removing characters from non_word_boundaries, they should become
matchable as individual keywords.
"""
import unittest
from flashtext import KeywordProcessor


class TestUnderscoreMatching(unittest.TestCase):
    """Test matching characters after removing them from non_word_boundaries."""

    def test_underscore_extract(self):
        """Issue #10: Extract underscore after removing from boundaries."""
        kp = KeywordProcessor()
        kp.non_word_boundaries.discard('_')
        kp.add_keyword('_', 'UNDERSCORE')
        
        result = kp.extract_keywords('hello_world')
        self.assertEqual(result, ['UNDERSCORE'])

    def test_underscore_replace(self):
        """Issue #10: Replace underscore with space."""
        kp = KeywordProcessor()
        kp.non_word_boundaries.discard('_')
        kp.add_keyword('_', ' ')
        
        result = kp.replace_keywords('hello_world')
        self.assertEqual(result, 'hello world')

    def test_underscore_multiple(self):
        """Multiple underscores should all be replaced."""
        kp = KeywordProcessor()
        kp.non_word_boundaries.discard('_')
        kp.add_keyword('_', ' ')
        
        result = kp.replace_keywords('the_quick_brown_fox')
        self.assertEqual(result, 'the quick brown fox')

    def test_underscore_with_span(self):
        """Underscore position should be correct in span info."""
        kp = KeywordProcessor()
        kp.non_word_boundaries.discard('_')
        kp.add_keyword('_', 'X')
        
        result = kp.extract_keywords('a_b', span_info=True)
        self.assertEqual(len(result), 1)
        keyword, start, end = result[0]
        self.assertEqual(keyword, 'X')
        self.assertEqual(start, 1)
        self.assertEqual(end, 2)

    def test_custom_char_removed_from_boundary(self):
        """Any character removed from boundaries should become matchable."""
        kp = KeywordProcessor()
        kp.non_word_boundaries.discard('x')
        kp.add_keyword('x', 'FOUND')
        
        result = kp.extract_keywords('axb')
        self.assertEqual(result, ['FOUND'])


if __name__ == '__main__':
    unittest.main()
