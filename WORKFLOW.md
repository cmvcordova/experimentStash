# Advanced Workflows

This document contains advanced CI/CD examples and workflow patterns for the ExperimentStash template.

## GitHub Actions Workflows

### CI Workflow

The main CI workflow runs on every push and pull request:

```yaml
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install uv
      uses: astral-sh/setup-uv@v1
      with:
        version: latest

    - name: Install dependencies
      run: |
        uv sync --extra dev

    - name: Run pre-commit
      run: |
        pre-commit run --all-files

    - name: Run tests
      run: |
        pytest -v

    - name: Run validation
      run: |
        python scripts/validate_configs.py --skip-tool-tests
```

### Release Workflow

Automated releases triggered by version tags:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install uv
      uses: astral-sh/setup-uv@v1
      with:
        version: latest

    - name: Install dependencies
      run: |
        uv sync --extra dev

    - name: Run tests
      run: |
        pytest -v

    - name: Run validation
      run: |
        python scripts/validate_configs.py

    - name: Build package
      run: |
        uv build

    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push'

    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install uv
      uses: astral-sh/setup-uv@v1
      with:
        version: latest

    - name: Download build artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Local Development Workflow

### Setting Up a New Experiment

```bash
# 1. Clone the template
git clone --recurse-submodules https://github.com/user/experiment-stash.git my-paper
cd my-paper

# 2. Setup environment
uv sync --extra dev
pre-commit install

# 3. Add your tools
python scripts/setup_tool.py my-tool https://github.com/user/my-tool.git

# 4. Configure experiments
# Edit configs/meta.yaml, configs/runs.yaml, and create experiment configs

# 5. Validate setup
python scripts/validate_configs.py

# 6. Run experiments
python tools/hello-world/src/main.py --config-name hello_world
```

### Daily Development Workflow

```bash
# Start of day
git pull origin main
git submodule update --remote --merge

# Make changes
# Edit configs, add tools, etc.

# Before committing
pre-commit run --all-files
pytest
python scripts/validate_configs.py

# Commit and push
git add .
git commit -m "Add new experiment configuration"
git push origin main
```

## Tool Development Workflow

### Creating a New Tool

```bash
# 1. Create tool repository
mkdir my-tool
cd my-tool

# 2. Initialize as Python package
uv init
# Edit pyproject.toml

# 3. Create tool structure
mkdir src
touch src/__init__.py
touch src/main.py

# 4. Implement tool
# Write main.py with config loading from parent configs/

# 5. Test locally
python src/main.py --config-name hello_world

# 6. Push to GitHub
git add .
git commit -m "Initial tool implementation"
git push origin main
```

### Tool Integration

```bash
# 1. Add tool to experiment template
python scripts/setup_tool.py my-tool https://github.com/user/my-tool.git

# 2. Update metadata
# Edit configs/meta.yaml

# 3. Create experiment configs
# Create configs/my_experiment.yaml

# 4. Define runs
# Edit configs/runs.yaml

# 5. Test integration
python scripts/validate_configs.py
python tools/my-tool/src/main.py --config-name my_experiment
```

## Release Workflow

### Creating a Release

```bash
# 1. Update version
# Edit pyproject.toml version

# 2. Update changelog
# Edit CHANGELOG.md

# 3. Commit changes
git add .
git commit -m "Bump version to 1.0.0"

# 4. Create tag
git tag v1.0.0

# 5. Push tag (triggers release workflow)
git push origin v1.0.0
```

### Automated Release Process

1. **Tag Creation**: Pushing a `v*` tag triggers the release workflow
2. **Testing**: All tests and validation run
3. **Building**: Package is built with `uv build`
4. **Publishing**: Package is published to PyPI
5. **GitHub Release**: Release notes are created automatically

## Advanced Patterns

### Multi-Tool Experiments

```yaml
# configs/runs.yaml
runs:
  baseline:
    tool: model-a
    config: baseline
    description: "Baseline experiment with Model A"
    estimated_runtime: "2h"

  comparison:
    tool: model-b
    config: comparison
    description: "Comparison experiment with Model B"
    estimated_runtime: "3h"
    depends_on: ["baseline"]

  analysis:
    tool: analysis-tool
    config: analysis
    description: "Analysis of both models"
    estimated_runtime: "1h"
    depends_on: ["baseline", "comparison"]
```

### Conditional Execution

```yaml
# configs/experiment.yaml
experiment:
  name: "conditional_experiment"
  conditions:
    gpu_available: true
    memory_gb: 16

model:
  type: "large"  # Only if conditions met
  fallback_type: "small"  # Otherwise
```

### Parallel Execution

```yaml
# configs/parallel_runs.yaml
runs:
  sweep_1:
    tool: hyperopt
    config: sweep_1
    parallel: true
    max_workers: 4

  sweep_2:
    tool: hyperopt
    config: sweep_2
    parallel: true
    max_workers: 4
    depends_on: ["sweep_1"]
```
