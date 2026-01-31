#!/usr/bin/env python3
"""
SETUP SIMULATION
----------------
Generates a "Real World" messy cluster dump for testing Yamlr's batch processing,
UI reporting, and safety mechanisms.

Output Structure:
tests/simulation/cluster_dump/
  ├── namespaces/
  │   ├── default/
  │   │   ├── frontend.yaml       (Valid)
  │   │   └── backend.yaml        (Valid)
  │   └── legacy/
  │       └── database.yaml       (Deprecated API: extensions/v1beta1)
  ├── violations/
  │   ├── security/
  │   │   └── root_pod.yaml       (Security: runAsRoot)
  │   ├── resources/
  │   │   └── no_limits.yaml      (BestPractice: missing requests/limits)
  │   └── logic/
  │       └── ghost_service.yaml  (Logic: Selector mismatch)
  └── garbage/
      ├── norway.yaml             (Syntax: NO/ON booleans)
      ├── indent_hell.yaml        (Syntax: Broken indentation)
      └── random.bin              (Ignored: Non-YAML file)
"""

import os
# import yaml (Unused)
from pathlib import Path

BASE_DIR = Path("tests/simulation/cluster_dump")

def write_file(path: str, content: str):
    full_path = BASE_DIR / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {full_path}")

def setup():
    if BASE_DIR.exists():
        import shutil
        shutil.rmtree(BASE_DIR)
    
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Valid Namespace
    write_file("namespaces/default/frontend.yaml", """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: default
  labels:
    app: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
""")

    # 2. Legacy API (Deprecation)
    write_file("namespaces/legacy/database.yaml", """
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: mongo-legacy
  namespace: legacy
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: mongo
        image: mongo:4.0
""")

    # 3. Security Violation
    write_file("violations/security/root_pod.yaml", """
apiVersion: v1
kind: Pod
metadata:
  name: root-runner
spec:
  containers:
  - name: ubuntu
    image: ubuntu:latest
    securityContext:
      privileged: true
      runAsUser: 0
""")

    # 4. Resource Violation
    write_file("violations/resources/no_limits.yaml", """
apiVersion: v1
kind: Pod
metadata:
  name: hungry-pod
spec:
  containers:
  - name: worker
    image: busybox
    # Missing resources block entirely
""")

    # 5. Logical Ghost Service
    write_file("violations/logic/ghost_service.yaml", """
apiVersion: v1
kind: Service
metadata:
  name: ghost-svc
spec:
  selector:
    app: non-existent-app
  ports:
  - port: 80
""")

    # 6. Syntax: Norway Problem
    write_file("garbage/norway.yaml", """
apiVersion: v1
kind: ConfigMap
metadata:
  name: country-codes
data:
  code: NO
  active: ON
""")

    # 7. Syntax: Indentation Error
    write_file("garbage/indent_hell.yaml", """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-indent
spec:
  replicas: 1
    selector:  # Wrong indent
    matchLabels:
      app: test
""")

    # 8. Ignored File
    write_file("garbage/random.txt", "This is not a YAML file and should be ignored.")

if __name__ == "__main__":
    setup()
    print("\\nSimulation Environment Ready.")
