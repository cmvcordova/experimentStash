#!/usr/bin/env python3
"""
Validate experimentStash setup and configurations.
"""

import sys
from pathlib import Path
import yaml
import argparse


def validate_directory_structure():
    """Validate that required directories exist."""
    print("Validating directory structure...")

    required_dirs = ["configs", "notebooks", "outputs", "tools", "scripts"]

    all_exist = True
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ Directory exists: {dir_name}")
        else:
            print(f"✗ Directory missing: {dir_name}")
            all_exist = False

    return all_exist


def validate_meta_yaml():
    """Validate configs/meta.yaml structure."""
    print("\nValidating configs/meta.yaml...")

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
            if section in meta:
                print(f"✓ Found section: {section}")
            else:
                print(f"✗ Missing section: {section}")
                return False

        # Validate tools
        tools = meta.get("tools", {})
        if not tools:
            print("⚠ Warning: No tools defined in meta.yaml")
        else:
            print(f"✓ Found {len(tools)} tools")
            for tool_name, tool_config in tools.items():
                print(f"  - {tool_name}: {tool_config.get('path', 'N/A')}")

        print("✓ configs/meta.yaml is valid")
        return True

    except yaml.YAMLError as e:
        print(f"✗ Invalid YAML in configs/meta.yaml: {e}")
        return False


def validate_tool_configs():
    """Validate that all tool configs exist and are valid."""
    print("\nValidating tool configurations...")

    meta_file = Path("configs/meta.yaml")
    if not meta_file.exists():
        return False

    with open(meta_file, "r") as f:
        meta = yaml.safe_load(f)

    all_valid = True

    for tool_name, tool_config in meta.get("tools", {}).items():
        tool_path = Path(tool_config.get("path", ""))

        if not tool_path.exists():
            print(f"✗ Tool path does not exist: {tool_path}")
            all_valid = False
            continue

        # Check if tool has uv.lock (indicating uv is set up)
        uv_lock = tool_path / "uv.lock"
        if not uv_lock.exists():
            print(f"⚠ Warning: No uv.lock found for {tool_name}")
            print(f"  Run: cd {tool_path} && uv sync")

        # Check if entrypoint exists
        entrypoint = tool_config.get("entrypoint", "")
        if entrypoint.startswith("-m "):
            # Module entrypoint
            module_name = entrypoint[3:]  # Remove "-m "
            module_file = tool_path / f"{module_name.replace('.', '/')}.py"
            if not module_file.exists():
                print(f"⚠ Warning: Module entrypoint not found: {module_file}")
        else:
            # File entrypoint
            entrypoint_file = tool_path / entrypoint
            if not entrypoint_file.exists():
                print(f"⚠ Warning: Entrypoint file not found: {entrypoint_file}")

        print(f"✓ {tool_name}: Tool validation completed")

    return all_valid


def find_config_files():
    """Find all config files in the configs directory."""
    print("\nScanning for config files...")

    config_files = []
    configs_dir = Path("configs")

    for config_file in configs_dir.rglob("*.yaml"):
        if config_file.name != "meta.yaml":
            config_files.append(config_file)

    if not config_files:
        print("⚠ Warning: No config files found in configs/")
    else:
        print(f"✓ Found {len(config_files)} config files:")
        for config_file in sorted(config_files):
            # Get relative path from configs/
            rel_path = config_file.relative_to(configs_dir)
            print(f"  - {rel_path}")

    return config_files


def validate_config_files(config_files):
    """Validate that all config files are valid YAML and have required fields."""
    print("\nValidating config files...")

    all_valid = True

    for config_file in config_files:
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            # Check required fields
            required_fields = ["tool", "experiment"]
            missing_fields = []
            for field in required_fields:
                if field not in config:
                    missing_fields.append(field)

            if missing_fields:
                print(
                    f"✗ {config_file.name}: Missing required fields: {missing_fields}"
                )
                all_valid = False
            else:
                print(f"✓ {config_file.name}: Valid")

        except yaml.YAMLError as e:
            print(f"✗ {config_file.name}: Invalid YAML - {e}")
            all_valid = False

    return all_valid


def test_tool_imports():
    """Test that all tools can be imported."""
    print("\nTesting tool imports...")

    meta_file = Path("configs/meta.yaml")
    if not meta_file.exists():
        return False

    with open(meta_file, "r") as f:
        meta = yaml.safe_load(f)

    all_success = True

    for tool_name, tool_config in meta.get("tools", {}).items():
        tool_path = Path(tool_config.get("path", ""))

        if not tool_path.exists():
            print(f"✗ Tool path does not exist: {tool_path}")
            all_success = False
            continue

        # Test if tool can be imported (basic test)
        try:
            # Add tool path to Python path and try to import
            import sys

            sys.path.insert(0, str(tool_path))

            # Try to import the tool's main module
            if tool_config.get("entrypoint", "").startswith("-m "):
                module_name = tool_config["entrypoint"][3:]  # Remove "-m "
                __import__(module_name)
                print(f"✓ {tool_name}: Module import successful")
            else:
                # For file-based entrypoints, just check if the file exists
                entrypoint_file = tool_path / tool_config.get("entrypoint", "")
                if entrypoint_file.exists():
                    print(f"✓ {tool_name}: Entrypoint file exists")
                else:
                    print(f"✗ {tool_name}: Entrypoint file not found")
                    all_success = False

        except Exception as e:
            print(f"✗ {tool_name}: Import failed - {e}")
            all_success = False

    return all_success


def main():
    """Main validation entry point."""
    parser = argparse.ArgumentParser(description="Validate experimentStash setup")
    parser.add_argument(
        "--skip-tool-tests", action="store_true", help="Skip tool import tests"
    )
    parser.add_argument(
        "--list-configs", action="store_true", help="List all available config files"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("experimentStash Setup Validation")
    print("=" * 60)

    all_passed = True

    # Validate basic structure
    if not validate_directory_structure():
        all_passed = False

    # Validate metadata
    if not validate_meta_yaml():
        all_passed = False

    # Validate tool configs
    if not validate_tool_configs():
        all_passed = False

    # Find and validate config files
    config_files = find_config_files()
    if config_files and not validate_config_files(config_files):
        all_passed = False

    # Test tool functionality (can be skipped for speed)
    if not args.skip_tool_tests:
        if not test_tool_imports():
            all_passed = False

    # List configs if requested
    if args.list_configs:
        print("\n" + "=" * 60)
        print("Available Configurations:")
        print("=" * 60)
        for config_file in sorted(config_files):
            rel_path = config_file.relative_to(Path("configs"))
            config_name = str(rel_path).replace(".yaml", "")
            try:
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f)
                tool = config.get("tool", "unknown")
                experiment = config.get("experiment", "unknown")
                description = config.get("description", "No description")
                print(f"  {config_name}")
                print(f"    Tool: {tool}")
                print(f"    Experiment: {experiment}")
                print(f"    Description: {description}")
                print()
            except Exception as e:
                print(f"  {config_name} (error reading config: {e})")

    print("=" * 60)
    if all_passed:
        print("✓ All validation checks passed!")
        print("\nYour experimentStash is ready to use!")
        print("\nNext steps:")
        print("1. Add tools: python scripts/setup_tool.py <tool> <repo_url>")
        print("2. Run experiments: python scripts/run_experiment <tool> <config_path>")
        print("3. List configs: python scripts/validate_setup.py --list-configs")
    else:
        print("✗ Some validation checks failed!")
        print("\nPlease fix the issues above before proceeding.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
