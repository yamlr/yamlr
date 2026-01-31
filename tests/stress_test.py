#!/usr/bin/env python3
"""
STRESS & EDGE CASE VERIFICATION
-------------------------------
Generates pathological YAML inputs to test robustness.

Scenarios:
1. "The Monolith": 5MB+ YAML file with 10k+ lines.
2. "Emoji Storm": Keys and values with Unicode characters.
3. "Norway Problem": Keys that get misparsed by standard loaders (NO, ON, OFF).
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def generate_monolith(path: Path):
    print(f"Generating 5MB Monolith at {path}...")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: monolith\ndata:\n")
        f.write("  # A storm of data\n")
        for i in range(50000):
            f.write(f"  key_{i}: 'value_{i}_🚀'\n")
            
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"Generated {size_mb:.2f} MB file.")

def generate_edge_cases(path: Path):
    print(f"Generating Edge Cases at {path}...")
    content = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: edge-cases
data:
  # The Norway Problem (ISO Country Codes treated as booleans)
  NO: "Norway"
  ON: "Ontario"
  OFF: "Offline"
  
  # Emoji Keys
  \U0001F4BE: "Floppy"
  \U0001F680: "Rocket"
  
  # Deep Nesting
  deep:
    level1:
      level2:
        level3:
          level4:
            val: "Bottom"
"""
    path.write_text(content, encoding='utf-8')

def run_cli_scan(path: Path):
    cmd = [sys.executable, "src/yamlr/cli/main.py", "scan", str(path), "--summary-only"]
    print(f"Running scan (output muted)...")
    
    start = time.time()
    # Force UTF-8 environment for subprocess
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="d:/kubecuro", encoding='utf-8', env=env)
    duration = time.time() - start
    
    print(f"Exit Code: {result.returncode}")
    print(f"Duration: {duration:.4f}s")
    
    if result.returncode != 0:
        print("STDERR (Last 500 chars):", result.stderr[-500:])
        return False
        
    print("STDOUT Head (Last 100 chars):", result.stdout[-100:])
    return True

def main():
    base_dir = Path("d:/kubecuro/tests/stress_out")
    base_dir.mkdir(exist_ok=True)
    
    # Test 1: Edge Cases
    edge_file = base_dir / "edge.yaml"
    generate_edge_cases(edge_file)
    if not run_cli_scan(edge_file):
        print("❌ Edge Case Test Failed")
        sys.exit(1)
    
    # Test 2: Monolith (Performance)
    mono_file = base_dir / "monolith.yaml"
    generate_monolith(mono_file)
    if not run_cli_scan(mono_file):
        print("❌ Monolith Stress Test Failed")
        sys.exit(1)
        
    print("\n✅ All Stress Tests Passed!")

if __name__ == "__main__":
    main()
