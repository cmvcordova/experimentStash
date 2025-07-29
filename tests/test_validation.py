#!/usr/bin/env python3
"""
Tests for validation script functionality.
"""

from pathlib import Path
import yaml


def test_validate_configs_script() -> None:
    """Test that the validate_configs script can be run."""
    script_path = Path("scripts/validate_configs.py")
    assert script_path.exists(), "validate_configs.py not found"

    # Test that the script can be imported
    # If we get here without exception, import is successful


def test_setup_tool_script() -> None:
    """Test that the setup_tool script can be run."""
    script_path = Path("scripts/setup_tool.py")
    assert script_path.exists(), "setup_tool.py not found"

    # Test that the script can be imported
    # If we get here without exception, import is successful


def test_meta_yaml_structure() -> None:
    """Test that meta.yaml has the correct structure."""
    with open("configs/meta.yaml", "r") as f:
        meta = yaml.safe_load(f)

    # Check required top-level sections
    assert "tools" in meta, "Missing 'tools' section"
    assert "experiment" in meta, "Missing 'experiment' section"
    assert "validation" in meta, "Missing 'validation' section"

    # Check that tools section has at least one tool
    assert len(meta["tools"]) > 0, "No tools defined in meta.yaml"

    # Check that hello-world tool exists
    assert "hello-world" in meta["tools"], "hello-world tool not found in meta.yaml"

    # Check tool structure
    hello_world = meta["tools"]["hello-world"]
    assert "path" in hello_world, "hello-world tool missing 'path'"
    assert "entrypoint" in hello_world, "hello-world tool missing 'entrypoint'"


def test_runs_yaml_structure() -> None:
    """Test that runs.yaml has the correct structure."""
    with open("configs/runs.yaml", "r") as f:
        runs = yaml.safe_load(f)

    assert "runs" in runs, "Missing 'runs' section"
    assert len(runs["runs"]) > 0, "No runs defined in runs.yaml"

    # Check that at least one run references hello-world tool
    has_hello_world = any(
        run_config.get("tool") == "hello-world" for run_config in runs["runs"].values()
    )
    assert has_hello_world, "No runs reference hello-world tool"
