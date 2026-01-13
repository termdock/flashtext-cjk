import unittest
from flashtext import KeywordProcessor

class TestMultiLabel(unittest.TestCase):
    def setUp(self):
        self.kp = KeywordProcessor()

    def test_add_list_keywords(self):
        """Test adding keyword with list of clean names."""
        self.kp.add_keyword('Apple', ['Fruit', 'Tech'])
        keywords = self.kp.extract_keywords('I have an Apple')
        
        # Should extract both
        self.assertEqual(len(keywords), 2)
        self.assertIn('Fruit', keywords)
        self.assertIn('Tech', keywords)

    def test_replace_list_keywords(self):
        """Test replacement uses first element."""
        self.kp.add_keyword('Apple', ['Fruit', 'Tech'])
        new_text = self.kp.replace_keywords('I have an Apple')
        
        # Should use 'Fruit' (first element)
        self.assertEqual(new_text, 'I have an Fruit')

    def test_mixed_single_and_list(self):
        """Test mixing single value and list value keywords."""
        self.kp.add_keyword('Apple', ['Fruit', 'Tech'])
        self.kp.add_keyword('Banana', 'Fruit')
        
        keywords = self.kp.extract_keywords('Apple and Banana')
        # Expect: Fruit, Tech, Fruit (order depends on extraction logic)
        
        self.assertEqual(len(keywords), 3)
        self.assertEqual(keywords.count('Fruit'), 2)
        self.assertEqual(keywords.count('Tech'), 1)

    def test_replace_with_overlaps(self):
        """Test replacement stability with multi-label overlap."""
        # Apple -> [Fruit, Tech]
        self.kp.add_keyword('Apple', ['Fruit', 'Tech'])
        
        # Verify replace doesn't duplicate text
        # If naive impl: "I have an " + "Fruit" + "" + "Tech" -> "I have an FruitTech"
        # Correct impl: "I have an Fruit"
        new_text = self.kp.replace_keywords('Apple')
        self.assertEqual(new_text, 'Fruit')

    def test_case_insensitive_multi(self):
        """Test case insensitive matching for multi-label."""
        self.kp = KeywordProcessor(case_sensitive=False)
        self.kp.add_keyword('apple', ['Fruit', 'Tech'])
        
        keywords = self.kp.extract_keywords('APPLE')
        self.assertEqual(len(keywords), 2)
        self.assertIn('Fruit', keywords)

    def test_multiple_multi_labels(self):
        """Test sequence of multi-label keywords."""
        self.kp.add_keyword('A', ['A1', 'A2'])
        self.kp.add_keyword('B', ['B1', 'B2'])
        
        text = "A B"
        keywords = self.kp.extract_keywords(text)
        # Should be [A1, A2, B1, B2] (or similar order)
        
        self.assertEqual(len(keywords), 4)
        expected = {'A1', 'A2', 'B1', 'B2'}
        self.assertEqual(set(keywords), expected)

        # Replace
        new_text = self.kp.replace_keywords(text)
        self.assertEqual(new_text, "A1 B1")

if __name__ == '__main__':
    unittest.main()
