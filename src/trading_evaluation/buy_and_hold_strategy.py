import pandas as pd


def buy_and_hold_simulation(price_df, initial_capital=1.0, price_col="close"):

    df = price_df.copy()
    if df.empty:
        return pd.Series(name="Buy & Hold Value")

    first_date = df.index[0]
    first_price = df.loc[first_date, price_col]

    coins_held = initial_capital / first_price

    daily_values = []
    for date in df.index:
        daily_price = df.loc[date, price_col]
        daily_values.append(coins_held * daily_price)

    bh_series = pd.Series(daily_values, index=df.index, name="Buy & Hold Value")
    return bh_series
