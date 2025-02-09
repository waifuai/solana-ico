import pytest
import math
from cli import bonding_curves

def test_linear_price():
    assert bonding_curves.linear_price(10, 2, 5) == 25
    assert bonding_curves.linear_price(0, 2, 5) == 5
    assert bonding_curves.linear_price(10, 0, 5) == 5
    assert bonding_curves.linear_price(10, 2, 0) == 20

def test_exponential_price():
    assert bonding_curves.exponential_price(0, 2, 0.5) == 2
    assert abs(bonding_curves.exponential_price(2, 2, 0.5) - 5.4365636) < 0.0001  # Check with some tolerance
    assert bonding_curves.exponential_price(2,1,0) == 1

def test_sigmoid_price():
    assert abs(bonding_curves.sigmoid_price(0, 10, 1, 0) - 5) < 0.0001 # k / (1 + e^0) = k / 2
    assert abs(bonding_curves.sigmoid_price(1,10,1,1) - 5) < 0.0001

def test_polynomial_price():
   assert bonding_curves.polynomial_price(2, [1, 2, 3]) == 17  # 1 + 2*2 + 3*(2**2) = 1 + 4 + 12 = 17
   assert bonding_curves.polynomial_price(0, [1,2,3]) == 1
   assert bonding_curves.polynomial_price(2, [1]) == 1
   assert bonding_curves.polynomial_price(3,[0,0,0,5]) == 5 * 3**3