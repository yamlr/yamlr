
import os
import shutil
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from kubecuro.core.engine import AkesoEngine
from kubecuro.core.io import FileSystemManager

def test_backup_location():
    cwd = Path.cwd()
    print(f"DEBUG: CWD = {cwd}")
    
    # 1. Initialize Engine
    engine = AkesoEngine(
        workspace_path=".", 
        catalog_path="d:/akeso/catalog/k8s_v1_distilled.json",
        app_name="kubecuro"
    )
    
    print(f"DEBUG: Engine app_name = {engine.app_name}")
    print(f"DEBUG: IO app_name = {engine.fs.app_name}")
    print(f"DEBUG: IO state_dir = {engine.fs.state_dir}")
    print(f"DEBUG: IO backup_dir = {engine.fs.backup_dir}")
    
    # 2. Check Directories
    if not engine.fs.backup_dir.exists():
        print("DEBUG: Backup dir does not exist! Creating...")
        engine.fs.ensure_workspace()
    else:
        print("DEBUG: Backup dir exists.")

    # 3. Simulate Backup
    test_file = cwd / "tests" / "backup_test.yaml"
    if not test_file.exists():
        with open(test_file, 'w') as f: f.write("test content")
        
    print(f"DEBUG: Test file = {test_file}")
    
    try:
        backup_path = engine.fs.create_backup(test_file)
        print(f"DEBUG: Backup created at: {backup_path}")
    except Exception as e:
        print(f"DEBUG: Backup failed: {e}")

if __name__ == "__main__":
    test_backup_location()
