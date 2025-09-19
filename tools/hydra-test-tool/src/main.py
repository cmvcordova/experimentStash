#!/usr/bin/env python3
"""
Minimal Hydra test tool for ExperimentStash integration testing.
"""

import hydra
from omegaconf import DictConfig


@hydra.main(version_base=None, config_path=None, config_name=None)
def main(cfg: DictConfig) -> None:
    """Main function that demonstrates successful config loading."""

    print("=" * 60)
    print("🎉 SUCCESS: Hydra integration working!")
    print("=" * 60)

    # Print the message from config if it exists
    if hasattr(cfg, 'message'):
        print(f"📝 Message from config: {cfg.message}")

    # Print the experiment name if it exists
    if hasattr(cfg, 'experiment_name'):
        print(f"🧪 Experiment: {cfg.experiment_name}")

    # Print any custom parameters
    if hasattr(cfg, 'params'):
        print("⚙️  Parameters:")
        for key, value in cfg.params.items():
            print(f"   {key}: {value}")

    print("=" * 60)
    print("✅ Test tool completed successfully!")
    print("✅ Top-level configs integrated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()