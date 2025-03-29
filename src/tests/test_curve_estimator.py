import unittest
import curve_estimator # Corrected import (assuming pytest runs from root with src in pythonpath)
import tokenomics # Corrected import

class TestCurveEstimator(unittest.TestCase): # Renamed class

    # def test_linear_price(self):
    #     # Function commented out in curve_estimator.py
    #     self.assertEqual(curve_estimator.linear_price(10, 2, 5), 25)
    #
    # def test_exponential_price(self):
    #     # Function commented out in curve_estimator.py
    #     self.assertAlmostEqual(curve_estimator.exponential_price(5, 2, 0.1), 3.29744, places=5)
    #
    # def test_sigmoid_price(self):
    #     # Function commented out in curve_estimator.py
    #     self.assertAlmostEqual(curve_estimator.sigmoid_price(5, 10, 1, 5), 5.0, places=5)
    #
    # def test_polynomial_price(self):
    #     # Function commented out in curve_estimator.py
    #     coefficients = [1, 2, 3]
    #     self.assertEqual(curve_estimator.polynomial_price(2, coefficients), 17)

    def test_calculate_price(self):
        """Tests the client-side price estimation function."""
        # This test relies on actual values from tokenomics.py.
        # For a pure unit test, mocking tokenomics constants would be better.
        tokens_sold = 1000 # Example value
        # Use float division consistent with the updated function
        expected_price = tokenomics.STARTING_PRICE * (1 + float(tokens_sold) / tokenomics.SCALING_FACTOR)
        self.assertAlmostEqual(curve_estimator.calculate_price(tokens_sold), expected_price, places=15) # Use assertAlmostEqual for float comparison

if __name__ == "__main__":
    unittest.main()