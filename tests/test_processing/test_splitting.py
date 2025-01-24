import pandas as pd
from src.processing.splitting import time_based_split


# helper functions to get min/max dates
def get_max_date(df, indices):
    return df.loc[indices].index.max()


def get_min_date(df, indices):
    return df.loc[indices].index.min()


# real tests
def test_time_based_split():
    # create date range and data
    dates = pd.date_range(start="2020-01-01", periods=1000, freq="D")
    data = {
        "feature1": range(1000),
        "feature2": range(1000, 2000),
        "logPriceChange": range(2000, 3000),
        "localMin_7": [0] * 1000,
    }

    # create dataframe with datetime index
    df = pd.DataFrame(data, index=dates)

    # split
    X_train, y_train, X_val, y_val, X_test, y_test = time_based_split(
        df,
        targets=["logPriceChange", "localMin_7"],
        test_months=12,
        val_months=3,
        lags=30,
    )

    # calculate split boundaries
    end_date = df.index.max()
    test_start = end_date - pd.DateOffset(months=12)
    val_start = test_start - pd.DateOffset(months=3)
    buffer = pd.DateOffset(days=30)
    train_end = val_start - buffer
    val_end = test_start - buffer

    # verify dates
    assert get_max_date(df, X_train.index) <= train_end, "train dates"
    assert (get_min_date(df, X_val.index) > train_end) and (
        get_max_date(df, X_val.index) <= val_end
    ), "val dates"
    assert get_min_date(df, X_test.index) > val_end, "test dates"

    # check feature/target isolation
    assert "logPriceChange" not in X_train.columns, "target leak"
    assert "localMin_7" not in X_train.columns, "target leak"
    assert {"logPriceChange", "localMin_7"} == set(y_train.columns), "target cols"

    # verify index alignment
    assert X_train.index.equals(y_train.index), "train index mismatch"
    assert X_val.index.equals(y_val.index), "val index mismatch"
    assert X_test.index.equals(y_test.index), "test index mismatch"
