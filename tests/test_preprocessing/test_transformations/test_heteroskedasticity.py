import unittest
import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer
from src.preprocessing.transformations.heteroskedasticity import (
    check_heteroskedasticity,
    log_heteroskedastic_vars,
)


class TestHeteroskedasticityTransformations(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        time = np.arange(100)

        # Create clear heteroskedastic series
        self.df = pd.DataFrame(
            {
                # Variance increases with time (heteroskedastic)
                "to_transform": 0.1 * time + np.random.normal(0, 0.5 * (1 + time / 50)),
                # Stable variance (homoskedastic)
                "no_transform": np.random.normal(0, 1, 100),
                # Heteroskedastic series with negatives
                "mixed": np.random.normal(0, 0.5 * (1 + time / 50), 100),
                # Special columns
                "target": np.random.randint(0, 2, 100),
                "excluded": np.random.randn(100),
            }
        )

    def test_heteroskedasticity_detection(self):
        result = check_heteroskedasticity(self.df["to_transform"])
        self.assertTrue(result["needs_transform"])

        result = check_heteroskedasticity(self.df["no_transform"])
        self.assertFalse(result["needs_transform"])

    def test_transformations_applied_correctly(self):
        processed = log_heteroskedastic_vars(
            self.df, target="target", variables_to_exclude=["excluded"], alpha=0.05
        )

        # Verify log transform
        if (self.df["to_transform"] > 0).all():
            expected_log = np.log(self.df["to_transform"])
            np.testing.assert_allclose(
                processed["to_transform"], expected_log, rtol=1e-5
            )

        # Verify Yeo-Johnson transform
        pt = PowerTransformer(method="yeo-johnson")
        expected_yj = pt.fit_transform(self.df[["mixed"]]).ravel()
        np.testing.assert_allclose(processed["mixed"], expected_yj, atol=1e-5)

        # Verify special columns
        pd.testing.assert_series_equal(processed["target"], self.df["target"])
        pd.testing.assert_series_equal(processed["excluded"], self.df["excluded"])


if __name__ == "__main__":
    unittest.main()
