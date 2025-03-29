"""Provides a client wrapper for interacting with the Solana blockchain."""

import os
from solana.rpc.api import Client # Stays
# from solana.transaction import Transaction # Moved
from solana.rpc.core import RPCException # Stays

# Imports moved from solana.* to solders.*
from solders.transaction import Transaction # Corrected import
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.rpc.responses import GetBalanceResp, SendTransactionResp, GetAccountInfoResp # Specific response types from solders
# from solana.rpc.types import RPCResponse # Removed incorrect import

from .exceptions import (
    SolanaConnectionError,
    KeypairError,
    TransactionError,
    ConfigurationError,
)
from . import config # Import the new config module

# TODO: Move this to a dedicated config module later in the refactoring
# SOLANA_CLUSTER_URL = os.environ.get("SOLANA_CLUSTER_URL", "http://localhost:8899") # Removed local definition

class SolanaClient:
    """A wrapper around the Solana Client for common operations."""

    def __init__(self):
        """
        Initializes the SolanaClient by fetching the cluster URL from config.

        Raises:
            ConfigurationError: If the cluster URL is not configured.
            SolanaConnectionError: If connection to the cluster fails.
        """
        try:
            # Fetch cluster URL from the config module
            self.cluster_url = config.get_cluster_url()
        except ConfigurationError as e:
             # Re-raise config errors immediately
             raise e

        if not self.cluster_url: # Should be caught by get_cluster_url, but belt-and-suspenders
            raise ConfigurationError("Solana cluster URL is configured but empty.")

        try:
            self.client = Client(self.cluster_url)
            # Test connection
            if not self.client.is_connected():
                 # Use self.cluster_url here
                 raise SolanaConnectionError(f"Failed to connect to Solana cluster at {self.cluster_url}")
            # Perform a simple request to confirm connectivity
            self.client.get_latest_blockhash()
        except RPCException as e:
             # Use self.cluster_url here
            raise SolanaConnectionError(f"RPC error connecting to Solana cluster at {self.cluster_url}: {e}") from e
        except Exception as e:
             # Use self.cluster_url here
            raise SolanaConnectionError(f"Unexpected error connecting to Solana cluster at {self.cluster_url}: {e}") from e

    def load_keypair(self, keypair_path: str) -> Keypair:
        """
        Loads a keypair from a file.

        Args:
            keypair_path: The path to the keypair file.

        Returns:
            The loaded Keypair object.

        Raises:
            KeypairError: If the file cannot be read or the key is invalid.
        """
        try:
            with open(keypair_path, 'r') as f:
                # Assuming the key is stored as a comma-separated list of integers
                secret_key_str = f.readline().strip()
                # Remove brackets if present (common format)
                if secret_key_str.startswith('[') and secret_key_str.endswith(']'):
                    secret_key_str = secret_key_str[1:-1]
                secret_key = bytes(map(int, secret_key_str.split(',')))
            return Keypair.from_secret_key(secret_key)
        except FileNotFoundError:
            raise KeypairError(f"Keypair file not found at path: {keypair_path}")
        except ValueError:
             raise KeypairError(f"Invalid secret key format in file: {keypair_path}. Expected comma-separated integers.")
        except Exception as e:
            raise KeypairError(f"Failed to load keypair from {keypair_path}: {e}") from e

    def get_balance(self, public_key_str: str) -> int: # Return value is int (lamports)
        """
        Gets the balance of a Solana account in lamports.

        Args:
            public_key_str: The public key of the account as a string.

        Returns:
            The balance in lamports.

        Raises:
            SolanaConnectionError: If the balance check fails due to connection issues.
            ValueError: If the public key string is invalid.
        """
        try:
            public_key = Pubkey.from_string(public_key_str)
            # Type hint with the specific solders response type
            response: GetBalanceResp = self.client.get_balance(public_key)
            if response.value is None: # Accessing .value directly on GetBalanceResp
                 raise SolanaConnectionError(f"Received null value when getting balance for {public_key_str}. RPC Response: {response}")
            return response.value.value # Access the inner value field
        except ValueError as e:
            raise ValueError(f"Invalid public key format: {public_key_str}") from e
        except RPCException as e:
            raise SolanaConnectionError(f"RPC error getting balance for {public_key_str}: {e}") from e
        except Exception as e:
            raise SolanaConnectionError(f"Failed to get balance for {public_key_str}: {e}") from e

    def send_sol(self, from_keypair: Keypair, to_public_key_str: str, amount_lamports: int) -> str:
        """
        Sends SOL from one account to another.

        Args:
            from_keypair: The keypair of the sender account.
            to_public_key_str: The public key of the recipient account as a string.
            amount_lamports: The amount of SOL to send in lamports.

        Returns:
            The transaction signature as a string.

        Raises:
            TransactionError: If the SOL transfer fails.
            ValueError: If the recipient public key string is invalid.
        """
        try:
            to_pubkey = Pubkey.from_string(to_public_key_str)
            params = TransferParams(
                from_pubkey=from_keypair.pubkey(),
                to_pubkey=to_pubkey,
                lamports=amount_lamports
            )
            transfer_instruction = transfer(params)
            transaction = Transaction().add(transfer_instruction)
            # send_transaction now returns RPCResponse[SendTransactionResp]
            result = self.send_transaction(transaction, from_keypair)
            # Assuming result.value holds the signature (needs confirmation based on RPCResponse structure)
            if result.value is None:
                 raise TransactionError(f"Send SOL transaction failed, received null value in response: {result}")
            return str(result.value) # Return the signature
        except ValueError as e:
             raise ValueError(f"Invalid recipient public key format: {to_public_key_str}") from e
        except RPCException as e:
            raise TransactionError(f"RPC error sending SOL: {e}") from e
        except Exception as e:
            raise TransactionError(f"Failed to send SOL: {e}") from e

    def send_transaction(self, transaction: Transaction, *signers: Keypair) -> SendTransactionResp:
        """
        Sends a transaction to the Solana cluster.

        Args:
            transaction: The transaction to send.
            *signers: The keypairs required to sign the transaction.

        Returns:
            The SendTransactionResp containing the result of the send_transaction call.

        Raises:
            TransactionError: If sending the transaction fails.
        """
        try:
            # Ensure latest blockhash is set before sending
            # Note: solana-py client might handle this automatically in recent versions,
            # but explicit setting is safer.
            latest_blockhash_resp = self.client.get_latest_blockhash() # Returns GetLatestBlockhashResp
            if latest_blockhash_resp.value is None or latest_blockhash_resp.value.blockhash is None:
                 raise TransactionError(f"Failed to get latest blockhash: {latest_blockhash_resp}")
            transaction.recent_blockhash = latest_blockhash_resp.value.blockhash

            # Type hint with the specific solders response type
            result: SendTransactionResp = self.client.send_transaction(transaction, *signers)
            # Check for errors in the response if possible (structure might vary)
            # Example check (adjust based on actual response structure if needed):
            # if result.value is None: # SendTransactionResp value is the signature
            #    raise TransactionError(f"Transaction failed: {result}")
            return result
        except RPCException as e:
            raise TransactionError(f"RPC error sending transaction: {e}") from e
        except Exception as e:
            raise TransactionError(f"Failed to send transaction: {e}") from e

    # from solders.rpc.responses import GetAccountInfoResp # Import is already at the top

    def get_account_info(self, public_key: Pubkey) -> GetAccountInfoResp:
         """Gets account information."""
         try:
             # Type hint with the specific solders response type
             response: GetAccountInfoResp = self.client.get_account_info(public_key)
             return response
         except RPCException as e:
             raise SolanaConnectionError(f"RPC error getting account info for {public_key}: {e}") from e
         except Exception as e:
             raise SolanaConnectionError(f"Failed to get account info for {public_key}: {e}") from e

    def confirm_transaction(self, signature: str, commitment: str = "confirmed"):
        """Confirms a transaction."""
        try:
            return self.client.confirm_transaction(signature, commitment)
        except RPCException as e:
            raise TransactionError(f"RPC error confirming transaction {signature}: {e}") from e
        except Exception as e:
            raise TransactionError(f"Failed to confirm transaction {signature}: {e}") from e