import typer
import sys
from typing import Optional # For optional arguments if needed later
from typing_extensions import Annotated # For richer CLI options

# Use relative imports for modules within the 'src' directory
from . import tokenomics
from . import config
from .solana_client import SolanaClient
from .ico_manager import initialize_ico, buy_tokens, sell_tokens, withdraw_from_escrow
from .resource_manager import create_resource_access, access_resource
from .exceptions import (
    SolanaIcoError,
    ConfigurationError,
    KeypairError,
    SolanaConnectionError,
    TransactionError,
    ICOError,
    ResourceError,
    PDAError,
    # NotImplementedError, # Removed - Use built-in NotImplementedError
)

# --- Typer App Initialization ---
app = typer.Typer(help="ContextCoin (CTX) Solana CLI - Manage ICO and Resources")
ico_app = typer.Typer(help="ICO operations")
resource_app = typer.Typer(help="Resource access operations")
config_app = typer.Typer(help="Configuration commands")

app.add_typer(ico_app, name="ico")
app.add_typer(resource_app, name="resource")
app.add_typer(config_app, name="config")

# --- Helper Function for Common Logic ---
# (Could be expanded later if more common setup is needed)
def get_client_and_program_id() -> tuple[SolanaClient, str]:
    """Instantiates client and gets program ID, handling config errors."""
    client = SolanaClient() # Handles connection errors internally
    program_id = config.get_program_id() # Handles missing program ID error
    return client, program_id

# --- Top-Level Commands ---

@app.command("info")
def info_command():
    """Display ContextCoin token information."""
    print(f"Name: {tokenomics.NAME}")
    print(f"Symbol: {tokenomics.SYMBOL}")
    print(f"Total Supply: {tokenomics.TOTAL_SUPPLY}")
    print(f"Decimals: {tokenomics.DECIMAL_PLACES}")

@app.command("balance")
def balance_command(
    public_key: Annotated[str, typer.Argument(help="Public key of the account to check")]
):
    """Get the balance of a Solana account."""
    client, _ = get_client_and_program_id() # Client needed, program_id not
    balance_lamports = client.get_balance(public_key)
    balance_sol = balance_lamports / 1_000_000_000 # Convert lamports to SOL
    print(f"Balance for {public_key}: {balance_sol:.9f} SOL ({balance_lamports} Lamports)")

@app.command("send")
def send_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the sender's keypair file")],
    to_public_key: Annotated[str, typer.Argument(help="Recipient's public key")],
    amount: Annotated[int, typer.Argument(help="Amount to send (lamports)")]
):
    """Send SOL from one account to another."""
    client, _ = get_client_and_program_id()
    sender_keypair = client.load_keypair(keypair_path)
    signature = client.send_sol(sender_keypair, to_public_key, amount)
    print(f"Successfully sent {amount} lamports.")
    print(f"Transaction signature: {signature}")
    # Optional: Add confirmation wait here

# --- ICO Subcommands ---

@ico_app.command("init")
def init_ico_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the owner's keypair file")],
    token_mint: Annotated[str, typer.Argument(help="SPL token mint address")],
    total_supply: Annotated[int, typer.Argument(help="Total supply of the token")],
    base_price: Annotated[int, typer.Argument(help="Initial price (lamports)")],
    scaling_factor: Annotated[int, typer.Argument(help="Scaling factor")]
):
    """Initialize the ICO."""
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
    print(f"ICO initialized successfully.")
    print(f"Transaction signature: {signature}")

@ico_app.command("buy")
def buy_tokens_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the buyer's keypair file")],
    amount: Annotated[int, typer.Argument(help="Amount of SOL to spend (lamports)")],
    ico_owner_pubkey: Annotated[str, typer.Argument(help="Public key of the ICO owner")],
    # token_mint: Annotated[str, typer.Argument(help="SPL token mint address (required for ATA)")] # Temporarily removed, needs fix in ico_manager
):
    """Buy CTX tokens from the ICO."""
    client, program_id = get_client_and_program_id()
    buyer_keypair = client.load_keypair(keypair_path)
    # TODO: Fix token mint determination in ico_manager.buy_tokens
    # For now, it will raise NotImplementedError from ico_manager
    signature = buy_tokens(
        solana_client=client,
        program_id_str=program_id,
        buyer_keypair=buyer_keypair,
        amount_lamports=amount,
        ico_owner_pubkey_str=ico_owner_pubkey,
        # token_mint_str_arg=token_mint # Pass if needed by ico_manager
    )
    print(f"Successfully bought tokens with {amount} lamports.")
    print(f"Transaction signature: {signature}")

@ico_app.command("sell")
def sell_tokens_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the seller's keypair file")],
    amount: Annotated[int, typer.Argument(help="Amount of CTX tokens to sell")],
    ico_owner_pubkey: Annotated[str, typer.Argument(help="Public key of the ICO owner")],
    # token_mint: Annotated[str, typer.Argument(help="SPL token mint address (required for ATA)")] # Temporarily removed, needs fix in ico_manager
):
    """Sell CTX tokens back to the ICO."""
    client, program_id = get_client_and_program_id()
    seller_keypair = client.load_keypair(keypair_path)
    # TODO: Fix token mint determination in ico_manager.sell_tokens
    # For now, it will raise NotImplementedError from ico_manager
    signature = sell_tokens(
        solana_client=client,
        program_id_str=program_id,
        seller_keypair=seller_keypair,
        amount_tokens=amount,
        ico_owner_pubkey_str=ico_owner_pubkey,
        # token_mint_str_arg=token_mint # Pass if needed by ico_manager
    )
    print(f"Successfully sold {amount} tokens.")
    print(f"Transaction signature: {signature}")

@ico_app.command("withdraw")
def withdraw_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the owner's keypair file")],
    amount: Annotated[int, typer.Argument(help="Amount of SOL to withdraw (lamports)")]
):
    """Withdraw SOL from escrow (owner only)."""
    client, program_id = get_client_and_program_id()
    owner_keypair = client.load_keypair(keypair_path)
    signature = withdraw_from_escrow(
        solana_client=client,
        program_id_str=program_id,
        owner_keypair=owner_keypair,
        amount_lamports=amount
    )
    print(f"Successfully withdrew {amount} lamports from escrow.")
    print(f"Transaction signature: {signature}")

# --- Resource Subcommands ---

@resource_app.command("create")
def create_resource_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the server's keypair file")],
    resource_id: Annotated[str, typer.Argument(help="Unique resource identifier")],
    access_fee: Annotated[int, typer.Argument(help="Access fee (lamports)")]
):
    """Create or update resource access information."""
    client, program_id = get_client_and_program_id()
    server_keypair = client.load_keypair(keypair_path)
    signature = create_resource_access(
        solana_client=client,
        program_id_str=program_id,
        server_keypair=server_keypair,
        resource_id=resource_id,
        access_fee=access_fee
    )
    print(f"Resource access '{resource_id}' created/updated successfully.")
    print(f"Transaction signature: {signature}")

@resource_app.command("access")
def access_resource_command(
    keypair_path: Annotated[str, typer.Argument(help="Path to the user's keypair file")],
    resource_id: Annotated[str, typer.Argument(help="Unique resource identifier")],
    server_pubkey: Annotated[str, typer.Argument(help="Public key of the server managing the resource")],
    amount: Annotated[int, typer.Argument(help="Amount of SOL to spend (lamports)")]
):
    """Pay to access a registered resource."""
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
    print(f"Successfully paid {amount} lamports to access resource '{resource_id}'.")
    print(f"Transaction signature: {signature}")

# --- Config Subcommands ---

@config_app.command("verify")
def verify_config_command():
    """Verify the CLI's configuration and connection to the Solana cluster."""
    print("Verifying configuration and connection...")
    try:
        # Instantiating client tests connection, getting program ID tests config
        client, prog_id = get_client_and_program_id()
        print(f"Successfully connected to cluster: {client.cluster_url}")
        print(f"Program ID configured: {prog_id}")
        # Optional: Add a get_health or similar check if client supports it
        # health = client.client.get_health() # Access underlying client if needed
        # print(f"Cluster health: {health}")
        print("Verification successful.")
    except (ConfigurationError, SolanaConnectionError) as e:
        # Catch expected verification errors here specifically
        print(f"\n❌ Verification Failed: {e}", file=sys.stderr)
        sys.exit(1)
    # Let other unexpected errors propagate to the main handler

@config_app.command("show")
def show_config_command():
    """Show the current configuration values."""
    config.print_config()


# --- Main Execution & Error Handling ---

def run_app():
    """Runs the Typer app and handles errors gracefully."""
    try:
        app()
    # --- Specific Error Handling ---
    except ConfigurationError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        print("Please check your environment variables (SOLANA_CLUSTER_URL, SOLANA_PROGRAM_ID) or .env file.", file=sys.stderr)
        sys.exit(1)
    except KeypairError as e:
        print(f"\n❌ Keypair Error: {e}", file=sys.stderr)
        sys.exit(1)
    except SolanaConnectionError as e:
        print(f"\n❌ Connection Error: {e}", file=sys.stderr)
        # Cluster URL might not be available if config failed early
        try:
             print(f"Please ensure the Solana cluster at {config.get_cluster_url()} is running and accessible.", file=sys.stderr)
        except ConfigurationError:
             print("Please ensure the configured Solana cluster is running and accessible.", file=sys.stderr)
        sys.exit(1)
    except TransactionError as e:
        print(f"\n❌ Transaction Error: {e}", file=sys.stderr)
        # TODO: Potentially parse RPC error details if available in exception
        sys.exit(1)
    except (ICOError, ResourceError, PDAError) as e:
        print(f"\n❌ Application Logic Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        # Catch potential Pubkey.from_string errors or other value issues
        print(f"\n❌ Invalid Input Error: {e}", file=sys.stderr)
        sys.exit(1)
    except NotImplementedError as e:
         print(f"\n❌ Feature Not Fully Implemented: {e}", file=sys.stderr)
         print("This part of the client needs adjustment based on the on-chain program details.", file=sys.stderr)
         sys.exit(1)
    except FileNotFoundError as e:
         print(f"\n❌ File Not Found Error: {e}", file=sys.stderr)
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