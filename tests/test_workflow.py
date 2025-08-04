#!/usr/bin/env python3
"""
Test script to verify experimentStash workflow.
"""

import subprocess
import sys
from pathlib import Path
import yaml


def test_validation():
    """Test the validation script."""
    print("Testing validation script...")

    try:
        subprocess.run(
            ["python3", "scripts/validate_setup.py", "--skip-tool-tests"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✓ Validation script works")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Validation script failed: {e.stderr}")
        return False


def test_config_loading():
    """Test that configs can be loaded."""
    print("\nTesting config loading...")

    try:
        # Test meta.yaml
        with open("configs/meta.yaml", "r") as f:
            yaml.safe_load(f)
        print("✓ meta.yaml loaded successfully")

        # Test example experiment config
        config_file = Path("configs/example_experiment.yaml")
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        print("✓ Example experiment config loaded successfully")

        # Validate config structure
        required_fields = ["tool", "experiment"]
        for field in required_fields:
            if field in config:
                print(f"✓ Found required field: {field}")
            else:
                print(f"✗ Missing required field: {field}")
                return False

        return True

    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False


def test_run_experiment_script():
    """Test the run_experiment script structure."""
    print("\nTesting run_experiment script...")

    script_path = Path("scripts/run_experiment")
    if not script_path.exists():
        print("✗ run_experiment script not found")
        return False

    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ run_experiment script syntax is valid")
            return True
        else:
            print(f"✗ run_experiment script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test run_experiment script: {e}")
        return False


def test_add_tool_script():
    """Test the add_tool script structure."""
    print("\nTesting add_tool script...")

    script_path = Path("scripts/add_tool.py")
    if not script_path.exists():
        print("✗ add_tool.py script not found")
        return False

    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ add_tool.py script syntax is valid")
            return True
        else:
            print(f"✗ add_tool.py script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test add_tool.py script: {e}")
        return False


def test_remove_tool_script():
    """Test the remove_tool script structure."""
    print("\nTesting remove_tool script...")

    script_path = Path("scripts/remove_tool.py")
    if not script_path.exists():
        print("✗ remove_tool.py script not found")
        return False

    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ remove_tool.py script syntax is valid")
            return True
        else:
            print(f"✗ remove_tool.py script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test remove_tool.py script: {e}")
        return False


def test_directory_structure():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")

    required_dirs = ["configs", "notebooks", "outputs", "tools", "scripts"]

    all_exist = True
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ Directory exists: {dir_name}")
        else:
            print(f"✗ Directory missing: {dir_name}")
            all_exist = False

    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("experimentStash Workflow Test")
    print("=" * 60)

    tests = [
        test_directory_structure,
        test_config_loading,
        test_validation,
        test_run_experiment_script,
        test_add_tool_script,
        test_remove_tool_script,
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
        print("\nYour experimentStash is ready to use!")
        print("\nNext steps:")
        print("1. Add a tool: python3 scripts/add_tool.py <tool> <repo_url>")
        print("2. Create experiment configs in configs/")
        print("3. Run experiments: python3 scripts/run_experiment <tool> <config>")
        print("4. Remove tools: python3 scripts/remove_tool.py <tool>")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
