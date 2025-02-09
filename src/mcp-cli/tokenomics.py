# Tokenomics of ContextCoin (CTX)

NAME = "ContextCoin"
SYMBOL = "CTX"
TOTAL_SUPPLY = 1_000_000_000  # 1 Billion
DECIMAL_PLACES = 9

# Initial Distribution
TEAM_DEVELOPMENT = 0.20  # 20%
ECOSYSTEM_FUND = 0.30  # 30%
INITIAL_SALE = 0.50  # 50%

# Bonding Curve ICO Details
STARTING_PRICE = 0.00001  # SOL per CTX
SCALING_FACTOR = 100_000_000

def calculate_price(tokens_sold):
    """Calculates the price of CTX after selling a certain number of tokens based on a linear bonding curve."""
    return STARTING_PRICE * (1 + tokens_sold / SCALING_FACTOR)