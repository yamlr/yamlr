
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from yamlr.parsers.lexer import YamlrLexer
from yamlr.parsers.structurer import YamlrStructurer

def debug_structure():
    content = """apiVersion: v1
kind: Service
metadata:
  name: my-service
spec
  ports:
    - port: "80'  # String port (should be int)
  selector:
    app: missing-app
"""
    print("--- INPUT ---")
    print(content)
    
    # 1. Lex
    lexer = YamlrLexer()
    shards = lexer.shard(content)
    
    print("\n--- TOKENS (SHARDS) ---")
    for s in shards:
        # Simplified token view
        try:
            indent = "  " * s.indent
            print(f"L{s.line_no} | {indent}{s.key}: {s.value} (Type: {s.type}) [Indent: {s.indent}]")
        except:
             print(f"RAW: {s}")
        
    # 2. Structure
    mock_catalog = {"Service": {"fields": {}}}
    structurer = YamlrStructurer(catalog=mock_catalog)
    # _build_tree is internal but accessible for debugging
    result = structurer._build_tree(shards, default_kind="Service")
    
    print("\n--- OUTPUT (DICT) ---")
    import json
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    debug_structure()
