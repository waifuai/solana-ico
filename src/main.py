import argparse
import os
from src import tokenomics
from src import bonding_curves
from src import solana_interactions
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.publickey import Pubkey

def main():
    parser = argparse.ArgumentParser(description="ContextCoin (CTX) Solana CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # --- Info Command ---
    info_parser = subparsers.add_parser("info", help="Display ContextCoin information.")

    # --- Balance Command ---
    balance_parser = subparsers.add_parser("balance", help="Get the balance of a Solana account.")
    balance_parser.add_argument("keypair_path", help="Path to the keypair file")

    # --- Send Command ---
    send_parser = subparsers.add_parser("send", help="Send SOL.")
    send_parser.add_argument("keypair_path", help="Path to the keypair file")
    send_parser.add_argument("to_public_key", help="Recipient's public key")
    send_parser.add_argument("amount", type=int, help="Amount to send (lamports)")

    # --- ICO Subcommands ---
    ico_parser = subparsers.add_parser("ico", help="ICO operations")
    ico_subparsers = ico_parser.add_subparsers(dest="ico_command", help="ICO subcommands")

    # --- Initialize ICO Command ---
    init_ico_parser = ico_subparsers.add_parser("init", help="Initialize the ICO.")
    init_ico_parser.add_argument("program_id", help="The program ID")
    init_ico_parser.add_argument("keypair_path", help="Path to the keypair file")
    init_ico_parser.add_argument("token_mint", help="SPL token mint address")
    init_ico_parser.add_argument("total_supply", type=int, help="Total supply of the token")
    init_ico_parser.add_argument("base_price", type=int, help="Initial price (lamports)")
    init_ico_parser.add_argument("scaling_factor", type=int, help="Scaling factor")

    # --- Buy Tokens Command ---
    buy_tokens_parser = ico_subparsers.add_parser("buy", help="Buy CTX tokens.")
    buy_tokens_parser.add_argument("program_id", help="The program ID")
    buy_tokens_parser.add_argument("keypair_path", help="Path to the buyer's keypair file")
    buy_tokens_parser.add_argument("amount", type=int, help="Amount of SOL to spend (lamports)")

    # --- Sell Tokens Command ---
    sell_tokens_parser = ico_subparsers.add_parser("sell", help="Sell CTX tokens.")
    sell_tokens_parser.add_argument("program_id", help="The program ID")
    sell_tokens_parser.add_argument("keypair_path", help="Path to the seller's keypair file")
    sell_tokens_parser.add_argument("amount", type=int, help="Amount of CTX tokens to sell")

    # --- Withdraw From Escrow Command ---
    withdraw_parser = ico_subparsers.add_parser("withdraw", help="Withdraw SOL from escrow (owner only).")
    withdraw_parser.add_argument("program_id", help="The program ID")
    withdraw_parser.add_argument("keypair_path", help="Path to the owner's keypair file")
    withdraw_parser.add_argument("amount", type=int, help="Amount of SOL to withdraw (lamports)")

    # --- Resource Subcommands ---
    resource_parser = subparsers.add_parser("resource", help="Resource access operations")
    resource_subparsers = resource_parser.add_subparsers(dest="resource_command", help="Resource subcommands")

    # --- Create Resource Access Command ---
    create_resource_parser = resource_subparsers.add_parser("create", help="Create resource access info.")
    create_resource_parser.add_argument("program_id", help="The program ID")
    create_resource_parser.add_argument("keypair_path", help="Path to the server's keypair file")
    create_resource_parser.add_argument("resource_id", help="Unique resource identifier")
    create_resource_parser.add_argument("access_fee", type=int, help="Access fee (lamports)")

    # --- Access Resource Command ---
    access_resource_parser = resource_subparsers.add_parser("access", help="Pay to access a resource.")
    access_resource_parser.add_argument("program_id", help="The program ID")
    access_resource_parser.add_argument("keypair_path", help="Path to the user's keypair file")
    access_resource_parser.add_argument("resource_id", help="Unique resource identifier")
    access_resource_parser.add_argument("amount", type=int, help="Amount of SOL to spend (lamports)")

    # --- Config Command ---
    config_parser = subparsers.add_parser("config", help="Configuration commands")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config subcommands")

    # --- Verify Config Command ---
    verify_config_parser = config_subparsers.add_parser("verify", help="Verify the CLI's configuration.")

    args = parser.parse_args()

    try:
        if args.command == "info":
            print(f"Name: {tokenomics.NAME}")
            print(f"Symbol: {tokenomics.SYMBOL}")
            print(f"Total Supply: {tokenomics.TOTAL_SUPPLY}")
        elif args.command == "balance":
            client = solana_interactions.connect_to_cluster()
            keypair = solana_interactions.load_keypair(args.keypair_path)
            balance = solana_interactions.get_balance(client, str(keypair.pubkey()))
            print(f"Balance: {balance} SOL")
        elif args.command == "send":
            client = solana_interactions.connect_to_cluster()
            keypair = solana_interactions.load_keypair(args.keypair_path)
            result = solana_interactions.send_sol(client, keypair, args.to_public_key, args.amount)
            print(f"Send result: {result}")
        elif args.command == "ico":
            if args.ico_command == "init":
                client = solana_interactions.connect_to_cluster()
                keypair = solana_interactions.load_keypair(args.keypair_path)
                result = solana_interactions.initialize_ico(
                    client,
                    args.program_id,
                    keypair,
                    args.token_mint,
                    args.total_supply,
                    args.base_price,
                    args.scaling_factor
                )
                print(f"Initialize ICO result: {result}")
            elif args.ico_command == "buy":
                client = solana_interactions.connect_to_cluster()
                keypair = solana_interactions.load_keypair(args.keypair_path)
                result = solana_interactions.buy_tokens(client, args.program_id, keypair, args.amount)
                print(f"Buy tokens result: {result}")
            elif args.ico_command == "sell":
                client = solana_interactions.connect_to_cluster()
                keypair = solana_interactions.load_keypair(args.keypair_path)
                result = solana_interactions.sell_tokens(client, args.program_id, keypair, args.amount)
                print(f"Sell tokens result: {result}")
            elif args.ico_command == "withdraw":
                client = solana_interactions.connect_to_cluster()
                keypair = solana_interactions.load_keypair(args.keypair_path)
                result = solana_interactions.withdraw_from_escrow(client, args.program_id, keypair, args.amount)
                print(f"Withdraw from escrow result: {result}")
            else:
                parser.print_help()
        elif args.command == "resource":
            if args.resource_command == "create":
                client = solana_interactions.connect_to_cluster()
                keypair = solana_interactions.load_keypair(args.keypair_path)
                result = solana_interactions.create_resource_access(client, args.program_id, keypair, args.resource_id, args.access_fee)
                print(f"Create resource result: {result}")
            elif args.resource_command == "access":
                client = solana_interactions.connect_to_cluster()
                keypair = solana_interactions.load_keypair(args.keypair_path)
                result = solana_interactions.access_resource(client, args.program_id, keypair, args.resource_id, args.amount)
                print(f"Access resource result: {result}")
            else:
                parser.print_help()
        elif args.command == "config":
            if args.config_command == "verify":
                client = solana_interactions.connect_to_cluster()
                try:
                    health = client.get_health()
                    print(f"Connection to Solana cluster successful. Health: {health}")
                except Exception as e:
                    print(f"Error connecting to Solana cluster: {e}")
            else:
                parser.print_help()
        else:
            parser.print_help()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()