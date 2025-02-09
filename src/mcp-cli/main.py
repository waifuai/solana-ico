import argparse
from mcp_cli import tokenomics
from mcp_cli import solana_utils
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
import os  # Import the 'os' module


def load_keypair(keypair_path: str) -> Keypair:
    """Loads a keypair from a file."""
    with open(keypair_path, 'r') as f:
        secret_key = list(map(int, f.readline().strip().split(',')))
    return Keypair.from_secret_key(secret_key)


def main():
    parser = argparse.ArgumentParser(description="ContextCoin (CTX) Solana CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # --- Info Command ---
    info_parser = subparsers.add_parser("info", help="Display ContextCoin information.")

    # --- Balance Command ---
    balance_parser = subparsers.add_parser("balance", help="Get the balance of a Solana account.")
    balance_parser.add_argument("--keypair", help="Path to the keypair file", required=True)

    # --- Send Command ---
    send_parser = subparsers.add_parser("send", help="Send SOL.")
    send_parser.add_argument("--keypair", help="Path to the keypair file", required=True)
    send_parser.add_argument("--to", help="Recipient's public key", required=True)
    send_parser.add_argument("--amount", type=int, help="Amount to send (lamports)", required=True)

    # --- Initialize ICO Command ---
    init_ico_parser = subparsers.add_parser("initialize_ico", help="Initialize the ICO.")
    init_ico_parser.add_argument("--program_id", help="The program ID", required=True)
    init_ico_parser.add_argument("--keypair", help="Path to the keypair file", required=True)
    init_ico_parser.add_argument("--token_mint", help="SPL token mint address", required=True)
    init_ico_parser.add_argument("--total_supply", type=int, help="Total supply of the token", required=True)
    init_ico_parser.add_argument("--base_price", type=int, help="Initial price (lamports)", required=True)
    init_ico_parser.add_argument("--scaling_factor", type=int, help="Scaling factor", required=True)

    # --- Buy Tokens Command ---
    buy_tokens_parser = subparsers.add_parser("buy_tokens", help="Buy CTX tokens.")
    buy_tokens_parser.add_argument("--program_id", help="The program ID", required=True)
    buy_tokens_parser.add_argument("--keypair", help="Path to the buyer's keypair file", required=True)
    buy_tokens_parser.add_argument("--amount", type=int, help="Amount of SOL to spend (lamports)", required=True)

    # --- Sell Tokens Command ---
    sell_tokens_parser = subparsers.add_parser("sell_tokens", help="Sell CTX tokens.")
    sell_tokens_parser.add_argument("--program_id", help="The program ID", required=True)
    sell_tokens_parser.add_argument("--keypair", help="Path to the seller's keypair file", required=True)
    sell_tokens_parser.add_argument("--amount", type=int, help="Amount of CTX tokens to sell", required=True)

    # --- Withdraw From Escrow Command ---
    withdraw_parser = subparsers.add_parser("withdraw_from_escrow", help="Withdraw SOL from escrow (owner only).")
    withdraw_parser.add_argument("--program_id", help="The program ID", required=True)
    withdraw_parser.add_argument("--keypair", help="Path to the owner's keypair file", required=True)
    withdraw_parser.add_argument("--amount", type=int, help="Amount of SOL to withdraw (lamports)", required=True)

    # --- Create Resource Access Command ---
    create_resource_parser = subparsers.add_parser("create_resource_access", help="Create resource access info.")
    create_resource_parser.add_argument("--program_id", help="The program ID", required=True)
    create_resource_parser.add_argument("--keypair", help="Path to the server's keypair file", required=True)
    create_resource_parser.add_argument("--resource_id", help="Unique resource identifier", required=True)
    create_resource_parser.add_argument("--access_fee", type=int, help="Access fee (lamports)", required=True)

    # --- Access Resource Command ---
    access_resource_parser = subparsers.add_parser("access_resource", help="Pay to access a resource.")
    access_resource_parser.add_argument("--program_id", help="The program ID", required=True)
    access_resource_parser.add_argument("--keypair", help="Path to the user's keypair file", required=True)
    access_resource_parser.add_argument("--resource_id", help="Unique resource identifier", required=True)
    access_resource_parser.add_argument("--amount", type=int, help="Amount of SOL to spend (lamports)", required=True)

    # --- Verify Config Command ---
    verify_config_parser = subparsers.add_parser("verify_config", help="Verify the CLI's configuration.")

    args = parser.parse_args()

    # Use environment variable for Solana cluster URL, with a default
    solana_client = Client(os.environ.get("SOLANA_CLUSTER_URL", solana_utils.SOLANA_CLUSTER_URL))

    try:
        if args.command == "info":
            print(f"Name: {tokenomics.NAME}")
            print(f"Symbol: {tokenomics.SYMBOL}")
            print(f"Total Supply: {tokenomics.TOTAL_SUPPLY}")
            print(f"Starting Price: {tokenomics.STARTING_PRICE} SOL per CTX")

        elif args.command == "balance":
            keypair = load_keypair(args.keypair)
            balance = solana_utils.get_balance(solana_client, str(keypair.pubkey()))
            print(f"Balance: {balance} SOL")

        elif args.command == "send":
            keypair = load_keypair(args.keypair)
            result = solana_utils.send_sol(solana_client, keypair, args.to, args.amount)
            print(f"Send result: {result}")

        elif args.command == "initialize_ico":
            keypair = load_keypair(args.keypair)
            result = solana_utils.initialize_ico(
                solana_client,
                args.program_id,
                keypair,
                args.token_mint,
                args.total_supply,
                args.base_price,
                args.scaling_factor
            )
            print(f"Initialize ICO result: {result}")

        elif args.command == "buy_tokens":
            keypair = load_keypair(args.keypair)
            result = solana_utils.buy_tokens(solana_client, args.program_id, keypair, args.amount)
            print(f"Buy tokens result: {result}")

        elif args.command == "sell_tokens":
            keypair = load_keypair(args.keypair)
            result = solana_utils.sell_tokens(solana_client, args.program_id, keypair, args.amount)
            print(f"Sell tokens result: {result}")

        elif args.command == "withdraw_from_escrow":
            keypair = load_keypair(args.keypair)
            result = solana_utils.withdraw_from_escrow(solana_client, args.program_id, keypair, args.amount)
            print(f"Withdraw from escrow result: {result}")
        
        elif args.command == "create_resource_access":
            keypair = load_keypair(args.keypair)
            result = solana_utils.create_resource_access(solana_client, args.program_id, keypair, args.resource_id, args.access_fee)
            print(f"Create resource result: {result}")
        
        elif args.command == "access_resource":
            keypair = load_keypair(args.keypair)
            result = solana_utils.access_resource(solana_client, args.program_id, keypair, args.resource_id, args.amount)
            print(f"Access resource result: {result}")

        elif args.command == "verify_config":
            health = solana_client.get_health()
            print(f"Connection to Solana cluster successful. Health: {health}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()