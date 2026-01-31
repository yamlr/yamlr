
"""
Yamlr Enterprise: Authentication Manager
----------------------------------------
Manages user sessions, JWT storage, and verification.

Flow:
1. `yamlr auth login` -> Opens browser for SSO.
2. Callback receives JWT.
3. Token stored in `~/.yamlr/credentials`.
4. Pro features verify token signature before execution.

Author: Yamlr Team
"""

import os
import json
import time
import base64
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger("yamlr.pro.auth")

class AuthManager:
    """Manages Enterprise Authentication state."""
    
    def __init__(self, app_name: str = "Yamlr"):
        self.app_name = app_name
        self.config_dir = Path.home() / f".{app_name.lower()}"
        self.creds_file = self.config_dir / "credentials"
        self._token_cache = None

    def login(self) -> bool:
        """
        Initiates the Device Authorization Flow.
        For MVP: Simulates a login by prompting for a token or generating a mock one.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Opening browser to https://auth.yamlr.io/device ...")
        print("Waiting for authentication...")
        
        # Simulate Network Delay
        time.sleep(1.5)
        
        # In a real app, we'd poll an endpoint or listen on a localhost port.
        # For this demo, we'll generate a "mock" valid token.
        mock_token = self._generate_mock_token()
        
        self.save_credentials(mock_token)
        print("✅ Successfully authenticated as demo-user@yamlr.io")
        return True

    def logout(self):
        """Removes stored credentials."""
        if self.creds_file.exists():
            self.creds_file.unlink()
            logger.info("Credentials removed.")
            print("Logged out.")
        else:
            print("No active session found.")

    def get_token(self) -> Optional[str]:
        """Retrieves and validates the current access token."""
        if self._token_cache:
            return self._token_cache
            
        if not self.creds_file.exists():
            return None
            
        try:
            data = json.loads(self.creds_file.read_text(encoding='utf-8'))
            token = data.get("access_token")
            # In real world: check expiry here
            self._token_cache = token
            return token
        except Exception as e:
            logger.warning(f"Failed to read credentials: {e}")
            return None

    def save_credentials(self, token: str):
        """Persists the token securely."""
        data = {
            "access_token": token,
            "token_type": "Bearer",
            "expiry": time.time() + 3600  # 1 hour
        }
        # Secure the file (Unix only, strictly speaking)
        if hasattr(os, 'chmod'):
            # Create file first if not exists
            if not self.creds_file.exists():
                self.creds_file.touch(mode=0o600)
            
        self.creds_file.write_text(json.dumps(data), encoding='utf-8')
        if hasattr(os, 'chmod'):
             os.chmod(self.creds_file, 0o600)
        
        self._token_cache = token

    def validate_session(self) -> bool:
        """Checks if the user has a valid active session."""
        token = self.get_token()
        if not token:
            return False
        
        try:
            # Simple Mock Validation: Check structure and decode payload
            parts = token.split('.')
            if len(parts) != 3:
                return False
                
            # Padding fix for base64 decode
            payload_segment = parts[1]
            padding = '=' * (4 - (len(payload_segment) % 4))
            payload_json = base64.urlsafe_b64decode(payload_segment + padding).decode()
            payload = json.loads(payload_json)
            
            return payload.get("iss") == "yamlr-demo"
        except Exception as e:
            logger.debug(f"Token validation failed: {e}")
            return False

    def _generate_mock_token(self) -> str:
        """Generates a dummy JWT-like string for the demo."""
        # Header: {"alg": "HS256", "typ": "JWT"}
        header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        # Payload: {"sub": "1234567890", "name": "Demo User", "iat": 1516239022}
        payload = base64.urlsafe_b64encode(json.dumps({
            "sub": "user_001",
            "email": "demo-user@yamlr.io",
            "tier": "enterprise",
            "iss": "yamlr-demo"
        }).encode()).decode().strip("=")
        
        signature = "mock-signature-hash"
        return f"{header}.{payload}.{signature}"

# Singleton instance
auth_device = AuthManager()
