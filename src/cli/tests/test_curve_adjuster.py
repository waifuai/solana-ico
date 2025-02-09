import pytest
from cli import curve_adjuster

def test_adjust_curve_linear():
    current_params = {"slope": 0.1, "initial_price": 1}
    market_data = {"demand": 1.2}
    adjustment_algorithm = "simple_demand_adjustment"
    new_params = curve_adjuster.adjust_curve("linear", current_params, market_data, adjustment_algorithm)
    assert abs(new_params["slope"] - 0.12) < 0.0001 # 0.1 * 1.2
    assert new_params["initial_price"] == 1 # Should not be changed

    current_params = {"slope": 0.1, "initial_price": 1}
    market_data = {"demand": 0.8}
    adjustment_algorithm = "simple_demand_adjustment"
    new_params = curve_adjuster.adjust_curve("linear", current_params, market_data, adjustment_algorithm)
    assert abs(new_params["slope"] - 0.08) < 0.0001  # 0.1 * 0.8

def test_adjust_curve_unknown_type():
    current_params = {"slope": 0.1}
    market_data = {"demand": 1.2}
    adjustment_algorithm = ""
    # Expect current params if curve type not recognized
    assert curve_adjuster.adjust_curve("unknown", current_params, market_data, adjustment_algorithm) == current_params