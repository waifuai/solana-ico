"""
Unit tests for the PDA utilities module.

This module contains unit tests for the Program Derived Address (PDA) utility
functions, including tests for ICO state PDA derivation, escrow PDA derivation,
and resource state PDA derivation. Tests verify correct seed generation and
PDA calculation using mocked Solana program address functionality.
"""

import unittest
from unittest.mock import patch, MagicMock

# Import functions and exception from src
import pda_utils
from exceptions import PDAError

# Import solders types
from solders.pubkey import Pubkey

# Mock data
MOCK_OWNER_PUBKEY = Pubkey.new_unique()
MOCK_SERVER_PUBKEY = Pubkey.new_unique()
MOCK_PROGRAM_ID = Pubkey.new_unique()
MOCK_RESOURCE_ID = "test_resource_123"
MOCK_RESOURCE_ID_BYTES = MOCK_RESOURCE_ID.encode('utf-8')

MOCK_ICO_PDA = Pubkey.new_unique()
MOCK_ICO_BUMP = 255
MOCK_ESCROW_PDA = Pubkey.new_unique()
MOCK_ESCROW_BUMP = 254
MOCK_RESOURCE_PDA = Pubkey.new_unique()
MOCK_RESOURCE_BUMP = 253

class TestPdaUtils(unittest.TestCase):

    @patch('pda_utils.Pubkey.find_program_address')
    def test_find_ico_state_pda_success(self, mock_find_program_address):
        """Tests successful derivation of ICO state PDA."""
        mock_find_program_address.return_value = (MOCK_ICO_PDA, MOCK_ICO_BUMP)

        pda, bump = pda_utils.find_ico_state_pda(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)

        # Verify find_program_address was called with correct seeds
        expected_seeds = [b"ico_state", bytes(MOCK_OWNER_PUBKEY)]
        mock_find_program_address.assert_called_once_with(expected_seeds, MOCK_PROGRAM_ID)

        self.assertEqual(pda, MOCK_ICO_PDA)
        self.assertEqual(bump, MOCK_ICO_BUMP)

    @patch('pda_utils.Pubkey.find_program_address', side_effect=Exception("Derivation failed"))
    def test_find_ico_state_pda_error(self, mock_find_program_address):
        """Tests PDAError on derivation failure for ICO state PDA."""
        with self.assertRaisesRegex(PDAError, "Failed to find ICO state PDA: Derivation failed"):
            pda_utils.find_ico_state_pda(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)

    @patch('pda_utils.Pubkey.find_program_address')
    def test_find_escrow_pda_success(self, mock_find_program_address):
        """Tests successful derivation of escrow PDA."""
        mock_find_program_address.return_value = (MOCK_ESCROW_PDA, MOCK_ESCROW_BUMP)

        pda, bump = pda_utils.find_escrow_pda(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)

        # Verify find_program_address was called with correct seeds
        expected_seeds = [b"escrow_account", bytes(MOCK_OWNER_PUBKEY)]
        mock_find_program_address.assert_called_once_with(expected_seeds, MOCK_PROGRAM_ID)

        self.assertEqual(pda, MOCK_ESCROW_PDA)
        self.assertEqual(bump, MOCK_ESCROW_BUMP)

    @patch('pda_utils.Pubkey.find_program_address', side_effect=Exception("Derivation failed"))
    def test_find_escrow_pda_error(self, mock_find_program_address):
        """Tests PDAError on derivation failure for escrow PDA."""
        with self.assertRaisesRegex(PDAError, "Failed to find escrow PDA: Derivation failed"):
            pda_utils.find_escrow_pda(MOCK_OWNER_PUBKEY, MOCK_PROGRAM_ID)

    @patch('pda_utils.Pubkey.find_program_address')
    def test_find_resource_state_pda_success(self, mock_find_program_address):
        """Tests successful derivation of resource state PDA."""
        mock_find_program_address.return_value = (MOCK_RESOURCE_PDA, MOCK_RESOURCE_BUMP)

        pda, bump = pda_utils.find_resource_state_pda(MOCK_SERVER_PUBKEY, MOCK_RESOURCE_ID, MOCK_PROGRAM_ID)

        # Verify find_program_address was called with correct seeds
        expected_seeds = [b"resource_state", bytes(MOCK_SERVER_PUBKEY), MOCK_RESOURCE_ID_BYTES]
        mock_find_program_address.assert_called_once_with(expected_seeds, MOCK_PROGRAM_ID)

        self.assertEqual(pda, MOCK_RESOURCE_PDA)
        self.assertEqual(bump, MOCK_RESOURCE_BUMP)

    @patch('pda_utils.Pubkey.find_program_address', side_effect=Exception("Derivation failed"))
    def test_find_resource_state_pda_error(self, mock_find_program_address):
        """Tests PDAError on derivation failure for resource state PDA."""
        with self.assertRaisesRegex(PDAError, f"Failed to find resource state PDA for resource '{MOCK_RESOURCE_ID}': Derivation failed"):
            pda_utils.find_resource_state_pda(MOCK_SERVER_PUBKEY, MOCK_RESOURCE_ID, MOCK_PROGRAM_ID)

if __name__ == "__main__":
    unittest.main()