# FlashText i18n

A maintained fork of [FlashText](https://github.com/vi3k6i5/flashtext) with internationalization and Unicode fixes.

[![PyPI version](https://badge.fury.io/py/flashtext-i18n.svg)](https://badge.fury.io/py/flashtext-i18n)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why This Fork?

The original FlashText is no longer actively maintained and has several bugs with international text:

- **CJK languages**: Adjacent keywords not extracted (Chinese, Japanese, Korean)
- **Unicode case folding**: Wrong span positions for characters like Turkish `İ`
- **Non-ASCII boundaries**: Various edge cases with international characters

This fork aims to fix these issues while maintaining full API compatibility.

## Fixed in v2.8.0

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
```

## Installation

```bash
pip install flashtext-i18n
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
```

## Performance

FlashText uses the Aho-Corasick algorithm with O(n) time complexity, making it extremely fast for keyword extraction from large texts.

| Benchmark | FlashText | Regex |
|-----------|-----------|-------|
| 1000 keywords, 1M chars | ~0.1s | ~10s+ |

## Roadmap

See [Issues](https://github.com/termdock/flashtext-i18n/issues) for planned fixes:

- [ ] Unicode case folding span fix (Turkish İ, German ß)
- [ ] Keywords followed by numbers extraction
- [ ] Internationalized word boundary detection
- [ ] Indian languages (Devanagari) support

## Credits

This project is a fork of [FlashText](https://github.com/vi3k6i5/flashtext) created by [Vikash Singh](https://github.com/vi3k6i5).

The original FlashText algorithm is described in the paper: [Replace or Retrieve Keywords In Documents at Scale](https://arxiv.org/abs/1711.00046)

## License

MIT License - see [LICENSE](LICENSE) file.

The original copyright belongs to Vikash Singh (2017). This fork is maintained by [termdock](https://github.com/termdock).
