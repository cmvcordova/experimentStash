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

---

## SearchPathPlugin (Avoid Config Copying)

Instead of copying tool configs, discover them from installed packages.

### Setup

**1. Add `search_packages` to meta.yaml:**

```yaml
tools:
  manylatents:
    path: tools/manylatents
    entrypoint: "-m manylatents.main"
    search_packages: "manylatents.configs"  # Colon-separated for multiple
```

**2. Register plugin in tool's main.py** (before `@hydra.main`):

```python
try:
    from shop.hydra import register_dynamic_search_path
    register_dynamic_search_path()
except ImportError:
    pass
```

**3. Use `config_path=None`** in the tool:

```python
@hydra.main(config_path=None, config_name=None, version_base=None)
def main(cfg):
    ...
```

### How It Works

```
run_experiment manylatents my_exp
         ↓
Sets HYDRA_SEARCH_PACKAGES="manylatents.configs"
         ↓
Tool registers DynamicSearchPathPlugin
         ↓
Hydra search path includes:
  - file://experimentStash/configs/manylatents  (experiments)
  - pkg://manylatents.configs                   (base configs)
```

### Multiple Tools

Each tool gets its own config directory and search packages:

```yaml
tools:
  manylatents:
    search_packages: "manylatents.configs"
  geomancy:
    search_packages: "geomancy.configs:manylatents.configs"  # Can include dependencies
  manyagents:
    search_packages: "manyagents.configs"
```

Directory structure:
```
configs/
├── manylatents/experiment/   # manylatents experiments
├── geomancy/experiment/      # geomancy experiments
└── manyagents/experiment/    # manyagents experiments
```

### Verify

```bash
python scripts/run_experiment manylatents my_exp --info searchpath
# Should show both file:// (experiments) and pkg:// (base configs)
```

---

## Multi-Tool Structure

Each tool gets its own isolated config namespace:

```
experimentStash/
├── configs/
│   ├── meta.yaml                    # Tool registry
│   ├── tool1/
│   │   └── experiment/              # tool1 experiments only
│   ├── tool2/
│   │   └── experiment/              # tool2 experiments only
│   └── tool3/
│       └── experiment/              # tool3 experiments only
└── tools/
    ├── tool1/                       # Submodule
    ├── tool2/                       # Submodule
    └── tool3/                       # Submodule
```

### Tool Registry (meta.yaml)

```yaml
tools:
  tool1:
    path: tools/tool1
    entrypoint: "-m tool1.main"
    search_packages: "tool1.configs"

  tool2:
    path: tools/tool2
    entrypoint: "-m tool2.main"
    search_packages: "tool2.configs:tool1.configs"  # Can include deps

  tool3:
    path: tools/tool3
    entrypoint: "-m tool3.main"
    search_packages: "tool3.configs"
```

### Isolation

| Aspect | Behavior |
|--------|----------|
| `--config-path` | Points to `configs/<tool>/` for that tool |
| `search_packages` | Tool-specific; can include dependencies |
| Experiments | Namespaced by tool directory |
| Collisions | None - each tool has isolated namespace |

### Running

```bash
python scripts/run_experiment tool1 my_exp      # Uses configs/tool1/
python scripts/run_experiment tool2 figure1     # Uses configs/tool2/
python scripts/run_experiment tool3 prompt_test # Uses configs/tool3/
```
