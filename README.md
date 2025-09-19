# ExperimentStash: General-Purpose Hydra Tool Orchestrator

A simple, powerful framework for orchestrating experiments across any Hydra-based tools with clean separation of concerns.

## 🎯 Overview

ExperimentStash provides a **tool-agnostic experiment orchestration system** that:
- **Works with any Hydra-based tool** without modification
- **Keeps experiment configs at the top level** for easy organization
- **Maintains complete separation** between orchestrator and tools
- **Provides unified execution interface** across diverse tools
- **Ensures reproducible workflows** with proper environment management

## ✨ Key Features

- 🔧 **Zero-Configuration Tool Integration**: Works with any Hydra tool out of the box
- 📁 **Clean Architecture**: Top-level configs, isolated tool environments
- 🔄 **Reproducible Environments**: Each tool has its own `uv`-managed environment
- 🎛️ **Unified Interface**: Same command structure for all tools
- 📊 **Built-in Validation**: Comprehensive setup and config validation
- 🧪 **Template Ready**: Includes working test tool for immediate use

## 🚀 Quick Start

### 1. Test the Template

The repository includes a working test tool to verify integration:

```bash
# Test the framework immediately
python3 scripts/run_experiment hydra-test-tool test_integration

# Validate setup
python3 scripts/run_experiment hydra-test-tool test_integration --validate-only
```

**Expected Output:**
```
🎉 SUCCESS: Hydra integration working!
📝 Message from config: Hello from top-level ExperimentStash config! Integration working perfectly!
✅ Top-level configs integrated successfully!
```

### 2. Add Your Own Tool

```bash
# Option A: Add existing tool as git submodule
git submodule add <your-tool-repo-url> tools/<tool-name>
cd tools/<tool-name> && uv sync

# Option B: Copy/create your tool in tools/ directory
mkdir tools/my-hydra-tool
# ... set up your tool ...
```

### 3. Register Your Tool

Edit `configs/meta.yaml`:

```yaml
tools:
  my-hydra-tool:
    path: tools/my-hydra-tool
    entrypoint: src/main.py  # or "-m src.main" for module-style
    description: "My awesome Hydra-based tool"
```

### 4. Create Experiment Config

```yaml
# configs/my_experiment.yaml
tool: my-hydra-tool
experiment: my_experiment_name
description: "My first experiment"
tags: ["demo", "test"]
estimated_runtime: "5m"

# Your experiment parameters here
message: "Hello from my experiment!"
params:
  learning_rate: 0.001
  batch_size: 32
```

### 5. Run Your Experiment

```bash
python3 scripts/run_experiment my-hydra-tool my_experiment
```

## 📋 Core Architecture

### Clean Separation of Concerns

```
experimentstash/
├── configs/                    # 🎯 Top-level experiment definitions
│   ├── meta.yaml              # Tool registry
│   ├── test_integration.yaml  # Example working config
│   └── my_experiment.yaml     # Your experiment configs
├── tools/                     # 🔧 Isolated tool environments
│   ├── hydra-test-tool/       # Example minimal Hydra tool
│   └── my-hydra-tool/         # Your Hydra-based tools
└── scripts/                   # 🛠️ Orchestration scripts
    └── run_experiment         # Main experiment runner
```

### How It Works

1. **Top-level configs** define what experiment to run and with which tool
2. **Tools** are self-contained Hydra applications with their own environments
3. **Orchestrator** passes the top-level config directly to the tool via Hydra's standard flags
4. **No coupling** between orchestrator and tool internals

## 🛠️ Tool Integration

### Requirements for Tools

Your Hydra-based tool needs:

1. **Hydra main function** that accepts configs
2. **Proper entrypoint** (file or module)
3. **uv-compatible dependencies** (pyproject.toml/requirements.txt)

### Example Minimal Tool

```python
# tools/my-tool/src/main.py
import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path=None, config_name=None)
def main(cfg: DictConfig) -> None:
    print(f"Running experiment: {cfg.get('experiment', 'Unknown')}")
    print(f"Message: {cfg.get('message', 'No message')}")

    # Your tool logic here
    for key, value in cfg.get('params', {}).items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
```

### Tool Registration

```yaml
# configs/meta.yaml
tools:
  my-tool:
    path: tools/my-tool
    entrypoint: src/main.py        # File-style: python src/main.py
    # OR
    entrypoint: "-m src.main"      # Module-style: python -m src.main
    description: "Description of my tool"
```

**Choosing Entrypoint Style:**
- **File-style** (`src/main.py`): Simple, works for standalone scripts
- **Module-style** (`-m src.main`): Better for packages with relative imports

## 🧪 Experiment Configuration

### Basic Structure

```yaml
# Required fields
tool: my-tool                    # Which tool to use
experiment: experiment_name      # Identifier for your experiment

# Optional metadata
description: "Human-readable description"
tags: ["tag1", "tag2"]          # For organization
estimated_runtime: "30m"        # Planning aid

# Your experiment parameters (passed directly to tool)
message: "Hello from config!"
params:
  learning_rate: 0.001
  model_type: "transformer"
  data:
    batch_size: 32
    dataset: "my_dataset"
```

### Parameter Passing

Everything in your config (except the orchestrator fields) gets passed directly to your tool via Hydra:

```yaml
# This config...
tool: my-tool
experiment: test
custom_param: "hello"
nested:
  value: 42

# Becomes accessible in your tool as:
# cfg.custom_param == "hello"
# cfg.nested.value == 42
```

## 🔧 Command Reference

### Run Experiments

```bash
# Basic run
python3 scripts/run_experiment <tool> <config-name>

# Validate setup only
python3 scripts/run_experiment <tool> <config-name> --validate-only

# Examples
python3 scripts/run_experiment hydra-test-tool test_integration
python3 scripts/run_experiment my-tool my_experiment --validate-only
```

### Validation

```bash
# Validate entire setup
python3 scripts/validate_setup.py

# List available configs
python3 scripts/validate_setup.py --list-configs

# Check specific tool
python3 scripts/validate_setup.py --tool <tool-name>
```

## 📁 Directory Organization

### Organizing Experiments

Create subdirectories in `configs/` for related experiments:

```
configs/
├── meta.yaml
├── test_integration.yaml
├── paper_experiments/
│   ├── figure1_comparison.yaml
│   ├── figure2_ablation.yaml
│   └── table1_metrics.yaml
├── development/
│   ├── quick_test.yaml
│   └── debug_config.yaml
└── production/
    ├── final_model.yaml
    └── benchmark.yaml
```

Run with paths: `python3 scripts/run_experiment my-tool paper_experiments/figure1_comparison`

### Tool Directory Structure

```
tools/my-tool/
├── pyproject.toml         # Dependencies
├── uv.lock               # Locked environment
├── src/
│   ├── main.py           # Entry point
│   ├── algorithms/       # Tool code
│   └── utils/
└── .venv/                # Isolated environment
```

## 🚨 Troubleshooting

### Common Issues

#### "Tool not found in meta config"
**Problem**: Tool not registered in `configs/meta.yaml`
**Solution**: Add tool entry to meta.yaml

#### "Config file not found"
**Problem**: Config path doesn't match file location
**Solution**: Check that `configs/<config-name>.yaml` exists

#### "No module named X" Error
**Problem**: Wrong entrypoint style or missing dependencies
**Solution**:
- Check entrypoint in meta.yaml (file vs module style)
- Ensure tool dependencies are installed: `cd tools/<tool> && uv sync`

#### Tool Environment Issues
**Problem**: Dependencies not installed or conflicting versions
**Solution**:
```bash
cd tools/<tool-name>
rm -rf .venv uv.lock
uv sync
```

### Debug Mode

Add debug information to see what's happening:

```bash
# See full command construction and execution
HYDRA_FULL_ERROR=1 python3 scripts/run_experiment <tool> <config> --validate-only
```

## 🎯 Best Practices

### Tool Development
1. **Keep tools self-contained** with their own dependencies
2. **Use Hydra's config system** for maximum flexibility
3. **Test tools independently** before adding to orchestrator
4. **Use semantic versioning** for tool releases

### Experiment Organization
1. **Group related experiments** in subdirectories
2. **Use descriptive names** and tags
3. **Include runtime estimates** for resource planning
4. **Document experiment purposes** in descriptions

### Configuration Management
1. **Keep configs minimal** - only specify what you need to change
2. **Use consistent naming** across related experiments
3. **Version control your configs** along with results
4. **Test configs with validate-only** before running

## 🔄 Example Workflows

### Adding a New Tool

```bash
# 1. Add tool to repository
git submodule add https://github.com/user/my-tool.git tools/my-tool

# 2. Set up environment
cd tools/my-tool && uv sync && cd ../..

# 3. Register in meta.yaml
# Edit configs/meta.yaml to add tool entry

# 4. Create test config
cat > configs/test_my_tool.yaml << EOF
tool: my-tool
experiment: quick_test
description: "Test my tool integration"
message: "Hello from ExperimentStash!"
EOF

# 5. Test integration
python3 scripts/run_experiment my-tool test_my_tool --validate-only
python3 scripts/run_experiment my-tool test_my_tool
```

### Running Experiment Suite

```bash
# Run related experiments
python3 scripts/run_experiment my-tool paper_experiments/figure1
python3 scripts/run_experiment my-tool paper_experiments/figure2
python3 scripts/run_experiment my-tool paper_experiments/table1

# Validate before running suite
for config in paper_experiments/*; do
    python3 scripts/run_experiment my-tool $(basename $config .yaml) --validate-only
done
```

## 🧪 Testing Your Setup

The repository includes a working test tool that demonstrates the full integration:

```bash
# Test basic integration
python3 scripts/run_experiment hydra-test-tool test_integration

# Inspect the test tool
ls tools/hydra-test-tool/
cat tools/hydra-test-tool/src/main.py
cat configs/test_integration.yaml
```

This provides a working reference for creating your own tools and configs.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Test with the included test tool
4. Add your improvements
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built for reproducible research with any Hydra-based tool** 🧪⚡
