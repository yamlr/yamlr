"""
HEAL COMMAND
------------
Executes manifest reconciliation and healing.
"""
import os
import sys
import json
from rich.panel import Panel
from kubecuro.core.engine import AkesoEngine
from kubecuro.core.bridge import AkesoBridge, ProStatus
from kubecuro.cli.commands.base import get_console

logger = get_console()

def handle_heal_command(args, engine, formatter, is_pro: bool):
    """
    Handles 'heal' subcommand execution.
    """
    console = get_console()
    extensions = [e.strip() for e in args.ext.split(",")]
    is_dry = getattr(args, 'dry_run', False)
    auto_yes = getattr(args, 'yes', False)
    # Support both --yes-all and fallback to --yes for batch consistency
    auto_yes_all = getattr(args, 'yes_all', False) or auto_yes # If user says yes to all, they implicitly say yes to one.

    from kubecuro.ui.diff import DiffEngine

    if not args.path:
        return 1 # Should rely on validation, but safety check

    targets = args.path
    
    # Determine execution mode
    # Use Batch Mode if: Multiple targets OR the single target is a directory
    is_batch_mode = len(targets) > 1 or (len(targets) == 1 and os.path.isdir(targets[0]))

    if not is_batch_mode:
        target_file = targets[0]
        if not os.path.exists(target_file):
            console.print(f"[red]❌ File not found: {target_file}[/red]")
            return 1

        # SINGLE FILE MODE: Interactive Diff -> Confirm -> Write
        # First, run in dry-run mode to get the proposed changes
        result = engine.audit_and_heal_file(target_file, dry_run=True)
        
        # Calculate diff if changed
        # Accessing dict keys, not attributes
        if result.get("success") and result.get("healed_content") and result.get("raw_content") != result.get("healed_content"):
             original_content = result.get("raw_content", "")
             if not original_content:
                 # Fallback to reading disk if raw_content missing
                 try:
                    with open(target_file, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                 except: pass
             
             healed_content = result.get("healed_content", "")
             
             # Show Diff
             if not getattr(args, 'quiet', False):
                 DiffEngine.render_diff(original_content, healed_content, target_file)
             
             if is_dry:
                 console.print("[dim yellow]Dry-run: No changes written.[/dim yellow]")
                 formatter.display_report(result)
                 # Return 1 to indicate "Diff Found" (Success code 0 implies no changes needed)
                 return 1
                 
             if not auto_yes:
                 # Interactive Prompt
                 confirm = console.input(f"\n[bold yellow]Apply changes to {target_file}? (y/n) [n]: [/bold yellow]")
                 if confirm.lower() != 'y':
                     console.print("[red]Aborted.[/red]")
                     return 0
            
             # Actually Write
             final_result = engine.audit_and_heal_file(target_file, dry_run=False)
             formatter.display_report(final_result)
             job_results = [final_result]

        else:
             # No changes needed
             console.print(f"[green]No changes required for {target_file}[/green]")
             job_results = [result]

    else:
        # BATCH MODE: Scan -> Summary -> Diffs -> "CONFIRM" -> Write
        console.print(f"[bold cyan]Scanning {len(targets)} targets...[/bold cyan]")
        
        # 1. First Pass: Dry Run
        job_results = []
        for target in targets:
            if os.path.isfile(target):
                job_results.append(engine.audit_and_heal_file(target, dry_run=True))
            elif os.path.isdir(target):
                job_results.extend(engine.batch_heal(
                    root_path=target, 
                    extensions=extensions, 
                    max_depth=args.max_depth,
                    dry_run=True
                ))
            else:
                console.print(f"[yellow]Skipping invalid target: {target}[/yellow]")
        
        # Filter for actual changes. 
        # Check logic: raw != healed AND success
        changed_jobs = [
            j for j in job_results 
            if j.get("healed_content") and j.get("raw_content") != j.get("healed_content")
        ]
        
        if not changed_jobs:
            console.print("[green]All files are healthy! No changes needed.[/green]")
            return 0
            
        formatter.print_final_table(job_results, summary_only=True)
        
        if is_dry:
            console.print(f"\n[bold yellow]Dry Run Complete. Found {len(changed_jobs)} files to heal.[/bold yellow]")
            
            # Batch Throttling Strategy
            THRESHOLD = 5
            show_diffs = True
            
            if len(changed_jobs) > THRESHOLD and not auto_yes_all:
                console.print(f"\n[bold]Summary of Changes:[/bold]")
                for job in changed_jobs:
                    # Determine change type hint
                    hint = "Modified"
                    if "Ghost Service" in str(job.get("logic_logs", [])): hint = "Ghost Fix"
                    console.print(f"  • {job.get('file_path')} [dim]({hint})[/dim]")
                
                # Ask user if they want to see the wall of text
                view_diffs = console.input(f"\n[bold cyan]View detailed diffs for all {len(changed_jobs)} files? [y/N] (Default: No): [/bold cyan]")
                if view_diffs.lower() != 'y':
                    show_diffs = False
                    console.print("[dim]Skipping detailed diffs.[/dim]")

            if show_diffs:
                 for job in changed_jobs:
                      DiffEngine.render_diff(
                          job.get("raw_content", ""), 
                          job.get("healed_content", ""), 
                          job.get("file_path", "Unknown")
                      )
            
            # Return 1 to indicate "Diff Found"
            return 1

        # Safety Interlock
        if not auto_yes_all:
             console.print(f"\n[bold red]WARNING: You are about to modify {len(changed_jobs)} files.[/bold red]")
             console.print("To verify, run with --dry-run. To approve, type 'CONFIRM'.")
             
             confirm = console.input("[bold red]Type 'CONFIRM' to proceed: [/bold red]")
             if confirm != "CONFIRM":
                 console.print("[red]Operation cancelled.[/red]")
                 return 0
        
        # 2. Second Pass: Actual Write
        console.print("[green]Applying repairs...[/green]")
        
        final_results = []
        for target in targets:
            if os.path.isfile(target):
                final_results.append(engine.audit_and_heal_file(target, dry_run=False))
            elif os.path.isdir(target):
                 final_results.extend(engine.batch_heal(
                    root_path=target, 
                    extensions=extensions, 
                    max_depth=args.max_depth,
                    dry_run=False
                 ))
        
        # Check for genuine errors
        failures = [j for j in final_results if j.get("status") in ["ENGINE_ERROR", "SECURITY_ERROR"]]
        if failures:
            console.print(f"[bold red]Failed to heal {len(failures)} files.[/bold red]")
            return 1
            
        console.print(f"[bold green]Successfully healed {len(changed_jobs)} files.[/bold green]")
        
    return 0

def _check_trial_usage(is_pro: bool, console):
    """Checks and displays trial usage warnings."""
    if not is_pro: return
    try:
        from kubecuro.pro import license as pro_license
        status, msg = AkesoBridge.check_pro_status()
        
        if status == ProStatus.TRIAL_ACTIVE:
            summary = pro_license.get_usage_summary()
            
            high_usage_features = []
            for feature, data in summary.items():
                if data["percentage"] >= 80:
                    feature_name = feature.replace("_", " ").title()
                    high_usage_features.append(
                        f"{feature_name}: {data['used']}/{data['limit']} ({data['percentage']}%)"
                    )
            
            if high_usage_features:
                console.print(f"\n[yellow]⚠️  Trial Usage Alert:[/yellow]")
                for feat in high_usage_features:
                    console.print(f"  {feat}")
            
            if any(d["percentage"] >= 100 for d in summary.values()):
                console.print("\n")
                console.print(Panel(
                    "[bold yellow]🎉 Trial Limit Reached![/bold yellow]\n\n"
                    "You've successfully used Kubecuro Pro.\n\n"
                    "Upgrade now for unlimited features:\n"
                    "  • [cyan]https://kubecuro.dev/upgrade[/cyan]\n"
                    "  • Special: 20% off with code TRIAL20\n\n"
                    "[dim]Akeso OSS features remain unlimited.[/dim]",
                    border_style="yellow",
                    expand=False
                ))
    except Exception:
        pass
