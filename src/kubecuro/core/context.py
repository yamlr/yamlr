#!/usr/bin/env python3
"""
AKESO HEALING CONTEXT
---------------------
A state-management object that acts as the 'Medical Record' for a manifest 
undergoing repair. It stores both the raw trauma and the healed structures.

This context is the primary data carrier between the Lexer, Scanner, 
and the Surgical Engine.

Enhancements (2026-01-26):
- cluster_version now parameterized (not hardcoded)
- OSS: Manual override via --kube-version flag or AKESO_KUBE_VERSION env
- Pro: Auto-detection from kubectl/cluster (graceful fallback to OSS)
- Smart defaults based on latest stable K8s version

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-26
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Any, List, Optional

from kubecuro.models import Shard, ManifestIdentity, HealAction

logger = logging.getLogger("kubecuro.context")


@dataclass
class HealContext:
    """
    Maintains the state of a single manifest repair session.
    
    Key responsibilities:
    - Hold the original raw text for surgical reference.
    - Store the Shards (lexical units) produced by the Lexer.
    - Track proposed 'Prescriptions' (HealActions) for the manifest.
    - Carry reconstructed document structures for final output.
    - Manage cluster version for accurate deprecation detection.
    """
    
    # =========================================================================
    # 1. INPUT SOURCE
    # =========================================================================
    raw_text: str
    
    # =========================================================================
    # 2. LEXICAL STATE
    # =========================================================================
    # List of processed Shard objects (healed lexical units)
    shards: List[Shard] = field(default_factory=list)
    
    # Reference to the Shadow engine used to capture layout (comments, gaps)
    # This allows Akeso to preserve human formatting after surgery.
    shadow_engine: Any = None
    
    # =========================================================================
    # 3. IDENTITY STATE
    # =========================================================================
    # The detected primary K8s Kind and API for the current document
    kind: Optional[str] = None
    api_version: Optional[str] = None
    
    # Complete set of identities for multi-document manifests (separated by ---)
    identities: List[ManifestIdentity] = field(default_factory=list)
    
    # =========================================================================
    # 4. SURGICAL STATE
    # =========================================================================
    # List of HealAction objects (The 'Prescriptions' for the manifest)
    prescriptions: List[HealAction] = field(default_factory=list)
    
    # List of reconstructed document objects produced by the Structurer
    reconstructed_docs: List[Any] = field(default_factory=list)
    
    # =========================================================================
    # 5. GLOBAL METADATA (ENHANCED: Cluster Version Management)
    # =========================================================================
    
    # FIXED: cluster_version is now dynamic (not hardcoded to v1.31)
    # Supports:
    # - OSS: Manual override via --kube-version flag or AKESO_KUBE_VERSION env
    # - Pro: Auto-detection from kubectl/cluster (via bridge)
    # - Fallback: Latest stable K8s version (v1.31 as of 2026-01)
    cluster_version: str = field(
        default_factory=lambda: HealContext._get_default_cluster_version()
    )
    
    # Pro feature flag (set by Shield/Validator if Pro is active)
    is_hardened: bool = False
    
    # =========================================================================
    # 6. DIAGNOSTIC AUDIT TRAIL
    # =========================================================================
    logic_logs: List[str] = field(default_factory=list)
    
    # =========================================================================
    # CLUSTER VERSION DETECTION (OSS + Pro)
    # =========================================================================
    
    @staticmethod
    def _get_default_cluster_version() -> str:
        """
        Intelligently determines the target Kubernetes version.
        
        Detection Priority (OSS + Pro):
        ┌────────────────────────────────────────────────────────────┐
        │ Priority 1: Explicit override (passed by engine/CLI)       │
        │             - Handled by caller, not here                  │
        │ Priority 2: AKESO_KUBE_VERSION environment variable (OSS)  │
        │ Priority 3: 💎 Auto-detect from kubectl (Pro)              │
        │ Priority 4: 💎 Auto-detect from cluster API (Pro)          │
        │ Priority 5: Default to v1.31 (latest stable)               │
        └────────────────────────────────────────────────────────────┘
        
        Returns:
            str: Kubernetes version in format "v1.31" or "1.31"
        
        Examples:
            >>> os.environ['AKESO_KUBE_VERSION'] = '1.28'
            >>> HealContext._get_default_cluster_version()
            'v1.28'
            
            >>> # Pro mode with kubectl available
            >>> HealContext._get_default_cluster_version()
            'v1.28'  # Auto-detected from kubectl
        """
        
        # =====================================================================
        # PRIORITY 2: ENVIRONMENT VARIABLE (OSS)
        # =====================================================================
        env_version = os.getenv("AKESO_KUBE_VERSION")
        if env_version:
            normalized = HealContext._normalize_version(env_version)
            logger.debug(f"Using cluster version from AKESO_KUBE_VERSION: {normalized}")
            return normalized
        
        # =====================================================================
        # PRIORITY 3-4: AUTO-DETECTION (PRO - via Bridge)
        # =====================================================================
        # Try to load Pro detection module (graceful degradation)
        try:
            from kubecuro.core.bridge import AkesoBridge
            
            if AkesoBridge.is_pro_enabled():
                # Try Pro auto-detection
                pro_detection = AkesoBridge.get_pro_module("cluster_detection")
                if pro_detection:
                    # Try kubectl detection first (faster)
                    detected = pro_detection.ClusterDetection.detect_from_kubectl()
                    if detected:
                        logger.info(f"💎 Pro: Auto-detected K8s {detected} from kubectl")
                        return detected
                    
                    # Try cluster API detection (requires cluster access)
                    detected = pro_detection.ClusterDetection.detect_from_cluster()
                    if detected:
                        logger.info(f"💎 Pro: Auto-detected K8s {detected} from cluster API")
                        return detected
        except ImportError:
            # Bridge not available (shouldn't happen, but defensive)
            pass
        except Exception as e:
            # Pro detection failed, fall back to default
            logger.debug(f"Pro auto-detection failed (non-critical): {e}")
        
        # =====================================================================
        # PRIORITY 5: DEFAULT TO LATEST STABLE (OSS + Pro)
        # =====================================================================
        default_version = "v1.31"  # Latest stable as of 2026-01
        logger.debug(f"Using default cluster version: {default_version}")
        return default_version
    
    @staticmethod
    def _normalize_version(version: str) -> str:
        """
        Normalizes version string to consistent format.
        
        Accepts:
        - "1.28" → "v1.28"
        - "v1.28" → "v1.28"
        - "1.28.3" → "v1.28"
        
        Args:
            version: Raw version string
            
        Returns:
            str: Normalized version (e.g., "v1.28")
        """
        # Remove leading 'v' if present
        clean = version.strip().lstrip('v')
        
        # Extract major.minor (ignore patch)
        parts = clean.split('.')
        if len(parts) >= 2:
            major, minor = parts[0], parts[1]
            return f"v{major}.{minor}"
        
        # Fallback: return as-is with 'v' prefix
        return f"v{clean}" if not version.startswith('v') else version
    
    @staticmethod
    def set_cluster_version(version: str) -> str:
        """
        Helper to set cluster version with validation.
        
        Used by CLI to validate user input before creating context.
        
        Args:
            version: User-provided version string
            
        Returns:
            str: Normalized, validated version
            
        Raises:
            ValueError: If version format is invalid
            
        Examples:
            >>> HealContext.set_cluster_version("1.28")
            'v1.28'
            
            >>> HealContext.set_cluster_version("invalid")
            ValueError: Invalid K8s version format
        """
        normalized = HealContext._normalize_version(version)
        
        # Basic validation: check format vX.Y
        parts = normalized.lstrip('v').split('.')
        if len(parts) < 2:
            raise ValueError(
                f"Invalid Kubernetes version format: '{version}'. "
                f"Expected format: '1.28' or 'v1.31'"
            )
        
        try:
            int(parts[0])  # Major must be integer
            int(parts[1])  # Minor must be integer
        except ValueError:
            raise ValueError(
                f"Invalid Kubernetes version: '{version}'. "
                f"Major and minor versions must be numbers."
            )
        
        return normalized
    
    # =========================================================================
    # PUBLIC API: SURGICAL OPERATIONS
    # =========================================================================
    
    def prescribe(self, action: HealAction) -> None:
        """
        Adds a surgical fix to the context.
        
        Usage: 
            context.prescribe(HealAction(
                stage="Lexer",
                action_type="repair",
                target="line 5",
                description="Fixed flush-left list",
                severity="INFO"
            ))
        
        Args:
            action: The healing action to record
        """
        self.prescriptions.append(action)
        self.add_log(f"Surgery: {action.description} at {action.target}")
    
    def add_log(self, message: str) -> None:
        """
        Appends a diagnostic message to the audit trail.
        
        Args:
            message: Log message to record
        """
        self.logic_logs.append(message)
    
    def get_summary(self) -> str:
        """
        Returns a scannable summary of the healing progress.
        
        Returns:
            str: Human-readable summary
            
        Example:
            "Manifest: Deployment/nginx | Heals: 3 | Target K8s: v1.28"
        """
        heal_count = len(self.prescriptions)
        return (
            f"Manifest: {self.kind or 'Unknown'} | "
            f"Heals: {heal_count} | "
            f"Target K8s: {self.cluster_version}"
        )
    
    def get_cluster_info(self) -> dict:
        """
        Returns cluster configuration details.
        
        Useful for debugging and audit reports.
        
        Returns:
            dict: Cluster metadata
        """
        return {
            "cluster_version": self.cluster_version,
            "is_hardened": self.is_hardened,
            "detected_kind": self.kind,
            "detected_api": self.api_version,
            "resource_count": len(self.identities)
        }
