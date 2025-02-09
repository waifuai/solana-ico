import pytest
import argparse
from unittest.mock import MagicMock, patch
from cli import token_commands

def test_add_token_commands():
    subparsers = MagicMock()
    token_commands.add_token_commands(subparsers)
    subparsers.add_parser.assert_called_with("generate_animation", help="Generate a Manim animation script")

@patch('cli.animation_templates.tokenized_economy_intro_template')
def test_handle_token_commands_intro(mock_intro_template):
    args = argparse.Namespace(command="generate_animation", animation_type="tokenized_economy_intro", title="My Title", subtitle="My Subtitle")
    mock_intro_template.return_value = "Mocked animation script"

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_commands.handle_token_commands(args)
    sys.stdout = sys.__stdout__

    assert "Generated animation script:\nMocked animation script" in captured_output.getvalue()
    mock_intro_template.assert_called_once_with("My Title", "My Subtitle")

@patch('cli.animation_templates.token_affiliates_animation_template')
def test_handle_token_commands_affiliates(mock_affiliates_template):
    args = argparse.Namespace(command="generate_animation", animation_type="token_affiliates_animation")
    mock_affiliates_template.return_value = "Mocked animation script"

    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_commands.handle_token_commands(args)
    sys.stdout = sys.__stdout__
    assert "Generated animation script:\nMocked animation script" in captured_output.getvalue()
    mock_affiliates_template.assert_called_once()

@patch('cli.animation_templates.tokenized_economy_intro_template')
def test_handle_token_commands_intro_default_values(mock_intro_template):
    args = argparse.Namespace(command="generate_animation", animation_type="tokenized_economy_intro", title=None, subtitle=None)
    mock_intro_template.return_value = "Mocked animation script"
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    token_commands.handle_token_commands(args)
    sys.stdout = sys.__stdout__
    mock_intro_template.assert_called_once_with("The Tokenized Economy", "A Solana-Based Barter System")