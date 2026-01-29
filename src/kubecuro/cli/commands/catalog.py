"""
CATALOG COMMAND
---------------
Manages Kubernetes schema definitions.
"""
import sys
from kubecuro.core.catalog_manager import CatalogManager
from kubecuro.core.context import HealContext
from kubecuro.cli.commands.base import get_console

def handle_catalog_command(args, target_cluster_version):
    """
    Handles 'catalog' subcommand execution.
    """
    console = get_console()
    catalog_mgr = CatalogManager()
    
    if args.action == "list":
        versions = catalog_mgr.list_installed_versions()
        if versions:
            console.print(f"[bold]Installed Catalogs:[/bold]")
            for v in versions:
                console.print(f"  • {v}")
        else:
            console.print("[yellow]No local catalogs installed. Using bundled defaults.[/yellow]")
            
    elif args.action == "update":
        # Default to target version or latest stable
        target_v = target_cluster_version or "v1.31"
        console.print(f"Fetching catalog for [cyan]{target_v}[/cyan]...")
        if catalog_mgr.fetch_catalog(target_v):
            console.print(f"[bold green]Successfully updated catalog for {target_v}[/bold green]")
        else:
            console.print(f"[bold red]Failed to update catalog for {target_v}[/bold red]")
            sys.exit(1)
            
    elif args.action == "status":
            # Show what would be used
            target_v = target_cluster_version or "v1.31"
            # Fallback path is usually relative to bundle
            resolved = catalog_mgr.resolve_catalog(target_v, fallback_path=getattr(args, 'catalog', None))
            source = "Local Cache" if ".akeso" in resolved else "Bundled/Fallback"
            console.print(f"Target Version: [green]{target_v}[/green]")
            console.print(f"Resolved Path:  [dim]{resolved}[/dim]")
            console.print(f"Source:         [bold cyan]{source}[/bold cyan]")
            
    return 0
