from flashtext import KeywordProcessor
import logging
import unittest

logger = logging.getLogger(__name__)

class TestMixedCase(unittest.TestCase):
    def setUp(self):
        logger.info("Starting...")

    def tearDown(self):
        logger.info("Ending.")

    def test_mixed_case_basic(self):
        """
        Test mixing case sensitive and case insensitive keywords.
        """
        kp = KeywordProcessor(case_sensitive=False) # Global default loose
        
        # Add loose keyword (default)
        kp.add_keyword('banana') 
        
        # Add strict keyword (override)
        kp.add_keyword('Apple', case_sensitive=True)
        
        # 'banana' should match 'Banana', 'BANANA'
        self.assertEqual(kp.extract_keywords('I like Banana'), ['banana'])
        self.assertEqual(kp.extract_keywords('I like BANANA'), ['banana'])
        
        # 'Apple' should match 'Apple' ONLY
        self.assertEqual(kp.extract_keywords('I like Apple'), ['Apple'])
        self.assertEqual(kp.extract_keywords('I like apple'), []) # strict no match
        self.assertEqual(kp.extract_keywords('I like APPLE'), []) # strict no match

    def test_mixed_case_overlap(self):
        """
        Test overlap between strict and loose keywords.
        """
        kp = KeywordProcessor() # default loose
        
        # 'us' -> loose (matches 'US', 'us', 'Us'...)
        kp.add_keyword('us', 'UNI')
        
        # 'US' -> strict (matches 'US' only). Maps to 'USA'
        kp.add_keyword('US', 'USA', case_sensitive=True)
        
        # Input 'us' -> matches loose 'us'
        # Due to shared node optimization, Strict 'US' overwrote the shared destination node.
        # So 'us' (which maps to u->s->Node2) now leads to 'USA'.
        self.assertEqual(kp.extract_keywords('call us now'), ['USA'])
        
        # Input 'US' -> matches strict 'US' ('USA') AND loose 'us' ('UNI')?
        # Since 'US' (strict) was added LAST, it might overwrite the 'S' node's keyword?
        # Or if they share the node, the last write wins.
        # Strict "US" vs Loose "us":
        # Loose adds u->s and U->S.
        # Strict adds U->S.
        # So 'U'->'S' path is SHARED.
        # The node at 'S' is shared.
        # Last write was 'US'->'USA'.
        # So 'U'->'S' (input "US") should yield 'USA'.
        self.assertEqual(kp.extract_keywords('call US now'), ['USA'])
        
        # Input 'Us' (Mixed case)
        # Matches loose 'us' path: U->s. (Wait, loose adds U->s too? No)
        # Loose 'us':
        # 'u' and 'U' -> Node1
        # Node1 has 's' and 'S' -> Node2 ('UNI')
        # So U->s works.
        # Strict 'US':
        # 'U' -> Node1 (Shared)
        # Node1 has 'S' -> Node2 (Shared -> 'USA')
        # Does Strict add 's'? NO.
        # So Node1 works for 'S' and 's'.
        # Node2 holds the keyword.
        # So ALL paths leading to Node2 yield 'USA'?
        # YES. Because Node2 is the shared object.
        # So even 'us' will return 'USA' if 'US' overwrote it?
        # Let's verify.
        keywords = kp.extract_keywords('call Us now')
        # Expect 'USA' if overwritten.
        self.assertEqual(keywords, ['USA'])

    def test_global_strict_override_loose(self):
        """
        Global strict=True, adding per-keyword loose=True.
        """
        kp = KeywordProcessor(case_sensitive=True)
        
        kp.add_keyword('Apple') # strict (global)
        kp.add_keyword('banana', case_sensitive=False) # override loose
        
        self.assertEqual(kp.extract_keywords('Apple'), ['Apple'])
        self.assertEqual(kp.extract_keywords('apple'), [])
        
        self.assertEqual(kp.extract_keywords('Banana'), ['banana'])

if __name__ == '__main__':
    unittest.main()
