"""
API version inference for Kubernetes resources.
Extracted from scanner.py to reduce complexity and improve maintainability.
"""
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class APIVersionInferrer:
    """
    Infers API versions for Kubernetes resources when not explicitly specified.
    
    Uses a three-tier strategy:
    1. Catalog lookup (most accurate)
    2. Common heuristics for well-known resources
    3. Safe fallback to None if unknown
    
    This is primarily used in Pro mode for intelligent manifest repair.
    """
    
    def __init__(
        self, 
        catalog: Dict[Any, Any],
        crd_catalog: Optional[Dict[Any, Any]] = None,
        plugin_catalogs: Optional[List[Dict[Any, Any]]] = None
    ):
        """
        Initialize inferrer with K8s API catalogs.
        
        Args:
            catalog: Primary K8s API schema catalog
            crd_catalog: Custom Resource Definition catalog (optional)
            plugin_catalogs: User-provided schema plugins (optional)
        """
        self.catalog = catalog
        self.crd_catalog = crd_catalog
        self.plugin_catalogs = plugin_catalogs or []
        logger.debug("APIVersionInferrer initialized")
    
    def infer_version(self, kind: str) -> Optional[str]:
        """
        Infers the most appropriate apiVersion for a given Kind.
        
        Strategy (in priority order):
        1. Check catalog for exact match (catalog-driven inference)
        2. Use hardcoded heuristics for common K8s resources
        3. Return None if kind is unknown (safe fallback)
        
        Args:
            kind: The Kubernetes Kind name
        
        Returns:
            Inferred apiVersion or None if unknown
        """
        # Strategy 1: Catalog-driven inference (most accurate)
        catalog_api = self.infer_from_catalog(kind)
        if catalog_api:
            logger.debug(f"Inferred apiVersion {catalog_api} for kind {kind} from catalog")
            return catalog_api
        
        # Strategy 2: Heuristic-driven inference (fallback for common kinds)
        heuristic_api = self.infer_from_heuristics(kind)
        if heuristic_api:
            logger.debug(f"Inferred apiVersion {heuristic_api} for kind {kind} from heuristics")
            return heuristic_api
        
        # Strategy 3: Unknown kind - cannot infer safely
        logger.debug(f"Cannot infer apiVersion for unknown kind {kind}")
        return None
    
    def infer_from_catalog(self, kind: str) -> Optional[str]:
        """
        Searches all catalogs for this kind and returns its apiVersion.
        
        Searches in order:
        1. Primary K8s catalog
        2. CRD catalog (if present)
        3. Plugin catalogs (if present)
        
        Args:
            kind: Kind name to search for
        
        Returns:
            apiVersion from catalog or None
        """
        # Check primary K8s catalog
        for key in self.catalog.keys():
            if isinstance(key, tuple) and len(key) == 2:
                api_version, catalog_kind = key
                if catalog_kind == kind:
                    return api_version
        
        # Check CRD catalog if present
        if self.crd_catalog:
            for key in self.crd_catalog.keys():
                if isinstance(key, tuple) and len(key) == 2:
                    api_version, catalog_kind = key
                    if catalog_kind == kind:
                        return api_version
        
        # Check plugin catalogs if present
        for plugin_catalog in self.plugin_catalogs:
            if isinstance(plugin_catalog, dict):
                for key in plugin_catalog.keys():
                    if isinstance(key, tuple) and len(key) == 2:
                        api_version, catalog_kind = key
                        if catalog_kind == kind:
                            return api_version
        
        return None
    
    def infer_from_heuristics(self, kind: str) -> Optional[str]:
        """
        Uses hardcoded heuristics for common Kubernetes kinds.
        
        This is a fallback when catalog lookup fails.
        Based on stable K8s API versions as of K8s 1.31+ (2026).
        
        Args:
            kind: Kind name
        
        Returns:
            Inferred apiVersion or None
        """
        # Core v1 resources
        core_v1_kinds = {
            "Pod", "Service", "ConfigMap", "Secret", "PersistentVolume",
            "PersistentVolumeClaim", "Namespace", "Node", "ServiceAccount",
            "Endpoints", "Event", "LimitRange", "ResourceQuota", "ReplicationController"
        }
        if kind in core_v1_kinds:
            return "v1"
        
        # apps/v1 resources
        apps_v1_kinds = {
            "Deployment", "StatefulSet", "DaemonSet", "ReplicaSet"
        }
        if kind in apps_v1_kinds:
            return "apps/v1"
        
        # batch resources
        if kind == "Job":
            return "batch/v1"
        if kind == "CronJob":
            return "batch/v1"  # v1 stable since K8s 1.21+
        
        # networking.k8s.io resources
        if kind == "Ingress":
            return "networking.k8s.io/v1"
        if kind == "NetworkPolicy":
            return "networking.k8s.io/v1"
        if kind == "IngressClass":
            return "networking.k8s.io/v1"
        
        # rbac.authorization.k8s.io resources
        rbac_kinds = {
            "Role", "RoleBinding", "ClusterRole", "ClusterRoleBinding"
        }
        if kind in rbac_kinds:
            return "rbac.authorization.k8s.io/v1"
        
        # autoscaling resources
        if kind == "HorizontalPodAutoscaler":
            return "autoscaling/v2"  # v2 is stable
        
        # policy resources
        if kind == "PodDisruptionBudget":
            return "policy/v1"
        if kind == "PodSecurityPolicy":
            return "policy/v1beta1"  # Deprecated but still exists
        
        # storage.k8s.io resources
        storage_kinds = {
            "StorageClass", "VolumeAttachment", "CSIDriver", "CSINode"
        }
        if kind in storage_kinds:
            return "storage.k8s.io/v1"
        
        # admissionregistration.k8s.io resources
        admission_kinds = {
            "ValidatingWebhookConfiguration",
            "MutatingWebhookConfiguration"
        }
        if kind in admission_kinds:
            return "admissionregistration.k8s.io/v1"
        
        # apiextensions.k8s.io resources
        if kind == "CustomResourceDefinition":
            return "apiextensions.k8s.io/v1"
        
        # certificates.k8s.io resources
        if kind == "CertificateSigningRequest":
            return "certificates.k8s.io/v1"
        
        # coordination.k8s.io resources
        if kind == "Lease":
            return "coordination.k8s.io/v1"
        
        # Unknown kind
        return None