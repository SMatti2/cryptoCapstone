import pandas as pd
import numpy as np


def run_trading_simulation(df_pred, df, initial_capital=1.0, amount_per_investment=1.0):
    trade_dicts = {}
    portfolio = {
        "capital": initial_capital,
        "fully_invested": False,
        "amount_per_investment": amount_per_investment,
        "holdings": 0.0,
        "portfolio_value": [],
        "trades_executed": 0,
    }

    # convert predicted log price change to binary signal (1 for positive, 0 for negative)
    df_pred["predictedPriceMovement"] = (df_pred["predictedLogPriceChange"] > 0).astype(
        int
    )

    # shift predictions to align with next day's action
    df_pred = df_pred.shift(-1).dropna()

    # buy or sell based on binary trading signal
    for index, row in df_pred.iterrows():
        trade_dicts[index] = {
            "date": index,
            "close": df.loc[index, "close"],
            "action": ("buy" if row["predictedPriceMovement"] == 1 else "sell"),
        }

    # simulate trade
    for index, trade in trade_dicts.items():
        close_price = trade["close"]
        action = trade["action"]

        if action == "buy" and not portfolio["fully_invested"]:
            if portfolio["capital"] >= portfolio["amount_per_investment"]:
                btc_purchased = portfolio["amount_per_investment"] / close_price
                portfolio["holdings"] += btc_purchased
                portfolio["capital"] -= portfolio["amount_per_investment"]
                portfolio["fully_invested"] = True
                portfolio["trades_executed"] += 1
                print(f"Bought {btc_purchased:.6f} BTC at {close_price:.2f} on {index}")
            else:
                print(
                    f"Cannot buy: insufficient capital on {index} (capital: {portfolio['capital']:.2f})"
                )
                return portfolio

        elif action == "sell":
            btc_to_sell = portfolio["amount_per_investment"] / close_price

            # check to not sell more than we have
            if btc_to_sell > portfolio["holdings"]:
                btc_to_sell = portfolio["holdings"]

            portfolio["capital"] += btc_to_sell * close_price
            portfolio["holdings"] -= btc_to_sell
            portfolio["trades_executed"] += 1

            # if holdings are zero, mark as not fully invested
            if portfolio["holdings"] == 0.0:
                portfolio["fully_invested"] = False

            print(f"Sold {btc_to_sell:.6f} BTC at {close_price:.2f} on {index}")

        # calculate portfolio value (cash+value of holdings)
        current_portfolio_value = portfolio["capital"] + (
            portfolio["holdings"] * close_price
        )
        portfolio["portfolio_value"].append(current_portfolio_value)

    # calculate final portfolio value
    final_portfolio_value = portfolio["capital"] + (
        portfolio["holdings"] * df["close"].iloc[-1]
    )

    print("\nFinal Portfolio Summary:")
    print(f"Capital: {portfolio['capital']:.2f}")
    print(f"Holdings: {portfolio['holdings']:.6f} BTC")
    print(f"Final Portfolio Value: {final_portfolio_value:.2f}")
    print(f"Total Trades Executed: {portfolio['trades_executed']}")

    return portfolio
