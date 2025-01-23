import unittest
import numpy as np

from src.preprocessing.transformations.stationarity import adf_test


class TestStationarityTest(unittest.TestCase):

    def test_stationary_series(self):
        # Create a stationary time series (e.g., white noise)
        np.random.seed(42)
        stationary_series = np.random.normal(0, 1, 100)

        # Perform ADF test with alpha = 0.05
        result = adf_test(stationary_series, alpha=0.05)

        # Check if the series is identified as stationary
        self.assertTrue(result["Stationary"])

    def test_non_stationary_series(self):
        # Create a non-stationary time series (e.g., random walk)
        np.random.seed(42)
        non_stationary_series = np.cumsum(np.random.normal(0, 1, 100))

        # Perform ADF test with alpha = 0.05
        result = adf_test(non_stationary_series, alpha=0.05)

        # Check if the series is identified as non-stationary
        self.assertFalse(result["Stationary"])
