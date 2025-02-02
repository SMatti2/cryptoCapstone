import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def shift_and_convert_binary(df_pred):
    df_processed = df_pred.copy()
    df_processed["predictedPriceMovement"] = (
        df_processed["predictedLogPriceChange"] > 0
    ).astype(int)
    return df_processed.shift(-1).dropna()


def generate_trades(df_pred_processed, price_df):
    return [
        {
            "date": index,
            "close": price_df.loc[index, "close"],
            "action": "buy" if row["predictedPriceMovement"] == 1 else "sell",
        }
        for index, row in df_pred_processed.iterrows()
    ]


def initialize_portfolio(initial_capital, trade_size):
    return {
        "capital": initial_capital,
        "holdings": 0.0,
        "trade_size": trade_size,
        "fully_invested": False,
        "portfolio_values": [],
        "trades_executed": 0,
    }


def execute_buy(trade, portfolio, crypto_symbol="BTC", verbose=True):
    if portfolio["capital"] < portfolio["trade_size"]:
        if verbose:
            print(
                f"Cannot buy: Insufficient capital on {trade['date']} ({portfolio['capital']:.2f})"
            )
        return False

    amount_bought = portfolio["trade_size"] / trade["close"]
    portfolio["holdings"] += amount_bought
    portfolio["capital"] -= portfolio["trade_size"]
    portfolio["fully_invested"] = True
    portfolio["trades_executed"] += 1

    if verbose:
        print(
            f"[BUY] {amount_bought:.6f} {crypto_symbol} at {trade['close']:.2f} on {trade['date']}"
        )
    return True


def execute_sell(trade, portfolio, crypto_symbol="BTC", verbose=True):
    max_btc = portfolio["trade_size"] / trade["close"]
    btc_to_sell = min(max_btc, portfolio["holdings"])

    portfolio["capital"] += btc_to_sell * trade["close"]
    portfolio["holdings"] -= btc_to_sell
    portfolio["trades_executed"] += 1

    if portfolio["holdings"] < 1e-8:
        portfolio["fully_invested"] = False

    if verbose:
        print(
            f"[SELL] {btc_to_sell:.6f} {crypto_symbol} at {trade['close']:.2f} on {trade['date']}"
        )


def update_portfolio(portfolio, current_price):
    portfolio["portfolio_values"].append(
        portfolio["capital"] + portfolio["holdings"] * current_price
    )


def run_trading_simulation(
    df_pred,
    price_df,
    initial_capital=1.0,
    trade_amount=1.0,
    crypto_symbol="BTC",
    verbose=True,
):
    processed_signals = shift_and_convert_binary(df_pred)
    trades = generate_trades(processed_signals, price_df)
    portfolio = initialize_portfolio(initial_capital, trade_amount)

    for trade in trades:
        if trade["action"] == "buy":
            if not portfolio["fully_invested"]:
                success = execute_buy(trade, portfolio, crypto_symbol, verbose)
                if not success:
                    break
        else:
            execute_sell(trade, portfolio, crypto_symbol, verbose)

        update_portfolio(portfolio, trade["close"])

    final_price = price_df["close"].iloc[-1]
    portfolio["final_value"] = (
        portfolio["capital"] + portfolio["holdings"] * final_price
    )

    if verbose:
        summary = {
            "Initial Capital": f"{initial_capital:.2f}",
            "Final Value": f"{portfolio['final_value']:.2f}",
            "Return %": f"{(portfolio['final_value']/initial_capital - 1)*100:.1f}% \n",
            "Total Trades": portfolio["trades_executed"],
            "Remaining Capital": f"{portfolio['capital']:.2f}",
            f"{crypto_symbol} Holdings": f"{portfolio['holdings']:.6f}",
        }

        print("\n=== Portfolio Summary ===")
        for k, v in summary.items():
            print(f"{k:>18}: {v}")

        print("\n=== Performance Metrics ===")
        print(f"{'Best Value':>18}: {max(portfolio['portfolio_values']):.2f}")
        print(f"{'Worst Value':>18}: {min(portfolio['portfolio_values']):.2f}")
        print(f"{'Volatility (std)':>18}: {np.std(portfolio['portfolio_values']):.3f}")

    return portfolio
