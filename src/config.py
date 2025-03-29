"""Handles configuration loading for the Solana ICO CLI."""

import os
from dotenv import load_dotenv
from .exceptions import ConfigurationError

# Load environment variables from a .env file if it exists
# This allows for easy local configuration without setting system env vars
load_dotenv()

# --- Solana Cluster Configuration ---
DEFAULT_SOLANA_CLUSTER_URL = "http://localhost:8899" # Default to local cluster
SOLANA_CLUSTER_URL = os.environ.get("SOLANA_CLUSTER_URL", DEFAULT_SOLANA_CLUSTER_URL)

if not SOLANA_CLUSTER_URL:
    # This case should ideally not happen with a default set, but good practice
    raise ConfigurationError("SOLANA_CLUSTER_URL environment variable is not set and no default is available.")

# --- Solana Program ID Configuration ---
# It's highly recommended to load the program ID from an environment variable
# as it can change between deployments (devnet, testnet, mainnet).
PROGRAM_ID_STR = os.environ.get("SOLANA_PROGRAM_ID")

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
    Retrieves the Program ID.

    Raises:
        ConfigurationError: If the Program ID is not configured via environment variable.

    Returns:
        The Program ID as a string.
    """
    prog_id = PROGRAM_ID_STR
    if not prog_id:
        raise ConfigurationError(
            "SOLANA_PROGRAM_ID environment variable is not set. "
            "Please set this variable to your deployed program's ID."
        )
    return prog_id

def get_cluster_url() -> str:
    """Returns the configured Solana Cluster URL."""
    return SOLANA_CLUSTER_URL

# Optional: Add a function to print current config for verification
def print_config():
    """Prints the current configuration values."""
    print("--- Solana ICO CLI Configuration ---")
    print(f"Cluster URL: {get_cluster_url()}")
    try:
        print(f"Program ID: {get_program_id()}")
    except ConfigurationError as e:
        print(f"Program ID: Not Set ({e})")
    print("------------------------------------")