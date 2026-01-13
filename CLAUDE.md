# ExperimentStash

**Config-centric experiment reproducibility for any Hydra-based tool.**

---

## What It Does

ExperimentStash captures experiments as **config + pinned code** for exact reproduction:

1. **Add any Hydra tool** as a git submodule
2. **Copy or snapshot configs** to top-level for versioning
3. **Run experiments** via unified orchestrator
4. **Snapshot for papers** with flattened config + commit pin

---

## Quick Start

### 1. Add Your Tool
```bash
python scripts/add_tool mytool https://github.com/org/mytool
```

This:
- Adds submodule to `tools/mytool/`
- Installs deps (`uv sync`)
- Copies configs to `configs/mytool/`
- Registers in `configs/meta.yaml`

### 2. Run Experiment
```bash
python scripts/run_experiment mytool my_experiment
```

### 3. Snapshot for Reproducibility
```bash
python scripts/snapshot_experiment mytool my_experiment --tag paper-v1 --commit
```

Creates:
- Flattened config (no defaults, all values resolved)
- Git tag `snapshot/paper-v1`
- Tool pinned at current commit

### 4. Reproduce Later
```bash
git checkout snapshot/paper-v1
git submodule update --init
python scripts/run_experiment mytool my_experiment
```

---

## Two Modes

| Mode | Script | Purpose |
|------|--------|---------|
| **A: Copy** | `add_tool` | Development - configs editable |
| **B: Snapshot** | `snapshot_experiment` | Production - frozen for papers |

---

## Directory Structure

```
experimentStash/
├── configs/
│   ├── meta.yaml              # Tool registry
│   └── <tool>/
│       ├── experiment/        # Experiment configs
│       ├── data/, metrics/    # Supporting Hydra groups
│       └── snapshots/<tag>/   # Frozen configs (Mode B)
├── tools/
│   └── <tool>/                # Git submodule (pinned commit)
└── scripts/
    ├── run_experiment         # Unified runner
    ├── add_tool               # Mode A: copy configs
    └── snapshot_experiment    # Mode B: frozen snapshot
```

---

## Tool Requirements

For a tool to work with experimentStash, its `main.py` decorator should allow CLI config override:

```python
# Compatible (allows --config-path override)
@hydra.main(config_path=None, config_name=None, version_base=None)

# Not compatible (ignores CLI)
@hydra.main(config_path="../configs", config_name="config", version_base=None)
```

The `add_tool` script warns if decorator needs fixing.

---

## Config Injection Pattern

ExperimentStash injects configs via Hydra CLI:

```bash
python -m tool.main \
  --config-path=/path/to/experimentStash/configs/tool \
  --config-name=experiment/my_experiment \
  override=value
```

`--config-path` prepends to search path, so tool defaults still work as fallback.

---

## Snapshot Format

Snapshots are fully-resolved YAML with metadata header:

```yaml
# SNAPSHOT: mytool/my_experiment
# TAG: paper-v1
# TOOL_COMMIT: abc1234
# TIMESTAMP: 2026-01-12 22:30:00
# DO NOT EDIT - regenerate with: python scripts/snapshot_experiment ...

name: my_experiment
data:
  type: swissroll
  n_samples: 1000
# ... all values resolved, no ${} interpolations
```

---

## Example: Paper Reproduction Setup

```bash
# 1. Fork experimentStash for your paper
git clone https://github.com/you/experimentStash-mypaper

# 2. Add your tool
python scripts/add_tool myanalysis https://github.com/org/myanalysis

# 3. Create experiment config
cat > configs/myanalysis/experiment/figure1.yaml << 'EOF'
# @package _global_
defaults:
  - /data: dataset_a
  - /model: transformer
name: figure1_main_result
# ...
EOF

# 4. Run and iterate
python scripts/run_experiment myanalysis figure1

# 5. Snapshot final version for paper
python scripts/snapshot_experiment myanalysis figure1 --tag camera-ready --commit

# 6. Push - reviewers can reproduce exactly
git push origin main --tags
```

---

## Commands Reference

```bash
# Add tool (Mode A)
python scripts/add_tool <name> <repo_url> [--entrypoint "-m name.main"]

# Run experiment
python scripts/run_experiment <tool> <experiment> [hydra_overrides...]

# Validate without running
python scripts/run_experiment <tool> <experiment> --validate-only

# Snapshot (Mode B)
python scripts/snapshot_experiment <tool> <experiment> --tag <tag> [--commit]
```

---

## Troubleshooting

**"Config not found"**
- Check `configs/<tool>/experiment/<name>.yaml` exists
- Verify experiment name matches filename (no `.yaml` suffix needed)

**"Tool not found"**
- Run `python scripts/add_tool` or manually add to `configs/meta.yaml`

**Config resolution fails**
- Tool decorator may be hardcoded - change to `config_path=None`
- Missing supporting configs (data/, metrics/) - copy from tool

**Hydra composition errors**
- Ensure all `defaults:` references exist in `configs/<tool>/`
- Use absolute paths with leading `/` (e.g., `/data: mydata`)
