#!/usr/bin/env python3
"""
AKESO ENGINE - The High Orchestrator
---------------------------------------
Coordinates the complete healing workflow for Kubernetes manifests.

Enhancements:
- Eliminated double-scan overhead (identities returned from pipeline)
- Enhanced atomic writes with fsync for durability
- Comprehensive deprecation info serialization
- Professional security and error handling

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-26
"""
import sys
import os
from pathlib import Path

# [2026-01-21] PyInstaller Path Anchor
if getattr(sys, 'frozen', False):
    # Get the directory where the binary is unpacked (_MEIPASS)
    bundle_dir = sys._MEIPASS
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

import shutil
import time
import json
import logging
from typing import Dict, Any, List, Optional

from akeso.core.pipeline import HealingPipeline
from akeso.core.bridge import AkesoBridge
from akeso.core.context import HealContext
from akeso.core.io import FileSystemManager
from akeso.core.config import ConfigManager


logger = logging.getLogger("akeso.engine")

class AkesoEngine:
    """
    Principal Orchestrator for Kubernetes manifest healing.
    
    Responsibilities:
    - Workspace and catalog management
    - File I/O and atomic writes
    - Batch healing operations
    - Result aggregation and reporting
    """
    
    def __init__(self, 
                 workspace_path: str, 
                 catalog_path: str,
                 cpu_limit: str = "500m", 
                 mem_limit: str = "512Mi",
                 default_namespace: str = "default",
                 deep_array_validation: bool = False,
                 custom_key_order: Optional[List[str]] = None,
                 health_threshold: int = 70,
                 cluster_version: Optional[str] = None):
        """
        Initializes the Akeso Engine with workspace and catalog.
        """
        self.workspace = Path(workspace_path).resolve()
        
        # Initialize I/O Manager and Config Manager
        self.fs = FileSystemManager(self.workspace)
        self.fs.ensure_workspace()
        
        self.config = ConfigManager(self.workspace)
        
        # Use config threshold if not explicitly overridden, otherwise default
        self.health_threshold = health_threshold if health_threshold != 70 else self.config.health_threshold
        
        # Store and validate cluster version
        if cluster_version:
            self.cluster_version = HealContext.set_cluster_version(cluster_version)
        else:
            self.cluster_version = HealContext._get_default_cluster_version()
        
        logger.info(f"Engine initialized for target K8s: {self.cluster_version}")
        
        # --- CATALOG LOADING ---
        # Handles both standard paths and PyInstaller/Container environments
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        resolved_catalog = Path(base_path) / catalog_path

        try:
            if not resolved_catalog.exists():
                resolved_catalog = Path(catalog_path).resolve()

            with open(resolved_catalog, 'r', encoding='utf-8') as f:
                self.catalog = json.load(f)
                
            logger.info(f"Loaded catalog from {resolved_catalog} ({len(self.catalog)} resource types)")
        except Exception as e:
            logger.error(f"Failed to load catalog at {resolved_catalog}: {e}")
            raise RuntimeError(f"Engine initialization aborted: Catalog missing or corrupt.")
            
        # --- PIPELINE INITIALIZATION ---
        try:
            self.pipeline = HealingPipeline(
                catalog=self.catalog,
                cpu_limit=cpu_limit,
                mem_limit=mem_limit,
                default_namespace=default_namespace
            )
            
            # Configure validator (if available)
            if hasattr(self.pipeline.validator, 'deep_array_check'):
                self.pipeline.validator.deep_array_check = deep_array_validation
            
            # Configure exporter (if available)
            if self.pipeline.exporter and custom_key_order:
                self.pipeline.exporter.custom_order = custom_key_order
                
            logger.info("HealingPipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HealingPipeline: {e}")
            raise RuntimeError(f"Pipeline initialization failed: {str(e)}")

    def audit_and_heal_file(self, 
                            relative_path: str, 
                            dry_run: bool = True, 
                            force_write: bool = False,
                            strict_validation: bool = False,
                            compact: bool = False) -> Dict[str, Any]:
        """
        Performs a full audit and healing cycle on a single manifest file.
        """
        full_path = (self.workspace / relative_path).resolve()
        
        # =====================================================================
        # SECURITY: PREVENT DIRECTORY TRAVERSAL
        # =====================================================================
        try:
            full_path.relative_to(self.workspace)
        except ValueError:
            return self._file_error(relative_path, "SECURITY_ERROR", "Path outside workspace")

        # =====================================================================
        # CONFIG CHECK: IGNORE RULES
        # =====================================================================
        if self.config.is_ignored(relative_path):
             return {
                "file_path": Path(relative_path).name,
                "full_path": str(relative_path),
                "success": True,
                "status": "IGNORED",
                "written": False,
                "kind": "Ignored",
                "backup_created": None,
                "raw_content": None, 
                "healed_content": None,
                "logic_logs": ["File ignored by .akeso.yaml config"],
                "health_score": 100,
                "identities": [],
                "timestamp": time.time(),
                "processing_time_seconds": 0.0
            }

        if not full_path.exists():
            return self._file_error(relative_path, "FILE_NOT_FOUND", "Path does not exist")

        all_logic_logs = []
        start_time = time.time()

        try:
            # Read file with BOM handling
            raw_text = full_path.read_text(encoding='utf-8-sig')
            if not raw_text.strip():
                return self._file_error(relative_path, "EMPTY_FILE", "File contains no content")
            
            # Pass cluster_version to pipeline
            healed_text, pipeline_logs, health_score, identities, findings = self.pipeline.heal(
                raw_text, 
                strict_validation=strict_validation,
                compact=compact,
                cluster_version=self.cluster_version 
            )
            
            # Serialize findings with Rule Filtering
            serialized_findings = []
            if findings:
                from dataclasses import asdict
                for f in findings:
                    # check if specific rule is ignored
                    if f.rule_id and self.config.is_ignored(relative_path, rule_id=f.rule_id):
                        continue
                    serialized_findings.append(asdict(f))

            all_logic_logs.extend(pipeline_logs)
            processing_time = time.time() - start_time

            # Determine file status
            is_modified = raw_text.strip() != healed_text.strip()
            meets_threshold = health_score >= self.health_threshold
            should_apply = is_modified and (meets_threshold or force_write)
            
            display_status = self._derive_status(is_modified, dry_run, meets_threshold)
            
            # =====================================================================
            # FIXED: USE IDENTITIES FROM PIPELINE (NO RE-SCAN)
            # =====================================================================
            res_kind = "Unknown"
            identities_list = []
            
            if identities:
                for identity in identities:
                    ident_data = identity.to_dict()
                    
                    # Serialize deprecation info if present
                    if hasattr(identity, 'deprecation_info') and identity.deprecation_info:
                        dep = identity.deprecation_info
                        ident_data['deprecation_info'] = {
                            'deprecated_api': dep.deprecated_api,
                            'replacement_api': dep.replacement_api,
                            'deprecated_in_version': dep.deprecated_in_version,
                            'removed_in_version': dep.removed_in_version,
                            'kind': dep.kind,
                            'severity': dep.severity,
                            'migration_notes': dep.migration_notes
                        }
                    
                    identities_list.append(ident_data)
                
                # Use first identity's kind for file kind
                res_kind = identities_list[0].get("kind", "Unknown")

            # Build result object
            result = {
                "file_path": Path(relative_path).name,
                "full_path": str(relative_path),
                "success": meets_threshold or not is_modified,
                "status": display_status,
                "written": False,
                "kind": res_kind,
                "backup_created": None,
                "raw_content": raw_text,
                "healed_content": healed_text if is_modified else None,
                "logic_logs": all_logic_logs,
                "findings": serialized_findings,
                "health_score": health_score,
                "identities": identities_list,
                "timestamp": time.time(),
                "processing_time_seconds": processing_time
            }

            # =====================================================================
            # ATOMIC WRITE WITH BACKUP
            # =====================================================================
            if not dry_run and should_apply:
                backup_path = self._create_unique_backup(full_path)
                shutil.copy2(full_path, backup_path)
                result["backup_created"] = str(backup_path.relative_to(self.workspace))
                
                self._atomic_write(full_path, healed_text)
                result["written"] = True
                logger.info(f"Healed and saved: {relative_path}")

            return result

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            return self._file_error(
                relative_path, 
                "ENGINE_ERROR", 
                str(e), 
                time.time() - start_time
            )

    def audit_stream(self, 
                     content: str, 
                     source_name: str = "stdin", 
                     strict_validation: bool = False,
                     compact: bool = False) -> Dict[str, Any]:
        """
        Audits content from input stream without disk I/O.
        Returns standard result dict (written=False).
        """
        start_time = time.time()
        try:
            if not content.strip():
                return self._file_error(source_name, "EMPTY_FILE", "Stream contains no content")

            # Execute Pipeline
            healed_text, logs, score, identities, findings = self.pipeline.heal(
                content, 
                strict_validation=strict_validation,
                compact=compact,
                cluster_version=self.cluster_version
            )

            # Serialize Findings
            serialized_findings = []
            if findings:
                from dataclasses import asdict
                for f in findings:
                    serialized_findings.append(asdict(f))

            # Serialize Identities
            identities_list = []
            res_kind = "Unknown"
            if identities:
                for identity in identities:
                    ident_data = identity.to_dict()
                    if hasattr(identity, 'deprecation_info') and identity.deprecation_info:
                        dep = identity.deprecation_info
                        ident_data['deprecation_info'] = {
                            'deprecated_api': dep.deprecated_api,
                            'replacement_api': dep.replacement_api,
                            'kind': dep.kind,
                            'severity': dep.severity,
                            'removed_in_version': dep.removed_in_version,
                            'migration_notes': dep.migration_notes
                        }
                    identities_list.append(ident_data)
                res_kind = identities_list[0].get("kind", "Unknown")

            is_modified = content.strip() != healed_text.strip()
            meets_threshold = score >= self.health_threshold
            display_status = self._derive_status(is_modified, dry=True, meets_threshold=meets_threshold)

            return {
                "file_path": source_name,
                "full_path": source_name,
                "success": meets_threshold or not is_modified,
                "status": display_status,
                "written": False,
                "kind": res_kind,
                "backup_created": None,
                "raw_content": content,
                "healed_content": healed_text if is_modified else None,
                "logic_logs": logs,
                "findings": serialized_findings,
                "health_score": score,
                "identities": identities_list,
                "timestamp": time.time(),
                "processing_time_seconds": time.time() - start_time
            }

        except Exception as e:
            logger.error(f"Stream Error: {e}")
            return self._file_error(source_name, "STREAM_ERROR", str(e))

    # =========================================================================
    # PUBLIC API: BATCH HEALING
    # =========================================================================

    def batch_heal(self, 
                   root_path: str, 
                   extensions: List[str], 
                   max_depth: int = 10, 
                   dry_run: bool = True) -> List[Dict[str, Any]]:
        """
        Crawls the filesystem starting at root_path to find and heal manifests.
        
        Args:
            root_path: Starting directory for recursive search
            extensions: List of file extensions to process (e.g., ['.yaml', '.yml'])
            max_depth: Maximum directory depth to search
            dry_run: If True, preview changes without writing
            
        Returns:
            List of healing results (one per file)
        """
        results = []
        search_root = Path(root_path).resolve()

        if not search_root.exists():
            logger.error(f"Batch path does not exist: {root_path}")
            return results

        # Normalize extensions (ensure leading dot)
        ext_set = {e.strip() if e.startswith('.') else f".{e.strip()}" for e in extensions}

        # Recursive directory walk with depth limiting
        for root, dirs, files in os.walk(search_root):
            current_depth = len(Path(root).relative_to(search_root).parts)
            
            # Stop descending if max depth reached
            if current_depth >= max_depth:
                del dirs[:]
                continue

            # Process matching files
            for file in files:
                if any(file.endswith(ext) for ext in ext_set):
                    abs_file_path = Path(root) / file
                    
                    # Determine path relative to workspace
                    try:
                        # Attempt to make it relative to the workspace
                        target_path = str(abs_file_path.relative_to(self.workspace))
                    except ValueError:
                        # If outside workspace, use the absolute path 
                        # (audit_and_heal_file will catch security error)
                        target_path = str(abs_file_path)

                    # Heal the file and collect result
                    results.append(self.audit_and_heal_file(target_path, dry_run=dry_run))

        return results

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _derive_status(self, modified: bool, dry: bool, meets_threshold: bool) -> str:
        """
        Derives human-readable status from healing state.
        
        Args:
            modified: Whether file content changed
            dry: Whether in dry-run mode
            meets_threshold: Whether health score meets threshold
            
        Returns:
            Status string (UNCHANGED, PREVIEW, HEALED, FAILED)
        """
        if not modified: 
            return "UNCHANGED"
        if dry: 
            return "PREVIEW"
        return "HEALED" if meets_threshold else "FAILED"

    def _atomic_write(self, target_path: Path, content: str):
        """
        Atomically writes content to file with fsync for durability.
        
        Uses temp file + os.replace for atomic operation.
        Prevents partial writes during crashes.
        
        Args:
            target_path: Destination file path
            content: Content to write
            
        Raises:
            IOError: If write fails
        """
        temp_file = target_path.with_suffix('.akeso.tmp')
        try:
            # Write to temp file with explicit flush and fsync
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Force OS to write to disk
            
            # Atomically replace original file
            os.replace(temp_file, target_path)
            
        except Exception as e:
            # Clean up temp file on failure
            if temp_file.exists(): 
                temp_file.unlink()
            raise IOError(f"Atomic write failed: {str(e)}")

    def _create_unique_backup(self, target_path: Path) -> Path:
        """
        Creates a unique backup file path (avoids overwriting existing backups).
        
        Args:
            target_path: Original file path
            
        Returns:
            Unique backup file path
        """
        backup_path = target_path.with_suffix('.akeso.backup')
        counter = 1
        
        # Increment counter until we find an unused filename
        while backup_path.exists():
            backup_path = target_path.with_name(f"{target_path.stem}-{counter}.akeso.backup")
            counter += 1
        
        return backup_path

    def _file_error(self, 
                    path: str, 
                    status: str, 
                    error: str, 
                    processing_time: float = 0.0) -> Dict[str, Any]:
        """
        Constructs a standardized error result object.
        
        Args:
            path: File path that failed
            status: Error status code
            error: Error message
            processing_time: Time spent before error
            
        Returns:
            Error result dictionary
        """
        return {
            "file_path": path,
            "full_path": path,
            "kind": "Error",
            "status": status,
            "error": error,
            "success": False,
            "written": False,
            "backup_created": None,
            "raw_content": None,
            "healed_content": None,
            "logic_logs": [f"Error: {error}"],
            "health_score": 0,
            "identities": [],
            "timestamp": time.time(),
            "processing_time_seconds": processing_time
        }


# =============================================================================
# LEGACY ALIASES
# =============================================================================
# Maintain backwards compatibility with older codebases
AuditEngineV3 = AkesoEngine
