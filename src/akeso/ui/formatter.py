#!/usr/bin/env python3
"""
AKESO FORMATTER - The Visual Heart 
----------------------------------
Renders high-fidelity surgical reports using 'rich'. 
Supports multi-doc expansion, staged audit logs, and unified diffs.

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-26
"""

import difflib
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

console = Console()


class AkesoFormatter:
    """
    Renders surgical reports with multi-doc awareness and staged log hierarchy.
    
    Now supports summary-only mode for batch operations at scale.
    """

    def __init__(self):
        """Initialize formatter with no configuration needed."""
        pass

    # -------------------------------------------------------------------------
    # Unified Report Display
    # -------------------------------------------------------------------------

    def display_report(self, result: Dict[str, Any], verbose: bool = False):
        """
        Renders the full surgical details for a single file.
        
        Args:
            result: Result dict from engine.audit_and_heal_file()
            verbose: If True, shows the full 'Stage X' audit trail.
        """
        status = result.get("status", "UNKNOWN")
        file_path = result.get("file_path", "Unknown")
        
        # Handle errors early
        if status in ["ENGINE_ERROR", "FILE_NOT_FOUND", "SECURITY_ERROR", "EMPTY_FILE"]:
            self.display_error(
                file_path,
                result.get("error", "Unknown error"),
                status
            )
            return

        # Main Panel Component for the File
        score = result.get("health_score", 0)
        color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        
        # Header Info
        identities = result.get("identities", [])
        resources_str = ""
        if identities:
            resources_list = []
            for identity in identities:
                kind = identity.get("kind", "Unknown")
                name = identity.get("name", "unnamed")
                resources_list.append(f"{kind}/{name}")
            resources_str = ", ".join(resources_list)
        else:
            resources_str = "[dim]No resources[/dim]"

        # Create Title Panel
        console.print(Panel(
            f"[bold]Resources:[/bold] {resources_str}\n"
            f"[bold]Health Score:[/bold] [{color}]{score}/100[/{color}]\n"
            f"[bold]Status:[/bold] {status}",
            title=f"[bold {color}]Reference: {file_path}[/bold {color}]",
            border_style=color,
            expand=True # Expanded for better layout
        ))

        logs = result.get("logic_logs", [])

        # NEW: Issues Summary Table (Always visible if there are issues)
        self._render_issues_summary(logs, status)

        # OLD: Audit Tree (Visible ONLY if verbose)
        if verbose:
            if logs:
                self._render_staged_logs(logs, file_path)
        
        # =====================================================================
        # DEPRECATION WARNINGS (OSS Feature)
        # =====================================================================
        for identity in identities:
            dep = identity.get("deprecation_info")
            if dep:
                console.print(Panel(
                    f"[bold yellow]⚠️  DEPRECATED API DETECTED[/bold yellow]\n\n"
                    f"[bold]Resource:[/bold] {identity.get('kind')}/{identity.get('name', 'unnamed')}\n"
                    f"[bold]Current API:[/bold] {dep.deprecated_api}\n"
                    f"[bold]Replacement:[/bold] {dep.replacement_api}\n"
                    f"[bold]Removed in K8s:[/bold] {dep.removed_in_version}\n\n"
                    f"[dim]{dep.migration_notes}[/dim]",
                    title="[yellow]Deprecation Warning[/yellow]",
                    border_style="yellow",
                    padding=(1, 2)
                ))

    def _render_issues_summary(self, logs: List[str], status: str):
        """Renders a clean table of Warnings and Errors found in the logs."""
        issues = []
        for log in logs:
            severity = None
            rule = "General"
            msg = log
            
            if "Ghost Service detected" in log:
                severity = "WARNING"
                rule = "GhostService"
                
                # Extract core message and hint
                # Expected format from pipeline: "Ghost Service detected: ... \n  Hint: ..."
                parts = log.split("Hint:")
                core_msg = parts[0]
                hint = parts[1].strip() if len(parts) > 1 else ""
                
                # Clean up core message
                if "Ghost Service detected:" in core_msg:
                    core_msg = core_msg.split("Ghost Service detected:")[1]
                
                # Remove tree characters
                core_msg = core_msg.replace("Stage 3.5: Semantic Warnings (1):", "").replace("└─", "").replace("•", "").strip()
                
                msg = f"Ghost Service detected: {core_msg}"
                if hint:
                    msg += f"\n[dim italic]Hint: {hint}[/dim italic]"
            
            elif "Warning" in log or "WARNING" in log:
                 # Check if it is a real issue or just a header
                 if "Semantic Warnings" in log: continue
                 # Filter internal layout warnings
                 if "Stage 2" in log or "layout preservation" in log.lower(): continue
                 
                 severity = "WARNING"
                 if "Deprecation" in log: rule = "DeprecatedAPI"
                 msg = log.replace("[WARNING]", "").replace("Warning -", "").strip()

            elif "Error" in log or "CRITICAL" in log:
                 severity = "ERROR"
                 msg = log.replace("[ERROR]", "").replace("Error -", "").strip()

            if severity:
                # Deduplicate simplistic way
                if not any(i['msg'] == msg for i in issues):
                    issues.append({"severity": severity, "rule": rule, "msg": msg})

        if not issues:
            return

        table = Table(title="[bold red]ISSUES FOUND[/bold red]", show_header=True, header_style="bold white", expand=True, box=None)
        table.add_column("Severity", width=10)
        table.add_column("Rule", width=20)
        table.add_column("Message")

        for i in issues:
            sev_style = "bold red" if i["severity"] == "ERROR" else "bold yellow"
            icon = "❌" if i["severity"] == "ERROR" else "⚠️"
            table.add_row(
                f"[{sev_style}]{icon} {i['severity']}[/{sev_style}]",
                f"[cyan]{i['rule']}[/cyan]",
                i["msg"]
            )
        
        console.print(table)
        console.print()

        # Recommendation Hint
        invoked_as = "akeso"
        try:
            from akeso.core.bridge import AkesoBridge
            invoked_as = AkesoBridge.get_invoked_command()
        except:
             pass

        if any(i["rule"] == "GhostService" for i in issues):
             # Context-Aware Suggestions
             if status == "PREVIEW":
                 # If we are in preview/scan and changes are possible -> Suggest Heal
                 console.print(Panel(
                     f"Run [white]{invoked_as} heal <file>[/white] to automatically fix detected issues.",
                     title="💡 SUGGESTION",
                     border_style="green",
                     expand=False
                 ))
             elif status in ["HEALED", "UNCHANGED", "WARN"]:
                 # If we already healed (or can't heal) -> Suggest Manual Action
                 console.print(Panel(
                     "Automated healing complete. Remaining issues require [bold]manual intervention[/bold].\n"
                     "Check valid labels and ensure referenced deployments exist.",
                     title="📝 MANUAL CHECK REQUIRED",
                     border_style="yellow",
                     expand=False
                 ))
        console.print()

    def _render_staged_logs(self, logs: List[str], file_path: Optional[str] = None):
        """Groups logs by 'Stage X:' prefixes with visual hierarchy."""
        tree = Tree(f"[bold cyan]📋 Audit Trail{f': {file_path}' if file_path else ''}[/bold cyan]")
        current_branch = None

        for log in logs:
            if log.startswith("Stage "):
                current_branch = tree.add(f"[bold magenta]{log}[/bold magenta]")
            elif "Warning" in log or "WARNING" in log:
                target = current_branch if current_branch else tree
                target.add(f"[bold yellow]⚠️  {log}[/bold yellow]")
            elif "Error" in log or "CRITICAL" in log or "Failed" in log:
                target = current_branch if current_branch else tree
                target.add(f"[bold red]❌ {log}[/bold red]")
            elif "Shield" in log or "Action:" in log:
                target = current_branch if current_branch else tree
                target.add(f"[cyan]🛡️  {log}[/cyan]")
            elif "Passed" in log or "completed" in log:
                target = current_branch if current_branch else tree
                target.add(f"[green]✅ {log}[/green]")
            else:
                target = current_branch if current_branch else tree
                target.add(f"[dim]└─ {log}[/dim]")

        console.print(tree)
        console.print()

    # -------------------------------------------------------------------------
    # Multi-Doc Expanded Summary Table
    # -------------------------------------------------------------------------

    def print_final_table(self, reports: List[Dict[str, Any]], summary_only: bool = False):
        """
        Summary table with multi-resource expansion.
        
        Args:
            reports: List of file processing results
            summary_only: If True, show aggregate stats only (recommended for 100+ files)
        """
        if not reports:
            console.print("[dim yellow]No files processed.[/dim yellow]")
            return

        # FIX: For large batches, use summary mode
        if summary_only or len(reports) > 100:
            console.print(f"\n[dim]Processing {len(reports)} files - using summary mode[/dim]\n")
            self._print_summary_stats(reports)
            return

        # Standard detailed table for smaller batches
        self._print_detailed_table(reports)

    def _print_detailed_table(self, reports: List[Dict[str, Any]]):
        """Renders detailed table with per-file and per-resource rows."""
        table = Table(
            title="\n[bold magenta]━━━ Akeso Healing Summary ━━━[/bold magenta]",
            show_header=True,
            header_style="bold white on magenta",
            show_lines=True,
            padding=(0, 1)
        )

        table.add_column("File / Resource", style="cyan", no_wrap=False)
        table.add_column("Kind/Name", justify="left")
        table.add_column("Score", justify="center", width=8)
        table.add_column("Time", justify="right", width=8)
        table.add_column("Status", justify="center", width=12)
        table.add_column("✓", justify="center", width=3)

        total_files = len(reports)
        successful = 0
        healed = 0
        unchanged = 0
        warnings = 0
        failed = 0

        for r in reports:
            status = r.get("status", "UNKNOWN")
            success = r.get("success", False)
            logs = r.get("logic_logs", [])
            
            # Smart Status Detection: Check for semantic warnings even if file is unchanged
            has_warnings = any("Warning" in log or "WARN" in log for log in logs)
            if status == "UNCHANGED" and has_warnings:
                status = "WARN"
            score = r.get("health_score", 0)
            proc_time = r.get("processing_time_seconds", 0)
            file_path = r.get("file_path", "Unknown")

            # Handle errors
            if status in ["ENGINE_ERROR", "FILE_NOT_FOUND", "SECURITY_ERROR"]:
                failed += 1
                table.add_row(
                    file_path,
                    f"[red]{status}[/red]",
                    "[red]0[/red]",
                    "-",
                    "[bold red]ERROR[/bold red]",
                    "❌"
                )
                continue

            # Handle empty identities gracefully
            identities = r.get("identities", [])
            if not identities:
                # Show file-level row with clear message
                score_style = "yellow"
                status_style = "yellow" if status == "HEALED" else "dim yellow"
                result_icon = "⚠️"
                
                table.add_row(
                    file_path,
                    "[yellow]⚠ No K8s resources detected[/yellow]",
                    f"[{score_style}]{score}[/{score_style}]",
                    f"{proc_time:.2f}s",
                    f"[{status_style}]{status}[/{status_style}]",
                    result_icon
                )
                
                if status == "HEALED":
                    healed += 1
                elif status == "WARN":
                    warnings += 1
                elif status == "UNCHANGED":
                    unchanged += 1
                
                if success:
                    successful += 1
                
                continue

            # Expand resources for files with identities
            is_first_row = True
            for identity in identities:
                kind = identity.get("kind", "Unknown")
                name = identity.get("name", "unnamed")
                
                score_style = "green" if score >= 80 else "yellow" if score >= 50 else "red"
                
                if status == "HEALED":
                    status_style = "bold green"
                    if is_first_row: healed += 1
                elif status == "WARN":
                    status_style = "bold yellow"
                    if is_first_row: warnings += 1
                elif status == "UNCHANGED":
                    status_style = "dim green"
                    if is_first_row: unchanged += 1
                elif status == "PREVIEW":
                    status_style = "yellow"
                else:
                    status_style = "dim"
                
                result_icon = "✅" if success else "❌"
                
                table.add_row(
                    file_path if is_first_row else "",
                    f"{kind}: [dim]{name}[/dim]",
                    f"[{score_style}]{score}[/{score_style}]",
                    f"{proc_time:.2f}s" if is_first_row else "",
                    f"[{status_style}]{status}[/{status_style}]" if is_first_row else "",
                    result_icon if is_first_row else ""
                )
                is_first_row = False

            if success:
                successful += 1

        console.print(table)

        # Summary stats
        console.print(f"\n[bold]Akeso Engine Summary:[/bold]")
        console.print(f"  Total: {total_files} | "
                     f"[green]✓ {successful}[/green] | "
                     f"[cyan]→ {healed}[/cyan] | "
                     f"[yellow]⚠ {warnings}[/yellow] | "
                     f"[dim]○ {unchanged}[/dim] | "
                     f"[red]✗ {failed}[/red]")
        console.print(f"\n[dim]💾 Backups: *.akeso.backup[/dim]\n")

    def _print_summary_stats(self, reports: List[Dict[str, Any]]):
        """
        FIX: Compact summary mode for large batches (100+ files).
        
        Shows aggregate statistics without per-file details.
        Recommended for CI/CD pipelines and batch operations.
        """
        # Aggregate stats
        total_files = len(reports)
        by_status = {}
        by_kind = {}
        successful = 0
        failed = 0
        total_resources = 0
        total_time = 0.0
        avg_score = 0
        
        for r in reports:
            status = r.get("status", "UNKNOWN")
            logs = r.get("logic_logs", [])
            
            # Smart Status Detection for Summary
            has_warnings = any("Warning" in log or "WARN" in log for log in logs)
            if status == "UNCHANGED" and has_warnings:
                status = "WARN"
                
            by_status[status] = by_status.get(status, 0) + 1
            
            if r.get("success", False):
                successful += 1
            
            if status in ["ENGINE_ERROR", "FILE_NOT_FOUND", "SECURITY_ERROR"]:
                failed += 1
            
            total_time += r.get("processing_time_seconds", 0)
            avg_score += r.get("health_score", 0)
            
            # Count resources by kind
            for identity in r.get("identities", []):
                kind = identity.get("kind", "Unknown")
                by_kind[kind] = by_kind.get(kind, 0) + 1
                total_resources += 1
        
        avg_score = avg_score / total_files if total_files > 0 else 0
        avg_time = total_time / total_files if total_files > 0 else 0
        
        # Build summary panel
        summary_text = (
            f"[bold cyan]Files Processed:[/bold cyan] {total_files}\n"
            f"[bold cyan]Resources Found:[/bold cyan] {total_resources}\n"
            f"[bold cyan]Average Health Score:[/bold cyan] {avg_score:.1f}/100\n"
            f"[bold cyan]Average Processing Time:[/bold cyan] {avg_time:.2f}s\n\n"
            
            f"[bold]Status Breakdown:[/bold]\n"
            f"  [green]✓ Successful:[/green] {successful}\n"
            f"  [cyan]→ Healed:[/cyan] {by_status.get('HEALED', 0)}\n"
            f"  [yellow]⚠ Warning:[/yellow] {by_status.get('WARN', 0)}\n"
            f"  [dim]○ Unchanged:[/dim] {by_status.get('UNCHANGED', 0)}\n"
            f"  [yellow]⚠ Preview:[/yellow] {by_status.get('PREVIEW', 0)}\n"
            f"  [red]✗ Failed:[/red] {failed}\n"
        )
        
        # Add resource type breakdown if any found
        if by_kind:
            summary_text += f"\n[bold]Resource Types:[/bold]\n"
            # Sort by count descending
            sorted_kinds = sorted(by_kind.items(), key=lambda x: x[1], reverse=True)
            for kind, count in sorted_kinds[:10]:  # Top 10 kinds
                summary_text += f"  {kind}: {count}\n"
            if len(sorted_kinds) > 10:
                summary_text += f"  [dim]... and {len(sorted_kinds) - 10} more types[/dim]\n"
        
        console.print(Panel(
            summary_text,
            title="[bold magenta]━━━ Akeso Batch Summary ━━━[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        ))
        
        console.print(f"\n[dim]💾 Backups: *.akeso.backup[/dim]")
        console.print(f"[dim]💡 Tip: Use detailed mode for < 100 files[/dim]\n")

    def display_error(self, file_path: str, error_msg: str, status: str = "ERROR"):
        """Displays a formatted error panel."""
        panel = Panel(
            f"[red]{error_msg}[/red]",
            title=f"[bold red]❌ {status}: {file_path}[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(panel)
