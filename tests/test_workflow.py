#!/usr/bin/env python3
"""
Test script to verify experimentStash workflow.
"""

import subprocess
import sys
import os
from pathlib import Path
import yaml


def test_validation():
    """Test the validation script."""
    print("Testing validation script...")
    
    try:
        result = subprocess.run(
            ["python", "scripts/validate_setup.py", "--skip-tool-tests"],
            capture_output=True,
            text=True,
            check=True
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
        with open("configs/meta.yaml", 'r') as f:
            meta = yaml.safe_load(f)
        print("✓ meta.yaml loaded successfully")
        
        # Test experiment config
        config_file = Path("configs/figure1_method_comparison/pca_swissroll.yaml")
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        print("✓ Experiment config loaded successfully")
        
        # Validate config structure
        required_fields = ['tool', 'experiment']
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
            ["python", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True
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


def test_plugin_script():
    """Test the plugin script structure."""
    print("\nTesting plugin script...")
    
    script_path = Path("scripts/plugin.py")
    if not script_path.exists():
        print("✗ plugin.py script not found")
        return False
    
    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ plugin.py script syntax is valid")
            return True
        else:
            print(f"✗ plugin.py script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test plugin.py script: {e}")
        return False


def test_teardown_script():
    """Test the teardown script structure."""
    print("\nTesting teardown script...")
    
    script_path = Path("scripts/teardown.py")
    if not script_path.exists():
        print("✗ teardown.py script not found")
        return False
    
    # Test that script can be imported (syntax check)
    try:
        result = subprocess.run(
            ["python", "-m", "py_compile", str(script_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ teardown.py script syntax is valid")
            return True
        else:
            print(f"✗ teardown.py script has syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test teardown.py script: {e}")
        return False


def test_directory_structure():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "configs",
        "notebooks", 
        "outputs",
        "tools",
        "scripts"
    ]
    
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
        test_plugin_script,
        test_teardown_script,
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
        print("✓ All tests passed!")
        print("\nYour experimentStash is ready to use!")
        print("\nNext steps:")
        print("1. Set up tool environments: cd tools/manylatents && uv sync")
        print("2. Run experiments: python scripts/run_experiment manylatents figure1_method_comparison/pca_swissroll")
        print("3. Add more tools: python scripts/plugin.py <tool> <repo_url>")
        print("4. Remove tools: python scripts/teardown.py <tool>")
        return 0
    else:
        print(f"✗ {total - passed} out of {total} tests failed")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 