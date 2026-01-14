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

---

## Advanced: Avoiding Config Duplication with SearchPathPlugin

By default, `add_tool` copies base configs into `configs/<tool>/`. For large config sets or when you want to keep configs in the installed package, you can use Hydra's SearchPathPlugin pattern instead.

### The Problem

ExperimentStash uses `--config-path` to point Hydra at experiment configs. But your tool's base configs (algorithms, data, metrics) live in its installed package. Without extra setup, Hydra can't find them.

### Solution: Dynamic SearchPathPlugin

1. **Add `search_packages` to meta.yaml**:

```yaml
tools:
  mytool:
    path: tools/mytool
    entrypoint: "-m mytool.main"
    search_packages: "mytool.configs:mytool.extension.configs"  # Colon-separated
```

2. **Register the plugin in your tool's main.py** (before `@hydra.main`):

```python
try:
    from shop.hydra import register_dynamic_search_path
    register_dynamic_search_path()
except ImportError:
    pass  # shop not installed
```

3. **Use `config_path=None`** in your `@hydra.main` decorator:

```python
@hydra.main(config_path=None, config_name=None, version_base=None)
def main(cfg):
    ...
```

### How It Works

1. `run_experiment` sets `HYDRA_SEARCH_PACKAGES` env var from meta.yaml
2. Your tool registers `SearchPathPlugin` on import
3. The plugin reads the env var and adds `pkg://` paths to Hydra's search path
4. Experiment configs can reference package configs without copying

### Result

Your experiment configs can reference package configs:

```yaml
# configs/mytool/experiment/my_exp.yaml
defaults:
  - /algorithm: pca    # Found in pkg://mytool.configs
  - /data: swissroll   # Found in pkg://mytool.configs

name: my_experiment
```

No config duplication needed. Package updates are picked up automatically.

---

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed usage guide.
