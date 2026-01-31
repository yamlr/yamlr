
"""
Yamlr Enterprise: License Manager
---------------------------------
Enforces feature access based on authentication tier.
"""

import logging
import base64
import json
from typing import Optional
from yamlr.pro.auth import auth_device

logger = logging.getLogger("yamlr.pro.license")

# Module-level export for YamlrBridge compatibility
def validate() -> tuple:
    return (True, "Valid License")

class LicenseManager:
    """
    Validates entitlements against the authenticated user's session.
    """

    FEATURES = {
        "opa": "enterprise",
        "shield": "enterprise",
        "bulk_fix": "pro",
        "deep_validate": "pro"
    }

    TIER_HIERARCHY = {
        "free": 0,
        "pro": 1,
        "enterprise": 2
    }

    def check_feature_access(self, feature_name: str) -> bool:
        """
        Determines if the current user is permitted to use a feature.
        """
        required_tier = self.FEATURES.get(feature_name, "enterprise")
        current_tier = self._get_current_tier()

        req_level = self.TIER_HIERARCHY.get(required_tier, 99)
        curr_level = self.TIER_HIERARCHY.get(current_tier, 0)
        
        is_allowed = curr_level >= req_level
        
        if not is_allowed:
            logger.warning(
                f"Feature '{feature_name}' requires '{required_tier}' tier. "
                f"Current tier: '{current_tier}'."
            )
            
        return is_allowed

    def track_usage(self, metric: str, value: int):
        """
        Records usage metrics for billing/quota.
        """
        # MVP: Just log it. Real implementation would batch send to API.
        logger.debug(f"[Usage] {metric}: {value}")

    def _get_current_tier(self) -> str:
        """Extracts tier from JWT."""
        token = auth_device.get_token()
        if not token:
            return "free"
            
        try:
            # Decode payload without verifying signature (AuthManager already validates session)
            # We assume token integrity here for feature flagging purposes
            parts = token.split('.')
            if len(parts) == 3:
                payload_segment = parts[1]
                padding = '=' * (4 - (len(payload_segment) % 4))
                payload_json = base64.urlsafe_b64decode(payload_segment + padding).decode()
                payload = json.loads(payload_json)
                return payload.get("tier", "free")
        except Exception:
            pass
            
        return "free"

# Singleton
license_manager = LicenseManager()

# Init hook for usage tracking
track_usage = license_manager.track_usage
