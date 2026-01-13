import unittest
from flashtext import KeywordProcessor


class TestExtractSentences(unittest.TestCase):
    def setUp(self):
        self.kp = KeywordProcessor()
        self.kp.add_keyword('Python')
        self.kp.add_keyword('Java')
        self.kp.add_keyword('C++')

    def test_basic_sentence_extraction(self):
        """Test basic sentence extraction with default delimiters."""
        text = "I love Python. Java is old. C++ is hard!"
        sentences = self.kp.extract_sentences(text)
        
        # Expected: 
        # ("I love Python.", ["Python"])
        # ("Java is old.", ["Java"])
        # ("C++ is hard!", ["C++"])
        # Note: trailing spaces might be issue depending on split logic
        
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0][0].strip(), "I love Python.")
        self.assertEqual(sentences[0][1], ["Python"])
        
        self.assertEqual(sentences[1][0].strip(), "Java is old.")
        self.assertEqual(sentences[1][1], ["Java"])
        
        self.assertEqual(sentences[2][0].strip(), "C++ is hard!")
        self.assertEqual(sentences[2][1], ["C++"])

    def test_sentence_with_multiple_keywords(self):
        """Test sentence with multiple keywords."""
        text = "Python and Java are languages."
        sentences = self.kp.extract_sentences(text)
        
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0][0].strip(), "Python and Java are languages.")
        self.assertEqual(sorted(sentences[0][1]), ["Java", "Python"])

    def test_no_matches(self):
        """Test sentences with no keywords are skipped."""
        text = "Hello world. Python is great."
        sentences = self.kp.extract_sentences(text)
        
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0][1], ["Python"])

    def test_custom_delimiters(self):
        """Test custom delimiters."""
        text = "Item 1: Python|Item 2: Ruby|Item 3: Java"
        # Ruby is not a keyword
        sentences = self.kp.extract_sentences(text, delimiters=['|'])
        
        # "Item 1: Python|" -> match
        # "Item 2: Ruby|" -> no match
        # "Item 3: Java" -> match
        
        # Wait, my logic: "full_sentence = sentence_content + delimiter"
        # Split "Item 1: Python|Item 2: Ruby|Item 3: Java" by "|"
        # Parts: ["Item 1: Python", "|", "Item 2: Ruby", "|", "Item 3: Java"]
        # 1. "Item 1: Python|"
        # 2. "Item 2: Ruby|"
        # 3. "Item 3: Java"
        
        self.assertEqual(len(sentences), 2)
        self.assertIn("Java", sentences[1][0])
        self.assertIn("Python", sentences[0][0])

    def test_consecutive_delimiters(self):
        """Test consecutive delimiters treated as one block."""
        text = "Python is cool!!! Java is ok."
        sentences = self.kp.extract_sentences(text)
        
        # "Python is cool!!!"
        # " Java is ok."
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[0][0].strip().endswith("!!!"))

if __name__ == '__main__':
    unittest.main()
