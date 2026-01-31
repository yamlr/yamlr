
import unittest
import sys
import os
from io import StringIO
from typing import List

# Mock environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from yamlr.models import ManifestIdentity, Shard
from yamlr.analyzers.cross_resource import CrossResourceAnalyzer
from yamlr.parsers.scanner import KubeScanner
from yamlr.parsers.lexer import KubeLexer

class TestLegacyFeatures(unittest.TestCase):
    def setUp(self):
        self.analyzer = CrossResourceAnalyzer(pro_mode=False)
        self.scanner = KubeScanner()

    def test_service_port_mismatch(self):
        yaml_content = """
apiVersion: v1
kind: Service
metadata:
  name: web-svc
  namespace: default
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 9090 # MISMATCH (Pod has 8080)
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deploy
  namespace: default
spec:
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 8080 # Correct port
"""
        shards = KubeLexer().shard(yaml_content)
        identities = self.scanner.scan_shards(shards)
        
        # Verify extraction worked
        svc = next(i for i in identities if i.kind == "Service")
        deploy = next(i for i in identities if i.kind == "Deployment")
        
        print(f"DEBUG: Service Ports: {svc.service_ports}")
        print(f"DEBUG: Deploy Ports: {deploy.container_ports}")
        
        results = self.analyzer.analyze(identities)
        
        found = False
        for res in results:
            if "Service port targets '9090'" in res.message:
                found = True
                print(f"PASS: Detected mismatch: {res.message}")
        
        self.assertTrue(found, "Failed to detect Service port mismatch")

    def test_ingress_orphan_service(self):
        yaml_content = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  namespace: logic-test
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: missing-svc # ORPHAN
            port:
              number: 80
"""
        shards = KubeLexer().shard(yaml_content)
        identities = self.scanner.scan_shards(shards)
        print(f"DEBUG: Ingress Backends: {identities[0].ingress_backends}")
        
        results = self.analyzer.analyze(identities)
        
        found = False
        for res in results:
            if "references missing Service 'missing-svc'" in res.message:
                found = True
        
        self.assertTrue(found, "Failed to detect orphan Ingress backend")

if __name__ == '__main__':
    unittest.main()
