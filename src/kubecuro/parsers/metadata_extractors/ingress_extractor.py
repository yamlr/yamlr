#!/usr/bin/env python3
"""
Extractor for Service references from Ingress resources.

Extracts:
- spec.rules[].http.paths[].backend.service.name (Ingress v1)
- spec.rules[].http.paths[].backend.serviceName (Ingress v1beta1)
"""

from typing import List
from kubecuro.models import Shard, ManifestIdentity


class IngressExtractor:
    """Extracts Service references from Ingress resources."""
    
    @staticmethod
    def extract_if_applicable(
        shard: Shard,
        key: str,
        val: str,
        path_keys: List[str],
        identity: ManifestIdentity
    ) -> bool:
        """
        Extract Service name if in Ingress backend context.
        
        Only applies to Ingress resources.
        
        Returns:
            bool: True if extraction was performed
        """
        # Only extract from Ingress resources
        if identity.kind != "Ingress":
            return False
        
        # Check for service name reference
        if key in ("name", "serviceName"):
            # Must be in backend context
            if "backend" in path_keys:
                # v1: backend.service.name
                # v1beta1: backend.serviceName
                if "service" in path_keys or key == "serviceName":
                    if val and val not in identity.service_refs:
                        identity.service_refs.append(val)
                    return True
        
        return False