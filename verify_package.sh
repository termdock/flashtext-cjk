#!/bin/bash
set -e

echo "🔹 Cleaning previous builds..."
rm -rf dist target/wheels .venv_verify

echo "🔹 Building fresh release wheels..."
maturin build --release

echo "🔹 Creating fresh verification venv..."
python3 -m venv .venv_verify
source .venv_verify/bin/activate

echo "🔹 Installing the generated wheel..."
# Find the wheel file (taking the first one found in target/wheels)
WHEEL_FILE=$(find target/wheels -name "*.whl" | head -n 1)
pip install "$WHEEL_FILE"

echo "🔹 Verifying installation..."
python -c "
import flashtext
print(f'✅ Successfully imported flashtext from {flashtext.__file__}')
print(f'✅ Rust module version: {flashtext.__version__ if hasattr(flashtext, \"__version__\") else \"N/A\"}')
print(f'✅ Rust hello check: {flashtext.hello()}')

from flashtext import KeywordProcessor
kp = KeywordProcessor()
kp.add_keyword('Big Apple', 'New York')
res = kp.extract_keywords('I love Big Apple')
if res == ['New York']:
    print('✅ KeywordProcessor logic verified')
else:
    raise Exception(f'❌ Logic Verification Failed: {res}')
"

echo "🎉 Package verification PASSED! You are ready to ship."
deactivate
rm -rf .venv_verify:
