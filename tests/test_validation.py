#!/usr/bin/env python3
"""
Test script to verify experimentStash validation.
"""

import yaml
from pathlib import Path


def test_run_experiment_script_exists() -> None:
    """Test that the run_experiment script exists."""
    script_path = Path("scripts/run_experiment")
    assert script_path.exists(), "run_experiment script not found"


def test_meta_yaml_structure() -> None:
    """Test that meta.yaml has the correct structure."""
    meta_path = Path("configs/meta.yaml")
    assert meta_path.exists(), "meta.yaml not found"

    with open(meta_path, "r") as f:
        meta_config = yaml.safe_load(f)

    # Check required top-level keys
    assert "tools" in meta_config, "Missing 'tools' in meta.yaml"
    assert "experiment" in meta_config, "Missing 'experiment' in meta.yaml"
    assert "validation" in meta_config, "Missing 'validation' in meta.yaml"

    # Check experiment section
    experiment = meta_config["experiment"]
    assert "name" in experiment, "Missing 'name' in experiment section"
    assert "description" in experiment, "Missing 'description' in experiment section"
    assert "authors" in experiment, "Missing 'authors' in experiment section"

    # Check validation section
    validation = meta_config["validation"]
    assert "require_commit_pins" in validation, "Missing 'require_commit_pins' in validation"
    assert "validate_configs" in validation, "Missing 'validate_configs' in validation"
    assert "check_dependencies" in validation, "Missing 'check_dependencies' in validation"


def test_example_experiment_config() -> None:
    """Test that the example experiment config is valid."""
    config_path = Path("configs/example_experiment.yaml")
    assert config_path.exists(), "example_experiment.yaml not found"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Check required fields
    assert "tool" in config, "Missing 'tool' in example_experiment.yaml"
    assert "experiment" in config, "Missing 'experiment' in example_experiment.yaml"
    assert "description" in config, "Missing 'description' in example_experiment.yaml"
    assert "tags" in config, "Missing 'tags' in example_experiment.yaml"
    assert "estimated_runtime" in config, "Missing 'estimated_runtime' in example_experiment.yaml"

    # Check that tool is example_tool
    assert config["tool"] == "example_tool", "Tool should be 'example_tool' in example_experiment.yaml"


def test_directory_structure() -> None:
    """Test that all required directories exist."""
    required_dirs = ["configs", "scripts", "tests", "tools", "outputs", "notebooks"]

    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        assert dir_path.exists(), f"Required directory '{dir_name}' not found"


def test_script_files_exist() -> None:
    """Test that all required script files exist."""
    required_scripts = [
        "scripts/add_tool.py",
        "scripts/remove_tool.py",
        "scripts/run_experiment",
        "scripts/validate_setup.py",
        "scripts/cleanup_wandb.py",
    ]

    for script_path in required_scripts:
        path = Path(script_path)
        assert path.exists(), f"Required script '{script_path}' not found"


def test_config_loading() -> None:
    """Test that configs can be loaded properly."""
    # Load meta config
    with open("configs/meta.yaml", "r") as f:
        meta_config = yaml.safe_load(f)

    # Load example experiment config
    with open("configs/example_experiment.yaml", "r") as f:
        example_config = yaml.safe_load(f)

    # Test that both configs are valid YAML
    assert isinstance(meta_config, dict), "meta.yaml should be a dictionary"
    assert isinstance(example_config, dict), "example_experiment.yaml should be a dictionary"

    # Test that example config references a tool
    tool_name = example_config.get("tool")
    assert tool_name is not None, "Example config should specify a tool"
    assert isinstance(tool_name, str), "Tool name should be a string"


if __name__ == "__main__":
    print("Running validation tests...")

    tests = [
        test_run_experiment_script_exists,
        test_meta_yaml_structure,
        test_example_experiment_config,
        test_directory_structure,
        test_script_files_exist,
        test_config_loading,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All validation tests passed!")
        exit(0)
    else:
        print("❌ Some validation tests failed")
        exit(1)
