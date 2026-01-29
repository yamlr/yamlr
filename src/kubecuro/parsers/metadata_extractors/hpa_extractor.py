#!/usr/bin/env python3
"""
Extractor for HPA scale target references.

Extracts:
- spec.scaleTargetRef.name (HorizontalPodAutoscaler)
"""

from typing import List
from kubecuro.models import Shard, ManifestIdentity


class HPAExtractor:
    """Extracts scale target references from HPA resources."""
    
    @staticmethod
    def extract_if_applicable(
        shard: Shard,
        key: str,
        val: str,
        path_keys: List[str],
        identity: ManifestIdentity
    ) -> bool:
        """
        Extract scale target name if in HPA context.
        
        Only applies to HorizontalPodAutoscaler resources.
        
        Returns:
            bool: True if extraction was performed
        """
        # Only extract from HPA resources
        if identity.kind != "HorizontalPodAutoscaler":
            return False
        
        # Check for scaleTargetRef.name
        if key == "name" and "scaleTargetRef" in path_keys:
            if val and not identity.scale_target:
                identity.scale_target = val
            return True
        
        return False