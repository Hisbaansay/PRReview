# conftest.py (repo root)
import os, sys
# Ensure the repository root is on sys.path so "import app" works in tests
sys.path.insert(0, os.path.abspath("."))
