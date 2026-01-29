
import os
from pathlib import Path

DEFAULT_CONFIG = """# Akeso Configuration File
# Documentation: https://akeso.dev/config

rules:
  # Minimum health score (0-100) to fail the pipeline
  threshold: 80
  
  # Ignore specific rules globally
  # ignore:
  #   - "rules/no-latest-tag"
  #   - "rules/resource-limits"

ignore:
  # Paths to exclude from scanning (glob patterns)
  files:
    - "test/*"
    - "vendor/**"

output:
  # Default output format (text, json, sarif)
  format: text
"""

def handle_init_command(console):
    """Generates the .akeso.yaml file."""
    target = Path(".akeso.yaml")
    
    if target.exists():
        console.print("[yellow]⚠️  Configuration file .akeso.yaml already exists.[/yellow]")
        return 1
    
    try:
        target.write_text(DEFAULT_CONFIG, encoding="utf-8")
        console.print(f"[green]✅ Created configuration file: {target.absolute()}[/green]")
        console.print("[dim]Edit this file to customize rule thresholds and file ignores.[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Failed to create config file: {e}[/red]")
        return 1
        
    return 0
