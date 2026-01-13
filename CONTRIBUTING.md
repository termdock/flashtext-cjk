# Contributing to FlashText

## Core Philosophy: Performance First
FlashText is designed to be an extremely fast (O(N)) keyword extraction library. 
**Performance is our most critical feature.** We prioritize speed over "syntactic sugar" or non-critical features that introduce runtime overhead.

## Development Rules

### 1. Always Benchmark
Any changes to the core logic (`flashtext/keyword.py`) MUST be verified with `benchmark.py`.

**Procedure:**
1. Run `python3 benchmark.py` on the current `dev` branch to establish a baseline.
2. Apply your changes.
3. Run `python3 benchmark.py` again.
4. If your changes cause a **regression (>5%)**, you must optimize your code or justify the cost. 
   - *Example: A 3x slowdown for "better internationalization" is unresponsive and will be rejected (see Issue #4).*

### 2. Zero Runtime Overhead for "Opt-in" Features
If a feature is optional (e.g., `span_info=True`), it should impose **zero cost** when disabled.
- Avoid unconditional function calls inside the hot loop.
- Use flags or separate code paths if necessary.

### 3. Testing
Ensure all unit tests pass:
```bash
python3 -m pytest
```
