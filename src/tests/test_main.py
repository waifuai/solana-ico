import unittest
from unittest.mock import patch, MagicMock
import argparse
from io import StringIO
from main import main
from tokenomics import tokenomics
from solana_interactions import solana_interactions

from tests import test_bonding_curves
from tests import test_solana_interactions

class TestCLI(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='info'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_info_command(self, stdout_mock, parse_args_mock):
        main.main()
        expected_output = f"Name: {tokenomics.NAME}\\nSymbol: {tokenomics.SYMBOL}\\nTotal Supply: {tokenomics.TOTAL_SUPPLY}\\n"
        self.assertEqual(stdout_mock.getvalue(), expected_output)

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='balance', keypair_path='test_keypair.json'))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.get_balance', return_value=1000)
    @patch('sys.stdout', new_callable=StringIO)
    def test_balance_command(self, stdout_mock, get_balance_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertEqual(stdout_mock.getvalue(), "Balance: 1000 SOL\n")

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='send', keypair_path='test_keypair.json', to_public_key='test_pubkey', amount=100))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.send_sol', return_value='test_transaction_id')
    @patch('sys.stdout', new_callable=StringIO)
    def test_send_command(self, stdout_mock, send_sol_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertEqual(stdout_mock.getvalue(), "Send result: test_transaction_id\n")

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='ico', ico_command='init', program_id='test_program_id', keypair_path='test_keypair.json', token_mint='test_token_mint', total_supply=1000, base_price=1, scaling_factor=10))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.initialize_ico', return_value='test_transaction_id')
    @patch('sys.stdout', new_callable=StringIO)
    def test_ico_init_command(self, stdout_mock, initialize_ico_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertEqual(stdout_mock.getvalue(), "Initialize ICO result: test_transaction_id\n")

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='ico', ico_command='buy', program_id='test_program_id', keypair_path='test_keypair.json', amount=100))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.buy_tokens', return_value='test_transaction_id')
    @patch('sys.stdout', new_callable=StringIO)
    def test_ico_buy_command(self, stdout_mock, buy_tokens_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertEqual(stdout_mock.getvalue(), "Buy tokens result: test_transaction_id\n")

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='ico', ico_command='sell', program_id='test_program_id', keypair_path='test_keypair.json', amount=100))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.sell_tokens', return_value='test_transaction_id')
    @patch('sys.stdout', new_callable=StringIO)
    def test_ico_sell_command(self, stdout_mock, sell_tokens_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertEqual(stdout_mock.getvalue(), "Sell tokens result: test_transaction_id\n")

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='ico', ico_command='withdraw', program_id='test_program_id', keypair_path='test_keypair.json', amount=100))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.withdraw_from_escrow', return_value='test_transaction_id')
    @patch('sys.stdout', new_callable=StringIO)
    def test_ico_withdraw_command(self, stdout_mock, withdraw_from_escrow_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertEqual(stdout_mock.getvalue(), "Withdraw from escrow result: test_transaction_id\n")

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='resource', resource_command='create', program_id='test_program_id', keypair_path='test_keypair.json', resource_id='test_resource_id', access_fee=100))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.create_resource_access', return_value='test_transaction_id')
    @patch('sys.stdout', new_callable=StringIO)
    def test_resource_create_command(self, stdout_mock, create_resource_access_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertEqual(stdout_mock.getvalue(), "Create resource result: test_transaction_id\n")

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='resource', resource_command='access', program_id='test_program_id', keypair_path='test_keypair.json', resource_id='test_resource_id', amount=100))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana_interactions.load_keypair')
    @patch('solana_interactions.access_resource', side_effect=Exception("access_resource not fully implemented due to server key retrieval issue.  Needs resource_state_pda derivation with server key."))
    @patch('sys.stdout', new_callable=StringIO)
    def test_resource_access_command(self, stdout_mock, access_resource_mock, load_keypair_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertIn("Failed to access resource", stdout_mock.getvalue())

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(command='config', config_command='verify'))
    @patch('solana_interactions.connect_to_cluster')
    @patch('solana.rpc.api.Client.get_health', return_value={'result': 'ok'})
    @patch('sys.stdout', new_callable=StringIO)
    def test_config_verify_command(self, stdout_mock, get_health_mock, connect_to_cluster_mock, parse_args_mock):
        main.main()
        self.assertIn("Connection to Solana cluster successful. Health: {'result': 'ok'}", stdout_mock.getvalue())

class TestAll(unittest.TestSuite):
    def __init__(self):
        super().__init__()
        self.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_bonding_curves))
        self.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_solana_interactions))
        self.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestCLI))

if __name__ == "__main__":
    unittest.main()