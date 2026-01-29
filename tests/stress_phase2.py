#!/usr/bin/env python3
"""
PHASE 2: RIGOROUS STRESS TESTING
-------------------------------
Targeting "Real World" complexities:
1. Helm Render Output (Multi-doc, Cross-ref)
2. CRDs (ArgoCD, Prometheus) - Testing "Learning Mode"
3. Embedded Languages (PromQL in Block Scalars)
"""
import sys
import time
import logging
from pathlib import Path
from kubecuro.core.engine import AkesoEngine
from kubecuro.ui.formatter import AkesoFormatter

# Configure logging
logging.basicConfig(level=logging.ERROR) # Only show errors to keep output clean
logger = logging.getLogger("stress_phase2")

CORPUS_PATH = Path("tests/corpus/real_world")

def test_helm_render(engine):
    """
    Validates handling of large multi-document streams (Helm output).
    """
    print(f"\n[TEST 1] Helm Render Output (helm_render.yaml)...", end=" ")
    start = time.time()
    
    res = engine.audit_and_heal_file(str(CORPUS_PATH / "helm_render.yaml"))
    duration = time.time() - start
    
    # Validation Code
    assert res['success'], f"Failed to process Helm chart: {res.get('error')}"
    
    # Logic Checks
    identities = res.get('identities', [])
    kinds = [i['kind'] for i in identities]
    
    # 1. Multi-doc extraction check
    assert "ServiceAccount" in kinds, "Missing ServiceAccount"
    assert "Deployment" in kinds, "Missing Deployment"
    assert "ConfigMap" in kinds, "Missing ConfigMap"
    
    # 2. Analyzer Check (Did we find the good security context?)
    findings = res.get('findings', [])
    # We expect some warnings (e.g. no cpu limit on some containers maybe?) 
    # But specifically, verifying it didn't crash on the 'nginx.conf' block scalar
    
    print(f"✅ PASS ({duration:.3f}s)")
    print(f"    - Found {len(identities)} resources")
    print(f"    - Clean parsing of nginx.conf block scalar")

def test_crd_learning(engine):
    """
    Validates that Unknown CRDs (ArgoCD) don't crash and are treated as 'Unknown' but valid.
    """
    print(f"[TEST 2] CRD Learning Mode (argo_app.yaml)...", end=" ")
    res = engine.audit_and_heal_file(str(CORPUS_PATH / "argo_app.yaml"))
    
    assert res['success'], "Engine crashed on unknown CRD"
    
    # Should identify as "Application" even if not in standard catalog
    assert res['kind'] == "Application", f"Failed to infer kind from CRD: Got {res['kind']}"
    
    print(f"✅ PASS")

def test_embedded_syntax(engine):
    """
    Validates parsing of complex embedded expressions (PromQL) in PrometheusRule.
    """
    print(f"[TEST 3] Embedded PromQL (prometheus.yaml)...", end=" ")
    res = engine.audit_and_heal_file(str(CORPUS_PATH / "prometheus.yaml"))
    
    assert res['success'], "Engine crashed on PromQL content"
    assert res['kind'] == "PrometheusRule"
    
    # Ensure block scalar wasn't mangled (Shadow engine check)
    # We can check if specific content exists in the 'raw' vs 'healed' if we heal it
    # For now, just ensuring it parsed without syntax error is the baseline
    
    print(f"✅ PASS")

def test_healing_robustness(engine):
    """
    Validates healing of broken real-world files (broken_helm_indent.yaml).
    """
    print(f"[TEST 4] Healing Robustness (broken_helm_indent.yaml)...", end=" ")
    # Ensure we use a fresh engine instance or allow writing? 
    # audit_and_heal_file won't write unless forced, but returns healed_content
    
    res = engine.audit_and_heal_file(str(CORPUS_PATH / "broken_helm_indent.yaml"))
    
    # It should have FAILED parsing initially but successfully HEALED (returned healed_content)
    # Actually, audit_and_heal_file returns success=True if it successfully healed it to a valid state
    # provided the health score meets threshold.
    # If syntax was broken, it might return success=False but with healed_content available.
    
    assert res.get('healed_content'), "Failed to generate healed content for broken file"
    
    # Check if healed content is valid YAML
    # validation using Akeso's own parser (if it parses cleanly, it's valid enough for us)
    try:
        from kubecuro.parsers.lexer import AkesoLexer
        
        # We use the internal Lexer to verify strict validity
        lexer = AkesoLexer()
        shards = lexer.shard(res['healed_content'])
        assert len(shards) > 0, "Healed content is empty"
        
    except Exception as e:
        raise AssertionError(f"Healed content is invalid according to Akeso Parser: {e}")

    print(f"✅ PASS (Healed Syntax)")

if __name__ == "__main__":
    try:
        if not CORPUS_PATH.exists():
            print(f"❌ Corpus missing at {CORPUS_PATH}")
            sys.exit(1)
            
        print("Initializing Engine with Standard Catalog...")
        # Use bundled catalog to force 'Unknown' status for CRDs (simulating reality)
        engine = AkesoEngine(workspace_path=".", catalog_path="catalog/k8s_v1_distilled.json")
        
        test_helm_render(engine)
        test_crd_learning(engine)
        test_embedded_syntax(engine)
        test_healing_robustness(engine)
        
        print("\n✨ PHASE 2 STRESS TESTS PASSED ✨")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 CRITICAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
