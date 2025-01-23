import unittest
import numpy as np

from src.preprocessing.transformations.stationarity import adf_test, pp_test, kpss_test


class TestStationarity(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.stationary_series = np.random.normal(0, 1, 100)
        self.non_stationary_series = np.cumsum(np.random.normal(0, 1, 100))

    # ADF Tests
    def test_adf_stationary(self):
        result = adf_test(self.stationary_series, 0.05)
        self.assertTrue(result["Stationary"])

    def test_adf_non_stationary(self):
        result = adf_test(self.non_stationary_series, 0.05)
        self.assertFalse(result["Stationary"])

    # PP Tests
    def test_pp_stationary(self):
        result = pp_test(self.stationary_series, 0.05)
        self.assertTrue(result["Stationary"])

    def test_pp_non_stationary(self):
        result = pp_test(self.non_stationary_series, 0.05)
        self.assertFalse(result["Stationary"])

    # KPSS Tests
    def test_kpss_stationary(self):
        result = kpss_test(self.stationary_series, 0.05)
        self.assertTrue(result["Stationary"])

    def test_kpss_non_stationary(self):
        result = kpss_test(self.non_stationary_series, 0.05)
        self.assertFalse(result["Stationary"])


if __name__ == "__main__":
    unittest.main()
