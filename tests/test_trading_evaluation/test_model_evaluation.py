import unittest
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from src.trading_evaluation.model_evaluation import evaluate_and_plot


class TestEvaluateAndPlot(unittest.TestCase):
    def setUp(self):
        # sample data
        self.index = pd.date_range(start="2023-01-01", periods=11, freq="D")
        self.actual_values = np.random.rand(11)
        self.predicted_values = np.random.rand(10)  # One less than actual values
        self.actual_df = pd.DataFrame(
            {"logPriceChange": self.actual_values}, index=self.index
        )
        self.predicted_df = pd.DataFrame(
            {"predicted_log_price_change": self.predicted_values}, index=self.index[1:]
        )

    def test_mse_and_mae_calculation(self):
        # test if MSE and MAE are calculated correctly
        mse, mae = evaluate_and_plot(
            self.actual_df,
            self.predicted_df,
            "logPriceChange",
            "predicted_log_price_change",
            "Test",
        )
        expected_mse = mean_squared_error(
            self.actual_values[:-1], self.predicted_values
        )
        expected_mae = mean_absolute_error(
            self.actual_values[:-1], self.predicted_values
        )
        self.assertAlmostEqual(mse, expected_mse, places=4)
        self.assertAlmostEqual(mae, expected_mae, places=4)

    def test_empty_data(self):
        # test empty df
        empty_df = pd.DataFrame()
        with self.assertRaises(KeyError):
            evaluate_and_plot(
                empty_df,
                empty_df,
                "logPriceChange",
                "predicted_log_price_change",
                "Empty Test",
            )

    def test_mismatched_indices(self):
        # test handling of mismatched indices
        mismatched_index = pd.date_range(start="2023-01-05", periods=10, freq="D")
        mismatched_df = pd.DataFrame(
            {"predicted_log_price_change": np.random.rand(10)}, index=mismatched_index
        )
        # The function doesn't raise a ValueError for mismatched indices, it just ignores the mismatch
        mse, mae = evaluate_and_plot(
            self.actual_df,
            mismatched_df,
            "logPriceChange",
            "predicted_log_price_change",
            "Mismatched Test",
        )
        self.assertIsNotNone(mse)
        self.assertIsNotNone(mae)
