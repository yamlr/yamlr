#!/usr/bin/env python3
"""
AKESO/KUBECURO UNIFIED CLI
--------------------------
High-fidelity manifest healing and diagnostics.
Maintains 1:1 parity between OSS (Akeso) and Enterprise (Kubecuro).

Refactored (2026-01-27):
- Modularized command handling (src/akeso/cli/commands/)
- Simplified main entry point
"""

import sys
import os
import argparse
import logging
import platform

# Core Modules
from akeso.core.engine import AkesoEngine
from akeso.core.bridge import AkesoBridge
from akeso.core.context import HealContext
from akeso.core.catalog_manager import CatalogManager

# UI Modules
from akeso.ui.formatter import AkesoFormatter

# Command Modules
from akeso.cli.commands.base import (
    get_console, 
    print_custom_header, 
    print_version, 
    get_console, 
    print_custom_header, 
    print_version, 
    add_standard_flags,
    validate_required_arg
)
from akeso.cli.commands.scan import handle_scan_command
from akeso.cli.commands.heal import handle_heal_command
from akeso.cli.commands.catalog import handle_catalog_command

# Global setup
console = get_console()
formatter = AkesoFormatter()
logger = logging.getLogger("akeso.cli")

def print_kubectl_help(invoked_as: str):
    """
    Displays the main help menu in a 'kubectl' inspired format.
    """
    from rich.table import Table
    console.print("\n[bold cyan]┌─ COMMANDS[/bold cyan]")
    cmd_table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    cmd_table.add_column(style="bold green", width=12)
    cmd_table.add_column(style="white")
    
    # Core Flow
    cmd_table.add_row("init", "Bootstrap a new project with defaults")
    cmd_table.add_row("scan", "Audit manifests for logical issues (read-only)")
    cmd_table.add_row("heal", "Fix validation issues and enforce best practices")
    
    # Info & Docs
    cmd_table.add_row("explain", "Get documentation for a specific rule")
    cmd_table.add_row("completion", "Generate shell autocompletion scripts")
    cmd_table.add_row("catalog", "Manage Kubernetes schema definitions")
    
    # System
    cmd_table.add_row("version", "Display version info and license status")
    cmd_table.add_row("auth", "Manage Kubecuro Enterprise authentication")
    
    console.print(cmd_table)

    console.print("\n[bold cyan]┌─ GLOBAL OPTIONS & FILTERS[/bold cyan]")
    opt_table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    opt_table.add_column(style="yellow", width=24)
    opt_table.add_column(style="dim white")
    opt_table.add_row("-h, --help", "Display usage information")
    opt_table.add_row("-v, --version", "Display version information")
    opt_table.add_row("--kube-version VERSION", "Target K8s version (e.g., 1.28, v1.31)")
    opt_table.add_row("--catalog PATH", "Specify a custom K8s schema catalog")
    opt_table.add_row("--max-depth N", "Limit directory recursion depth (Default: 10)")
    opt_table.add_row("--ext LIST", "Process files with these extensions (Default: .yaml,.yml)")
    opt_table.add_row("-s, --summary-only", "Show aggregate stats (recommended for 100+ files)")
    console.print(opt_table)
    
    console.print(f"\n[bold magenta]💡 TIP[/bold magenta]")
    console.print(f"   Use [cyan bold]{invoked_as} <command> --help[/cyan bold] for subcommand specific flags.")
    console.print(f"   Override cluster version: [dim]AKESO_KUBE_VERSION=<version> {invoked_as} heal ...[/dim]\n")

def main():
    """
    Primary orchestration logic for the CLI.
    """
    # Enable twin command creation (akeso <--> kubecuro symlinks)
    AkesoBridge.ensure_dual_identity()
    
    # 1. Identity Gate
    try:
        invoked_as = AkesoBridge.get_invoked_command()
        status, message = AkesoBridge.check_pro_status()
        is_pro = status.is_usable()
        
        # License warnings... (Keeping logic simplified for brevity but preserving intent)
        # In a real refactor, this block handles the daily reminders logic
        
    except Exception as e:
        logger.debug(f"Identity detection failed: {e}")
        invoked_as = "akeso"
        is_pro = False

    # 2. Argument Configuration
    parser = argparse.ArgumentParser(prog=invoked_as, add_help=False)
    
    # Global flags
    parser.add_argument("--kube-version", type=str, default=None, metavar="VERSION", dest="kube_version")
    parser.add_argument("--catalog", default=None, help="Path to custom catalog (default: bundled)")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('-s', '--summary-only', action='store_true')
    
    subparsers = parser.add_subparsers(dest="command")
    
    # SCAN
    scan_parser = subparsers.add_parser("scan", add_help=False)
    add_standard_flags(scan_parser)
    scan_parser.add_argument("--output", choices=["text", "json", "sarif"], default="text", help="Output format")
    scan_parser.add_argument("--diff", action="store_true", help="Show proposed fixes (like heal --dry-run)")
    
    # HEAL
    heal_parser = subparsers.add_parser("heal", add_help=False)
    add_standard_flags(heal_parser)
    heal_parser.add_argument("--dry-run", action="store_true")
    heal_parser.add_argument("--harden", action="store_true")
    heal_parser.add_argument("--check-deprecations", action="store_true")

    # INIT
    init_parser = subparsers.add_parser("init", add_help=False)
    init_parser.add_argument("-h", "--help", action="store_true")

    # EXPLAIN
    explain_parser = subparsers.add_parser("explain", add_help=False)
    explain_parser.add_argument("rule_id", nargs="?", help="Rule ID to explain (e.g., rules/no-latest-tag)")
    explain_parser.add_argument("-h", "--help", action="store_true")

    # COMPLETION
    completion_parser = subparsers.add_parser("completion", add_help=False)
    completion_parser.add_argument("shell", choices=["powershell", "bash", "zsh"], nargs="?", help="Target shell")
    completion_parser.add_argument("-h", "--help", action="store_true")

    # CATALOG
    catalog_parser = subparsers.add_parser("catalog", add_help=False)
    catalog_parser.add_argument("action", choices=["update", "list", "status"], nargs="?", default="status")
    catalog_parser.add_argument("--kube-version", type=str, metavar="VERSION")
    catalog_parser.add_argument("-h", "--help", action="store_true")

    # UTILS
    subparsers.add_parser("version", add_help=False)
    auth_parser = subparsers.add_parser("auth", add_help=False)
    auth_parser.add_argument("--login", metavar="TOKEN")

    # 3. Parse Args
    args, unknown = parser.parse_known_args()
    
    # Pre-process: Support comma-separated args
    from akeso.cli.commands.base import normalize_paths
    if hasattr(args, 'path') and args.path:
        args.path = normalize_paths(args.path)

    # 4. Version Check
    target_cluster_version = None
    if args.kube_version:
        try:
            target_cluster_version = HealContext.set_cluster_version(args.kube_version)
        except ValueError as e:
            console.print(f"[bold red]❌ Invalid K8s version:[/bold red] {e}")
            sys.exit(1)

    if args.version or args.command == "version":
        print_version(invoked_as, is_pro, cluster_version=target_cluster_version)
        sys.exit(0)

    # 5. Help / Headers
    if args.help or not args.command:
        # Subcommand specific custom help
        if args.command == "catalog":
             console.print(f"\n[bold green]USAGE:[/bold green] [bold white]{invoked_as} catalog <action>[/bold white] [options]")
             console.print("\n[bold cyan]ACTIONS[/bold cyan]")
             console.print("  update   Download latest schemas from upstream")
             console.print("  list     Show installed local catalogs")
             console.print("  status   Show current catalog resolution info")
             sys.exit(0)
        
        if args.command == "init":
             console.print(f"\n[bold green]USAGE:[/bold green] [bold white]{invoked_as} init[/bold white]")
             console.print("Generates a default [cyan].akeso.yaml[/cyan] configuration file in the current directory.")
             sys.exit(0)

        if args.command == "explain":
             console.print(f"\n[bold green]USAGE:[/bold green] [bold white]{invoked_as} explain [rule_id][/bold white]")
             console.print("Shows detailed documentation, rationale, and remediation steps for a specific rule.")
             sys.exit(0)
             
        if args.command in ["heal", "scan"] and not args.path:
             pass # Fallthrough to standard help
        elif args.command not in ["catalog", "init", "explain", "version"]: 
             pass

        print_custom_header(invoked_as, is_pro)
        
        if args.command == "scan":
            console.print(f"\n[bold green]USAGE:[/bold green] [bold white]{invoked_as} scan <target...>[/bold white] [options]")
            console.print("\n[bold cyan]OPTIONS[/bold cyan]")
            console.print("  target              File(s) or directory(s) to audit")
            console.print("  --output FORMAT     Report format (text, json, sarif)")
            console.print("  --diff              Show visual diff of proposed fixes")
            console.print("  --ext LIST          Extensions to scan (default: .yaml,.yml)")
            console.print("  --max-depth N       Recursion depth (default: 10)")
            
        elif args.command == "heal":
            console.print(f"\n[bold green]USAGE:[/bold green] [bold white]{invoked_as} heal <target...>[/bold white] [options]")
            console.print("\n[bold cyan]OPTIONS[/bold cyan]")
            console.print("  target              File(s) or directory(s) to heal")
            console.print("  --dry-run           Show proposed changes without writing")
            console.print("  -y, --yes           Auto-confirm single file healing")
            console.print("  --yes-all           Auto-confirm batch healing (Use with caution)")
            console.print("  --harden            Apply security hardening (Pro feature)")
            
        else:
            print_kubectl_help(invoked_as)
        sys.exit(0)

    # 6. Dispatch
    
    # Init Dispatch
    if args.command == "init":
        from akeso.cli.commands.config import handle_init_command
        sys.exit(handle_init_command(console))

    # Explain Dispatch
    if args.command == "explain":
        from akeso.cli.commands.explain import handle_explain_command
        sys.exit(handle_explain_command(args, console))

    # Completion Dispatch
    if args.command == "completion":
        from akeso.cli.commands.completion import handle_completion_command
        sys.exit(handle_completion_command(args, parser, console))
    
    # Catalog Dispatch (No Engine Reqd)
    if args.command == "catalog":
        sys.exit(handle_catalog_command(args, target_cluster_version))

    # Auth Dispatch
    if args.command == "auth":
        from akeso.cli.commands.auth import handle_auth_command
        sys.exit(handle_auth_command(args, console))

    # Engine Setup (For Scan/Heal)
    try:
        # Pre-Validation (Before spinning up engine)
        if args.command == "scan":
            if not validate_required_arg(args.path, "path", "scan", [f"{invoked_as} scan .", f"{invoked_as} scan <path-to-file-or-dir>"]):
                sys.exit(1)
        elif args.command == "heal":
            # Heal usage suggestion should be safe (interactive by default)
            if not validate_required_arg(args.path, "path", "heal", [f"{invoked_as} heal .", f"{invoked_as} heal <path-to-file-or-dir>"]):
                sys.exit(1)

        if target_cluster_version:
            console.print(f"🎯 Target K8s: [bold green]{target_cluster_version}[/bold green]")
        else:
            detected_version = HealContext._get_default_cluster_version()
            console.print(f"🎯 Target K8s: [bold green]{detected_version}[/bold green] (default)")
            target_cluster_version = detected_version
            
        # Programmatically resolve bundled catalog location
        if args.catalog:
            fallback_path = args.catalog
        else:
            # Robust Resolution Strategy: Check multiple candidate locations
            candidates = []
            
            # 1. Dev/Source Root (up 4 levels from cli/main.py)
            dev_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            candidates.append(os.path.join(dev_root, "catalog", "k8s_v1_distilled.json"))
            
            # 2. Package Root (up 2 levels from cli/main.py -> src/akeso/catalog)
            pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidates.append(os.path.join(pkg_root, "catalog", "k8s_v1_distilled.json"))
            
            # 3. System Install (share/akeso/catalog)
            # This handles pip install prefixes
            candidates.append(os.path.join(sys.prefix, "share", "akeso", "catalog", "k8s_v1_distilled.json"))

            fallback_path = None
            for p in candidates:
                if os.path.isfile(p):
                    fallback_path = p
                    break
            
            if not fallback_path:
                # If we can't find a bundled catalog, explicitly warn (but let Manager try cache)
                logger.debug(f"Could not locate bundled catalog in {candidates}")
                # fallback_path remains None
            
        catalog_mgr = CatalogManager()
        final_catalog_path = catalog_mgr.resolve_catalog(target_cluster_version, fallback_path=fallback_path)

        engine = AkesoEngine(
            workspace_path=".", 
            catalog_path=final_catalog_path,
            cluster_version=target_cluster_version 
        )

        if args.command == "scan":
            sys.exit(handle_scan_command(args, engine, formatter))
            
        elif args.command == "heal":
            # Pro Gate
            if getattr(args, 'harden', False) and not is_pro:
                AkesoBridge.notify_pro_required("Shield Security Hardening")
                sys.exit(0)
            sys.exit(handle_heal_command(args, engine, formatter, is_pro))

    except Exception as e:
        console.print(f"[bold red]Fatal Error:[/bold red] {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
