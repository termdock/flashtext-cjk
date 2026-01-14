# FlashText i18n

[English](README.md) | [繁體中文](README_zh-TW.md)

A maintained fork of [FlashText](https://github.com/vi3k6i5/flashtext) with internationalization and Unicode fixes.

[![PyPI version](https://badge.fury.io/py/flashtext-i18n.svg)](https://badge.fury.io/py/flashtext-i18n)
[![Python Versions](https://img.shields.io/pypi/pyversions/flashtext-i18n.svg)](https://pypi.org/project/flashtext-i18n/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why This Fork?

The original FlashText is no longer actively maintained and has several bugs with international text:

- **CJK languages**: Adjacent keywords not extracted (Chinese, Japanese, Korean)
- **Unicode case folding**: Wrong span positions for characters like Turkish `İ`
- **Non-ASCII boundaries**: Various edge cases with international characters

This fork aims to fix these issues while maintaining full API compatibility.

## Version History

### v4.0.0 (Rust Core) - *Alpha Released*

**Performance**
- **Rust Core**: Massive throughput improvement (~3-4x faster than Python).
- **Scalability**: Near-constant match time even with 100k+ keywords.
- **Compatibility**: 100% Drop-in replacement for Python API.

**New Features**
- **International Word Boundaries**: Unicode-aware boundary detection.
- **Load Keywords from File**: Support for JSON/Text files.
- **Mixed Case Support**: Case-sensitive and Case-insensitive coexistence.
- **Fuzzy Matching**: Optional Levenshtein support.
- **New APIs**: Extract sentences, replacement metadata.

### v3.0.0 (Python Core) - *Released*
- **Unicode case folding**: Correct spans for Turkish `İ` and German `ß`
- **Numbers**: Keywords followed by numbers are now extracted correctly
- **CJK Support**: Adjacent keywords (Chinese/Japanese) now extracted correctly

## Feature Highlights

### International Word Boundaries (v4.0)

The original FlashText only supported ASCII characters (`A-Za-z0-9_`) as word parts. This caused issues for many languages where characters like `é`, `ß`, or `ç` were treated as delimiters, breaking words apart.

**v4.0 Fix**: All valid Unicode alphanumeric characters are now treated as part of a word by default.

```python
# Hindi (Devanagari)
kp.add_keyword('नमस्ते')
kp.extract_keywords('नमस्ते दुनिया') 
# ✅ ['नमस्ते'] (Previously failed)

# French/German
kp.add_keyword('café')
kp.extract_keywords('I went to a café.') 
# ✅ ['café'] (Previously extracted 'caf')
```

### CJK Adjacent Keywords (v3.0)

```python
from flashtext import KeywordProcessor

kp = KeywordProcessor()
kp.add_keyword('雅詩蘭黛')  # Estée Lauder
kp.add_keyword('小棕瓶')    # Advanced Night Repair

text = '推薦雅詩蘭黛小棕瓶超好用'
result = kp.extract_keywords(text)
# Original FlashText: ['雅詩蘭黛']  ❌ Missing '小棕瓶'
# FlashText i18n:     ['雅詩蘭黛', '小棕瓶']  ✅ Both extracted!
```

### Loading Keywords from File (v4.0)

You can now load keywords directly from JSON or text files.

```python
# keywords.json
# {
#    "Color": ["red", "blue", "green"],
#    "Vehicle": ["car", "bike"]
# }

kp.add_keywords_from_file('keywords.json')
```

## Installation

```bash
pip install flashtext-i18n
```

> **Note**: This package provides a drop-in replacement module named `flashtext`. Please **uninstall** the original `flashtext` package first to avoid conflicts.
> ```bash
> pip uninstall -y flashtext
> pip uninstall -y flashtext-i18n # optional cleanup
> pip install -U flashtext-i18n
> ```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install flashtext-i18n
```

Or install from GitHub:

```bash
pip install git+https://github.com/termdock/flashtext-i18n.git
```

## Usage

The API is 100% compatible with the original FlashText:

```python
from flashtext import KeywordProcessor

# Create processor
kp = KeywordProcessor()

# Add keywords
kp.add_keyword('Python')
kp.add_keyword('機器學習', 'Machine Learning')

# Extract keywords
text = 'I love Python and 機器學習'
keywords = kp.extract_keywords(text)
# ['Python', 'Machine Learning']

# Extract with span info
keywords_with_span = kp.extract_keywords(text, span_info=True)
# [('Python', 7, 13), ('Machine Learning', 18, 22)]

# Replace keywords
new_text = kp.replace_keywords(text)
# 'I love Python and Machine Learning'

# Get replacement details (New in v4.0)
new_text, replacements = kp.replace_keywords(text, span_info=True)
# replacements = [
#     {'original': 'Python', 'replacement': 'Python', 'start': 7, 'end': 13},
#     {'original': '機器學習', 'replacement': 'Machine Learning', 'start': 18, 'end': 22}
# ]


# Extract sentences with keywords (New in v4.0)
sentences = kp.extract_sentences(text)
# [('I love Python and 機器學習', ['Python', 'Machine Learning'])]

# Get keyword count
print(len(kp))
# 2

# One keyword matching multiple Tags (New in v4.0)
kp.add_keyword('Apple', ['Fruit', 'Tech'])
keywords = kp.extract_keywords('I have an Apple')
# ['Fruit', 'Tech']

# Mixed Case Support (Case-Sensitive & Case-Insensitive) (New in v4.0)
# Default: case_sensitive=False (Global)
kp = KeywordProcessor()

# Add a case-insensitive keyword (matches 'banana', 'Banana', 'BANANA')
kp.add_keyword('banana')

# Add a case-sensitive keyword (matches 'Apple' ONLY)
kp.add_keyword('Apple', case_sensitive=True)

keywords_found = kp.extract_keywords('I like Apple and Banana.')
# ['Apple', 'banana']

keywords_found = kp.extract_keywords('I like apple and BANANA.')
# ['banana'] (Strict 'Apple' does not match 'apple')

> **Note**: **Shared Trie Path Tradeoff**. If you add `Apple` (Case-Sensitive) and `apple` (Insensitive), they share the path a-p-p-l-e. The last definition wins. **Recommendation**: Add case-sensitive keywords *after* case-insensitive ones if strict separation is needed.

### Fuzzy Matching (Levenshtein Distance)

FlashText supports fuzzy matching to handle typos.

> **Warning**: Fuzzy matching introduces additional Levenshtein distance calculation overhead, making it **significantly slower** than exact matching. Use only when necessary.

Use `max_cost` to specify the maximum allowable Levenshtein distance.

```python
kp = KeywordProcessor()
kp.add_keyword('Machine Learning')

# Exact match
kp.extract_keywords('I love Machine Learning')
# ['Machine Learning']

# Fuzzy match (max_cost=2) -> Matches "Mchine Larning" (2 deletions)
kp.extract_keywords('I love Mchine Larning', max_cost=2)
# ['Machine Learning']

# Fuzzy match for CJK (New in v4.0)
kp.add_keyword('人工智慧')
# Matches "人工智障" (1 substitution)
kp.extract_keywords('這有人工智障功能', max_cost=1)
# ['人工智慧']
```

## Performance (v4.0 Rust Core)

Comparison of **FlashText 4.0 (Rust)**, **FlashText 3.0 (Python)**, and **Regex (compiled)**.

### Benchmark Methodology

- **Corpus**: 10,000 lines (Short sentences, simulated natural language).
- **Terms**: 1,000 to 100,000 unique keywords.
- **Metric**: Median Match Time (Seconds) over 10 iterations (Warmup enabled).
- **Environment**: Apple Silicon (M1/M2/M3), Python 3.11.

### Results: Keyword Extraction Time (Lower is Better)

| Keywords | Rust (v4.0) | Python (v3.0) | Regex | Speedup (vs Py) | Speedup (vs Re) |
|---------:|------------:|--------------:|------:|----------------:|----------------:|
| 1,000    | **0.012s**  | 0.043s        | 0.92s | **3.6x**        | 76x             |
| 5,000    | **0.013s**  | 0.042s        | 4.80s | **3.2x**        | 369x            |
| 20,000   | **0.018s**  | 0.046s        | 19.16s| **2.6x**        | **1064x**       |
| 100,000  | **0.021s**  | 0.056s        | N/A   | **2.7x**        | N/A             |

> **Note**: Rust match latency remains **nearly constant** as keyword count scales from 1k to 100k (on this corpus). Regex performance degrades sharply as the number of alternations grows, making it unsuitable for large keyword sets. Rust reduces per-character overhead and memory allocations, resulting in a consistent **2.6x to 3.6x** speedup over the Python implementation.

![Match Time ![Benchmark](docs/img/benchmark.png)/match_time_short_low.png)
*(Figure 1: Comparison vs Regex - Rust is 1000x faster)*

![Match Time Rust vs Python](docs/img/match_time_short_low_no_regex.png)
*(Figure 2: Comparison vs Python - Rust is ~3x faster and scales better)*

### Build Time (Index Construction)

| Keywords | Rust (v4.0) | Python (v3.0) |
|---------:|------------:|--------------:|
| 100,000  | **0.08s**   | 0.17s         |

Rust constructs the keyword trie index 2x faster than Python.
*(Build time measured on the same machine, release build, 10 iterations)*

## Roadmap

See [Issues](https://github.com/termdock/flashtext-i18n/issues) for planned fixes:

- [x] Unicode case folding span fix (Turkish İ, German ß) (Fixed in v3.0.0)
- [x] Keywords followed by numbers extraction (Fixed in v3.0.0)
- [x] Internationalized word boundary detection (Fixed in v4.0)
- [x] Indian languages (Devanagari) support (Fixed in v4.0)
- [x] Load keywords from JSON/Text file (Fixed in v4.0)

## Credits

This project is a fork of [FlashText](https://github.com/vi3k6i5/flashtext) created by [Vikash Singh](https://github.com/vi3k6i5).

The original FlashText algorithm is described in the paper: [Replace or Retrieve Keywords In Documents at Scale](https://arxiv.org/abs/1711.00046)

## License

MIT License - see [LICENSE](LICENSE) file.

The original copyright belongs to Vikash Singh (2017). This fork is maintained by [termdock](https://github.com/termdock) & Huang Chung Yi.
