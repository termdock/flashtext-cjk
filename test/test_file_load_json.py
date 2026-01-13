import unittest
import json
import os
from flashtext import KeywordProcessor

class TestFileLoadJSON(unittest.TestCase):
    def setUp(self):
        self.filename = "test_keywords.json"
        
    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_json_loading(self):
        """Test loading keywords from a JSON file."""
        # Create a dummy JSON file
        data = {
            "Color": ["red", "blue", "green"],
            "Vehicle": ["car", "bike"]
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        kp = KeywordProcessor()
        kp.add_keyword_from_file(self.filename)

        # Verify extractions
        self.assertEqual(kp.extract_keywords("I have a red car"), ["Color", "Vehicle"])
        self.assertEqual(kp.extract_keywords("Blue sky"), ["Color"])
    
    def test_json_flat_dict(self):
        """Test loading keywords from a flat JSON dict (key->value)."""
        # Create a dummy JSON file
        data = {
            "apple": "Fruit",
            "carrot": "Vegetable"
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        kp = KeywordProcessor()
        kp.add_keyword_from_file(self.filename)

        self.assertEqual(kp.extract_keywords("apple pie"), ["Fruit"])
        self.assertEqual(kp.extract_keywords("carrot cake"), ["Vegetable"])

    def test_invalid_json(self):
        """Test error handling for invalid JSON."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write("Not valid json")

        kp = KeywordProcessor()
        with self.assertRaises(ValueError): # json.load raise ValueError or JSONDecodeError
            try:
                kp.add_keyword_from_file(self.filename)
            except Exception as e:
                # python 2/3 compatibility for json error
                raise ValueError(e) 

    def test_text_file_still_works(self):
        """Ensure non-json files are still read as text."""
        txt_filename = "test_keywords.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("java=>Language\npython\n")
        
        try:
            kp = KeywordProcessor()
            kp.add_keyword_from_file(txt_filename)
            
            self.assertEqual(kp.extract_keywords("java code"), ["Language"])
            self.assertEqual(kp.extract_keywords("python code"), ["python"])
        finally:
            if os.path.exists(txt_filename):
                os.remove(txt_filename)

if __name__ == '__main__':
    unittest.main()
