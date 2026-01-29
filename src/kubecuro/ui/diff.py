"""
AKESO DIFF ENGINE
-----------------
Provides rich, colorful diffs for the CLI.
Supports:
- Side-by-side comparison (ideal for batch review)
- Inline diffs (classic git style)
- Syntax highlighting via Rich

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-27
"""

import difflib
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text

console = Console()

class DiffEngine:
    """Renders colorful diffs for Kubernetes manifests."""

    @staticmethod
    def render_diff(original: str, healed: str, file_path: str, side_by_side: bool = True):
        """
        Displays a diff between the original and healed content.
        
        Args:
            original: The raw content before healing.
            healed: The content after healing.
            file_path: Name of the file being modified.
            side_by_side: If True, uses a 2-column layout. False uses unified diff.
        """
        if original == healed:
            console.print(f"[dim]No changes for {file_path}[/dim]")
            return

        # Prepare title
        title = f":wrench: Proposed Changes for [bold cyan]{file_path}[/bold cyan]"
        
        if side_by_side:
            DiffEngine._render_side_by_side(original, healed, title)
        else:
            DiffEngine._render_inline(original, healed, title)

    @staticmethod
    def _render_side_by_side(original: str, healed: str, title: str):
        """
        Renders two panels side-by-side using smart block extraction.
        Highlights changed lines with background colors.
        """
        matcher = difflib.SequenceMatcher(None, original.splitlines(), healed.splitlines())
        
        # Prepare table
        table = Table(title=title, show_header=True, header_style="bold magenta", expand=True, box=None)
        table.add_column("Original (Current)", style="on #3b0e0e", ratio=1) # Dark red bg for deletions
        table.add_column("Healed (Proposed)", style="on #0e3b0e", ratio=1)  # Dark green bg for additions

        orig_lines = original.splitlines()
        healed_lines = healed.splitlines()

        # Iterate through matched blocks
        # We want to show EQUAL blocks (context) + REPLACE/DELETE/INSERT blocks
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Show context (max 3 lines) if it's a long equal block
                # If block is small (< 6 lines), show it all.
                # If block is huge, show start...end
                
                block_len = i2 - i1
                if block_len <= 6:
                    # Show full context
                    left_text = "\n".join(orig_lines[i1:i2])
                    right_text = "\n".join(healed_lines[j1:j2])
                    
                    # No background color for equal lines
                    table.add_row(
                        Syntax(left_text, "yaml", theme="monokai", start_line=i1+1),
                        Syntax(right_text, "yaml", theme="monokai", start_line=j1+1)
                    )
                else:
                    # Context is too long, collapse it
                    # Show first 2 lines
                    left_start = "\n".join(orig_lines[i1:i1+2])
                    right_start = "\n".join(healed_lines[j1:j1+2])
                    
                    table.add_row(
                        Syntax(left_start, "yaml", theme="monokai", start_line=i1+1),
                        Syntax(right_start, "yaml", theme="monokai", start_line=j1+1)
                    )
                    
                    # Separator
                    table.add_row("[dim]... (unchanged) ...[/dim]", "[dim]... (unchanged) ...[/dim]")
                    
                    # Show last 2 lines
                    left_end = "\n".join(orig_lines[i2-2:i2])
                    right_end = "\n".join(healed_lines[j2-2:j2])
                    
                    table.add_row(
                        Syntax(left_end, "yaml", theme="monokai", start_line=i2-1),
                        Syntax(right_end, "yaml", theme="monokai", start_line=j2-1)
                    )

            elif tag in ['replace', 'delete', 'insert']:
                # Changed Block
                left_content = ""
                right_content = ""
                
                if tag != 'insert':
                    left_content = "\n".join(orig_lines[i1:i2])
                
                if tag != 'delete':
                    right_content = "\n".join(healed_lines[j1:j2])
                
                # Render with explicit styling (handled by column style, but Syntax overrides background)
                # To force background color on Syntax, we can rely on Text or just standard Styles.
                # However, Rich Syntax themes handle bg. 
                # Improving visibility by adding ">>>" markers
                
                left_panel = Panel(left_content, style="red" if left_content else "dim")
                right_panel = Panel(right_content, style="green" if right_content else "dim")
                
                # To get syntax highlighting + background is tricky without a custom theme.
                # We will stick to Syntax for clarity, but the row structure highlights matched pairs.
                
                table.add_row(
                    Syntax(left_content, "yaml", theme="monokai", background_color="#3b0e0e") if left_content else "",
                    Syntax(right_content, "yaml", theme="monokai", background_color="#0e3b0e") if right_content else ""
                )

        console.print(table)
        console.print("[dim italic]Use arrows to scroll if content is long[/dim italic]\n")

    @staticmethod
    def _render_inline(original: str, healed: str, title: str):
        """Renders a standard unified diff with colors."""
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            healed.splitlines(keepends=True),
            fromfile="Original",
            tofile="Healed",
            n=3 # Context lines
        ))
        
        # Build a Rich Text object for the diff
        diff_text = Text()
        for line in diff_lines:
             if line.startswith("---") or line.startswith("+++"):
                 diff_text.append(line, style="bold magenta")
             elif line.startswith("@@"):
                 diff_text.append(line, style="cyan")
             elif line.startswith("-"):
                 diff_text.append(line, style="red")
             elif line.startswith("+"):
                 diff_text.append(line, style="green")
             else:
                 diff_text.append(line, style="dim white")
        
        console.print(Panel(diff_text, title=title, expand=False, border_style="blue"))
