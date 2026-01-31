#!/usr/bin/env python3
"""
Yamlr STRUCTURER - The Reconciled Architect
-------------------------------------------
Critical Fix: Handle nested forced_arrays (e.g., apiGroups under rules).

Author: Nishar A Sunkesala / Yamlr Team
Date: 2026-01-26
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
from io import StringIO
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from yamlr.models import Shard

if TYPE_CHECKING:
    from yamlr.core.context import HealContext

logger = logging.getLogger("yamlr.parsers.structurer")

class YamlrStructurer:
    """
    The Architect: Rebuilds the YAML tree from identified shards.
    """

    def __init__(self, catalog: Dict[str, Any]):
        self.catalog = catalog
        self.yaml_engine = YAML()
        self.yaml_engine.preserve_quotes = True
        self.yaml_engine.indent(mapping=2, sequence=4, offset=2)
        
        # Fields that MUST be arrays in Kubernetes
        self.forced_arrays = {
            "containers", "initContainers", "ephemeralContainers", 
            "ports", "env", "envFrom", "volumeMounts", "volumeDevices",
            "volumes", "args", "command", "imagePullSecrets", 
            "tolerations", "nodeSelector", "hostAliases",
            "rules", "subjects", "roleRef", "paths", "hosts",
            "matchExpressions", "endpoints", "subsets", 
            "addresses", "notReadyAddresses", "topologyKeys",
            "finalizers", "ownerReferences", "managedFields",
            "conditions", "taints", "apiGroups", "resources", "verbs"
        }

    def reconstruct(self, context: 'HealContext') -> List[CommentedMap]:
        """[Stage 6] Rebuilds the folder-like structure from flat data shards."""
        all_documents = []
        current_shards = []
        doc_count = 0
        
        try:
            if hasattr(context.shadow_engine, 'majority_indent'):
                m_indent = context.shadow_engine.majority_indent
                self.yaml_engine.indent(mapping=m_indent, sequence=m_indent*2, offset=m_indent)

            for shard in context.shards:
                if shard.is_doc_boundary:
                    if current_shards:
                        this_kind = context.identities[doc_count].kind if doc_count < len(context.identities) else None
                        try:
                            doc = self._build_tree(current_shards, this_kind)
                            all_documents.append(doc)
                        except Exception as e:
                            logger.error(f"Stage 6: Failed to build tree for document {doc_count} (kind: {this_kind}): {e}")
                        current_shards = []
                        doc_count += 1
                else:
                    current_shards.append(shard)
            
            if current_shards:
                this_kind = context.identities[doc_count].kind if doc_count < len(context.identities) else None
                try:
                    doc = self._build_tree(current_shards, this_kind)
                    all_documents.append(doc)
                except Exception as e:
                    logger.error(f"Stage 6: Failed to build tree for final document (kind: {this_kind}): {e}")

            return all_documents
            
        except Exception as e:
            logger.error(f"Stage 6: Critical reconstruction failure: {e}")
            raise

    def serialize(self, documents: List[CommentedMap], compact: bool = False) -> str:
        """[Stage 9] Turns the internal tree back into a text file (YAML)."""
        output = StringIO()
        if compact:
            self.yaml_engine.indent(mapping=2, sequence=2, offset=0)
        
        try:
            if len(documents) > 1:
                self.yaml_engine.dump_all(documents, output)
            elif documents:
                self.yaml_engine.dump(documents[0], output)
            else:
                return ""
            return output.getvalue()
        except Exception as e:
            logger.error(f"Stage 9: Serialization failed: {e}")
            raise
        finally:
            output.close()

    def _build_tree(self, shards: List[Shard], default_kind: Optional[str]) -> CommentedMap:
        """
        [Optimized v2] The core engine that puts the pieces back together.
        """
        rebuilt_tree = CommentedMap()
        active_kind = default_kind
        
        # Identity Discovery (Fast Scan)
        if not active_kind:
            for s in shards:
                if s.key == "kind" and s.value:
                    active_kind = str(s.value).strip("'\"")
                    break
        
        # Heuristic Learning Mode
        kind_schema = self.catalog.get(active_kind, {"fields": {}})
        if active_kind and not kind_schema.get("fields"):
            logger.info(f"Learning Mode: Heuristic recovery for unknown kind '{active_kind}'")

        # Cache Locals for Speed
        forced_arrays = self.forced_arrays
        clean_value = self._clean_value
        apply_layout = self._apply_layout
        
        # Stack: [(indent: int, container: Map/Seq, schema: dict)]
        # We use a simpler stack structure for speed: indent is the primary key
        stack = [(-1, rebuilt_tree, kind_schema)]
        
        # Cache Types
        T_MAP = CommentedMap
        T_SEQ = CommentedSeq
        T_INT = int

        for i, shard in enumerate(shards):
            # Skip empty lines (comments and spacing handled by previous shard layout)
            if not shard.key and shard.value is None and not shard.is_list_item:
                continue

            # Fast property access
            s_key = shard.key
            s_val = shard.value
            s_indent = shard.indent if shard.indent is not None else 0
            s_is_list = shard.is_list_item

            # =================================================================
            # 1. OPTIMIZED STACK MANAGEMENT (Indentation Physics)
            # =================================================================
            # Pop deeper scopes until we find the parent
            # Avoids tuple unpacking inside the condition
            while True:
                last_ident = stack[-1][0]
                
                # If we are deeper, we are good (break)
                if s_indent > last_ident:
                    break
                    
                # If same indent:
                if s_indent == last_ident:
                    # Special case: List items at the same indent are SIBLINGS, not children
                    # So we don't pop.
                    if s_is_list and isinstance(stack[-1][1], T_SEQ):
                        break
                    
                    # Special case: Sibling fields in a map inside a sequence
                    # Check if grandparent is a sequence
                    if len(stack) > 1 and isinstance(stack[-2][1], T_SEQ):
                         break
                
                # If we are shallower (or same indent but not special case), pop
                if len(stack) > 1:
                    stack.pop()
                else:
                    break

            # Current Context
            parent_indent, parent_container, parent_schema = stack[-1]
            
            # Schema lookup (Dictionary get is fast, no need to optimize much)
            field_info = parent_schema.get("fields", {}).get(s_key, {}) if s_key else {}

            # =================================================================
            # 2. CONTAINER SELECTION & CREATION
            # =================================================================
            
            # CASE A: We are adding to a Sequence (List)
            if isinstance(parent_container, T_SEQ):
                # If it's not a list item ("-"), but has a key, it's a map inside a list
                if not s_is_list and s_key:
                    # Check if we should add to the LAST item in the list (sibling field)
                    # or start a NEW item (implicit list item)
                    
                    # Heuristic: Is this a child of the current last item?
                    # Check nesting: is the NEXT shard indented relative to this one?
                    is_parent = (i + 1 < len(shards) and 
                               (shards[i+1].indent or 0) > s_indent)

                    # Try to reuse the last item if it exists and matches indent
                    use_existing = False
                    if len(parent_container) > 0 and isinstance(parent_container[-1], T_MAP):
                         # If we are at the same indentation as the map in the stack
                         # effectively we are adding a key to that map
                         if len(stack) > 1 and s_indent == stack[-1][0]:
                             use_existing = True

                    if use_existing:
                        existing_map = stack[-1][1]
                        if is_parent:
                            if s_key in forced_arrays:
                                new_seq = T_SEQ()
                                existing_map[s_key] = new_seq
                                apply_layout(existing_map, shard, is_key=True)
                                stack.append((s_indent, new_seq, field_info))
                            else:
                                new_map = T_MAP()
                                existing_map[s_key] = new_map
                                apply_layout(new_map, shard, is_key=False)
                                stack.append((s_indent, new_map, field_info))
                        else:
                            existing_map[s_key] = clean_value(s_val)
                            apply_layout(existing_map, shard, is_key=True)
                    else:
                        # New Map Item
                        new_item = T_MAP()
                        if is_parent:
                            if s_key in forced_arrays:
                                new_seq = T_SEQ()
                                new_item[s_key] = new_seq
                                parent_container.append(new_item)
                                apply_layout(new_item, shard, is_key=True)
                                stack.append((s_indent, new_item, field_info)) # Map
                                stack.append((s_indent, new_seq, field_info))  # Seq
                            else:
                                new_map = T_MAP() # Should this be the same new_item? NO.
                                # Wait, if key has children, the key IS the map entry
                                # BUT we are inside a sequence. 
                                # The structure is: - key: (new map)
                                # Actually, it's: - key: val
                                
                                # Correct logic:
                                # We add 'new_item' to list. 'new_item' gets 's_key'
                                # If 's_key' is parent, then `new_item[s_key]` = nested_map
                                nested_val = clean_value(s_val)
                                new_item[s_key] = nested_val if nested_val is not None else T_MAP() # Placeholder
                                
                                parent_container.append(new_item)
                                apply_layout(new_item, shard, is_key=True)
                                stack.append((s_indent, new_item, field_info))
                                
                                # If it was a parent, we need to push the CHILD container
                                # For normal maps, the child container is the value of the key
                                if isinstance(new_item[s_key], T_MAP):
                                     stack.append((s_indent, new_item[s_key], field_info))
                        else:
                            new_item[s_key] = clean_value(s_val)
                            parent_container.append(new_item)
                            apply_layout(new_item, shard, is_key=True)
                            stack.append((s_indent, new_item, field_info))
                    continue

            # CASE B: Explicit List Item ("- ...")
            if s_is_list:
                target_seq = parent_container
                
                # If parent is a Map, we might need to Auto-Vivify a sequence
                if isinstance(parent_container, T_MAP) and s_key:
                    if s_key not in parent_container:
                        parent_container[s_key] = T_SEQ()
                    target_seq = parent_container[s_key]
                
                # Handle "- value" vs "- key: value"
                if not s_key:
                    if isinstance(target_seq, T_MAP):
                        # SAFETY FIX: Parent is a Map (default assumption), but we found a scalar list.
                        # Instead of crashing with .append(), synthesize a key.
                        # This turns "- item" into "item_N: item" which Validator will flag as type error.
                        idx = len(target_seq)
                        target_seq[f"item_{idx}"] = clean_value(s_val)
                    else:
                        target_seq.append(clean_value(s_val))
                else:
                    new_item = T_MAP()
                    new_item[s_key] = clean_value(s_val)
                    if isinstance(target_seq, T_MAP):
                        # Same safety fix for keyed items, though rare
                        # ("- key: val" inside a Map -> "item_N: {key: val}")
                        idx = len(target_seq)
                        target_seq[f"item_{idx}"] = new_item
                    else:
                        target_seq.append(new_item)
                    apply_layout(new_item, shard, is_key=True)
                    stack.append((s_indent, new_item, field_info))
                continue

            # CASE C: Map Key ("key: value")
            is_parent = (i + 1 < len(shards) and (shards[i+1].indent or 0) > s_indent)
            
            if is_parent and s_key:
                if s_key in forced_arrays:
                    new_seq = T_SEQ()
                    parent_container[s_key] = new_seq
                    apply_layout(parent_container, shard, is_key=True)
                    stack.append((s_indent, new_seq, field_info))
                else:
                    new_map = T_MAP()
                    parent_container[s_key] = new_map
                    apply_layout(new_map, shard, is_key=False)
                    stack.append((s_indent, new_map, field_info))
            
            elif s_key:
                val = clean_value(s_val)
                if s_key in forced_arrays and not isinstance(val, list):
                    val = [val]
                parent_container[s_key] = val
                apply_layout(parent_container, shard, is_key=True)

        return rebuilt_tree

    def _apply_layout(self, container: Any, shard: Shard, is_key: bool = False):
        """Attaches saved comments and spacing."""
        # Check explicit attribute to avoid hasattr overhead
        if shard.layout_sequence:
            comments = []
            for item in shard.layout_sequence:
                if isinstance(item, str): 
                    comments.append(item)
                elif hasattr(item, "count"): 
                    comments.extend([""] * int(item.count))
            if comments:
                try: 
                    container.yaml_set_start_comment("\n".join(comments), indent=shard.indent)
                except: 
                    pass

        if shard.comment and is_key and isinstance(container, CommentedMap):
            try: 
                container.yaml_add_eol_comment(shard.comment, key=shard.key)
            except: 
                pass

    def _clean_value(self, val: Any) -> Any:
        """
        [Optimized] Ensures numbers stay numbers and booleans stay booleans.
        Short-circuits for common cases.
        """
        if val is None: return None
        if not isinstance(val, str): return val
        
        # Fast path for simple strings (identifiers, names)
        # 90% of K8s values are alphanumeric strings
        if val.isalnum() and not val.isdigit():
             lower = val.lower()
             if lower == "true": return True
             if lower == "false": return False
             return val

        v = val.strip().strip("'\"")
        
        # Check booleans again after stripping
        v_lower = v.lower()
        if v_lower == "true": return True
        if v_lower == "false": return False
        
        # Try number conversion only if it looks like one
        if v and (v[0].isdigit() or v[0] == '-'):
            try: 
                return float(v) if "." in v else int(v)
            except: 
                return v
        return v

# Compatibility Alias
KubeStructurer = YamlrStructurer
