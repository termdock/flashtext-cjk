import unittest
from flashtext import KeywordProcessor


class TestReplaceMetadata(unittest.TestCase):
    def setUp(self):
        self.kp = KeywordProcessor()
        self.kp.add_keyword('Big Apple', 'New York')
        self.kp.add_keyword('Bay Area')

    def test_basic_metadata(self):
        """Test basic replacement with metadata."""
        text = "I love Big Apple"
        new_text, replacements = self.kp.replace_keywords(text, span_info=True)
        
        self.assertEqual(new_text, "I love New York")
        self.assertEqual(len(replacements), 1)
        self.assertEqual(replacements[0]['original'], 'Big Apple')
        self.assertEqual(replacements[0]['replacement'], 'New York')
        self.assertEqual(replacements[0]['start'], 7)
        self.assertEqual(replacements[0]['end'], 16)

    def test_multiple_replacements(self):
        """Test multiple replacements."""
        text = "I love Big Apple and Bay Area"
        new_text, replacements = self.kp.replace_keywords(text, span_info=True)
        
        self.assertEqual(new_text, "I love New York and Bay Area")
        self.assertEqual(len(replacements), 2)
        
        # Check order
        self.assertEqual(replacements[0]['original'], 'Big Apple')
        self.assertEqual(replacements[1]['original'], 'Bay Area')
        
        # Check span validity
        # Original: I love Big Apple and Bay Area (Len 29)
        # Big Apple: 7-16
        # Bay Area: 21-29
        self.assertEqual(text[replacements[0]['start']:replacements[0]['end']], 'Big Apple')
        self.assertEqual(text[replacements[1]['start']:replacements[1]['end']], 'Bay Area')

    def test_no_replacements(self):
        """Test functionality when no keywords match."""
        text = "Hello World"
        new_text, replacements = self.kp.replace_keywords(text, span_info=True)
        
        self.assertEqual(new_text, "Hello World")
        self.assertEqual(replacements, [])
        self.assertIsInstance(replacements, list)

    def test_backward_compatibility(self):
        """Ensure default behavior remains unchanged."""
        text = "I love Big Apple"
        result = self.kp.replace_keywords(text)
        
        self.assertTrue(isinstance(result, str))
        self.assertEqual(result, "I love New York")
        
        # Default span_info=False
        result = self.kp.replace_keywords(text, span_info=False)
        self.assertEqual(result, "I love New York")

if __name__ == '__main__':
    unittest.main()
