import argparse
from cli import token_commands, token_management, token_operations, token_pricing, affiliate_commands, affiliate_management, bonding_curves

def main():
    parser = argparse.ArgumentParser(description="Solana CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    token_commands.add_token_commands(subparsers)
    token_management.add_token_management_commands(subparsers)
    token_operations.add_token_operations_commands(subparsers)
    token_pricing.add_token_pricing_commands(subparsers)
    affiliate_commands.add_affiliate_commands(subparsers)
    affiliate_management.add_affiliate_management_commands(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'command'):
        if args.command == "generate_animation":
            token_commands.handle_token_commands(args)
        elif args.command in ["optimize_portfolio", "find_trade_route", "adjust_curve"]:
            token_management.handle_token_management_commands(args)
        elif args.command in ["ico", "exchange_tokens", "create_token"]:
            token_operations.handle_token_operations_commands(args)
        elif args.command in ["calculate_commission"]:
            affiliate_commands.handle_affiliate_commands(args, bonding_curves)
        elif args.command in ["generate_referral_link", "record_referral", "update_commission_rate", "predict_rate"]:
            affiliate_management.handle_affiliate_management_commands(args)
        elif args.command in ["calculate_price", "calculate_buy_sell_price"]:
            token_pricing.handle_token_pricing_commands(args)

if __name__ == "__main__":
    main()