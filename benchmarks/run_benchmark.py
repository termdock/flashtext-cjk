
import time
import json
import re
import os
import gc
import statistics
import sys
import psutil
from collections import defaultdict

# Add current directory to path to find local flashtext package
sys.path.append(os.getcwd())

# Implementations
try:
    import flashtext
    print(f"✅ Found FlashText Python: {flashtext.__file__}")
except ImportError:
    flashtext = None
    print("❌ FlashText Python NOT found")

import flashtext_rs
print(f"✅ Found FlashText Rust: {flashtext_rs}")

# Configuration
DATA_DIR = "benchmarks/data"
OUTPUT_FILE = "benchmarks/results.json"
WARMUP = 2
ITERATIONS = 10

def load_terms(count):
    with open(f"{DATA_DIR}/terms_{count}.json", 'r') as f:
        return json.load(f)

def load_corpus(name):
    path = f"{DATA_DIR}/corpus_{name}.txt"
    with open(path, 'r') as f:
        return f.read()

class BenchmarkSuite:
    def __init__(self):
        self.results = []

    def measure(self, name, func, *args):
        # Warmup
        for _ in range(WARMUP):
            func(*args)
        
        times = []
        gc.disable()
        for _ in range(ITERATIONS):
            start = time.perf_counter()
            count = func(*args)
            end = time.perf_counter()
            times.append(end - start)
        gc.enable()
        
        return times, count

    def run_scenarios(self):
        term_files = [1000, 5000, 20000, 100000]
        # For quick MVP, let's pick specific scenarios to avoid 1 hour run
        # Short Low, Short High, Long Low.
        corpora = ["short_low", "short_high"] 
        
        for term_count in term_files:
            print(f"--- Terms: {term_count} ---")
            terms = load_terms(term_count)
            
            # 1. Build Time
            # Rust
            setup_rs = lambda: flashtext_rs.KeywordProcessor()
            def build_rs(kp):
                 for t in terms: kp.add_keyword(t)
                 return 0
            
            times, _ = self.measure("Rust Build", lambda: build_rs(setup_rs()))
            self.record("Rust", term_count, "Build", None, times)
            
            # Python
            if flashtext:
                setup_py = lambda: flashtext.KeywordProcessor()
                def build_py(kp):
                    kp.add_keywords_from_list(terms)
                    return 0
                times, _ = self.measure("Python Build", lambda: build_py(setup_py()))
                self.record("Python", term_count, "Build", None, times)

            # Regex Build
            def build_re():
                pattern = re.compile(r'\b(' + '|'.join(map(re.escape, terms)) + r')\b', re.IGNORECASE)
                return 0
            # Warning: 100k terms regex compile is SLOW/Crash?
            if term_count <= 20000:
                times, _ = self.measure("Regex Build", build_re)
                self.record("Regex", term_count, "Build", None, times)
            
            # 2. Match Time
            for corpus_name in corpora:
                print(f"  Corpus: {corpus_name}")
                text = load_corpus(corpus_name)
                
                # Setup Processors once
                kp_rs = setup_rs()
                for t in terms: kp_rs.add_keyword(t)
                
                if flashtext:
                    kp_py = setup_py()
                    kp_py.add_keywords_from_list(terms)
                
                if term_count <= 20000:
                    pat = re.compile(r'\b(' + '|'.join(map(re.escape, terms)) + r')\b', re.IGNORECASE)

                # Rust Match
                # Counting matches to avoid I/O
                # Using extract_keywords and len()
                def match_rs():
                    # flashtext_rs returns list of strings. 
                    # Allocate only the list backbone?
                    # Ideally we want a method that just counts? 
                    # But extract_keywords is what we benchmark.
                    return len(kp_rs.extract_keywords(text))
                
                times, count_rs = self.measure("Rust Match", match_rs)
                self.record("Rust", term_count, "Match", corpus_name, times, count=count_rs)
                
                # Python Match
                if flashtext:
                    def match_py():
                        return len(kp_py.extract_keywords(text))
                    times, count_py = self.measure("Python Match", match_py)
                    self.record("Python", term_count, "Match", corpus_name, times, count=count_py)
                
                # Regex Match
                if term_count <= 20000:
                    def match_re():
                        return len(pat.findall(text))
                    times, count_re = self.measure("Regex Match", match_re)
                    self.record("Regex", term_count, "Match", corpus_name, times, count=count_re)

    def record(self, engine, terms, metric, corpus, times, count=0):
        median = statistics.median(times)
        p95 = statistics.quantiles(times, n=20)[18] # approx 95th percentile
        res = {
            "engine": engine,
            "terms": terms,
            "metric": metric,
            "corpus": corpus,
            "median": median,
            "p95": p95,
            "count": count
        }
        self.results.append(res)
        print(f"    {engine}: {median:.4f}s (P95: {p95:.4f}s) Count: {count}")

    def save(self):
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(self.results, f, indent=2)
            
if __name__ == "__main__":
    b = BenchmarkSuite()
    b.run_scenarios()
    b.save()
