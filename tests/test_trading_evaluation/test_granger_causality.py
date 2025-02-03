import pandas as pd
import numpy as np
from src.trading_evaluation.granger_causality import granger_causality_tests


def test_output_is_dict():
    # mock dataset with 50 rows and three columns
    n = 50
    index = pd.date_range("2020-01-01", periods=n)
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "target": np.random.randn(n),
            "var1": np.random.randn(n),
            "var2": np.random.randn(n),
        },
        index=index,
    )

    # run tests
    results = granger_causality_tests(
        df, crypto_symbol="TEST", target="target", max_lag=1, alpha=0.05
    )

    # check the output is a dict
    assert isinstance(results, dict), "output should be a dictionary"


def test_insufficient_data_returns_empty():
    # create a dataset with too few rows
    n = 3
    index = pd.date_range("2020-01-01", periods=n)
    df = pd.DataFrame({"target": np.arange(n), "var1": np.arange(n)}, index=index)

    # run tests
    results = granger_causality_tests(
        df, crypto_symbol="TEST", target="target", max_lag=2, alpha=0.05
    )

    # check the output is an empty dict
    assert results == {}, "should return empty dict for insufficient data"
