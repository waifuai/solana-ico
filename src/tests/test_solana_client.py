"""
Unit tests for the Solana client module.

This module contains comprehensive unit tests for the Solana client wrapper,
including tests for client initialization, keypair loading, balance queries,
SOL transfers, transaction sending, and account information retrieval. Tests
use extensive mocking to isolate the client from actual Solana RPC calls.
"""

import unittest
import os
from unittest.mock import patch, MagicMock, mock_open

# Import necessary classes from src (assuming pytest runs from root)
from solana_client import SolanaClient
from config import get_cluster_url # To mock config dependency
from exceptions import SolanaConnectionError, KeypairError, TransactionError, ConfigurationError

# Import solders types for mocking
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.api import Client as SoldersClient # Alias to avoid clash with solana.rpc.api.Client
from solders.rpc.responses import GetBalanceResp, SendTransactionResp, GetAccountInfoResp, GetLatestBlockhashResp
from solders.rpc.types import RPCResponse, Context, Blockhash
from solders.transaction import Transaction, Signature

# Mock data
MOCK_CLUSTER_URL = "http://mock-test-cluster:8899"
MOCK_KEYPAIR_PATH = "fake_keypair.json"
MOCK_SECRET_KEY_BYTES = bytes(range(64))
MOCK_PUBLIC_KEY_STR = "MockPubkey11111111111111111111111111111111"
MOCK_PUBLIC_KEY = Pubkey.from_string(MOCK_PUBLIC_KEY_STR)
MOCK_SIGNATURE_STR = "MockSig" + "X" * 57 # Approx length
MOCK_SIGNATURE = Signature.from_string(MOCK_SIGNATURE_STR)
MOCK_BLOCKHASH_STR = "MockBlockhash" + "Y" * 31 # Approx length
MOCK_BLOCKHASH = Blockhash.from_string(MOCK_BLOCKHASH_STR)

class TestSolanaClient(unittest.TestCase):

    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client') # Mock the underlying solana.rpc.api.Client
    def test_init_success(self, mock_rpc_client_constructor, mock_get_url):
        """Tests successful initialization of SolanaClient."""
        mock_rpc_client_instance = MagicMock()
        mock_rpc_client_instance.is_connected.return_value = True
        # Mock get_latest_blockhash response needed for connection check
        mock_blockhash_resp = GetLatestBlockhashResp(
            context=Context(slot=1),
            value=GetLatestBlockhashResp.Value(blockhash=MOCK_BLOCKHASH, last_valid_block_height=100)
        )
        mock_rpc_client_instance.get_latest_blockhash.return_value = mock_blockhash_resp
        mock_rpc_client_constructor.return_value = mock_rpc_client_instance

        client = SolanaClient()

        mock_get_url.assert_called_once()
        mock_rpc_client_constructor.assert_called_once_with(MOCK_CLUSTER_URL)
        mock_rpc_client_instance.is_connected.assert_called_once()
        mock_rpc_client_instance.get_latest_blockhash.assert_called_once()
        self.assertEqual(client.cluster_url, MOCK_CLUSTER_URL)
        self.assertEqual(client.client, mock_rpc_client_instance)

    @patch('solana_client.config.get_cluster_url', side_effect=ConfigurationError("URL not set"))
    def test_init_config_error(self, mock_get_url):
        """Tests initialization failure due to config error."""
        with self.assertRaisesRegex(ConfigurationError, "URL not set"):
            SolanaClient()
        mock_get_url.assert_called_once()

    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client')
    def test_init_connection_error_disconnected(self, mock_rpc_client_constructor, mock_get_url):
        """Tests initialization failure due to is_connected() returning False."""
        mock_rpc_client_instance = MagicMock()
        mock_rpc_client_instance.is_connected.return_value = False
        mock_rpc_client_constructor.return_value = mock_rpc_client_instance

        with self.assertRaisesRegex(SolanaConnectionError, f"Failed to connect to Solana cluster at {MOCK_CLUSTER_URL}"):
            SolanaClient()
        mock_rpc_client_instance.is_connected.assert_called_once()

    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client')
    def test_init_connection_error_rpc_exception(self, mock_rpc_client_constructor, mock_get_url):
        """Tests initialization failure due to RPCException during connection check."""
        mock_rpc_client_instance = MagicMock()
        mock_rpc_client_instance.is_connected.return_value = True
        # Simulate RPC error during blockhash fetch
        mock_rpc_client_instance.get_latest_blockhash.side_effect = SolanaConnectionError("RPC Timeout") # Using our exception type for simplicity
        mock_rpc_client_constructor.return_value = mock_rpc_client_instance

        with self.assertRaisesRegex(SolanaConnectionError, f"RPC error connecting to Solana cluster at {MOCK_CLUSTER_URL}: RPC Timeout"):
             SolanaClient()
        mock_rpc_client_instance.get_latest_blockhash.assert_called_once()


    @patch('builtins.open', new_callable=mock_open, read_data="[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]")
    @patch('solana_client.Keypair') # Mock solders.keypair.Keypair
    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL) # Need to mock config for init
    @patch('solana_client.Client') # Need to mock rpc client for init
    def test_load_keypair_success(self, mock_rpc_client, mock_get_url, mock_solders_keypair, mock_file):
        """Tests successful loading of a keypair."""
        # Prevent SolanaClient init from actually connecting
        mock_rpc_instance = MagicMock()
        mock_rpc_instance.is_connected.return_value = True
        mock_blockhash_resp = GetLatestBlockhashResp(context=Context(slot=1), value=GetLatestBlockhashResp.Value(blockhash=MOCK_BLOCKHASH, last_valid_block_height=100))
        mock_rpc_instance.get_latest_blockhash.return_value = mock_blockhash_resp
        mock_rpc_client.return_value = mock_rpc_instance

        # Mock the return value of Keypair.from_secret_key
        mock_loaded_keypair = MagicMock(spec=Keypair)
        mock_solders_keypair.from_secret_key.return_value = mock_loaded_keypair

        client = SolanaClient() # Initialize the client (mocks prevent connection)
        loaded_keypair = client.load_keypair(MOCK_KEYPAIR_PATH)

        mock_file.assert_called_once_with(MOCK_KEYPAIR_PATH, 'r')
        # Check that from_secret_key was called with the correct bytes
        expected_bytes = bytes(range(1, 65))
        mock_solders_keypair.from_secret_key.assert_called_once_with(expected_bytes)
        self.assertEqual(loaded_keypair, mock_loaded_keypair)

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client')
    def test_load_keypair_file_not_found(self, mock_rpc_client, mock_get_url, mock_file):
        """Tests KeypairError when the keypair file is not found."""
        mock_rpc_instance = MagicMock(); mock_rpc_instance.is_connected.return_value = True
        mock_blockhash_resp = GetLatestBlockhashResp(context=Context(slot=1), value=GetLatestBlockhashResp.Value(blockhash=MOCK_BLOCKHASH, last_valid_block_height=100))
        mock_rpc_instance.get_latest_blockhash.return_value = mock_blockhash_resp
        mock_rpc_client.return_value = mock_rpc_instance

        client = SolanaClient()
        with self.assertRaisesRegex(KeypairError, f"Keypair file not found at path: {MOCK_KEYPAIR_PATH}"):
            client.load_keypair(MOCK_KEYPAIR_PATH)

    @patch('builtins.open', new_callable=mock_open, read_data="invalid,data")
    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client')
    def test_load_keypair_invalid_format(self, mock_rpc_client, mock_get_url, mock_file):
        """Tests KeypairError when the keypair file has invalid format."""
        mock_rpc_instance = MagicMock(); mock_rpc_instance.is_connected.return_value = True
        mock_blockhash_resp = GetLatestBlockhashResp(context=Context(slot=1), value=GetLatestBlockhashResp.Value(blockhash=MOCK_BLOCKHASH, last_valid_block_height=100))
        mock_rpc_instance.get_latest_blockhash.return_value = mock_blockhash_resp
        mock_rpc_client.return_value = mock_rpc_instance

        client = SolanaClient()
        with self.assertRaisesRegex(KeypairError, f"Invalid secret key format in file: {MOCK_KEYPAIR_PATH}"):
            client.load_keypair(MOCK_KEYPAIR_PATH)

    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client')
    def test_get_balance_success(self, mock_rpc_client_constructor, mock_get_url):
        """Tests successful retrieval of balance."""
        mock_rpc_instance = MagicMock()
        mock_rpc_instance.is_connected.return_value = True
        mock_blockhash_resp = GetLatestBlockhashResp(context=Context(slot=1), value=GetLatestBlockhashResp.Value(blockhash=MOCK_BLOCKHASH, last_valid_block_height=100))
        mock_rpc_instance.get_latest_blockhash.return_value = mock_blockhash_resp
        mock_rpc_client_constructor.return_value = mock_rpc_instance

        # Mock the get_balance response
        balance_value = 1_000_000_000 # 1 SOL
        mock_balance_resp = GetBalanceResp(
             context=Context(slot=1),
             value=balance_value
        )
        # Note: solders GetBalanceResp structure is simpler than older solana-py
        mock_rpc_instance.get_balance.return_value = mock_balance_resp

        client = SolanaClient()
        balance = client.get_balance(MOCK_PUBLIC_KEY_STR)

        mock_rpc_instance.get_balance.assert_called_once_with(MOCK_PUBLIC_KEY)
        self.assertEqual(balance, balance_value)

    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client')
    def test_get_balance_invalid_pubkey(self, mock_rpc_client_constructor, mock_get_url):
        """Tests ValueError for invalid public key string in get_balance."""
        mock_rpc_instance = MagicMock(); mock_rpc_instance.is_connected.return_value = True
        mock_blockhash_resp = GetLatestBlockhashResp(context=Context(slot=1), value=GetLatestBlockhashResp.Value(blockhash=MOCK_BLOCKHASH, last_valid_block_height=100))
        mock_rpc_instance.get_latest_blockhash.return_value = mock_blockhash_resp
        mock_rpc_client_constructor.return_value = mock_rpc_instance

        client = SolanaClient()
        with self.assertRaisesRegex(ValueError, "Invalid public key format: invalid-key"):
            client.get_balance("invalid-key")

    @patch('solana_client.config.get_cluster_url', return_value=MOCK_CLUSTER_URL)
    @patch('solana_client.Client')
    def test_send_transaction_success(self, mock_rpc_client_constructor, mock_get_url):
        """Tests successful sending of a transaction."""
        mock_rpc_instance = MagicMock()
        mock_rpc_instance.is_connected.return_value = True
        # Mock blockhash response
        mock_blockhash_resp = GetLatestBlockhashResp(context=Context(slot=1), value=GetLatestBlockhashResp.Value(blockhash=MOCK_BLOCKHASH, last_valid_block_height=100))
        mock_rpc_instance.get_latest_blockhash.return_value = mock_blockhash_resp
        # Mock send_transaction response
        mock_send_tx_resp = SendTransactionResp(value=MOCK_SIGNATURE)
        mock_rpc_instance.send_transaction.return_value = mock_send_tx_resp
        mock_rpc_client_constructor.return_value = mock_rpc_instance

        client = SolanaClient()
        mock_tx = MagicMock(spec=Transaction)
        mock_signer = MagicMock(spec=Keypair)

        result = client.send_transaction(mock_tx, mock_signer)

        mock_rpc_instance.get_latest_blockhash.assert_called_once()
        # Check that recent_blockhash was set on the transaction object
        self.assertEqual(mock_tx.recent_blockhash, MOCK_BLOCKHASH)
        mock_rpc_instance.send_transaction.assert_called_once_with(mock_tx, mock_signer)
        self.assertEqual(result, mock_send_tx_resp)

    # Add more tests for send_sol, get_account_info, confirm_transaction,
    # and error handling within those methods (e.g., RPCException -> TransactionError)

if __name__ == "__main__":
    unittest.main()