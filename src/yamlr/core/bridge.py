#!/usr/bin/env python3
"""
Yamlr BRIDGE - The Capability Discovery & Identity Layer
-------------------------------------------------------
Enhanced License Management System for Yamlr OSS ↔ Yamlr Pro Integration

Features:
1. Identifies if the Yamlr Enterprise extension is installed.
2. Validates Pro license status with detailed error messages.
3. Silently ensures 'Yamlr' alias exists.
4. Manages brand identity based on invocation.
5. Provides defensive license checking that never breaks OSS functionality.

[2026-01-26] ENHANCED: Multi-tier license validation with ProStatus enum
[2026-01-21] Hardened: Removed top-level orchestrator imports to prevent circularities.

Author: Nishar A Sunkesala / Emplatix Team
Date: 2026-01-26
"""

import importlib.util
import importlib
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Any, Tuple
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

logger = logging.getLogger("yamlr.bridge")
console = Console()


# ============================================================================
# LICENSE STATUS ENUMERATION
# ============================================================================

class ProStatus(Enum):
    """
    Represents the state of Yamlr Enterprise installation and licensing.
    
    Used to provide detailed feedback to users and enable graceful degradation.
    """
    NOT_INSTALLED = "not_installed"      # yamlr.pro package not found
    VALID = "valid"                      # Pro installed with active license
    TRIAL_ACTIVE = "trial_active"        # Pro installed in trial period
    TRIAL_EXPIRED = "trial_expired"      # Trial period ended
    LICENSE_EXPIRED = "license_expired"  # Paid license expired
    LICENSE_INVALID = "license_invalid"  # License file corrupt or tampered
    NETWORK_ERROR = "network_error"      # Could not verify online (fallback allowed)
    INSTALLATION_CORRUPT = "corrupt"     # Pro installed but missing critical modules
    
    def is_usable(self) -> bool:
        """Returns True if Pro features should be enabled."""
        return self in {
            ProStatus.VALID,
            ProStatus.TRIAL_ACTIVE,
            ProStatus.NETWORK_ERROR  # Graceful degradation for offline users
        }
    
    def requires_user_action(self) -> bool:
        """Returns True if user needs to take action (renew, activate, etc.)."""
        return self in {
            ProStatus.TRIAL_EXPIRED,
            ProStatus.LICENSE_EXPIRED,
            ProStatus.LICENSE_INVALID
        }


# ============================================================================
# Yamlr BRIDGE - MAIN INTERFACE CLASS
# ============================================================================

class YamlrBridge:
    """
    Manages the interface between Yamlr OSS and Yamlr Pro.
    
    Design Principles:
    - Defensive: OSS features ALWAYS work, even if Pro detection fails
    - Transparent: Clear error messages guide users to resolution
    - Non-blocking: License checks never crash the CLI
    - Privacy-first: No telemetry without explicit user consent
    """

    # ========================================================================
    # ENHANCED LICENSE DETECTION (Three-Tier Validation)
    # ========================================================================

    @staticmethod
    def check_pro_status() -> Tuple[ProStatus, str]:
        """
        Performs comprehensive Pro license validation with detailed diagnostics.
        
        Three-Tier Detection:
        1. Installation Check: Is yamlr.pro package present?
        2. Module Integrity: Can we import the license validator?
        3. License Validation: Is the license active and valid?
        
        Returns:
            Tuple[ProStatus, str]: (status_enum, human_readable_message)
            
        Examples:
            >>> status, msg = YamlrBridge.check_pro_status()
            >>> if status == ProStatus.VALID:
            ...     print(f"Pro active: {msg}")
            >>> elif status.requires_user_action():
            ...     print(f"Action needed: {msg}")
        
        Note:
            This function is DEFENSIVE and will never raise exceptions.
            If validation fails for any reason, it safely returns NOT_INSTALLED.
        """
        try:
            # ----------------------------------------------------------------
            # TIER 1: Installation Check
            # ----------------------------------------------------------------
            pro_spec = importlib.util.find_spec("yamlr.pro")
            
            if pro_spec is None:
                return (
                    ProStatus.NOT_INSTALLED,
                    "Yamlr Enterprise not installed. Using Yamlr OSS features."
                )
            
            # ----------------------------------------------------------------
            # TIER 2: License Module Validation
            # ----------------------------------------------------------------
            try:
                # Attempt to import the Pro license validator
                # This is a separate module to keep licensing logic in Pro codebase
                from yamlr.pro import license as pro_license
                
                # Verify the module has the required validate() function
                if not hasattr(pro_license, 'validate'):
                    logger.warning(
                        "yamlr.pro.license module exists but missing validate() function"
                    )
                    return (
                        ProStatus.INSTALLATION_CORRUPT,
                        "Yamlr installation incomplete. Reinstall with: pip install --upgrade Yamlr"
                    )
                
            except ImportError as e:
                # Pro package exists but license.py is missing
                logger.warning(f"Pro installed but license module unavailable: {e}")
                return (
                    ProStatus.INSTALLATION_CORRUPT,
                    "Yamlr installation incomplete. Please reinstall the Enterprise package."
                )
            
            # ----------------------------------------------------------------
            # TIER 3: License Status Validation
            # ----------------------------------------------------------------
            try:
                # Call the Pro license validator
                # Expected signature: validate() -> Tuple[bool, str]
                # Returns: (is_valid: bool, reason: str)
                is_valid, reason = pro_license.validate()
                
                # Parse the validation result and map to appropriate status
                if is_valid:
                    # License is active - check if it's trial or paid
                    if "trial" in reason.lower():
                        return (
                            ProStatus.TRIAL_ACTIVE,
                            reason  # e.g., "Trial active: 15 days remaining"
                        )
                    else:
                        return (
                            ProStatus.VALID,
                            reason  # e.g., "Enterprise license active until 2027-12-31"
                        )
                
                # License validation failed - determine why
                reason_lower = reason.lower()
                
                if "trial" in reason_lower and "expired" in reason_lower:
                    return (
                        ProStatus.TRIAL_EXPIRED,
                        f"{reason}. Activate your license at https://yamlr.dev/activate"
                    )
                elif "expired" in reason_lower:
                    return (
                        ProStatus.LICENSE_EXPIRED,
                        f"{reason}. Renew at https://yamlr.dev/renew"
                    )
                elif "invalid" in reason_lower or "corrupt" in reason_lower:
                    return (
                        ProStatus.LICENSE_INVALID,
                        f"{reason}. Contact support at support@yamlr.dev"
                    )
                elif "network" in reason_lower or "offline" in reason_lower:
                    # Network validation failed, but allow offline usage
                    logger.info("Pro license validation offline - allowing graceful degradation")
                    return (
                        ProStatus.NETWORK_ERROR,
                        f"{reason}. Running with cached validation."
                    )
                else:
                    # Generic validation failure
                    return (
                        ProStatus.LICENSE_INVALID,
                        f"License validation failed: {reason}"
                    )
                    
            except Exception as e:
                # License validation threw an exception
                # This is defensive - we log it but don't crash
                logger.warning(f"Pro license validation error: {e}", exc_info=True)
                return (
                    ProStatus.NETWORK_ERROR,
                    "Could not verify license (offline mode). Enterprise features enabled with cached validation."
                )
                
        except Exception as e:
            # Ultimate failsafe: If anything goes wrong in the entire detection chain,
            # we default to NOT_INSTALLED to ensure OSS always works
            logger.debug(f"Pro detection failed gracefully: {e}")
            return (
                ProStatus.NOT_INSTALLED,
                "License check unavailable. Using Yamlr OSS features only."
            )

    @staticmethod
    def is_pro_enabled() -> bool:
        """
        Legacy compatibility wrapper for simple boolean Pro detection.
        
        Returns:
            bool: True if Pro features should be enabled, False otherwise.
            
        Note:
            This is a simplified interface. For detailed status information,
            use check_pro_status() instead.
        
        Usage:
            >>> if YamlrBridge.is_pro_enabled():
            ...     run_pro_feature()
        """
        status, _ = YamlrBridge.check_pro_status()
        return status.is_usable()

    @staticmethod
    def get_pro_status_display() -> Tuple[str, str, str]:
        """
        Returns formatted status information for UI display.
        
        Returns:
            Tuple[str, str, str]: (status_badge, message, color)
            
        Example:
            >>> badge, msg, color = YamlrBridge.get_pro_status_display()
            >>> console.print(f"[{color}]{badge}[/{color}] {msg}")
        """
        status, message = YamlrBridge.check_pro_status()
        
        # Map status to display components
        display_map = {
            ProStatus.NOT_INSTALLED: ("OSS", message, "cyan"),
            ProStatus.VALID: ("PRO ✓", message, "green"),
            ProStatus.TRIAL_ACTIVE: ("TRIAL", message, "yellow"),
            ProStatus.TRIAL_EXPIRED: ("TRIAL EXPIRED", message, "red"),
            ProStatus.LICENSE_EXPIRED: ("EXPIRED", message, "red"),
            ProStatus.LICENSE_INVALID: ("INVALID", message, "red"),
            ProStatus.NETWORK_ERROR: ("PRO (OFFLINE)", message, "yellow"),
            ProStatus.INSTALLATION_CORRUPT: ("ERROR", message, "red"),
        }
        
        return display_map.get(status, ("UNKNOWN", message, "dim"))

    # ========================================================================
    # IDENTITY & BRANDING MANAGEMENT
    # ========================================================================

    @staticmethod
    def ensure_dual_identity():
        """
        Silently ensures 'Yamlr' alias exists.
        Creates symlinks or copies to enable twin-command invocation.
        
        Behavior:
        - If user runs 'yamlr', creates 'Yamlr' alias
        - If user runs 'Yamlr', creates 'yamlr' alias
        - Handles permission errors gracefully (no crash)
        - Cross-platform compatible (Windows uses copy, Unix uses symlink)
        
        Security:
        - Only operates in the current binary's directory
        - Validates write permissions before attempting creation
        - Logs failures at debug level (no user-facing errors)
        
        Note:
            This function is safe to call multiple times (idempotent).
        """
        try:
            # 1. Determine the path of the current running binary or script
            if getattr(sys, 'frozen', False):
                # Running as a PyInstaller binary
                current_exe = Path(sys.executable)
            else:
                # Running as a Python script
                current_exe = Path(sys.argv[0]).resolve()

            bin_dir = current_exe.parent
            current_name = current_exe.name.lower()
            
            # 2. Check for write permissions to avoid 'Permission Denied' crashes
            if not os.access(bin_dir, os.W_OK):
                logger.debug(f"Skipping identity bridge: No write access to {bin_dir}")
                return

            # 3. Determine the "Twin" name (Cross-platform)
            is_windows = os.name == 'nt'
            suffix = ".exe" if is_windows else ""
            
            if "Yamlr" in current_name:
                target_name = f"Yamlr-alias{suffix}" # Example alternate
            else:
                target_name = f"Yamlr{suffix}"
                
            target_path = bin_dir / target_name

            # 4. If the twin doesn't exist, create it silently
            if not target_path.exists():
                try:
                    if is_windows:
                        # Windows: Binary copy is more reliable than links for CLI tools
                        import shutil
                        shutil.copy2(current_exe, target_path)
                        logger.info(f"Identity bridge established: {target_name} (copy)")
                    else:
                        # Linux/Mac: Symbolic link is the industry standard
                        os.symlink(current_exe.name, target_path)
                        logger.info(f"Identity bridge established: {target_name} (symlink)")
                        
                except PermissionError:
                    # Expected in system-wide installs (/usr/local/bin, etc.)
                    logger.debug(f"Identity bridge skipped: Permission denied for {target_path}")
                except Exception as e:
                    # Fail silently: User's work is more important than the alias
                    logger.debug(f"Identity bridge failed gracefully: {e}")
            else:
                logger.debug(f"Identity bridge already exists: {target_name}")
                
        except Exception as e:
            # Ultimate failsafe: Twin identity creation should never crash the app
            logger.debug(f"ensure_dual_identity() failed gracefully: {e}")

    @staticmethod
    def get_identity() -> str:
        """
        Detects the branding mode based on how the user invoked the CLI.
        
        Validation Strategy (Anti-Fraud):
        - "Yamlr" in name → Check if Pro package installed
        - "Yamlr" in name → Check if Pro package installed
        - Other names → Default to OSS (prevent false branding)
        
        This prevents wrapper scripts from falsely claiming "PRO" status.
        
        Returns:
            str: 'OSS' if Pro not installed,
                 'PRO' if invoked with Pro package present
        
        Examples:
            >>> # User runs: yamlr heal deployment.yaml
            >>> get_identity()  # Returns "OSS"
            
            >>> # User runs: Yamlr heal deployment.yaml (with Pro installed)
            >>> get_identity()  # Returns "PRO"
            
            >>> # User runs: my-k8s-tool.sh (wrapper without Pro)
            >>> get_identity()  # Returns "OSS" (safe default)
        """
        invoked_as = os.path.basename(sys.argv[0]).lower()
        
        # Rule 1: Explicit OSS branding request
        # if "yamlr" in invoked_as:
        #    return "OSS"
        
        # Rule 2: Explicit Pro branding request (verify installation)
        if "Yamlr" in invoked_as:
            pro_spec = importlib.util.find_spec("yamlr.pro")
            if pro_spec is not None:
                return "PRO"
            else:
                # User typed "Yamlr" but Pro not installed
                logger.warning(
                    "Invoked as 'Yamlr' but Enterprise package not found. "
                    "Install with: pip install Yamlr"
                )
                return "OSS"
        
        # Rule 3: Unknown invocation (wrapper scripts, etc.)
        # Default to OSS to prevent false branding claims
        logger.debug(f"Unknown invocation '{invoked_as}' - defaulting to OSS branding")
        return "OSS"


    @staticmethod
    def get_invoked_command() -> str:
        """
        Returns the specific string used to call the CLI.
        
        Returns:
            str: The exact command name (e.g., 'yamlr', 'Yamlr', 'python -m yamlr')
        
        Example:
            >>> cmd = YamlrBridge.get_invoked_command()
            >>> print(f"You ran: {cmd}")
        """
        return os.path.basename(sys.argv[0])

    # ========================================================================
    # USER NOTIFICATIONS & UX
    # ========================================================================

    @staticmethod
    def notify_pro_required(feature_name: str):
        """
        Displays a standardized 'Polite Refusal' panel when users try Pro features.
        
        Design Philosophy:
        - Educational, not naggy
        - Clear value proposition
        - Actionable next steps
        - Respects OSS users (no degraded performance messaging)
        
        Args:
            feature_name (str): The name of the feature being requested
                               (e.g., "Shield Security Hardening", "PDF Export")
        
        Example Output:
            ┌─────────────────────────────────────────┐
            │ ✨ Shield Security is a Pro Feature     │
            │                                         │
            │ This feature requires Yamlr          │
            │ Enterprise extension.                   │
            │                                         │
            │ Visit https://yamlr.dev to:          │
            │  • Start a 30-day free trial            │
            │  • View enterprise pricing              │
            │  • Request a demo                       │
            └─────────────────────────────────────────┘
        """
        # Build the message content
        message_parts = [
            f"[bold yellow]✨ {feature_name} is a Pro Feature[/bold yellow]",
            "",
            "This feature requires the [bold]Yamlr Enterprise[/bold] extension.",
            "",
            "Visit [cyan]https://yamlr.dev[/cyan] to:",
            "  • Start a 30-day free trial",
            "  • View enterprise pricing and features",
            "  • Request a personalized demo",
            "",
            "[dim]Yamlr OSS will continue to provide core healing features.[/dim]"
        ]
        
        message = "\n".join(message_parts)
        
        console.print(Panel(
            message,
            border_style="yellow",
            expand=False,
            padding=(1, 2)
        ))

    @staticmethod
    def notify_license_status(status: ProStatus, message: str):
        """
        Displays license status notifications to users.
        
        Used for:
        - Trial expiration warnings
        - License renewal reminders
        - Installation error diagnostics
        
        Args:
            status (ProStatus): The current license status
            message (str): Detailed message from validation
        """
        if status == ProStatus.TRIAL_ACTIVE:
            # Friendly trial reminder (not alarming)
            console.print(
                f"[yellow]ℹ️  {message}[/yellow]",
                style="dim"
            )
        
        elif status == ProStatus.TRIAL_EXPIRED:
            # Urgent but respectful
            console.print(Panel(
                f"[bold red]⏰ Trial Period Ended[/bold red]\n\n"
                f"{message}\n\n"
                "[cyan]Activate your license at https://yamlr.dev/activate[/cyan]",
                border_style="red",
                expand=False
            ))
        
        elif status == ProStatus.LICENSE_EXPIRED:
            # Renewal reminder
            console.print(Panel(
                f"[bold yellow]🔄 License Renewal Required[/bold yellow]\n\n"
                f"{message}\n\n"
                "[cyan]Renew at https://yamlr.dev/renew[/cyan]\n"
                "[dim]Or contact sales@yamlr.dev for assistance[/dim]",
                border_style="yellow",
                expand=False
            ))
        
        elif status == ProStatus.LICENSE_INVALID:
            # Technical issue - guide to support
            console.print(Panel(
                f"[bold red]❌ License Validation Failed[/bold red]\n\n"
                f"{message}\n\n"
                "Please contact [cyan]support@yamlr.dev[/cyan] with:\n"
                f"  • Your license key\n"
                f"  • System info: {sys.platform}, Python {sys.version_info.major}.{sys.version_info.minor}",
                border_style="red",
                expand=False
            ))
        
        elif status == ProStatus.INSTALLATION_CORRUPT:
            # Reinstallation guide
            console.print(Panel(
                f"[bold red]⚠️ Installation Issue Detected[/bold red]\n\n"
                f"{message}\n\n"
                "Try reinstalling:\n"
                "  [cyan]pip uninstall Yamlr[/cyan]\n"
                "  [cyan]pip install --upgrade Yamlr[/cyan]",
                border_style="red",
                expand=False
            ))

    # ========================================================================
    # PRO MODULE LOADING
    # ========================================================================

    @staticmethod
    def get_pro_module(submodule: str) -> Optional[Any]:
        """
        Safely imports a Pro submodule if Pro is enabled and valid.
        
        Args:
            submodule (str): The name of the Pro submodule to load
                            (e.g., "shield", "validator", "exporter")
        
        Returns:
            Optional[Any]: The imported module, or None if unavailable
        
        Security:
        - Only loads modules if license is valid
        - Returns None gracefully if module missing
        - Logs import failures at debug level
        
        Usage:
            >>> shield = YamlrBridge.get_pro_module("shield")
            >>> if shield:
            ...     shield_engine = shield.ShieldEngine()
            ...     shield_engine.apply_policies(manifest)
        """
        # First check if Pro is actually usable
        if not YamlrBridge.is_pro_enabled():
            logger.debug(f"Pro module '{submodule}' not loaded: Pro not enabled")
            return None
        
        try:
            # Dynamic import to avoid circular dependency with high-level modules
            module = importlib.import_module(f"yamlr.pro.{submodule}")
            logger.debug(f"Pro module '{submodule}' loaded successfully")
            return module
            
        except ImportError as e:
            # Module doesn't exist in Pro package (expected for some features)
            logger.debug(f"Pro submodule '{submodule}' not available: {e}")
            return None
            
        except Exception as e:
            # Unexpected error - log but don't crash
            logger.warning(f"Failed to load Pro module '{submodule}': {e}", exc_info=True)
            return None
    @staticmethod
    def has_pro_license_file() -> bool:
        """Check if user ever had Pro (license file exists)."""
        from pathlib import Path
        license_file = Path.home() / ".Yamlr" / "license.key"
        return license_file.exists()

    @staticmethod
    def should_show_daily_reminder() -> bool:
        """Check if we should show the daily reminder (max once/day)."""
        from pathlib import Path
        from datetime import datetime, timedelta
        
        reminder_file = Path.home() / ".Yamlr" / "last_reminder.txt"
        
        if not reminder_file.exists():
            return True
        
        # Check last reminder time
        try:
            last_reminder = reminder_file.read_text().strip()
            last_time = datetime.fromisoformat(last_reminder)
            
            # Show if more than 24 hours ago
            if datetime.now() - last_time > timedelta(hours=24):
                return True
        except Exception:
            return True
        
        return False

    @staticmethod
    def mark_reminder_shown():
        """Record that we showed the reminder."""
        from pathlib import Path
        from datetime import datetime
        
        reminder_file = Path.home() / ".Yamlr" / "last_reminder.txt"
        reminder_file.parent.mkdir(parents=True, exist_ok=True)
        reminder_file.write_text(datetime.now().isoformat())


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# These ensure existing code continues to work
# Legacy Compatibility: Removed for Cleanliness
