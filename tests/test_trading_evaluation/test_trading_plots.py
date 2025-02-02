import unittest
import pandas as pd
import numpy as np
from src.trading_evaluation.trading_plots import plot_portfolio_comparison


def test_plot_portfolio_comparison():
    # create dummy data eth btc
    dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
    df_btc = pd.DataFrame({"close": np.random.rand(10)}, index=dates)
    df_eth = pd.DataFrame({"close": np.random.rand(10)}, index=dates)

    # create dummy portfolio
    df_portfolio_btc = pd.DataFrame(
        {"Portfolio Value": np.random.rand(10)}, index=dates
    )
    df_portfolio_eth = pd.DataFrame(
        {"Portfolio Value": np.random.rand(10)}, index=dates
    )

    try:
        plot_portfolio_comparison(df_portfolio_btc, df_portfolio_eth, df_btc, df_eth)
        print("Test passed: plot_portfolio_comparison executed successfully.")
    except Exception as e:
        raise AssertionError(
            f"Test failed: plot_portfolio_comparison raised an exception: {e}"
        )
