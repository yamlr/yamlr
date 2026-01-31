
import os
import shutil
import tempfile
import logging
from yamlr.core.engine import YamlrEngine

logging.basicConfig(level=logging.INFO)

def test_migration():
    work_dir = tempfile.mkdtemp()
    try:
        # 1. Create Legacy Deployment (extensions/v1beta1)
        # Note: No selector (it was optional back then)
        legacy_yaml = """
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: legacy-app
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: legacy
    spec:
      containers:
      - name: nginx
        image: nginx:1.14
        """
        
        target_file = os.path.join(work_dir, "legacy.yaml")
        with open(target_file, "w") as f:
            f.write(legacy_yaml)

        # 2. Initialize Engine targeting K8s 1.25 (where extensions is DEAD)
        # We simulate this by forcing the target version via CLI args (conceptually)
        # But Engine expects catalog path.
        catalog_path = os.path.join(os.path.dirname(__file__), "../catalog/k8s_v1_distilled.json")
        engine = YamlrEngine(work_dir, catalog_path=catalog_path)
        
        # 3. Heal with Target Version override
        # We assume engine.audit_and_heal_file accepts cluster_version or we pass it via context override?
        # engine.batch_heal doesn't expose cluster_version directly to heal().
        # Wait, heal() takes cluster_version! 
        # But `batch_heal` calls `audit_and_heal_file` which calls `pipeline.heal`.
        # `YamlrEngine.audit_and_heal_file` needs to pass it down.
        
        # Checking engine.py to see if it supports passing version...
        # It uses self.target_cluster_version!
        engine.target_cluster_version = "v1.25"
        
        print("\n--- RUN: Healing Legacy Manifest ---")
        results = engine.batch_heal(work_dir, ["yaml"], dry_run=False) # dry_run=False to see file change? 
        # Actually batch_heal returns the healed content in result['healed_text'].
        
        res = results[0]
        healed_text = res.get("healed_content") or res.get("raw_content") # Fallback for printing
        
        # 4. Verify Upgrades
        print("\n--- Healed Output ---")
        print(healed_text)
        
        if "apiVersion: apps/v1" in healed_text:
            print("✅ UPGRADE SUCCESS: apiVersion upgraded to apps/v1")
        else:
            print("❌ FAIL: apiVersion not upgraded")
            
        if "selector:" in healed_text and "matchLabels:" in healed_text:
             print("✅ SELECTOR SUCCESS: Selector injected")
        else:
             print("❌ FAIL: Selector missing")
             
        # Check audit log for "Prophetic Migration"
        logs = res.get("logic_logs", [])
        if any("Prophetic Migration Applied" in log for log in logs):
            print("✅ AUDIT SUCCESS: Logged migration")
        else:
            print(f"❌ FAIL: Migration not logged. Logs: {logs}")

    finally:
        shutil.rmtree(work_dir)

if __name__ == "__main__":
    test_migration()
