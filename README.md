# ExperimentStash

*Config-centric experiment reproducibility for any Hydra-based tool.*

## Quick Start

```bash
# 1. Add your tool
python scripts/add_tool mytool https://github.com/org/mytool

# 2. Run experiment
python scripts/run_experiment mytool my_experiment

# 3. Snapshot for paper reproducibility
python scripts/snapshot_experiment mytool my_experiment --tag v1.0 --commit
```

## Structure

```
experimentStash/
├── configs/
│   ├── meta.yaml              # Tool registry
│   └── <tool>/
│       ├── experiment/        # Experiment configs
│       └── snapshots/<tag>/   # Frozen configs (fully resolved)
├── tools/
│   └── <tool>/                # Git submodule (pinned commit)
└── scripts/
    ├── run_experiment         # Run experiments
    ├── add_tool               # Add new tools (Mode A)
    └── snapshot_experiment    # Freeze for reproduction (Mode B)
```

## Two Modes

| Mode | Script | Use Case |
|------|--------|----------|
| **Copy** | `add_tool` | Development - configs editable |
| **Snapshot** | `snapshot_experiment` | Papers - frozen + commit pinned |

## Adding Tools

```bash
python scripts/add_tool <name> <repo_url> [--entrypoint "-m name.main"]
```

This:
- Adds tool as git submodule
- Installs dependencies (`uv sync`)
- Copies configs to `configs/<tool>/`
- Registers in `configs/meta.yaml`

## Reproducibility

```bash
# Create snapshot
python scripts/snapshot_experiment mytool my_exp --tag camera-ready --commit

# Later: exact reproduction
git checkout snapshot/camera-ready
git submodule update --init
python scripts/run_experiment mytool my_exp
```

## Tool Requirements

Tools must allow CLI config override:

```python
# Compatible
@hydra.main(config_path=None, config_name=None, version_base=None)

# Not compatible (hardcoded path)
@hydra.main(config_path="../configs", config_name="config", version_base=None)
```

## Requirements

- Python 3.10+
- `uv` for dependency management
- Git for submodule management

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed usage guide.
