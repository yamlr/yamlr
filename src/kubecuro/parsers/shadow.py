#!/usr/bin/env python3
"""
AKESO SHADOW - Layout Preservation Engine
-----------------------------------------
Captures and preserves the "Visual Shadow" (comments, gaps, and indentation) 
of a manifest. Ensures that structural healing does not destroy human intent.

Architecture:
Anchors non-data artifacts (comments, blank lines) to the nearest logical Shard.
This allows the Structurer to move a key (e.g., moving 'kind' to the top) 
while carrying its associated comments along with it.

[2026-01-22] OSS Enhancements:
- Indentation Physics 2.0: Detects and prepares indentation normalization.
- Opaque Buffer Protection: Hardened handling for block-scalar data (scripts).
- Thorough documentation and CNCF standard compliance.

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-22
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

# Internal imports
from kubecuro.models import Shard
from kubecuro.parsers.lexer import KubeLexer

logger = logging.getLogger("kubecuro.shadow")

@dataclass
class Gap:
    """Represents consecutive blank lines for layout preservation."""
    count: int = 1

@dataclass
class ShadowMetadata:
    """Metadata anchored to a specific line/Shard."""
    sequence_above: List[Union[str, Gap]] = field(default_factory=list)
    inline_comment: Optional[str] = None
    original_indent: int = 0

class AkesoShadow:
    """
    The Curator: Anchors comments and blank lines to the nearest Shard.
    Ensures that the final YAML output looks exactly like the input, 
    even if keys were reordered or repaired.
    """

    def __init__(self):
        """
        Initializes the shadow engine.
        Uses KubeLexer logic to ensure quote-aware comment splitting.
        """
        # Share the logic with the Lexer to ensure quote/escape awareness
        self._lexer_logic = KubeLexer()
        self.comment_map: Dict[int, ShadowMetadata] = {}
        self.orphans: List[Union[str, Gap]] = []
        self._orphans_anchored: bool = False
        
        # OSS-1: Indentation Physics state
        self.detected_indents: List[int] = []
        self.majority_indent: int = 2

    def reset(self) -> None:
        """
        [Stage 0] Clears all captured layout data to prepare for a new manifest.
        Required by the HealingPipeline for idempotent operations.
        """
        self.comment_map.clear()
        self.orphans.clear()
        self._orphans_anchored = False
        self.detected_indents.clear()
        self.majority_indent = 2
        logger.debug("Shadow engine state reset.")

    def _get_indent_level(self, line: str) -> int:
        """Calculates the number of leading spaces in a line."""
        leading_spaces = re.match(r'^\s*', line).group()
        return len(leading_spaces)

    def capture(self, raw_text: str, shards: List[Shard]) -> None:
        """
        [Stage 2A] Roadmaps the raw text using Shards to identify layout-only lines.
        Identifies comments and whitespace gaps that aren't part of the K8s logic.
        
        Args:
            raw_text: The full string of the manifest.
            shards: List of data shards identified by the Lexer.
        """
        lines = raw_text.splitlines()
        timeline_buffer: List[Union[str, Gap]] = []
        shard_lookup: Dict[int, Shard] = {s.line_no: s for s in shards}
        
        # OSS-6: Block lines (like scripts in ConfigMaps) are handled as opaque data.
        # We must NOT attempt to anchor layout metadata inside these lines.
        protected_lines = {s.line_no for s in shards if s.is_block}

        for i, line in enumerate(lines, 1):
            # Skip processing for opaque block data to preserve internal script formatting
            if i in protected_lines:
                continue

            stripped = line.strip()
            current_indent = self._get_indent_level(line)

            # --- GAP CAPTURE ---
            # If the line is empty, it's a gap. Increment the count if following another gap.
            if not stripped:
                if timeline_buffer and isinstance(timeline_buffer[-1], Gap):
                    timeline_buffer[-1].count += 1
                else:
                    timeline_buffer.append(Gap(count=1))
                continue

            # --- STANDALONE COMMENT CAPTURE ---
            # Capture lines that are exclusively comments and not attached to a Shard key.
            if stripped.startswith("#") and i not in shard_lookup:
                timeline_buffer.append(line)
                continue

            # --- ANCHOR TO DATA LINE ---
            # When we hit a line containing actual data (a Shard), we flush the buffer to it.
            if i in shard_lookup:
                current_shard = shard_lookup[i]
                
                # OSS-1: Track indentation for majority-based normalization
                if current_indent > 0:
                    self.detected_indents.append(current_indent)

                inline_part: Optional[str] = None
                # Use lexer logic to correctly find '#' that isn't inside a quoted string
                comment_idx = self._lexer_logic._find_comment_split(line)
                
                if comment_idx != -1:
                    inline_part = line[comment_idx:].strip()

                # SKIP ANCHORING TO DOCUMENT BOUNDARIES
                # Let orphan logic in apply() handle comments before/after ---
                if not current_shard.is_doc_boundary:
                    # Anchor the captured layout to this line number
                    self.comment_map[i] = ShadowMetadata(
                        sequence_above=timeline_buffer.copy(),
                        inline_comment=inline_part,
                        original_indent=current_indent
                    )
                    timeline_buffer.clear()
                # If it IS a boundary, keep buffer intact for orphan processing

        # Determine majority indentation (OSS-1 Physics)
        if self.detected_indents:
            # Simple heuristic: find the most frequent non-zero indentation step
            diffs = [self.detected_indents[i] - self.detected_indents[i-1] 
                     for i in range(1, len(self.detected_indents)) 
                     if self.detected_indents[i] > self.detected_indents[i-1]]
            if diffs:
                self.majority_indent = max(set(diffs), key=diffs.count)
            else:
                self.majority_indent = min(self.detected_indents) if self.detected_indents else 2

        # Any leftover comments or gaps at the end of the file are 'orphans'
        self.orphans = timeline_buffer

    def apply(self, shards: List[Shard]) -> None:
        """
        [Stage 2B] Grafts the captured layout onto the Shard objects.
        This modifies the shards in-place so the Structurer can see the metadata.
        
        Args:
            shards: The list of shards to be enriched with layout metadata.
        """
        if not shards:
            return

        for idx, shard in enumerate(shards):
            meta = self.comment_map.get(shard.line_no)
            if meta:
                # Ensure the shard has a layout_sequence attribute
                if not hasattr(shard, "layout_sequence"):
                    shard.layout_sequence = []
                
                # Prepend the comments/gaps found above this line
                shard.layout_sequence.extend(meta.sequence_above)

                # Store indentation metadata for Stage 9 (Serialization)
                shard.original_indent = meta.original_indent

                # Merge inline comments into the shard's primary comment field
                if meta.inline_comment:
                    clean_inline = meta.inline_comment.lstrip("#").strip()
                    if shard.comment:
                        # Prevent duplicate comments if the Lexer already caught it
                        if clean_inline and clean_inline not in shard.comment:
                            shard.comment = f"{shard.comment} | {clean_inline}"
                    else:
                        shard.comment = clean_inline

            # Handle trailing orphans: Attach them to the last ACTUAL DATA shard
            # Skip document boundaries and find the last meaningful content
            if idx == len(shards) - 1 and self.orphans and not self._orphans_anchored:
                # Find the last non-boundary shard to anchor orphans
                target_shard = None
                for reverse_idx in range(len(shards) - 1, -1, -1):
                    candidate = shards[reverse_idx]
                    if not candidate.is_doc_boundary:
                        target_shard = candidate
                        break
                
                # Anchor to the found target (or fallback to current shard if all are boundaries)
                anchor_target = target_shard if target_shard else shard
                
                if not hasattr(anchor_target, "layout_sequence"):
                    anchor_target.layout_sequence = []
                
                anchor_target.layout_sequence.extend(self.orphans)
                self._orphans_anchored = True
                
                logger.debug(
                    f"Orphan anchoring: Attached {len(self.orphans)} orphans to "
                    f"line {anchor_target.line_no} (skipped {len(shards) - reverse_idx - 1} boundaries)"
                )
        
        logger.debug(f"Layout metadata grafted onto {len(shards)} shards. "
                     f"Majority Indent detected: {self.majority_indent}")

# Namespaced Alias for Kubecuro compatibility
# Ensures the pipeline can call KubeShadow directly without import errors.
KubeShadow = AkesoShadow