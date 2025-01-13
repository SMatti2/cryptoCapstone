import os
import csv
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from pathlib import Path

from src.data_collection.gold import fetch_futures_prices_to_csv


def test_fetch_futures_prices_to_csv(tmp_path):
    """
    Test that fetch_futures_prices_to_csv:
      1) Calls yfinance.download with expected arguments,
      2) Creates a CSV in the specified output_dir,
      3) Returns a non-empty Series of Close prices.
    """

    # ---------------------------
    # 1) SETUP
    # ---------------------------
    ticker = "GC=F"
    start_date = "2022-01-01"
    end_date = "2022-01-10"

    # temporary directory for output
    output_dir = tmp_path / "data_raw"
    output_dir.mkdir()

    # mock df
    mock_dates = pd.date_range(start="2022-01-01", periods=3, freq="D")
    mock_data = {
        "Open": [1800, 1805, 1810],
        "High": [1810, 1815, 1820],
        "Low": [1790, 1795, 1800],
        "Close": [1795, 1801, 1807],
        "Volume": [1000, 1100, 1200],
    }
    mock_df = pd.DataFrame(data=mock_data, index=mock_dates)

    # patch yfinance.download to return the mock
    with patch("yfinance.download", return_value=mock_df) as mock_download:
        result_series = fetch_futures_prices_to_csv(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            output_dir=str(output_dir),
        )

    # yfinance.download called with correct args
    mock_download.assert_called_once_with(ticker, start=start_date, end=end_date)

    # CSV file was created corrcetly
    created_files = list(output_dir.glob("*.csv"))
    assert len(created_files) == 1, "Expected exactly one CSV file to be created."
    csv_file_path = created_files[0]
    file_name = os.path.basename(csv_file_path)

    # ticker_startdate_to_enddate.csv
    expected_substr = f"{ticker.lower()}_{start_date}_to_{end_date}"
    assert (
        expected_substr in file_name
    ), f"Expected file name to include '{expected_substr}', got '{file_name}'"

    # non-empty Series with length as our mock data
    assert isinstance(result_series, pd.Series), "Expected a pandas Series."
    assert len(result_series) == len(
        mock_df
    ), "Returned Series length must match the mock data."
    assert list(result_series) == list(mock_df["Close"]), "Close price data mismatch."

    # column named 'Close'
    csv_df = pd.read_csv(csv_file_path, index_col=0)
    assert list(csv_df.columns) == [
        "Close"
    ], "CSV should only contain the 'Close' column."
    assert len(csv_df) == len(mock_df), "CSV row count should match the mock data size."
    assert list(csv_df["Close"]) == list(mock_df["Close"]), "CSV close prices mismatch."

    print("Test passed: fetch_futures_prices_to_csv with at least one day of data.")
