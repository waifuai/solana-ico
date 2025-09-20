"""
Unit tests for the ICO manager module.

This module contains comprehensive unit tests for the Initial Coin Offering (ICO)
management functionality, including tests for ICO initialization, token buying,
token selling, and escrow withdrawal operations. Tests use extensive mocking
to isolate the ICO manager from Solana client and PDA dependencies.
"""

import unittest
import struct
from unittest.mock import patch, MagicMock, ANY

# Import modules and classes from src
import ico_manager
from solana_client import SolanaClient
from exceptions import ICOInitializationError, TokenPurchaseError, TokenSaleError, EscrowWithdrawalError, TransactionError, PDAError, SolanaIcoError

# Import solders types
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction, TransactionError as SoldersTxError # Alias to avoid clash
from solders.instruction import Instruction, AccountMeta
from solders.rpc.responses import SendTransactionResp, GetAccountInfoResp
from solders.rpc.types import RPCResponse, Context
import solders.system_program as system_program
import solders.sysvar as sysvar

# Mock data
MOCK_PROGRAM_ID_STR = "ProgId111111111111111111111111111111111111"
MOCK_PROGRAM_ID = Pubkey.from_string(MOCK_PROGRAM_ID_STR)
MOCK_OWNER_KEYPAIR = Keypair()
MOCK_OWNER_PUBKEY = MOCK_OWNER_KEYPAIR.pubkey()
MOCK_BUYER_KEYPAIR = Keypair()
MOCK_BUYER_PUBKEY = MOCK_BUYER_KEYPAIR.pubkey()
MOCK_SELLER_KEYPAIR = Keypair()
MOCK_SELLER_PUBKEY = MOCK_SELLER_KEYPAIR.pubkey()
MOCK_TOKEN_MINT_STR = "Mint1111111111111111111111111111111111111"
MOCK_TOKEN_MINT = Pubkey.from_string(MOCK_TOKEN_MINT_STR)
MOCK_ICO_STATE_PDA = Pubkey.new_unique()
MOCK_ESCROW_PDA = Pubkey.new_unique()
MOCK_BUYER_ATA = Pubkey.new_unique() # Mock Associated Token Account
MOCK_SELLER_ATA = Pubkey.new_unique()
MOCK_SIGNATURE_STR = "MockSigICO" + "A" * 54 # Approx length
MOCK_SIGNATURE = SendTransactionResp(value=Pubkey.from_string(MOCK_SIGNATURE_STR[:32])) # Simplified mock response

# Mock SolanaClient instance
mock_solana_client = MagicMock(spec=SolanaClient)

class TestIcoManager(unittest.TestCase):

    def setUp(self):
        # Reset mocks before each test
        mock_solana_client.reset_mock()
        # Mock successful transaction sending by default
        mock_solana_client.send_transaction.return_value = MOCK_SIGNATURE

    @patch('ico_manager.find_ico_state_pda', return_value=(MOCK_ICO_STATE_PDA, 255))
    @patch('ico_manager.find_escrow_pda', return_value=(MOCK_ESCROW_PDA, 254))
    @patch('ico_manager.Pubkey.from_string')
    @patch('ico_manager.Transaction')
    @patch('ico_manager._create_and_add_instruction')
    def test_initialize_ico_success(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey_from_string, mock_find_escrow, mock_find_ico_state):
        """Tests successful ICO initialization."""
        # Arrange mocks
        mock_pubkey_from_string.side_effect = lambda s: Pubkey.from_string(s) # Keep original behavior
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance

        total_supply = 1_000_000_000
        base_price = 1000
        scaling_factor = 100_000

        # Act
        signature = ico_manager.initialize_ico(
            mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_OWNER_KEYPAIR, MOCK_TOKEN_MINT_STR,
            total_supply, base_price, scaling_factor
        )

        # Assert
        mock_find_ico_state.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)
        mock_find_escrow.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)
        mock_pubkey_from_string.assert_any_call(MOCK_PROGRAM_ID_STR)
        mock_pubkey_from_string.assert_any_call(MOCK_TOKEN_MINT_STR)

        expected_instruction_data = struct.pack("<BQQQ", 0, total_supply, base_price, scaling_factor)
        expected_accounts = [
            AccountMeta(pubkey=MOCK_ICO_STATE_PDA, is_signer=False, is_writable=True),
            AccountMeta(pubkey=MOCK_OWNER_PUBKEY, is_signer=True, is_writable=True),
            AccountMeta(pubkey=MOCK_ESCROW_PDA, is_signer=False, is_writable=True),
            AccountMeta(pubkey=MOCK_TOKEN_MINT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=sysvar.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ]
        mock_create_add_ix.assert_called_once_with(mock_tx_instance, MOCK_PROGRAM_ID, *expected_accounts, data=expected_instruction_data)
        mock_solana_client.send_transaction.assert_called_once_with(mock_tx_instance, MOCK_OWNER_KEYPAIR)
        self.assertEqual(signature, str(MOCK_SIGNATURE.value)) # Compare string representation

    @patch('ico_manager.find_ico_state_pda', side_effect=PDAError("PDA Derivation Failed"))
    def test_initialize_ico_pda_error(self, mock_find_ico_state):
        """Tests ICOInitializationError when PDA derivation fails."""
        with self.assertRaises(PDAError): # Expect the original PDAError
             ico_manager.initialize_ico(
                 mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_OWNER_KEYPAIR, MOCK_TOKEN_MINT_STR,
                 1, 1, 1
             )

    @patch('ico_manager.find_ico_state_pda', return_value=(MOCK_ICO_STATE_PDA, 255))
    @patch('ico_manager.find_escrow_pda', return_value=(MOCK_ESCROW_PDA, 254))
    @patch('ico_manager.Pubkey.from_string', side_effect=ValueError("Invalid Key"))
    def test_initialize_ico_value_error(self, mock_pubkey_from_string, mock_find_escrow, mock_find_ico_state):
         """Tests re-raising ValueError for invalid pubkeys."""
         with self.assertRaises(ValueError): # Expect the original ValueError
             ico_manager.initialize_ico(
                 mock_solana_client, "invalid-prog-id", MOCK_OWNER_KEYPAIR, MOCK_TOKEN_MINT_STR,
                 1, 1, 1
             )

    @patch('ico_manager.find_ico_state_pda', return_value=(MOCK_ICO_STATE_PDA, 255))
    @patch('ico_manager.find_escrow_pda', return_value=(MOCK_ESCROW_PDA, 254))
    @patch('ico_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    @patch('ico_manager.Transaction')
    @patch('ico_manager._create_and_add_instruction')
    def test_initialize_ico_transaction_error(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey_from_string, mock_find_escrow, mock_find_ico_state):
        """Tests ICOInitializationError when send_transaction fails."""
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance
        # Simulate transaction failure
        mock_solana_client.send_transaction.side_effect = TransactionError("RPC Error")

        with self.assertRaisesRegex(ICOInitializationError, "Transaction failed during ICO initialization: RPC Error"):
            ico_manager.initialize_ico(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_OWNER_KEYPAIR, MOCK_TOKEN_MINT_STR,
                1, 1, 1
            )
        mock_solana_client.send_transaction.assert_called_once()


    # --- buy_tokens Tests ---
    @patch('ico_manager.find_ico_state_pda', return_value=(MOCK_ICO_STATE_PDA, 255))
    @patch('ico_manager.find_escrow_pda', return_value=(MOCK_ESCROW_PDA, 254))
    @patch('ico_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    def test_buy_tokens_not_implemented_error(self, mock_pubkey, mock_escrow, mock_ico_state):
        """Tests that buy_tokens raises NotImplementedError due to token mint logic."""
        amount_lamports = 10000

        with self.assertRaisesRegex(NotImplementedError, "Token mint determination for 'buy_tokens' is not implemented"):
            ico_manager.buy_tokens(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_BUYER_KEYPAIR, amount_lamports, str(MOCK_OWNER_PUBKEY)
            )
        # Ensure PDAs were found before the error
        mock_ico_state.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)
        mock_escrow.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)

    # --- sell_tokens Tests ---
    @patch('ico_manager.find_ico_state_pda', return_value=(MOCK_ICO_STATE_PDA, 255))
    @patch('ico_manager.find_escrow_pda', return_value=(MOCK_ESCROW_PDA, 254))
    @patch('ico_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    def test_sell_tokens_not_implemented_error(self, mock_pubkey, mock_escrow, mock_ico_state):
        """Tests that sell_tokens raises NotImplementedError due to token mint logic."""
        amount_tokens = 50

        with self.assertRaisesRegex(NotImplementedError, "Token mint determination for 'sell_tokens' is not implemented"):
            ico_manager.sell_tokens(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_SELLER_KEYPAIR, amount_tokens, str(MOCK_OWNER_PUBKEY)
            )
        # Ensure PDAs were found before the error
        mock_ico_state.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)
        mock_escrow.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)


    # --- withdraw_from_escrow Tests ---
    @patch('ico_manager.find_ico_state_pda', return_value=(MOCK_ICO_STATE_PDA, 255))
    @patch('ico_manager.find_escrow_pda', return_value=(MOCK_ESCROW_PDA, 254))
    @patch('ico_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    @patch('ico_manager.Transaction')
    @patch('ico_manager._create_and_add_instruction')
    def test_withdraw_from_escrow_success(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey, mock_find_escrow, mock_find_ico_state):
        """Tests successful withdrawal from escrow."""
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance
        amount_lamports = 50000

        signature = ico_manager.withdraw_from_escrow(
            mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_OWNER_KEYPAIR, amount_lamports
        )

        mock_find_ico_state.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)
        mock_find_escrow.assert_called_once_with(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)

        expected_instruction_data = struct.pack("<BQ", 3, amount_lamports)
        expected_accounts = [
           AccountMeta(pubkey=MOCK_ICO_STATE_PDA, is_signer=False, is_writable=False),
           AccountMeta(pubkey=MOCK_OWNER_PUBKEY, is_signer=True, is_writable=True),
           AccountMeta(pubkey=MOCK_ESCROW_PDA, is_signer=False, is_writable=True),
           AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False)
        ]
        mock_create_add_ix.assert_called_once_with(mock_tx_instance, MOCK_PROGRAM_ID, *expected_accounts, data=expected_instruction_data)
        mock_solana_client.send_transaction.assert_called_once_with(mock_tx_instance, MOCK_OWNER_KEYPAIR)
        self.assertEqual(signature, str(MOCK_SIGNATURE.value))

    @patch('ico_manager.find_ico_state_pda', return_value=(MOCK_ICO_STATE_PDA, 255))
    @patch('ico_manager.find_escrow_pda', return_value=(MOCK_ESCROW_PDA, 254))
    @patch('ico_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    @patch('ico_manager.Transaction')
    @patch('ico_manager._create_and_add_instruction')
    def test_withdraw_from_escrow_tx_error(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey, mock_find_escrow, mock_find_ico_state):
        """Tests EscrowWithdrawalError on transaction failure."""
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance
        mock_solana_client.send_transaction.side_effect = TransactionError("Withdraw Failed")

        with self.assertRaisesRegex(EscrowWithdrawalError, "Transaction failed during escrow withdrawal: Withdraw Failed"):
            ico_manager.withdraw_from_escrow(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_OWNER_KEYPAIR, 1000
            )
        mock_solana_client.send_transaction.assert_called_once()


if __name__ == "__main__":
    unittest.main()