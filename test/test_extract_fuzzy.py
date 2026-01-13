import unittest
from flashtext import KeywordProcessor


class TestExtractFuzzy(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_extract_addition(self):
        """
        Fuzzy addition
        """
        keyword_proc = KeywordProcessor()
        for keyword in (('colour here', 'couleur ici'), ('and heere', 'et ici')):
            keyword_proc.add_keyword(*keyword)

        sentence = "color here blabla and here"

        extracted_keywords = [('couleur ici', 0, 10), ('et ici', 18, 26)]
        self.assertListEqual(keyword_proc.extract_keywords(sentence, span_info=True, max_cost=1), extracted_keywords)

    def test_extract_cost_spread_over_multiple_words(self):
        """
        Here we try to extract a keyword made of different words
        the current cost should be decreased by one when encountering 'maade' (1 insertion)
        and again by one when encountering 'multple' (1 deletion)
        """
        keyword_proc = KeywordProcessor()
        keyword_made_of_multiple_words = 'made of multiple words'
        keyword_proc.add_keyword(keyword_made_of_multiple_words)
        sentence = "this sentence contains a keyword maade of multple words"

        extracted_keywords = [(keyword_made_of_multiple_words, 33, 55)]
        self.assertEqual(keyword_proc.extract_keywords(sentence, span_info=True, max_cost=2), extracted_keywords)


    def test_extract_multiple_keywords(self):
        keyword_proc = KeywordProcessor()
        keyword_proc.add_keyword('first keyword')
        keyword_proc.add_keyword('second keyword')
        sentence = "starts with a first kyword then add a secand keyword"
        extracted_keywords = [
            ('first keyword', 14, 26),
            ('second keyword', 38, 52),
        ]
        self.assertEqual(keyword_proc.extract_keywords(sentence, span_info=True, max_cost=1), extracted_keywords)

    def test_intermediate_match(self):
        """
        In this test, we have an intermediate fuzzy match with a keyword (the shortest one)
        We first check that we extract the longest keyword if the max_cost is big enough
        Then we retry with a smaller max_cost, excluding the longest, and check that the shortest is extracted
        """
        keyword_proc = KeywordProcessor()
        keyword_proc.add_keyword('keyword')
        keyword_proc.add_keyword('keyword with many words')
        sentence = "This sentence contains a keywrd with many woords"

        shortest_keyword = ('keyword', 25, 31)
        longest_keyword = ('keyword with many words', 25, 48)

        self.assertEqual(keyword_proc.extract_keywords(sentence, span_info=True, max_cost=2), [longest_keyword])
        self.assertEqual(keyword_proc.extract_keywords(sentence, span_info=True, max_cost=1), [shortest_keyword])

    def test_intermediate_match_then_no_match(self):
        """
        In this test, we have an intermediate fuzzy match with a keyword (the shortest one)
        We check that we get only the shortest keyword when going further into fuzzy match is too
        expansive to get the longest keyword. We also extract a classic match later in the string,
        to check that the inner data structures all have a correct state
        """
        keyword_proc = KeywordProcessor()
        keyword_proc.add_keyword('keyword')
        keyword_proc.add_keyword('keyword with many words')
        sentence = "This sentence contains a keywrd with many items inside, a keyword at the end"

        keywords = [('keyword', 25, 31), ('keyword', 58, 65)]
        self.assertEqual(keyword_proc.extract_keywords(sentence, span_info=True, max_cost=2), keywords)


if __name__ == '__main__':
    unittest.main()