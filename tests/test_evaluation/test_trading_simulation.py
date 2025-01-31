import pandas as pd
import numpy as np

from src.trading_evaluation.trading_simulation import run_trading_simulation


def test_run_trading_simulation():
    # Create a small dataset for testing
    dates = pd.date_range(start="2023-01-01", periods=5, freq="D")
    close_prices = [100, 105, 110, 108, 112]
    predicted_log_price_changes = [0.02, -0.01, 0.03, -0.02, 0.01]

    df = pd.DataFrame({"close": close_prices}, index=dates)
    df_pred = pd.DataFrame(
        {"predictedLogPriceChange": predicted_log_price_changes}, index=dates
    )

    # Run the trading simulation
    portfolio = run_trading_simulation(
        df_pred, df, initial_capital=1000.0, trade_amount=500.0
    )

    # Assertions to check the final portfolio state
    assert portfolio["capital"] >= 0, "Capital should not be negative"
    assert portfolio["holdings"] >= 0, "Holdings should not be negative"
    assert portfolio["trades_executed"] > 0, "At least one trade should be executed"
    assert (
        len(portfolio["portfolio_values"]) == len(df_pred) - 1
    ), "Portfolio value should be recorded for each trade"
