# ExperimentStash

*Reproducible ML experiments through config-centric orchestration*

## What It Does

ExperimentStash manages experiments by:
- **Top-level config storage** - All experiment configs live in `configs/<tool>/experiment/`
- **Pinned tool versions** - Tools are git submodules at specific commits
- **Clean orchestration** - Pass configs to tools via CLI, no coupling
- **Full reproducibility** - Config + tool version = exact reproduction

## Quick Start

```bash
# Run an experiment
python scripts/run_experiment <tool> <experiment_name>

# Example
python scripts/run_experiment manylatents single_algorithm
```

## Structure

```
experimentStash/
├── configs/                    # All experiment configs (top-level)
│   └── <tool>/
│       ├── experiment/         # Experiment configs
│       │   └── my_exp.yaml     # Filename = experiment identifier
│       ├── data/              # Supporting configs
│       ├── algorithms/
│       └── ...
├── tools/                      # Tool source code (git submodules)
│   └── <tool>/                # Pinned at specific commit
└── scripts/
    └── run_experiment          # Orchestrator
```

## How It Works

**1. Experiment configs use filenames as identifiers:**
```yaml
# configs/manylatents/experiment/my_pca_test.yaml
#                                  ^^^^^^^^^^^^
#                                  This IS the experiment ID

# @package _global_
name: pca_swissroll_d2  # Human-readable name (for wandb/logs)

defaults:
  - /config
  - override /algorithms/latent: pca
  - override /data: swissroll

algorithms:
  latent:
    n_components: 2
```

**2. Tools are executed from their directory with top-level configs:**
```bash
# ExperimentStash does:
cd tools/manylatents
python -m manylatents.main \
  --config-dir=/path/to/experimentStash/configs/manylatents \
  --config-name=experiment/my_pca_test
```

**3. Reproducibility tracking:**
- **Experiment ID**: Filename (`my_pca_test`)
- **Config**: `configs/manylatents/experiment/my_pca_test.yaml`
- **Tool version**: `tools/manylatents` @ commit `abc123`
- **Result**: Exact reproduction months/years later

## Adding Tools

1. Add tool as submodule:
```bash
git submodule add <repo_url> tools/<tool_name>
cd tools/<tool_name> && uv sync
```

2. Register in `configs/meta.yaml`:
```yaml
tools:
  <tool_name>:
    path: tools/<tool_name>
    entrypoint: "-m <tool_name>.main"
    description: "Tool description"
```

3. Copy tool's config structure:
```bash
cp -r tools/<tool_name>/<tool_name>/configs/* configs/<tool_name>/
```

4. Add experiment configs to `configs/<tool_name>/experiment/`

## Key Principles

- **Filename = Experiment Identity** - No `experiment:` field needed, filesystem provides semantic link
- **Config Inheritance** - Experiments inherit from base: `defaults: [/config, ...]`
- **Tool Flexibility** - Tools keep default configs, CLI overrides for orchestration
- **Clean Separation** - ExperimentStash manages configs, tools execute logic

## Requirements

- Python 3.10+
- `uv` for dependency management
- Git for submodule management
