import unittest
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Import module and exception from src
import config
from exceptions import ConfigurationError

# Default values from config.py for comparison
DEFAULT_URL = "http://localhost:8899"

class TestConfig(unittest.TestCase):

    def test_get_cluster_url_default(self):
        """Tests get_cluster_url returns default when env var is not set."""
        # Ensure the env var is unset for this test
        with patch.dict(os.environ, {}, clear=True):
             # Reload config module to pick up the mocked environment
             import importlib
             importlib.reload(config)
             self.assertEqual(config.get_cluster_url(), DEFAULT_URL)

    def test_get_cluster_url_env_var(self):
        """Tests get_cluster_url returns value from env var when set."""
        test_url = "http://custom-url:9000"
        with patch.dict(os.environ, {"SOLANA_CLUSTER_URL": test_url}, clear=True):
             import importlib
             importlib.reload(config)
             self.assertEqual(config.get_cluster_url(), test_url)

    def test_get_program_id_env_var_set(self):
        """Tests get_program_id returns value from env var when set."""
        test_prog_id = "MyProgramId1111111111111111111111111111111"
        with patch.dict(os.environ, {"SOLANA_PROGRAM_ID": test_prog_id}, clear=True):
             import importlib
             importlib.reload(config)
             self.assertEqual(config.get_program_id(), test_prog_id)

    def test_get_program_id_env_var_not_set(self):
        """Tests get_program_id raises ConfigurationError when env var is not set."""
        # Ensure the env var is unset
        with patch.dict(os.environ, {}, clear=True):
             import importlib
             importlib.reload(config)
             with self.assertRaisesRegex(ConfigurationError, "SOLANA_PROGRAM_ID environment variable is not set"):
                 config.get_program_id()

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_config_all_set(self, mock_stdout):
        """Tests print_config output when all variables are set."""
        test_url = "http://test-url:8899"
        test_prog_id = "TestProgId1111111111111111111111111111111"
        with patch.dict(os.environ, {"SOLANA_CLUSTER_URL": test_url, "SOLANA_PROGRAM_ID": test_prog_id}, clear=True):
            import importlib
            importlib.reload(config)
            config.print_config()
            output = mock_stdout.getvalue()
            self.assertIn("--- Solana ICO CLI Configuration ---", output)
            self.assertIn(f"Cluster URL: {test_url}", output)
            self.assertIn(f"Program ID: {test_prog_id}", output)
            self.assertIn("------------------------------------", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_config_program_id_not_set(self, mock_stdout):
        """Tests print_config output when program ID is not set."""
        test_url = "http://test-url-no-prog:8899"
        # Ensure only URL is set
        with patch.dict(os.environ, {"SOLANA_CLUSTER_URL": test_url}, clear=True):
            import importlib
            importlib.reload(config)
            config.print_config()
            output = mock_stdout.getvalue()
            self.assertIn("--- Solana ICO CLI Configuration ---", output)
            self.assertIn(f"Cluster URL: {test_url}", output)
            self.assertIn("Program ID: Not Set (SOLANA_PROGRAM_ID environment variable is not set", output)
            self.assertIn("------------------------------------", output)

# It's important to reload the config module after tests modify the environment
# to ensure subsequent tests don't use stale values. A fixture might be better in pytest.
def tearDownModule():
    import importlib
    # Ensure the original environment (or lack thereof) is restored for other test modules
    with patch.dict(os.environ, os.environ.copy(), clear=True): # Use a copy of original env
         importlib.reload(config)


if __name__ == "__main__":
    unittest.main()