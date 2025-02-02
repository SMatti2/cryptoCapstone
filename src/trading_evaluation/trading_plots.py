import matplotlib.pyplot as plt
import pandas as pd

from src.trading_evaluation.buy_and_hold_strategy import buy_and_hold_simulation


def plot_portfolio_comparison(
    df_portfolio_btc,
    df_portfolio_eth,
    df_btc,
    df_eth,
    strategy_label_btc="BTC Strategy",
    strategy_label_eth="ETH Strategy",
):

    bh_btc = buy_and_hold_simulation(df_btc, initial_capital=1.0, price_col="close")
    bh_eth = buy_and_hold_simulation(df_eth, initial_capital=1.0, price_col="close")

    plt.figure(figsize=(12, 10))

    # btc subplot
    plt.subplot(2, 1, 1)
    plt.plot(
        df_portfolio_btc.index,
        df_portfolio_btc["Portfolio Value"],
        label=strategy_label_btc,
        color="blue",
    )
    plt.plot(
        bh_btc.index,
        bh_btc.values,
        label="BTC Buy & Hold",
        color="red",
        linestyle="--",
    )
    plt.title("BTC Strategy vs Buy & Hold")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)

    # eth subplot
    plt.subplot(2, 1, 2)
    plt.plot(
        df_portfolio_eth.index,
        df_portfolio_eth["Portfolio Value"],
        label=strategy_label_eth,
        color="green",
    )
    plt.plot(
        bh_eth.index,
        bh_eth.values,
        label="ETH Buy & Hold",
        color="orange",
        linestyle="--",
    )
    plt.title("ETH Strategy vs Buy & Hold")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
