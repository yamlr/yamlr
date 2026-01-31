
import subprocess
import unittest
import os
import tempfile
import sys

# Ensure we define how to call the CLI
CLI_CMD = [sys.executable, "-m", "yamlr"]

import re

# Helper to remove ANSI color codes
def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class TestQACertification(unittest.TestCase):
    
    def run_cli(self, args):
        env = os.environ.copy()
        # Add src to PYTHONPATH so the subprocess can find 'yamlr' module
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
        
        cmd = CLI_CMD + args
        # Force strict UTF-8 to avoid encoding issues on Windows
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        return result

    def test_invalid_flag(self):
        """Ensure invalid flags produce friendly error, not stack trace."""
        res = self.run_cli(["--garbage-flag"])
        clean_stderr = strip_ansi(res.stderr)
        clean_stdout = strip_ansi(res.stdout)
        
        print(f"DEBUG Invalid Flag Output: {clean_stdout} / {clean_stderr}")

        self.assertNotEqual(res.returncode, 0, "Invalid flag should exit with non-zero code")
        # argparse output is usually in stderr
        combined = (clean_stderr + clean_stdout).lower()
        self.assertIn("unrecognized arguments", combined)
        self.assertNotIn("traceback (most recent call last)", combined)

    def test_missing_file(self):
        """Ensure missing input file exits gracefully."""
        res = self.run_cli(["heal", "non_existent_file.yaml"])
        clean_stderr = strip_ansi(res.stderr)
        
        self.assertNotEqual(res.returncode, 0, "Missing file should failure")
        self.assertNotIn("Traceback", clean_stderr)
        # Should have some error message
        self.assertTrue(len(clean_stderr) > 0 or len(res.stdout) > 0)

    def test_empty_file(self):
        """Ensure empty file is handled without panic."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            f.close()
            try:
                res = self.run_cli(["scan", f.name]) # Use scan for read-only check
                # It might fail with "no content" or pass. Check no Crash.
                self.assertNotIn("Traceback", strip_ansi(res.stderr))
            finally:
                os.unlink(f.name)

    def test_binary_file(self):
        """Ensure binary file doesn't crash the lexer."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
            f.close()
            try:
                res = self.run_cli(["scan", f.name])
                self.assertNotIn("Traceback", strip_ansi(res.stderr))
            finally:
                os.unlink(f.name)

    def test_deep_nesting(self):
        """Test 100 levels of indentation."""
        content = ""
        for i in range(100):
            content += ("  " * i) + f"level_{i}:\n"
        content += ("  " * 100) + "value: test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=".yaml", delete=False) as f:
            f.write(content)
            f.close()
            try:
                res = self.run_cli(["heal", f.name])
                self.assertNotIn("RecursionError", res.stderr)
                self.assertNotIn("Traceback", res.stderr)
            finally:
                os.unlink(f.name)

    def test_long_line(self):
        """Test extremely long line (>10k chars)."""
        long_str = "a" * 15000
        content = f"apiVersion: v1\nkind: Pod\nmetadata:\n  name: long-pod\n  annotations:\n    note: {long_str}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=".yaml", delete=False) as f:
            f.write(content)
            f.close()
            try:
                res = self.run_cli(["heal", f.name])
                self.assertNotIn("Traceback", res.stderr)
            finally:
                os.unlink(f.name)

if __name__ == '__main__':
    unittest.main()
