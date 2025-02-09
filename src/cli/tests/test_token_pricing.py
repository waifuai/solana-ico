import pytest
import argparse
from unittest.mock import MagicMock, patch
from cli import token_pricing

def test_add_token_pricing_commands():
    subparsers = MagicMock()
    token_pricing.add_token_pricing_commands(subparsers)
    assert subparsers.add_parser.call_count == 2
    subparsers.add_parser.assert_any_call("calculate_price", help="Calculate token price based on bonding curve")
    subparsers.add_parser.assert_any_call("calculate_buy_sell_price", help="Calculate the cost to buy or revenue from selling tokens")

@patch('cli.bonding_curves.linear_price')
def test_handle_token_pricing_commands_linear(mock_linear_price):
    mock_linear_price.return_value = 25
    args = argparse.Namespace(command="calculate_price", curve_type="linear", supply=10, slope=2, initial_price=5)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Price for linear curve: 25" in captured_output.getvalue()
    mock_linear_price.assert_called_once_with(10, 2, 5)

@patch('cli.bonding_curves.exponential_price')
def test_handle_token_pricing_commands_exponential(mock_exponential_price):
    mock_exponential_price.return_value = 5.4365636
    args = argparse.Namespace(command="calculate_price", curve_type="exponential", supply=2, scaling_factor=2, steepness=0.5)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Price for exponential curve: 5.4365636" in captured_output.getvalue()
    mock_exponential_price.assert_called_once_with(2, 2, 0.5)

@patch('cli.bonding_curves.sigmoid_price')
def test_handle_token_pricing_commands_sigmoid(mock_sigmoid_price):
    mock_sigmoid_price.return_value = 5
    args = argparse.Namespace(command="calculate_price", curve_type="sigmoid", supply=0, k = 10, a = 1, b = 0)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Price for sigmoid curve: 5" in captured_output.getvalue()
    mock_sigmoid_price.assert_called_once_with(0, 10, 1, 0)

@patch('cli.bonding_curves.polynomial_price')
def test_handle_token_pricing_commands_polynomial(mock_polynomial_price):
    mock_polynomial_price.return_value = 17
    args = argparse.Namespace(command="calculate_price", curve_type="polynomial", supply=2, coefficients=[1,2,3])

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Price for polynomial curve: 17" in captured_output.getvalue()
    mock_polynomial_price.assert_called_once_with(2, [1,2,3])

def test_handle_token_pricing_commands_linear_missing_params():
    args = argparse.Namespace(command="calculate_price", curve_type="linear", supply=10, slope=None, initial_price=None)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__
    assert "Error: Slope and initial price are required for linear curve" in captured_output.getvalue()

def test_handle_token_pricing_commands_exponential_missing_params():
    args = argparse.Namespace(command="calculate_price", curve_type="exponential", supply=10, scaling_factor=None, steepness=None)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__
    assert "Error: Scaling factor and steepness are required for exponential curve" in captured_output.getvalue()

def test_handle_token_pricing_commands_sigmoid_missing_params():
    args = argparse.Namespace(command="calculate_price", curve_type="sigmoid", supply=0, k = None, a = None, b = None)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Error: k, a, and b are required for sigmoid curve" in captured_output.getvalue()

def test_handle_token_pricing_commands_polynomial_missing_params():
    args = argparse.Namespace(command="calculate_price", curve_type="polynomial", supply=0, coefficients=None)
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Error: coefficients are required for polynomial curve" in captured_output.getvalue()

def test_handle_token_pricing_commands_buy_sell_positive_delta_s():
    args = argparse.Namespace(command="calculate_buy_sell_price", supply=10, delta_s=5, slope=2, y_intercept=1)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Cost to buy 5 tokens: 112.5" in captured_output.getvalue()  # 2 * (5**2)/2 + (2 * 10 + 1)*5

def test_handle_token_pricing_commands_buy_sell_negative_delta_s():
    args = argparse.Namespace(command="calculate_buy_sell_price", supply=10, delta_s=-5, slope=2, y_intercept=1)
    
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_pricing.handle_token_pricing_commands(args)
    sys.stdout = sys.__stdout__

    assert "Revenue from selling 5 tokens: -87.5" in captured_output.getvalue()  # 2 * (-5)**2 / 2 + (2 * 10 + 1) * -5