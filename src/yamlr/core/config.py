"""
Yamlr CONFIGURATION MANAGER
------------------------------
Handles loading and parsing of user configuration (.yamlr.yaml).
Allows customization of:
- Rule ignore patterns (glob-based)
- Health thresholds
- Analyzer settings
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fnmatch import fnmatch
from ruamel.yaml import YAML

logger = logging.getLogger("yamlr.config")

class ConfigManager:
    """
    Manages user configuration state.
    defaults:
      threshold: 70
      ignore: []
    """
    
    DEFAULT_CONFIG = {
        "rules": {
            "threshold": 70,
            "ignore": [
                ".git/*",
                "node_modules/*",
                "venv/*",
                "__pycache__/*"
            ]
        },
        "analyzers": {
            "enabled": ["*"]
        }
    }

    def __init__(self, workspace_root: Path, app_name: str = "Yamlr"):
        self.workspace = workspace_root
        self.app_name = app_name
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_config()

    def _load_config(self):
        """
        Attempts to load configuration from:
        1. .<app_name>/config.yaml (Preferred)
        2. .<app_name>.yaml (Root file)
        3. .yamlr.legacy.yaml (Fallback if branded differently)
        """
        yaml = YAML(typ='safe')
        
        # 1. State Directory Config
        state_config = self.workspace / f".{self.app_name}" / "config.yaml"
        
        # 2. Root File Configs
        possible_files = [state_config, self.workspace / f".{self.app_name}.yaml", self.workspace / ".yamlr.yaml"]
        
        for path in possible_files:
            if path.exists():
                try:
                    loaded = yaml.load(path)
                    if loaded:
                        self._merge_config(loaded)
                    logger.info(f"Loaded configuration from {path.name}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to parse {path.name}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to parse {fname}: {e}")

    def _merge_config(self, user_config: Dict[str, Any]):
        """Deep merge of user config into defaults."""
        # Simple depth-1 merge for now, can be expanded if needed
        if "rules" in user_config:
            self.config["rules"].update(user_config["rules"])
        if "analyzers" in user_config:
            self.config["analyzers"].update(user_config["analyzers"])

    def is_ignored(self, file_path: str, rule_id: Optional[str] = None) -> bool:
        """
        Determines if a file or rule should be ignored.
        
        Args:
            file_path: Relative path to the file.
            rule_id: Optional rule ID (e.g., 'rules/no-latest-tag').
            
        Returns:
            True if ignored, False otherwise.
        """
        ignores = self.config["rules"].get("ignore", [])
        
        # Check explicit ignore patterns
        for pattern in ignores:
            # File match
            if fnmatch(file_path, pattern):
                return True
            # Rule ID match (if provided)
            if rule_id and rule_id == pattern:
                return True
        
        return False

    @property
    def health_threshold(self) -> int:
        return self.config["rules"].get("threshold", 70)
