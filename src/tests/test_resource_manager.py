import unittest
import struct
from unittest.mock import patch, MagicMock, ANY

# Import modules and classes from src
import resource_manager
from solana_client import SolanaClient
from exceptions import ResourceCreationError, ResourceAccessError, TransactionError, PDAError

# Import solders types
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction, TransactionError as SoldersTxError # Alias
from solders.instruction import Instruction, AccountMeta
from solders.rpc.responses import SendTransactionResp
import solders.system_program as system_program
import solders.sysvar as sysvar

# Mock data
MOCK_PROGRAM_ID_STR = "ProgIdRes11111111111111111111111111111111"
MOCK_PROGRAM_ID = Pubkey.from_string(MOCK_PROGRAM_ID_STR)
MOCK_SERVER_KEYPAIR = Keypair()
MOCK_SERVER_PUBKEY = MOCK_SERVER_KEYPAIR.pubkey()
MOCK_USER_KEYPAIR = Keypair()
MOCK_USER_PUBKEY = MOCK_USER_KEYPAIR.pubkey()
MOCK_RESOURCE_ID = "api_endpoint_xyz"
MOCK_RESOURCE_ID_BYTES = MOCK_RESOURCE_ID.encode('utf-8')
MOCK_RESOURCE_STATE_PDA = Pubkey.new_unique()
MOCK_SIGNATURE_STR = "MockSigRes" + "B" * 54 # Approx length
MOCK_SIGNATURE = SendTransactionResp(value=Pubkey.from_string(MOCK_SIGNATURE_STR[:32])) # Simplified mock response

# Mock SolanaClient instance
mock_solana_client = MagicMock(spec=SolanaClient)

class TestResourceManager(unittest.TestCase):

    def setUp(self):
        # Reset mocks before each test
        mock_solana_client.reset_mock()
        # Mock successful transaction sending by default
        mock_solana_client.send_transaction.return_value = MOCK_SIGNATURE

    @patch('resource_manager.find_resource_state_pda', return_value=(MOCK_RESOURCE_STATE_PDA, 255))
    @patch('resource_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    @patch('resource_manager.Transaction')
    @patch('resource_manager._create_and_add_instruction')
    def test_create_resource_access_success(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey, mock_find_pda):
        """Tests successful creation of resource access."""
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance
        access_fee = 5000

        signature = resource_manager.create_resource_access(
            mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_SERVER_KEYPAIR, MOCK_RESOURCE_ID, access_fee
        )

        mock_find_pda.assert_called_once_with(MOCK_SERVER_PUBKEY, MOCK_RESOURCE_ID, MOCK_PROGRAM_ID)
        mock_pubkey.assert_called_with(MOCK_PROGRAM_ID_STR) # Called for program ID

        # Verify instruction data packing (adjust based on actual packing in resource_manager)
        # Assuming simple packing: instruction index 4, resource_id bytes, access_fee
        expected_instruction_data = struct.pack(f"<B{len(MOCK_RESOURCE_ID_BYTES)}sQ", 4, MOCK_RESOURCE_ID_BYTES, access_fee)
        expected_accounts = [
            AccountMeta(pubkey=MOCK_RESOURCE_STATE_PDA, is_signer=False, is_writable=True),
            AccountMeta(pubkey=MOCK_SERVER_PUBKEY, is_signer=True, is_writable=True),
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=sysvar.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ]
        mock_create_add_ix.assert_called_once_with(mock_tx_instance, MOCK_PROGRAM_ID, *expected_accounts, data=expected_instruction_data)
        mock_solana_client.send_transaction.assert_called_once_with(mock_tx_instance, MOCK_SERVER_KEYPAIR)
        self.assertEqual(signature, str(MOCK_SIGNATURE.value))

    @patch('resource_manager.find_resource_state_pda', side_effect=PDAError("PDA Deriv Failed"))
    def test_create_resource_access_pda_error(self, mock_find_pda):
        """Tests ResourceCreationError on PDA derivation failure."""
        with self.assertRaises(PDAError): # Expect original PDAError
            resource_manager.create_resource_access(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_SERVER_KEYPAIR, MOCK_RESOURCE_ID, 5000
            )

    @patch('resource_manager.find_resource_state_pda', return_value=(MOCK_RESOURCE_STATE_PDA, 255))
    @patch('resource_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    @patch('resource_manager.Transaction')
    @patch('resource_manager._create_and_add_instruction')
    def test_create_resource_access_tx_error(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey, mock_find_pda):
        """Tests ResourceCreationError on transaction sending failure."""
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance
        mock_solana_client.send_transaction.side_effect = TransactionError("Create Failed")

        with self.assertRaisesRegex(ResourceCreationError, f"Transaction failed during resource access creation for '{MOCK_RESOURCE_ID}': Create Failed"):
            resource_manager.create_resource_access(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_SERVER_KEYPAIR, MOCK_RESOURCE_ID, 5000
            )
        mock_solana_client.send_transaction.assert_called_once()


    @patch('resource_manager.find_resource_state_pda', return_value=(MOCK_RESOURCE_STATE_PDA, 255))
    @patch('resource_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    @patch('resource_manager.Transaction')
    @patch('resource_manager._create_and_add_instruction')
    def test_access_resource_success(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey, mock_find_pda):
        """Tests successful resource access payment."""
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance
        amount_lamports = 5000

        signature = resource_manager.access_resource(
            mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_USER_KEYPAIR, MOCK_RESOURCE_ID, str(MOCK_SERVER_PUBKEY), amount_lamports
        )

        mock_find_pda.assert_called_once_with(MOCK_SERVER_PUBKEY, MOCK_RESOURCE_ID, MOCK_PROGRAM_ID)
        mock_pubkey.assert_any_call(MOCK_PROGRAM_ID_STR)
        mock_pubkey.assert_any_call(str(MOCK_SERVER_PUBKEY))

        # Verify instruction data packing (adjust based on actual packing)
        # Assuming simple packing: instruction index 5, resource_id bytes, amount_lamports
        expected_instruction_data = struct.pack(f"<B{len(MOCK_RESOURCE_ID_BYTES)}sQ", 5, MOCK_RESOURCE_ID_BYTES, amount_lamports)
        expected_accounts = [
            AccountMeta(pubkey=MOCK_RESOURCE_STATE_PDA, is_signer=False, is_writable=False),
            AccountMeta(pubkey=MOCK_USER_PUBKEY, is_signer=True, is_writable=True),
            AccountMeta(pubkey=MOCK_SERVER_PUBKEY, is_signer=False, is_writable=True),
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        ]
        mock_create_add_ix.assert_called_once_with(mock_tx_instance, MOCK_PROGRAM_ID, *expected_accounts, data=expected_instruction_data)
        mock_solana_client.send_transaction.assert_called_once_with(mock_tx_instance, MOCK_USER_KEYPAIR)
        self.assertEqual(signature, str(MOCK_SIGNATURE.value))

    @patch('resource_manager.find_resource_state_pda', side_effect=PDAError("PDA Deriv Failed"))
    def test_access_resource_pda_error(self, mock_find_pda):
        """Tests ResourceAccessError on PDA derivation failure."""
        with self.assertRaises(PDAError): # Expect original PDAError
            resource_manager.access_resource(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_USER_KEYPAIR, MOCK_RESOURCE_ID, str(MOCK_SERVER_PUBKEY), 5000
            )

    @patch('resource_manager.find_resource_state_pda', return_value=(MOCK_RESOURCE_STATE_PDA, 255))
    @patch('resource_manager.Pubkey.from_string', side_effect=lambda s: Pubkey.from_string(s))
    @patch('resource_manager.Transaction')
    @patch('resource_manager._create_and_add_instruction')
    def test_access_resource_tx_error(self, mock_create_add_ix, mock_tx_constructor, mock_pubkey, mock_find_pda):
        """Tests ResourceAccessError on transaction sending failure."""
        mock_tx_instance = MagicMock(spec=Transaction)
        mock_tx_constructor.return_value = mock_tx_instance
        mock_solana_client.send_transaction.side_effect = TransactionError("Access Failed")

        with self.assertRaisesRegex(ResourceAccessError, f"Transaction failed during resource access for '{MOCK_RESOURCE_ID}': Access Failed"):
            resource_manager.access_resource(
                mock_solana_client, MOCK_PROGRAM_ID_STR, MOCK_USER_KEYPAIR, MOCK_RESOURCE_ID, str(MOCK_SERVER_PUBKEY), 5000
            )
        mock_solana_client.send_transaction.assert_called_once()


if __name__ == "__main__":
    unittest.main()