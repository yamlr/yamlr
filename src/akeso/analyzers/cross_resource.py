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
import difflib
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
                
                # Intelligent Suggestion: Fuzzy Match for Typos
                # Scan all workloads for "almost matching" labels
                typo_candidates = self._find_typo_matches(service.selector, workloads)
                if typo_candidates:
                    best_match = typo_candidates[0] # Pick the best one
                    
                    # Format the suggestion nicely
                    diff_msg = []
                    for k, v in service.selector.items():
                        match_val = best_match['labels'].get(k)
                        if match_val and match_val != v:
                            diff_msg.append(f"'{k}: {match_val}'")
                        elif k not in best_match['labels']:
                             # Check for key typos
                             close_keys = [wk for wk in best_match['labels'] if difflib.SequenceMatcher(None, k, wk).ratio() > 0.8]
                             if close_keys:
                                 diff_msg.append(f"'{close_keys[0]}: {best_match['labels'][close_keys[0]]}'")

                    if diff_msg:
                        hint += f"\n\n    💡 Did you mean: {', '.join(diff_msg)}? (Found in {best_match['kind']}/{best_match['name']})"

                ghost_services.append({
                    "name": service.name,
                    "namespace": service.namespace or "default",
                    "hint": hint,
                    # We might need to map doc_index back to file_path if available in ManifestIdentity
                    "file_path": getattr(service, 'file_path', 'unknown') 
                })
        
        return ghost_services

    def _find_typo_matches(self, selector: Dict[str, str], workloads: List[ManifestIdentity]) -> List[Dict]:
        """Finds workloads that *almost* match the selector."""
        candidates = []
        
        # Helper to flatten dict to comparable strings
        def flatten(d): return sorted([f"{k}={v}" for k,v in d.items()])
        
        sel_str = str(flatten(selector))
        
        for workload in workloads:
            if not workload.labels: continue
            
            # 1. Direct value typo? (Keys match, values close)
            # Check overlap of keys first
            common_keys = set(selector.keys()) & set(workload.labels.keys())
            if len(common_keys) == len(selector):
                 # All keys exist, check value similarity
                 similarity = 0
                 for k in selector:
                     v1 = selector[k]
                     v2 = workload.labels[k]
                     similarity += difflib.SequenceMatcher(None, v1, v2).ratio()
                 
                 avg_sim = similarity / len(selector)
                 if avg_sim > 0.75 and avg_sim < 1.0: # 75% match on values
                     candidates.append({'name': workload.name, 'kind': workload.kind, 'score': avg_sim, 'labels': workload.labels})
                     continue

            # 2. General fuzzy match (e.g. key typo)
            # Compare the full label sets
            # We filter workload labels to only include relevant keys (fuzzy intersection) to avoid noise from extra labels
            
            # Simple approach: Textual similarity of the "selector part" only
            # Construct a virtual label set from workload that tries to match selector keys
            # (Too complex? Let's stick to simple sequence matching of flattened str)
            
            # FallbackRecalculate against full workload labels is noisy.
            # Let's try matching individual items.
            matches = 0
            for k, v in selector.items():
                # Is this k=v *almost* in workload?
                for wk, wv in workload.labels.items():
                    # Check string distance of "k=v"
                    if difflib.SequenceMatcher(None, f"{k}={v}", f"{wk}={wv}").ratio() > 0.85:
                        matches += 1
                        break
            
            if matches == len(selector): # Found a close match for EVERY selector item
                 # Ensure it's not an exact match (logic error check)
                 candidates.append({'name': workload.name, 'kind': workload.kind, 'score': 0.9, 'labels': workload.labels})

        return sorted(candidates, key=lambda x: x['score'], reverse=True)
    
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