#!/usr/bin/env python3
"""
Script to add new tools as submodules to the experiment template.
Addresses submodule pitfalls by providing a guided setup process.
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


def update_meta_yaml(
    tool_name: str, tool_path: str, entrypoint: str = "src/main.py"
) -> bool:
    """Update configs/meta.yaml with new tool information."""
    meta_file = Path("configs/meta.yaml")

    if not meta_file.exists():
        print("✗ configs/meta.yaml not found")
        return False

    with open(meta_file, "r") as f:
        meta = yaml.safe_load(f)

    # Add tool to tools section
    if "tools" not in meta:
        meta["tools"] = {}

    meta["tools"][tool_name] = {
        "path": tool_path,
        "entrypoint": entrypoint,
        "commit": "HEAD",  # Track main branch for development
        "python_version": "3.8",
        "dependencies": [],
        "description": f"Added tool: {tool_name}",
    }

    with open(meta_file, "w") as f:
        yaml.dump(meta, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Updated configs/meta.yaml with {tool_name}")
    return True


def main() -> None:
    """Main entry point for tool setup."""
    parser = argparse.ArgumentParser(description="Setup new tool as submodule")
    parser.add_argument("tool_name", help="Name of the tool (e.g., my-tool)")
    parser.add_argument("repo_url", help="Git repository URL")
    parser.add_argument(
        "--entrypoint",
        default="src/main.py",
        help="Entry point script (default: src/main.py)",
    )
    parser.add_argument(
        "--branch", default="main", help="Branch to track (default: main)"
    )
    parser.add_argument("--pin-commit", help="Pin to specific commit (optional)")

    args = parser.parse_args()

    # Validate inputs
    if not args.tool_name.replace("-", "").replace("_", "").isalnum():
        print("✗ Tool name must be alphanumeric (can contain - or _)")
        sys.exit(1)

    tool_path = f"tools/{args.tool_name}"

    print(f"Setting up tool: {args.tool_name}")
    print(f"Repository: {args.repo_url}")
    print(f"Path: {tool_path}")
    print(f"Entrypoint: {args.entrypoint}")
    print()

    # Check if tool already exists
    if Path(tool_path).exists():
        print(f"✗ Tool {args.tool_name} already exists at {tool_path}")
        sys.exit(1)

    # Add submodule
    print("1. Adding submodule...")
    cmd = ["git", "submodule", "add", "-b", args.branch, args.repo_url, tool_path]

    if not run_command(cmd):
        print("✗ Failed to add submodule")
        sys.exit(1)

    # Pin to specific commit if requested
    if args.pin_commit:
        print(f"2. Pinning to commit {args.pin_commit}...")
        cmd = ["git", "checkout", args.pin_commit]
        if not run_command(cmd, cwd=Path(tool_path)):
            print("✗ Failed to pin commit")
            sys.exit(1)

    # Update meta.yaml
    print("3. Updating metadata...")
    if not update_meta_yaml(args.tool_name, tool_path, args.entrypoint):
        print("✗ Failed to update metadata")
        sys.exit(1)

    # Test the tool
    print("4. Testing tool...")
    main_script = Path(tool_path) / args.entrypoint
    if main_script.exists():
        print(f"✓ Tool entrypoint found: {main_script}")
    else:
        print(f"⚠ Warning: Entrypoint not found: {main_script}")

    print()
    print("✓ Tool setup completed!")
    print()
    print("Next steps:")
    print("1. Edit configs/meta.yaml to add tool-specific details")
    print("2. Create config files in configs/ for your experiments")
    print("3. Add experiments to configs/runs.yaml")
    print(f"4. Test with: python {tool_path}/{args.entrypoint}")


if __name__ == "__main__":
    main()
