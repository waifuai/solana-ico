"""Handles configuration loading for the Solana ICO CLI."""

import os
import re
from typing import Optional

from dotenv import load_dotenv
from .exceptions import ConfigurationError

# Load environment variables from a .env file if it exists
# This allows for easy local configuration without setting system env vars
load_dotenv()

# --- Solana Cluster Configuration ---
DEFAULT_SOLANA_CLUSTER_URL: str = "http://localhost:8899"  # Default to local cluster
SOLANA_CLUSTER_URL: str = os.environ.get("SOLANA_CLUSTER_URL", DEFAULT_SOLANA_CLUSTER_URL)

if not SOLANA_CLUSTER_URL:
    # This case should ideally not happen with a default set, but good practice
    raise ConfigurationError("SOLANA_CLUSTER_URL environment variable is not set and no default is available.")

# Validate cluster URL format
if not validate_cluster_url(SOLANA_CLUSTER_URL):
    raise ConfigurationError(f"Invalid SOLANA_CLUSTER_URL format: {SOLANA_CLUSTER_URL}")

# --- Solana Program ID Configuration ---
# It's highly recommended to load the program ID from an environment variable
# as it can change between deployments (devnet, testnet, mainnet).
PROGRAM_ID_STR: Optional[str] = os.environ.get("SOLANA_PROGRAM_ID")

if not PROGRAM_ID_STR:
    # If you have a *fixed* program ID for a specific deployment (e.g., local testing),
    # you *could* uncomment the line below, but using env vars is more flexible.
    # PROGRAM_ID_STR = "YourDefaultProgramIdHere..." # Replace with actual ID if needed as fallback
    pass # Allow it to be None for now, CLI commands might require it explicitly if not set

# You could add other configuration variables here as needed,
# for example, default keypair paths, etc.

# Example: Default keypair path (optional)
# DEFAULT_KEYPAIR_PATH = os.path.expanduser("~/.config/solana/id.json")
# KEYPAIR_PATH = os.environ.get("SOLANA_KEYPAIR_PATH", DEFAULT_KEYPAIR_PATH)

def get_program_id() -> str:
    """
    Retrieves the Program ID from configuration.

    Returns:
        The Program ID as a string.

    Raises:
        ConfigurationError: If the Program ID is not configured or invalid.
    """
    if not PROGRAM_ID_STR:
        raise ConfigurationError(
            "SOLANA_PROGRAM_ID environment variable is not set. "
            "Please set this variable to your deployed program's ID."
        )

    if not validate_program_id(PROGRAM_ID_STR):
        raise ConfigurationError(
            f"Invalid program ID format: {PROGRAM_ID_STR}. "
            "Program IDs must be base58-encoded strings of 32 bytes (40-50 characters)."
        )

    return PROGRAM_ID_STR

def get_cluster_url() -> str:
    """Returns the configured Solana Cluster URL."""
    return SOLANA_CLUSTER_URL

def is_program_id_set() -> bool:
    """
    Checks if the Program ID is configured.

    Returns:
        True if Program ID is set, False otherwise.
    """
    return PROGRAM_ID_STR is not None and len(PROGRAM_ID_STR.strip()) > 0

def validate_cluster_url(url: str) -> bool:
    """
    Validates if the provided URL is a valid Solana cluster URL.

    Args:
        url: The URL to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False

    # Check if it's a valid HTTP/HTTPS URL
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    return url_pattern.match(url) is not None

def validate_program_id(program_id: str) -> bool:
    """
    Validates if the provided string is a valid Solana program ID.

    Args:
        program_id: The program ID to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not program_id or not isinstance(program_id, str):
        return False

    # Solana public keys are base58 strings of 32 bytes (43-44 characters)
    if len(program_id) < 40 or len(program_id) > 50:
        return False

    # Check if it's a valid base58 string (simplified check)
    base58_chars = set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
    return all(c in base58_chars for c in program_id)

def print_config() -> None:
    """Prints the current configuration values to stdout."""
    print("--- Solana ICO CLI Configuration ---")
    cluster_url = get_cluster_url()
    print(f"Cluster URL: {cluster_url}")

    try:
        program_id = get_program_id()
        print(f"Program ID: {program_id}")
        # Validate the configuration
        if not validate_cluster_url(cluster_url):
            print("⚠️  Warning: Cluster URL format may be invalid")
        if not validate_program_id(program_id):
            print("⚠️  Warning: Program ID format may be invalid")
    except ConfigurationError as e:
        print(f"Program ID: Not Set ({e})")
    print("------------------------------------")

def validate_configuration() -> None:
    """
    Validates the entire configuration and raises ConfigurationError if invalid.

    Raises:
        ConfigurationError: If any configuration value is invalid.
    """
    cluster_url = get_cluster_url()
    if not validate_cluster_url(cluster_url):
        raise ConfigurationError(f"Invalid cluster URL format: {cluster_url}")

    try:
        program_id = get_program_id()
        if not validate_program_id(program_id):
            raise ConfigurationError(f"Invalid program ID format: {program_id}")
    except ConfigurationError:
        # Re-raise if program ID is missing
        raise