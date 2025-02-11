import unittest
from unittest.mock import patch, MagicMock
from solana_interactions import solana_interactions
from solana.keypair import Keypair
from solana.publickey import Pubkey
from solana.transaction import Transaction
from solana.instruction import Instruction, AccountMeta
import solana.sysvar.rent
import base64

class TestSolanaInteractions(unittest.TestCase):

    def test_load_keypair(self):
        # Create a dummy keypair file
        test_keypair_path = "test_keypair.json"
        with open(test_keypair_path, "w") as f:
            f.write("1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64")

        # Load the keypair
        keypair = solana_interactions.load_keypair(test_keypair_path)

        # Assert that the keypair is loaded (basic check)
        self.assertIsInstance(keypair, Keypair)

        # Clean up the dummy file
        import os
        os.remove(test_keypair_path)

    def test__create_and_add_instruction(self):
        transaction = Transaction()
        program_id = Pubkey("Gh9Ej26Vk9Topbn5RxQ61jyh1ipFSpLh2gh2kfzN9L")
        account_meta = AccountMeta(pubkey=Pubkey("11111111111111111111111111111111"), is_signer=False, is_writable=False)
        data = b'\x01\x02\x03'

        solana_interactions._create_and_add_instruction(transaction, program_id, account_meta, data=data)

        self.assertEqual(len(transaction.instructions), 1)
        self.assertEqual(transaction.instructions[0].program_id, program_id)
        self.assertEqual(transaction.instructions[0].accounts[0], account_meta)
        self.assertEqual(transaction.instructions[0].data, data)

if __name__ == "__main__":
    unittest.main()