
import os
import sys
import shutil
import tempfile
import logging
from yamlr.core.engine import YamlrEngine

logging.basicConfig(level=logging.INFO)

def test_graph():
    work_dir = tempfile.mkdtemp()
    try:
        engine = YamlrEngine(
            workspace_path=work_dir,
            catalog_path=os.path.join(os.path.dirname(__file__), "../catalog/k8s_v1_distilled.json")
        )
        
        # Valid Scenario (Run 2 only)
        with open(os.path.join(work_dir, "service.yaml"), "w") as f:
            f.write("apiVersion: v1\nkind: Service\nmetadata:\n  name: my-svc\nspec:\n  selector:\n    app: nginx\n  ports:\n  - port: 80")
            
        with open(os.path.join(work_dir, "deploy.yaml"), "w") as f:
            f.write("apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: my-dep\n  labels:\n    app: nginx\nspec:\n  selector:\n    matchLabels:\n      app: nginx\n  template:\n    metadata:\n      labels:\n        app: nginx\n    spec:\n      containers:\n      - name: nginx\n        image: nginx")

        print("\n--- RUN: Graph Scan ---")
        results = engine.batch_heal(work_dir, ["yaml"], dry_run=True)
        
        # DEBUG: Print all identities found
        for r in results:
            print(f"DEBUG FILE: {r['file_path']}")
            print(f"DEBUG IDENTITIES: {r.get('identities')}")
        
        svc_res = next(r for r in results if r["file_path"] == "service.yaml")
        ghost_found = any("Ghost Service" in str(f) for f in svc_res["findings"])
        
        if not ghost_found:
            print("✅ PASS: Correctly linked.")
        else:
            print("❌ FAIL: False Positive.")
            print(f"Findings: {svc_res['findings']}")
            
    finally:
        shutil.rmtree(work_dir)

if __name__ == "__main__":
    test_graph()
