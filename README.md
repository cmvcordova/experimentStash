# ExperimentStash

**TL;DR:** A modern experiment template for reproducible ML research with multiple tools.

```bash
git clone --recurse-submodules <repo> my-paper \
  && cd my-paper \
  && python scripts/setup_tool.py hello-world <tool-url> \
  && python tools/hello-world/src/main.py --config-name hello_world
```

## Table of Contents

- [Purpose](#purpose)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Scripts & Commands](#scripts--commands)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Purpose

ExperimentStash provides a template for organizing ML experiments with:
- **Multiple tools as Git submodules** in `tools/`
- **Centralized configuration** in `configs/`
- **Shared analysis notebooks** in `notebooks/`
- **Unified outputs** in `outputs/`
- **Reproducible workflows** with commit pinning

## Quick Start

### 1. Clone this template (with submodules)

```bash
$ git clone --recurse-submodules https://github.com/YOUR_USERNAME/experiment-stash.git my-paper
$ cd my-paper

# If you forgot --recurse-submodules, initialize them:
$ git submodule update --init --recursive
```

### 2. Add your ML tool(s)

```bash
$ python scripts/setup_tool.py hello-world https://github.com/YOUR_USERNAME/my-tool.git
```

### 3. Configure your experiments

Edit the configuration files:
- `configs/meta.yaml` - Declare your tools
- `configs/runs.yaml` - Define experiments
- `configs/your_experiment.yaml` - Experiment-specific configs

### 4. Run an experiment

```bash
$ python tools/hello-world/src/main.py --config-name hello_world
```

## Project Structure

```
experiment-stash/                      # Your experiment repository
├── configs/                           # Central experiment configurations
│   ├── meta.yaml                     # Tool declarations and metadata
│   ├── runs.yaml                     # Named experiment definitions
│   ├── hello_world.yaml             # Example experiment config
│   └── baseline_experiment.yaml     # Your experiment configs
├── notebooks/                         # Jupyter analyses across tools
├── outputs/                          # Experiment outputs and artifacts
├── tools/                            # Tool submodules
│   ├── hello-world/                 # Example tool (included)
│   └── my-tool/                     # Your tools (added as submodules)
├── scripts/                          # Utility scripts
│   ├── setup_tool.py               # Add new tools
│   └── validate_configs.py          # Validate configuration
├── expstash.toml                    # Template configuration
├── pyproject.toml                    # Top-level dependencies
└── README.md                         # This file
```

## Configuration

### Configuration File Interaction

| File | Purpose | Authority |
|------|---------|-----------|
| `expstash.toml` | Template settings (paths, logging) | **Authoritative** for template settings |
| `configs/meta.yaml` | Tool declarations and metadata | **Authoritative** for tools |
| `configs/runs.yaml` | Named experiment definitions | **Authoritative** for runs |
| `configs/*.yaml` | Experiment-specific configs | **Authoritative** for experiments |

### configs/meta.yaml
Single source of truth for tool metadata:

```yaml
tools:
  hello-world:
    path: tools/hello-world
    entrypoint: src/main.py
    commit: HEAD  # Track main branch for development
    python_version: "3.8"
    dependencies: ["pyyaml>=6.0"]
    description: "Minimal hello-world tool"

experiment:
  name: "my-paper"
  description: "My research paper experiments"
  authors: ["Your Name"]
  date_created: "2024-01-01"

validation:
  require_commit_pins: false  # Allow branch tracking
  validate_configs: true
  check_dependencies: true
```

### configs/runs.yaml
Define named experiments:

```yaml
runs:
  hello_world:
    tool: hello-world
    config: hello_world
    description: "Hello World: Demonstration of the template"
    tags: ["demo", "template"]
    estimated_runtime: "1s"

  baseline:
    tool: hello-world
    config: baseline_experiment
    description: "Baseline experiment to establish performance"
    tags: ["baseline", "template"]
    estimated_runtime: "2h"
    depends_on: []  # No dependencies
```

### expstash.toml
Template configuration settings:

```toml
[paths]
config_dir = "configs"
output_dir = "outputs"
tools_dir = "tools"

[reproducibility]
pin_commits = false  # Allow branch tracking for development
validate_submodules = true
check_uncommitted_changes = true

[logging]
log_level = "INFO"
log_file = "outputs/logs/experiment.log"
```

## Environment Management

### Dependency Management with uv

This template uses [uv](https://github.com/astral-sh/uv) for fast, reproducible dependency management.

```bash
$ # Install all dependencies (top-level and dev)
$ uv sync --extra dev

$ # Add a new dependency
$ uv add <package>

$ # Add a dev dependency
$ uv add --dev <package>

$ # Install tool-specific dependencies
$ cd tools/hello-world
$ uv sync
```

**Note:** You do not need to create or activate a venv; uv manages isolation for you.

### Code Quality with pre-commit

This project uses pre-commit hooks to ensure code quality:

```bash
$ # Install pre-commit hooks
$ pre-commit install

$ # Run on all files
$ pre-commit run --all-files

$ # Update pre-commit hooks
$ pre-commit autoupdate
```

## Scripts & Commands

### Core Scripts

```bash
$ # Add a new tool
$ python scripts/setup_tool.py my-tool https://github.com/user/my-tool.git

$ # Validate configurations
$ python scripts/validate_configs.py

$ # Validate configurations (skip tool tests)
$ python scripts/validate_configs.py --skip-tool-tests
```

### Running Experiments

```bash
# Direct tool execution (recommended)
$ python tools/hello-world/src/main.py --config-name hello_world

# Run with specific config file
$ python tools/hello-world/src/main.py --config-path configs/my_experiment.yaml
```

## Testing

### Run Tests

```bash
$ # Run all tests
$ pytest

$ # Run with verbose output
$ pytest -v

$ # Run specific test file
$ pytest tests/test_setup.py
```

### Validation

```bash
$ # Validate all configurations
$ python scripts/validate_configs.py

$ # Test tool imports
$ python scripts/validate_configs.py --skip-tool-tests

$ # Run the hello-world example
$ python tools/hello-world/src/main.py --config-name hello_world
```

## Contributing

1. **Add new tools** using `scripts/setup_tool.py`
2. **Update metadata** in `configs/meta.yaml`
3. **Create configs** in `configs/`
4. **Define experiments** in `configs/runs.yaml`
5. **Test everything** with `python scripts/validate_configs.py`

### How to File Issues

- **Bug reports**: Include error messages and steps to reproduce
- **Feature requests**: Describe the use case and expected behavior
- **Questions**: Check [PITFALLS.md](PITFALLS.md) first

For detailed troubleshooting and advanced workflows, see:
- [PITFALLS.md](PITFALLS.md) - Common issues and solutions
- [WORKFLOW.md](WORKFLOW.md) - Advanced CI/CD examples

## License

Licensed under MIT. See [LICENSE](LICENSE).
