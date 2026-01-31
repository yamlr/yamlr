import re
import logging
from typing import Dict, Any, Set
from .base import BaseHeuristic

logger = logging.getLogger("yamlr.lexer.heuristics")

class MagicColonHeuristic(BaseHeuristic):
    """
    Injects missing colons in 'key value' patterns.
    Safe against English text via stopword filtering.
    """
    
    COMMON_ENGLISH_STOPWORDS: Set[str] = {
        "This", "The", "A", "An", "It", "If", "When", "Then", 
        "For", "To", "Note", "But", "And", "Or"
    }

    @property
    def name(self) -> str:
        return "magic_colon"

    @property
    def description(self) -> str:
        return "Injects missing colons (key value -> key: value)"

    def apply(self, line: str, context: Dict[str, Any]) -> str:
        # Don't touch lines that already have colons (mostly)
        # Exception: "image: nginx:latest" has colons.
        # But we look for "image nginx".
        
        # We work on the stripped code part, but we must return full line
        # This is tricky because Heuristic expects line -> line
        # We need to preserve indent.
        
        indent_len = len(line) - len(line.lstrip())
        indent_str = line[:indent_len]
        code_part = line.lstrip()
        
        if not code_part or code_part.startswith("#") or code_part.startswith("-"):
             return line

        # If colon exists in the "key" position (first word), skip
        # Logic from lexer.py
        first_colon_idx = code_part.find(":")
        
        # Regex to find "word space value"
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s+(.+)$", code_part)
        
        if match:
            key = match.group(1)
            val = match.group(2)
            
            # If the extracted key itself has a colon, we are good (e.g. "foo: bar")
            # The regex `[a-zA-Z0-9_\-\.]+` does NOT include colon. 
            # So if `key` matches, it definitively does NOT have a colon.
            
            # Additional safety: check if the line *actually* has the colon later?
            # No, if `key` matched group 1 (no colon), and `val` is group 2.
            # "image: nginx" -> key="image" (matches regex?? NO, because : is not in regex class)
            # So `image:` fails the match. `image nginx` matches.
            
            # Safety checks
            if (not key.startswith("-") and 
                not key.startswith("_") and 
                key not in self.COMMON_ENGLISH_STOPWORDS and 
                not (len(key) <= 2 and key.isupper())):
                
                new_line = f"{indent_str}{key}: {val}"
                
                if 'stats' in context:
                    context['stats']['spacing_fixes'] += 1
                    
                logger.debug(f"MagicColon: '{code_part}' -> '{key}: {val}'")
                return new_line
                
        return line

class QuoteBalancingHeuristic(BaseHeuristic):
    @property
    def name(self) -> str:
        return "quote_balancing"

    @property
    def description(self) -> str:
        return "Closes unclosed quotes"

    def apply(self, line: str, context: Dict[str, Any]) -> str:
        # Simplistic version of the complex logic in lexer.py
        # We can copy the _balance_quotes logic but we need to extract value first.
        # This is hard on a full line.
        # Heuristics might need to be applied *after* splitting key/value?
        # But the Lexer uses `repair_line` *before* semantics.
        
        # Let's target specific "key: value" lines where value is unclosed
        if ":" not in line:
            return line
            
        k, sep, v = line.partition(":")
        v_stripped = v.strip()
        
        if not v_stripped:
            return line
            
        # Quote fixing logic
        if len(v_stripped) >= 1:
            first = v_stripped[0]
            if first in ('"', "'"):
                 if not v_stripped.endswith(first):
                     # Fix it
                     # append quote to the REAL line (preserving trailing spaces?)
                     # Usually safe to rstrip and add quote
                     return line.rstrip() + first
                     
                     if 'stats' in context:
                        context['stats']['quote_repairs'] += 1

        return line

class SpacingHeuristic(BaseHeuristic):
    @property
    def name(self) -> str:
        return "spacing_fix"

    @property
    def description(self) -> str:
         return "Fixes '-item' and 'key:value' spacing"

    def apply(self, line: str, context: Dict[str, Any]) -> str:
         stripped = line.lstrip()
         indent = len(line) - len(stripped)
         indent_str = line[:indent]
         
         # 1. Dash spacing "-item" -> "- item"
         if stripped.startswith("-") and len(stripped) > 1 and not stripped[1].isspace():
             new_content = "- " + stripped[1:]
             if 'stats' in context: context['stats']['spacing_fixes'] += 1
             return indent_str + new_content
             
         # 2. Colon spacing "key:value" -> "key: value"
         if ":" in stripped:
             k, sep, v = stripped.partition(":")
             if v and not v.startswith(" ") and not v.strip() == "":
                 # Only if value exists and no space
                 # "key:value"
                 new_content = f"{k}: {v}"
                 if 'stats' in context: context['stats']['spacing_fixes'] += 1
                 return indent_str + new_content
                 
         return line
