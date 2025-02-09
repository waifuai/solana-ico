import pytest
import math
from cli import pathfinder

def test_find_trade_route_simple():
    tokens = ["A", "B", "C"]
    exchange_rates = {
        "A": {"B": 2},  # A -> B costs 2
        "B": {"C": 3},  # B -> C costs 3
    }
    route = pathfinder.find_trade_route(tokens, exchange_rates)
    assert route == ["A", "B", "C"]

def test_find_trade_route_no_direct_path():
    tokens = ["A", "B", "C"]
    exchange_rates = {
        "A": {"B": 2},
        "C": {"B": 0.5} # No B -> C, but can use C
    }
    route = pathfinder.find_trade_route(tokens, exchange_rates)
    assert route == ['A', 'B'] # Only partial route

def test_find_trade_route_no_path():
     tokens = ["A", "B", "C"]
     exchange_rates = {}
     route = pathfinder.find_trade_route(tokens, exchange_rates)
     assert route == ["A"]

def test_find_trade_route_circular():
    tokens = ["A", "B", "C"]
    exchange_rates = {
        "A":{"B": 2},
        "B":{"C":1},
        "C":{"A":0.5}
    }
    route = pathfinder.find_trade_route(tokens,exchange_rates)
    assert route == ['A', 'B', 'C']