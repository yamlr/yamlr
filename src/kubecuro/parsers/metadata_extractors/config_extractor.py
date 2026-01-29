#!/usr/bin/env python3
"""
Extractor for ConfigMap/Secret references.

Extracts:
- volumes[].configMap.name
- volumes[].secret.secretName
- env[].valueFrom.configMapKeyRef.name
- envFrom[].configMapRef.name
"""

from typing import List
from kubecuro.models import Shard, ManifestIdentity


class ConfigExtractor:
    """Extracts ConfigMap/Secret references from Pod specs."""
    
    @staticmethod
    def extract_if_applicable(
        shard: Shard,
        key: str,
        val: str,
        path_keys: List[str],
        identity: ManifestIdentity
    ) -> bool:
        """
        Extract ConfigMap/Secret name if in config reference context.
        
        Returns:
            bool: True if extraction was performed
        """
        # Volume references
        if key in ("name", "secretName"):
            if "volumes" in path_keys:
                if "configMap" in path_keys or "secret" in path_keys:
                    if val and val not in identity.config_refs:
                        identity.config_refs.append(val)
                    return True
        
        # Env references
        if key == "name":
            if "env" in path_keys or "envFrom" in path_keys:
                config_ref_keys = ["configMapKeyRef", "secretKeyRef", "configMapRef", "secretRef"]
                if any(ref in path_keys for ref in config_ref_keys):
                    if val and val not in identity.config_refs:
                        identity.config_refs.append(val)
                    return True
        
        return False