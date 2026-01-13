# FlashText i18n

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

## Fixed in v3.0.0

### International Word Boundaries (New in v3.1.0-dev)

The original FlashText only supported ASCII characters (`A-Za-z0-9_`) as word parts. This caused issues for many languages where characters like `é`, `ß`, or `ç` were treated as delimiters, breaking words apart.

**Fixed in v3.1.0**: All valid Unicode alphanumeric characters are now treated as part of a word by default.

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

### CJK Adjacent Keywords

```python
from flashtext import KeywordProcessor

kp = KeywordProcessor()
kp.add_keyword('雅詩蘭黛')  # Estée Lauder
kp.add_keyword('小棕瓶')    # Advanced Night Repair

text = '推薦雅詩蘭黛小棕瓶超好用'
result = kp.extract_keywords(text)
# Original FlashText: ['雅詩蘭黛']  ❌ Missing '小棕瓶'
# FlashText i18n:     ['雅詩蘭黛', '小棕瓶']  ✅ Both extracted!
### Loading Keywords from File (New in v3.1.0-dev)

You can now load keywords directly from JSON or text files.

```python
# keywords.json
# {
#    "Color": ["red", "blue", "green"],
#    "Vehicle": ["car", "bike"]
# }

kp.add_keyword_from_file('keywords.json')
```

## Installation

```bash
pip install flashtext-i18n
```

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

# Get replacement details (New in v3.1.0)
new_text, replacements = kp.replace_keywords(text, span_info=True)
# replacements = [
#     {'original': 'Python', 'replacement': 'Python', 'start': 7, 'end': 13},
#     {'original': '機器學習', 'replacement': 'Machine Learning', 'start': 18, 'end': 22}
# ]


# Extract sentences with keywords (New in v3.1.0)
sentences = kp.extract_sentences(text)
# [('I love Python and 機器學習', ['Python', 'Machine Learning'])]

# Get keyword count
print(len(kp))
# 2
```

## Performance

FlashText uses the Aho-Corasick algorithm with O(n) time complexity, making it extremely fast for keyword extraction from large texts.

| Benchmark | FlashText | Regex |
|-----------|-----------|-------|
| 1000 keywords, 1M chars | ~0.1s | ~10s+ |

## Roadmap

See [Issues](https://github.com/termdock/flashtext-i18n/issues) for planned fixes:

- [x] Unicode case folding span fix (Turkish İ, German ß) (Fixed in v3.0.0)
- [x] Keywords followed by numbers extraction (Fixed in v3.0.0)
- [x] Internationalized word boundary detection (Fixed in v3.1.0)
- [x] Indian languages (Devanagari) support (Fixed in v3.1.0)
- [x] Load keywords from JSON/Text file (Fixed in v3.1.0)

## Credits

This project is a fork of [FlashText](https://github.com/vi3k6i5/flashtext) created by [Vikash Singh](https://github.com/vi3k6i5).

The original FlashText algorithm is described in the paper: [Replace or Retrieve Keywords In Documents at Scale](https://arxiv.org/abs/1711.00046)

## License

MIT License - see [LICENSE](LICENSE) file.

The original copyright belongs to Vikash Singh (2017). This fork is maintained by [termdock](https://github.com/termdock) & Huang Chung Yi.
