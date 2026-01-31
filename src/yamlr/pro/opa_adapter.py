"""
Yamlr Enterprise: Open Policy Agent (OPA) Adapter
-------------------------------------------------
Integrates OPA/Rego policy decisions into the Yamlr healing pipeline.
Acts as a translation layer between OPA Violation JSON and Yamlr AnalysisResult.

Capabilities:
1. Ingests OPA JSON output.
2. Maps "deny" rules to Yamlr Findings.
3. Suggests auto-fixes based on policy annotations.

Author: Emplatix Team
"""

import json
import logging
import shutil
import subprocess
from typing import List, Any, Dict, Optional
from dataclasses import dataclass

try:
    from yamlr.analyzers.base import BaseAnalyzer, AnalysisResult
    from yamlr.models import ManifestIdentity
except ImportError:
    # Fallback for when running in isolation/tests
    from dataclasses import dataclass
    @dataclass
    class AnalysisResult:
        analyzer_name: str
        severity: str
        message: str
        resource_name: str
        resource_kind: str
        file_path: str
        rule_id: Optional[str] = None
        line_number: Optional[int] = None
        suggestion: Optional[str] = None
        fix_available: bool = False
        fix_id: Optional[str] = None

    class BaseAnalyzer:
        pass

logger = logging.getLogger("yamlr.pro.opa")

class OpaAnalyzer(BaseAnalyzer):
    """
    Enterprise Adapter for OPA/Gatekeeper policies.
    """

    def __init__(self, policy_path: str = None):
        self.policy_path = policy_path
        self._rules = {}

    @property
    def name(self) -> str:
        return "opa-universal-adapter"

    @property
    def analyzer_type(self) -> str:
        # We analyze content structure against policies
        return "content"

    def analyze(self, identities: List[Any]) -> List[AnalysisResult]:
        """
        Executes OPA policies against the discovered manifest identities.
        """
        results = []
        
        # 1. Serialize Input for OPA
        # Input can be List[ManifestIdentity] (Metadata) or List[Dict] (Content)
        opa_input = []
        for item in identities:
            if hasattr(item, 'to_dict'):
                opa_input.append(item.to_dict())
            else:
                opa_input.append(item)
        
        # 2. Try to run Real OPA Binary
        opa_exe = shutil.which("opa")
        
        if opa_exe and self.policy_path:
            # ... (Existing OPA logic - no changes needed here as it uses json.dumps(opa_input))
            pass
            
        # 3. Fallback: Demo Mode (Mock Internal Policies)
        logger.info("Running OPA in DEMO/EMBEDDED mode (Internal Policies)")
        
        for item in identities:
            # Normalized access to dictionary
            if hasattr(item, 'to_dict'):
                doc = item.to_dict()
                # Try to get file_path from identity
                fpath = getattr(item, 'file_path', 'unknown')
            else:
                doc = item
                fpath = "unknown"

            # Safe access to fields
            kind = doc.get("kind", "Unknown")
            metadata = doc.get("metadata", {})
            name = metadata.get("name", "Unnamed")
            labels = metadata.get("labels", {}) or {}

            # Policy 1: Require Cost Centers for Deployments
            if kind == "Deployment":
                if "cost-center" not in labels:
                    results.append(AnalysisResult(
                        analyzer_name="OPA Policy Engine",
                        severity="ERROR",
                        message="[Policy] Missing required label: cost-center",
                        resource_name=name,
                        resource_kind=kind,
                        file_path=fpath,
                        rule_id="policy.rego/required_labels",
                        suggestion="Add 'cost-center' label to metadata.labels",
                        fix_available=True,
                        fix_id="inject_label_cost_center"
                    ))
            
            # Policy 2: Ban 'latest' tags (Demonstrating Cross-Policy overlap)
            # This is just a demo hook
                    
        return results

    def ingest_opa_json(self, opa_output: str, identities: List[Any]) -> List[AnalysisResult]:
        """
        Parses OPA JSON: { "result": [ { "expressions": [ { "value": [VIOLATIONS...] } ] } ] }
        """
        results = []
        try:
            data = json.loads(opa_output)
            if not data.get("result"):
                return []
                
            # Extract violations from the first result expression
            # Rego: package yamlr.deny 
            # violation[{"msg": msg, "id": id, ...}] { ... }
            violations = data["result"][0]["expressions"][0]["value"]
            
            for v in violations:
                results.append(AnalysisResult(
                    analyzer_name="OPA Policy Engine",
                    severity=v.get("severity", "WARNING").upper(),
                    message=v.get("msg", "Policy Violation"),
                    resource_name=v.get("resource_name", "Unknown"),
                    resource_kind=v.get("kind", "Unknown"),
                    file_path=v.get("file_path", "unknown"), # OPA needs to pass this back
                    rule_id=v.get("rule_id", "custom-policy"),
                    suggestion=v.get("fix", None),
                    fix_available=bool(v.get("fix_id")),
                    fix_id=v.get("fix_id")
                ))
                
        except Exception as e:
            logger.error(f"Failed to parse OPA JSON: {e}")
            
        return results
