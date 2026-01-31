"""
Yamlr CORE ANALYZERS (Best Practices)
----------------------------------------
Standard Kubernetes policy checks implemented as Yamlr Analyzers.
"""
from typing import List, Dict, Any
from yamlr.analyzers.base import BaseAnalyzer, AnalysisResult

class ResourceAnalyzer(BaseAnalyzer):
    """Enforces CPU/Memory requests and limits."""
    
    @property
    def name(self) -> str: return "resource-limit-check"

    @property
    def analyzer_type(self) -> str: return "content"
    
    def analyze(self, resources: List[Dict[str, Any]], **kwargs) -> List[AnalysisResult]:
        results = []
        for resource in resources:
            kind = resource.get("kind", "")
            if kind not in ["Deployment", "StatefulSet", "DaemonSet", "Pod"]:
                continue

        containers = self._get_containers(resource)
        for container in containers:
            name = container.get("name", "unknown")
            resources = container.get("resources", {})
            r_name = resource.get("metadata", {}).get("name", "unknown")
            r_kind = resource.get("kind", "unknown")
            
            # Check Requests
            if not resources.get("requests"):
                results.append(AnalysisResult(
                    analyzer_name=self.name,
                    rule_id="resources/missing-requests",
                    severity="warning",
                    message=f"Container '{name}' has no resource requests defined",
                    resource_name=r_name,
                    resource_kind=r_kind,
                    file_path="unknown",
                    line_number=0 
                ))
            
            # Check Limits
            if not resources.get("limits"):
                results.append(AnalysisResult(
                    analyzer_name=self.name,
                    rule_id="resources/missing-limits",
                    severity="warning",
                    message=f"Container '{name}' has no resource limits defined",
                    resource_name=r_name,
                    resource_kind=r_kind,
                    file_path="unknown",
                    line_number=0
                ))
        return results

    def _get_containers(self, resource: Dict) -> List[Dict]:
        """Helper to extract containers from various workloads."""
        kind = resource.get("kind")
        if kind == "Pod":
            return resource.get("spec", {}).get("containers", [])
        # Workloads
        return resource.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])


class ImageAnalyzer(BaseAnalyzer):
    """Enforces image tagging best practices."""
    
    @property
    def name(self) -> str: return "image-tag-check"

    @property
    def analyzer_type(self) -> str: return "content"
    
    def analyze(self, resources: List[Dict[str, Any]], **kwargs) -> List[AnalysisResult]:
        results = []
        for resource in resources:
            kind = resource.get("kind", "")
            if kind not in ["Deployment", "StatefulSet", "DaemonSet", "Job", "Pod"]:
                continue

        containers = self._get_containers(resource)
        for container in containers:
            image = container.get("image", "")
            if not image: continue
            
            if ":" not in image or image.endswith(":latest"):
                r_name = resource.get("metadata", {}).get("name", "unknown")
                r_kind = resource.get("kind", "unknown")
                results.append(AnalysisResult(
                    analyzer_name=self.name,
                    rule_id="images/no-latest",
                    severity="error",
                    message=f"Container uses '{image}'. Do not use ':latest' tag in production.",
                    resource_name=r_name,
                    resource_kind=r_kind,
                    file_path="unknown",
                    line_number=0
                ))
        return results
    
    def _get_containers(self, resource: Dict) -> List[Dict]:
        kind = resource.get("kind")
        if kind == "Pod":
            return resource.get("spec", {}).get("containers", [])
        return resource.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])


class SecurityAnalyzer(BaseAnalyzer):
    """Enforces Pod Security Standards (Baseline/Restricted)."""
    
    @property
    def name(self) -> str: return "security-check"

    @property
    def analyzer_type(self) -> str: return "content"
    
    def analyze(self, resources: List[Dict[str, Any]], **kwargs) -> List[AnalysisResult]:
        results = []
        for resource in resources:
            kind = resource.get("kind", "")
            if kind not in ["Deployment", "StatefulSet", "DaemonSet", "Pod"]:
                continue

        pod_spec = self._get_pod_spec(resource)
        if not pod_spec: return []
        
        # Check RunAsNonRoot (Pod Level)
        security_ctx = pod_spec.get("securityContext", {})
        r_name = resource.get("metadata", {}).get("name", "unknown")
        r_kind = resource.get("kind", "unknown")
        
        if not security_ctx.get("runAsNonRoot", False):
             results.append(AnalysisResult(
                analyzer_name=self.name,
                rule_id="security/run-as-non-root",
                severity="error", 
                message="Pod securityContext should set 'runAsNonRoot: true'",
                resource_name=r_name,
                resource_kind=r_kind,
                file_path="unknown",
                line_number=0
            ))

        # Check Privileged (Container Level)
        for container in pod_spec.get("containers", []):
            ctx = container.get("securityContext", {})
            if ctx.get("privileged", False):
                results.append(AnalysisResult(
                    analyzer_name=self.name,
                    rule_id="security/no-privileged",
                    severity="error",
                    message=f"Container '{container.get('name')}' is running in Privileged mode.",
                    resource_name=r_name,
                    resource_kind=r_kind,
                    file_path="unknown",
                    line_number=0
                ))

        return results

    def _get_pod_spec(self, resource: Dict) -> Dict:
        kind = resource.get("kind")
        if kind == "Pod": return resource.get("spec", {})
        return resource.get("spec", {}).get("template", {}).get("spec", {})


class ProbeAnalyzer(BaseAnalyzer):
    """Ensures availability checks are defined."""
    
    @property
    def name(self) -> str: return "probe-check"

    @property
    def analyzer_type(self) -> str: return "content"
    
    def analyze(self, resources: List[Dict[str, Any]], **kwargs) -> List[AnalysisResult]:
        results = []
        for resource in resources:
            kind = resource.get("kind", "")
            if kind not in ["Deployment", "StatefulSet", "DaemonSet"]: # Jobs don't need probes
                continue

        containers = self._get_pod_spec(resource).get("containers", [])
        r_name = resource.get("metadata", {}).get("name", "unknown")
        r_kind = resource.get("kind", "unknown")
        
        for container in containers:
            name = container.get("name")
            
            if "livenessProbe" not in container:
                results.append(AnalysisResult(
                    analyzer_name=self.name,
                    rule_id="probes/missing-liveness",
                    severity="warning",
                    message=f"Container '{name}' missing livenessProbe",
                    resource_name=r_name,
                    resource_kind=r_kind,
                    file_path="unknown",
                    line_number=0
                ))
                
            if "readinessProbe" not in container:
                results.append(AnalysisResult(
                    analyzer_name=self.name,
                    rule_id="probes/missing-readiness",
                    severity="warning",
                    message=f"Container '{name}' missing readinessProbe",
                    resource_name=r_name,
                    resource_kind=r_kind,
                    file_path="unknown",
                    line_number=0
                ))
        return results

    def _get_pod_spec(self, resource: Dict) -> Dict:
        return resource.get("spec", {}).get("template", {}).get("spec", {})
