#!/usr/bin/env python3
"""
KUBECURO LICENSE VALIDATOR
--------------------------
Implements hybrid trial model with usage-based limits.

Trial Limits (30 days OR usage caps, whichever comes first):
- 50 files healed
- 10 workspace Ghost scans
- 5 Shield policy runs
- 1 cluster connection

Author: Nishar A Sunkesala / Kubecuro Team
Date: 2026-01-26
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Dict, Any
from enum import Enum

logger = logging.getLogger("kubecuro.pro.license")

# ============================================================================
# CONFIGURATION
# ============================================================================

class LicenseType(Enum):
    TRIAL = "trial"
    PAID = "paid"
    TEAM = "team"
    ENTERPRISE = "enterprise"

# Trial Limits (Generous but prevents abuse)
TRIAL_LIMITS = {
    "files_healed": 50,              # Enough to test thoroughly
    "ghost_workspace_scans": 10,     # Cross-manifest analysis
    "shield_policy_runs": 10,        # Security hardening
    "cluster_connections": 1,        # Live cluster sync
    "audit_exports": 5,              # PDF/HTML reports
    "days": 30                       # Time-based fallback
}

# File paths (XDG Base Directory compliant)
CONFIG_DIR = Path.home() / ".config" / "kubecuro"
INSTALL_DATE_FILE = CONFIG_DIR / "install_date"
USAGE_FILE = CONFIG_DIR / "trial_usage.json"
LICENSE_FILE = CONFIG_DIR / "license.key"

# ============================================================================
# USAGE TRACKING
# ============================================================================

def _ensure_config_dir():
    """Creates config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def _get_install_date() -> datetime:
    """Gets or creates the trial installation date."""
    _ensure_config_dir()
    
    if INSTALL_DATE_FILE.exists():
        return datetime.fromisoformat(INSTALL_DATE_FILE.read_text().strip())
    
    # First run - create install date
    now = datetime.now()
    INSTALL_DATE_FILE.write_text(now.isoformat())
    logger.info(f"Trial started: {now.isoformat()}")
    return now

def _get_usage() -> Dict[str, int]:
    """Loads current trial usage statistics."""
    _ensure_config_dir()
    
    if not USAGE_FILE.exists():
        # Initialize usage tracking
        default_usage = {
            "files_healed": 0,
            "ghost_workspace_scans": 0,
            "shield_policy_runs": 0,
            "cluster_connections": 0,
            "audit_exports": 0
        }
        USAGE_FILE.write_text(json.dumps(default_usage, indent=2))
        return default_usage
    
    try:
        return json.loads(USAGE_FILE.read_text())
    except Exception as e:
        logger.warning(f"Could not load usage file: {e}")
        return {key: 0 for key in TRIAL_LIMITS.keys() if key != "days"}

def _save_usage(usage: Dict[str, int]):
    """Persists usage statistics."""
    _ensure_config_dir()
    try:
        USAGE_FILE.write_text(json.dumps(usage, indent=2))
    except Exception as e:
        logger.warning(f"Could not save usage: {e}")

def track_usage(feature: str, count: int = 1):
    """
    Increments usage counter for a Pro feature.
    
    Args:
        feature (str): One of the keys in TRIAL_LIMITS
        count (int): Amount to increment (default: 1)
    
    Example:
        >>> track_usage("files_healed", 5)  # User healed 5 files
        >>> track_usage("ghost_workspace_scans")  # User ran 1 scan
    """
    usage = _get_usage()
    
    if feature in usage:
        usage[feature] += count
        _save_usage(usage)
        logger.debug(f"Usage tracked: {feature} = {usage[feature]}/{TRIAL_LIMITS.get(feature, 'unlimited')}")

def get_usage_summary() -> Dict[str, Dict[str, Any]]:
    """
    Returns detailed usage summary for UI display.
    
    Returns:
        Dict with structure:
        {
            "files_healed": {"used": 45, "limit": 50, "remaining": 5},
            "ghost_workspace_scans": {"used": 3, "limit": 10, "remaining": 7},
            ...
        }
    """
    usage = _get_usage()
    summary = {}
    
    for feature, limit in TRIAL_LIMITS.items():
        if feature == "days":
            continue
        
        used = usage.get(feature, 0)
        remaining = max(0, limit - used)
        
        summary[feature] = {
            "used": used,
            "limit": limit,
            "remaining": remaining,
            "percentage": int((used / limit) * 100) if limit > 0 else 0
        }
    
    return summary

# ============================================================================
# LICENSE VALIDATION (Main Entry Point)
# ============================================================================

def validate() -> Tuple[bool, str]:
    """
    Validates Kubecuro Pro license status.
    
    Returns:
        Tuple[bool, str]: (is_valid, detailed_message)
        
    Examples:
        >>> is_valid, msg = validate()
        >>> if is_valid:
        ...     print(f"Pro active: {msg}")
        
    Validation Logic:
        1. Check for paid license file
        2. If no paid license, check trial status
        3. Trial is valid if BOTH conditions met:
           - Within 30 days of installation
           - AND no usage limit exceeded
    """
    _ensure_config_dir()
    
    # ----------------------------------------------------------------
    # PATH 1: Paid License Check
    # ----------------------------------------------------------------
    if LICENSE_FILE.exists():
        try:
            license_data = json.loads(LICENSE_FILE.read_text())
            return _validate_paid_license(license_data)
        except Exception as e:
            logger.error(f"License file corrupt: {e}")
            return (False, f"License file invalid or corrupt: {e}")
    
    # ----------------------------------------------------------------
    # PATH 2: Trial License Check
    # ----------------------------------------------------------------
    return _validate_trial_license()

def _validate_paid_license(license_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates a paid license file.
    
    License file structure (JSON):
    {
        "license_key": "KUBECURO-XXXX-XXXX-XXXX",
        "type": "team",  # or "paid", "enterprise"
        "email": "user@company.com",
        "expires": "2027-12-31",
        "seats": 10,
        "features": ["unlimited", "priority_support"]
    }
    """
    try:
        license_type = license_data.get("type", "paid")
        expires_str = license_data.get("expires")
        
        if not expires_str:
            return (False, "License missing expiration date")
        
        expires = datetime.fromisoformat(expires_str)
        
        if datetime.now() > expires:
            days_expired = (datetime.now() - expires).days
            return (False, f"License expired {days_expired} days ago on {expires.date()}")
        
        days_remaining = (expires - datetime.now()).days
        
        # License is valid
        if license_type == "enterprise":
            return (True, f"Enterprise license active until {expires.date()} ({days_remaining} days)")
        elif license_type == "team":
            seats = license_data.get("seats", 1)
            return (True, f"Team license ({seats} seats) active until {expires.date()}")
        else:
            return (True, f"Pro license active until {expires.date()}")
            
    except Exception as e:
        logger.error(f"License validation error: {e}")
        return (False, f"License validation failed: {str(e)}")

def _validate_trial_license() -> Tuple[bool, str]:
    """
    Validates trial license with hybrid time + usage limits.
    
    Trial is VALID if:
        - Within 30 days AND
        - All usage limits respected
    
    Trial EXPIRES if:
        - 30 days passed OR
        - Any single usage limit exceeded
    """
    install_date = _get_install_date()
    days_elapsed = (datetime.now() - install_date).days
    days_remaining = TRIAL_LIMITS["days"] - days_elapsed
    
    usage = _get_usage()
    
    # ----------------------------------------------------------------
    # CHECK 1: Time-Based Expiration
    # ----------------------------------------------------------------
    if days_remaining <= 0:
        return (False, f"Trial expired {abs(days_remaining)} days ago. "
                       f"Installed on {install_date.date()}")
    
    # ----------------------------------------------------------------
    # CHECK 2: Usage-Based Limits
    # ----------------------------------------------------------------
    exceeded_limits = []
    
    for feature, limit in TRIAL_LIMITS.items():
        if feature == "days":
            continue
        
        used = usage.get(feature, 0)
        if used >= limit:
            exceeded_limits.append(f"{feature}: {used}/{limit}")
    
    if exceeded_limits:
        return (False, f"Trial limit exceeded: {', '.join(exceeded_limits)}. "
                       f"Upgrade to continue using Pro features")
    
    # ----------------------------------------------------------------
    # Trial is VALID - Build Status Message
    # ----------------------------------------------------------------
    
    # Find the feature closest to its limit (for user awareness)
    usage_percentages = []
    for feature, limit in TRIAL_LIMITS.items():
        if feature == "days":
            continue
        used = usage.get(feature, 0)
        pct = (used / limit) * 100
        usage_percentages.append((feature, used, limit, pct))
    
    # Sort by percentage used (descending)
    usage_percentages.sort(key=lambda x: x[3], reverse=True)
    
    # Build informative message
    if usage_percentages:
        top_feature, used, limit, pct = usage_percentages[0]
        feature_display = top_feature.replace("_", " ").title()
        
        return (True, f"Trial active: {days_remaining} days remaining. "
                      f"{feature_display}: {used}/{limit} used ({int(pct)}%)")
    else:
        return (True, f"Trial active: {days_remaining} days remaining")

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def check_feature_available(feature: str) -> Tuple[bool, str]:
    """
    Checks if a specific Pro feature is available without incrementing usage.
    
    Args:
        feature (str): Feature name (e.g., "ghost_workspace_scans")
        
    Returns:
        Tuple[bool, str]: (available, reason_if_not)
        
    Example:
        >>> available, msg = check_feature_available("shield_policy_runs")
        >>> if not available:
        ...     print(f"Cannot use Shield: {msg}")
    """
    is_valid, msg = validate()
    
    if not is_valid:
        return (False, msg)
    
    # If paid license, all features available
    if LICENSE_FILE.exists():
        return (True, "Enterprise license active")
    
    # Trial - check specific feature limit
    usage = _get_usage()
    limit = TRIAL_LIMITS.get(feature, float('inf'))
    used = usage.get(feature, 0)
    
    if used >= limit:
        return (False, f"Trial limit reached: {feature} ({used}/{limit}). "
                       f"Upgrade at https://kubecuro.dev/upgrade")
    
    remaining = limit - used
    return (True, f"{remaining} {feature.replace('_', ' ')} remaining in trial")

def get_trial_status_display() -> str:
    """
    Returns a formatted string for CLI display.
    
    Example output:
        Trial Status (15 days remaining):
        ├─ Files Healed: 45/50 (90%) ██████████░
        ├─ Ghost Scans: 3/10 (30%) ███░░░░░░░░
        ├─ Shield Runs: 8/10 (80%) ████████░░
        └─ Audit Reports: 2/5 (40%) ████░░░░░░░
    """
    is_valid, msg = validate()
    
    if not is_valid:
        return f"❌ {msg}"
    
    if LICENSE_FILE.exists():
        return f"✅ {msg}"
    
    # Trial status with progress bars
    summary = get_usage_summary()
    install_date = _get_install_date()
    days_elapsed = (datetime.now() - install_date).days
    days_remaining = TRIAL_LIMITS["days"] - days_elapsed
    
    lines = [f"Trial Status ({days_remaining} days remaining):"]
    
    feature_labels = {
        "files_healed": "Files Healed",
        "ghost_workspace_scans": "Ghost Scans",
        "shield_policy_runs": "Shield Runs",
        "audit_exports": "Audit Reports",
        "cluster_connections": "Cluster Syncs"
    }
    
    for feature, data in summary.items():
        label = feature_labels.get(feature, feature)
        used = data["used"]
        limit = data["limit"]
        pct = data["percentage"]
        
        # Simple progress bar (10 blocks)
        filled = int(pct / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        lines.append(f"├─ {label}: {used}/{limit} ({pct}%) {bar}")
    
    return "\n".join(lines)

# ============================================================================
# MIGRATION HELPERS (For Paid Conversions)
# ============================================================================

def activate_license(license_key: str, email: str) -> Tuple[bool, str]:
    """
    Activates a paid license (called from CLI or web activation).
    
    This would typically:
    1. Validate license key with Kubecuro licensing server
    2. Download license file
    3. Save to LICENSE_FILE
    
    For MVP, this is a placeholder.
    """
    _ensure_config_dir()
    
    # TODO: Implement actual license server validation
    # For now, create a sample license file
    
    license_data = {
        "license_key": license_key,
        "type": "paid",
        "email": email,
        "expires": (datetime.now() + timedelta(days=365)).isoformat(),
        "activated_on": datetime.now().isoformat()
    }
    
    try:
        LICENSE_FILE.write_text(json.dumps(license_data, indent=2))
        return (True, f"License activated successfully for {email}")
    except Exception as e:
        return (False, f"Could not save license: {e}")

def get_trial_conversion_url() -> str:
    """Returns the URL for upgrading trial to paid."""
    usage = _get_usage()
    files_healed = usage.get("files_healed", 0)
    
    # Include usage data in URL for sales intelligence
    return (f"https://kubecuro.dev/upgrade"
            f"?files={files_healed}"
            f"&source=trial_limit")
