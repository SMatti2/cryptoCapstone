import unittest
import pandas as pd
from src.processing.scaling import scale_features


class TestScaleFeatures(unittest.TestCase):
    def test_scale_features(self):
        # sample data
        X_train = pd.DataFrame({"feature1": [1, 2, 3], "feature2": [10, 20, 30]})
        X_val = pd.DataFrame({"feature1": [4, 5], "feature2": [40, 50]})
        X_test = pd.DataFrame({"feature1": [6], "feature2": [60]})

        X_train_scaled, X_val_scaled, X_test_scaled, scaler = scale_features(
            X_train, X_val, X_test
        )

        # check if output is df
        self.assertIsInstance(X_train_scaled, pd.DataFrame)
        self.assertIsInstance(X_val_scaled, pd.DataFrame)
        self.assertIsInstance(X_test_scaled, pd.DataFrame)

        # check if the scaler is returned
        self.assertIsNotNone(scaler)

        # check if the scaled data has the same shape as the input
        self.assertEqual(X_train_scaled.shape, X_train.shape)
        self.assertEqual(X_val_scaled.shape, X_val.shape)
        self.assertEqual(X_test_scaled.shape, X_test.shape)
