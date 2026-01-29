"""
AKESO CATALOG MANAGER
---------------------
Manages the lifecycle of Kubernetes schema definitions (catalogs).
Responsible for:
1.  Local storage (`~/.akeso/catalogs`)
2.  Fetching updates from upstream (Standard versions)
3.  Cache resolution
"""

import os
import json
import logging
import urllib.request
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger("kubecuro.catalog")

class CatalogManager:
    """
    Manages versioned Kubernetes catalogs (distilled schemas).
    """
    
    # Placeholder for the official Akeso schema repository
    # In a real build, this would point to the CDN or GitHub Raw
    UPSTREAM_BASE_URL = "https://raw.githubusercontent.com/akeso-io/catalogs/main/distilled"

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Args:
            storage_dir: Custom path for catalog storage. 
                         Defaults to ~/.akeso/catalogs
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir).resolve()
        else:
            self.storage_dir = Path.home() / ".akeso" / "catalogs"
            
        self._ensure_storage()

    def _ensure_storage(self):
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create catalog storage: {e}")

    def get_catalog_path(self, version: str) -> Path:
        """
        Constructs the expected local path for a version.
        Does NOT check existence.
        """
        version = self._normalize_version(version)
        return self.storage_dir / f"k8s_{version}_distilled.json"

    def resolve_catalog(self, version: str, fallback_path: Optional[str] = None) -> str:
        """
        Intelligent resolution of catalog path.
        Priority:
        1. Local Cache (~/.akeso/catalogs/k8s_vX.Y_distilled.json)
        2. Fallback Path (Bundled default)
        
        Args:
            version: Target K8s version
            fallback_path: Path to bundled/default catalog
            
        Returns:
            Absolute path to the resolved catalog
        """
        # 1. Check Cache
        cached_path = self.get_catalog_path(version)
        if cached_path.exists():
            logger.debug(f"Using cached catalog: {cached_path}")
            return str(cached_path)
            
        # 2. Return Fallback
        if fallback_path:
            logger.debug(f"Cached catalog not found for {version}, using fallback: {fallback_path}")
            return fallback_path
            
        # 3. If no fallback, return the cached path (caller will handle FileNotFoundError)
        return str(cached_path)

    def fetch_catalog(self, version: str) -> bool:
        """
        Downloads the specified version from upstream.
        Returns True if successful.
        """
        version = self._normalize_version(version)
        target_path = self.get_catalog_path(version)
        url = f"{self.UPSTREAM_BASE_URL}/k8s_{version}_distilled.json"
        
        logger.info(f"Fetching catalog {version} from {url}...")
        
        try:
            # Create request with user agent
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Akeso-CLI/0.1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                # Handle HTTP status (file:// returns None)
                if response.status is not None and response.status != 200:
                    logger.error(f"Upstream returned HTTP {response.status}")
                    return False
                data = response.read()
                
            # Verify valid JSON
            try:
                content = json.loads(data)
                if not isinstance(content, dict):
                    raise ValueError("Root element is not a dictionary")
            except Exception as e:
                logger.error(f"Invalid JSON received: {e}")
                return False

            # Atomic Write
            temp_path = target_path.with_suffix(".tmp")
            temp_path.write_bytes(data)
            os.replace(temp_path, target_path)
            
            logger.info(f"Successfully installed catalog for {version}")
            return True
            
        except urllib.error.URLError as e:
            logger.error(f"Network error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")
            return False

    def list_installed_versions(self) -> List[str]:
        """Returns list of locally available versions (e.g. ['v1.28', 'v1.29'])."""
        if not self.storage_dir.exists():
            return []
            
        versions = []
        for f in self.storage_dir.glob("k8s_*_distilled.json"):
            # Extract version from filename "k8s_v1.28_distilled.json"
            try:
                # remove prefix "k8s_" (4 chars) and suffix "_distilled.json" (15 chars)
                name = f.name
                if name.startswith("k8s_") and name.endswith("_distilled.json"):
                    ver = name[4:-15]
                    versions.append(ver)
            except:
                continue
        return sorted(versions)

    def _normalize_version(self, version: str) -> str:
        """Ensures 'v1.XX' format."""
        clean = version.strip().lower().lstrip('v')
        return f"v{clean}"
