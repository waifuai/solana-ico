import unittest
from bonding_curves import bonding_curves

class TestBondingCurves(unittest.TestCase):

    def test_linear_price(self):
        self.assertEqual(bonding_curves.linear_price(10, 2, 5), 25)

    def test_exponential_price(self):
        self.assertAlmostEqual(bonding_curves.exponential_price(5, 2, 0.1), 3.29744, places=5)

    def test_sigmoid_price(self):
        self.assertAlmostEqual(bonding_curves.sigmoid_price(5, 10, 1, 5), 5.0, places=5)

    def test_polynomial_price(self):
        coefficients = [1, 2, 3]
        self.assertEqual(bonding_curves.polynomial_price(2, coefficients), 17)

    def test_calculate_price(self):
        # This test relies on tokenomics.py, which might be considered an integration test
        # For a proper unit test, you'd mock tokenomics.STARTING_PRICE and tokenomics.SCALING_FACTOR
        from tokenomics import tokenomics
        expected_price = tokenomics.STARTING_PRICE * (1 + 10 / tokenomics.SCALING_FACTOR)
        self.assertEqual(bonding_curves.calculate_price(10), expected_price)

if __name__ == "__main__":
    unittest.main()