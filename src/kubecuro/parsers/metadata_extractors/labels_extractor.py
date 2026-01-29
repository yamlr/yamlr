#!/usr/bin/env python3
"""
Extractor for Pod/Deployment labels.

Extracts:
- metadata.labels (root level or in Pod template)
"""

from typing import List
from kubecuro.models import Shard, ManifestIdentity


class LabelsExtractor:
    """Extracts label fields for selector matching."""
    
    @staticmethod
    def extract_if_applicable(
        shard: Shard,
        key: str,
        val: str,
        path_keys: List[str],
        identity: ManifestIdentity
    ) -> bool:
        """
        Extract label key-value pair if we're in labels context.
        
        Returns:
            bool: True if extraction was performed
        """
        # Skip structural keys
        if key in ("labels", "metadata"):
            return False
        
        # Must have both 'metadata' and 'labels' in path
        # But NOT in selector (selector also has labels)
        if "metadata" in path_keys and "labels" in path_keys:
            if "selector" not in path_keys:
                if identity.labels is None:
                    identity.labels = {}
                identity.labels[key] = val
                return True
        
        return False