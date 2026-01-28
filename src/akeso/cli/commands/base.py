"""
CLI SHARED UTILITIES
--------------------
Common logic used across multiple CLI commands.
"""

import sys
import platform
import logging
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from akeso.core.bridge import AkesoBridge, ProStatus
from akeso.core.context import HealContext

# Global UI Controller
console = Console()
formatter = None # Lazy loaded to avoid circular imports if needed

# Constants
CORE_VERSION = "0.1.0-stable"
CATALOG_VERSION = "k8s-01.32-distilled"

def get_console():
    return console

def add_standard_flags(sub):
    """Helper to inject path arguments and search filters into sub-parsers."""
    sub.add_argument("--kube-version", type=str, default=None, metavar="VERSION", dest="kube_version", help="Target K8s version (e.g., 1.28, v1.31)")
    sub.add_argument("path", nargs="*", metavar="TARGET", help="File(s) or directory(s) to process")
    sub.add_argument("--max-depth", type=int, default=10)
    sub.add_argument("--ext", default=".yaml,.yml")
    sub.add_argument("-h", "--help", action="store_true")
    sub.add_argument("-s", "--summary-only", action="store_true",
                    help="Show aggregate stats (recommended for 100+ files)")
    sub.add_argument("--verbose", action="store_true", help="Show full audit logs and stages")

def validate_required_arg(value, arg_name: str, context: str, examples: list):
    """
    Validates that a required argument is present. 
    If missing, prints a Smart Error Panel and returns False.
    """
    if value:
        return True
        
    from rich.align import Align
    
    error_msg = f"[bold red]❌ Missing Required Argument: {arg_name}[/bold red]\n\n"
    error_msg += f"The [bold]{context}[/bold] command requires a specific target.\n"
    
    if examples:
         error_msg += f"\n[dim italic]Try:[/dim italic]\n"
         for ex in examples:
             error_msg += f"  [cyan]{ex}[/cyan]\n"

    console.print(Panel(
        Align.center(error_msg),
        border_style="red",
        title="[bold yellow]Input Error[/bold yellow]",
        padding=(0, 2),
        expand=False
    ))
    return False

def normalize_paths(raw_paths):
    """
    Flattens a list of paths that might contain split commas.
    Example: ["f1,f2", "f3"] -> ["f1", "f2", "f3"]
    """
    if not raw_paths:
        return []
        
    normalized = []
    for p in raw_paths:
        for sub in p.split(","):
            clean = sub.strip()
            if clean:
                normalized.append(clean)
    return normalized

def print_custom_header(invoked_as: str, is_pro: bool):
    """
    Displays the top-level application banner.
    """
    console.print("")
    if invoked_as == "kubecuro":
        title = "💎 Kubecuro Enterprise"
        subtitle = "Logic Diagnostics & YAML Auto-Healer"
        border = "magenta"
        if not is_pro:
            subtitle += " (via Akeso OSS Foundation)"
    else:
        # Use simple shield (U+1F6E1) without variation selectors for consistent width
        title = "🛡 Akeso OSS"
        subtitle = "High-Fidelity Kubernetes Manifest Healing"
        border = "cyan"

    from rich import box
    from rich.text import Text
    
    # Create Text objects to get proper cell width
    title_text = Text(title)
    subtitle_text = Text(subtitle)
    
    # Get visual cell widths
    title_width = title_text.cell_len
    subtitle_width = subtitle_text.cell_len
    
    # Calculate padding needed to center title over the longer subtitle
    if subtitle_width > title_width:
        total_padding = subtitle_width - title_width
        pad_left = total_padding // 2
        pad_right = total_padding - pad_left
        
        # Add spaces to center the title and force exact width match
        title_centered = (" " * pad_left) + title + (" " * pad_right)
    else:
        title_centered = title
    
    banner_content = (
        f"[bold]{title_centered}[/bold]\n"
        f"[dim italic]{subtitle}[/dim italic]"
    )
    
    console.print(Panel(
        banner_content, 
        border_style=border, 
        box=box.ROUNDED,
        padding=(0, 2),
        expand=False
    ))

def print_version(invoked_as: str, is_pro: bool, cluster_version: str = None):
    """
    Displays system information panel.
    """
    tier = "Enterprise" if invoked_as == "kubecuro" else "OSS"
    border_color = "magenta" if invoked_as == "kubecuro" else "cyan"
    
    sys_platform = f"{platform.system()} {platform.release()}"
    sys_arch = platform.machine()
    runtime_env = f"Python {platform.python_version()}"
    
    if not cluster_version:
        cluster_version = HealContext._get_default_cluster_version()
    
    info_table = Table(box=None, show_header=False, padding=(0, 1))
    info_table.add_column(width=18, justify="left")
    info_table.add_column(justify="left")
    
    info_table.add_row("Client Version:", f"[bold white]{CORE_VERSION}[/bold white]")
    info_table.add_row("Identity:", f"[bold {border_color}]{invoked_as.upper()}[/bold {border_color}] ({tier})")
    
    if is_pro:
        badge, license_msg, color = AkesoBridge.get_pro_status_display()
        info_table.add_row("License Status:", f"[{color}]{badge}[/{color}]")
        info_table.add_row("", f"[dim]{license_msg}[/dim]")
        
        try:
            from akeso.pro import license as pro_license
            trial_status = pro_license.get_trial_status_display()
            if "Trial" in trial_status:
                console.print("\n[bold]Trial Usage:[/bold]")
                console.print(trial_status)
        except Exception:
            pass
    else:
        info_table.add_row("License Status:", "[dim]Community/Unlicensed[/dim]")
    
    info_table.add_row("Catalog Schema:", f"[yellow]{CATALOG_VERSION}[/yellow]")
    info_table.add_row("Target K8s:", f"[green]{cluster_version}[/green]")
    info_table.add_row("Platform:", f"{sys_platform} ({sys_arch})")
    info_table.add_row("Runtime:", f"{runtime_env}")
    
    tip_table = Table(box=None, show_header=False, padding=(1, 1, 0, 1))
    tip_table.add_column()
    
    if not is_pro:
        tip_text = "[bold]💡 Kubecuro Enterprise supports auto-detection from kubectl[/bold]"
    else:
        tip_text = "[dim]✨ Pro: Auto-detect cluster versions from kubectl/API[/dim]"
    
    tip_table.add_row(tip_text)

    panel_group = Group(info_table, tip_table)

    console.print(Panel.fit(
        panel_group, 
        title=f"[bold]Operational Context[/bold]", 
        border_style=border_color,
        padding=(0, 2)
    ))
