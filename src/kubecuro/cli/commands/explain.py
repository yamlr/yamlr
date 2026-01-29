
from rich.panel import Panel
from rich.markdown import Markdown

# This would ideally load from the Analyzer Registry dynamic metadata
# For MVP, we use a static lookup to demonstrate the UI
RULE_DB = {
    "rules/no-latest-tag": {
        "name": "Avoid Latest Tag",
        "severity": "Warning",
        "description": "Container images should use specific version tags instead of 'latest'.",
        "rationale": """
        Using `latest` makes deployments non-deterministic. A new version of the image could break your application 
        without any change to the manifest. Rollbacks become impossible because `latest` is a moving target.
        """,
        "remediation": "Pin the image to a specific SHA digest or version tag (e.g., `nginx:1.25.3`)."
    },
    "rules/resource-limits": {
        "name": "Resource Limits Missing",
        "severity": "Warning",
        "description": "Containers should define resource requests and limits.",
        "rationale": """
        Without limits, a single container can consume all node resources (CPU/Memory), causing a Denial of Service 
        for other pods. Without requests, the scheduler cannot make intelligent placement decisions.
        """,
        "remediation": "Add a `resources` block with `requests` and `limits` for cpu and memory."
    },
    "rules/run-as-root": {
        "name": "Container Runs as Root",
        "severity": "High",
        "description": "Containers should run as a non-root user.",
        "rationale": """
        Running processes as root increases the attack surface. If the container is compromised, the attacker 
        has root privileges inside the container, which facilitates container escape attacks.
        """,
        "remediation": "Set `securityContext.runAsNonRoot: true` and specify a `runAsUser` ID > 1000."
    }
}

def handle_explain_command(args, console):
    """
    Explains a specific rule or lists available rules.
    """
    rule_id = args.rule_id
    
    if not rule_id:
        console.print("[bold cyan]Available Rules:[/bold cyan]")
        for rid, data in RULE_DB.items():
            console.print(f" - [bold]{rid}[/bold]: {data['name']}")
        console.print("\n[dim]Usage: akeso explain <rule_id>[/dim]")
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
