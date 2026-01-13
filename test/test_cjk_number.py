"""Test cases for Issue #1: CJK keywords followed by numbers/letters.

This test ensures that CJK keywords can be extracted even when followed by
numbers or ASCII letters, since CJK characters are word boundaries themselves.
"""
import unittest
from flashtext import KeywordProcessor


class TestCJKNumberExtraction(unittest.TestCase):
    """Test CJK keyword extraction when followed by numbers or ASCII."""

    def test_chinese_followed_by_number(self):
        """Issue #1: Chinese keyword followed by number should be extracted."""
        kp = KeywordProcessor()
        kp.add_keyword('地中海贫血')
        
        # Should extract keyword even with trailing number
        self.assertEqual(
            kp.extract_keywords('地中海贫血'),
            ['地中海贫血']
        )
        self.assertEqual(
            kp.extract_keywords('地中海贫血2'),
            ['地中海贫血']
        )
        self.assertEqual(
            kp.extract_keywords('地中海贫血123'),
            ['地中海贫血']
        )

    def test_chinese_followed_by_letters(self):
        """Chinese keyword followed by ASCII letters should be extracted."""
        kp = KeywordProcessor()
        kp.add_keyword('地中海贫血')
        
        self.assertEqual(
            kp.extract_keywords('地中海贫血abc'),
            ['地中海贫血']
        )
        self.assertEqual(
            kp.extract_keywords('地中海贫血ABC'),
            ['地中海贫血']
        )

    def test_chinese_in_sentence_with_number(self):
        """Chinese keyword in middle of sentence followed by number."""
        kp = KeywordProcessor()
        kp.add_keyword('地中海贫血')
        
        self.assertEqual(
            kp.extract_keywords('我有地中海贫血2型'),
            ['地中海贫血']
        )

    def test_english_word_boundary_preserved(self):
        """Ensure English word boundary semantics are preserved.
        
        This is a regression test to ensure the CJK fix doesn't break
        English keyword matching which requires proper word boundaries.
        """
        kp = KeywordProcessor()
        kp.add_keyword('python prog', 'Python')
        
        # Should NOT match "python programming" - keyword is "python prog"
        self.assertEqual(
            kp.extract_keywords('i like python programming'),
            []
        )
        # Should match "python prog" at word boundary
        self.assertEqual(
            kp.extract_keywords('i like python prog'),
            ['Python']
        )

    def test_span_info_with_cjk_number(self):
        """Verify span positions are correct with CJK + number."""
        kp = KeywordProcessor()
        kp.add_keyword('地中海贫血')
        
        result = kp.extract_keywords('地中海贫血2', span_info=True)
        self.assertEqual(len(result), 1)
        keyword, start, end = result[0]
        self.assertEqual(keyword, '地中海贫血')
        self.assertEqual(start, 0)
        self.assertEqual(end, 5)  # 5 Chinese characters


if __name__ == '__main__':
    unittest.main()
