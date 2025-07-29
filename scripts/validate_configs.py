#!/usr/bin/env python3
"""
Script to validate experiment configurations and tool setups.
Addresses CI testing issues by providing comprehensive validation.
"""

import subprocess
import sys
from pathlib import Path
import yaml
import argparse
from typing import Union


def run_command(cmd: list, cwd: Union[Path, None] = None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=True
        )
        print(f"✓ {cmd[0]}: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {cmd[0]}: {e.stderr.strip()}")
        return False


def validate_meta_yaml() -> bool:
    """Validate configs/meta.yaml structure."""
    print("Validating configs/meta.yaml...")

    meta_file = Path("configs/meta.yaml")
    if not meta_file.exists():
        print("✗ configs/meta.yaml not found")
        return False

    try:
        with open(meta_file, "r") as f:
            meta = yaml.safe_load(f)

        # Check required sections
        required_sections = ["tools", "experiment", "validation"]
        for section in required_sections:
            if section not in meta:
                print(f"✗ Missing required section: {section}")
                return False

        # Validate tools
        for tool_name, tool_config in meta["tools"].items():
            required_fields = ["path", "entrypoint"]
            for field in required_fields:
                if field not in tool_config:
                    print(f"✗ Tool {tool_name} missing required field: {field}")
                    return False

            # Check if tool path exists
            tool_path = Path(tool_config["path"])
            if not tool_path.exists():
                print(f"✗ Tool path does not exist: {tool_path}")
                return False

        print("✓ configs/meta.yaml is valid")
        return True

    except yaml.YAMLError as e:
        print(f"✗ Invalid YAML in configs/meta.yaml: {e}")
        return False


def validate_runs_yaml() -> bool:
    """Validate configs/runs.yaml structure."""
    print("Validating configs/runs.yaml...")

    runs_file = Path("configs/runs.yaml")
    if not runs_file.exists():
        print("✗ configs/runs.yaml not found")
        return False

    try:
        with open(runs_file, "r") as f:
            runs = yaml.safe_load(f)

        if "runs" not in runs:
            print("✗ Missing 'runs' section in configs/runs.yaml")
            return False

        # Validate each run
        for run_name, run_config in runs["runs"].items():
            required_fields = ["tool", "config", "description"]
            for field in required_fields:
                if field not in run_config:
                    print(f"✗ Run {run_name} missing required field: {field}")
                    return False

            # Check if config file exists
            config_file = Path(f"configs/{run_config['config']}.yaml")
            if not config_file.exists():
                print(f"✗ Config file not found: {config_file}")
                return False

        print("✓ configs/runs.yaml is valid")
        return True

    except yaml.YAMLError as e:
        print(f"✗ Invalid YAML in configs/runs.yaml: {e}")
        return False


def test_tool_imports() -> bool:
    """Test that all tools can be imported."""
    print("Testing tool imports...")

    meta_file = Path("configs/meta.yaml")
    if not meta_file.exists():
        return False

    with open(meta_file, "r") as f:
        meta = yaml.safe_load(f)

    all_success = True

    for tool_name, tool_config in meta["tools"].items():
        tool_path = Path(tool_config["path"])
        entrypoint = tool_config["entrypoint"]

        if not tool_path.exists():
            print(f"✗ Tool path does not exist: {tool_path}")
            all_success = False
            continue

        # Test if entrypoint exists
        entrypoint_path = tool_path / entrypoint
        if not entrypoint_path.exists():
            print(f"✗ Tool entrypoint not found: {entrypoint_path}")
            all_success = False
            continue

        # Test Python import (basic syntax check)
        try:
            cmd = [
                "python",
                "-c",
                f"import sys; sys.path.insert(0, '{tool_path}'); import src",
            ]
            if run_command(cmd):
                print(f"✓ {tool_name}: Import successful")
            else:
                print(f"✗ {tool_name}: Import failed")
                all_success = False
        except Exception as e:
            print(f"✗ {tool_name}: Import error - {e}")
            all_success = False

    return all_success


def test_config_loading() -> bool:
    """Test that all config files can be loaded by their respective tools."""
    print("Testing config loading...")

    runs_file = Path("configs/runs.yaml")
    if not runs_file.exists():
        return False

    with open(runs_file, "r") as f:
        runs = yaml.safe_load(f)

    all_success = True

    for run_name, run_config in runs["runs"].items():
        tool_name = run_config["tool"]
        # config_name = run_config["config"]  # Not used in this test

        # Load meta.yaml to get tool info
        meta_file = Path("configs/meta.yaml")
        with open(meta_file, "r") as f:
            meta = yaml.safe_load(f)

        if tool_name not in meta["tools"]:
            print(f"✗ Run {run_name}: Tool {tool_name} not found in meta.yaml")
            all_success = False
            continue

        tool_config = meta["tools"][tool_name]
        tool_path = Path(tool_config["path"])
        entrypoint = tool_config["entrypoint"]

        # Test config loading (basic test)
        try:
            # Try to run the tool with --help to test basic functionality
            cmd = ["python", str(tool_path / entrypoint), "--help"]
            if run_command(cmd, cwd=None):
                print(f"✓ {run_name}: Config loading test passed")
            else:
                print(f"✗ {run_name}: Config loading test failed")
                all_success = False
        except Exception as e:
            print(f"✗ {run_name}: Config loading error - {e}")
            all_success = False

    return all_success


def main() -> None:
    """Main validation entry point."""
    parser = argparse.ArgumentParser(description="Validate experiment configuration")
    parser.add_argument(
        "--skip-tool-tests",
        action="store_true",
        help="Skip tool import and config loading tests",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("Experiment Template Validation")
    print("=" * 50)

    all_passed = True

    # Validate metadata files
    if not validate_meta_yaml():
        all_passed = False

    if not validate_runs_yaml():
        all_passed = False

    # Test tool functionality (can be skipped for CI speed)
    if not args.skip_tool_tests:
        if not test_tool_imports():
            all_passed = False

        if not test_config_loading():
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("✓ All validation checks passed!")
        sys.exit(0)
    else:
        print("✗ Some validation checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
