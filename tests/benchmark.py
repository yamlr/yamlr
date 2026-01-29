#!/usr/bin/env python3
"""
AKESO PERFORMANCE BENCHMARK
---------------------------
Measures throughput and latency on large datasets.
Target: Scan 50MB of YAML in reasonable time.
"""
import sys
import time
import os
from pathlib import Path
from kubecuro.core.engine import AkesoEngine

# Constants
TARGET_SIZE_MB = 10
OUTPUT_FILE = Path("tests/corpus/stress/benchmark_large.yaml")

TEMPLATE = """
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: benchmark-app-{i}
  labels:
    app: benchmark
    instance: "{i}"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: benchmark-{i}
  template:
    metadata:
      labels:
        app: benchmark-{i}
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: "500m"
            memory: "128Mi"
"""

def generate_large_file(path: Path, target_mb: int):
    print(f"Generating {target_mb}MB synthetic manifest...")
    with open(path, "w", encoding="utf-8") as f:
        i = 0
        while path.stat().st_size < (target_mb * 1024 * 1024):
            f.write(TEMPLATE.format(i=i))
            i += 1
    print(f"Generated {path.stat().st_size / 1024 / 1024:.2f} MB file with {i} documents.")

def run_benchmark():
    # Setup
    if not OUTPUT_FILE.parent.exists():
        OUTPUT_FILE.parent.mkdir(parents=True)
        
    generate_large_file(OUTPUT_FILE, TARGET_SIZE_MB)
    
    # Initialize Engine (exclude initiation time from benchmark)
    print("\nInitializing Engine...")
    engine = AkesoEngine(workspace_path=".", catalog_path="catalog/k8s_v1_distilled.json")
    
    print(f"Starting Scan on {OUTPUT_FILE}...")
    start_time = time.time()
    
    # Standard Scan
    result = engine.audit_and_heal_file(str(OUTPUT_FILE), dry_run=True)
    
    duration = time.time() - start_time
    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    throughput = file_size_mb / duration
    
    print(f"\nRESULTS:")
    print(f"--------------------------------------------------")
    print(f"File Size:      {file_size_mb:.2f} MB")
    print(f"Duration:       {duration:.4f} seconds")
    print(f"Throughput:     {throughput:.2f} MB/s")
    print(f"Success:        {result['success']}")
    print(f"Health Score:   {result['health_score']}")
    print(f"--------------------------------------------------")
    
    # Cleanup (optional, maybe keep for manual inspection)
    # OUTPUT_FILE.unlink()

if __name__ == "__main__":
    run_benchmark()
