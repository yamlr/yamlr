#!/usr/bin/env python3
"""
Extractor for PersistentVolumeClaim references.

Extracts:
- volumes[].persistentVolumeClaim.claimName
"""

from typing import List
from yamlr.models import Shard, ManifestIdentity


class VolumeExtractor:
    """Extracts PVC references from Pod specs."""
    
    @staticmethod
    def extract_if_applicable(
        shard: Shard,
        key: str,
        val: str,
        path_keys: List[str],
        identity: ManifestIdentity
    ) -> bool:
        """
        Extract PVC name if in volume reference context.
        
        Note: We don't require 'volumes' in path because it may be
        replaced by list item keys during iteration.
        
        Returns:
            bool: True if extraction was performed
        """
        if key == "claimName" and "persistentVolumeClaim" in path_keys:
            if val and val not in identity.volume_refs:
                identity.volume_refs.append(val)
            return True
        
        return False
