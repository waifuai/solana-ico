"""
Unit tests for the main CLI module.

This module contains comprehensive tests for the main CLI interface, including
tests for all command-line commands, argument parsing, error handling, and
integration with the various manager modules. Tests use Typer's CliRunner
for end-to-end CLI testing with mocked dependencies.
"""

import unittest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

# Import the app and modules from the src directory
# Assumes pytest is run from the root directory and src is in pythonpath (as per pytest.ini)
import main
import tokenomics
import config
from exceptions import ConfigurationError, SolanaConnectionError, KeypairError, TransactionError, ICOError, ResourceError, PDAError

# Create a runner instance
runner = CliRunner()

# Mock keypair and public key for reuse
MOCK_KEYPAIR_PATH = "fake/path/keypair.json"
MOCK_OWNER_PUBKEY = "OwnerPubkey11111111111111111111111111111111"
MOCK_BUYER_PUBKEY = "BuyerPubkey11111111111111111111111111111111"
MOCK_SELLER_PUBKEY = "SellerPubkey1111111111111111111111111111111"
MOCK_SERVER_PUBKEY = "ServerPubkey1111111111111111111111111111111"
MOCK_TOKEN_MINT = "TokenMint1111111111111111111111111111111111"
MOCK_PROGRAM_ID = "ProgramId111111111111111111111111111111111"
MOCK_SIGNATURE = "MockSignature" + "1" * 53 # Approx length

class TestMainCLI(unittest.TestCase):

    def test_info_command(self):
        """Tests the 'info' command."""
        result = runner.invoke(main.app, ["info"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(f"Name: {tokenomics.NAME}", result.stdout)
        self.assertIn(f"Symbol: {tokenomics.SYMBOL}", result.stdout)
        self.assertIn(f"Total Supply: {tokenomics.TOTAL_SUPPLY}", result.stdout)
        self.assertIn(f"Decimals: {tokenomics.DECIMAL_PLACES}", result.stdout)

    @patch('main.get_client_and_program_id')
    def test_balance_command(self, mock_get_client):
        """Tests the 'balance' command."""
        mock_client = MagicMock()
        mock_client.get_balance.return_value = 5_000_000_000 # 5 SOL in lamports
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)

        result = runner.invoke(main.app, ["balance", MOCK_OWNER_PUBKEY])

        self.assertEqual(result.exit_code, 0)
        mock_client.get_balance.assert_called_once_with(MOCK_OWNER_PUBKEY)
        self.assertIn(f"Balance for {MOCK_OWNER_PUBKEY}: 5.000000000 SOL (5000000000 Lamports)", result.stdout)

    @patch('main.get_client_and_program_id')
    def test_send_command(self, mock_get_client):
        """Tests the 'send' command."""
        mock_client = MagicMock()
        mock_keypair = MagicMock() # Simulate loaded keypair
        mock_client.load_keypair.return_value = mock_keypair
        mock_client.send_sol.return_value = MOCK_SIGNATURE
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)

        amount_lamports = 100_000_000 # 0.1 SOL

        result = runner.invoke(main.app, [
            "send", MOCK_KEYPAIR_PATH, MOCK_BUYER_PUBKEY, str(amount_lamports)
        ])

        self.assertEqual(result.exit_code, 0)
        mock_client.load_keypair.assert_called_once_with(MOCK_KEYPAIR_PATH)
        mock_client.send_sol.assert_called_once_with(mock_keypair, MOCK_BUYER_PUBKEY, amount_lamports)
        self.assertIn(f"Successfully sent {amount_lamports} lamports.", result.stdout)
        self.assertIn(f"Transaction signature: {MOCK_SIGNATURE}", result.stdout)

    @patch('main.initialize_ico')
    @patch('main.get_client_and_program_id')
    def test_ico_init_command(self, mock_get_client, mock_init_ico):
        """Tests the 'ico init' command."""
        mock_client = MagicMock()
        mock_keypair = MagicMock()
        mock_client.load_keypair.return_value = mock_keypair
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)
        mock_init_ico.return_value = MOCK_SIGNATURE

        total_supply = 1_000_000
        base_price = 1000
        scaling_factor = 100

        result = runner.invoke(main.app, [
            "ico", "init", MOCK_KEYPAIR_PATH, MOCK_TOKEN_MINT,
            str(total_supply), str(base_price), str(scaling_factor)
        ])

        self.assertEqual(result.exit_code, 0)
        mock_client.load_keypair.assert_called_once_with(MOCK_KEYPAIR_PATH)
        mock_init_ico.assert_called_once_with(
            solana_client=mock_client,
            program_id_str=MOCK_PROGRAM_ID,
            owner_keypair=mock_keypair,
            token_mint_str=MOCK_TOKEN_MINT,
            total_supply=total_supply,
            base_price=base_price,
            scaling_factor=scaling_factor
        )
        self.assertIn("ICO initialized successfully.", result.stdout)
        self.assertIn(f"Transaction signature: {MOCK_SIGNATURE}", result.stdout)

    @patch('main.buy_tokens')
    @patch('main.get_client_and_program_id')
    def test_ico_buy_command(self, mock_get_client, mock_buy_tokens):
        """Tests the 'ico buy' command."""
        mock_client = MagicMock()
        mock_keypair = MagicMock()
        mock_client.load_keypair.return_value = mock_keypair
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)
        mock_buy_tokens.return_value = MOCK_SIGNATURE

        amount_lamports = 50000

        result = runner.invoke(main.app, [
            "ico", "buy", MOCK_KEYPAIR_PATH, str(amount_lamports), MOCK_OWNER_PUBKEY
            # Removed token_mint arg to match current main.py
        ])

        self.assertEqual(result.exit_code, 0)
        mock_client.load_keypair.assert_called_once_with(MOCK_KEYPAIR_PATH)
        # Note: This will fail until NotImplementedError is resolved in ico_manager
        # We assert it's called correctly for now.
        mock_buy_tokens.assert_called_once_with(
            solana_client=mock_client,
            program_id_str=MOCK_PROGRAM_ID,
            buyer_keypair=mock_keypair,
            amount_lamports=amount_lamports,
            ico_owner_pubkey_str=MOCK_OWNER_PUBKEY
            # token_mint_str_arg=... # Add if required by ico_manager later
        )
        self.assertIn(f"Successfully bought tokens with {amount_lamports} lamports.", result.stdout)
        self.assertIn(f"Transaction signature: {MOCK_SIGNATURE}", result.stdout)

    @patch('main.sell_tokens')
    @patch('main.get_client_and_program_id')
    def test_ico_sell_command(self, mock_get_client, mock_sell_tokens):
        """Tests the 'ico sell' command."""
        mock_client = MagicMock()
        mock_keypair = MagicMock()
        mock_client.load_keypair.return_value = mock_keypair
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)
        mock_sell_tokens.return_value = MOCK_SIGNATURE

        amount_tokens = 50

        result = runner.invoke(main.app, [
            "ico", "sell", MOCK_KEYPAIR_PATH, str(amount_tokens), MOCK_OWNER_PUBKEY
            # Removed token_mint arg to match current main.py
        ])

        self.assertEqual(result.exit_code, 0)
        mock_client.load_keypair.assert_called_once_with(MOCK_KEYPAIR_PATH)
        # Note: This will fail until NotImplementedError is resolved in ico_manager
        # We assert it's called correctly for now.
        mock_sell_tokens.assert_called_once_with(
            solana_client=mock_client,
            program_id_str=MOCK_PROGRAM_ID,
            seller_keypair=mock_keypair,
            amount_tokens=amount_tokens,
            ico_owner_pubkey_str=MOCK_OWNER_PUBKEY
            # token_mint_str_arg=... # Add if required by ico_manager later
        )
        self.assertIn(f"Successfully sold {amount_tokens} tokens.", result.stdout)
        self.assertIn(f"Transaction signature: {MOCK_SIGNATURE}", result.stdout)

    @patch('main.withdraw_from_escrow')
    @patch('main.get_client_and_program_id')
    def test_ico_withdraw_command(self, mock_get_client, mock_withdraw):
        """Tests the 'ico withdraw' command."""
        mock_client = MagicMock()
        mock_keypair = MagicMock()
        mock_client.load_keypair.return_value = mock_keypair
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)
        mock_withdraw.return_value = MOCK_SIGNATURE

        amount_lamports = 10000

        result = runner.invoke(main.app, [
            "ico", "withdraw", MOCK_KEYPAIR_PATH, str(amount_lamports)
        ])

        self.assertEqual(result.exit_code, 0)
        mock_client.load_keypair.assert_called_once_with(MOCK_KEYPAIR_PATH)
        mock_withdraw.assert_called_once_with(
            solana_client=mock_client,
            program_id_str=MOCK_PROGRAM_ID,
            owner_keypair=mock_keypair,
            amount_lamports=amount_lamports
        )
        self.assertIn(f"Successfully withdrew {amount_lamports} lamports from escrow.", result.stdout)
        self.assertIn(f"Transaction signature: {MOCK_SIGNATURE}", result.stdout)

    @patch('main.create_resource_access')
    @patch('main.get_client_and_program_id')
    def test_resource_create_command(self, mock_get_client, mock_create_resource):
        """Tests the 'resource create' command."""
        mock_client = MagicMock()
        mock_keypair = MagicMock()
        mock_client.load_keypair.return_value = mock_keypair
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)
        mock_create_resource.return_value = MOCK_SIGNATURE

        resource_id = "my_api"
        access_fee = 500

        result = runner.invoke(main.app, [
            "resource", "create", MOCK_KEYPAIR_PATH, resource_id, str(access_fee)
        ])

        self.assertEqual(result.exit_code, 0)
        mock_client.load_keypair.assert_called_once_with(MOCK_KEYPAIR_PATH)
        mock_create_resource.assert_called_once_with(
            solana_client=mock_client,
            program_id_str=MOCK_PROGRAM_ID,
            server_keypair=mock_keypair,
            resource_id=resource_id,
            access_fee=access_fee
        )
        self.assertIn(f"Resource access '{resource_id}' created/updated successfully.", result.stdout)
        self.assertIn(f"Transaction signature: {MOCK_SIGNATURE}", result.stdout)

    @patch('main.access_resource')
    @patch('main.get_client_and_program_id')
    def test_resource_access_command(self, mock_get_client, mock_access_resource):
        """Tests the 'resource access' command."""
        mock_client = MagicMock()
        mock_keypair = MagicMock()
        mock_client.load_keypair.return_value = mock_keypair
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)
        mock_access_resource.return_value = MOCK_SIGNATURE

        resource_id = "my_api"
        amount_lamports = 500

        result = runner.invoke(main.app, [
            "resource", "access", MOCK_KEYPAIR_PATH, resource_id, MOCK_SERVER_PUBKEY, str(amount_lamports)
        ])

        self.assertEqual(result.exit_code, 0)
        mock_client.load_keypair.assert_called_once_with(MOCK_KEYPAIR_PATH)
        mock_access_resource.assert_called_once_with(
            solana_client=mock_client,
            program_id_str=MOCK_PROGRAM_ID,
            user_keypair=mock_keypair,
            resource_id=resource_id,
            server_pubkey_str=MOCK_SERVER_PUBKEY,
            amount_lamports=amount_lamports
        )
        self.assertIn(f"Successfully paid {amount_lamports} lamports to access resource '{resource_id}'.", result.stdout)
        self.assertIn(f"Transaction signature: {MOCK_SIGNATURE}", result.stdout)

    @patch('config.print_config')
    def test_config_show_command(self, mock_print_config):
        """Tests the 'config show' command."""
        result = runner.invoke(main.app, ["config", "show"])
        self.assertEqual(result.exit_code, 0)
        mock_print_config.assert_called_once()

    @patch('main.get_client_and_program_id')
    def test_config_verify_command_success(self, mock_get_client):
        """Tests the 'config verify' command on success."""
        mock_client = MagicMock()
        mock_client.cluster_url = "http://mock-url:8899"
        # Simulate successful connection and config retrieval
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)

        result = runner.invoke(main.app, ["config", "verify"])

        self.assertEqual(result.exit_code, 0)
        mock_get_client.assert_called_once()
        self.assertIn("Verifying configuration and connection...", result.stdout)
        self.assertIn(f"Successfully connected to cluster: {mock_client.cluster_url}", result.stdout)
        self.assertIn(f"Program ID configured: {MOCK_PROGRAM_ID}", result.stdout)
        self.assertIn("Verification successful.", result.stdout)

    @patch('main.get_client_and_program_id', side_effect=ConfigurationError("SOLANA_PROGRAM_ID not set"))
    def test_config_verify_command_config_error(self, mock_get_client):
        """Tests the 'config verify' command with a configuration error."""
        result = runner.invoke(main.app, ["config", "verify"])
        self.assertNotEqual(result.exit_code, 0) # Expect non-zero exit code
        self.assertIn("Verifying configuration and connection...", result.stdout)
        self.assertIn("❌ Verification Failed: SOLANA_PROGRAM_ID not set", result.stdout) # Check stderr? Typer might redirect stderr to stdout

    @patch('main.get_client_and_program_id', side_effect=SolanaConnectionError("Connection refused"))
    def test_config_verify_command_connection_error(self, mock_get_client):
        """Tests the 'config verify' command with a connection error."""
        result = runner.invoke(main.app, ["config", "verify"])
        self.assertNotEqual(result.exit_code, 0) # Expect non-zero exit code
        self.assertIn("Verifying configuration and connection...", result.stdout)
        self.assertIn("❌ Verification Failed: Connection refused", result.stdout) # Check stderr?

    # --- Test Error Handling ---
    # Example: Test how a KeypairError is handled
    @patch('main.get_client_and_program_id')
    def test_send_command_keypair_error(self, mock_get_client):
        """Tests error handling for KeypairError during 'send'."""
        mock_client = MagicMock()
        mock_client.load_keypair.side_effect = KeypairError("File not found")
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)

        result = runner.invoke(main.app, ["send", "bad/path.json", MOCK_BUYER_PUBKEY, "100"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("❌ Keypair Error: File not found", result.stdout) # Check stderr?

    # Example: Test how NotImplementedError is handled (for buy/sell)
    @patch('main.buy_tokens', side_effect=NotImplementedError("Token mint determination needed"))
    @patch('main.get_client_and_program_id')
    def test_ico_buy_command_not_implemented(self, mock_get_client, mock_buy_tokens):
        """Tests error handling for NotImplementedError during 'ico buy'."""
        mock_client = MagicMock()
        mock_keypair = MagicMock()
        mock_client.load_keypair.return_value = mock_keypair
        mock_get_client.return_value = (mock_client, MOCK_PROGRAM_ID)

        result = runner.invoke(main.app, ["ico", "buy", MOCK_KEYPAIR_PATH, "50000", MOCK_OWNER_PUBKEY])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("❌ Feature Not Fully Implemented: Token mint determination needed", result.stdout) # Check stderr?


# Remove the old TestAll suite and __main__ block if present
# if __name__ == "__main__":
#     unittest.main()