import unittest
from flashtext import KeywordProcessor


class TestInternationalBoundaries(unittest.TestCase):
    def setUp(self):
        self.kp = KeywordProcessor()

    def test_international_characters_are_word_parts(self):
        """Test that international characters are treated as part of words by default."""
        # 'caf' should NOT be found in 'café' (e is part of word)
        self.kp.add_keyword('caf')
        keywords = self.kp.extract_keywords('café')
        self.assertEqual(keywords, [], "Failed: 'caf' extracted from 'café'")

        # 'café' should be found in 'café'
        self.kp.add_keyword('café')
        keywords = self.kp.extract_keywords('I went to a café yesterday')
        self.assertEqual(keywords, ['café'])

    def test_explicit_removal_makes_boundary(self):
        """Test that removing a character makes it a boundary."""
        # Default: 'é' is part of word
        self.kp.add_keyword('caf')
        self.assertEqual(self.kp.extract_keywords('café'), [])

        # Remove 'é' from word boundaries (make it a separator)
        # Note: non_word_boundaries logic is inverted in naming:
        # non_word_boundaries = Set of characters that are PART of a word.
        # So removing from it means it becomes a boundary.
        self.kp.non_word_boundaries.remove('é')
        
        # Now 'caf' should be extracted from 'café' because 'é' is a boundary
        keywords = self.kp.extract_keywords('café')
        self.assertEqual(keywords, ['caf'])

    def test_explicit_addition_makes_word_part(self):
        """Test that adding a character makes it part of a word."""
        # Default: '!' is a boundary
        self.kp.add_keyword('Hello')
        self.assertEqual(self.kp.extract_keywords('Hello!'), ['Hello'])

        # Add '!' to word characters
        self.kp.non_word_boundaries.add('!')
        
        # Now 'Hello' should NOT be extracted from 'Hello!' because '!' is part of word
        self.assertEqual(self.kp.extract_keywords('Hello!'), [])

        # 'Hello!' should be extracted
        self.kp.add_keyword('Hello!')
        self.assertEqual(self.kp.extract_keywords('Hello!'), ['Hello!'])

    def test_chinese_characters(self):
        """Test with CJK characters."""
        # '中' should be extracted from '中国' because '国' is a boundary for CJK
        self.kp.add_keyword('中')
        self.assertEqual(self.kp.extract_keywords('中国'), ['中'])

        # '中国' should be extracted (Longest match wins if both present)
        self.kp.add_keyword('中国')
        # If both '中' and '中国' are keywords, '中国' should be extracted due to longest match
        self.assertEqual(self.kp.extract_keywords('中国'), ['中国'])

    def test_mixed_operations(self):
        """Test mix of add/remove/discard."""
        # 'e' is word char
        self.assertTrue('e' in self.kp.non_word_boundaries)
        
        # Remove 'e' -> boundary
        self.kp.non_word_boundaries.remove('e')
        self.assertFalse('e' in self.kp.non_word_boundaries)
        
        # 'app' found in 'apple' because 'e' is boundary
        self.kp.add_keyword('appl')
        self.assertEqual(self.kp.extract_keywords('apple'), ['appl'])
        
        # Add 'e' back -> word char
        self.kp.non_word_boundaries.add('e')
        self.assertTrue('e' in self.kp.non_word_boundaries)
        self.assertEqual(self.kp.extract_keywords('apple'), [])

    def test_compatibility_apis(self):
        """Test API compatibility with set operations."""
        # Copy
        copy_boundaries = self.kp.non_word_boundaries.copy()
        self.assertTrue('a' in copy_boundaries)
        self.assertTrue('é' in copy_boundaries)
        
        # Make changes to copy shouldn't affect original
        copy_boundaries.remove('a')
        self.assertFalse('a' in copy_boundaries)
        self.assertTrue('a' in self.kp.non_word_boundaries)

if __name__ == '__main__':
    unittest.main()
