import os
import yfinance as yf
import pandas as pd

from pathlib import Path
from datetime import datetime


def fetch_yfinance_price_to_csv(
    ticker: str,
    start_date: str,
    end_date: str,
    output_filename: str = None,
    output_dir: Path = None,
    price_column: str = "Close",
):
    """
    fetch historical price data for a given ticker from Yahoo Finance and saves it to a CSV file
    """

    # create output directory
    if output_dir is None:
        output_dir = config.DATA_DIR / "raw" / "crypto_prices"
    else:
        output_dir = Path(output_dir)
    # ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # convert string dates to datetime objects
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    if output_filename is None:
        # Ensure the ticker is lowercased and special characters are handled
        ticker_cleaned = ticker.replace("^", "").lower()
        filename = (
            f"{ticker_cleaned}_{start_date_obj.date()}_to_{end_date_obj.date()}.csv"
        )
    else:
        filename = output_filename

    # full filepath
    filepath = output_dir / filename

    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        print(f"No data fetched for {ticker} between {start_date} and {end_date}.")
        return pd.Series(dtype=float)

    price_data = data[price_column]
    price_data.to_csv(filepath)
    print(f"Data saved to '{filepath}'")
    print(price_data.head())

    return price_data


if __name__ == "__main__":
    ticker = "^GSPC"
    start_date = "2017-01-01"
    end_date = "2022-12-31"
    output_filename = "apple_stock_prices.csv"

    fetch_yfinance_price_to_csv(ticker, start_date, end_date, output_filename)
