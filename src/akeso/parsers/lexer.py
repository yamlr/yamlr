#!/usr/bin/env python3
"""
AKESO SEMANTIC LEXER (Foundation for Kubecuro)
----------------------------------------------
The core sharding engine for Akeso. This module decomposes raw YAML text into 
semantic Shard models while healing structural "trauma" (indentation errors, 
broken list markers, unclosed quotes).

ENHANCEMENTS:
- Phase 1: Stateful flush-left list repair with lookahead
- Phase 2: Two-pass lexing for complete indentation normalization
- Phase 3: Scanner-ready context tracking for schema-aware fixes

CNCF Standards Compliance:
- Vendor Neutral: Core logic remains independent of enterprise features.
- Extensible: Designed to allow the Kubecuro 'Pro' layer to inject custom 
  heuristics via the HealContext.
- Robust: Handles complex K8s manifest patterns (Anchors, Block Scalars).

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-26
"""

import re
import sys
import logging
from typing import List, Tuple, Any, Optional, Dict
from akeso.models import Shard

logger = logging.getLogger("akeso.lexer")


class AkesoLexer:
    """
    Orchestrates the transition from raw text to semantic Shards.

    This lexer is 'forgiving'—it attempts to fix common YAML syntax errors 
    found in GitOps pipelines before they reach the structural validation stage.
    
    Enhanced Architecture (Multi-Phase):
    1. Line-by-line tokenization (Pass 1)
    2. Context-aware indentation repair (Pass 2)
    3. Semantic validation hooks (for Scanner integration)
    """

    def __init__(self):
        # State tracking for multi-line block scalars (|, >)
        self.in_block: bool = False
        self.block_indent: int = 0
        
        # Phase 1: Stateful repair tracking
        self._last_list_parent_indent: Optional[int] = None
        self._consecutive_list_fixes: int = 0
        
        # Phase 2: Context stack for nested structures
        self._indent_context: List[Tuple[str, int]] = []  # [(key_name, indent_level)]
        
        # Statistics for audit logs
        self.repair_stats: Dict[str, int] = {
            "flush_left_lists_fixed": 0,
            "nested_lists_normalized": 0,
            "quote_repairs": 0,
            "spacing_fixes": 0
        }

    # =========================================================================
    # LOW-LEVEL HELPERS (Pure Logic)
    # =========================================================================

    def _clean_artifacts(self, text: str) -> str:
        """
        Removes UTF-8 BOM markers and normalizes line endings.
        
        Handles:
        - UTF-8 BOM (\ufeff)
        - Windows CRLF → Unix LF
        - Trailing whitespace normalization
        """
        text = text.lstrip("\ufeff")
        return text.replace("\r\n", "\n")

    def _find_comment_split(self, text: str) -> int:
        r"""
        Finds the real '#' start point for inline comments.
        
        Correctly handles:
        - Hashes inside quotes: key: "value#notcomment"
        - Escaped hashes: key: value\#notcomment
        - YAML 1.1 edge cases: url: http://example.com#anchor
        
        Returns:
            int: Index of comment start, or -1 if no comment
        """
        in_double_quote = False
        in_single_quote = False
        escaped = False

        # Track the first "comment-like" hash seen inside a quote
        # If the quote never closes, we fallback to this index.
        potential_comment_idx = -1

        for i, char in enumerate(text):
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote

            # Hash is a comment if not quoted and preceded by whitespace
            if char == "#":
                is_quoted = in_double_quote or in_single_quote
                is_boundary = (i == 0 or text[i - 1].isspace())
                
                if not is_quoted and is_boundary:
                    return i
                
                # If it looks like a comment but is quoted, track it as candidate
                if is_quoted and is_boundary and potential_comment_idx == -1:
                    potential_comment_idx = i

        # Edge Case: If we ended with an unclosed quote, assume the first 
        # "comment-like" hash was actually a comment (lexical recovery).
        if (in_double_quote or in_single_quote) and potential_comment_idx != -1:
            return potential_comment_idx

        return -1

    # =========================================================================
    # SEMANTIC EXTRACTION (Key / Value / List Logic)
    # =========================================================================

    def _extract_semantics(self, code_part: str) -> Tuple[str, Optional[Any], bool]:
        """
        Decomposes a string into (key, value, is_list).
        
        Handles YAML 1.1 boolean protection (yes/no/on/off) automatically.
        
        Examples:
            "- item" → ("", "item", True)
            "key: value" → ("key", "value", False)
            "key:" → ("key", None, False)
            "- key: value" → ("key", "value", True)
        
        Returns:
            Tuple[str, Optional[Any], bool]: (key, value, is_list_item)
        """
        clean = code_part.strip()

        if not clean or clean.startswith("---"):
            return "", None, False

        # 1. Handle Anchors (&), Aliases (*), and Tags (!)
        if clean.startswith(("&", "*", "!")):
            split_match = re.search(r'[\s"\'\[\{]', clean[1:])
            split_pos = split_match.start() + 1 if split_match else len(clean)
            modifier = clean[:split_pos]
            remaining = clean[split_pos:].lstrip()

            _, val, is_l = self._extract_semantics(remaining)
            return "", f"{modifier} {val or ''}".strip(), is_l

        # 2. List item detection
        is_list = clean.startswith("-")
        if is_list:
            clean = clean[1:].lstrip()
            if not clean:
                return "", "", True

        # 3. Standard key: value parsing
        if ":" in clean:
            # Check for quoted keys (e.g., "service.beta:8080": val)
            if clean[0] in ('"', "'"):
                quote = clean[0]
                end_idx = clean.find(quote, 1)
                if end_idx != -1 and clean[end_idx + 1:].lstrip().startswith(":"):
                    key = clean[1:end_idx]
                    val = clean[end_idx + 1:].lstrip()[1:].strip()
                    return key, val or None, is_list

            key_part, _, val_part = clean.partition(":")
            val = val_part.strip()

            # Boolean protection: prevents YAML 1.1 parsers from turning 'on' into True
            if val.lower() in {"yes", "no", "y", "n", "on", "off"}:
                val = f'"{val}"'
                self.repair_stats["quote_repairs"] += 1

            return key_part.strip().strip('"\''), val if val else None, is_list

        return "", clean, is_list

    # =========================================================================
    # ENHANCED QUOTE BALANCING (Pro-Grade)
    # =========================================================================

    def _balance_quotes(self, value: str) -> str:
        """
        Intelligently balances quotes in YAML values.
        
        Handles:
        1. Unclosed quotes: "hello → "hello"
        2. Mid-value quotes: hello" world → hello" world (no fix, ambiguous)
        3. Escaped quotes: "say \\"hi\\" → preserved
        4. Mixed quotes: "it's fine → "it's fine"
        
        Args:
            value: The value part after the colon
            
        Returns:
            str: Value with balanced quotes (if fixable)
        """
        stripped = value.strip()
        
        # Empty or single character - skip
        if len(stripped) <= 1:
            return value
        
        first_char = stripped[0]
        last_char = stripped[-1]
        
        # Only repair if value STARTS with a quote
        if first_char not in ('"', "'"):
            return value
        
        # Check if already balanced
        if first_char == last_char:
            return value  # Already balanced
        
        # Count quotes to detect escaped vs unescaped
        quote_type = first_char
        quote_count = 0
        escaped = False
        
        for i, char in enumerate(stripped):
            if escaped:
                escaped = False
                continue
            
            if char == '\\':
                escaped = True
                continue
            
            if char == quote_type:
                quote_count += 1
        
        # If odd number of quotes, add closing quote
        if quote_count % 2 == 1:
            # Add to original value (preserve spacing)
            fixed_value = value.rstrip() + quote_type
            self.repair_stats["quote_repairs"] += 1
            logger.debug(f"Quote repair: {value.strip()} → {fixed_value.strip()}")
            return fixed_value
        
        # Even number of quotes or ambiguous - don't touch
        return value

    # =========================================================================
    # PHASE 1: STATEFUL FLUSH-LEFT REPAIR
    # =========================================================================

    def _fix_flush_left_lists_phase1(self, shards: List[Shard], working_line: str) -> str:
        """
        Phase 1: Stateful flush-left list repair with memory.
        
        Algorithm:
        1. Detect key without value (parent)
        2. Check if current line is flush-left list item
        3. Fix with memory to prevent double-fixing
        4. Track consecutive fixes for audit logs
        
        Fixes Edge Cases:
        - Multiple list items under one key
        - Already-indented items (skip to prevent double-indent)
        - Nested keys with lists
        
        Args:
            shards: Previously processed shards (for context)
            working_line: Current line to potentially fix
            
        Returns:
            str: Fixed line (or original if no fix needed)
        """
        # Safety: Need at least one previous shard
        if not shards:
            return working_line
        
        last_shard = shards[-1]
        
        # Only fix if previous line was a key without value
        if not (last_shard.key and not last_shard.value):
            # Reset tracking when we move past list context
            self._last_list_parent_indent = None
            self._consecutive_list_fixes = 0
            return working_line
        
        # Check if current line is a list item
        stripped = working_line.lstrip()
        current_indent = len(working_line) - len(stripped)
        
        if not stripped.startswith("-"):
            return working_line
        
        # Already indented - check if it's correct or needs adjustment
        if current_indent > 0:
            expected_indent = last_shard.indent + 2
            
            # If indented but wrong amount, normalize it
            if current_indent != expected_indent:
                logger.debug(
                    f"Line {len(shards)+1}: Normalizing indent from {current_indent} to {expected_indent}"
                )
                working_line = (" " * expected_indent) + stripped
                self.repair_stats["nested_lists_normalized"] += 1
            
            return working_line
        
        # Flush-left list item detected - needs fixing
        parent_indent = last_shard.indent
        expected_indent = parent_indent + 2
        
        # Track consecutive fixes under same parent
        if self._last_list_parent_indent == parent_indent:
            self._consecutive_list_fixes += 1
        else:
            self._last_list_parent_indent = parent_indent
            self._consecutive_list_fixes = 1
        
        # Apply fix
        fixed_line = (" " * expected_indent) + stripped
        self.repair_stats["flush_left_lists_fixed"] += 1
        
        logger.debug(
            f"Line {len(shards)+1}: Fixed flush-left list item "
            f"(parent indent={parent_indent}, fix #{self._consecutive_list_fixes})"
        )
        
        return fixed_line

    # =========================================================================
    # PHASE 2: TWO-PASS INDENTATION NORMALIZATION
    # =========================================================================

    def _normalize_indentation_phase2(self, shards: List[Shard]) -> List[Shard]:
        """
        Phase 2: Context-aware indentation repair with full document visibility.
        
        This pass runs AFTER initial sharding and fixes:
        1. Inconsistent list indentation across multi-doc YAMLs
        2. Nested structures that Phase 1 couldn't see
        3. Mixed indentation styles (2-space vs 4-space)
        
        Algorithm:
        1. Build context stack of parent keys and their indents
        2. When we see a list item, validate against expected indent
        3. Fix entire list sequences atomically (not one-by-one)
        4. Handle document boundaries (---) as context resets
        
        Args:
            shards: List of shards from Pass 1
            
        Returns:
            List[Shard]: Shards with normalized indentation
        """
        if not shards:
            return shards
        
        context_stack: List[Tuple[str, int]] = []  # [(key_name, indent_level)]
        normalized_shards = []
        
        i = 0
        while i < len(shards):
            shard = shards[i]
            
            # Document boundary resets all context
            if shard.is_doc_boundary:
                context_stack.clear()
                normalized_shards.append(shard)
                i += 1
                continue
            
            # Update context stack for keys
            if shard.key and ":" in shard.raw_line:
                # Pop stack back to current or shallower indent
                while context_stack and context_stack[-1][1] >= shard.indent:
                    context_stack.pop()
                
                # Add this key to context if it has no value (expects children)
                if not shard.value:
                    context_stack.append((shard.key, shard.indent))
                
                normalized_shards.append(shard)
                i += 1
                continue
            
            # Handle list items with context awareness
            if shard.is_list_item or shard.raw_line.lstrip().startswith("-"):
                # Determine expected indent from context
                if context_stack:
                    parent_key, parent_indent = context_stack[-1]
                    expected_indent = parent_indent + 2
                else:
                    # Top-level list (no parent key)
                    expected_indent = 0
                
                # Check if this list item needs normalization
                if shard.indent != expected_indent:
                    old_indent = shard.indent
                    
                    # Fix this shard
                    shard.indent = expected_indent
                    shard.raw_line = (" " * expected_indent) + shard.raw_line.lstrip()
                    
                    logger.debug(
                        f"Phase 2: Normalized list item indent {old_indent} → {expected_indent} "
                        f"(parent: {context_stack[-1][0] if context_stack else 'root'})"
                    )
                    
                    self.repair_stats["nested_lists_normalized"] += 1
                
                # Look ahead to fix consecutive list items at same level
                j = i + 1
                while j < len(shards):
                    next_shard = shards[j]
                    
                    # Stop if we hit a non-list item or different indent level
                    if not (next_shard.is_list_item or next_shard.raw_line.lstrip().startswith("-")):
                        break
                    
                    # Fix consecutive item if needed
                    if next_shard.indent != expected_indent:
                        next_shard.indent = expected_indent
                        next_shard.raw_line = (" " * expected_indent) + next_shard.raw_line.lstrip()
                        self.repair_stats["nested_lists_normalized"] += 1
                    
                    j += 1
                
                # Add all list items we processed
                normalized_shards.extend(shards[i:j])
                i = j
                continue
            
            # Default: pass through unchanged
            normalized_shards.append(shard)
            i += 1
        
        return normalized_shards

    # =========================================================================
    # LINE REPAIR (Structural Healing)
    # =========================================================================

    def repair_line(self, line: str) -> Tuple[int, str, str, bool]:
        """
        Performs surgical line repair and returns the updated block state.
        
        This is the bridge between raw trauma and semantic shards.
        
        Repairs:
        - Tab → Space conversion
        - Missing spaces after list markers (--item → - item)
        - Missing spaces after colons (key:value → key: value)
        - Unclosed quotes (key: "value → key: "value")
        - Block scalar detection (| and >)
        
        Returns:
            Tuple[int, str, str, bool]: (indent, code, comment, in_block_state)
        """
        indent = len(line) - len(line.lstrip("\t "))
        raw_line = line.replace("\t", "  ").rstrip()
        content = raw_line.lstrip()

        if not content:
            return 0, "", "", self.in_block

        if content.startswith("---"):
            self.in_block = False
            return 0, "---", "", False

        # Manage block scalar state (|, >)
        if self.in_block:
            if indent < self.block_indent and content != "":
                self.in_block = False
            else:
                return indent, content, "", True

        # Split code from comments
        split_idx = self._find_comment_split(raw_line)
        if split_idx != -1:
            code_part = raw_line[:split_idx].strip()
            comment_part = raw_line[split_idx:].lstrip("# ").rstrip()
        else:
            code_part = raw_line.strip()
            comment_part = ""

        if content.startswith("#"):
            return indent, "", content, self.in_block

        # Structural Healing: Ensure space after list markers
        if code_part.startswith("-") and len(code_part) > 1 and code_part[1].isalpha():
            code_part = "- " + code_part[1:]
            self.repair_stats["spacing_fixes"] += 1

        # Structural Healing: Ensure space after colons
        if ":" in code_part:
            k, s, v = code_part.partition(":")
            if v.strip() and not v.startswith(" "):
                v = " " + v.lstrip()
                self.repair_stats["spacing_fixes"] += 1

            # Enhanced Quote Balancing for unclosed strings
            v_val = v.strip()
            if len(v_val) > 1 and v_val[0] in ('"', "'") and v_val[-1] != v_val[0]:
                quote_char = v_val[0]
                # Safety: Only fix if no other quotes of same type inside
                if v_val[1:-1].count(quote_char) == 0:
                    v = v + quote_char
                    self.repair_stats["quote_repairs"] += 1
                else:
                    logger.debug(f"Skipping ambiguous quote: {v_val[:30]}...")
            
            code_part = f"{k}:{v}"

        # Detect block scalar headers
        if re.search(r"[|>][+\-]?\d?$", code_part.strip()):
            self.in_block = True
            self.block_indent = indent + 1

        return indent, code_part, comment_part, self.in_block

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def shard(self, raw_yaml: str, enable_phase2: bool = True) -> List[Shard]:
        """
        Transforms raw text into semantic Shards with multi-phase healing.
        
        Architecture:
        - Pass 1: Line-by-line tokenization with Phase 1 stateful repairs
        - Pass 2: Context-aware indentation normalization (optional)
        
        Args:
            raw_yaml: Raw YAML text (potentially malformed)
            enable_phase2: If True, runs two-pass normalization (default: True)
                          Set False for performance-critical paths
        
        Returns:
            List[Shard]: Semantic shards ready for Scanner processing
        
        Example:
            >>> lexer = AkesoLexer()
            >>> shards = lexer.shard(broken_yaml)
            >>> print(f"Fixed {lexer.repair_stats['flush_left_lists_fixed']} lists")
        """
        # Reset state for new document
        self._reset_state()
        
        # Clean input
        clean_yaml = self._clean_artifacts(raw_yaml)
        self.in_block = False
        lines = clean_yaml.splitlines()
        shards: List[Shard] = []

        # =====================================================================
        # PASS 1: LINE-BY-LINE TOKENIZATION + PHASE 1 REPAIRS
        # =====================================================================
        
        for i, original_line in enumerate(lines):
            was_in_block = self.in_block
            
            # Phase 1: Stateful flush-left repair
            working_line = self._fix_flush_left_lists_phase1(shards, original_line)
            
            # Phase 1.5: Universal Fused Keyword Heuristic
            # Fixes: "kindService" -> "kind: Service", "apiVersionV1" -> "apiVersion: V1"
            stripped = working_line.strip()
            # Run this BEFORE missing colon check to catch "specPorts" -> "spec: Ports" 
            # instead of "specPorts:"
            if stripped and ":" not in working_line:
                # Safe List: Keys that should NEVER be prefixes of other standard keys
                SAFE_FUSED_KEYS = {
                    "kind", "apiVersion", "metadata", "spec", "status", 
                    "selector", "template", "resources", "containers", 
                    "volumes", "labels", "annotations", "data", "ports",
                    "env", "image"
                }
                
                for key_candidate in SAFE_FUSED_KEYS:
                    if stripped.startswith(key_candidate) and len(stripped) > len(key_candidate):
                        suffix = stripped[len(key_candidate):]
                        # Only split if suffix implies a new word (Uppercase or Digit)
                        if suffix[0].isupper() or suffix[0].isdigit() or (key_candidate == "apiVersion" and suffix.lower().startswith('v')):
                             # Calculate original indent
                             prefix_indent = len(working_line) - len(working_line.lstrip())
                             working_line = (" " * prefix_indent) + f"{key_candidate}: {suffix}"
                             self.repair_stats["spacing_fixes"] += 1
                             logger.debug(f"Line {i+1}: Healed fused keyword '{stripped}' -> '{key_candidate}: {suffix}'")
                             break

            # Phase 1.6: Missing Colon Heuristic (Lookahead)
            # Fixes: "spec" (newline) "  ports:" -> "spec:" (newline) "  ports:"
            # Re-strip working_line in case Phase 1.5 modified it? 
            # If Phase 1.5 modified it, it has a colon now, so the check `if ":" not in` matches intended behavior.
            stripped = working_line.strip()
            if stripped and stripped.replace("-", "").replace("_","").isalnum() and ":" not in stripped:
                # Look ahead for indentation
                if i + 1 < len(lines):
                    next_line = lines[i+1]
                    cur_indent = len(working_line) - len(working_line.lstrip())
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    if next_indent > cur_indent and next_line.strip():
                        working_line = working_line.rstrip() + ":"
                        self.repair_stats["spacing_fixes"] += 1
                        logger.debug(f"Line {i+1}: Healed missing colon for parent key '{stripped}'")

            # Structural repair (spacing, quotes, etc.)
            indent, code, comment, is_now_in_block = self.repair_line(working_line)
            
            is_block_content = was_in_block and is_now_in_block
            is_doc = code == "---"

            # Build shard if there's content
            if code.strip() or is_block_content or is_doc:
                if is_block_content:
                    key, value, is_list = "", code, False
                else:
                    key, value, is_list = self._extract_semantics(code)

                shards.append(Shard(
                    line_no=i + 1,
                    indent=indent,
                    key=key,
                    value=value,
                    is_list_item=is_list,
                    is_block=is_block_content,
                    is_doc_boundary=is_doc,
                    comment=comment,
                    raw_line=working_line,  # Use potentially-fixed line
                ))

        # =====================================================================
        # PASS 2: CONTEXT-AWARE INDENTATION NORMALIZATION
        # =====================================================================
        
        if enable_phase2 and shards:
            shards = self._normalize_indentation_phase2(shards)
            logger.debug(
                f"Phase 2 complete: Normalized {self.repair_stats['nested_lists_normalized']} items"
            )
        
        # Log repair summary
        total_fixes = sum(self.repair_stats.values())
        if total_fixes > 0:
            logger.info(
                f"Lexer healing complete: {total_fixes} repairs "
                f"(flush-left: {self.repair_stats['flush_left_lists_fixed']}, "
                f"normalized: {self.repair_stats['nested_lists_normalized']}, "
                f"quotes: {self.repair_stats['quote_repairs']}, "
                f"spacing: {self.repair_stats['spacing_fixes']})"
            )
        
        return shards

    # =========================================================================
    # PHASE 3: SCANNER INTEGRATION HOOKS
    # =========================================================================

    def get_repair_audit_log(self) -> List[str]:
        """
        Returns human-readable audit log of all repairs performed.
        
        Used by Pipeline for comprehensive audit trail.
        
        Returns:
            List[str]: Audit log entries
        """
        log_entries = []
        
        if self.repair_stats["flush_left_lists_fixed"] > 0:
            log_entries.append(
                f"Lexer: Fixed {self.repair_stats['flush_left_lists_fixed']} flush-left list items"
            )
        
        if self.repair_stats["nested_lists_normalized"] > 0:
            log_entries.append(
                f"Lexer: Normalized {self.repair_stats['nested_lists_normalized']} nested list indents"
            )
        
        if self.repair_stats["quote_repairs"] > 0:
            log_entries.append(
                f"Lexer: Repaired {self.repair_stats['quote_repairs']} unclosed quotes"
            )
        
        if self.repair_stats["spacing_fixes"] > 0:
            log_entries.append(
                f"Lexer: Fixed {self.repair_stats['spacing_fixes']} spacing issues"
            )
        
        return log_entries

    def prepare_for_scanner(self, shards: List[Shard]) -> Dict[str, Any]:
        """
        Prepares metadata for Scanner to enable schema-aware validation.
        
        This is Phase 3 preparation - provides context the Scanner needs
        to make intelligent decisions about structure.
        
        Returns:
            Dict with:
            - indent_context: Current nesting structure
            - repair_stats: What was fixed
            - structure_hints: Detected patterns (lists vs maps)
        """
        # Build structure map
        structure_hints = {
            "has_lists": any(s.is_list_item for s in shards),
            "max_nesting_depth": max((s.indent // 2 for s in shards), default=0),
            "document_count": sum(1 for s in shards if s.is_doc_boundary) + 1,
            "has_block_scalars": any(s.is_block for s in shards),
        }
        
        return {
            "indent_context": self._indent_context.copy(),
            "repair_stats": self.repair_stats.copy(),
            "structure_hints": structure_hints,
        }

    # =========================================================================
    # INTERNAL STATE MANAGEMENT
    # =========================================================================

    def _reset_state(self):
        """Resets all internal state for processing a new document."""
        self.in_block = False
        self.block_indent = 0
        self._last_list_parent_indent = None
        self._consecutive_list_fixes = 0
        self._indent_context.clear()
        self.repair_stats = {
            "flush_left_lists_fixed": 0,
            "nested_lists_normalized": 0,
            "quote_repairs": 0,
            "spacing_fixes": 0
        }
# =============================================================================
# BACKWARD COMPATIBILITY ALIAS
# =============================================================================

KubeLexer = AkesoLexer
