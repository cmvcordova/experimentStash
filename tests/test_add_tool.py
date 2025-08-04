#!/usr/bin/env python3
"""
Test script to verify the plugin utility works correctly.
"""

import subprocess
import sys
from pathlib import Path


def test_plugin_help():
    """Test that the plugin utility shows help correctly."""
    print("Testing plugin help...")
    
    try:
        result = subprocess.run(
            ["python", "scripts/plugin.py", "--help"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Plugin help works")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Plugin help failed: {e.stderr}")
        return False


def test_plugin_validation():
    """Test that the plugin utility validates inputs correctly."""
    print("\nTesting plugin validation...")
    
    # Test with invalid tool name
    try:
        result = subprocess.run(
            ["python", "scripts/plugin.py", "invalid-tool!", "https://github.com/user/tool.git"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print("✓ Plugin correctly rejected invalid tool name")
        else:
            print("✗ Plugin should have rejected invalid tool name")
            return False
    except Exception as e:
        print(f"✗ Plugin validation test failed: {e}")
        return False
    
    # Test with invalid GitHub URL
    try:
        result = subprocess.run(
            ["python", "scripts/plugin.py", "valid-tool", "not-a-github-url"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print("✓ Plugin correctly rejected invalid GitHub URL")
        else:
            print("✗ Plugin should have rejected invalid GitHub URL")
            return False
    except Exception as e:
        print(f"✗ Plugin validation test failed: {e}")
        return False
    
    return True


def test_plugin_structure():
    """Test that the plugin script has correct structure."""
    print("\nTesting plugin script structure...")
    
    plugin_path = Path("scripts/plugin.py")
    if not plugin_path.exists():
        print("✗ Plugin script not found")
        return False
    
    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python", "-m", "py_compile", str(plugin_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Plugin script syntax is valid")
            return True
        else:
            print(f"✗ Plugin script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test plugin script: {e}")
        return False


def main():
    """Run all plugin tests."""
    print("=" * 60)
    print("Plugin Utility Test")
    print("=" * 60)
    
    tests = [
        test_plugin_help,
        test_plugin_validation,
        test_plugin_structure,
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
        print("✓ All plugin tests passed!")
        print("\nThe plugin utility is ready to use!")
        print("\nTry it out:")
        print("python scripts/plugin.py <tool_name> <github_url>")
        return 0
    else:
        print(f"✗ {total - passed} out of {total} plugin tests failed")
        print("\nPlease fix the issues above before using the plugin.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 