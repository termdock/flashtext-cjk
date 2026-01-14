# Changelog

All notable changes to this project will be documented in this file.

## [4.0.0a1] - 2026-01-14

### 🚀 Major Rewrite (The Rust Era)
- **Rust Core**: The entire core logic has been rewritten in Rust (`flashtext-rs`), providing massive performance gains and memory safety.
- **Performance**: Throughput increased by **3x-4x** compared to v3.0 (Python). Match latency is now near-constant regardless of keyword count.
- **Drop-in Compatible**: 100% API compatibility with the original FlashText and v3.x series.

### Added
- **True Unicode Boundaries**: Fixed the long-standing issue where non-ASCII characters (e.g., `é`, `ß`, `Adjancent CJK`) were incorrectly treated as delimiters. Rust's `unicode-segmentation` now handles word boundaries correctly for ALL languages.
- **Universal Wheels**: Pre-compiled binary wheels for **macOS (Intel/Silicon)**, **Windows (x64)**, **Linux (x86_64/aarch64)**, and **Musl Linux (Alpine)**. No Rust compiler needed for users.
- **JSON File Loading**: Native support for loading keywords from JSON files for faster startup.

### Changed
- **Packaging**: Migrated build system to `maturin` + `pyo3`.
- **Minimum Python**: Now requires Python >= 3.8.

## [3.1.1] - 2026-01-13

### Refactoring (Architecture 3.0)
- **Modularization**: Split monolithic `keyword.py` into distinct responsibilities:
  - `flashtext/keyword.py`: High-level API and facade.
  - `flashtext/trie_dict.py`: Data structure operations (pure functions).
  - `flashtext/utils.py`: Algorithms (Levenshtein) and helper utilities.
- **Utils**: Extracted `extract_sentences` and `levensthein` to `utils.py` to reduce class weight.

### Performance
- **Loop Optimization**: Optimized `extract_keywords` hot loop by caching member variables and reducing object creation overhead.
- **Benchmark**: Performance restored to ~0.27s (Case-Sensitive) / 0.29s (Case-Insensitive) on standard corpus.
- **Reverted**: "Internationalized Word Boundaries" (Issue #4) reverted due to 3.5x performance regression. This feature is reopened for future optimized implementation.

### Added
- **Mixed Case Support**: Added ability to mix case-sensitive and case-insensitive keywords in the same processor.
  - Implemented via Multi-Edge Trie (Space-for-Time), removing runtime `lower()` calls.
- **Fuzzy Matching Support**: Added `max_cost` parameter to support Levenshtein distance matching (including CJK support).
- **Keyword Count API**: New `len(keyword_processor)` support to get total unique terms.
- **Replacement Metadata**: `replace_keywords` now supports `span_info=True` to return detailed replacement records.
- **Sentence Extraction**: New `extract_sentences()` API to find sentences containing keywords.
- **Clean Name Mapping**: `add_keyword` now accepts a list of clean names (Issue #11).

### Fixed
- **CJK Support**: Fixed adjacent keyword extraction for Chinese/Japanese/Korean text (Issue #1).
- **Unicode Spans**: Fixed inaccurate span positions when handling Unicode characters that change length during case folding (Issue #2).
- **Edge Cases**:
  - Fixed behavior when removing characters from `non_word_boundaries` (Issue #10).
  - Fixed `replace_keywords` with empty boundary sets (Issue #3).
- **Platform**: Verified Linux aarch64 support (Pure Python).

### Documentation
- Added `CONTRIBUTING.md` with strict performance guidelines.
- Added `benchmark.py` for standardized performance testing.
- Updated `README.md` with new features and benchmark results.
