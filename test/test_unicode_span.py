"""Test cases for Issue #2: Unicode case conversion span issue.

When lowercasing certain Unicode characters like Turkish İ, the string length
can change (İ -> i̇ is 1 char -> 2 chars). This causes span positions to be
incorrect if we lowercase the entire string upfront.

The fix is to lowercase each character individually during traversal.
"""
import unittest
from flashtext import KeywordProcessor


class TestUnicodeSpan(unittest.TestCase):
    """Test that span positions are correct with special Unicode characters."""

    def test_turkish_dotted_i(self):
        """Issue #2: Turkish İ causes span position offset.
        
        İ (U+0130, Latin Capital Letter I With Dot Above) lowercases to
        'i̇' which is 2 characters (i + combining dot above).
        """
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keyword('Bay Area')
        
        text = 'İ I love big Apple and Bay Area.'
        keywords = kp.extract_keywords(text, span_info=True)
        
        self.assertEqual(len(keywords), 1)
        keyword, start, end = keywords[0]
        
        # Verify the span points to correct position in original text
        self.assertEqual(text[start:end], 'Bay Area')
        self.assertEqual(keyword, 'Bay Area')

    def test_german_sharp_s(self):
        """German ß (sharp s) uppercases to SS (2 chars).
        
        While we lowercase text (not uppercase), this tests similar
        Unicode case folding edge cases.
        """
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keyword('straße', 'street')
        
        text = 'Die Straße ist lang'
        keywords = kp.extract_keywords(text, span_info=True)
        
        self.assertEqual(len(keywords), 1)
        keyword, start, end = keywords[0]
        self.assertEqual(text[start:end], 'Straße')
        self.assertEqual(keyword, 'street')

    def test_multiple_keywords_with_unicode(self):
        """Multiple keywords with Unicode characters in text."""
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keyword('Big Apple', 'New York')
        kp.add_keyword('Bay Area')
        
        # İ at the start shifts all positions if not handled correctly
        text = 'İ love Big Apple and Bay Area!'
        keywords = kp.extract_keywords(text, span_info=True)
        
        self.assertEqual(len(keywords), 2)
        
        # Check first keyword
        kw1, start1, end1 = keywords[0]
        self.assertEqual(text[start1:end1], 'Big Apple')
        self.assertEqual(kw1, 'New York')
        
        # Check second keyword
        kw2, start2, end2 = keywords[1]
        self.assertEqual(text[start2:end2], 'Bay Area')
        self.assertEqual(kw2, 'Bay Area')

    def test_normal_ascii_unchanged(self):
        """Normal ASCII text should work as before."""
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keyword('PYTHON', 'Python')
        
        text = 'I love python programming'
        keywords = kp.extract_keywords(text, span_info=True)
        
        self.assertEqual(len(keywords), 1)
        keyword, start, end = keywords[0]
        self.assertEqual(text[start:end], 'python')
        self.assertEqual(keyword, 'Python')


if __name__ == '__main__':
    unittest.main()
