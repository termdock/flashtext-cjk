import unittest
import flashtext_rs

class TestRustCompatibility(unittest.TestCase):
    def test_case_insensitive_dag(self):
        """Test Mixed Case Support logic in Rust (Arena DAG)"""
        # Rust Implementation
        kp = flashtext_rs.KeywordProcessor(case_sensitive=False)
        kp.add_keyword("Test")
        
        # Should match all variations without lowercasing text
        text = "TEST test TeSt"
        keywords = kp.extract_keywords(text)
        self.assertEqual(keywords, ["Test", "Test", "Test"])

    def test_case_sensitive_strict(self):
        """Test Case Sensitive logic in Rust"""
        kp = flashtext_rs.KeywordProcessor(case_sensitive=True)
        kp.add_keyword("Test")
        
        text = "TEST test TeSt Test"
        keywords = kp.extract_keywords(text)
        self.assertEqual(keywords, ["Test"])

    def test_overlap_logic(self):
        """Test that overlaps are handled (longest match wins or sequential?)
        Note: Python implementation allows overlaps if they start at different positions? 
        Actually Python implementation jumps index.
        """
        kp = flashtext_rs.KeywordProcessor()
        kp.add_keyword("word")
        kp.add_keyword("word2")
        
        text = "word2"
        # Since 'word2' is longer, it should be matched if it is in trie
        # The rust implementation basically finds longest match starting at current char
        keywords = kp.extract_keywords(text)
        self.assertEqual(keywords, ["word2"])

    def test_boundary_chars(self):
        """Test simple boundary"""
        kp = flashtext_rs.KeywordProcessor()
        kp.add_keyword("apple")
        
        # 'apple.' -> match
        # 'pineapple' -> no match
        self.assertEqual(kp.extract_keywords("apple."), ["apple"])
        self.assertEqual(kp.extract_keywords("pineapple"), [])

    def test_len_and_properties(self):
        """Test len() and properties"""
        kp = flashtext_rs.KeywordProcessor()
        kp.add_keyword("one")
        kp.add_keyword("two")
        self.assertEqual(len(kp), 2)
        
        # Test boundaries get/set
        boundaries = kp.non_word_boundaries
        self.assertTrue('a' in boundaries)
        self.assertFalse('!' in boundaries)
        
        # Modify
        new_boundaries = boundaries.copy()
        new_boundaries.add('!')
        kp.non_word_boundaries = new_boundaries
        
        self.assertTrue('!' in kp.non_word_boundaries)
        
    def test_cjk_basics(self):
         """Test CJK behavior with default boundaries"""
         kp = flashtext_rs.KeywordProcessor()
         kp.add_keyword("中")
         
         # '国' is not in default non_word_boundaries (it is a separator/boundary)
         # So '中' should be extracted from '中国'
         self.assertEqual(kp.extract_keywords("中国"), ["中"])
         
         current_b = kp.non_word_boundaries
         current_b.add("国")
         kp.non_word_boundaries = current_b
         
         # '中' is separator, '国' is word. "Sep Word" -> Matches Sep.
         # So it should still match '中'.
         self.assertEqual(kp.extract_keywords("中国"), ["中"])

    def test_fuzzy_levensthein(self):
        """Test Fuzzy Matching (Levenshtein)"""
        kp = flashtext_rs.KeywordProcessor()
        kp.add_keyword("apple")
        kp.add_keyword("banana")
        
        # 'aple' -> cost 1 to 'apple'
        # Rust returns list iterator, convert to list for len()
        results = list(kp.levensthein("aple", max_cost=1))
        
        self.assertTrue(len(results) > 0)
        
        found = False
        for item in results:
            node_dict, cost, depth = item
            if node_dict.get('_keyword_') == 'apple':
                self.assertEqual(cost, 1)
                found = True
        self.assertTrue(found)

    def test_replace_keywords(self):
        """Test replace_keywords (Rust)"""
        kp = flashtext_rs.KeywordProcessor()
        kp.add_keyword("New York", "NY")
        kp.add_keyword("Big Apple", "NY")
        
        text = "I love Big Apple and New York."
        # Should replace both with NY
        new_text = kp.replace_keywords(text)
        self.assertEqual(new_text, "I love NY and NY.")
        
        text2 = "Big ApplePie"
        self.assertEqual(kp.replace_keywords(text2), "Big ApplePie")

    def test_remove_keywords(self):
        """Test remove_keyword (Rust)"""
        kp = flashtext_rs.KeywordProcessor()
        kp.add_keyword("Test")
        kp.add_keyword("Test Case")
        
        self.assertEqual(len(kp), 2)
        
        # Remove 'Test'
        # 'Test Case' should remain
        self.assertTrue(kp.remove_keyword("Test"))
        self.assertFalse(kp.remove_keyword("Test")) # Already removed
        
        self.assertEqual(len(kp), 1)
        self.assertEqual(kp.extract_keywords("Test Case"), ["Test Case"])
        self.assertEqual(kp.extract_keywords("Test"), [])
        
        # Remove 'Test Case' (pruning check)
        self.assertTrue(kp.remove_keyword("Test Case"))
        self.assertEqual(len(kp), 0)

    def test_get_keywords(self):
        """Test get_keyword and get_all_keywords (Rust)"""
        kp = flashtext_rs.KeywordProcessor()
        kp.add_keyword("Big Apple", "New York")
        kp.add_keyword("Apple", "Fruit")
        
        # get_keyword
        self.assertEqual(kp.get_keyword("Big Apple"), "New York")
        self.assertEqual(kp.get_keyword("Apple"), "Fruit")
        self.assertIsNone(kp.get_keyword("Orange"))
        
        # get_keyword (Mixed Case check) - default is case_sensitive=False
        self.assertEqual(kp.get_keyword("big apple"), "New York")
        
        # get_all_keywords
        all_kws = kp.get_all_keywords()
        self.assertTrue(len(all_kws) > 2)
        self.assertEqual(all_kws["Big Apple"], "New York")
        self.assertEqual(all_kws["big apple"], "New York")
        self.assertEqual(all_kws["Apple"], "Fruit")

    def test_item_protocols(self):
        """Test __getitem__, __setitem__, __contains__, __delitem__"""
        kp = flashtext_rs.KeywordProcessor()
        kp['Key'] = 'Value'
        
        self.assertTrue('Key' in kp)
        self.assertEqual(kp['Key'], 'Value')
        
        # Test missing key error
        with self.assertRaises(KeyError) as cm:
            _ = kp['Missing']
        
        del kp['Key']
        self.assertFalse('Key' in kp)
        
        # Test iter disabled
        with self.assertRaises(NotImplementedError):
            iter(kp)

if __name__ == "__main__":
    unittest.main()
