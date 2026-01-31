import os
import yaml
import pkgutil
from rich.panel import Panel
from rich.markdown import Markdown

def load_rules():
    """Loads rules from the data directory."""
    try:
        # Try finding the resource relative to the package first
        # This handles both source and installed package cases
        data = pkgutil.get_data("yamlr.core", "data/rules.yaml")
        if data:
            return yaml.safe_load(data)
    except Exception:
        pass
        
    # Fallback for direct execution/dev mode
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "../data/rules.yaml")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    return {}

RULE_DB = load_rules()

def handle_explain_command(args, console):
    """
    Explains a specific rule or lists available rules.
    """
    rule_id = args.rule_id
    
    if not rule_id:
        console.print("[bold cyan]Available Rules:[/bold cyan]")
        for rid, data in RULE_DB.items():
            console.print(f" - [bold]{rid}[/bold]: {data['name']}")
        console.print("\n[dim]Usage: Yamlr explain <rule_id>[/dim]")
        return 0
        
    data = RULE_DB.get(rule_id)
    if not data:
        console.print(f"[red]❌ Unknown rule ID: {rule_id}[/red]")
        return 1
        
    content = f"""
**Severity:** {data['severity']}

### Description
{data['description']}

### Rationale
{data['rationale']}

### Remediation
{data['remediation']}
    """
    
    console.print(Panel(
        Markdown(content),
        title=f"[bold magenta]📜 Rule: {data['name']} ({rule_id})[/bold magenta]",
        border_style="magenta"
    ))
    
    return 0
