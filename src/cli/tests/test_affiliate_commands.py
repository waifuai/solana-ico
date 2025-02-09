import pytest
import argparse
from unittest.mock import MagicMock
from cli import affiliate_commands, bonding_curves

def test_add_affiliate_commands():
    subparsers = MagicMock()
    affiliate_commands.add_affiliate_commands(subparsers)
    subparsers.add_parser.assert_called_with("calculate_commission", help="Calculate affiliate commission")

def test_handle_affiliate_commands_no_curve():
    args = argparse.Namespace(command="calculate_commission", investment_amount=100, commission_rate=None, curve_type=None)
    bonding_curves_mock = MagicMock()
    
    # Redirect stdout to capture output
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    affiliate_commands.handle_affiliate_commands(args, bonding_curves_mock)
    
    sys.stdout = sys.__stdout__  # Reset redirect.
    assert "Affiliate commission (rate 0.1): 10.0" in captured_output.getvalue()

def test_handle_affiliate_commands_custom_commission_rate():
    args = argparse.Namespace(command="calculate_commission", investment_amount=100, commission_rate=0.2, curve_type=None)
    bonding_curves_mock = MagicMock()
    
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output

    affiliate_commands.handle_affiliate_commands(args, bonding_curves_mock)
    
    sys.stdout = sys.__stdout__
    assert "Affiliate commission (rate 0.2): 20.0" in captured_output.getvalue()

def test_handle_affiliate_commands_linear_curve():
    args = argparse.Namespace(command="calculate_commission", investment_amount=100, commission_rate=None, curve_type="linear", supply=10, slope=2, initial_price=1)
    bonding_curves_mock = MagicMock()
    bonding_curves_mock.linear_price.return_value = 21  # supply * slope + initial_price
    
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output

    affiliate_commands.handle_affiliate_commands(args, bonding_curves_mock)
    sys.stdout = sys.__stdout__
    assert "Affiliate commission (linear curve, rate 0.1): 10.0" in captured_output.getvalue()
    bonding_curves_mock.linear_price.assert_called_once_with(10, 2, 1)

def test_handle_affiliate_commands_linear_curve_missing_params():
    args = argparse.Namespace(command="calculate_commission", investment_amount=100, commission_rate=None, curve_type="linear", supply=10, slope=None, initial_price=None)
    bonding_curves_mock = MagicMock()

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    affiliate_commands.handle_affiliate_commands(args, bonding_curves_mock)
    sys.stdout = sys.__stdout__
    assert "Error: Slope and initial price are required for linear curve" in captured_output.getvalue()


def test_handle_affiliate_commands_exponential_curve():
    args = argparse.Namespace(command="calculate_commission", investment_amount=100, commission_rate=0.15, curve_type="exponential", supply=5, scaling_factor=2, steepness=0.5)
    bonding_curves_mock = MagicMock()
    bonding_curves_mock.exponential_price.return_value = 24.36  # Dummy value
    
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    affiliate_commands.handle_affiliate_commands(args, bonding_curves_mock)
    sys.stdout = sys.__stdout__
    assert "Affiliate commission (exponential curve, rate 0.15): 15.0" in captured_output.getvalue()
    bonding_curves_mock.exponential_price.assert_called_once_with(5, 2, 0.5)

def test_handle_affiliate_commands_exponential_curve_missing_params():
     args = argparse.Namespace(command="calculate_commission", investment_amount=100, commission_rate=None, curve_type="exponential", supply=5, scaling_factor=None, steepness=None)
     bonding_curves_mock = MagicMock()

     import io
     import sys
     captured_output = io.StringIO()
     sys.stdout = captured_output
     affiliate_commands.handle_affiliate_commands(args, bonding_curves_mock)
     sys.stdout = sys.__stdout__
     assert "Error: Scaling factor and steepness are required for exponential curve" in captured_output.getvalue()