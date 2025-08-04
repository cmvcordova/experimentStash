#!/usr/bin/env python3
"""
Test script for add_tool.py functionality.
"""

import subprocess
import sys
from pathlib import Path


def test_add_tool_help():
    """Test that the add_tool utility shows help correctly."""
    print("Testing add_tool help...")

    try:
        subprocess.run(
            ["python3", "scripts/add_tool.py", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✓ Add tool help works")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Add tool help failed: {e.stderr}")
        return False


def test_add_tool_validation():
    """Test that the add_tool utility validates inputs correctly."""
    print("\nTesting add_tool validation...")

    # Test with invalid tool name
    try:
        result = subprocess.run(
            [
                "python3",
                "scripts/add_tool.py",
                "invalid-tool!",
                "https://github.com/user/tool.git",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print("✓ Add tool correctly rejected invalid tool name")
        else:
            print("✗ Add tool should have rejected invalid tool name")
            return False
    except Exception as e:
        print(f"✗ Add tool validation test failed: {e}")
        return False

    # Test with invalid GitHub URL
    try:
        result = subprocess.run(
            ["python3", "scripts/add_tool.py", "valid-tool", "not-a-github-url"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print("✓ Add tool correctly rejected invalid GitHub URL")
        else:
            print("✗ Add tool should have rejected invalid GitHub URL")
            return False
    except Exception as e:
        print(f"✗ Add tool validation test failed: {e}")
        return False

    return True


def test_add_tool_structure():
    """Test that the add_tool script has correct structure."""
    print("\nTesting add_tool script structure...")

    script_path = Path("scripts/add_tool.py")
    if not script_path.exists():
        print("✗ Add tool script not found")
        return False

    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ Add tool script syntax is valid")
            return True
        else:
            print(f"✗ Add tool script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test add tool script: {e}")
        return False


def main():
    """Run all add_tool tests."""
    print("=" * 60)
    print("Add Tool Utility Test")
    print("=" * 60)

    tests = [
        test_add_tool_help,
        test_add_tool_validation,
        test_add_tool_structure,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
