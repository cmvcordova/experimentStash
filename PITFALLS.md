# Common Pitfalls & Solutions

This document contains detailed troubleshooting information for the ExperimentStash template.

## Submodule Issues

### Detached HEAD State

**Problem:** Detached HEAD state when pinning commits
```bash
# ❌ Don't do this
git submodule add https://github.com/user/tool.git tools/tool
cd tools/tool
git checkout abc1234  # Creates detached HEAD
```

**Solution:** Use branch tracking for development
```bash
# ✅ Do this instead
git submodule add -b main https://github.com/user/tool.git tools/tool
# Pin commits only for production releases
```

### Missing Submodules

**Problem:** Forgetting to clone submodules
```bash
# ❌ Don't do this
git clone https://github.com/user/template.git
# Submodules are missing!
```

**Solution:** Always use recursive clone
```bash
# ✅ Do this
git clone --recurse-submodules https://github.com/user/template.git
# Or initialize after cloning
git submodule update --init --recursive
```

## Path Resolution Issues

### Hydra Config Path Resolution

**Problem:** Hydra config_path resolution
```python
# ❌ Don't do this
@hydra.main(config_path="../configs", config_name="config")
def main(cfg):
    # This breaks when run from different directories
```

**Solution:** Use absolute paths
```python
# ✅ Do this
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent

@hydra.main(
    config_path=str(project_root / "configs"),
    config_name="config"
)
def main(cfg):
    # Works from any directory
```

## Environment Conflicts

### Mixing Dependency Managers

**Problem:** Mixing dependency managers
```bash
# ❌ Don't mix uv and pip
uv sync  # In CI
pip install -r requirements.txt  # Locally
```

**Solution:** Pick one dependency manager
```bash
# ✅ Use uv consistently
uv sync  # Both CI and local
```

## CI Setup Issues

### Missing Submodules in CI

**Problem:** CI forgets submodules
```yaml
# ❌ Don't do this
- uses: actions/checkout@v3
  # Missing submodules!
```

**Solution:** Always include submodules
```yaml
# ✅ Do this
- uses: actions/checkout@v3
  with:
    submodules: recursive
```

## Troubleshooting

### Tool Not Found
```bash
# Check if submodule is initialized
git submodule status

# Initialize missing submodules
git submodule update --init --recursive
```

### Config Loading Fails
```bash
# Check config file exists
ls configs/your_config.yaml

# Test config loading
python tools/your-tool/src/main.py --config-name your_config
```

### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Test tool import
cd tools/your-tool
python -c "import src"
```

## Best Practices

### For Tool Developers

1. **Load configs from parent**: Use absolute paths to `../../configs/`
2. **Handle command-line args**: Support `--config-name` and `--config-path`
3. **Provide clear errors**: Exit with meaningful error codes
4. **Document dependencies**: List all requirements in `pyproject.toml`

### For Experimenters

1. **Pin commits for production**: Use specific commits for reproducibility
2. **Track branches for development**: Use `HEAD` for active development
3. **Validate before committing**: Run validation scripts
4. **Document changes**: Update metadata when adding tools

### For CI/CD

1. **Always clone with submodules**: Use `--recurse-submodules`
2. **Test tool imports**: Verify each tool can be imported
3. **Validate configs**: Check all YAML files are valid
4. **Test on clean checkout**: Simulate new user experience
