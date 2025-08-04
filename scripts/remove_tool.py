#!/usr/bin/env python3
"""
experimentStash Teardown Utility

Clean removal of tools from experimentStash.
This utility helps manage tool lifecycle and switch between different implementations.

Usage:
    python scripts/teardown.py <tool_name>
    python scripts/teardown.py manylatents --dry-run
"""

import subprocess
import sys
import argparse
import yaml
import time
from pathlib import Path
from typing import Optional, List


class TeardownError(Exception):
    """Custom exception for teardown-related errors."""

    pass


def run_command(
    cmd: list,
    cwd: Optional[Path] = None,
    capture_output: bool = False,
    check: bool = True,
    timeout: int = 300,
) -> tuple[bool, str]:
    """
    Run a command and return success status and output.

    Args:
        cmd: Command to run
        cwd: Working directory
        capture_output: Whether to capture output
        check: Whether to raise exception on non-zero exit code
        timeout: Timeout in seconds

    Returns:
        (success, output)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check,
            timeout=timeout,
        )
        output = result.stdout.strip() if capture_output else ""
        return True, output
    except subprocess.CalledProcessError as e:
        output = e.stderr.strip() if capture_output else str(e)
        return False, output
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, str(e)


def validate_tool_exists(tool_name: str) -> Path:
    """Validate that the tool exists and return its path."""
    tool_path = Path(f"tools/{tool_name}")

    if not tool_path.exists():
        raise TeardownError(f"Tool '{tool_name}' not found at {tool_path}")

    # Check if it's actually a submodule
    git_file = tool_path / ".git"
    if not git_file.exists():
        raise TeardownError(f"'{tool_name}' is not a git submodule")

    return tool_path


def check_tool_usage(tool_name: str) -> List[str]:
    """Check if the tool is referenced in any config files."""
    print(f"🔍 Checking usage of {tool_name}...")

    config_files = []
    configs_dir = Path("configs")

    # Find all config files that reference this tool
    for config_file in configs_dir.rglob("*.yaml"):
        if config_file.name == "meta.yaml":
            continue

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            if config.get("tool") == tool_name:
                config_files.append(str(config_file.relative_to(configs_dir)))
        except Exception:
            continue

    if config_files:
        print(
            f"⚠ Warning: {tool_name} is referenced in {len(config_files)} config file(s):"
        )
        for config_file in config_files:
            print(f"  - {config_file}")
    else:
        print(f"✓ {tool_name} is not referenced in any config files")

    return config_files


def remove_from_meta_yaml(tool_name: str, dry_run: bool = False) -> None:
    """Remove tool from configs/meta.yaml."""
    print(f"\n📝 Removing {tool_name} from metadata...")

    meta_file = Path("configs/meta.yaml")
    if not meta_file.exists():
        raise TeardownError("configs/meta.yaml not found")

    with open(meta_file, "r") as f:
        meta = yaml.safe_load(f)

    if "tools" not in meta or tool_name not in meta["tools"]:
        print(f"⚠ Warning: {tool_name} not found in meta.yaml")
        return

    if dry_run:
        print(f"  [DRY RUN] Would remove {tool_name} from meta.yaml")
        return

    # Remove the tool
    del meta["tools"][tool_name]

    with open(meta_file, "w") as f:
        yaml.dump(meta, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Removed {tool_name} from meta.yaml")


def remove_from_gitignore(tool_name: str, dry_run: bool = False) -> None:
    """Remove the tool directory from .gitignore."""
    print(f"\n📝 Removing {tool_name} from .gitignore...")

    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("✓ .gitignore file not found, nothing to remove")
        return

    # Read current .gitignore content
    with open(gitignore_path, "r") as f:
        content = f.read()

    # Check if the tool is in .gitignore
    tool_pattern = f"tools/{tool_name}/"
    if tool_pattern not in content:
        print(f"✓ {tool_name} not found in .gitignore")
        return

    if dry_run:
        print(f"  [DRY RUN] Would remove {tool_pattern} from .gitignore")
        return

    # Remove the tool pattern from .gitignore
    lines = content.split("\n")
    filtered_lines = [line for line in lines if line.strip() != tool_pattern]

    # Reconstruct content
    new_content = "\n".join(filtered_lines)

    with open(gitignore_path, "w") as f:
        f.write(new_content)

    print(f"✓ Removed tools/{tool_name}/ from .gitignore")


def remove_submodule(tool_name: str, tool_path: Path, dry_run: bool = False) -> None:
    """Remove the git submodule."""
    print(f"\n📦 Removing {tool_name} submodule...")

    if dry_run:
        print(f"  [DRY RUN] Would remove submodule: {tool_path}")
        return

    # Deinit the submodule
    success, output = run_command(
        ["git", "submodule", "deinit", "-f", str(tool_path)], capture_output=True
    )
    if not success:
        print(f"⚠ Warning: Failed to deinit submodule: {output}")

    # Remove from .gitmodules
    success, output = run_command(
        ["git", "rm", "-f", str(tool_path)], capture_output=True
    )
    if not success:
        print(f"⚠ Warning: Failed to remove from git: {output}")

    # Remove the directory
    if tool_path.exists():
        import shutil

        shutil.rmtree(tool_path)
        print(f"✓ Removed directory: {tool_path}")

    print(f"✓ Submodule {tool_name} removed")


def clean_example_configs(tool_name: str, dry_run: bool = False) -> None:
    """Remove example config files for the tool."""
    print(f"\n📄 Cleaning example configs for {tool_name}...")

    configs_dir = Path("configs")
    example_files = [
        configs_dir / f"example_{tool_name}.yaml",
        configs_dir / f"example_{tool_name}.yml",
    ]

    removed_files = []
    for example_file in example_files:
        if example_file.exists():
            if dry_run:
                print(f"  [DRY RUN] Would remove: {example_file}")
            else:
                example_file.unlink()
                print(f"✓ Removed: {example_file}")
            removed_files.append(example_file)

    if not removed_files:
        print(f"✓ No example configs found for {tool_name}")


def check_for_dependencies(tool_name: str) -> List[str]:
    """Check if other tools depend on this tool."""
    print(f"\n🔍 Checking for dependencies on {tool_name}...")

    meta_file = Path("configs/meta.yaml")
    if not meta_file.exists():
        return []

    with open(meta_file, "r") as f:
        meta = yaml.safe_load(f)

    dependent_tools = []
    for other_tool_name, tool_config in meta.get("tools", {}).items():
        if other_tool_name == tool_name:
            continue

        # Check if this tool has any dependencies listed
        dependencies = tool_config.get("dependencies", [])
        if tool_name in dependencies:
            dependent_tools.append(other_tool_name)

    if dependent_tools:
        print(f"⚠ Warning: {tool_name} is listed as a dependency for:")
        for dep_tool in dependent_tools:
            print(f"  - {dep_tool}")
    else:
        print(f"✓ No tools depend on {tool_name}")

    return dependent_tools


def backup_tool_data(tool_name: str, tool_path: Path, dry_run: bool = False) -> None:
    """Create a backup of the tool data before removal."""
    print(f"\n💾 Creating backup of {tool_name}...")

    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_name = f"{tool_name}_{timestamp}"
    backup_path = backup_dir / backup_name

    if dry_run:
        print(f"  [DRY RUN] Would create backup: {backup_path}")
        return

    import shutil

    shutil.copytree(tool_path, backup_path)
    print(f"✓ Backup created: {backup_path}")


def interactive_confirmation(
    tool_name: str, config_files: List[str], dependent_tools: List[str]
) -> bool:
    """Ask for user confirmation before proceeding."""
    print("\n⚠️  CONFIRMATION REQUIRED")
    print("=" * 50)
    print(f"Tool to remove: {tool_name}")

    if config_files:
        print(f"⚠ This tool is referenced in {len(config_files)} config file(s)")
        print("  These configs will become invalid!")

    if dependent_tools:
        print(f"⚠ This tool is a dependency for {len(dependent_tools)} other tool(s)")
        print("  Removing it may break those tools!")

    print("\nThis action will:")
    print("  - Remove the git submodule")
    print("  - Delete the tool directory")
    print("  - Remove from meta.yaml")
    print("  - Clean up example configs")
    print("  - Create a backup")

    response = (
        input(f"\nAre you sure you want to remove '{tool_name}'? (yes/no): ")
        .lower()
        .strip()
    )
    return response in ["yes", "y"]


def main():
    """Main teardown entry point."""
    parser = argparse.ArgumentParser(
        description="experimentStash Teardown Utility - Remove tools cleanly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/teardown.py manylatents
  python scripts/teardown.py old-tool --dry-run
  python scripts/teardown.py deprecated-tool --force --no-backup

This utility helps manage tool lifecycle and switch between different implementations.
        """,
    )
    parser.add_argument("tool_name", help="Name of the tool to remove")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompts"
    )
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument(
        "--keep-configs",
        action="store_true",
        help="Keep config files that reference this tool",
    )

    args = parser.parse_args()

    start_time = time.time()

    try:
        print("=" * 60)
        print("🗑️  experimentStash Teardown Utility")
        print("=" * 60)
        print(f"Tool: {args.tool_name}")
        print(f"Dry run: {args.dry_run}")
        print(f"Force: {args.force}")
        print("=" * 60)

        # Validate tool exists
        tool_path = validate_tool_exists(args.tool_name)

        # Check usage
        config_files = check_tool_usage(args.tool_name)

        # Check dependencies
        dependent_tools = check_for_dependencies(args.tool_name)

        # Interactive confirmation (unless --force)
        if not args.force and not args.dry_run:
            if not interactive_confirmation(
                args.tool_name, config_files, dependent_tools
            ):
                print("❌ Teardown cancelled by user")
                return 0

        # Create backup (unless --no-backup)
        if not args.no_backup:
            backup_tool_data(args.tool_name, tool_path, args.dry_run)

        # Remove from meta.yaml
        remove_from_meta_yaml(args.tool_name, args.dry_run)

        # Remove from .gitignore
        remove_from_gitignore(args.tool_name, args.dry_run)

        # Remove submodule
        remove_submodule(args.tool_name, tool_path, args.dry_run)

        # Clean example configs
        clean_example_configs(args.tool_name, args.dry_run)

        # Warn about config files
        if config_files and not args.keep_configs:
            print(
                f"\n⚠ Warning: {len(config_files)} config file(s) still reference {args.tool_name}"
            )
            print("  You may want to update or remove these configs:")
            for config_file in config_files:
                print(f"    - {config_file}")

        # Print summary
        print("\n" + "=" * 60)
        if args.dry_run:
            print("🔍 DRY RUN COMPLETE")
            print(
                "No changes were made. Use without --dry-run to actually remove the tool."
            )
        else:
            print("✅ TEARDOWN COMPLETE")
            print(f"Tool '{args.tool_name}' has been removed from experimentStash.")

        print("\n📋 Next Steps:")
        print("1. Update any remaining config files that referenced the removed tool")
        print(
            "2. Consider adding a replacement tool: python scripts/plugin.py <new_tool> <repo_url>"
        )
        print("3. Validate your setup: python scripts/validate_setup.py")

        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed_time:.1f} seconds")

    except TeardownError as e:
        print(f"\n❌ Teardown Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Teardown cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
