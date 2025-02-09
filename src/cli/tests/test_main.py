# test_main.py
import pytest
from unittest.mock import patch
from cli.main import main

@patch('argparse.ArgumentParser.parse_args')
def test_main_no_args(mock_parse_args):
    # Test the main function with no arguments
    mock_parse_args.return_value = argparse.Namespace(command=None)
    main() # Should just run without error

@patch('argparse.ArgumentParser.parse_args')
@patch('cli.token_commands.handle_token_commands')
def test_main_generate_animation(mock_handle_token_commands, mock_parse_args):
    mock_parse_args.return_value = argparse.Namespace(command='generate_animation')
    main()
    mock_handle_token_commands.assert_called_once()

@patch('argparse.ArgumentParser.parse_args')
@patch('cli.token_management.handle_token_management_commands')
def test_main_optimize_portfolio(mock_handle, mock_parse_args):
    mock_parse_args.return_value = argparse.Namespace(command='optimize_portfolio')
    main()
    mock_handle.assert_called_once()

@patch('argparse.ArgumentParser.parse_args')
@patch('cli.affiliate_commands.handle_affiliate_commands')
def test_main_affiliate_commands(mock_handle, mock_parse_args):
    mock_parse_args.return_value = argparse.Namespace(command='calculate_commission')
    main()
    mock_handle.assert_called_once()