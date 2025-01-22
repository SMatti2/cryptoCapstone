import unittest
import numpy as np
import statsmodels.api as sm
from src.preprocessing.transformations.heteroskedasticity import (
    check_heteroskedasticity,
)


class TestHeteroskedasticity(unittest.TestCase):
    def test_heteroskedasticity_detection(self):
        # create data  with heteroskedasticity
        np.random.seed(42)
        n = 100
        time = np.arange(n)
        heteroskedastic_series = 0.5 * time + np.random.normal(0, 1, n) * (
            1 + 0.1 * time
        )

        # check for heteroskedasticity
        result = check_heteroskedasticity(heteroskedastic_series)
        # assert that heteroskedasticity is detected
        self.assertTrue(
            result["needs_transform"], "Heteroskedasticity should be detected"
        )

    def test_no_heteroskedasticity(self):
        # create data without heteroskedasticity
        np.random.seed(42)
        n = 100
        time = np.arange(n)
        homoskedastic_series = 0.5 * time + np.random.normal(0, 1, n)

        # check for heteroskedasticity
        result = check_heteroskedasticity(homoskedastic_series)
        # assert that heteroskedasticity is not detected
        self.assertFalse(
            result["needs_transform"], "Heteroskedasticity should not be detected"
        )


if __name__ == "__main__":
    unittest.main()
