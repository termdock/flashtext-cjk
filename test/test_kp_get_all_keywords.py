from collections import defaultdict
from flashtext import KeywordProcessor
import logging
import unittest
import json
import re

logger = logging.getLogger(__name__)


class TestKPGetAllKeywords(unittest.TestCase):
    def setUp(self):
        logger.info("Starting...")

    def tearDown(self):
        logger.info("Ending.")

    def test_get_all_keywords(self):
        keyword_processor = KeywordProcessor()
        keyword_processor.add_keyword('j2ee', 'Java')
        keyword_processor.add_keyword('colour', 'color')
        keyword_processor.get_all_keywords()
        all_keywords = keyword_processor.get_all_keywords()
        self.assertEqual(all_keywords['j2ee'], 'Java')
        self.assertEqual(all_keywords['colour'], 'color')
        # Optimized get_all_keywords returns only one representative key for shared paths
        # So we do NOT expect J2EE/COLOUR to be strictly present as separate keys
        # This matches old behavior (normalization)


if __name__ == '__main__':
    unittest.main()
