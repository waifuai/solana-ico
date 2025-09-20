"""
Main entry point and CLI interface for the Solana ICO application.

This module serves as the main entry point for the ContextCoin (CTX) Solana ICO CLI.
It provides a command-line interface using Typer for managing ICO operations,
resource access, and configuration. The CLI supports operations like initializing
ICOs, buying/selling tokens, managing resources, and interacting with the Solana
blockchain through a structured command hierarchy.
"""

import sys
from typing import Tuple

import typer
from typing_extensions import Annotated

# Use relative imports for modules within the 'src' directory
from . import config
from . import tokenomics
from .exceptions import (
    ConfigurationError,
    ICOError,
    KeypairError,
    PDAError,
    ResourceError,
    SolanaConnectionError,
    SolanaIcoError,
    TransactionError,
)
from .ico_manager import (
    buy_tokens,
    initialize_ico,
    sell_tokens,
    withdraw_from_escrow,
)
from .resource_manager import access_resource, create_resource_access
from .solana_client import SolanaClient

# --- Typer App Initialization ---
app = typer.Typer(
    help="ContextCoin (CTX) Solana CLI - Manage ICO and Resources",
    epilog="For more information, visit: https://github.com/waifuai/solana-ico"
)
ico_app = typer.Typer(
    help="ICO operations - Initialize, buy, sell tokens, and manage escrow",
    epilog="All ICO operations require a configured Solana cluster and program ID."
)
resource_app = typer.Typer(
    help="Resource access operations - Create and access off-chain resources",
    epilog="Resource operations allow pay-to-access functionality for premium content."
)
config_app = typer.Typer(
    help="Configuration commands - Show, verify, and validate CLI settings",
    epilog="Use 'config verify' to test your Solana cluster connection."
)

app.add_typer(ico_app, name="ico")
app.add_typer(resource_app, name="resource")
app.add_typer(config_app, name="config")

# Constants
LAMPORTS_PER_SOL: int = 1_000_000_000

# --- Helper Function for Common Logic ---
def get_client_and_program_id() -> Tuple[SolanaClient, str]:
    """Instantiates client and gets program ID, handling config errors."""
    client = SolanaClient()  # Handles connection errors internally
    program_id = config.get_program_id()  # Handles missing program ID error
    return client, program_id

# --- Top-Level Commands ---

@app.command("info")
def info_command() -> None:
    """
    Display ContextCoin token information.

    Shows basic token details including name, symbol, total supply,
    and decimal places. This information is static and doesn't require
    a Solana cluster connection.
    """
    print(f"Name: {tokenomics.NAME}")
    print(f"Symbol: {tokenomics.SYMBOL}")
    print(f"Total Supply: {tokenomics.TOTAL_SUPPLY:,} tokens")
    print(f"Decimals: {tokenomics.DECIMAL_PLACES}")
    print(f"Initial Price: {tokenomics.STARTING_PRICE} SOL per token")
    print(f"Scaling Factor: {tokenomics.SCALING_FACTOR:,}")

@app.command("balance")
def balance_command(
    public_key: Annotated[str, typer.Argument(help="Public key of the account to check (base58 string)")]
) -> None:
    """
    Get the SOL balance of a Solana account.

    This command queries the Solana cluster for the account balance
    and displays it in both SOL and lamports.

    Example:
        python -m src.main balance 11111111111111111111111111111112
    """
    client, _ = get_client_and_program_id()  # Client needed, program_id not
    balance_lamports = client.get_balance(public_key)
    balance_sol = balance_lamports / LAMPORTS_PER_SOL  # Convert lamports to SOL
    print(f"Balance for {public_key}:")
    print(f"  {balance_sol:.9f} SOL")
    print(f"  {balance_lamports:,} lamports")

@app.command("send")
def send_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the sender's keypair file (JSON format)")],
    to_public_key: Annotated[str, typer.Argument(help="Recipient's public key (base58 string)")],
    amount: Annotated[int, typer.Argument(help="Amount to send in lamports (1 SOL = 1,000,000,000 lamports)")]
) -> None:
    """
    Send SOL from one account to another.

    Transfers SOL from the specified keypair to the recipient address.
    The sender must have sufficient balance and the keypair file must exist.

    Example:
        python -m src.main send ~/keys/my-keypair.json 11111111111111111111111111111112 1000000000
    """
    client, _ = get_client_and_program_id()
    sender_keypair = client.load_keypair(keypair_path)
    signature = client.send_sol(sender_keypair, to_public_key, amount)
    print(f"✅ Successfully sent {amount:,} lamports ({amount / LAMPORTS_PER_SOL:.9f} SOL)")
    print(f"📝 Transaction signature: {signature}")

# --- ICO Subcommands ---

@ico_app.command("init")
def init_ico_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the owner's keypair file (JSON format)")],
    token_mint: Annotated[str, typer.Argument(help="SPL token mint address (base58 string)")],
    total_supply: Annotated[int, typer.Argument(help="Total supply of the token")],
    base_price: Annotated[int, typer.Argument(help="Initial price in lamports (1 SOL = 1,000,000,000 lamports)")],
    scaling_factor: Annotated[int, typer.Argument(help="Scaling factor for bonding curve (higher = slower price increase)")]
) -> None:
    """
    Initialize the ICO on the Solana blockchain.

    Sets up the ICO state account with the specified parameters. This is a one-time
    operation that must be performed by the ICO owner. The ICO will use a linear
    bonding curve based on the provided parameters.

    Example:
        python -m src.main ico init ~/keys/owner-keypair.json TokenMint111111111111111111111111111111111 1000000000 1000000000 100000000
    """
    client, program_id = get_client_and_program_id()
    owner_keypair = client.load_keypair(keypair_path)
    signature = initialize_ico(
        solana_client=client,
        program_id_str=program_id,
        owner_keypair=owner_keypair,
        token_mint_str=token_mint,
        total_supply=total_supply,
        base_price=base_price,
        scaling_factor=scaling_factor
    )
    print(f"✅ ICO initialized successfully!")
    print(f"📝 Transaction signature: {signature}")

@ico_app.command("buy")
def buy_tokens_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the buyer's keypair file (JSON format)")],
    amount: Annotated[int, typer.Argument(help="Amount of SOL to spend in lamports")],
    ico_owner_pubkey: Annotated[str, typer.Argument(help="Public key of the ICO owner (base58 string)")],
    token_mint: Annotated[str, typer.Argument(help="SPL token mint address (base58 string)")]
) -> None:
    """
    Buy CTX tokens from the ICO using SOL.

    Exchanges SOL for CTX tokens at the current bonding curve price. If the buyer
    doesn't have an associated token account, one will be created automatically.

    Example:
        python -m src.main ico buy ~/keys/buyer-keypair.json 1000000000 OwnerPubkey11111111111111111111111111111111 TokenMint111111111111111111111111111111111
    """
    client, program_id = get_client_and_program_id()
    buyer_keypair = client.load_keypair(keypair_path)
    signature = buy_tokens(
        solana_client=client,
        program_id_str=program_id,
        buyer_keypair=buyer_keypair,
        amount_lamports=amount,
        ico_owner_pubkey_str=ico_owner_pubkey,
        token_mint_str=token_mint
    )
    print(f"✅ Successfully bought tokens!")
    print(f"💰 Amount spent: {amount:,} lamports ({amount / LAMPORTS_PER_SOL:.9f} SOL)")
    print(f"📝 Transaction signature: {signature}")

@ico_app.command("sell")
def sell_tokens_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the seller's keypair file (JSON format)")],
    amount: Annotated[int, typer.Argument(help="Amount of CTX tokens to sell")],
    ico_owner_pubkey: Annotated[str, typer.Argument(help="Public key of the ICO owner (base58 string)")],
    token_mint: Annotated[str, typer.Argument(help="SPL token mint address (base58 string)")]
) -> None:
    """
    Sell CTX tokens back to the ICO for SOL.

    Exchanges CTX tokens for SOL at the current bonding curve price. The seller
    must have the tokens in their associated token account.

    Example:
        python -m src.main ico sell ~/keys/seller-keypair.json 100 OwnerPubkey11111111111111111111111111111111 TokenMint111111111111111111111111111111111
    """
    client, program_id = get_client_and_program_id()
    seller_keypair = client.load_keypair(keypair_path)
    signature = sell_tokens(
        solana_client=client,
        program_id_str=program_id,
        seller_keypair=seller_keypair,
        amount_tokens=amount,
        ico_owner_pubkey_str=ico_owner_pubkey,
        token_mint_str=token_mint
    )
    print(f"✅ Successfully sold {amount:,} tokens!")
    print(f"📝 Transaction signature: {signature}")

@ico_app.command("withdraw")
def withdraw_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the owner's keypair file (JSON format)")],
    amount: Annotated[int, typer.Argument(help="Amount of SOL to withdraw in lamports")]
) -> None:
    """
    Withdraw SOL from the ICO escrow account (owner only).

    Allows the ICO owner to withdraw accumulated SOL from the escrow account.
    This can only be called by the ICO owner.

    Example:
        python -m src.main ico withdraw ~/keys/owner-keypair.json 500000000
    """
    client, program_id = get_client_and_program_id()
    owner_keypair = client.load_keypair(keypair_path)
    signature = withdraw_from_escrow(
        solana_client=client,
        program_id_str=program_id,
        owner_keypair=owner_keypair,
        amount_lamports=amount
    )
    print(f"✅ Successfully withdrew {amount:,} lamports ({amount / LAMPORTS_PER_SOL:.9f} SOL) from escrow!")
    print(f"📝 Transaction signature: {signature}")

# --- Resource Subcommands ---

@resource_app.command("create")
def create_resource_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the server's keypair file (JSON format)")],
    resource_id: Annotated[str, typer.Argument(help="Unique resource identifier (e.g., 'premium_api', 'vip_content')")],
    access_fee: Annotated[int, typer.Argument(help="Access fee in lamports (1 SOL = 1,000,000,000 lamports)")]
) -> None:
    """
    Create or update resource access information on-chain.

    Sets up a resource that can be accessed by paying the specified fee.
    The server (resource owner) can update the access fee at any time.

    Example:
        python -m src.main resource create ~/keys/server-keypair.json premium_api 50000000
    """
    client, program_id = get_client_and_program_id()
    server_keypair = client.load_keypair(keypair_path)
    signature = create_resource_access(
        solana_client=client,
        program_id_str=program_id,
        server_keypair=server_keypair,
        resource_id=resource_id,
        access_fee=access_fee
    )
    print(f"✅ Resource access '{resource_id}' created/updated successfully!")
    print(f"💰 Access fee: {access_fee:,} lamports ({access_fee / LAMPORTS_PER_SOL:.9f} SOL)")
    print(f"📝 Transaction signature: {signature}")

@resource_app.command("access")
def access_resource_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the user's keypair file (JSON format)")],
    resource_id: Annotated[str, typer.Argument(help="Unique resource identifier")],
    server_pubkey: Annotated[str, typer.Argument(help="Public key of the server managing the resource (base58 string)")],
    amount: Annotated[int, typer.Argument(help="Amount of SOL to spend in lamports (must match resource fee)")]
) -> None:
    """
    Pay to access a registered resource.

    Transfers the access fee to the resource server in exchange for access.
    The amount must exactly match the resource's access fee.

    Example:
        python -m src.main resource access ~/keys/user-keypair.json premium_api ServerPubkey11111111111111111111111111111111 50000000
    """
    client, program_id = get_client_and_program_id()
    user_keypair = client.load_keypair(keypair_path)
    signature = access_resource(
        solana_client=client,
        program_id_str=program_id,
        user_keypair=user_keypair,
        resource_id=resource_id,
        server_pubkey_str=server_pubkey,
        amount_lamports=amount
    )
    print(f"✅ Successfully paid {amount:,} lamports ({amount / LAMPORTS_PER_SOL:.9f} SOL) to access resource '{resource_id}'!")
    print(f"📝 Transaction signature: {signature}")

# --- Config Subcommands ---

@config_app.command("verify")
def verify_config_command() -> None:
    """
    Verify the CLI's configuration and connection to the Solana cluster.

    Tests that:
    - Environment variables are properly set
    - Configuration values are valid
    - Connection to the Solana cluster can be established
    - Program ID is accessible
    """
    print("🔍 Verifying configuration and connection...")
    try:
        # Test configuration validation
        config.validate_configuration()
        print("✅ Configuration validation passed")

        # Test connection and get program ID
        client, prog_id = get_client_and_program_id()
        print(f"✅ Successfully connected to cluster: {client.cluster_url}")
        print(f"✅ Program ID configured: {prog_id}")
        print("\n🎉 Verification successful! Your CLI is ready to use.")
    except (ConfigurationError, SolanaConnectionError) as e:
        print(f"\n❌ Verification Failed: {e}", file=sys.stderr)
        print("\n💡 Troubleshooting tips:", file=sys.stderr)
        print("   - Check that SOLANA_CLUSTER_URL and SOLANA_PROGRAM_ID are set in your environment", file=sys.stderr)
        print("   - Ensure your Solana cluster is running (use 'solana-test-validator' for local development)", file=sys.stderr)
        print("   - Verify your program ID is correct and the program is deployed", file=sys.stderr)
        sys.exit(1)

@config_app.command("show")
def show_config_command() -> None:
    """
    Display the current configuration values.

    Shows the cluster URL, program ID, and validation status.
    Use this to verify your environment variables are loaded correctly.
    """
    config.print_config()


# --- Main Execution & Error Handling ---

def run_app() -> None:
    """Runs the Typer app and handles errors gracefully."""
    try:
        app()
    # --- Specific Error Handling ---
    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        print("Please check your environment variables (SOLANA_CLUSTER_URL, SOLANA_PROGRAM_ID) or .env file.", file=sys.stderr)
        sys.exit(1)
    except KeypairError as e:
        print(f"❌ Keypair Error: {e}", file=sys.stderr)
        print("Please verify the keypair file path and format.", file=sys.stderr)
        sys.exit(1)
    except SolanaConnectionError as e:
        print(f"❌ Connection Error: {e}", file=sys.stderr)
        cluster_url = "unknown"
        try:
            cluster_url = config.get_cluster_url()
        except ConfigurationError:
            pass  # Keep default message
        print(f"Please ensure the Solana cluster/validator at '{cluster_url}' is running and accessible.", file=sys.stderr)
        print("If using a local validator, run 'solana-test-validator' in a separate terminal.", file=sys.stderr)
        print("Verify the SOLANA_CLUSTER_URL environment variable or .env file.", file=sys.stderr)
        sys.exit(1)
    except TransactionError as e:
        print(f"❌ Transaction Error: {e}", file=sys.stderr)
        print("The transaction failed. Please check your account balance and try again.", file=sys.stderr)
        sys.exit(1)
    except (ICOError, ResourceError, PDAError) as e:
        print(f"❌ Application Logic Error: {e}", file=sys.stderr)
        print("This might indicate a program state issue or invalid parameters.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Invalid Input Error: {e}", file=sys.stderr)
        print("Please check your command arguments and try again.", file=sys.stderr)
        sys.exit(1)
    except NotImplementedError as e:
        print(f"❌ Feature Not Fully Implemented: {e}", file=sys.stderr)
        print("This part of the client needs adjustment based on the on-chain program details.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ File Not Found Error: {e}", file=sys.stderr)
        print("Please check the file path and ensure the file exists.", file=sys.stderr)
        sys.exit(1)
    except typer.Exit as e:
        # Handle Typer's exit for --help etc.
        sys.exit(e.code)
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"\n❌ An unexpected error occurred: {type(e).__name__}: {e}", file=sys.stderr)
        # Consider adding traceback logging here for debugging
        # import traceback
        # traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_app()