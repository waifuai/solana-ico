"""
Price estimation module for the Solana ICO CLI.

This module provides client-side price estimation functions for the ContextCoin
token based on the configured bonding curve parameters. It calculates estimated
token prices based on tokens sold, which can be used for informational purposes
before executing actual buy/sell transactions on the Solana blockchain.
"""

import math

# --- General Bonding Curve Formulas (Likely illustrative, not directly used by client) ---
# def linear_price(supply, slope, initial_price):
#     return slope * supply + initial_price
#
# def exponential_price(supply, scaling_factor, steepness):
#     return scaling_factor * math.exp(steepness * supply)
#
# def sigmoid_price(supply, k, a, b):
#     return k / (1 + math.exp(-a * (supply - b)))
#
# def polynomial_price(supply, coefficients):
#     price = 0
#     for i, coefficient in enumerate(coefficients):
#         price += coefficient * (supply ** i)
#     return price
# --- End General Formulas ---

def calculate_price(tokens_sold: int) -> float:
    """
    Estimates the CTX token price based on the number of tokens sold,
    using the configured linear bonding curve parameters.

    Note: This is a client-side estimation. The actual transaction price
    is determined by the on-chain program logic during buy/sell operations.
    """
    from . import tokenomics # Corrected import
    # Ensure floating point division
    return tokenomics.STARTING_PRICE * (1 + float(tokens_sold) / tokenomics.SCALING_FACTOR)