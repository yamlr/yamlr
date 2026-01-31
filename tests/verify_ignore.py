import unittest
from yamlr.parsers.lexer import YamlrLexer

class TestIgnoreMechanism(unittest.TestCase):
    def setUp(self):
        self.lexer = YamlrLexer()

    def test_ignore_snap_to_grid(self):
        """Test that bad indentation is preserved if ignored."""
        # Standard behavior: 3 spaces -> 2 spaces
        normal = "   key: val"
        shards = self.lexer.shard(normal)
        self.assertEqual(shards[0].indent, 2, "Failed baseline: Should heal to 2 spaces")
        
        # Ignored behavior: 3 spaces -> 3 spaces (preserved)
        ignored = "   key: val # yamlr:ignore"
        shards = self.lexer.shard(ignored)
        # We need to check raw_line or reconstructed indent
        # Shard.indent comes from repair_line result
        self.assertEqual(shards[0].indent, 3, "Failed to ignore: Indent was healed!")
        
    def test_ignore_magic_colon(self):
        """Test that missing colon is preserved if ignored."""
        broken = "image nginx # yamlr:ignore"
        shards = self.lexer.shard(broken)
        # Should be parsed as key='image nginx' (or whatever default behavior is without colon)
        # If magic colon worked, it would be key='image', val='nginx'
        
        # Without Magic Colon, "image nginx" -> key='', val='image nginx', is_list=False?
        # Let's check what _extract_semantics does.
        # "image nginx" -> semantics?
        
        print(f"Shard Content: key='{shards[0].key}', val='{shards[0].value}', raw='{shards[0].raw_line}'")
        
        # We verify raw_line wasn't changed
        self.assertIn("image nginx", shards[0].raw_line)
        self.assertNotIn("image:", shards[0].raw_line)

if __name__ == '__main__':
    unittest.main()
