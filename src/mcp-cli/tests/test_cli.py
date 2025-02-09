import unittest
import subprocess
import os

class TestCLI(unittest.TestCase):

    CLI_PATH = "main.py"  # Path to your CLI script
    CLI_DIR = "." # Path to the CLI directory

    def run_cli(self, *args):
        """Runs the CLI command and returns the output."""
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = os.getcwd()  # Add current directory to PYTHONPATH
            result = subprocess.run(
                ["python", self.CLI_PATH] + list(args),
                capture_output=True,
                text=True,
                cwd=self.CLI_DIR,  # Ensure correct working directory
                env=env,
                check=True  # Raise exception on non-zero exit code
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.fail(f"CLI command failed: {e.stderr}")

    def test_info_command(self):
        """Tests the 'info' command."""
        output = self.run_cli("info")
        self.assertIn("Name: ContextCoin", output)
        self.assertIn("Symbol: CTX", output)

    def test_help_command(self):
        """Tests the CLI's help output."""
        output = self.run_cli("--help")
        self.assertIn("ContextCoin (CTX) Solana CLI", output)
        self.assertIn("info", output)
        self.assertIn("balance", output)

    # Add more tests as you develop the CLI

if __name__ == "__main__":
    unittest.main()