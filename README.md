# ExperimentStash: Multi-Tool Experiment Orchestration Framework

A robust, modular framework for orchestrating experiments across multiple tools and repositories with clean separation of concerns.

## 🎯 Overview

ExperimentStash provides a **tool-agnostic experiment orchestration system** that:
- **Imports tools as Git submodules** for version control and reproducibility
- **Separates experiment organization from implementation**
- **Provides unified experiment execution** across diverse tools
- **Handles complex dependency management** with uv environments
- **Ensures reproducible workflows** with proper git state management

## ⚠️ Known Issues

### Process Termination and Wandb State Management

**Issue**: When processes are killed by the system (due to memory limits, wall time, or other resource constraints), wandb runs may remain in "running" state indefinitely instead of being properly marked as failed.

**Symptoms**:
- Process gets killed with SIGKILL (-9) or SIGTERM (-15)
- Wandb runs remain in "running" state indefinitely
- No proper error messages or traceback
- Dashboard shows hanging runs that never complete

**Root Cause**: 
When a process is killed abruptly, the wandb context manager and signal handlers may not have time to call `wandb.finish()`, leaving the run in an open state.

**Solutions**:
1. **Use offline mode**: Set `WANDB_MODE=offline` for cluster environments
   ```bash
   export WANDB_MODE=offline
   python3 scripts/run_experiment <tool> <config>
   ```
2. **Sync runs after completion**: Use `wandb sync` to close offline runs
   ```bash
   wandb sync --sync-all tools/<tool-name>/wandb/
   ```
3. **Request grace period**: Ask your cluster admin for SLURM grace periods
   ```bash
   #SBATCH --signal=TERM@90  # 90 second grace period
   ```

**Note**: The framework includes signal handling and wandb cleanup mechanisms, but these may not work if the process is killed immediately without a grace period.

## 🚀 Quick Start

### 1. Clone and Initialize

```bash
# Clone the repository
git clone <your-repo-url>
cd experimentstash

# Initialize submodules (if any exist)
git submodule update --init --recursive
```

### 2. Add Your First Tool

```bash
# Use the automated tool addition script
python3 scripts/add_tool.py <tool-name> <github-url>

# Example:
python3 scripts/add_tool.py manylatents https://github.com/cmvcordova/manyLatents.git
```

### 3. Create Your First Experiment

```bash
# Create an experiment config
cat > configs/my_first_experiment.yaml << EOF
tool: manylatents
experiment: my_experiment
description: "My first experiment"
tags: ["demo", "test"]
estimated_runtime: "5m"
EOF

# Run the experiment
python3 scripts/run_experiment manylatents my_first_experiment
```

### 4. Verify Everything Works

```bash
# Check your setup
python3 scripts/validate_setup.py

# List available experiments
python3 scripts/validate_setup.py --list-configs
```

## 📋 Core Concepts

### Tool Registration

Tools are registered in `configs/meta.yaml` with **critical entrypoint configuration**:

```yaml
tools:
  manylatents:
    path: tools/manylatents
    entrypoint: "-m src.main"        # ⚠️ CRITICAL: Module-style entrypoint
    commit: HEAD
    python_version: '3.9'
    dependencies: []
    description: 'ManyLatents dimensionality reduction framework'
```

### ⚠️ **ENTRYPOINT CONFIGURATION - CRITICAL**

The `entrypoint` field **MUST** match how your tool expects to be executed:

#### **Module-Style Entrypoints (Recommended)**
```yaml
entrypoint: "-m src.main"           # Runs: python -m src.main
entrypoint: "-m experiments.run"     # Runs: python -m experiments.run
```

#### **File-Style Entrypoints**
```yaml
entrypoint: "src/main.py"           # Runs: python src/main.py
entrypoint: "experiments/run.py"    # Runs: python experiments/run.py
```

#### **Why This Matters**
- **Module-style**: Allows relative imports (`from src.algorithms import ...`)
- **File-style**: Requires absolute imports or proper PYTHONPATH setup
- **Most Python packages work better with module-style execution**

### Experiment Organization

Top-level configs in `configs/` serve as **experiment organizers**:

```yaml
# configs/figure1_method_comparison/pca_swissroll.yaml
tool: manylatents                    # Which tool to use
experiment: swissroll_pca           # Which experiment within the tool
description: "PCA on Swiss roll data"
tags: ["pca", "swissroll", "method_comparison"]
estimated_runtime: "30m"
debug: true                         # Optional debug flag
```

## 🛠️ Tool Management

### Experiment Organization

Top-level configs in `configs/` serve as **experiment organizers**:

```yaml
# configs/figure1_method_comparison/pca_swissroll.yaml
tool: manylatents                    # Which tool to use
experiment: swissroll_pca           # Which experiment within the tool
description: "PCA on Swiss roll data"
tags: ["pca", "swissroll", "method_comparison"]
estimated_runtime: "30m"
debug: true                         # Optional debug flag
```

### Adding Tools

#### **Automated Method (Recommended)**
```bash
python3 scripts/add_tool.py <tool-name> <github-url> [--branch <branch>]

# Examples:
python3 scripts/add_tool.py manylatents https://github.com/cmvcordova/manyLatents.git
python3 scripts/add_tool.py mytool https://github.com/user/mytool.git --branch develop
```

#### **Manual Method**
```bash
# 1. Add as submodule
git submodule add <github-url> tools/<tool-name>

# 2. Update meta.yaml
# Edit configs/meta.yaml to add tool configuration

# 3. Set up environment
cd tools/<tool-name> && uv sync
```

### Removing Tools

```bash
python3 scripts/remove_tool.py <tool-name>

# Example:
python3 scripts/remove_tool.py manylatents
```

**⚠️ Warning**: This will remove all references to the tool and create a backup.

### Tool Configuration Schema

```yaml
tools:
  <tool-name>:
    path: tools/<tool-name>          # Required: Path to tool directory
    entrypoint: "<entrypoint>"       # Required: How to run the tool
    commit: HEAD                     # Optional: Git commit to track
    python_version: '3.9'           # Optional: Python version
    dependencies: []                 # Optional: Additional dependencies
    description: 'Tool description'  # Optional: Human-readable description
```

## 🧪 Experiment Management

### Creating Experiments

1. **Create experiment config in your tool repository**
2. **Create experiment organizer in `configs/`**
3. **Run the experiment**

```bash
# Create experiment organizer
cat > configs/my_experiment.yaml << EOF
tool: manylatents
experiment: my_experiment_name
description: "My experiment description"
tags: ["demo", "test"]
estimated_runtime: "10m"
EOF

# Run the experiment
python3 scripts/run_experiment manylatents my_experiment
```

### Experiment Config Schema

```yaml
tool: <tool-name>                    # Required: Which tool to use
experiment: <experiment-name>        # Required: Experiment name within tool
description: "Human description"     # Optional: Description
tags: ["tag1", "tag2"]             # Optional: Tags for organization
estimated_runtime: "30m"            # Optional: Runtime estimate
debug: true                         # Optional: Enable debug mode
```

### Running Experiments

```bash
# Basic experiment run
python3 scripts/run_experiment <tool> <config-path>

# With debug mode
python3 scripts/run_experiment <tool> <config-path> --debug

# Validate only (don't run)
python3 scripts/run_experiment <tool> <config-path> --validate-only

# Examples:
python3 scripts/run_experiment manylatents figure1_method_comparison/pca_swissroll
python3 scripts/run_experiment manylatents example_manylatents --debug
```

### Experiment Outputs

Experiments produce outputs in the tool's `outputs/` directory:

```bash
tools/<tool-name>/outputs/
├── YYYY-MM-DD/
│   └── HH-MM-SS/
│       ├── embeddings.csv          # Embedding data
│       ├── experiment_name.png     # Visualization plots
│       └── wandb/                 # Wandb logs (if enabled)
```

## 📁 Directory Structure

```
experimentstash/
├── configs/                          # Top-level experiment organizers
│   ├── meta.yaml                     # Tool definitions and metadata
│   ├── example_manylatents.yaml      # Example experiment config
│   └── figure1_method_comparison/    # Organized experiment groups
│       ├── pca_swissroll.yaml
│       └── umap_swissroll.yaml
├── tools/                            # Tool submodules
│   ├── manylatents/                  # Git submodule
│   │   ├── src/
│   │   │   ├── main.py              # Tool entrypoint
│   │   │   └── configs/experiment/  # Tool-specific configs
│   │   └── pyproject.toml           # Tool dependencies
│   └── .gitkeep
├── scripts/                          # Framework scripts
│   ├── add_tool.py                  # Tool addition utility
│   ├── remove_tool.py               # Tool removal utility
│   ├── run_experiment               # Main experiment runner
│   └── validate_setup.py            # Setup validation
├── outputs/                          # Experiment outputs
├── backups/                          # Tool removal backups
└── tests/                           # Framework tests
```

## 🔧 Advanced Configuration

### Environment Management

Each tool manages its own environment using `uv`:

```bash
# Set up tool environment
cd tools/<tool-name> && uv sync

# Run with tool environment
python3 scripts/run_experiment <tool> <config>
```

### Git State Management

The framework handles complex git state management:

- **Automatic cleanup** of leftover git directories
- **Index cleanup** for submodule operations
- **Force fallback** for stubborn git states
- **Complete removal** with backup creation

### Debugging

Enable debug mode for verbose output:

```bash
# Debug experiment run
python3 scripts/run_experiment <tool> <config> --debug

# Debug tool addition
python3 scripts/add_tool.py <tool> <url> --debug

# Validate setup with debug
python3 scripts/validate_setup.py --debug
```

## 🧪 Validation and Testing

### Setup Validation

```bash
# Validate entire setup
python3 scripts/validate_setup.py

# List available configs
python3 scripts/validate_setup.py --list-configs

# Validate specific tool
python3 scripts/validate_setup.py --tool <tool-name>
```

### Comprehensive Testing

```bash
# Run framework tests
python -m pytest tests/

# Test complete workflow
python test_workflow.py
```

## 🚨 Troubleshooting

### Common Issues

#### **"No module named 'src'" Error**
**Problem**: Tool expects module-style execution but configured for file-style
**Solution**: Update entrypoint in `configs/meta.yaml`:
```yaml
# Change from:
entrypoint: "src/main.py"
# To:
entrypoint: "-m src.main"
```

#### **"A git directory for 'tools/...' is found locally"**
**Problem**: Leftover git state from previous submodule operations
**Solution**: The framework automatically handles this. If persistent:
```bash
rm -rf tools/<tool-name>/.git
git rm --cached tools/<tool-name>
python3 scripts/add_tool.py <tool> <url>
```

#### **"already exists in the index" Error**
**Problem**: Git index still references the tool
**Solution**: The framework automatically handles this with enhanced cleanup.

#### **Process Killed (SIGKILL)**
**Problem**: Large datasets causing memory pressure
**Solution**: See the [Known Issues](#known-issues) section above for detailed solutions.

### Debug Mode

Enable debug mode for detailed error information:

```bash
python3 scripts/run_experiment <tool> <config> --debug
```

### Getting Help

1. **Check the logs**: Look for error messages in the output
2. **Validate setup**: Run `python3 scripts/validate_setup.py`
3. **Enable debug**: Add `--debug` flag to any command
4. **Check tool docs**: Each tool may have specific requirements

## 📚 Best Practices

### Tool Development

1. **Use module-style entrypoints** when possible
2. **Structure your tool with clear entry points**
3. **Use relative imports within your tool**
4. **Provide clear experiment naming**

### Experiment Organization

1. **Group related experiments** in subdirectories
2. **Use descriptive experiment names**
3. **Include runtime estimates** for resource planning
4. **Add tags** for easy filtering and organization

### Git Workflow

1. **Commit tool changes** before adding to experimentstash
2. **Use semantic versioning** for tool releases
3. **Pin specific commits** for reproducibility
4. **Test tool removal** before committing

## 🔄 Workflow Examples

### Complete Tool Lifecycle

```bash
# 1. Add tool
python3 scripts/add_tool.py mytool https://github.com/user/mytool.git

# 2. Create experiment
cat > configs/my_experiment.yaml << EOF
tool: mytool
experiment: my_experiment
description: "My experiment"
tags: ["demo"]
estimated_runtime: "5m"
EOF

# 3. Run experiment
python3 scripts/run_experiment mytool my_experiment

# 4. Remove tool (if needed)
python3 scripts/remove_tool.py mytool
```

### Multi-Tool Experiment

```bash
# Set up multiple tools
python3 scripts/add_tool.py tool1 https://github.com/user/tool1.git
python3 scripts/add_tool.py tool2 https://github.com/user/tool2.git

# Create experiment configs
# configs/comparison/experiment1.yaml -> tool1
# configs/comparison/experiment2.yaml -> tool2

# Run comparison
python3 scripts/run_experiment tool1 comparison/experiment1
python3 scripts/run_experiment tool2 comparison/experiment2
```

## 📖 API Reference

### Scripts

#### `add_tool.py`
```bash
python3 scripts/add_tool.py <tool-name> <github-url> [--branch <branch>]
```
**Purpose**: Adds a tool as a Git submodule and configures it for use
**Actions**:
- Adds tool as submodule
- Updates meta.yaml with tool configuration
- Sets up uv environment for the tool
- Creates example experiment config

#### `remove_tool.py`
```bash
python3 scripts/remove_tool.py <tool-name> [--force]
```
**Purpose**: Completely removes a tool and all its references
**Actions**:
- Removes tool submodule
- Cleans up metadata in meta.yaml
- Creates backup of tool data
- Warns about dependent configs

#### `run_experiment`
```bash
python3 scripts/run_experiment <tool> <config-path> [--debug] [--validate-only]
```
**Purpose**: Executes experiments with proper error handling
**Actions**:
- Validates setup and configurations
- Loads experiment configs
- Executes experiment in tool's environment
- Handles errors and timeouts gracefully

#### `validate_setup.py`
```bash
python3 scripts/validate_setup.py [--list-configs] [--tool <tool>] [--debug]
```
**Purpose**: Validates the entire experimentStash setup
**Actions**:
- Validates tool configurations
- Checks experiment mappings
- Lists available configs
- Reports configuration issues

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

## 📄 License

[Your License Here]

---

**Built with ❤️ for reproducible research**
