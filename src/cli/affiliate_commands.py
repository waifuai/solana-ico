import argparse

def add_affiliate_commands(subparsers):
    # Calculate Commission Subcommand
    commission_parser = subparsers.add_parser("calculate_commission", help="Calculate affiliate commission")
    commission_parser.add_argument("investment_amount", type=float, help="Investment amount")
    commission_parser.add_argument("--curve_type", choices=["linear", "exponential"], help="Type of bonding curve")
    commission_parser.add_argument("--supply", type=float, help="Token supply")
    commission_parser.add_argument("--slope", type=float, help="Slope for linear curve")
    commission_parser.add_argument("--initial_price", type=float, help="Initial price for linear curve")
    commission_parser.add_argument("--scaling_factor", type=float, help="Scaling factor for exponential curve")
    commission_parser.add_argument("--steepness", type=float, help="Steepness for exponential curve")
    commission_parser.add_argument("--commission_rate", type=float, help="Custom commission rate (optional)")

def handle_affiliate_commands(args, bonding_curves):
    if args.command == "calculate_commission":
        investment_amount = args.investment_amount
        if args.commission_rate is not None:
            commission_rate = args.commission_rate
        else:
            commission_rate = 0.10  # 10% commission

        if args.curve_type:
            if args.curve_type == "linear":
                if args.slope is None or args.initial_price is None:
                    print("Error: Slope and initial price are required for linear curve")
                else:
                    token_price = bonding_curves.linear_price(args.supply, args.slope, args.initial_price)
                    commission = (investment_amount / token_price) * commission_rate * token_price
                    print(f"Affiliate commission (linear curve, rate {commission_rate}): {commission}")
            elif args.curve_type == "exponential":
                if args.scaling_factor is None or args.steepness is None:
                    print("Error: Scaling factor and steepness are required for exponential curve")
                else:
                    token_price = bonding_curves.exponential_price(args.supply, args.scaling_factor, args.steepness)
                    commission = (investment_amount / token_price) * commission_rate * token_price
                    print(f"Affiliate commission (exponential curve, rate {commission_rate}): {commission}")
        else:
            commission = investment_amount * commission_rate
            print(f"Affiliate commission (rate {commission_rate}): {commission}")