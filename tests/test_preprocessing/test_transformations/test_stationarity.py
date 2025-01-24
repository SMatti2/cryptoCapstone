import unittest
import pandas as pd
import numpy as np

from src.preprocessing.transformations.stationarity import (
    adf_test,
    pp_test,
    kpss_test,
    difference_non_stationary_features,
)


class TestStationarity(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.stationary_series = np.random.normal(0, 1, 100)
        self.non_stationary_series = np.cumsum(np.random.normal(0, 1, 100))

        self.test_df = pd.DataFrame(
            {
                "stationary": self.stationary_series,
                "non_stationary": self.non_stationary_series,
                "with_nans": self.non_stationary_series,
            }
        )
        self.test_df.loc[10:20, "with_nans"] = np.nan

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

    def test_difference_non_stationary_basic(self):
        """Test basic differencing functionality"""
        df_clean, diff_cols = difference_non_stationary_features(self.test_df)

        # Should difference 2 columns (non_stationary and with_nans)
        self.assertEqual(len(diff_cols), 2)
        self.assertIn("non_stationary", diff_cols)
        self.assertIn("with_nans", diff_cols)

        # Verify non-stationary column was differenced
        expected_diff = np.diff(self.non_stationary_series)
        np.testing.assert_allclose(
            df_clean["non_stationary"].values[1:], expected_diff[1:]
        )

    def test_no_differencing_needed(self):
        """Test when no columns need differencing"""
        df = pd.DataFrame(
            {"col1": self.stationary_series, "col2": self.stationary_series * 2}
        )
        df_clean, diff_cols = difference_non_stationary_features(df)
        self.assertEqual(len(diff_cols), 0)
        self.assertEqual(df_clean.shape[0], df.shape[0])


if __name__ == "__main__":
    unittest.main()
