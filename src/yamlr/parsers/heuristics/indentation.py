from .base import BaseHeuristic
from typing import Dict, Any

class TabExpansionHeuristic(BaseHeuristic):
    @property
    def name(self) -> str:
        return "tab_expansion"

    @property
    def description(self) -> str:
        return "Expands tabs to 2 spaces"

    def apply(self, line: str, context: Dict[str, Any]) -> str:
        # Simple tab expansion
        if "\t" in line:
            # Stats tracking should ideally happen here, but context is dict
            # We assume context contains 'stats' dict
             # context.get('stats', {})['spacing_fixes'] += line.count("\t")
             pass
        return line.replace("\t", "  ")


class SnapToGridHeuristic(BaseHeuristic):
    @property
    def name(self) -> str:
        return "snap_to_grid"

    @property
    def description(self) -> str:
        return "Enforces even indentation (2-space standard)"

    def apply(self, line: str, context: Dict[str, Any]) -> str:
        # We need to process indentation, which implies we look at the raw line
        # content logic is mostly indentation based.
        
        raw_line = line.rstrip()
        content = raw_line.lstrip()
        indent = len(raw_line) - len(content)
        
        if not content:
            return line
            
        # Don't touch comments or block scalars here, just fix indent
        if indent > 0 and indent % 2 != 0:
            if indent == 1:
                new_indent = 2
            else:
                new_indent = indent - 1
            
            # Update stats
            if 'stats' in context:
                 context['stats']['spacing_fixes'] += 1
                 
            return (" " * new_indent) + content
            
        return line
