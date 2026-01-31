#!/usr/bin/env python3
"""
YAMLR LEXER FUZZER
---------------------
Stress-test the Yamlr Lexer against a corpus of valid and broken YAML files.
Goal: Ensure NO CRASHES occur, regardless of input quality.
"""

import sys
import os
import time
import glob
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add src to path so we can import Yamlr modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from yamlr.parsers.lexer import YamlrLexer

console = Console()

def run_fuzz():
    corpus_dir = Path("d:/kubecuro/tests/corpus")
    files = glob.glob(str(corpus_dir / "**/*.yaml"), recursive=True)
    
    if not files:
        console.print("[red]No corpus files found![/red]")
        return
    
    console.print(f"[bold cyan]🚀 Starting Fuzz Test on {len(files)} files...[/bold cyan]")
    
    lexer = YamlrLexer()
    results = []
    crashes = 0
    norway_issues = 0
    
    for fpath in files:
        fname = os.path.basename(fpath)
        category = Path(fpath).parent.name
        
        try:
            start_time = time.time()
            raw_text = Path(fpath).read_text(encoding='utf-8')
            shards = lexer.shard(raw_text)
            duration = (time.time() - start_time) * 1000
            
            # Count repairs
            repairs = sum(lexer.repair_stats.values())
            
            status = "PASS"
            
            # Norway Problem Check
            if fname == "norway.yaml":
                for s in shards:
                    # Check if "NO" became boolean False or "ON" became True
                    # The lexer stores the raw value in `value` string
                    if s.key == "country" and s.value != "NO":
                        status = "WARN (Norway)"
                        norway_issues += 1
                        console.print(f"[yellow]⚠️ Norway Problem Detected: 'country' parsed as {s.value!r}[/yellow]")
                    elif s.key == "on_flag" and s.value != "ON":
                         status = "WARN (Norway)"
                         norway_issues += 1
                         console.print(f"[yellow]⚠️ Norway Problem Detected: 'on_flag' parsed as {s.value!r}[/yellow]")

            results.append({
                "file": fname,
                "category": category,
                "status": status,
                "shards": len(shards),
                "repairs": repairs,
                "time_ms": f"{duration:.2f}"
            })
            
        except Exception as e:
            crashes += 1
            results.append({
                "file": fname,
                "category": category,
                "status": "CRASH",
                "error": str(e),
                "time_ms": "N/A"
            })
            console.print(f"[bold red]💥 CRASH: {fname} ({category})[/bold red]")
            console.print(f"  Error: {e}")

    # Display Results
    table = Table(title="Lexer Fuzz Results")
    table.add_column("File", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Status", justify="center")
    table.add_column("Shards", justify="right")
    table.add_column("Repairs", justify="right")
    table.add_column("Time (ms)", justify="right")
    
    for res in results:
        status_style = "green"
        if "CRASH" in res["status"]: status_style = "bold red"
        elif "WARN" in res["status"]: status_style = "yellow"
        
        table.add_row(
            res["file"],
            res["category"],
            f"[{status_style}]{res['status']}[/{status_style}]",
            str(res.get("shards", "-")),
            str(res.get("repairs", "-")),
            res["time_ms"]
        )
        
    console.print(table)
    
    if crashes > 0:
        console.print(f"\n[bold red]❌ Fuzzing Failed: {crashes} crashes detected.[/bold red]")
        sys.exit(1)
    elif norway_issues > 0:
        console.print(f"\n[bold yellow]⚠️ Fuzzing Passed (No Crashes), but {norway_issues} type inference warnings detected.[/bold yellow]")
        sys.exit(0)
    else:
        console.print("\n[bold green]✅ Fuzzing Complete: 0 Crashes, 0 Norway Issues.[/bold green]")
        sys.exit(0)

if __name__ == "__main__":
    run_fuzz()
