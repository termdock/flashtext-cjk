import sys
import unittest
import os

# 1. Force load Rust extension
try:
    import flashtext_rs
    print("✅ Rust extension found: flashtext_rs")
except ImportError:
    print("❌ Rust extension not found. Did you run 'maturin develop'?")
    sys.exit(1)

# 2. Monkeypatch flashtext BEFORE tests import it
# We need to load 'flashtext' package structure first without full import if possible,
# or just patch it in sys.modules logic.
# Simpler: Import flashtext, then overwrite the attribute.

import flashtext
print(f"Original KeywordProcessor: {flashtext.KeywordProcessor}")

# Capture original for reference if needed, but we want to fail if Rust behaves unlike Python
flashtext.KeywordProcessor = flashtext_rs.KeywordProcessor
print(f"Patched  KeywordProcessor: {flashtext.KeywordProcessor}")

# Also patch the module 'flashtext.keyword' because tests "from flashtext.keyword import KeywordProcessor"
import flashtext.keyword
flashtext.keyword.KeywordProcessor = flashtext_rs.KeywordProcessor

# 3. Discover and run tests
loader = unittest.TestLoader()
start_dir = 'test'
suite = loader.discover(start_dir, pattern='test_*.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if not result.wasSuccessful():
    sys.exit(1)
