#!/usr/bin/env python3
"""
AKESO CROSS-RESOURCE ANALYZER
------------------------------
Validates relationships between Kubernetes resources to detect
configuration issues that kubectl and the API server cannot catch.

Features:
- Ghost Service Detection: Services with selectors that match no Pods
- Orphan ConfigMap/Secret Detection: Unused configuration resources
- Broken Volume References: Missing PVCs in Pod specs

Metadata:
    - Component: Analyzer Plugin (Core)
    - Author: Nishar A Sunkesala / Akeso Team
    - License: Apache 2.0
"""

import logging
from typing import List, Dict, Any
from akeso.models import ManifestIdentity
from akeso.analyzers.base import BaseAnalyzer, AnalysisResult
from akeso.analyzers.registry import register_analyzer
from akeso.core.bridge import AkesoBridge

logger = logging.getLogger("akeso.analyzer.cross_resource")

@register_analyzer
class CrossResourceAnalyzer(BaseAnalyzer):
    """
    Analyzes relationships between Kubernetes resources.
    
    This is a critical production feature that catches configuration
    issues before they reach the cluster.
    """

    def __init__(self, pro_mode: bool = False):
        # Allow override, but default to checking Bridge
        if pro_mode:
            self.pro_mode = True
        else:
            try:
                self.pro_mode = AkesoBridge.is_pro_enabled()
            except ImportError:
                self.pro_mode = False
        # We don't need self.warnings/errors list as state anymore, 
        # but we can keep them if we want to log incrementally. 
        # For the plugin interface, we return results at the end.

    @property
    def name(self) -> str:
        return "cross-resource-analyzer"

    def analyze(self, identities: List[ManifestIdentity]) -> List[AnalysisResult]:
        """
        Performs comprehensive cross-resource analysis.
        
        Returns:
            List of AnalysisResult objects detailing findings.
        """
        results: List[AnalysisResult] = []
        
        # Build resource indexes by type
        services = [i for i in identities if i.kind == "Service"]
        workloads = [i for i in identities if i.kind in ("Deployment", "StatefulSet", "DaemonSet", "Pod")]
        configs = [i for i in identities if i.kind in ("ConfigMap", "Secret")]
        pvcs = [i for i in identities if i.kind == "PersistentVolumeClaim"]
        
        # Run detection algorithms
        ghost_services = self._detect_ghost_services(services, workloads)
        orphan_configs = self._detect_orphan_configs(configs, workloads)
        broken_volumes = self._detect_broken_volumes(workloads, pvcs)
        
        # Convert detector outputs to standardized AnalysisResult objects
        
        for ghost in ghost_services:
            results.append(AnalysisResult(
                analyzer_name=self.name,
                severity="WARNING",
                message=f"Ghost Service detected: selector matches no Pods.",
                resource_name=ghost["name"],
                resource_kind="Service",
                file_path=ghost.get("file_path", "unknown"), # Assuming ManifestIdentity has file_path, need to verify or handle
                suggestion=ghost.get("hint"),
                fix_available=False # Future Pro feature
            ))

        for orphan in orphan_configs:
            results.append(AnalysisResult(
                analyzer_name=self.name,
                severity="WARNING",
                message=f"Orphan {orphan['kind']} detected: not referenced by any workload.",
                resource_name=orphan["name"],
                resource_kind=orphan["kind"],
                file_path=orphan.get("file_path", "unknown"),
                suggestion="Remove if unused, or add a reference in a Pod spec.",
                fix_available=False
            ))

        for broken in broken_volumes:
            results.append(AnalysisResult(
                analyzer_name=self.name,
                severity="ERROR",
                message=f"Broken Volume: references missing PVC '{broken['missing_pvc']}'.",
                resource_name=broken["workload_name"],
                resource_kind=broken["workload_kind"],
                file_path=broken.get("file_path", "unknown"),
                suggestion=f"Ensure PVC '{broken['missing_pvc']}' exists in namespace '{broken['namespace']}'.",
                fix_available=False
            ))

        # Log summary (keeping existing logging behavior for transparency)
        # Log summary (keeping existing logging behavior for transparency)
        if results:
            logger.info(f"Cross-resource analysis found {len(results)} issues.")
        else:
            logger.info("Cross-resource analysis: No issues detected ✓")

        return results
    
    # -------------------------------------------------------------
    # Detection Logic (Preserved verbatim from original)
    # -------------------------------------------------------------

    def _detect_ghost_services(
        self, 
        services: List[ManifestIdentity], 
        workloads: List[ManifestIdentity]
    ) -> List[Dict]:
        """Detects Services with selectors that match no Pods."""
        ghost_services = []
        
        for service in services:
            if not service.selector:
                continue

            matching_workloads = []
            for workload in workloads:
                service_ns = service.namespace or "default"
                workload_ns = workload.namespace or "default"
                
                if service_ns == workload_ns:
                    if workload.labels and self._labels_match(service.selector, workload.labels):
                        matching_workloads.append(workload.name)
            
            if not matching_workloads:
                # Ghost service detected!
                hint = self._generate_ghost_service_hint(service)
                ghost_services.append({
                    "name": service.name,
                    "namespace": service.namespace or "default",
                    "hint": hint,
                    # We might need to map doc_index back to file_path if available in ManifestIdentity
                    "file_path": getattr(service, 'file_path', 'unknown') 
                })
        
        return ghost_services
    
    def _detect_orphan_configs(
        self,
        configs: List[ManifestIdentity],
        workloads: List[ManifestIdentity]
    ) -> List[Dict]:
        """Detects ConfigMaps/Secrets that no Pod references."""
        orphan_configs = []
        
        for config in configs:
            referencing_workloads = []
            for workload in workloads:
                if config.name in workload.config_refs:
                    referencing_workloads.append(workload.name)
            
            if not referencing_workloads:
                orphan_configs.append({
                    "kind": config.kind,
                    "name": config.name,
                    "namespace": config.namespace or "default",
                    "file_path": getattr(config, 'file_path', 'unknown')
                })
        
        return orphan_configs
    
    def _detect_broken_volumes(
        self,
        workloads: List[ManifestIdentity],
        pvcs: List[ManifestIdentity]
    ) -> List[Dict]:
        """Detects workloads referencing non-existent PVCs."""
        broken_volumes = []
        pvc_names = {pvc.name for pvc in pvcs}
        
        for workload in workloads:
            for pvc_ref in workload.volume_refs:
                if pvc_ref not in pvc_names:
                    broken_volumes.append({
                        "workload_kind": workload.kind,
                        "workload_name": workload.name,
                        "missing_pvc": pvc_ref,
                        "namespace": workload.namespace or "default",
                        "file_path": getattr(workload, 'file_path', 'unknown')
                    })
        
        return broken_volumes
    
    def _labels_match(self, selector: Dict[str, str], labels: Dict[str, str]) -> bool:
        """Checks if a selector matches a set of labels."""
        for key, value in selector.items():
            if labels.get(key) != value:
                return False
        return True
    
    def _generate_ghost_service_hint(self, service: ManifestIdentity) -> str:
        """Generates an actionable hint for fixing a ghost service."""
        selector_yaml = "\n        ".join(
            f"{k}: {v}" for k, v in service.selector.items()
        )
        
        hint = (
            f"Add a Deployment with matching labels:\n"
            f"    spec:\n"
            f"      template:\n"
            f"        metadata:\n"
            f"          labels:\n"
            f"            {selector_yaml}"
        )
        
        if self.pro_mode:
            hint += "\n    (Pro mode will auto-generate this in future release)"
        
        return hint

# Backward compatibility alias - in case it's imported elsewhere as a class explicitly
KubeCrossResourceAnalyzer = CrossResourceAnalyzer