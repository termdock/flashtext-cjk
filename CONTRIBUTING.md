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

## Release SOP

This project uses `maturin` and GitHub Actions for automated releases.

### 1. Prerequisites
- Ensure you have write access to the repository.
- Ensure PyPI Trusted Publishing is configured for this repo.

### 2. Verification
Before releasing, always verify the package locally:
```bash
./scripts/verify_package.sh
```
If this passes (🎉 Package verification PASSED!), you are safe to proceed.

### 3. TestPyPI Release (Optional but Recommended)
To test the packaging process without affecting production:
1. Go to **Actions** tab -> **build-and-publish** workflow.
2. Click **Run workflow** -> Select branch (e.g. `main`) -> Click **Run workflow**.
3. This triggers the `publish-testpypi` job.
4. Verify by installing:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --no-deps flashtext-i18n
   ```

### 4. Production Release
1. Update version in `pyproject.toml`.
2. Create and push a tag starting with `v`:
   ```bash
   git tag v4.0.0
   git push origin v4.0.0
   ```
3. This triggers the `publish-pypi` job automatically.
