import pytest
import argparse
from unittest.mock import MagicMock, patch
from cli import affiliate_management

def test_add_affiliate_management_commands():
    subparsers = MagicMock()
    affiliate_management.add_affiliate_management_commands(subparsers)
    assert subparsers.add_parser.call_count == 4
    subparsers.add_parser.assert_any_call("generate_referral_link", help="Generate a referral link for an affiliate")
    subparsers.add_parser.assert_any_call("record_referral", help="Record a referral in the smart contract")
    subparsers.add_parser.assert_any_call("update_commission_rate", help="Update an affiliate's commission rate for a token")
    subparsers.add_parser.assert_any_call("predict_rate", help="Predict the optimal commission rate for a token")

def test_handle_affiliate_management_commands_generate_referral_link():
    args = argparse.Namespace(command="generate_referral_link", affiliate_id="affiliate123")

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output

    affiliate_management.handle_affiliate_management_commands(args)
    sys.stdout = sys.__stdout__
    assert "Referral link: https://waifuai.com/ico?ref=affiliate123" in captured_output.getvalue()


def test_handle_affiliate_management_commands_record_referral():
    args = argparse.Namespace(command="record_referral", referral_code="ref123", user_wallet="0xabc")

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output

    affiliate_management.handle_affiliate_management_commands(args)
    sys.stdout = sys.__stdout__
    assert "Recording referral: Affiliate code ref123 - User wallet 0xabc" in captured_output.getvalue()


def test_handle_affiliate_management_commands_update_commission_rate():
    args = argparse.Namespace(command="update_commission_rate", affiliate_id="affiliate456", token_name="WAIFU", new_rate=0.15)

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output

    affiliate_management.handle_affiliate_management_commands(args)
    sys.stdout = sys.__stdout__
    assert "Updating commission rate: Affiliate affiliate456 - Token WAIFU - New rate 0.15" in captured_output.getvalue()


@patch('cli.rate_predictor.predict_rate')
def test_handle_affiliate_management_commands_predict_rate(mock_predict_rate):
    mock_predict_rate.return_value = 0.12
    args = argparse.Namespace(command="predict_rate", token_name="WAIFU")

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output

    affiliate_management.handle_affiliate_management_commands(args)
    sys.stdout = sys.__stdout__

    assert "Predicted optimal commission rate for WAIFU: 0.12" in captured_output.getvalue()
    mock_predict_rate.assert_called_once_with({}, {}, {})