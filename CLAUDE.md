# ExperimentStash

**Freeze experiments in time. Config + code commit = exact reproduction.**

---

## Core Idea

```
snapshot = flattened_config + tool_commit_pin + git_tag
```

Months later: `git checkout snapshot/<tag>` → identical results.

---

## Quick Start

```bash
# 1. Add tool
python scripts/add_tool mytool https://github.com/org/mytool

# 2. Run experiment
python scripts/run_experiment mytool my_experiment

# 3. Freeze for reproduction
python scripts/snapshot_experiment mytool my_experiment --tag v1.0 --commit

# 4. Reproduce anytime
git checkout snapshot/v1.0
git submodule update --init
python scripts/run_experiment mytool my_experiment
```

---

## Two Modes

| Mode | Script | When |
|------|--------|------|
| **Copy** | `add_tool` | Development - iterate on configs |
| **Freeze** | `snapshot_experiment` | Production - lock for papers/sharing |

---

## What Freeze Does

```bash
python scripts/snapshot_experiment mytool my_exp --tag camera-ready --commit
```

1. **Flattens config** - resolves all `defaults:`, no interpolations left
2. **Pins tool commit** - submodule locked to exact SHA
3. **Creates git tag** - `snapshot/camera-ready`
4. **Commits everything** - one atomic reproducibility checkpoint

Output:
```yaml
# configs/mytool/snapshots/camera-ready/my_exp.yaml
# SNAPSHOT: mytool/my_exp
# TOOL_COMMIT: abc1234
# TIMESTAMP: 2026-01-12

name: my_exp
data:
  type: swissroll
  n_samples: 1000
model:
  hidden_dim: 256
# ... every value resolved
```

---

## Directory Structure

```
experimentStash/
├── configs/<tool>/
│   ├── experiment/           # Working configs (Mode A)
│   └── snapshots/<tag>/      # Frozen configs (Mode B)
├── tools/<tool>/             # Submodule (pinned on freeze)
└── scripts/
    ├── add_tool              # Add + copy configs
    ├── run_experiment        # Execute
    └── snapshot_experiment   # Freeze
```

---

## Tool Compatibility

Tools must accept CLI config path:

```python
# Works
@hydra.main(config_path=None, config_name=None, version_base=None)

# Doesn't work (hardcoded)
@hydra.main(config_path="../configs", config_name="config")
```

---

## Commands

```bash
# Add tool
python scripts/add_tool <name> <repo_url>

# Run
python scripts/run_experiment <tool> <experiment> [overrides...]

# Validate only
python scripts/run_experiment <tool> <experiment> --validate-only

# Freeze
python scripts/snapshot_experiment <tool> <experiment> --tag <tag> --commit
```

---

## Paper Workflow

```bash
# Fork for your paper
git clone https://github.com/you/experimentStash-mypaper

# Add your tool
python scripts/add_tool myanalysis https://github.com/org/myanalysis

# Iterate
python scripts/run_experiment myanalysis figure1

# Freeze final
python scripts/snapshot_experiment myanalysis figure1 --tag camera-ready --commit

# Share
git push origin main --tags
# Reviewers: git checkout snapshot/camera-ready && git submodule update --init
```
