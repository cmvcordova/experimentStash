#!/usr/bin/env python3
"""
experimentStash Plugin Utility

Core functionality for adding new tools to experimentStash.
This is the primary way to add new ML tools to your experiment setup.

Usage:
    python scripts/plugin.py <tool_name> <github_url>
    python scripts/plugin.py manylatents https://github.com/cmvcordova/manyLatents.git
"""

import subprocess
import sys
import argparse
import yaml
import time
from pathlib import Path
from typing import Optional


class PluginError(Exception):
    """Custom exception for plugin-related errors."""

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


def validate_inputs(tool_name: str, github_url: str) -> None:
    """Validate input parameters."""
    if not tool_name.replace("-", "").replace("_", "").isalnum():
        raise PluginError("Tool name must be alphanumeric (can contain - or _)")

    if not github_url.startswith(("https://github.com/", "git@github.com:")):
        raise PluginError("GitHub URL must be a valid GitHub repository URL")

    if Path(f"tools/{tool_name}").exists():
        raise PluginError(f"Tool {tool_name} already exists at tools/{tool_name}")


def check_prerequisites() -> None:
    """Check that required tools are available."""
    print("🔍 Checking prerequisites...")

    # Check git
    success, output = run_command(["git", "--version"], capture_output=True)
    if not success:
        raise PluginError(f"Git not found: {output}")
    print(f"✓ Git: {output}")

    # Check uv
    success, output = run_command(["uv", "--version"], capture_output=True)
    if not success:
        raise PluginError(f"uv not found: {output}")
    print(f"✓ uv: {output}")

    # Check if we're in a git repository
    success, _ = run_command(["git", "rev-parse", "--git-dir"])
    if not success:
        raise PluginError(
            "Not in a git repository. Please run this from your experimentStash root."
        )
    print("✓ In git repository")


def clone_and_add_submodule(
    tool_name: str, github_url: str, branch: str = "main"
) -> Path:
    """Clone the repository and add it as a submodule."""
    print(f"\n📦 Adding {tool_name} as submodule...")

    tool_path = Path(f"tools/{tool_name}")

    # Always clean up any leftover git state
    print(f"🧹 Cleaning up any existing {tool_name} git state...")
    import shutil

    # Remove any .git directory that might be left behind
    git_dir = tool_path / ".git"
    if git_dir.exists():
        print(f"🗑️  Removing leftover .git directory in {tool_path}")
        shutil.rmtree(git_dir, ignore_errors=True)

    # Remove the entire directory if it exists
    if tool_path.exists():
        print(f"🗑️  Removing existing {tool_path} directory")
        shutil.rmtree(tool_path, ignore_errors=True)

    # Clean git cache and index for this path
    print(f"🗑️  Cleaning git index for {tool_path}")
    run_command(["git", "rm", "--cached", str(tool_path)], capture_output=True)
    run_command(["git", "reset", "HEAD", str(tool_path)], capture_output=True)
    run_command(["git", "rm", "-r", "--cached", str(tool_path)], capture_output=True)

    print(f"✓ Cleaned up {tool_path}")

    # Try to add submodule normally first
    cmd = ["git", "submodule", "add", "-b", branch, github_url, str(tool_path)]
    success, output = run_command(cmd, capture_output=True)

    # If that fails with the git directory error, try with --force
    if (
        not success
        and "A git directory for" in output
        and "use the '--force' option" in output
    ):
        print("🔄 Retrying with --force option...")
        cmd = [
            "git",
            "submodule",
            "add",
            "--force",
            "-b",
            branch,
            github_url,
            str(tool_path),
        ]
        success, output = run_command(cmd, capture_output=True)

    # If that fails with "already exists in the index", try to remove from index first
    if not success and "already exists in the index" in output:
        print("🔄 Removing from index and retrying...")
        run_command(
            ["git", "rm", "-r", "--cached", str(tool_path)], capture_output=True
        )
        run_command(["git", "reset", "HEAD", str(tool_path)], capture_output=True)
        cmd = ["git", "submodule", "add", "-b", branch, github_url, str(tool_path)]
        success, output = run_command(cmd, capture_output=True)

    if not success:
        raise PluginError(f"Failed to add submodule: {output}")

    print(f"✓ Submodule added: {tool_path}")
    return tool_path


def setup_uv_environment(tool_path: Path) -> None:
    """Set up uv environment for the tool."""
    print(f"\n🔧 Setting up uv environment for {tool_path.name}...")

    # Check if pyproject.toml exists
    pyproject_file = tool_path / "pyproject.toml"
    if not pyproject_file.exists():
        print(f"⚠ Warning: No pyproject.toml found in {tool_path}")
        return

    # Run uv sync
    success, output = run_command(["uv", "sync"], cwd=tool_path, capture_output=True)
    if not success:
        raise PluginError(f"Failed to run uv sync: {output}")

    print(f"✓ uv environment set up for {tool_path.name}")


def update_meta_yaml(
    tool_name: str, tool_path: Path, entrypoint: str = "src/main.py"
) -> None:
    """Update configs/meta.yaml with new tool information."""
    print("\n📝 Updating metadata...")

    meta_file = Path("configs/meta.yaml")
    if not meta_file.exists():
        raise PluginError("configs/meta.yaml not found")

    with open(meta_file, "r") as f:
        meta = yaml.safe_load(f)

    # Add tool to tools section
    if "tools" not in meta:
        meta["tools"] = {}

    # Detect entrypoint
    detected_entrypoint = detect_entrypoint(tool_path)
    if detected_entrypoint:
        entrypoint = detected_entrypoint
        print(f"✓ Detected entrypoint: {entrypoint}")

    meta["tools"][tool_name] = {
        "path": str(tool_path),
        "entrypoint": entrypoint,
        "commit": "HEAD",  # Track main branch for development
        "python_version": "3.9",
        "dependencies": [],
        "description": f"Added via plugin: {tool_name}",
    }

    with open(meta_file, "w") as f:
        yaml.dump(meta, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Updated configs/meta.yaml with {tool_name}")


def add_to_gitignore(tool_name: str) -> None:
    """Add the tool directory to .gitignore."""
    print(f"\n📝 Adding {tool_name} to .gitignore...")

    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("⚠️  .gitignore file not found, creating one...")
        gitignore_content = "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n# Virtual environments\n.venv/\nvenv/\n\n# IDE\n.vscode/\n.idea/\n\n# OS\n.DS_Store\nThumbs.db\n\n# Tools\n"
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)

    # Read current .gitignore content
    with open(gitignore_path, "r") as f:
        content = f.read()

    # Check if the tool is already in .gitignore
    tool_pattern = f"tools/{tool_name}/"
    if tool_pattern in content:
        print(f"✓ {tool_name} already in .gitignore")
        return

    # Add the tool to .gitignore
    if "# Tools" not in content:
        content += "\n# Tools\n"

    content += f"{tool_pattern}\n"

    with open(gitignore_path, "w") as f:
        f.write(content)

    print(f"✓ Added tools/{tool_name}/ to .gitignore")


def detect_entrypoint(tool_path: Path) -> Optional[str]:
    """Detect the appropriate entrypoint for the tool."""
    # Common entrypoint patterns
    entrypoints = [
        "src/main.py",
        "main.py",
        "-m src.main",
        "-m main",
        "src/__main__.py",
        "__main__.py",
    ]

    for entrypoint in entrypoints:
        if entrypoint.startswith("-m "):
            # Module entrypoint
            module_name = entrypoint[3:]
            module_file = tool_path / f"{module_name.replace('.', '/')}.py"
            if module_file.exists():
                return entrypoint
        else:
            # File entrypoint
            entrypoint_file = tool_path / entrypoint
            if entrypoint_file.exists():
                return entrypoint

    return None


def validate_tool_setup(tool_name: str, tool_path: Path) -> None:
    """Validate that the tool is properly set up."""
    print(f"\n🔍 Validating {tool_name} setup...")

    # Check if tool directory exists
    if not tool_path.exists():
        raise PluginError(f"Tool directory not found: {tool_path}")

    # Check if pyproject.toml exists
    pyproject_file = tool_path / "pyproject.toml"
    if not pyproject_file.exists():
        print(f"⚠ Warning: No pyproject.toml found in {tool_path}")

    # Check if uv.lock exists (indicating uv is set up)
    uv_lock_file = tool_path / "uv.lock"
    if not uv_lock_file.exists():
        print(f"⚠ Warning: No uv.lock found in {tool_path}")
        print(f"  You may need to run: cd {tool_path} && uv sync")

    # Check if src directory exists
    src_dir = tool_path / "src"
    if not src_dir.exists():
        print(f"⚠ Warning: No src/ directory found in {tool_path}")

    print(f"✓ {tool_name} validation completed")


def create_example_config(tool_name: str) -> None:
    """Create an example config file for the new tool."""
    print("\n📄 Creating example config...")

    # Create configs directory if it doesn't exist
    configs_dir = Path("configs")
    configs_dir.mkdir(exist_ok=True)

    # Create example config
    example_config = f"""# Example config for {tool_name}
# Copy this file and modify for your experiments

tool: {tool_name}
experiment: example_experiment
description: "Example experiment for {tool_name}"
tags: ["example", "demo"]
estimated_runtime: "5m"

# Add your experiment-specific parameters here
# model:
#   name: "example_model"
#   parameters:
#     learning_rate: 0.001
#     batch_size: 32
"""

    example_file = configs_dir / f"example_{tool_name}.yaml"
    with open(example_file, "w") as f:
        f.write(example_config)

    print(f"✓ Created example config: {example_file}")


def run_post_setup_validation(tool_name: str) -> None:
    """Run validation to ensure everything is working."""
    print("\n🧪 Running post-setup validation...")

    # Run the validation script
    success, output = run_command(
        ["python", "scripts/validate_setup.py", "--skip-tool-tests"],
        capture_output=True,
    )

    if success:
        print("✓ Post-setup validation passed")
    else:
        print(f"⚠ Post-setup validation had issues: {output}")


def print_success_summary(tool_name: str, tool_path: Path) -> None:
    """Print a success summary with next steps."""
    print("\n" + "=" * 60)
    print("🎉 Plugin Installation Complete!")
    print("=" * 60)
    print(f"✓ Tool: {tool_name}")
    print(f"✓ Path: {tool_path}")
    print("✓ Environment: uv-based")
    print("✓ Metadata: Updated in configs/meta.yaml")
    print("✓ Gitignore: Added to .gitignore (use --no-gitignore to disable)")
    print("\n📋 Next Steps:")
    print(f"1. Set up environment: cd {tool_path} && uv sync")
    print("2. Create experiment configs in configs/")
    print(f"3. Test the tool: python scripts/run_experiment {tool_name} <config_path>")
    print("4. List available configs: python scripts/validate_setup.py --list-configs")
    print("\n💡 Tips:")
    print(f"- Check the example config: configs/example_{tool_name}.yaml")
    print("- Validate your setup: python scripts/validate_setup.py")
    print("- Run comprehensive test: python test_workflow.py")


def main():
    """Main plugin entry point."""
    parser = argparse.ArgumentParser(
        description="experimentStash Plugin Utility - Add new tools easily",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/add_tool.py manylatents https://github.com/cmvcordova/manyLatents.git
  python scripts/add_tool.py clustering https://github.com/user/clustering-module.git
  python scripts/add_tool.py my-tool https://github.com/user/my-tool.git --branch develop
  python scripts/add_tool.py my-tool https://github.com/user/my-tool.git --no-gitignore

This is the primary way to add new ML tools to your experimentStash setup.
Tools are automatically added to .gitignore by default to prevent accidental commits.
        """,
    )
    parser.add_argument("tool_name", help="Name of the tool (e.g., manylatents)")
    parser.add_argument("github_url", help="GitHub repository URL")
    parser.add_argument(
        "--branch", default="main", help="Branch to track (default: main)"
    )
    parser.add_argument(
        "--entrypoint", help="Custom entrypoint (auto-detected if not specified)"
    )
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip post-setup validation"
    )
    parser.add_argument(
        "--gitignore",
        action="store_true",
        default=True,
        help="Add tool to .gitignore (default: True)",
    )
    parser.add_argument(
        "--no-gitignore", action="store_true", help="Don't add tool to .gitignore"
    )

    args = parser.parse_args()

    start_time = time.time()

    try:
        print("=" * 60)
        print("🚀 experimentStash Plugin Utility")
        print("=" * 60)
        print(f"Tool: {args.tool_name}")
        print(f"Repository: {args.github_url}")
        print(f"Branch: {args.branch}")
        print("=" * 60)

        # Validate inputs
        validate_inputs(args.tool_name, args.github_url)

        # Check prerequisites
        check_prerequisites()

        # Clone and add submodule
        tool_path = clone_and_add_submodule(
            args.tool_name, args.github_url, args.branch
        )

        # Set up uv environment
        setup_uv_environment(tool_path)

        # Update metadata
        update_meta_yaml(args.tool_name, tool_path, args.entrypoint)

        # Add to .gitignore if requested
        if args.gitignore and not args.no_gitignore:
            add_to_gitignore(args.tool_name)

        # Validate tool setup
        validate_tool_setup(args.tool_name, tool_path)

        # Create example config
        create_example_config(args.tool_name)

        # Run post-setup validation
        if not args.skip_validation:
            run_post_setup_validation(args.tool_name)

        # Print success summary
        print_success_summary(args.tool_name, tool_path)

        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed_time:.1f} seconds")

    except PluginError as e:
        print(f"\n❌ Plugin Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
