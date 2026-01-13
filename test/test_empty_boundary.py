"""Test cases for Issue #3: Empty non-word boundary replace failure.

When non_word_boundaries is set to empty, adjacent keywords should still
be replaced correctly.
"""
import unittest
from flashtext import KeywordProcessor


class TestEmptyBoundaryReplace(unittest.TestCase):
    """Test replace_keywords with empty non_word_boundaries."""

    def test_empty_boundary_adjacent_replace(self):
        """Issue #3: Adjacent keywords with empty boundary should all be replaced."""
        kp = KeywordProcessor(case_sensitive=True)
        kp.add_keyword('aa', 'b')
        kp.add_keyword('cc', 'd')
        kp.set_non_word_boundaries('')
        
        result = kp.replace_keywords('aacc')
        self.assertEqual(result, 'bd')

    def test_empty_boundary_triple_replace(self):
        """Three adjacent keywords with empty boundary."""
        kp = KeywordProcessor(case_sensitive=True)
        kp.add_keyword('aa', 'X')
        kp.add_keyword('bb', 'Y')
        kp.add_keyword('cc', 'Z')
        kp.set_non_word_boundaries('')
        
        result = kp.replace_keywords('aabbcc')
        self.assertEqual(result, 'XYZ')

    def test_cjk_adjacent_replace(self):
        """CJK adjacent keywords should all be replaced."""
        kp = KeywordProcessor()
        kp.add_keyword('雅詩蘭黛', 'Estee Lauder')
        kp.add_keyword('小棕瓶', 'ANR')
        
        result = kp.replace_keywords('推薦雅詩蘭黛小棕瓶超好用')
        self.assertEqual(result, '推薦Estee LauderANR超好用')

    def test_normal_replace_still_works(self):
        """Normal replace with default boundaries should still work."""
        kp = KeywordProcessor()
        kp.add_keyword('Big Apple', 'New York')
        kp.add_keyword('Bay Area')
        
        result = kp.replace_keywords('I love Big Apple and Bay Area.')
        self.assertEqual(result, 'I love New York and Bay Area.')


if __name__ == '__main__':
    unittest.main()
