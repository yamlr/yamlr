#!/usr/bin/env python3
"""
AKESO SCANNER - The Identity Archeologist
-----------------------------------------
Mines identity markers from Akeso Shards to extract the "Manifest DNA".
Strictly isolates global metadata from nested template metadata.

Architecture:
Uses an indentation stack to navigate the YAML hierarchy without a full parser.
This allows Stage 3 to identify the resource Kind/API before the Structurer 
even begins building the tree.

CNCF Standards Compliance:
- Vendor Neutral: Focuses on standard K8s Resource model.
- Robust: Block-safe and multi-document aware.
- Non-Destructive: Reads shards without modifying them.

Phase 3 Enhancements:
- Future-proof multi-schema architecture (K8s, OpenAPI, CRDs, plugins)
- Integrated with enhanced Lexer metadata (prepare_for_scanner)
- Schema-aware intent tagging with catalog integration
- Repair context correlation for audit trails
- Enhanced confidence scoring integration

OSS Patch:
- Enhanced Intent Tagging: Now tags structural K8s keys (spec, data, containers)
  to ensure the Confidence Engine accurately recognizes valid manifests.
- Multi-document isolation: Ensures clean state resets between '---' shards.

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-26
"""

import logging
from typing import List, Tuple, Optional, Any, Dict, Set

from kubecuro.models import Shard, ManifestIdentity
from kubecuro.core.deprecations import DeprecationChecker
from kubecuro.parsers.api_inference import APIVersionInferrer
from kubecuro.parsers.schema_manager import SchemaManager

logger = logging.getLogger("kubecuro.scanner")


class AkesoScanner:
    """
    Analyzes Shards to identify Kubernetes resources and tag semantic intent.

    Logic:
    - Path Tracking: Uses an indentation stack to ensure 'metadata.name' 
      is only captured at the document root, not inside a Pod template.
    - Document Awareness: Correctly handles YAML multi-doc (---) boundaries.
    - Intent Mapping: Tags shards to assist the Pipeline's confidence engine.
    - Schema Integration: Multi-catalog support for K8s, OpenAPI, CRDs, and plugins.
    """

    def __init__(self, 
                 catalog: Optional[Dict[Any, Any]] = None,
                 schema_type: str = "kubernetes",
                 app_name: str = "kubecuro",
                 **schema_sources):
        """
        Initializes the scanner with schema catalog(s).
        
        Args:
            catalog: Primary schema catalog (K8s core + CRDs)
            schema_type: Schema format type
            app_name: Name of the application (e.g. "kubecuro") for branding messages
            **schema_sources: Additional schema catalogs
        """
        # Primary catalog (K8s core + standard CRDs)
        self.catalog = catalog or {}
        self.schema_type = schema_type
        self.app_name = app_name.capitalize() # Ensure proper casing (Akeso/Kubecuro)
        
        # Future expansion: Additional schema sources
        self.openapi_catalog = schema_sources.get('openapi_catalog', {})
        self.crd_catalog = schema_sources.get('crd_catalog', {})
        self.plugin_catalogs = schema_sources.get('plugin_catalogs', [])
        
        # Result store for all documents found in a single file
        self.identities: List[ManifestIdentity] = []

        # State tracking for the current document (resets on '---')
        self._current_identity = ManifestIdentity()
        self._path_stack: List[Tuple[int, str]] = []
        self._in_global_metadata = False
        self._doc_index = 0
        self.deep_array_check = True
        
        # Lexer metadata integration
        self._lexer_context: Optional[Dict[str, Any]] = None
        
        # Build unified structure keys from all schema sources
        self.schema_manager = SchemaManager(
            catalog=self.catalog,
            openapi_catalog=self.openapi_catalog,
            crd_catalog=self.crd_catalog,
            plugin_catalogs=self.plugin_catalogs
        )
        self._known_structure_keys = self.schema_manager.get_structure_keys()
        
        # Log schema initialization
        self._log_schema_initialization()
        
        self.deprecation_checker = DeprecationChecker()
        self.api_inferrer = APIVersionInferrer(
            catalog=self.catalog,
            crd_catalog=self.crd_catalog,
            plugin_catalogs=self.plugin_catalogs
        )
        
        # Pro mode detection (controlled by environment variable or license)
        self.pro_mode = schema_sources.get('pro_mode', self._detect_pro_mode())
        
        if self.pro_mode:
            logger.info("Scanner initialized in PRO mode (intelligent repair enabled)")
        else:
            logger.info("Scanner initialized in OSS mode (strict validation)")

    # ... [Skipping unchanged methods] ...

    def _filter_identities_oss(self) -> List[ManifestIdentity]:
        """
        OSS mode: Strict validation filter.
        
        Requirements:
        - BOTH kind AND apiVersion must be present
        - Aligns with Kubernetes API Server requirements
        - Provides clear error messages for missing fields
        
        Returns:
            List[ManifestIdentity]: Identities with both kind and apiVersion
        """
        valid_ids = []
        skipped_count = 0
        
        for idnt in self.identities:
            # Strict check: BOTH required
            if idnt.kind and idnt.api_version:
                valid_ids.append(idnt)
            else:
                skipped_count += 1
                
                # Clear error messages for debugging
                if not idnt.kind and not idnt.api_version:
                    logger.error(
                        f"Document {idnt.doc_index}: Missing BOTH kind and apiVersion. "
                        f"Skipping resource. (OSS mode requires both fields)"
                    )
                elif not idnt.kind:
                    logger.error(
                        f"Document {idnt.doc_index}: Missing 'kind' field "
                        f"(apiVersion: {idnt.api_version}). Skipping resource. "
                        f"Hint: Add 'kind: <ResourceType>' at root level."
                    )
                else:  # not idnt.api_version
                    logger.error(
                        f"Document {idnt.doc_index}: Missing 'apiVersion' field "
                        f"(kind: {idnt.kind}). Skipping resource. "
                        f"Hint: Add 'apiVersion: <version>' at root level. "
                        f"(Upgrade to {self.app_name} Pro for auto-inference)"
                    )
        
        if skipped_count > 0:
            logger.warning(
                f"OSS mode: Skipped {skipped_count} document(s) with missing identity fields. "
                f"Upgrade to {self.app_name} Pro for intelligent apiVersion inference."
            )
        
        return valid_ids

    # =========================================================================
    # PHASE 3: LEXER METADATA INTEGRATION
    # =========================================================================

    def set_lexer_context(self, lexer_metadata: Dict[str, Any]) -> None:
        """
        Receives metadata from the enhanced Lexer for context-aware scanning.
        
        This enables the scanner to:
        - Know what was repaired (correlate with identity extraction)
        - Adjust confidence based on repair depth
        - Use structure hints for better intent tagging
        
        Args:
            lexer_metadata: Output from lexer.prepare_for_scanner()
                - indent_context: Current nesting structure
                - repair_stats: What was fixed by lexer
                - structure_hints: Detected patterns (lists vs maps)
        """
        self._lexer_context = lexer_metadata
        
        # Log lexer repair context
        if lexer_metadata.get("repair_stats"):
            total_fixes = sum(lexer_metadata["repair_stats"].values())
            if total_fixes > 0:
                logger.debug(
                    f"Scanner received lexer context: {total_fixes} repairs performed"
                )
        
        # Log structure hints if available
        if lexer_metadata.get("structure_hints"):
            hints = lexer_metadata["structure_hints"]
            logger.debug(
                f"Lexer structure hints: {hints.get('document_count', 0)} docs, "
                f"max depth={hints.get('max_nesting_depth', 0)}, "
                f"has_lists={hints.get('has_lists', False)}"
            )

    # =========================================================================
    # MULTI-SCHEMA STRUCTURE KEY BUILDING
    # =========================================================================




    def _log_schema_initialization(self) -> None:
        """Logs schema initialization summary for debugging."""
        catalog_count = len(self.catalog)
        openapi_count = len(self.openapi_catalog)
        crd_count = len(self.crd_catalog)
        plugin_count = len(self.plugin_catalogs)
        
        logger.debug(
            f"Scanner initialized with schema_type='{self.schema_type}': "
            f"{catalog_count} K8s schemas, {openapi_count} OpenAPI schemas, "
            f"{crd_count} CRD schemas, {plugin_count} plugin catalogs"
        )
    
    def _detect_pro_mode(self) -> bool:
        """
        Detects if Akeso is running in Pro mode.
        
        Pro mode enables intelligent apiVersion inference and repair.
        OSS mode uses strict validation (both kind and apiVersion required).
        
        Detection order:
        1. Environment variable AKESO_PRO=true
        2. License file presence
        3. Default: False (OSS mode)
        
        Returns:
            bool: True if Pro mode is active
        """
        import os
        
        # Check environment variable
        if os.getenv("AKESO_PRO", "").lower() in ("true", "1", "yes"):
            logger.debug("Pro mode enabled via AKESO_PRO environment variable")
            return True
        
        # Check for license file (future expansion)
        # license_path = Path.home() / ".akeso" / "license.key"
        # if license_path.exists():
        #     logger.debug("Pro mode enabled via license file")
        #     return True
        
        # Default: OSS mode
        return False

    # =========================================================================
    # PUBLIC API: SHARD SCANNING
    # =========================================================================

    def scan_shards(self, shards: List[Shard]) -> List[ManifestIdentity]:
        """
        [Stage 3] Processes a list of Shards into one or more ManifestIdentities.
        
        This stage is critical for the pipeline to know which schema to load 
        and which hardening policies (Shield) to apply in later stages.
        
        Algorithm:
        1. Reset state for fresh scan
        2. Track minimum indentation to determine "root level"
        3. For each shard:
           - Update path context (indentation stack)
           - Tag with semantic intent (k8s.spec, k8s.metadata, etc.)
           - Extract identity markers (kind, apiVersion, name, namespace)
        4. Flush final document identity
        5. Return all valid identities found
        
        Args:
            shards: The flat list of shards produced by the Lexer
            
        Returns:
            List[ManifestIdentity]: A list of identified K8s resources
        """
        self._reset_state()
        
        # Track the minimum indentation seen in the current document
        # to identify what "root level" actually is
        min_indent = 999

        for shard in shards:
            # Document boundary: flush current identity and reset for next doc
            if shard.is_doc_boundary:
                self._flush_current_identity()
                min_indent = 999  # Reset for next doc
                continue

            # Block scalar content: skip (it's literal text, not structure)
            if shard.is_block:
                continue

            # Update min_indent if we see a valid key at shallower depth
            if shard.key and shard.indent < min_indent:
                min_indent = shard.indent

            # Update path context (maintains indentation stack)
            self._update_path_context(shard)

            # Skip shards without keys (values only, comments, etc.)
            if not shard.key:
                continue
                
            key = shard.key.strip()
            val = self._clean_id(shard.value)

            # Enhanced intent tagging with schema awareness
            self._tag_intent(shard, key)
            
            # Extract cross-resource metadata (OSS feature)
            self._extract_cross_resource_metadata(shard, key, val)

            # Skip shards without values (we need values for identity extraction)
            if not val:
                continue

            # IDENTIFICATION LOGIC
            # Check if the shard is at the 'root' of the current document
            is_root = (shard.indent == min_indent)

            if is_root:
                if key == "kind":
                    self._current_identity.kind = val
                    shard.intent_tag = "identity.kind"
                    
                    # Log if this kind has a known schema
                    if self._has_schema_for(val):
                        logger.debug(f"Detected known kind: {val}")
                    else:
                        logger.debug(f"Detected unknown kind: {val} (learning mode)")
                    
                elif key == "apiVersion":
                    self._current_identity.api_version = val
                    shard.intent_tag = "identity.api_version"

            # Metadata extraction (name/namespace)
            # Only extract from global metadata, not nested (e.g., pod templates)
            if self._in_global_metadata and not shard.is_list_item:
                if key == "name" and not self._current_identity.name:
                    self._current_identity.name = val
                    shard.intent_tag = "identity.name"
                elif key == "namespace" and not self._current_identity.namespace:
                    self._current_identity.namespace = val
                    shard.intent_tag = "identity.namespace"

        # Flush the final document identity
        self._flush_current_identity()

        # Hybrid filter: Strict for OSS, Smart repair for Pro
        if self.pro_mode:
            # Pro mode: Intelligent repair with apiVersion inference
            valid_ids = self._filter_identities_pro()
        else:
            # OSS mode: Strict validation (both kind and apiVersion required)
            valid_ids = self._filter_identities_oss()
        
        # Enhanced logging with lexer context
        self._log_scan_summary(valid_ids)
        
        # Check for deprecations after identity extraction
        for identity in valid_ids:
            if identity.api_version and identity.kind:
                dep_info = self.deprecation_checker.check(
                    identity.api_version,
                    identity.kind
                )
                
                if dep_info:
                    logger.warning(
                        f"⚠️  DEPRECATED: {identity.api_version} {identity.kind} "
                        f"(removed in K8s {dep_info.removed_in_version})"
                    )
                    # Store for reporting
                    identity.deprecation_info = dep_info
        
        return valid_ids


    # =========================================================================
    # ENHANCED INTENT TAGGING
    # =========================================================================

    def _tag_intent(self, shard: Shard, key: str) -> None:
        """
        Tags shards with semantic intent for confidence scoring.
        
        Uses multiple heuristics:
        1. Known K8s structure keys (from all catalogs)
        2. Path context (root vs nested)
        3. Lexer repair context (was this line fixed?)
        
        Intent tags are used by the Pipeline's confidence scoring
        engine to determine how "well-known" a manifest is.
        
        Args:
            shard: The shard to tag
            key: The normalized key name
        """
        # Skip if already tagged by identity extraction logic
        if hasattr(shard, 'intent_tag') and shard.intent_tag:
            return
        
        # Tag known structural keys (from all schema sources)
        if key in self._known_structure_keys:
            shard.intent_tag = f"k8s.{key}"
            return
        
        # Tag based on path depth (root vs nested)
        path_depth = len(self._path_stack)
        if path_depth == 1:
            shard.intent_tag = "k8s.root_field"
        elif path_depth == 2:
            shard.intent_tag = "k8s.nested_field"
        elif path_depth >= 3:
            shard.intent_tag = "k8s.deep_field"
        
        # Correlate with lexer repairs (for audit trail)
        if self._lexer_context and self._was_repaired(shard):
            # Add repair tag for audit correlation
            existing_tag = shard.intent_tag or ""
            shard.intent_tag = f"{existing_tag}.repaired".strip('.')

    def _was_repaired(self, shard: Shard) -> bool:
        """
        Checks if this shard was modified by the lexer.
        
        Uses lexer context to determine if this line number
        corresponds to a repair action.
        
        Returns:
            bool: True if shard was repaired by lexer
        """
        if not self._lexer_context:
            return False
        
        repair_stats = self._lexer_context.get("repair_stats", {})
        
        # If there were list fixes and this is a list item, likely repaired
        if shard.is_list_item and repair_stats.get("flush_left_lists_fixed", 0) > 0:
            return True
        
        # If there were quote repairs and this has a value, potentially repaired
        if shard.value and repair_stats.get("quote_repairs", 0) > 0:
            return True
        
        # If there were spacing fixes and this has a key, potentially repaired
        if shard.key and repair_stats.get("spacing_fixes", 0) > 0:
            return True
        
        return False

    def _has_schema_for(self, kind: str) -> bool:
        """Check if schema exists for kind. Delegates to SchemaManager."""
        return self.schema_manager.has_schema_for(kind)


    def _update_path_context(self, shard: Shard) -> None:
        """
        Uses 'Indentation Physics' to track the current key hierarchy.
        
        Maintains a stack of (indent, key) tuples to determine:
        - Are we inside 'metadata'?
        - Are we inside a nested template?
        - What's the current path (e.g., spec.template.spec.containers)?
        
        This is critical for distinguishing between:
        - metadata.name (global identity) vs
        - spec.template.metadata.name (pod template, not global)
        
        Args:
            shard: Current shard being processed
        """
        # Pop keys from the stack that are at the same or deeper indentation
        # This signals we have moved horizontally or 'out' of a block's scope
        while self._path_stack and self._path_stack[-1][0] >= shard.indent:
            self._path_stack.pop()

        # Push the current key onto the stack to track the new depth
        if shard.key:
            self._path_stack.append((shard.indent, shard.key))

        # Determine if we are currently inside the root 'metadata' block
        path_keys = [item[1] for item in self._path_stack]
        
        if "metadata" in path_keys:
            # Logic: 'metadata' must be a top-level key (index 0) to be 'Global'
            # This prevents matching 'metadata' inside 'spec.template.metadata'
            try:
                metadata_index = path_keys.index("metadata")
                self._in_global_metadata = (metadata_index == 0)
            except (ValueError, IndexError):
                self._in_global_metadata = False
        else:
            self._in_global_metadata = False

    # =========================================================================
    # INTERNAL LOGIC: IDENTITY MANAGEMENT
    # =========================================================================

    def _flush_current_identity(self) -> None:
        """
        Saves current document identity and prepares for the next YAML document.
        
        Called when:
        - A document boundary (---) is encountered
        - End of file is reached
        """
        if self._current_identity.kind or self._current_identity.api_version:
            self._current_identity.doc_index = self._doc_index
            self.identities.append(self._current_identity)

        # Reset per-document state for multi-doc (---) support
        self._current_identity = ManifestIdentity()
        self._path_stack = []
        self._in_global_metadata = False
        self._doc_index += 1
        
    def _filter_identities_oss(self) -> List[ManifestIdentity]:
        """
        OSS mode: Strict validation filter.
        
        Requirements:
        - BOTH kind AND apiVersion must be present
        - Aligns with Kubernetes API Server requirements
        - Provides clear error messages for missing fields
        
        Returns:
            List[ManifestIdentity]: Identities with both kind and apiVersion
        """
        valid_ids = []
        skipped_count = 0
        
        for idnt in self.identities:
            # Strict check: BOTH required
            if idnt.kind and idnt.api_version:
                valid_ids.append(idnt)
            else:
                skipped_count += 1
                
                # Clear error messages for debugging
                if not idnt.kind and not idnt.api_version:
                    logger.error(
                        f"Document {idnt.doc_index}: Missing BOTH kind and apiVersion. "
                        f"Skipping resource. (OSS mode requires both fields)"
                    )
                elif not idnt.kind:
                    logger.error(
                        f"Document {idnt.doc_index}: Missing 'kind' field "
                        f"(apiVersion: {idnt.api_version}). Skipping resource. "
                        f"Hint: Add 'kind: <ResourceType>' at root level."
                    )
                else:  # not idnt.api_version
                    logger.error(
                        f"Document {idnt.doc_index}: Missing 'apiVersion' field "
                        f"(kind: {idnt.kind}). Skipping resource. "
                        f"Hint: Add 'apiVersion: <version>' at root level. "
                        f"(Upgrade to {self.app_name} Pro for auto-inference)"
                    )
        
        if skipped_count > 0:
            logger.warning(
                f"OSS mode: Skipped {skipped_count} document(s) with missing identity fields. "
                f"Upgrade to {self.app_name} Pro for intelligent apiVersion inference."
            )
        
        return valid_ids
        
    def _filter_identities_pro(self) -> List[ManifestIdentity]:
        """
        Pro mode: Intelligent repair with apiVersion inference.
        
        Capabilities:
        - Auto-infers apiVersion from kind using catalog + heuristics
        - Marks repaired identities for audit trail
        - Warns user about auto-inferred values
        
        Returns:
            List[ManifestIdentity]: Identities with repairs applied
        """
        valid_ids = []
        
        for idnt in self.identities:
            # Perfect case: Both present
            if idnt.kind and idnt.api_version:
                valid_ids.append(idnt)
                continue
            
            # Repairable case: Has kind, missing apiVersion
            if idnt.kind and not idnt.api_version:
                inferred_api = self._infer_api_version(idnt.kind)
                
                if inferred_api:
                    logger.warning(
                        f"Document {idnt.doc_index}: Missing apiVersion for kind '{idnt.kind}'. "
                        f"Pro mode auto-inferred '{inferred_api}' "
                        f"(verify accuracy before applying to cluster)"
                    )
                    idnt.api_version = inferred_api
                    idnt.was_repaired = True
                    valid_ids.append(idnt)
                else:
                    logger.error(
                        f"Document {idnt.doc_index}: Missing apiVersion for kind '{idnt.kind}' "
                        f"and cannot infer safely. Skipping resource."
                    )
                continue
            
            # Unrepairable case: Has apiVersion, missing kind
            if idnt.api_version and not idnt.kind:
                logger.error(
                    f"Document {idnt.doc_index}: Missing 'kind' field "
                    f"(apiVersion: {idnt.api_version}). Cannot infer kind safely. "
                    f"Skipping resource."
                )
                continue
            
            # Unrepairable: Missing both
            logger.error(
                f"Document {idnt.doc_index}: Missing BOTH kind and apiVersion. "
                f"Cannot identify resource. Skipping."
            )
        
        return valid_ids

    def _infer_api_version(self, kind: str) -> Optional[str]:
        """
        Infers apiVersion for a given Kind.
        Delegates to APIVersionInferrer.
        """
        return self.api_inferrer.infer_version(kind)



    def _extract_cross_resource_metadata(self, shard: Shard, key: str, val: str) -> None:
        """
        Extracts cross-resource metadata using pluggable extractors.
        
        This method delegates to specialized extractors instead of
        implementing all detection logic inline.
        
        Extractors are located in: akeso.parsers.metadata_extractors/
        
        Each extractor:
        - Checks if it can handle current context
        - Extracts metadata if applicable
        - Returns True if extraction was performed
        
        Args:
            shard: Current shard being processed
            key: The key name
            val: The value
        """
        from kubecuro.parsers.metadata_extractors import get_extractors
        
        # Get path context
        path_keys = [item[1] for item in self._path_stack]
        
        # Run all extractors
        # Extractors check their own applicability and extract if matched
        for extractor in get_extractors():
            extractor.extract_if_applicable(
                shard=shard,
                key=key,
                val=val,
                path_keys=path_keys,
                identity=self._current_identity
            )

    def _clean_id(self, val: Any) -> str:
        """
        Helper to sanitize values: removes YAML quotes and trailing whitespace.
        
        Args:
            val: Raw value from shard
            
        Returns:
            str: Cleaned string value
        """
        if val is None:
            return ""
        return str(val).strip().strip("'").strip('"')

    def _log_scan_summary(self, valid_ids: List[ManifestIdentity]) -> None:
        """
        Logs comprehensive scan summary with lexer context.
        
        Args:
            valid_ids: List of successfully identified resources
        """
        summary = f"Stage 3: Identity extraction complete. Found {len(valid_ids)} resources."
        
        # Add lexer context if available
        if self._lexer_context:
            repair_stats = self._lexer_context.get("repair_stats", {})
            total_repairs = sum(repair_stats.values())
            
            if total_repairs > 0:
                summary += f" (Lexer performed {total_repairs} repairs)"
        
        logger.info(summary)
        
        # Debug: Log each identity found
        for identity in valid_ids:
            logger.debug(
                f"  → {identity.api_version}/{identity.kind} "
                f"(name={identity.name or 'N/A'}, ns={identity.namespace or 'N/A'})"
            )

    def _reset_state(self) -> None:
        """Clears all state trackers to prepare for a fresh file scan."""
        self.identities = []
        self._current_identity = ManifestIdentity()
        self._path_stack = []
        self._in_global_metadata = False
        self._doc_index = 0
        self._lexer_context = None


# =============================================================================
# BACKWARD COMPATIBILITY ALIAS
# =============================================================================

# Namespaced Alias for Kubecuro compatibility
# Ensures the Chief Surgeon (pipeline.py) can call KubeScanner directly
KubeScanner = AkesoScanner
