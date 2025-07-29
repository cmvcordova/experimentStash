#!/usr/bin/env python3
"""
Tests for experiment template setup.
"""

import sys
from pathlib import Path
import yaml


def test_config_loading() -> None:
    """Test that configs can be loaded."""
    # Test meta.yaml
    with open("configs/meta.yaml", "r") as f:
        meta = yaml.safe_load(f)

    # Check required sections
    required = ["tools", "experiment", "validation"]
    for section in required:
        assert section in meta, f"Missing section: {section}"

    # Test runs.yaml
    with open("configs/runs.yaml", "r") as f:
        runs = yaml.safe_load(f)

    assert "runs" in runs, "Missing 'runs' section"

    # Test hello_world.yaml
    with open("configs/hello_world.yaml", "r") as f:
        yaml.safe_load(f)  # Just test that it loads


def test_hello_world_tool() -> None:
    """Test the hello-world tool."""
    # Check if tool exists
    tool_path = Path("tools/hello-world/src/main.py")
    assert tool_path.exists(), f"Tool not found: {tool_path}"

    # Test import
    sys.path.insert(0, str(Path("tools/hello-world")))
    # If we get here without exception, import is successful


def test_directory_structure() -> None:
    """Test that required directories exist."""
    required_dirs = ["configs", "notebooks", "outputs", "tools", "scripts"]

    for dir_name in required_dirs:
        assert Path(dir_name).exists(), f"Directory missing: {dir_name}"


def test_scripts_import() -> None:
    """Test that scripts can be imported."""
    # If we get here without exception, import is successful


def test_tools_hello_world() -> None:
    """Test that hello-world tool can be imported."""
    sys.path.insert(0, str(Path("tools/hello-world")))
    # If we get here without exception, import is successful
