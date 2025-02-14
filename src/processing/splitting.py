import pandas as pd


def time_based_split(
    df,
    test_months=12,
    val_months=3,
    lags=30,
    targets=["logPriceChange"],
):
    # ensure the index is a datetime index
    df.index = pd.to_datetime(df.index)
    end_date = df.index.max()

    # date calculations
    test_start = end_date - pd.DateOffset(months=test_months)
    val_start = test_start - pd.DateOffset(months=val_months)
    buffer = pd.DateOffset(days=lags)

    # split boundaries
    train_end = val_start - buffer
    val_end = test_start - buffer

    # separate data
    train = df[df.index <= train_end].copy()
    val = df[(df.index > train_end) & (df.index <= val_end)].copy()
    test = df[df.index > val_end].copy()

    # shift the target variable by 1 day
    for target in targets:
        train[target] = train[target].shift(-1)
        val[target] = val[target].shift(-1)
        test[target] = test[target].shift(-1)

    # drop the nan row after shifting
    train = train.dropna()
    val = val.dropna()
    test = test.dropna()

    # feature/target separation
    features = [col for col in df.columns if col not in targets]

    return (
        train[features],
        train[targets],
        val[features],
        val[targets],
        test[features],
        test[targets],
    )
