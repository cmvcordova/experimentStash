#!/usr/bin/env python3
"""
Utility script to force cleanup of hanging wandb runs.
Usage: python scripts/cleanup_wandb.py
"""

import wandb
import sys

def cleanup_wandb():
    """Force cleanup of any active wandb runs."""
    try:
        if wandb.run is not None:
            print(f"[INFO] Found active wandb run: {wandb.run.name}")
            wandb.finish()
            print("[INFO] Wandb run terminated successfully")
        else:
            print("[INFO] No active wandb run found")
    except Exception as e:
        print(f"[ERROR] Failed to cleanup wandb: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(cleanup_wandb()) 