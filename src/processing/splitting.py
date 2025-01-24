import pandas as pd


def time_based_split(df, test_months=12, val_months=3, lags=30, date_col="date"):
    # ensure date is datetime
    df[date_col] = pd.to_datetime(df[date_col])
    end_date = df[date_col].max()

    test_start = end_date - pd.DateOffset(months=test_months)
    val_start = test_start - pd.DateOffset(months=val_months)

    # use buffer for sequence alignment
    buffer = pd.DateOffset(days=lags)
    train_end = val_start - buffer
    val_end = test_start - buffer

    # split
    train = df[df[date_col] <= train_end]
    val = df[(df[date_col] > train_end) & (df[date_col] <= val_end)]
    test = df[df[date_col] > val_end]

    return train, val, test
