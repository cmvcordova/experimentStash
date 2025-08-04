#!/usr/bin/env python3
"""
Test script to verify template integrity.
"""

import yaml
from pathlib import Path


def test_required_directories():
    """Test that all required directories exist."""
    required_dirs = ["configs", "scripts", "tests", "tools", "outputs", "notebooks"]

    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        assert dir_path.exists(), f"Missing directory: {dir_name}"

    print("✅ All required directories exist")


def test_required_scripts():
    """Test that all required scripts exist."""
    required_scripts = [
        "scripts/add_tool.py",
        "scripts/remove_tool.py",
        "scripts/run_experiment",
        "scripts/validate_setup.py",
        "scripts/cleanup_wandb.py",
    ]

    for script_path in required_scripts:
        path = Path(script_path)
        assert path.exists(), f"Missing script: {script_path}"

    print("✅ All required scripts exist")


def test_config_files():
    """Test that config files are valid."""
    # Test meta.yaml
    meta_path = Path("configs/meta.yaml")
    assert meta_path.exists(), "meta.yaml not found"

    with open(meta_path, "r") as f:
        meta = yaml.safe_load(f)

    assert "tools" in meta, "Missing 'tools' in meta.yaml"
    assert "experiment" in meta, "Missing 'experiment' in meta.yaml"
    assert "validation" in meta, "Missing 'validation' in meta.yaml"

    print("✅ meta.yaml is valid")

    # Test example experiment config
    example_path = Path("configs/example_experiment.yaml")
    assert example_path.exists(), "example_experiment.yaml not found"

    with open(example_path, "r") as f:
        config = yaml.safe_load(f)

    assert "tool" in config, "Missing 'tool' in example_experiment.yaml"
    assert "experiment" in config, "Missing 'experiment' in example_experiment.yaml"
    assert "description" in config, "Missing 'description' in example_experiment.yaml"
    assert "tags" in config, "Missing 'tags' in example_experiment.yaml"
    assert (
        "estimated_runtime" in config
    ), "Missing 'estimated_runtime' in example_experiment.yaml"

    print("✅ example_experiment.yaml is valid")


def main():
    """Run all template integrity tests."""
    print("Running template integrity tests...")

    tests = [
        test_required_directories,
        test_required_scripts,
        test_config_files,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            return 1

    print("🎉 All template integrity tests passed!")
    return 0


if __name__ == "__main__":
    exit(main())
