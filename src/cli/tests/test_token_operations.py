import pytest
import argparse
from unittest.mock import MagicMock, patch
from cli import token_operations, bonding_curves

def test_add_token_operations_commands():
    subparsers = MagicMock()
    token_operations.add_token_operations_commands(subparsers)
    assert subparsers.add_parser.call_count == 3
    subparsers.add_parser.assert_any_call("ico", help="Simulate an ICO")
    subparsers.add_parser.assert_any_call("exchange_tokens", help="Exchange tokens between two companies")
    subparsers.add_parser.assert_any_call("create_token", help="Create a new token")

def test_handle_token_operations_commands_ico():
    args = argparse.Namespace(command="ico", token_name="WAIFU", initial_price=0.1, launch_cost=5000)
    
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_operations.handle_token_operations_commands(args)
    sys.stdout = sys.__stdout__
    assert "Simulating ICO for WAIFU with initial price 0.1 and launch cost 5000" in captured_output.getvalue()

def test_handle_token_operations_commands_create_token():
    args = argparse.Namespace(command="create_token", token_name="MyToken", token_symbol="MTK", token_supply=1000000)
    
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_operations.handle_token_operations_commands(args)
    sys.stdout = sys.__stdout__
    assert "Creating token: Name MyToken - Symbol MTK - Supply 1000000.0" in captured_output.getvalue()

@patch('cli.bonding_curves.linear_price')
@patch('cli.bonding_curves.exponential_price')
def test_handle_token_operations_commands_exchange_tokens_linear(mock_exponential, mock_linear):
    mock_linear.side_effect = [10, 20] # Price A, Price B
    args = argparse.Namespace(command="exchange_tokens", token_a="WAIFU", token_b="SOL", amount_a=100,
                              curve_type_a="linear", supply_a=5, slope_a=2, initial_price_a=0,
                              curve_type_b="linear", supply_b=10, slope_b=2, initial_price_b=0)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_operations.handle_token_operations_commands(args)
    sys.stdout = sys.__stdout__

    assert "Exchanging 100 WAIFU for 50.0 SOL at an exchange rate of 0.50" in captured_output.getvalue()
    mock_linear.assert_any_call(5,2,0)
    mock_linear.assert_any_call(10,2,0)
    mock_exponential.assert_not_called()

@patch('cli.bonding_curves.linear_price')
@patch('cli.bonding_curves.exponential_price')
def test_handle_token_operations_commands_exchange_tokens_exponential(mock_exponential, mock_linear):
     mock_exponential.side_effect = [5, 10]
     args = argparse.Namespace(command="exchange_tokens", token_a="WAIFU", token_b="SOL", amount_a=100,
                              curve_type_a="exponential", supply_a=5, scaling_factor_a=1, steepness_a=1,
                              curve_type_b="exponential", supply_b=5, scaling_factor_b=2, steepness_b=1)
     import io
     import sys
     captured_output = io.StringIO()
     sys.stdout = captured_output
     token_operations.handle_token_operations_commands(args)
     sys.stdout = sys.__stdout__

     assert "Exchanging 100 WAIFU for 50.0 SOL at an exchange rate of 0.50" in captured_output.getvalue()
     mock_exponential.assert_any_call(5, 1, 1)
     mock_exponential.assert_any_call(5, 2, 1)
     mock_linear.assert_not_called()

def test_handle_token_operations_missing_curve_type():
    args = argparse.Namespace(command="exchange_tokens", token_a="WAIFU", token_b="SOL", amount_a=100,
                                  curve_type_a=None, supply_a=5, slope_a=2, initial_price_a=0,
                                  curve_type_b="linear", supply_b=10, slope_b=2, initial_price_b=0)
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_operations.handle_token_operations_commands(args)
    sys.stdout = sys.__stdout__
    assert "Error: curve_type_a, supply_a, curve_type_b, and supply_b are required for token exchange" in captured_output.getvalue()

def test_handle_token_operations_missing_linear_params():
    args = argparse.Namespace(command="exchange_tokens", token_a="WAIFU", token_b="SOL", amount_a=100,
                              curve_type_a="linear", supply_a=5, slope_a=None, initial_price_a=None,
                              curve_type_b="linear", supply_b=10, slope_b=2, initial_price_b=0)
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_operations.handle_token_operations_commands(args)
    sys.stdout = sys.__stdout__
    assert "Error: slope_a and initial_price_a are required for linear curve for token A" in captured_output.getvalue()

def test_handle_token_operations_missing_exponential_params():
     args = argparse.Namespace(command="exchange_tokens", token_a="WAIFU", token_b="SOL", amount_a=100,
                              curve_type_a="exponential", supply_a=5, scaling_factor_a=None, steepness_a=None,
                              curve_type_b="linear", supply_b=10, slope_b=2, initial_price_b=0)
     import io
     import sys
     captured_output = io.StringIO()
     sys.stdout = captured_output
     token_operations.handle_token_operations_commands(args)
     sys.stdout = sys.__stdout__

     assert "Error: scaling_factor_a and steepness_a are required for exponential curve for token A" in captured_output.getvalue()