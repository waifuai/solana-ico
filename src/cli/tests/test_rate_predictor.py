import pytest
from cli import rate_predictor

def test_predict_rate():
    historical_data = {}
    market_data = {"volatility": 0.1}
    affiliate_preferences = {}
    rate = rate_predictor.predict_rate(historical_data, market_data, affiliate_preferences)
    # Since it's gradient descent, and simplified model, we'll just check
    # if its a reasonable rate and not an exact value
    assert 0 <= rate <= 1

def test_predict_rate_high_volatility():
    historical_data = {}
    market_data = {"volatility": 0.8} # High volatility
    affiliate_preferences = {}

    rate = rate_predictor.predict_rate(historical_data,market_data, affiliate_preferences)
    assert 0 <= rate <= 1

def test_predict_rate_no_volatility():
    historical_data = {}
    market_data = {} # No Volatility provided
    affiliate_preferences = {}

    rate = rate_predictor.predict_rate(historical_data,market_data, affiliate_preferences)
    assert 0 <= rate <= 1