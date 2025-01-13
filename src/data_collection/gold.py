import os
import yfinance as yf
import pandas as pd
from datetime import datetime


def fetch_futures_prices_to_csv(
    ticker: str,
    start_date: str,
    end_date: str,
    output_filename: str = None,
    output_dir: str = "data/data_raw",
):
    # output directory exists?
    os.makedirs(output_dir, exist_ok=True)

    # Convert string_dates to datetime
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    # create filename
    if output_filename is None:
        filename = (
            f"{ticker.lower()}_{start_date_obj.date()}_to_{end_date_obj.date()}.csv"
        )
    else:
        filename = output_filename

    # create filepath
    filepath = os.path.join(output_dir, filename)

    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    futures_data = yf.download(ticker, start=start_date, end=end_date)

    if futures_data.empty:
        print(f"No data fetched for {ticker} between {start_date} and {end_date}.")
        return pd.Series(dtype=float)

    close_prices = futures_data["Close"]
    close_prices.to_csv(filepath)
    print(f"Data saved to '{filepath}'")
    print(close_prices.head())

    return close_prices


if __name__ == "__main__":
    ticker = "GC=F"  # COMEX Gold Futures
    start = "2017-01-01"
    end = "2022-12-31"
    output_file = "comex_gold_futures_close_prices.csv"

    prices = fetch_futures_prices_to_csv(ticker, start, end, output_file)
