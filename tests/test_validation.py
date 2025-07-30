#!/usr/bin/env python3
"""
Tests for core functionality validation.
"""

from pathlib import Path
import yaml
import os


def test_run_experiment_script_exists() -> None:
    """Test that the run_experiment script exists."""
    script_path = Path("scripts/run_experiment")
    assert script_path.exists(), "run_experiment script not found"


def test_meta_yaml_structure() -> None:
    """Test that meta.yaml has the correct structure for core functionality."""
    with open("configs/meta.yaml", "r") as f:
        meta = yaml.safe_load(f)

    # Check required top-level sections
    assert "tools" in meta, "Missing 'tools' section"
    assert "experiment" in meta, "Missing 'experiment' section"
    assert "validation" in meta, "Missing 'validation' section"

    # Check that tools section has at least one tool
    assert len(meta["tools"]) > 0, "No tools defined in meta.yaml"

    # Check that manylatents tool exists (our core tool)
    assert "manylatents" in meta["tools"], "manylatents tool not found in meta.yaml"

    # Check tool structure
    manylatents = meta["tools"]["manylatents"]
    assert "path" in manylatents, "manylatents tool missing 'path'"
    assert "entrypoint" in manylatents, "manylatents tool missing 'entrypoint'"
    assert "config_path_support" in manylatents, "manylatents tool missing 'config_path_support'"
    assert manylatents["config_path_support"] is True, "manylatents config_path_support should be True"


def test_runs_yaml_structure() -> None:
    """Test that runs.yaml has the correct structure."""
    with open("configs/runs.yaml", "r") as f:
        runs = yaml.safe_load(f)

    assert "runs" in runs, "Missing 'runs' section"
    assert len(runs["runs"]) > 0, "No runs defined in runs.yaml"

    # Check that at least one run references manylatents tool
    has_manylatents = any(
        run_config.get("tool") == "manylatents" for run_config in runs["runs"].values()
    )
    assert has_manylatents, "No runs reference manylatents tool"


def test_top_level_configs_format() -> None:
    """Test that top-level configs are in the correct format."""
    config_dir = Path("configs/figure1_method_comparison")
    assert config_dir.exists(), "figure1_method_comparison config directory not found"

    # Check each config file
    for config_file in config_dir.glob("*.yaml"):
        if config_file.name == ".gitkeep":
            continue
            
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        assert "tool" in config, f"Missing 'tool' in {config_file.name}"
        assert "experiment" in config, f"Missing 'experiment' in {config_file.name}"
        assert "description" in config, f"Missing 'description' in {config_file.name}"
        assert "tags" in config, f"Missing 'tags' in {config_file.name}"
        assert "estimated_runtime" in config, f"Missing 'estimated_runtime' in {config_file.name}"
        
        # Check that tool is manylatents
        assert config["tool"] == "manylatents", f"Tool should be 'manylatents' in {config_file.name}"


def test_tool_experiments_exist() -> None:
    """Test that the experiments referenced in top-level configs exist in the tool."""
    config_dir = Path("configs/figure1_method_comparison")
    tool_experiment_dir = Path("tools/manylatents/src/configs/experiment")
    
    assert tool_experiment_dir.exists(), "Tool experiment directory not found"
    
    # Check each top-level config
    for config_file in config_dir.glob("*.yaml"):
        if config_file.name == ".gitkeep":
            continue
            
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        experiment_name = config["experiment"]
        experiment_file = tool_experiment_dir / f"{experiment_name}.yaml"
        
        assert experiment_file.exists(), f"Experiment {experiment_name} not found in tool"


def test_run_experiment_config_loading() -> None:
    """Test that the run_experiment script can load configs properly."""
    # This test simulates the config loading logic from run_experiment
    import yaml
    
    # Load meta config
    with open("configs/meta.yaml", "r") as f:
        meta_config = yaml.safe_load(f)
    
    # Load runs config
    with open("configs/runs.yaml", "r") as f:
        runs_config = yaml.safe_load(f)
    
    # Test finding a run
    run_key = None
    for key, run_info in runs_config.get("runs", {}).items():
        if run_info.get("tool") == "manylatents":
            config_path = run_info.get("config", "")
            if config_path.endswith("/pca_swissroll"):
                run_key = key
                break
    
    assert run_key is not None, "Could not find pca_swissroll run"
    
    # Test loading top-level config
    config_path = runs_config["runs"][run_key]["config"]
    top_level_config_path = f"configs/{config_path}.yaml"
    
    assert os.path.exists(top_level_config_path), f"Top-level config not found: {top_level_config_path}"
    
    with open(top_level_config_path, "r") as f:
        top_level_config = yaml.safe_load(f)
    
    experiment_name = top_level_config.get("experiment")
    assert experiment_name is not None, "No experiment specified in top-level config"
    
    # Test that the experiment exists in the tool
    tool_experiment_file = f"tools/manylatents/src/configs/experiment/{experiment_name}.yaml"
    assert os.path.exists(tool_experiment_file), f"Tool experiment not found: {tool_experiment_file}"
