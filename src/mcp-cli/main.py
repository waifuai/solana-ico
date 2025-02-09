import argparse
from mcp_cli import tokenomics
from mcp_cli import solana_utils
from solana.keypair import Keypair
from solana.rpc.api import Client

def main():
    parser = argparse.ArgumentParser(description="ContextCoin (CTX) Solana CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Info command
    info_parser = subparsers.add_parser("info", help="Display ContextCoin information, including name, symbol, total supply, and starting price.")

    # Balance command
    balance_parser = subparsers.add_parser("balance", help="Get the balance of a Solana account. Requires the path to the keypair file.")
    balance_parser.add_argument("--keypair", help="Path to the keypair file", required=True)

    # Send command
    send_parser = subparsers.add_parser("send", help="Send SOL from one account to another. Requires the path to the keypair file, the recipient's public key, and the amount to send.")
    send_parser.add_argument("--keypair", help="Path to the keypair file", required=True)
    send_parser.add_argument("--to", help="Recipient's public key", required=True)
    send_parser.add_argument("--amount", type=int, help="Amount to send", required=True)

    # Initialize ICO command
    init_ico_parser = subparsers.add_parser("initialize_ico", help="Initialize the ICO state. Requires the program ID, keypair file, token mint address, total supply, base price, and scaling factor.")
    init_ico_parser.add_argument("--program_id", help="The program ID", required=True)
    init_ico_parser.add_argument("--keypair", help="Path to the keypair file", required=True)
    init_ico_parser.add_argument("--token_mint", help="The address of the SPL token mint", required=True)
    init_ico_parser.add_argument("--total_supply", type=int, help="The total supply of the token", required=True)
    init_ico_parser.add_argument("--base_price", type=int, help="The initial price of the token in lamports", required=True)
    init_ico_parser.add_argument("--scaling_factor", type=int, help="The scaling factor used for the bonding curve", required=True)
    
    # Verify config command
    verify_config_parser = subparsers.add_parser("verify_config", help="Verify the CLI's configuration and connection to the Solana cluster.")

    args = parser.parse_args()

    if args.command == "info":
        print(f"Name: {tokenomics.NAME}")
        print(f"Symbol: {tokenomics.SYMBOL}")
        print(f"Total Supply: {tokenomics.TOTAL_SUPPLY}")
        print(f"Starting Price: {tokenomics.STARTING_PRICE} SOL per CTX")
    elif args.command == "balance":
        keypair = Keypair.from_seed(bytes([1]*32)) # Placeholder, replace with actual keypair loading
        balance = solana_utils.get_balance(str(keypair.pubkey()))
        print(f"Balance: {balance} SOL")
    elif args.command == "send":
        keypair = Keypair.from_seed(bytes([1]*32)) # Placeholder, replace with actual keypair loading
        result = solana_utils.send_sol(keypair, args.to, args.amount)
        print(f"Send result: {result}")
    elif args.command == "initialize_ico":
        result = solana_utils.initialize_ico(
            args.program_id,
            args.keypair,
            args.token_mint,
            args.total_supply,
            args.base_price,
            args.scaling_factor,
        )
        print(f"Initialize ICO result: {result}")
    elif args.command == "verify_config":
        try:
            solana_client = Client(solana_utils.SOLANA_CLUSTER_URL)
            health = solana_client.get_health()
            print(f"Connection to Solana cluster successful. Health: {health}")
        except Exception as e:
            print(f"Error: Could not connect to Solana cluster. Please check your configuration and network connection.\nDetails: {e}")
    else:
        print("Invalid command. Use 'info', 'balance', 'send', 'initialize_ico', or 'verify_config'.")

if __name__ == "__main__":
    main()