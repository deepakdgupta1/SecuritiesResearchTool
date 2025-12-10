#!/bin/bash

# Python Linting Auto-Fix Script
# This script automatically fixes most flake8 and some mypy issues

set -e  # Exit on error

echo "======================================"
echo "Python Auto-Linting Fix Script"
echo "======================================"
echo ""

# Define directories to exclude
EXCLUDE_DIRS=".venv,venv,env,.git,__pycache__,.mypy_cache,build,dist,.eggs,*.egg-info"

echo "Step 1: Installing required tools (if not already installed)..."
pip install -q autopep8 autoflake black isort flake8 mypy 2>/dev/null || true
echo "✓ Tools ready"
echo ""

echo "Step 2: Removing unused imports and variables..."
autoflake \
  --in-place \
  --remove-all-unused-imports \
  --remove-unused-variables \
  --remove-duplicate-keys \
  --recursive . \
  --exclude "$EXCLUDE_DIRS"
echo "✓ Removed unused imports and variables"
echo ""

echo "Step 3: Sorting imports..."
isort . \
  --skip .venv \
  --skip venv \
  --skip env \
  --profile black
echo "✓ Imports sorted"
echo ""

echo "Step 4: Formatting with black (line length: 79)..."
black . \
  --line-length 79 \
  --exclude "/(\.venv|venv|env|\.git|__pycache__|\.mypy_cache|build|dist|\.eggs)/"
echo "✓ Code formatted with black"
echo ""

echo "Step 5: Fixing remaining PEP 8 style issues with autopep8..."
autopep8 \
  --in-place \
  --aggressive \
  --aggressive \
  --recursive . \
  --max-line-length 79 \
  --exclude "$EXCLUDE_DIRS"
echo "✓ PEP 8 style issues fixed"
echo ""

echo "Step 6: Final pass - aggressive line breaking..."
autopep8 \
  --in-place \
  --aggressive \
  --aggressive \
  --aggressive \
  --recursive . \
  --max-line-length 79 \
  --select=E501 \
  --exclude "$EXCLUDE_DIRS"
echo "✓ Long lines fixed"
echo ""

echo "======================================"
echo "Auto-fixing complete!"
echo "======================================"
echo ""

echo "Running final checks..."
echo ""

echo "--- Remaining flake8 issues ---"
flake8 . --exclude="$EXCLUDE_DIRS" --count --statistics || echo "No flake8 issues found!"
echo ""

echo "--- Remaining mypy issues ---"
mypy . --exclude "$EXCLUDE_DIRS" --no-error-summary 2>&1 | head -n 50 || echo "No mypy issues found!"
echo ""

echo "======================================"
echo "Summary:"
echo "======================================"
echo "✓ Auto-fixable issues have been resolved"
echo "✗ Remaining issues (shown above) require manual fixes:"
echo "  - Type annotations (mypy errors)"
echo "  - Complex logic issues"
echo "  - Third-party library stubs"
echo ""
echo "To see full error reports, run:"
echo "  flake8 . --exclude='$EXCLUDE_DIRS' > flake8_errors.txt"
echo "  mypy . --exclude '$EXCLUDE_DIRS' > mypy_errors.txt"
echo ""