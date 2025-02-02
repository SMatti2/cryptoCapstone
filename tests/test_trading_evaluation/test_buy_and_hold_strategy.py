import pandas as pd
import numpy as np

from src.trading_evaluation.buy_and_hold_strategy import buy_and_hold_simulation


def test_buy_and_hold_simulation():
    # mock dataset
    dates = pd.date_range(start="2023-01-01", periods=5, freq="D")
    close_prices = [100, 105, 110, 108, 112]

    df = pd.DataFrame({"close": close_prices}, index=dates)

    initial_capital = 1000.0
    bh_values = buy_and_hold_simulation(
        df, initial_capital=initial_capital, price_col="close"
    )

    first_price = df["close"].iloc[0]
    coins_held = initial_capital / first_price
    expected_values = [coins_held * price for price in close_prices]

    assert isinstance(bh_values, pd.Series), "Output should be a pandas Series"
    assert len(bh_values) == len(df), "Output length should match input length"
    assert np.allclose(
        bh_values, expected_values
    ), "Buy-and-hold values should match expected values"
    assert (
        bh_values.name == "Buy & Hold Value"
    ), "Series name should be 'Buy & Hold Value'"
