#!/usr/bin/env python3
"""
Akeso Pro - Intelligent Cluster Version Detection
"""
import os
import subprocess
import json
from pathlib import Path
from typing import Optional

class ClusterDetection:
    """Pro-only: Advanced cluster version detection"""
    
    PROFILES_PATH = Path.home() / ".akeso" / "cluster_profiles.json"
    
    @staticmethod
    def detect_from_kubectl() -> Optional[str]:
        """
        💎 Pro: Auto-detect from kubectl.
        
        Runs: kubectl version --short
        Parses: Server Version: v1.28.3
        
        Returns:
            Optional[str]: Detected version or None
        """
        try:
            result = subprocess.run(
                ["kubectl", "version", "--short"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "Server Version:" in line:
                        version = line.split(":")[-1].strip()
                        # Extract major.minor (v1.28)
                        parts = version.split(".")
                        if len(parts) >= 2:
                            detected = f"{parts[0]}.{parts[1]}"
                            print(f"💎 Pro: Auto-detected K8s {detected} from kubectl")
                            return detected
        except Exception as e:
            print(f"⚠️  kubectl detection failed: {e}")
        
        return None
    
    @staticmethod
    def detect_from_cluster() -> Optional[str]:
        """
        💎 Pro: Query live cluster API.
        
        Uses kubectl to query /version endpoint.
        
        Returns:
            Optional[str]: Detected version or None
        """
        try:
            result = subprocess.run(
                ["kubectl", "get", "--raw", "/version"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                version_info = json.loads(result.stdout)
                major = version_info.get("major", "1")
                minor = version_info.get("minor", "31")
                detected = f"v{major}.{minor}"
                print(f"💎 Pro: Auto-detected K8s {detected} from cluster API")
                return detected
        except Exception as e:
            print(f"⚠️  Cluster detection failed: {e}")
        
        return None
    
    @staticmethod
    def get_profile_version() -> Optional[str]:
        """
        💎 Pro: Load version from saved cluster profile.
        
        Profiles stored in ~/.akeso/cluster_profiles.json:
        {
            "dev-cluster": "v1.28",
            "prod-cluster": "v1.31"
        }
        
        Returns:
            Optional[str]: Profile version or None
        """
        if not ClusterDetection.PROFILES_PATH.exists():
            return None
        
        try:
            with open(ClusterDetection.PROFILES_PATH, 'r') as f:
                profiles = json.load(f)
            
            # Get current kubectl context
            result = subprocess.run(
                ["kubectl", "config", "current-context"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                current_context = result.stdout.strip()
                if current_context in profiles:
                    version = profiles[current_context]
                    print(f"💎 Pro: Using saved profile for '{current_context}': {version}")
                    return version
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def save_profile(context_name: str, version: str):
        """
        💎 Pro: Save cluster version to profile.
        
        Usage:
            akeso config set-version dev-cluster 1.28
        """
        ClusterDetection.PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        profiles = {}
        if ClusterDetection.PROFILES_PATH.exists():
            with open(ClusterDetection.PROFILES_PATH, 'r') as f:
                profiles = json.load(f)
        
        profiles[context_name] = version
        
        with open(ClusterDetection.PROFILES_PATH, 'w') as f:
            json.dump(profiles, f, indent=2)
        
        print(f"✅ Saved: {context_name} → {version}")
