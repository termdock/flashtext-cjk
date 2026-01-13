from flashtext import KeywordProcessor
import logging
import unittest

logger = logging.getLogger(__name__)

class TestExtractFuzzyCJK(unittest.TestCase):
    def setUp(self):
        logger.info("Starting...")

    def tearDown(self):
        logger.info("Ending.")

    def test_fuzzy_cjk_deletion(self):
        """
        Test fuzzy deletion in CJK
        """
        kp = KeywordProcessor()
        kp.add_keyword('機器學習') # Machine Learning
        
        # Missing one char: "機器習" (cost 1)
        sentence = "我喜歡機器習"
        # Since '機器學習' is length 4. '機器習' is length 3. Distance 1.
        # Should match if max_cost=1
        
        keywords = kp.extract_keywords(sentence, max_cost=1)
        self.assertEqual(keywords, ['機器學習'])

    def test_fuzzy_cjk_substitution(self):
        """
        Test fuzzy substitution in CJK
        """
        kp = KeywordProcessor()
        kp.add_keyword('人工智慧') # AI
        
        # Typo: "人工智障" (Artificial Mental Retardation - common meme/typo). Distance 1.
        sentence = "這是人工智障應用"
        
        keywords = kp.extract_keywords(sentence, max_cost=1)
        self.assertEqual(keywords, ['人工智慧'])

    def test_fuzzy_mixed_unicode(self):
        """
        Test fuzzy match with mixed scripts
        """
        kp = KeywordProcessor()
        kp.add_keyword('iPhone 15')
        
        # Typo: "iPhone 1S" (Distance 1)
        sentence = "New iPhone 1S is here"
        
        keywords = kp.extract_keywords(sentence, max_cost=1)
        self.assertEqual(keywords, ['iPhone 15'])

if __name__ == '__main__':
    unittest.main()
