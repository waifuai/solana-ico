import math

def linear_price(supply, slope, initial_price):
    return slope * supply + initial_price

def exponential_price(supply, scaling_factor, steepness):
    return scaling_factor * math.exp(steepness * supply)