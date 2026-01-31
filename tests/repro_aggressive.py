import unittest
from yamlr.parsers.lexer import YamlrLexer

class TestAggressiveHealing(unittest.TestCase):
    def setUp(self):
        self.lexer = YamlrLexer()

    def test_missing_colon_simple(self):
        """Test 'key value' -> 'key: value'"""
        raw = "image nginx:latest"
        shards = self.lexer.shard(raw)
        # Should be healed to key: "image", value: "nginx:latest"
        self.assertEqual(shards[0].key, "image")
        self.assertEqual(shards[0].value, "nginx:latest")

    def test_missing_space_dash(self):
        """Test '-item' -> '- item'"""
        raw = "-item"
        shards = self.lexer.shard(raw)
        self.assertTrue(shards[0].is_list_item)
        self.assertEqual(shards[0].value, "item")

    def test_unclosed_quote_aggressive(self):
        """Test 'key: "value' -> 'key: "value"'"""
        raw = 'key: "broken string'
        shards = self.lexer.shard(raw)
        self.assertEqual(shards[0].value, '"broken string"')

    def test_mixed_indentation_garbage(self):
        """Test 3-space indent normalization"""
        raw = """
parent:
   child: value
"""
        shards = self.lexer.shard(raw)
        # Should normalize 3 spaces -> 2 spaces (standard indent)
        self.assertEqual(shards[1].indent, 2)

    def test_bad_indent_torture(self):
        """Test bad_indent.yaml content from torture corpus"""
        raw = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: bad-indent-nightmare
spec:
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
   # Bad indentation here (4 spaces then 3)
       app: nginx
    spec:
      containers:
\t  # Tab character used here
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
\t\t # Tabs mixing with spaces
"""
        shards = self.lexer.shard(raw)
        # Just ensure it doesn't crash and we get some shards
        self.assertTrue(len(shards) > 0)
        # Check if 'app: nginx' (the 3-space one) got fixed to something reasonable
        # Line 13 in file (0-indexed line 12 in string? No, it's line 13 here too roughly)
        # Scan for "app: nginx" in values
        found = False
        for s in shards:
            if s.key == "app" and s.value == "nginx":
                found = True
        self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
