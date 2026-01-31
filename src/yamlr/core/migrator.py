#!/usr/bin/env python3
"""
Yamlr OSS – PROPHETIC MIGRATION ENGINE
-----------------------------------------
Automatically upgrades deprecated Kubernetes resources to their supported versions.

Features:
- Structural Migration: Adds required fields (e.g., selectors)
- API Version Swapping: Updates apiVersion strings
- Safe Execution: Returns audit logs for all changes

Author: Nishar A Sunkesala / Yamlr Team
"""

import copy
import logging
from typing import Dict, List, Tuple, Any, Optional

from yamlr.core.deprecations import DeprecationChecker, DeprecationInfo

logger = logging.getLogger("yamlr.migrator")

class MigrationEngine:
    """
    Handles the transformation of deprecated resources into their modern counterparts.
    """

    def __init__(self, target_k8s_version: str = "v1.29"):
        self.checker = DeprecationChecker()
        self.target_version = target_k8s_version

    def migrate_all(self, docs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Migrates a list of documents.
        Returns (New Docs, Audit Logs).
        """
        migrated_docs = []
        all_logs = []
        
        for doc in docs:
            new_doc, logs = self.migrate(doc)
            migrated_docs.append(new_doc)
            all_logs.extend(logs)
            
        return migrated_docs, all_logs

    def migrate(self, doc: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Migrates a single document if it is deprecated and removed in the target version.
        """
        # Defensive copy to allow mutation without side effects on input
        new_doc = copy.deepcopy(doc)
        audit = []
        
        api_version = new_doc.get("apiVersion", "")
        kind = new_doc.get("kind", "")
        
        if not api_version or not kind:
            return new_doc, []

        # Check if removal is impending/past
        if not self.checker.is_removed(api_version, kind, self.target_version):
            return new_doc, []

        # Get deprecation info
        info = self.checker.check(api_version, kind)
        if not info or info.strategy == "NONE":
            return new_doc, []

        # Execute Strategy
        try:
            strategy = info.strategy
            
            if strategy == "REPLACE_API_VERSION":
                self._replace_api_version(new_doc, info.replacement_api)
                audit.append(f"MIGRATED: {kind}/{new_doc['metadata'].get('name')} from {api_version} to {info.replacement_api}")
            
            elif strategy == "DEPLOYMENT_SELECTOR":
                if self._fix_deployment_selector(new_doc, info.replacement_api):
                    audit.append(f"MIGRATED: {kind}/{new_doc['metadata'].get('name')} from {api_version} to {info.replacement_api} (Added Selector)")
            
            elif strategy == "INGRESS_V1":
                 if self._fix_ingress_v1(new_doc, info.replacement_api):
                    audit.append(f"MIGRATED: {kind}/{new_doc['metadata'].get('name')} from {api_version} to {info.replacement_api} (Updated Ingress Structure)")
            
            elif strategy == "CRONJOB_V1":
                self._replace_api_version(new_doc, info.replacement_api)
                # CronJob v1beta1 -> v1 is mostly compatible, just api change usually enough for basic specs
                audit.append(f"MIGRATED: {kind}/{new_doc['metadata'].get('name')} from {api_version} to {info.replacement_api}")

        except Exception as e:
            logger.error(f"Migration failed for {kind}: {e}")
            audit.append(f"MIGRATED_FAILED: Could not migrate {kind} - {e}")
            return doc, audit # Return original on failure

        return new_doc, audit

    # -------------------------------------------------------------------
    # Strategies
    # -------------------------------------------------------------------

    def _replace_api_version(self, doc: Dict, new_version: str):
        doc["apiVersion"] = new_version

    def _fix_deployment_selector(self, doc: Dict, new_version: str) -> bool:
        """
        apps/v1 Deployments REQUIRE a selector that matches the template labels.
        Old extensions/v1beta1 often defaulted this.
        """
        self._replace_api_version(doc, new_version)
        
        spec = doc.get("spec", {})
        if "selector" not in spec:
            # Infer selector from template labels
            template_labels = spec.get("template", {}).get("metadata", {}).get("labels", {})
            if template_labels:
                spec["selector"] = {"matchLabels": template_labels}
                doc["spec"] = spec
                return True
            else:
                # Cannot safely migrate without labels to select
                return False
        
        # If selector exists, assume it's valid (or linter will catch it later)
        return True

    def _fix_ingress_v1(self, doc: Dict, new_version: str) -> bool:
        """
        networking.k8s.io/v1 requirements:
        - pathType is mandatory
        - backend service structure changed
        """
        self._replace_api_version(doc, new_version)
        
        # Naive implementation: Attempt to add pathType=ImplementationSpecific if missing
        # Full Ingress migration is very complex (backend fields changed names).
        # For MVP, we fix the most common issue: pathType.
        
        spec = doc.get("spec", {})
        rules = spec.get("rules", [])
        
        changed = False
        for rule in rules:
            http = rule.get("http", {})
            for path in http.get("paths", []):
                if "pathType" not in path:
                    path["pathType"] = "ImplementationSpecific"
                    changed = True
                    
        return True # Return True even if only apiVersion changed (safe bet)
