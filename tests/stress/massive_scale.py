import os
import time
import shutil
import random
import tempfile
import psutil
from rich.console import Console
from yamlr.core.engine import YamlrEngine

console = Console()

def generate_massive_corpus(root_path: str, count: int = 1000):
    """Generates a mix of valid, broken, and garbage files."""
    console.print(f"[cyan]Generatng {count} files in {root_path}...[/cyan]")
    
    os.makedirs(root_path, exist_ok=True)
    
    templates = [
        # Valid
        """apiVersion: v1
kind: Service
metadata:
  name: service-{i}
spec:
  ports:
  - port: 80
  selector:
    app: nginx-{i}
""",
        # Broken (Missing Colon)
        """apiVersion: apps/v1
kind: Deployment
metadata:
  name: deploy-{i}
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nginx
        image nginx:latest
""",
        # Garbage (Mixed Indent)
        """apiVersion: v1
kind: Pod
metadata:
  name: pod-{i}
spec:
   containers:
     - name: busybox
       image: busybox
"""
    ]
    
    for i in range(count):
        content = random.choice(templates).format(i=i)
        with open(os.path.join(root_path, f"manifest_{i}.yaml"), "w") as f:
            f.write(content)

def run_scale_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Generate Files
        generate_massive_corpus(temp_dir, count=2000)
        
        # 2. Measure Memory/Time
        process = psutil.Process()
        start_mem = process.memory_info().rss / 1024 / 1024
        start_time = time.time()
        
        # 3. Init Engine
        # Write dummy catalog for isolation
        dummy_catalog = os.path.join(temp_dir, "catalog.json")
        with open(dummy_catalog, "w") as f:
            f.write('{"schemas": {}, "version": "v1.31-stress"}')
            
        engine = YamlrEngine(
            workspace_path=temp_dir, 
            app_name="yamlr",
            catalog_path=dummy_catalog
        )
        
        print(f"Starting Scan...")
        results = engine.batch_heal(
            root_path=temp_dir,
            extensions=[".yaml"],
            max_depth=5,
            dry_run=True
        )
        
        end_time = time.time()
        end_mem = process.memory_info().rss / 1024 / 1024
        
        duration = end_time - start_time
        
        console.print(f"\n[bold green]Scale Test Complete[/bold green]")
        console.print(f"Files Processed: {len(results)}")
        console.print(f"Time Taken: {duration:.2f}s (Avg: {duration/2000*1000:.2f}ms/file)")
        console.print(f"Memory Delta: {end_mem - start_mem:.2f} MB")
        
        if len(results) != 2000:
            console.print("[red]FAILED: Did not process all files![/red]")
            exit(1)
            
        console.print("[green]PASSED[/green]")

if __name__ == "__main__":
    run_scale_test()
