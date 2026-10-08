import subprocess
import sys
import unittest


class BootstrapTests(unittest.TestCase):
    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "netlab.cli", "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: netlab", result.stdout)
