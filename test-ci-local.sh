#!/bin/bash
set -e

echo "🧪 Simulating CI workflow locally..."
echo ""

echo "===== Step 1: Install dependencies ====="
uv sync --all-extras
echo ""

echo "===== Step 2: Ruff check (lint) ====="
time uv run ruff check src/ tests/
echo ""

echo "===== Step 3: Ruff format check ====="
time uv run ruff format --check src/ tests/
echo ""

echo "===== Step 4: Run tests with coverage ====="
time uv run pytest tests/ -v --cov=math_mcp --cov-report=term-missing
echo ""

echo "✅ All CI checks passed!"
