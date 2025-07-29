# Hello World Tool

A minimal tool for demonstrating the experiment template structure.

## Purpose

This tool shows how to:
1. Load configs from the parent `configs/` directory
2. Handle command-line arguments
3. Integrate with the experiment template workflow

## Usage

```bash
# Run with default config
python src/main.py

# Run with specific config
python src/main.py --config-name hello_world

# Run with custom config path
python src/main.py --config-name hello_world --config-path ../../configs
```

## Configuration

The tool expects a YAML config file in the parent `configs/` directory:

```yaml
# configs/hello_world.yaml
tool: hello-world
experiment:
  name: "hello_world_demo"
  description: "Demonstration of the hello-world tool"
  simulate_work: true
```

## Integration

This tool demonstrates the pattern for integrating any ML tool into the experiment template:

1. Load configs from parent directory
2. Handle command-line arguments
3. Provide clear error messages
4. Return appropriate exit codes
