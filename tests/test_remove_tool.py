#!/usr/bin/env python3
"""
Test script for remove_tool.py functionality.
"""

import subprocess
import sys
from pathlib import Path


def test_remove_tool_help():
    """Test that the remove_tool utility shows help correctly."""
    print("Testing remove_tool help...")

    result = subprocess.run(
        ["python3", "scripts/remove_tool.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Remove tool help failed: {result.stderr}"
    print("✓ Remove tool help works")


def test_remove_tool_validation():
    """Test that the remove_tool utility validates inputs correctly."""
    print("\nTesting remove_tool validation...")

    # Test with non-existent tool
    result = subprocess.run(
        ["python3", "scripts/remove_tool.py", "non-existent-tool"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0, "Remove tool should have rejected non-existent tool"
    print("✓ Remove tool correctly rejected non-existent tool")


def test_remove_tool_structure():
    """Test that the remove_tool script has correct structure."""
    print("\nTesting remove_tool script structure...")

    script_path = Path("scripts/remove_tool.py")
    assert script_path.exists(), "Remove tool script not found"

    # Test that script can be imported (syntax check)
    result = subprocess.run(
        ["python3", "-m", "py_compile", str(script_path)],
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"Remove tool script has syntax errors: {result.stderr}"
    print("✓ Remove tool script syntax is valid")


def main():
    """Run all remove_tool tests."""
    print("=" * 60)
    print("Remove Tool Utility Test")
    print("=" * 60)

    tests = [
        test_remove_tool_help,
        test_remove_tool_validation,
        test_remove_tool_structure,
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
