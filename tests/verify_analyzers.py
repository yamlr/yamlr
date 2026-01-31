#!/usr/bin/env python3
"""
VERIFY CORE ANALYZERS
---------------------
Tests the standard best-practice rules:
1. Image Tags (:latest)
2. Resource Limits (Missing)
3. Security Context (Root)
4. Probes (Missing)
"""
import sys
import shutil
import logging
from pathlib import Path
from yamlr.core.engine import YamlrEngine
from yamlr.core.config import ConfigManager

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_analyzers")

TEST_ROOT = Path("tests/analyzer_test_env")

BAD_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bad-practice-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-app:latest  # ERROR: Latest tag
        # WARNING: Missing resources
        # WARNING: Missing probes
        securityContext:
          privileged: true    # ERROR: Privileged
"""

def setup_env():
    if TEST_ROOT.exists(): shutil.rmtree(TEST_ROOT)
    TEST_ROOT.mkdir(parents=True)
    (TEST_ROOT / "bad.yaml").write_text(BAD_MANIFEST, encoding='utf-8')

def test_analyzers():
    logger.info("TEST: Running Core Analyzers")
    
    # DEBUG: Inspect Registry
    from yamlr.analyzers.registry import AnalyzerRegistry
    AnalyzerRegistry.register_defaults() # Force registration to check
    all_analyzers = AnalyzerRegistry.get_all_analyzers()
    logger.info(f"DEBUG: Registry has {len(all_analyzers)} analyzers")
    for a in all_analyzers:
        logger.info(f"  - {a.name} (type: {getattr(a, 'analyzer_type', 'UNKNOWN')})")

    # Init Engine
    engine = YamlrEngine(str(TEST_ROOT), "catalog/k8s_v1_distilled.json")
    
    # Run Audit
    res = engine.audit_and_heal_file("bad.yaml")
    
    # Check Logs for findings
    found_issues = []
    if "logic_logs" in res:
        for log in res["logic_logs"]:
            if "Container uses 'my-app:latest'" in log:
                found_issues.append("latest_tag")
            if "missing-requests" in str(log) or "no resource requests" in str(log):
                found_issues.append("missing_requests")
            if "Privileged mode" in log:
                found_issues.append("privileged")
            if "missing livenessProbe" in log:
                found_issues.append("missing_probes")

    # Assertions
    failures = []
    if "latest_tag" not in found_issues: failures.append("Failed to detect :latest tag")
    if "missing_requests" not in found_issues: failures.append("Failed to detect missing resources")
    if "privileged" not in found_issues: failures.append("Failed to detect privileged container")
    if "missing_probes" not in found_issues: failures.append("Failed to detect missing probes")
    
    if failures:
        logger.error("❌ Analyzer Verification Failed:")
        for f in failures: logger.error(f"  - {f}")
        logger.info("DEBUG LOGS:")
        for l in res.get("logic_logs", []): print(l)
        raise AssertionError("Analyzer check failed")
    
    logger.info("✅ All Core Analyzers Verified Successfully")

if __name__ == "__main__":
    try:
        setup_env()
        test_analyzers()
        print("\n🚀 ANALYZER SYSTEM VERIFIED")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
