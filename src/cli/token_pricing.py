import argparse
from cli import bonding_curves

def add_token_pricing_commands(subparsers):
    # Calculate Price Subcommand
    price_parser = subparsers.add_parser("calculate_price", help="Calculate token price based on bonding curve")
    price_parser.add_argument("curve_type", choices=["linear", "exponential", "sigmoid", "polynomial"], help="Type of bonding curve")
    price_parser.add_argument("supply", type=float, help="Token supply")
    price_parser.add_argument("--slope", type=float, help="Slope for linear curve")
    price_parser.add_argument("--initial_price", type=float, help="Initial price for linear curve")
    price_parser.add_argument("--scaling_factor", type=float, help="Scaling factor for exponential curve")
    price_parser.add_argument("--steepness", type=float, help="Steepness for exponential curve")
    price_parser.add_argument("--k", type=float, help="K parameter for sigmoid curve")
    price_parser.add_argument("--a", type=float, help="a parameter for sigmoid curve")
    price_parser.add_argument("--b", type=float, help="b parameter for sigmoid curve")
    price_parser.add_argument("--coefficients", nargs="+", type=float, help="Coefficients for polynomial curve (e.g., --coefficients 1 2 3 for x^2 + 2x + 3)")

    # Calculate Buy/Sell Price Subcommand
    buy_sell_parser = subparsers.add_parser("calculate_buy_sell_price", help="Calculate the cost to buy or revenue from selling tokens")
    buy_sell_parser.add_argument("supply", type=float, help="Current token supply")
    buy_sell_parser.add_argument("delta_s", type=float, help="Change in token supply (positive for buying, negative for selling)")
    buy_sell_parser.add_argument("slope", type=float, help="Slope of the linear bonding curve")
    buy_sell_parser.add_argument("y_intercept", type=float, help="Y-intercept of the linear bonding curve")

def handle_token_pricing_commands(args):
    if args.command == "calculate_price":
        if args.curve_type == "linear":
            if args.slope is None or args.initial_price is None:
                print("Error: Slope and initial price are required for linear curve")
            else:
                price = bonding_curves.linear_price(args.supply, args.slope, args.initial_price)
                print(f"Price for linear curve: {price}")
        elif args.curve_type == "exponential":
            if args.scaling_factor is None or args.steepness is None:
                print("Error: Scaling factor and steepness are required for exponential curve")
            else:
                price = bonding_curves.exponential_price(args.supply, args.scaling_factor, args.steepness)
                print(f"Price for exponential curve: {price}")
        elif args.curve_type == "sigmoid":
            if args.k is None or args.a is None or args.b is None:
                print("Error: k, a, and b are required for sigmoid curve")
            else:
                price = bonding_curves.sigmoid_price(args.supply, args.k, args.a, args.b)
                print(f"Price for sigmoid curve: {price}")
        elif args.curve_type == "polynomial":
            if args.coefficients is None:
                print("Error: coefficients are required for polynomial curve")
            else:
                price = bonding_curves.polynomial_price(args.supply, args.coefficients)
                print(f"Price for polynomial curve: {price}")
    elif args.command == "calculate_buy_sell_price":
        supply = args.supply
        delta_s = args.delta_s
        slope = args.slope
        y_intercept = args.y_intercept
        cost = slope * (delta_s**2) / 2 + (slope * supply + y_intercept) * delta_s
        if delta_s > 0:
            print(f"Cost to buy {delta_s} tokens: {cost}")
        else:
            print(f"Revenue from selling {abs(delta_s)} tokens: {cost}")