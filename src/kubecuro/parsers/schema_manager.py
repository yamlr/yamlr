"""
Schema catalog management for Kubernetes resources.
Extracted from scanner.py to improve maintainability.
"""
from typing import Dict, Set, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class SchemaManager:
    """
    Manages K8s schema catalogs and validation.
    
    Responsibilities:
    - Load and organize schema catalogs
    - Build known structure keys
    - Check schema availability
    - Support multiple schema sources (K8s, OpenAPI, CRDs, plugins)
    """
    
    def __init__(
        self,
        catalog: Optional[Dict[Any, Any]] = None,
        openapi_catalog: Optional[Dict[Any, Any]] = None,
        crd_catalog: Optional[Dict[Any, Any]] = None,
        plugin_catalogs: Optional[List[Dict[Any, Any]]] = None
    ):
        """
        Initialize schema manager with multiple catalog sources.
        
        Args:
            catalog: Primary K8s API schema catalog
            openapi_catalog: OpenAPI 3.0 schema definitions (optional)
            crd_catalog: Custom Resource Definition catalog (optional)
            plugin_catalogs: User-provided schema plugins (optional)
        """
        self.catalog = catalog or {}
        self.openapi_catalog = openapi_catalog
        self.crd_catalog = crd_catalog
        self.plugin_catalogs = plugin_catalogs or []
        
        # Build comprehensive structure keys from all sources
        self.known_structure_keys = self._build_structure_keys()
        
        logger.debug(
            f"SchemaManager initialized with {len(self.known_structure_keys)} "
            f"structure keys from {self._count_catalog_sources()} source(s)"
        )
    
    def _count_catalog_sources(self) -> int:
        """Count number of active catalog sources."""
        count = 1  # Primary catalog always counts
        if self.openapi_catalog:
            count += 1
        if self.crd_catalog:
            count += 1
        count += len(self.plugin_catalogs)
        return count
    
    def _build_structure_keys(self) -> Set[str]:
        """
        Builds a comprehensive set of known structure keys from all schema sources.
        
        This is the core of the scanner's intelligence - it knows what fields are 
        important by combining knowledge from multiple sources:
        1. Core K8s fields (hardcoded, always valid)
        2. Common nested fields (containers, volumes, etc.)
        3. K8s catalog-derived fields (from schema definitions)
        4. OpenAPI catalog-derived fields (future expansion)
        5. CRD catalog-derived fields (custom resources)
        6. Plugin catalog-derived fields (user extensions)
        
        Returns:
            Set of all recognized structural keys across all schema types
        """
        # Core K8s fields - these are ALWAYS valid for Kubernetes manifests
        core_keys = {
            "apiVersion", "kind", "metadata", "spec", "status", "data",
            "name", "namespace", "labels", "annotations", "finalizers",
            "ownerReferences", "resourceVersion", "generation", "uid",
            "creationTimestamp", "deletionTimestamp"
        }
        
        # Nested keys - these appear frequently in specs
        nested_keys = {
            # Container-related
            "containers", "initContainers", "ephemeralContainers",
            "image", "imagePullPolicy", "imagePullSecrets",
            "command", "args", "workingDir",
            "ports", "containerPort", "hostPort", "protocol",
            "env", "envFrom", "valueFrom",
            
            # Volume-related
            "volumes", "volumeMounts", "volumeDevices",
            "mountPath", "subPath", "readOnly",
            "configMap", "secret", "persistentVolumeClaim",
            "emptyDir", "hostPath", "nfs", "csi",
            
            # Resource management
            "resources", "limits", "requests",
            "cpu", "memory", "storage", "ephemeral-storage",
            
            # Networking
            "service", "clusterIP", "externalIPs", "loadBalancerIP",
            "sessionAffinity", "externalTrafficPolicy",
            "ports", "targetPort", "nodePort",
            
            # Security
            "securityContext", "runAsUser", "runAsGroup",
            "fsGroup", "capabilities", "privileged",
            
            # Common spec fields
            "replicas", "selector", "template", "strategy",
            "type", "rules", "subjects", "roleRef"
        }
        
        # Start with core and nested keys
        all_keys = core_keys | nested_keys
        
        # Extract keys from primary K8s catalog
        if self.catalog:
            all_keys |= self._extract_keys_from_catalog(self.catalog)
        
        # Extract keys from OpenAPI catalog
        if self.openapi_catalog:
            all_keys |= self._extract_openapi_keys(self.openapi_catalog)
        
        # Extract keys from CRD catalog
        if self.crd_catalog:
            all_keys |= self._extract_keys_from_catalog(self.crd_catalog)
        
        # Extract keys from plugin catalogs
        for plugin_catalog in self.plugin_catalogs:
            if isinstance(plugin_catalog, dict):
                all_keys |= self._extract_keys_from_catalog(plugin_catalog)
        
        return all_keys
    
    def _extract_keys_from_catalog(self, catalog: Dict[Any, Any]) -> Set[str]:
        """
        Extracts field keys from a catalog structure.
        
        Args:
            catalog: Catalog dictionary (K8s or CRD format)
        
        Returns:
            Set of field keys found in catalog
        """
        keys = set()
        
        for resource_key, schema in catalog.items():
            if not isinstance(schema, dict):
                continue
            
            # Extract properties if present
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                keys.update(properties.keys())
            
            # Recursively extract nested properties
            keys |= self._extract_nested_properties(properties)
        
        return keys
    
    def _extract_nested_properties(self, properties: Dict[str, Any], depth: int = 0) -> Set[str]:
        """
        Recursively extracts property keys from nested schema.
        
        Args:
            properties: Properties dictionary from schema
            depth: Current nesting depth (prevents infinite recursion)
        
        Returns:
            Set of nested property keys
        """
        if depth > 3:  # Limit recursion depth
            return set()
        
        keys = set()
        
        for prop_name, prop_schema in properties.items():
            if not isinstance(prop_schema, dict):
                continue
            
            # Add nested properties
            nested_props = prop_schema.get("properties", {})
            if isinstance(nested_props, dict):
                keys.update(nested_props.keys())
                keys |= self._extract_nested_properties(nested_props, depth + 1)
        
        return keys
    
    def _extract_openapi_keys(self, openapi_catalog: Dict[Any, Any]) -> Set[str]:
        """
        Extracts keys from OpenAPI 3.0 catalog.
        
        Args:
            openapi_catalog: OpenAPI 3.0 schema definitions
        
        Returns:
            Set of field keys from OpenAPI schemas
        """
        keys = set()
        
        # OpenAPI schemas are typically under "components.schemas"
        schemas = openapi_catalog.get("components", {}).get("schemas", {})
        
        for schema_name, schema in schemas.items():
            if not isinstance(schema, dict):
                continue
            
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                keys.update(properties.keys())
                keys |= self._extract_nested_properties(properties)
        
        return keys
    
    def has_schema_for(self, kind: str) -> bool:
        """
        Checks if any catalog contains a schema for this Kind.
        
        Searches across:
        1. Primary K8s catalog
        2. OpenAPI catalog
        3. CRD catalog
        4. Plugin catalogs
        
        Args:
            kind: The Kubernetes Kind name (e.g., "Deployment", "Service")
        
        Returns:
            True if schema exists in any catalog
        """
        # Check primary catalog
        if self._kind_in_catalog(kind, self.catalog):
            return True
        
        # Check OpenAPI catalog
        if self.openapi_catalog:
            # OpenAPI might have schemas under different structure
            schemas = self.openapi_catalog.get("components", {}).get("schemas", {})
            if kind in schemas:
                return True
        
        # Check CRD catalog
        if self.crd_catalog and self._kind_in_catalog(kind, self.crd_catalog):
            return True
        
        # Check plugin catalogs
        for plugin_catalog in self.plugin_catalogs:
            if isinstance(plugin_catalog, dict) and self._kind_in_catalog(kind, plugin_catalog):
                return True
        
        return False
    
    def _kind_in_catalog(self, kind: str, catalog: Dict[Any, Any]) -> bool:
        """
        Checks if a kind exists in a specific catalog.
        
        Args:
            kind: Kind name to search for
            catalog: Catalog to search in
        
        Returns:
            True if kind found in catalog
        """
        # Check for (apiVersion, kind) tuple keys
        for key in catalog.keys():
            if isinstance(key, tuple) and len(key) == 2:
                if key[1] == kind:
                    return True
        return False
    
    def get_structure_keys(self) -> Set[str]:
        """
        Returns the set of known structure keys.
        
        Returns:
            Set of recognized field keys
        """
        return self.known_structure_keys