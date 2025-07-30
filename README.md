# Experiment Orchestration Framework

A clean, modular framework for orchestrating experiments across multiple tools and repositories.

## Overview

This framework provides a simple way to:
1. **Import necessary tools as submodules**
2. **Specify experiment configs at a top level** 
3. **Call each tool and experiment config file in their lower level repo**

## Quick Start

### 1. Import Tools as Submodules

Add your tools as Git submodules in the `tools/` directory:

```bash
# Add a tool as a submodule
git submodule add <tool-repo-url> tools/<tool-name>

# Initialize and update submodules
git submodule update --init --recursive
```

Example:
```bash
git submodule add https://github.com/your-org/manylatents.git tools/manylatents
```

### 2. Configure Tools in `configs/meta.yaml`

Register your tools in the meta configuration:

```yaml
tools:
  manylatents:
    path: tools/manylatents
    entrypoint: "-m src.main"
    config_path_support: true
    commit: HEAD
    python_version: '3.9'
    dependencies: []
    description: ManyLatents dimensionality reduction framework
```

### 3. Specify Experiment Configs at Top Level

Create experiment organizers in `configs/` that point to experiments within each tool:

```yaml
# configs/figure1_method_comparison/pca_swissroll.yaml
tool: manylatents
experiment: swissroll_pca
description: "PCA on Swiss roll data"
tags: ["pca", "swissroll", "method_comparison"]
estimated_runtime: "30m"
```

### 4. Register Experiments in `configs/runs.yaml`

Map experiment names to their config files:

```yaml
runs:
  pca_swissroll:
    tool: manylatents
    config: figure1_method_comparison/pca_swissroll
    description: "PCA on Swiss roll data"
    tags: ["pca", "swissroll", "method_comparison"]
    estimated_runtime: "30m"
```

### 5. Run Experiments

Execute experiments using the simple command:

```bash
python scripts/run_experiment <tool> <config>
```

Examples:
```bash
# Run PCA on Swiss roll data
python scripts/run_experiment manylatents pca_swissroll

# Run UMAP on Swiss roll data  
python scripts/run_experiment manylatents umap_swissroll

# Run t-SNE on Swiss roll data
python scripts/run_experiment manylatents tsne_swissroll
```

## How It Works

### Top-Level Configs (Experiment Organizers)

Top-level configs in `configs/` serve as **experiment organizers** that specify:
- Which tool to use
- Which experiment within that tool to run
- Metadata (description, tags, runtime estimates)

Example:
```yaml
# configs/figure1_method_comparison/pca_swissroll.yaml
tool: manylatents
experiment: swissroll_pca  # Points to experiment in manylatents tool
description: "PCA on Swiss roll data"
tags: ["pca", "swissroll", "method_comparison"]
estimated_runtime: "30m"
```

### Tool-Level Configs (Actual Experiments)

The actual experiment configurations live within each tool's repository structure:

```
tools/manylatents/src/configs/experiment/swissroll_pca.yaml
```

This contains the full experiment configuration that the tool understands.

### Execution Flow

1. **User runs**: `python scripts/run_experiment manylatents pca_swissroll`
2. **Script finds**: Run in `runs.yaml` → `figure1_method_comparison/pca_swissroll`
3. **Script loads**: Top-level config → extracts `experiment: swissroll_pca`
4. **Script executes**: `python -m src.main experiment=swissroll_pca` in the tool's environment

## Directory Structure

```
├── configs/                    # Top-level experiment organizers
│   ├── meta.yaml              # Tool definitions
│   ├── runs.yaml              # Experiment mappings
│   └── figure1_method_comparison/
│       ├── pca_swissroll.yaml
│       ├── umap_swissroll.yaml
│       └── tsne_swissroll.yaml
├── tools/                      # Tool submodules
│   └── manylatents/
│       └── src/configs/experiment/
│           ├── swissroll_pca.yaml
│           ├── swissroll_umap.yaml
│           └── swissroll_tsne.yaml
└── scripts/
    └── run_experiment         # Main experiment runner
```

## Adding New Tools

1. **Add as submodule**:
   ```bash
   git submodule add <tool-repo> tools/<tool-name>
   ```

2. **Register in meta.yaml**:
   ```yaml
   tools:
     <tool-name>:
       path: tools/<tool-name>
       entrypoint: "<entrypoint>"
       config_path_support: true
   ```

3. **Create experiment organizers** in `configs/`

4. **Register experiments** in `runs.yaml`

## Adding New Experiments

1. **Create experiment config** in the tool's repository
2. **Create experiment organizer** in `configs/`
3. **Register in runs.yaml**

## Requirements

- Python 3.8+
- Git (for submodules)
- uv (for tool environment management)

## Setup

```bash
# Clone with submodules
git clone --recursive <repo-url>

# Install dependencies
pip install -r requirements.txt

# Set up tool environments
cd tools/manylatents && uv sync

# Validate your setup
python scripts/validate_setup.py
```

## Example Workflow

```bash
# 1. Import tool
git submodule add https://github.com/your-org/manylatents.git tools/manylatents

# 2. Set up tool environment
cd tools/manylatents && uv sync

# 3. Create experiment organizer
# Edit configs/figure1_method_comparison/my_experiment.yaml

# 4. Register experiment
# Edit configs/runs.yaml

# 5. Run experiment
python scripts/run_experiment manylatents my_experiment
```

This framework provides a clean separation between experiment organization (top-level) and experiment implementation (tool-level), making it easy to manage complex multi-tool experiment workflows.

## Testing

Run the validation script to ensure your setup is working correctly:

```bash
# Validate the entire setup
python scripts/validate_setup.py

# Run unit tests
python -m pytest tests/
```

The validation script checks:
- ✅ Tool configurations in `meta.yaml`
- ✅ Experiment mappings in `runs.yaml`  
- ✅ Top-level config format and structure
- ✅ Tool experiment existence
- ✅ Script syntax and availability

This ensures that after any changes or commits, your experiment orchestration system is still functional.
