import unittest
from flashtext import KeywordProcessor

class TestKPDictionaryLikeFeatures(unittest.TestCase):
    def test_term_in_dictionary(self):
        keyword_processor = KeywordProcessor()
        keyword_processor['Test'] = 'Test'
        self.assertTrue('Test' in keyword_processor)
        self.assertEqual(keyword_processor['Test'], 'Test')

    def test_term_in_dictionary_case_sensitive(self):
        keyword_processor = KeywordProcessor(case_sensitive=True)
        keyword_processor['J2ee'] = 'Java'
        self.assertTrue('J2ee' in keyword_processor)
        self.assertEqual(keyword_processor['J2ee'], 'Java')

    def test_set_term_in_dictionary_case_sensitive(self):
        keyword_processor = KeywordProcessor(case_sensitive=True)
        keyword_processor['J2ee'] = 'Java'
        keyword_processor['J2ee'] = 'J2EE'
        self.assertTrue('J2ee' in keyword_processor)
        self.assertEqual(keyword_processor['J2ee'], 'J2EE')
        
if __name__ == '__main__':
    unittest.main()
