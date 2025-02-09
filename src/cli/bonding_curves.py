import math

def linear_price(supply, slope, initial_price):
    return slope * supply + initial_price

def exponential_price(supply, scaling_factor, steepness):
    return scaling_factor * math.exp(steepness * supply)

def sigmoid_price(supply, k, a, b):
    return k / (1 + math.exp(-a * (supply - b)))

def polynomial_price(supply, coefficients):
    price = 0
    for i, coefficient in enumerate(coefficients):
        price += coefficient * (supply ** i)
    return price