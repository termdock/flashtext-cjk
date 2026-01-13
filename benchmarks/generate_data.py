import random
import string
import json
import os

# Configuration
TERM_COUNTS = [1000, 5000, 20000, 100000]
SEEDS = 42
OUTPUT_DIR = "benchmarks/data"

random.seed(SEEDS)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_random_string(length=None):
    if length is None:
        length = random.randint(4, 12)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_terms(count):
    terms = set()
    while len(terms) < count:
        terms.add(generate_random_string())
    return list(terms)

def generate_sentence(length_min, length_max, terms=None, hit_rate=0.0):
    # hit_rate: probability that a "word" is replaced by a term
    # avg word length ~5.
    length = random.randint(length_min, length_max)
    # Generate abstract words
    words = []
    current_len = 0
    while current_len < length:
        if terms and random.random() < hit_rate:
            word = random.choice(terms)
        else:
            word = generate_random_string(random.randint(2, 8))
        words.append(word)
        current_len += len(word) + 1
    return " ".join(words)[:length]

def main():
    ensure_dir(OUTPUT_DIR)
    
    # 1. Generate Terms
    print("Generating Terms...")
    all_terms = generate_terms(max(TERM_COUNTS))
    
    for count in TERM_COUNTS:
        subset = all_terms[:count]
        path = f"{OUTPUT_DIR}/terms_{count}.json"
        with open(path, 'w') as f:
            json.dump(subset, f)
        print(f"Saved {path}")

    # 2. Generate Corpus
    # Need to use 'all_terms' to ensure hits for "High Hit" scenarios
    # But real scenario: Terms might match or not.
    # We will use the Largest Term Set for generating hits? 
    # Or generating corpus independent of terms?
    # User said: "Hit Rates: Low vs High".
    # This implies the corpus content depends on the Terms we search.
    # We should generate ONE corpus, but "High Hit" version embeds words from `all_terms`.
    
    print("Generating Corpora...")
    
    # Scenarios
    scenarios = [
        ("short_low", 10000, 60, 0.001), # 10k lines
        ("short_high", 10000, 60, 0.2),  # 10k lines
        ("long_low", 200, 100000, 0.001), # 200 docs
        ("long_high", 200, 100000, 0.2),  # 200 docs
    ]
    # Note: Reducing size slightly to avoid 300MB+ generation time during interactive session.
    # 100k lines * 60 = 6MB. 
    # 2k * 100KB = 200MB.
    # I will stick to these sizes as "Standard".
    
    for name, count, size, hit_rate in scenarios:
        path = f"{OUTPUT_DIR}/corpus_{name}.txt"
        print(f"Generating {name} ({count} items)...")
        with open(path, 'w') as f:
            for _ in range(count):
                if "short" in name:
                    line = generate_sentence(30, 80, all_terms, hit_rate)
                    f.write(line + "\n")
                else:
                    # Long doc
                    doc = generate_sentence(size, size, all_terms, hit_rate)
                    f.write(doc + "\n")
        print(f"Saved {path}")

if __name__ == "__main__":
    main()
