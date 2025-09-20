"""
Tokenomics configuration for ContextCoin (CTX).

This module defines the core economic parameters and distribution model
for the ContextCoin token, including supply, pricing, and bonding curve
parameters used by the ICO system.
"""

# Token Basic Information
NAME = "ContextCoin"
SYMBOL = "CTX"
TOTAL_SUPPLY = 1_000_000_000  # 1 Billion
DECIMAL_PLACES = 9

# Initial Distribution (percentages)
TEAM_DEVELOPMENT = 0.20  # 20%
ECOSYSTEM_FUND = 0.30  # 30%
INITIAL_SALE = 0.50  # 50%

# Bonding Curve ICO Details
STARTING_PRICE = 0.00001  # SOL per CTX (base price)
SCALING_FACTOR = 100_000_000  # Controls curve steepness