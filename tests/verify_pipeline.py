#!/usr/bin/env python3
"""
VERIFY PIPELINE INTEGRATION
---------------------------
Tests if the refactored Analyzer Plugin System correctly:
1. Registers the CrossResourceAnalyzer
2. Detects a Ghost Service
3. Reports it in the audit log
"""

import sys
import os
import logging
from rich.console import Console

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from kubecuro.core.pipeline import HealingPipeline
from kubecuro.analyzers.registry import AnalyzerRegistry

# Configure logging
logging.basicConfig(level=logging.WARNING)
console = Console()

def test_pipeline():
    console.print("[bold cyan]🚀 Starting Pipeline Integration Test...[/bold cyan]")
    
    # 1. Check Registry
    analyzers = AnalyzerRegistry.get_all_analyzers()
    console.print(f"Registered Analyzers: {[a.name for a in analyzers]}")
    
    if not any(a.name == "cross-resource-analyzer" for a in analyzers):
        console.print("[bold red]❌ CrossResourceAnalyzer NOT detected in registry![/bold red]")
        sys.exit(1)
        
    # 2. Run Pipeline on Ghost Service
    ghost_manifest = """
apiVersion: v1
kind: Service
metadata:
  name: dead-end-svc
spec:
  selector:
    app: non-existent-app
  ports:
  - port: 80
"""
    
    pipeline = HealingPipeline(catalog={}) # Empty catalog is fine for this test
    healed, log, score, identities = pipeline.heal(ghost_manifest)
    
    # 3. Verify Output
    found_ghost = False
    for entry in log:
        if "Ghost Service detected" in entry:
            found_ghost = True
            console.print(f"[green]Found Log Entry:[/green] {entry.strip()}")
            
    if found_ghost:
        console.print("\n[bold green]✅ SUCCESS: Plugin system detected Ghost Service correctly.[/bold green]")
    else:
        console.print("\n[bold red]❌ FAILURE: Ghost Service NOT reported in audit log.[/bold red]")
        console.print("Full Log:")
        for l in log: print(l)
        sys.exit(1)

if __name__ == "__main__":
    test_pipeline()
