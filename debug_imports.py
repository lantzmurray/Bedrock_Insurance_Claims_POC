#!/usr/bin/env python3
import sys
import os

# Add debug logging to understand the import issue
print("=== DEBUG: Import Issue Diagnosis ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Python version: {sys.version}")

# Check if we're in the right directory
if os.path.exists("src"):
    print("✓ Found 'src' directory")
else:
    print("✗ 'src' directory not found")

# Check if config.py exists
if os.path.exists("src/config.py"):
    print("✓ Found 'src/config.py'")
    with open("src/config.py", "r") as f:
        content = f.read()
        if content.strip():
            print(f"  Content length: {len(content)} characters")
            print(f"  First 100 chars: {content[:100]}")
        else:
            print("  ✗ File is empty")
else:
    print("✗ 'src/config.py' not found")

# Check __init__.py
if os.path.exists("src/__init__.py"):
    print("✓ Found 'src/__init__.py'")
elif os.path.exists("src/__init__."):
    print("✗ Found 'src/__init__.' (missing .py extension)")
else:
    print("✗ 'src/__init__.py' not found")

# Try to import config
try:
    sys.path.insert(0, "src")
    import config
    print("✓ Successfully imported 'config' module")
    # Check if the required attributes exist
    required_attrs = ["CLAIM_BUCKET", "CLAIMS_PREFIX", "OUTPUTS_PREFIX", "DOC_EXTRACT_MODEL_ID", "SUMMARY_MODEL_ID"]
    for attr in required_attrs:
        if hasattr(config, attr):
            print(f"  ✓ Found {attr}")
        else:
            print(f"  ✗ Missing {attr}")
except ImportError as e:
    print(f"✗ Failed to import 'config': {e}")

print("=== END DEBUG ===")