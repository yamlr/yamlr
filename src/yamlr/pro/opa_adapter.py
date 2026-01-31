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
        opa_input = [ident.to_dict() for ident in identities]
        
        # 2. Try to run Real OPA Binary
        opa_exe = shutil.which("opa")
        
        if opa_exe and self.policy_path:
            try:
                # Run OPA: opa eval -I -b bundle/ -d data.yamlr.deny input
                # We assume the bundle defines 'data.yamlr.deny' which returns a list of violations
                cmd = [
                    opa_exe, "eval", 
                    "-I", # Read input from stdin
                    "--bundle", self.policy_path,
                    "--format", "json",
                    "data.yamlr.deny"
                ]
                
                process = subprocess.Popen(
                    cmd, 
                    stdin=subprocess.PIPE, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=json.dumps(opa_input))
                
                if process.returncode != 0:
                    logger.warning(f"OPA execution failed: {stderr}")
                else:
                    return self.ingest_opa_json(stdout, identities)
                    
            except Exception as e:
                logger.error(f"OPA Subprocess failed: {e}")

        # 3. Fallback: Demo Mode (Mock Internal Policies)
        # Used when OPA is not installed or no bundle provided
        logger.info("Running OPA in DEMO/EMBEDDED mode (Internal Policies)")
        
        for ident in identities:
            # Policy 1: Require Cost Centers for Deployments
            if ident.kind == "Deployment":
                labels = getattr(ident, "labels", {}) or {}
                
                if "cost-center" not in labels:
                    results.append(AnalysisResult(
                        analyzer_name="OPA Policy Engine",
                        severity="ERROR",
                        message="[Policy] Missing required label: cost-center",
                        resource_name=ident.name or "Unknown",
                        resource_kind=ident.kind,
                        file_path=getattr(ident, 'file_path', 'unknown'),
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
                    suggestion=v.get("fix", None)
                ))
                
        except Exception as e:
            logger.error(f"Failed to parse OPA JSON: {e}")
            
        return results
