#!/usr/bin/env python3
"""
YAMLR ENTERPRISE – ADVANCED DEPRECATION ENGINE
-----------------------------------------
Enterprise-grade API lifecycle intelligence.

Extends Yamlr OSS deprecation detection with:
• Cluster version targeting
• CRD lifecycle awareness
• Risk scoring
• Upgrade readiness analysis

Author: Nishar A Sunkesala / Emplatix Team
Date: 2026-01-26
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

# Ensure Yamlr OSS foundation is available
try:
    from yamlr.core.deprecations import DeprecationChecker, DeprecationInfo
except ImportError as e:
    raise RuntimeError(
        "Yamlr Enterprise requires Yamlr foundation. "
        "Install Yamlr first: pip install Yamlr"
    ) from e

logger = logging.getLogger("yamlr.pro.deprecations")


@dataclass
class ProDeprecationReport:
    """Enhanced deprecation report with risk analysis."""
    info: DeprecationInfo
    cluster_version: str
    will_break_on_upgrade: bool
    risk_score: int
    remediation_level: str  # "INFO" | "WARN" | "BLOCK"
    notes: str
    auto_fixable: bool = False
    estimated_impact: str = "Unknown"


class ProDeprecationChecker:
    """
    Enterprise deprecation engine with cluster-aware intelligence.
    """

    def __init__(
        self,
        cluster_version: str,
        target_upgrade_version: Optional[str] = None,
        discovered_crds: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize Pro deprecation checker.
        
        Args:
            cluster_version: Current cluster version (e.g., "1.28")
            target_upgrade_version: Planned upgrade version (e.g., "1.29")
            discovered_crds: CRD versions discovered from cluster
        """
        self.cluster_version = cluster_version
        self.target_upgrade_version = target_upgrade_version
        self.discovered_crds = discovered_crds or {}
        self.oss_checker = DeprecationChecker()
        
        logger.info(
            f"Pro deprecation checker initialized for cluster v{cluster_version}"
            + (f" → v{target_upgrade_version}" if target_upgrade_version else "")
        )

    # -------------------------------------------------------------
    # Core analysis
    # -------------------------------------------------------------

    def analyze(self, api_version: str, kind: str) -> Optional[ProDeprecationReport]:
        """
        Perform comprehensive deprecation analysis.
        
        Args:
            api_version: API version to analyze
            kind: Resource kind
            
        Returns:
            ProDeprecationReport with risk assessment, None if not deprecated
        """
        info = self.oss_checker.check(api_version, kind)
        if not info:
            return None

        will_break = False
        if self.target_upgrade_version:
            will_break = self.oss_checker.is_removed(
                api_version, kind, self.target_upgrade_version
            )

        risk = self._calculate_risk(info, will_break)
        auto_fixable = self._is_auto_fixable(info)
        impact = self._estimate_impact(info, will_break)

        return ProDeprecationReport(
            info=info,
            cluster_version=self.cluster_version,
            will_break_on_upgrade=will_break,
            risk_score=risk,
            remediation_level=self._risk_to_level(risk),
            notes=self._generate_notes(info, will_break),
            auto_fixable=auto_fixable,
            estimated_impact=impact
        )

    # -------------------------------------------------------------
    # CRD intelligence (PRO-only)
    # -------------------------------------------------------------

    def analyze_crd(self, crd_name: str, version: str) -> Optional[str]:
        """
        Detect deprecated CRD versions (requires live discovery).
        
        Args:
            crd_name: CRD name (e.g., "certificates.cert-manager.io")
            version: Version to check (e.g., "v1alpha1")
            
        Returns:
            Warning message if deprecated, None otherwise
        """
        versions = self.discovered_crds.get(crd_name, [])
        if not versions:
            return f"CRD {crd_name} not found in cluster"
        
        if version not in versions:
            return f"CRD {crd_name}/{version} is not served by the cluster"
        
        # TODO: Check CRD spec.versions[].deprecated field
        return None

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------

    def _calculate_risk(self, info: DeprecationInfo, will_break: bool) -> int:
        """Calculate risk score (0-100)."""
        if will_break:
            return 95
        if info.severity == "REMOVED":
            return 75
        return 40

    def _risk_to_level(self, score: int) -> str:
        """Convert risk score to remediation level."""
        if score >= 85:
            return "BLOCK"
        if score >= 60:
            return "WARN"
        return "INFO"

    def _generate_notes(self, info: DeprecationInfo, will_break: bool) -> str:
        """Generate contextual notes for the deprecation."""
        if will_break:
            return (
                f"⚠️  This resource will FAIL after upgrading to {self.target_upgrade_version}. "
                f"Migration required before upgrade."
            )
        return f"Deprecated but currently supported on {self.cluster_version}."
    
    def _is_auto_fixable(self, info: DeprecationInfo) -> bool:
        """Determine if deprecation can be auto-fixed."""
        # Simple API version changes are auto-fixable
        if info.replacement_api != "N/A" and "pathType" not in info.migration_notes:
            return True
        return False
    
    def _estimate_impact(self, info: DeprecationInfo, will_break: bool) -> str:
        """Estimate upgrade impact."""
        if will_break:
            return "High - Immediate action required"
        if info.severity == "REMOVED":
            return "Medium - Plan migration"
        return "Low - Monitor for future releases"
