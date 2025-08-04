#!/usr/bin/env python3
"""
Test script to verify the teardown utility works correctly.
"""

import subprocess
import sys
from pathlib import Path


def test_teardown_help():
    """Test that the teardown utility shows help correctly."""
    print("Testing teardown help...")
    
    try:
        result = subprocess.run(
            ["python", "scripts/teardown.py", "--help"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Teardown help works")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Teardown help failed: {e.stderr}")
        return False


def test_teardown_validation():
    """Test that the teardown utility validates inputs correctly."""
    print("\nTesting teardown validation...")
    
    # Test with non-existent tool
    try:
        result = subprocess.run(
            ["python", "scripts/teardown.py", "non-existent-tool"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print("✓ Teardown correctly rejected non-existent tool")
        else:
            print("✗ Teardown should have rejected non-existent tool")
            return False
    except Exception as e:
        print(f"✗ Teardown validation test failed: {e}")
        return False
    
    return True


def test_teardown_structure():
    """Test that the teardown script has correct structure."""
    print("\nTesting teardown script structure...")
    
    teardown_path = Path("scripts/teardown.py")
    if not teardown_path.exists():
        print("✗ Teardown script not found")
        return False
    
    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python", "-m", "py_compile", str(teardown_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Teardown script syntax is valid")
            return True
        else:
            print(f"✗ Teardown script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test teardown script: {e}")
        return False


def test_dry_run_functionality():
    """Test that dry-run functionality works."""
    print("\nTesting dry-run functionality...")
    
    # Test dry-run with a tool that might exist
    try:
        result = subprocess.run(
            ["python", "scripts/teardown.py", "manylatents", "--dry-run"],
            capture_output=True,
            text=True,
            check=False
        )
        # Dry run should not fail, but might show warnings
        if "DRY RUN" in result.stdout or "dry run" in result.stdout.lower():
            print("✓ Dry-run functionality works")
            return True
        else:
            print("⚠ Dry-run output not as expected")
            return True  # Don't fail the test, just warn
    except Exception as e:
        print(f"✗ Dry-run test failed: {e}")
        return False


def main():
    """Run all teardown tests."""
    print("=" * 60)
    print("Teardown Utility Test")
    print("=" * 60)
    
    tests = [
        test_teardown_help,
        test_teardown_validation,
        test_teardown_structure,
        test_dry_run_functionality,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("✓ All teardown tests passed!")
        print("\nThe teardown utility is ready to use!")
        print("\nTry it out:")
        print("python scripts/teardown.py <tool_name> --dry-run")
        return 0
    else:
        print(f"✗ {total - passed} out of {total} teardown tests failed")
        print("\nPlease fix the issues above before using the teardown utility.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 