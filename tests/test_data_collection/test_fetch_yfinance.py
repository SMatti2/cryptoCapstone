import os
import pytest
import pandas as pd

from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path

from src.data_collection.fetch_yfinance import fetch_yfinance_price_to_csv


def test_fetch_yfinance_price_to_csv(tmp_path):
    """
    test that fetch_yfinance_price_to_csv successfully fetches data,
    writes to a CSV, and the CSV contains the correct data
    """
    ticker = "^GSPC"
    start_date = "2022-01-01"
    end_date = "2022-01-10"
    output_dir = tmp_path / "data_raw"
    output_dir.mkdir()
    output_filename = "test_sp500.csv"

    # mock DataFrame to simulate yfinance.download return value
    mock_data = pd.DataFrame(
        {"Close": [3700, 3720, 3740], "Volume": [1000, 1100, 1200]},
        index=pd.date_range(start=start_date, periods=3, freq="D"),
    )

    with patch("yfinance.download", return_value=mock_data):
        result = fetch_yfinance_price_to_csv(
            ticker,
            start_date,
            end_date,
            output_filename=str(output_filename),
            output_dir=str(output_dir),
        )

        assert not result.empty, "The function should return non-empty Series."
        assert os.path.exists(
            output_dir / output_filename
        ), "The CSV file should exist."

        # read the CSV and validate contents
        written_data = pd.read_csv(
            output_dir / output_filename, index_col=0, parse_dates=True
        )

        # ensure the index is a DatetimeIndex with the correct frequency
        written_data.index = pd.to_datetime(written_data.index)
        written_data.index.freq = "D"
        # ensure the data types match
        written_data["Close"] = written_data["Close"].astype(mock_data["Close"].dtype)

        # compare the series
        pd.testing.assert_series_equal(
            written_data["Close"], mock_data["Close"], check_names=False
        )


def test_handle_empty_data(tmp_path):
    """
    fetch_yfinance_price_to_csv handles empty DataFrame correctly
    """
    with patch("yfinance.download", return_value=pd.DataFrame()):
        result = fetch_yfinance_price_to_csv(
            "^GSPC", "2022-01-01", "2022-01-10", output_dir=str(tmp_path)
        )
        assert result.empty, "Should return an empty Series for no data."
        assert not list(tmp_path.iterdir()), "No file should be created for empty data."


@pytest.mark.parametrize(
    "ticker, expected_part_of_filename",
    [
        ("^GSPC", "gspc"),
        ("AAPL", "aapl"),
    ],
)
def test_output_filename(tmp_path, ticker, expected_part_of_filename):
    """
    check the creation of filenames based on the ticker
    """
    start_date = "2022-01-01"
    end_date = "2022-01-10"
    output_dir = tmp_path / "data_raw"
    output_dir.mkdir()

    # mock df
    mock_data = pd.DataFrame(
        {"Close": [100, 101, 102]},
        index=pd.date_range(start=start_date, periods=3, freq="D"),
    )

    with patch("yfinance.download", return_value=mock_data):
        fetch_yfinance_price_to_csv(
            ticker, start_date, end_date, output_dir=str(output_dir)
        )

    # check if the file exists
    expected_filename = f"{expected_part_of_filename}_{start_date}_to_{end_date}.csv"
    file_path = output_dir / expected_filename

    try:
        assert file_path.exists(), f"Expected file {expected_filename} not found."
    finally:
        # delete the created file
        if file_path.exists():
            file_path.unlink()
