import pandas as pd
import numpy as np
import pytest
from pandas.testing import assert_frame_equal

from src.preprocessing.create_variables import (
    calculate_mfi,
    create_log_price_change,
    create_local_extrema,
    create_day_of_week_sin_cos,
    calculate_technical_indicators,
    create_variables,
)


def test_calculate_mfi():
    high = np.array([10, 12, 11, 13, 14])
    low = np.array([8, 9, 10, 11, 12])
    close = np.array([9, 11, 10, 12, 13])
    volume = np.array([100, 200, 150, 300, 250])
    period = 3

    mfi = calculate_mfi(high, low, close, volume, period)

    # check if MFI values are within (0 to 100)
    assert np.all(mfi >= 0) and np.all(mfi <= 100)
    assert len(mfi) == len(close)


def test_create_log_price_change():
    data = {"close": [100, 105, 102, 108, 110]}
    df = pd.DataFrame(data)
    create_log_price_change(df)

    # check if logPriceChange is created
    assert "logPriceChange" in df.columns
    assert "priceMovement" in df.columns
    assert not df["logPriceChange"].isnull().any()
    assert not df["priceMovement"].isnull().any()


def test_create_local_extrema():
    data = {"close": [100, 105, 102, 108, 110, 107, 109, 111, 108, 112]}
    df = pd.DataFrame(data)
    periods = [2, 3]
    create_local_extrema(df, periods, "close")

    # check if localMin and localMax are created
    for period in periods:
        assert f"localMin_{period}" in df.columns
        assert f"localMax_{period}" in df.columns

    # check if local extrema indicators are created
    assert df["localMin_2"].sum() > 0
    assert df["localMax_2"].sum() > 0


def test_create_day_of_week_sin_cos():
    dates = pd.date_range(start="2023-10-01", periods=7, freq="D")
    data = {"close": [100, 105, 102, 108, 110, 107, 109]}
    df = pd.DataFrame(data, index=dates)
    df = create_day_of_week_sin_cos(df)

    # check if sine and cosine are created
    assert "dayOfWeek_Sin" in df.columns
    assert "dayOfWeek_Cos" in df.columns

    # check if the values are within (-1 to 1)
    assert np.all(df["dayOfWeek_Sin"].between(-1, 1))
    assert np.all(df["dayOfWeek_Cos"].between(-1, 1))


def test_create_variables():
    data = {
        "open": [100 + i for i in range(90)],
        "high": [101 + i for i in range(90)],
        "low": [99 + i for i in range(90)],
        "close": [100 + i for i in range(90)],
        "volume": [1000 * (i + 1) for i in range(90)],
    }
    df = pd.DataFrame(data)
    df.index = pd.date_range(start="2023-10-01", periods=len(df), freq="D")

    df_result = create_variables(df)

    # Check if the logPriceChange and priceMovement columns are created
    assert "logPriceChange" in df_result.columns
    assert "priceMovement" in df_result.columns

    # Check if localMin and localMax columns are created for each period
    periods = [7, 14, 21]
    for period in periods:
        assert f"localMin_{period}" in df_result.columns
        assert f"localMax_{period}" in df_result.columns

    # Check if the dayOfWeek_Sin and dayOfWeek_Cos columns are created
    assert "dayOfWeek_Sin" in df_result.columns
    assert "dayOfWeek_Cos" in df_result.columns

    # Check if some key technical indicators are added
    technical_indicators = ["EMA_12", "RSI_14", "BB_Middle", "OBV", "MFI"]
    for indicator in technical_indicators:
        assert indicator in df_result.columns


if __name__ == "__main__":
    pytest.main()
