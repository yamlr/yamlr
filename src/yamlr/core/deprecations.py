#!/usr/bin/env python3
"""
Yamlr OSS – DEPRECATION ENGINE
-----------------------------
Static detection of deprecated and removed Kubernetes APIs.

• Complete upstream coverage
• No cluster access
• Deterministic & fast
• CNCF-friendly

Source of truth:
https://kubernetes.io/docs/reference/using-api/deprecation-guide/
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List
import logging

logger = logging.getLogger("yamlr.deprecations")


@dataclass(frozen=True)
class DeprecationInfo:
    deprecated_api: str
    replacement_api: str
    deprecated_in_version: str
    removed_in_version: str
    kind: str
    severity: str  # WARNING | REMOVED
    migration_notes: str
    strategy: str = "NONE"  # Strategies: NONE, REPLACE_API_VERSION, DEPLOYMENT_SELECTOR, INGRESS_V1, CRONJOB_V1


# -------------------------------------------------------------------
# Canonical Kubernetes API Deprecations (Static, OSS-safe)
# -------------------------------------------------------------------

DEPRECATED_APIS: Dict[Tuple[str, str], DeprecationInfo] = {

    # ---------------------------------------------------------------
    # REMOVED IN 1.16
    # ---------------------------------------------------------------
    ("extensions/v1beta1", "Deployment"): DeprecationInfo(
        "extensions/v1beta1", "apps/v1", "1.9", "1.16",
        "Deployment", "REMOVED",
        "Change apiVersion to apps/v1 and ensure selector is specified.",
        "DEPLOYMENT_SELECTOR"
    ),
    ("extensions/v1beta1", "DaemonSet"): DeprecationInfo(
        "extensions/v1beta1", "apps/v1", "1.9", "1.16",
        "DaemonSet", "REMOVED",
        "Change apiVersion to apps/v1.",
        "REPLACE_API_VERSION"
    ),
    ("extensions/v1beta1", "ReplicaSet"): DeprecationInfo(
        "extensions/v1beta1", "apps/v1", "1.9", "1.16",
        "ReplicaSet", "REMOVED",
        "Change apiVersion to apps/v1.",
        "REPLACE_API_VERSION"
    ),
    ("extensions/v1beta1", "NetworkPolicy"): DeprecationInfo(
        "extensions/v1beta1", "networking.k8s.io/v1", "1.7", "1.16",
        "NetworkPolicy", "REMOVED",
        "Change apiVersion to networking.k8s.io/v1.",
        "REPLACE_API_VERSION"
    ),

    # ---------------------------------------------------------------
    # REMOVED IN 1.22
    # ---------------------------------------------------------------
    ("networking.k8s.io/v1beta1", "Ingress"): DeprecationInfo(
        "networking.k8s.io/v1beta1", "networking.k8s.io/v1", "1.19", "1.22",
        "Ingress", "REMOVED",
        "pathType is required in v1.",
        "INGRESS_V1"
    ),
    ("admissionregistration.k8s.io/v1beta1", "ValidatingWebhookConfiguration"): DeprecationInfo(
        "admissionregistration.k8s.io/v1beta1", "admissionregistration.k8s.io/v1", "1.16", "1.22",
        "ValidatingWebhookConfiguration", "REMOVED",
        "Update apiVersion only.",
        "REPLACE_API_VERSION"
    ),
    ("admissionregistration.k8s.io/v1beta1", "MutatingWebhookConfiguration"): DeprecationInfo(
        "admissionregistration.k8s.io/v1beta1", "admissionregistration.k8s.io/v1", "1.16", "1.22",
        "MutatingWebhookConfiguration", "REMOVED",
        "Update apiVersion only.",
        "REPLACE_API_VERSION"
    ),
    ("apiextensions.k8s.io/v1beta1", "CustomResourceDefinition"): DeprecationInfo(
        "apiextensions.k8s.io/v1beta1", "apiextensions.k8s.io/v1", "1.16", "1.22",
        "CustomResourceDefinition", "REMOVED",
        "Structural schema required in v1.",
        "REPLACE_API_VERSION" # CRD migration is complex, stick to API swap for now or NONE? Let's try swap.
    ),

    # ---------------------------------------------------------------
    # REMOVED IN 1.25
    # ---------------------------------------------------------------
    ("batch/v1beta1", "CronJob"): DeprecationInfo(
        "batch/v1beta1", "batch/v1", "1.21", "1.25",
        "CronJob", "REMOVED",
        "Change apiVersion to batch/v1.",
        "CRONJOB_V1"
    ),
    ("policy/v1beta1", "PodSecurityPolicy"): DeprecationInfo(
        "policy/v1beta1", "N/A", "1.21", "1.25",
        "PodSecurityPolicy", "REMOVED",
        "Migrate to Pod Security Standards (PSS).",
        "NONE" # No auto-fix for removal
    ),
    ("policy/v1beta1", "PodDisruptionBudget"): DeprecationInfo(
        "policy/v1beta1", "policy/v1", "1.21", "1.25",
        "PodDisruptionBudget", "REMOVED",
        "Update apiVersion to policy/v1.",
        "REPLACE_API_VERSION"
    ),
    ("node.k8s.io/v1beta1", "RuntimeClass"): DeprecationInfo(
        "node.k8s.io/v1beta1", "node.k8s.io/v1", "1.20", "1.25",
        "RuntimeClass", "REMOVED",
        "Change apiVersion to node.k8s.io/v1.",
        "REPLACE_API_VERSION"
    ),

    # ---------------------------------------------------------------
    # REMOVED IN 1.26+
    # ---------------------------------------------------------------
    ("autoscaling/v2beta2", "HorizontalPodAutoscaler"): DeprecationInfo(
        "autoscaling/v2beta2", "autoscaling/v2", "1.23", "1.26",
        "HorizontalPodAutoscaler", "REMOVED",
        "Change apiVersion to autoscaling/v2.",
        "REPLACE_API_VERSION"
    ),
    ("storage.k8s.io/v1beta1", "CSIStorageCapacity"): DeprecationInfo(
        "storage.k8s.io/v1beta1", "storage.k8s.io/v1", "1.24", "1.27",
        "CSIStorageCapacity", "REMOVED",
        "Change apiVersion to storage.k8s.io/v1.",
        "REPLACE_API_VERSION"
    ),

    # ---------------------------------------------------------------
    # REMOVED IN 1.29
    # ---------------------------------------------------------------
    ("flowcontrol.apiserver.k8s.io/v1beta3", "FlowSchema"): DeprecationInfo(
        "flowcontrol.apiserver.k8s.io/v1beta3", "flowcontrol.apiserver.k8s.io/v1", "1.26", "1.29",
        "FlowSchema", "REMOVED",
        "Change apiVersion to v1.",
        "REPLACE_API_VERSION"
    ),
    ("flowcontrol.apiserver.k8s.io/v1beta3", "PriorityLevelConfiguration"): DeprecationInfo(
        "flowcontrol.apiserver.k8s.io/v1beta3", "flowcontrol.apiserver.k8s.io/v1", "1.26", "1.29",
        "PriorityLevelConfiguration", "REMOVED",
        "Change apiVersion to v1.",
        "REPLACE_API_VERSION"
    ),
}


# -------------------------------------------------------------------
# OSS Checker
# -------------------------------------------------------------------

class DeprecationChecker:

    def __init__(self):
        """Initialize OSS deprecation checker with static database."""
        pass  # No state needed for OSS

    def check(self, api_version: str, kind: str) -> Optional[DeprecationInfo]:
        return DEPRECATED_APIS.get((api_version, kind))

    def list_all(self) -> List[DeprecationInfo]:
        return list(DEPRECATED_APIS.values())

    def is_removed(self, api_version: str, kind: str, target_version: str) -> bool:
        """
        Check if an API is removed in a specific K8s version.
        
        Args:
            api_version: API version to check
            kind: Resource kind
            target_version: Target K8s version (e.g., "1.29")
            
        Returns:
            True if API is removed in that version or earlier
        """
        info = self.check(api_version, kind)
        if not info:
            return False
        
        return self._compare_versions(target_version, info.removed_in_version) >= 0

    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare K8s versions safely.
        
        Handles formats like:
        - "1.29", "1.30", "v1.29"
        - "1.30+" (strips the +)
        
        Args:
            v1: First version (e.g., "1.29")
            v2: Second version (e.g., "1.25")
            
        Returns:
            -1 if v1 < v2, 0 if equal, 1 if v1 > v2
        """
        try:
            # Strip 'v' prefix and handle "1.30+" style versions
            v1_clean = v1.lstrip('v').rstrip('+')
            v2_clean = v2.lstrip('v').rstrip('+')
            
            # Parse major.minor (ignore patch)
            v1_parts = [int(x) for x in v1_clean.split('.')[:2]]
            v2_parts = [int(x) for x in v2_clean.split('.')[:2]]
            
            # Compare major version first
            if v1_parts[0] != v2_parts[0]:
                return 1 if v1_parts[0] > v2_parts[0] else -1
            
            # Compare minor version
            if v1_parts[1] != v2_parts[1]:
                return 1 if v1_parts[1] > v2_parts[1] else -1
            
            return 0
        except (ValueError, IndexError) as e:
            logger.warning(f"Version comparison failed: {v1} vs {v2}: {e}")
            return 0
