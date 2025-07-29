#!/usr/bin/env python3
"""
Minimal hello-world tool for experiment template demonstration.
This tool shows how to load configs from the parent configs directory.
"""

import sys
from pathlib import Path
import yaml
import argparse
from typing import Dict, Any


def load_config(config_name: str) -> Dict[str, Any]:
    """
    Load config from parent configs directory.

    Args:
        config_name: Name of the config file (without .yaml extension)

    Returns:
        Dictionary containing the configuration
    """
    # Get the project root (3 levels up from src/main.py)
    project_root = Path(__file__).parent.parent.parent.parent
    config_file = project_root / "configs" / f"{config_name}.yaml"

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        if not isinstance(config, dict):
            raise ValueError(f"Config file {config_file} must contain a dictionary")
        return config


def main() -> None:
    """Main entry point for the hello-world tool."""
    parser = argparse.ArgumentParser(description="Hello World Tool")
    parser.add_argument(
        "--config-name",
        default="hello_world",
        help="Name of the config file (without .yaml extension)",
    )
    parser.add_argument(
        "--config-path",
        help="Path to configs directory (optional, defaults to parent configs)",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config_name)

        # Print hello world message
        print("=" * 50)
        print("Hello World from the experiment template!")
        print("=" * 50)

        # Display loaded configuration
        print(f"Loaded config: {args.config_name}")
        print(f"Tool: {config.get('tool', 'unknown')}")
        print(f"Experiment: {config.get('experiment', {}).get('name', 'unknown')}")
        print(
            f"Description: {config.get('experiment', {}).get('description', 'No description')}"
        )

        # Simulate some work
        if config.get("experiment", {}).get("simulate_work", False):
            import time

            print("Simulating work...")
            time.sleep(2)
            print("Work completed!")

        print("=" * 50)
        print("Tool execution completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
