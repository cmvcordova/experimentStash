#!/usr/bin/env python3
"""
Simple validation script to check if the experiment orchestration setup is working correctly.
"""

import yaml
import os
from pathlib import Path


def validate_meta_config():
    """Validate the meta.yaml configuration."""
    print("🔍 Validating meta.yaml...")
    
    try:
        with open("configs/meta.yaml", "r") as f:
            meta = yaml.safe_load(f)
        
        # Check required sections
        assert "tools" in meta, "Missing 'tools' section"
        assert "experiment" in meta, "Missing 'experiment' section"
        
        # Check that tools section has at least one tool
        assert len(meta["tools"]) > 0, "No tools defined in meta.yaml"
        
        print("✅ meta.yaml structure is valid")
        
        # Check each tool
        for tool_name, tool_config in meta["tools"].items():
            print(f"  📦 Tool: {tool_name}")
            assert "path" in tool_config, f"Tool {tool_name} missing 'path'"
            assert "entrypoint" in tool_config, f"Tool {tool_name} missing 'entrypoint'"
            
            # Check if tool directory exists
            tool_path = tool_config["path"]
            assert os.path.exists(tool_path), f"Tool path {tool_path} does not exist"
            print(f"    ✅ Path: {tool_path}")
            
            # Check if tool has config_path_support
            if "config_path_support" in tool_config:
                print(f"    ✅ Config path support: {tool_config['config_path_support']}")
        
        return True
        
    except Exception as e:
        print(f"❌ meta.yaml validation failed: {e}")
        return False


def validate_runs_config():
    """Validate the runs.yaml configuration."""
    print("🔍 Validating runs.yaml...")
    
    try:
        with open("configs/runs.yaml", "r") as f:
            runs = yaml.safe_load(f)
        
        assert "runs" in runs, "Missing 'runs' section"
        assert len(runs["runs"]) > 0, "No runs defined in runs.yaml"
        
        print("✅ runs.yaml structure is valid")
        
        # Check each run
        for run_name, run_config in runs["runs"].items():
            print(f"  🏃 Run: {run_name}")
            assert "tool" in run_config, f"Run {run_name} missing 'tool'"
            assert "config" in run_config, f"Run {run_name} missing 'config'"
            
            tool_name = run_config["tool"]
            config_path = run_config["config"]
            
            print(f"    📦 Tool: {tool_name}")
            print(f"    📄 Config: {config_path}")
            
            # Check if top-level config exists
            top_level_config_path = f"configs/{config_path}.yaml"
            assert os.path.exists(top_level_config_path), f"Top-level config not found: {top_level_config_path}"
            print(f"    ✅ Top-level config exists")
        
        return True
        
    except Exception as e:
        print(f"❌ runs.yaml validation failed: {e}")
        return False


def validate_top_level_configs():
    """Validate top-level configs are in correct format."""
    print("🔍 Validating top-level configs...")
    
    try:
        config_dir = Path("configs/figure1_method_comparison")
        assert config_dir.exists(), "figure1_method_comparison config directory not found"
        
        config_files = [f for f in config_dir.glob("*.yaml") if f.name != ".gitkeep"]
        assert len(config_files) > 0, "No config files found in figure1_method_comparison"
        
        print(f"✅ Found {len(config_files)} config files")
        
        for config_file in config_files:
            print(f"  📄 Config: {config_file.name}")
            
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ["tool", "experiment", "description", "tags", "estimated_runtime"]
            for field in required_fields:
                assert field in config, f"Missing '{field}' in {config_file.name}"
            
            print(f"    ✅ All required fields present")
            
            # Check that tool is manylatents
            assert config["tool"] == "manylatents", f"Tool should be 'manylatents' in {config_file.name}"
            print(f"    ✅ Tool: {config['tool']}")
            
            # Check that experiment exists in tool
            experiment_name = config["experiment"]
            tool_experiment_file = f"tools/manylatents/src/configs/experiment/{experiment_name}.yaml"
            assert os.path.exists(tool_experiment_file), f"Experiment {experiment_name} not found in tool"
            print(f"    ✅ Experiment: {experiment_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Top-level config validation failed: {e}")
        return False


def validate_run_experiment_script():
    """Validate that the run_experiment script exists and can be imported."""
    print("🔍 Validating run_experiment script...")
    
    try:
        script_path = Path("scripts/run_experiment")
        assert script_path.exists(), "run_experiment script not found"
        print("✅ run_experiment script exists")
        
        # Test that it can be imported (basic syntax check)
        import subprocess
        result = subprocess.run(["python3", "-m", "py_compile", str(script_path)], 
                              capture_output=True, text=True)
        assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"
        print("✅ run_experiment script syntax is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ run_experiment script validation failed: {e}")
        return False


def main():
    """Run all validations."""
    print("🚀 Validating experiment orchestration setup...\n")
    
    validations = [
        validate_meta_config,
        validate_runs_config,
        validate_top_level_configs,
        validate_run_experiment_script,
    ]
    
    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
        except Exception as e:
            print(f"❌ Validation failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("📊 Validation Summary:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} validations passed!")
        print("\n🎉 Your experiment orchestration setup is ready to use!")
        print("\nYou can now run experiments with:")
        print("  python scripts/run_experiment manylatents pca_swissroll")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} validations failed")
        print("\nPlease fix the issues above before running experiments.")
        return 1


if __name__ == "__main__":
    exit(main()) 