import time
import random
import string
import re
from flashtext import KeywordProcessor

def generate_random_corpus(num_words=100000):
    words = []
    for _ in range(num_words):
        word = ''.join(random.choices(string.ascii_letters, k=random.randint(3, 10)))
        words.append(word)
    return ' '.join(words)

def benchmark():
    # Setup
    print("Generating corpus...")
    corpus = generate_random_corpus(500000) # 500k words
    possible_chars = string.ascii_letters
    
    keywords = []
    for _ in range(1000):
        kw = ''.join(random.choices(possible_chars, k=random.randint(4, 8)))
        keywords.append(kw)
    
    print(f"Corpus length: {len(corpus)} chars")
    print(f"Keywords count: {len(keywords)}")
    
    # 1. FlashText Case-Insensitive (Mixed Case Optimization)
    kp = KeywordProcessor(case_sensitive=False)
    kp.add_keywords_from_list(keywords)
    
    start_time = time.time()
    kp.extract_keywords(corpus)
    end_time = time.time()
    flashtext_time = end_time - start_time
    print(f"FlashText (Case-Insensitive): {flashtext_time:.4f} seconds")
    
    # 2. FlashText Case-Sensitive
    kp_strict = KeywordProcessor(case_sensitive=True)
    kp_strict.add_keywords_from_list(keywords)
    
    start_time = time.time()
    kp_strict.extract_keywords(corpus)
    end_time = time.time()
    flashtext_strict_time = end_time - start_time
    print(f"FlashText (Case-Sensitive):   {flashtext_strict_time:.4f} seconds")

    # 3. Regex (Baseline comparison)
    # Compile regex for all keywords
    # escaped_keywords = [re.escape(k) for k in keywords]
    # pattern_str = r'\b(' + '|'.join(escaped_keywords) + r')\b'
    # pattern = re.compile(pattern_str, re.IGNORECASE)
    
    # start_time = time.time()
    # pattern.findall(corpus)
    # end_time = time.time()
    # regex_time = end_time - start_time
    # print(f"Regex (Compiled):             {regex_time:.4f} seconds")
    
    # print(f"Speedup vs Regex: {regex_time / flashtext_time:.2f}x")

if __name__ == "__main__":
    benchmark()
