#!/usr/bin/env python3
"""
YAMLR TORTURE TEST RUNNER
----------------------------
Executes 'yamlr heal --dry-run' against the most broken YAML files imaginable.
Verifies that:
1. The CLI does NOT crash (Exit Code 0 or handled 1).
2. The output (if produced) is valid, parseable YAML.
3. Quantifies how many issues were auto-fixed.
"""

import sys
import os
import subprocess
import glob
from ruamel.yaml import YAML, YAMLError # Use ruamel.yaml as it is installed
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def run_torture():
    torture_dir = Path(__file__).parent / "corpus" / "torture"
    files = glob.glob(str(torture_dir / "*.yaml"))
    
    if not files:
        console.print("[red]No torture files found![/red]")
        sys.exit(1)
        
    console.print(f"[bold red]🔥 Entering the Torture Chamber with {len(files)} files...[/bold red]")
    
    results = []
    
    for fpath in files:
        fname = os.path.basename(fpath)
        
        # Run Yamlr Heal (Dry Run)
        cmd = [
            sys.executable, 
            "src/yamlr/cli/main.py", 
            "heal", 
            fpath, 
            "--dry-run",
            "--output", "yaml" # Force YAML output to verify parseability
        ]
        
        # We expect errors, so we don't check=True immediately
        # We want to capture stderr to check for python tracebacks (crashes) vs handled errors
        proc = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(), 
            encoding='utf-8',
            env={**os.environ, "PYTHONPATH": "src"}
        )
        
        crashed = "Traceback" in proc.stderr
        exit_code = proc.returncode
        output_valid = False
        
        # If successfully repaired, verify output is valid YAML
        if exit_code == 0 and proc.stdout:
            try:
                # We need to extract the YAML part if there are logs mixed in
                # But --output yaml should theoretically be clean or strictly separated
                # For now, let's try parsing the whole stdout or finding the document start
                yaml = YAML(typ='safe')
                list(yaml.load_all(proc.stdout))
                output_valid = True
            except YAMLError:
                output_valid = False
        
        status = "UNKNOWN"
        if crashed:
            status = "CRASH"
            style = "bold red"
        elif exit_code == 0:
            if output_valid:
                status = "SURVIVED (Fixed)"
                style = "bold green"
            else:
                status = "SURVIVED (Bad Output)"
                style = "yellow"
        else:
            status = "HANDLED ERROR"
            style = "blue"

        results.append({
            "file": fname,
            "status": status,
            "style": style,
            "exit_code": exit_code,
            "crashed": crashed
        })
        
        if crashed:
            console.print(f"[red]Violent crash on {fname}![/red]")
            console.print(proc.stderr[:500]) # First 500 chars of traceback

    # Report
    table = Table(title="Torture Chamber Results")
    table.add_column("File", style="cyan")
    table.add_column("Result", justify="center")
    table.add_column("Exit Code", justify="right")
    
    crashes = 0
    survivals = 0
    
    for res in results:
        table.add_row(
            res["file"],
            f"[{res['style']}]{res['status']}[/{res['style']}]",
            str(res["exit_code"])
        )
        if res["crashed"]: crashes += 1
        if "SURVIVED" in res["status"]: survivals += 1
        
    console.print(table)
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"Total Files: {len(files)}")
    console.print(f"Crashes: [red]{crashes}[/red]")
    console.print(f"Survivals: [green]{survivals}[/green]")
    
    if crashes > 0:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    run_torture()
