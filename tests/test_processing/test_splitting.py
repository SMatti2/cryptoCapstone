import pandas as pd
from datetime import datetime

from src.processing.splitting import time_based_split


def test_time_based_split():
    dates = pd.date_range(start="2020-01-01", periods=1000, freq="D")
    data = {
        "date": dates,
        "feature1": range(1000),
        "feature2": range(1000, 2000),
        "logPriceChange": range(2000, 3000),
    }
    df = pd.DataFrame(data)

    test_months = 12
    val_months = 3
    lags = 30
    date_col = "date"

    train, val, test = time_based_split(
        df,
        test_months=test_months,
        val_months=val_months,
        lags=lags,
        date_col=date_col,
    )

    end_date = df[date_col].max()
    test_start = end_date - pd.DateOffset(months=test_months)
    val_start = test_start - pd.DateOffset(months=val_months)
    buffer = pd.DateOffset(days=lags)
    train_end = val_start - buffer
    val_end = test_start - buffer

    assert train[date_col].max() <= train_end, "Train set end date is incorrect"
    assert (
        val[date_col].min() > train_end and val[date_col].max() <= val_end
    ), "Validation set dates are incorrect"
    assert test[date_col].min() > val_end, "Test set start date is incorrect"

    # Check sizes
    expected_train_size = len(df[df[date_col] <= train_end])
    expected_val_size = len(df[(df[date_col] > train_end) & (df[date_col] <= val_end)])
    expected_test_size = len(df[df[date_col] > val_end])

    assert len(train) == expected_train_size, "Train set size is incorrect"
    assert len(val) == expected_val_size, "Validation set size is incorrect"
    assert len(test) == expected_test_size, "Test set size is incorrect"

    print("All tests passed!")
