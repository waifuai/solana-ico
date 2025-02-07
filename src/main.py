import argparse
import asyncio
from ico import setup_ico, run_example_transactions as ico_run_example_transactions
from affiliate import setup_affiliate_ico, run_example_transactions as affiliate_run_example_transactions

async def main():
    parser = argparse.ArgumentParser(description="Solana ICO CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ICO setup subcommand
    ico_parser = subparsers.add_parser("ico", help="Setup a standard ICO")
    ico_parser.add_argument("--cluster", default="devnet", help="Solana cluster to use (default: devnet)")

    # Affiliate ICO setup subcommand
    affiliate_parser = subparsers.add_parser("affiliate", help="Setup an ICO with affiliate program")
    affiliate_parser.add_argument("--cluster", default="devnet", help="Solana cluster to use (default: devnet)")

    args = parser.parse_args()

    if args.command == "ico":
        token_sale_proxy, owner_keypair, payer = await setup_ico(args.cluster)
        await ico_run_example_transactions(token_sale_proxy)
    elif args.command == "affiliate":
        token_sale_proxy, owner_keypair, payer = await setup_affiliate_ico(args.cluster)
        await affiliate_run_example_transactions(token_sale_proxy)
    else:
        print("Invalid command.")

if __name__ == "__main__":
    asyncio.run(main())