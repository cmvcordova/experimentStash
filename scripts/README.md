# experimentStash Scripts

This directory contains utility scripts for managing experimentStash.

## 🚀 Core Scripts

### `add_tool.py` - Add New Tools
```bash
python scripts/add_tool.py <tool_name> <github_url>
```
**Adds new tools to your experimentStash** - fully automated setup with dependency management.

### `remove_tool.py` - Remove Tools  
```bash
python scripts/remove_tool.py <tool_name>
```
**Removes tools safely** - handles cleanup with automatic backups.

### `run_experiment` - Run Experiments
```bash
python scripts/run_experiment <tool> <config_path>
```
**Runs experiments with direct config paths** - the main experiment execution script.

### `validate_setup.py` - Validate Setup
```bash
python scripts/validate_setup.py
```
**Validates your experimentStash setup** - comprehensive validation script.

## 📋 Script Functions

| Script | Purpose | Status |
|--------|---------|--------|
| `add_tool.py` | Add tools with full automation | ✅ **Primary** |
| `remove_tool.py` | Remove tools safely | ✅ **Primary** |
| `run_experiment` | Run experiments | ✅ **Primary** |
| `validate_setup.py` | Validate setup | ✅ **Primary** |

## 🎯 Quick Start

### 1. Add a Tool
```bash
python scripts/add_tool.py manylatents https://github.com/cmvcordova/manyLatents.git
```

### 2. Run an Experiment
```bash
python scripts/run_experiment manylatents figure1_method_comparison/pca_swissroll
```

### 3. Validate Setup
```bash
python scripts/validate_setup.py
```

## 📝 Notes

- All scripts use `uv` for dependency management
- All scripts support `--help` for usage information
- Scripts are designed to be run from the experimentStash root directory
- Error handling and validation are built into each script
- Experiment outputs are saved to `tools/<tool_name>/outputs/` 