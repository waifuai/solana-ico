import pytest
from cli import portfolio_optimizer

def test_optimize_portfolio():
    portfolio = ["WAIFU", "SOL", "USDC"]
    optimized = portfolio_optimizer.optimize_portfolio(portfolio)
    assert abs(optimized["WAIFU"] - 1/3) < 0.0001
    assert abs(optimized["SOL"] - 1/3) < 0.0001
    assert abs(optimized["USDC"] - 1/3) < 0.0001

    portfolio = ["WAIFU", "SOL"]
    optimized = portfolio_optimizer.optimize_portfolio(portfolio)
    assert abs(optimized["WAIFU"] - 0.5) < 0.0001
    assert abs(optimized["SOL"] - 0.5) < 0.0001