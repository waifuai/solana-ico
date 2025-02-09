import pytest
import argparse
from unittest.mock import MagicMock, patch
from cli import token_management

def test_add_token_management_commands():
    subparsers = MagicMock()
    token_management.add_token_management_commands(subparsers)
    assert subparsers.add_parser.call_count == 3
    subparsers.add_parser.assert_any_call("optimize_portfolio", help="Optimize a portfolio of tokens using AI")
    subparsers.add_parser.assert_any_call("find_trade_route", help="Find the optimal trade route between tokens")
    subparsers.add_parser.assert_any_call("adjust_curve", help="Adjust bonding curve parameters based on market data")

@patch('cli.portfolio_optimizer.optimize_portfolio')
def test_handle_token_management_commands_optimize_portfolio(mock_optimize_portfolio):
    mock_optimize_portfolio.return_value = {"WAIFU": 0.5, "SOL": 0.5}
    args = argparse.Namespace(command="optimize_portfolio", tokens=["WAIFU", "SOL"])

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_management.handle_token_management_commands(args)
    sys.stdout = sys.__stdout__

    assert "Optimized portfolio: {'WAIFU': 0.5, 'SOL': 0.5}" in captured_output.getvalue()
    mock_optimize_portfolio.assert_called_once_with(["WAIFU", "SOL"])

@patch('cli.pathfinder.find_trade_route')
def test_handle_token_management_commands_find_trade_route(mock_find_trade_route):
    mock_find_trade_route.return_value = ["WAIFU", "SOL", "USDC"]
    args = argparse.Namespace(command="find_trade_route", tokens=["WAIFU", "SOL", "USDC"], exchange_rates=None)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_management.handle_token_management_commands(args)
    sys.stdout = sys.__stdout__
    assert "Optimal trade route: ['WAIFU', 'SOL', 'USDC']" in captured_output.getvalue()
    mock_find_trade_route.assert_called_once_with(["WAIFU", "SOL", "USDC"], {})

@patch('cli.curve_adjuster.adjust_curve')
def test_handle_token_management_commands_adjust_curve(mock_adjust_curve):
    mock_adjust_curve.return_value = {"slope": 0.12, "initial_price": 1}
    args = argparse.Namespace(command="adjust_curve", curve_type="linear", current_params=None, market_data=None, adjustment_algorithm=None)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_management.handle_token_management_commands(args)
    sys.stdout = sys.__stdout__

    assert "Adjusted curve parameters: {'slope': 0.12, 'initial_price': 1}" in captured_output.getvalue()
    mock_adjust_curve.assert_called_once_with("linear", {"slope": 0.1, "initial_price": 1}, {"demand": 1.2}, "simple_demand_adjustment")