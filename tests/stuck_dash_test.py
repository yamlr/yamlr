
import unittest
import sys
import os

# Mock environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from yamlr.parsers.lexer import KubeLexer
from yamlr.parsers.scanner import KubeScanner
from yamlr.parsers.structurer import KubeStructurer
from yamlr.core.context import HealContext

class TestStuckDash(unittest.TestCase):
    def test_stuck_dash_repair(self):
        # Input has NO SPACE between dash and key
        bad_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: test
spec:
  containers:
  -name: nginx # STUCK DASH
   image: nginx
"""
        lexer = KubeLexer()
        scanner = KubeScanner()
        structurer = KubeStructurer(catalog={})
        
        # 1. Lex
        shards = lexer.shard(bad_yaml)
        
        # Verify Shard correctness
        # Must select the Container name, not Metadata name
        cont_name_shard = next(s for s in shards if s.key == "name" and s.value == "nginx")
        self.assertTrue(cont_name_shard.is_list_item, "Lexer failed to identify list item")
        self.assertEqual(cont_name_shard.key, "name", "Lexer failed to extract key")
        
        # 2. Scan (Identity)
        identities = scanner.scan_shards(shards)
        
        # 3. Structure (Rebuild)
        ctx = HealContext(raw_text=bad_yaml)
        ctx.shards = shards
        ctx.identities = identities
        
        docs = structurer.reconstruct(ctx)
        output = structurer.serialize(docs)
        
        print(f"DEBUG Output:\n{output}")
        
        # Verify Output Syntax
        self.assertIn("- name: nginx", output)
        self.assertNotIn("-name: nginx", output)

if __name__ == '__main__':
    unittest.main()
