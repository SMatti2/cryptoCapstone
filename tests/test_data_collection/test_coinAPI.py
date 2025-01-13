import csv
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

from src.models.client import Client
from src.data_collection.coinAPI import fetch_ohlcv_data_to_csv


def test_fetch_ohlcv_data_to_csv(tmp_path):
    # mock client instance
    client = Client(
        base_url="https://fakeapi.io", auth_header="X-FAKE-KEY", api_key="dummy"
    )

    # create a temporary directory for CSV output
    output_dir = tmp_path / "crypto_prices"
    output_dir.mkdir()

    # mock CSV response:
    mock_csv_headers = (
        "time_period_start;time_period_end;price_close;volume_traded;trades_count"
    )
    mock_csv_row = "2023-01-01T00:00:00;2023-01-01T23:59:59;16700.1;10.0;5"
    mock_response_text = f"{mock_csv_headers}\n{mock_csv_row}"

    # Mock fetch response
    mock_fetch_response = MagicMock()
    mock_fetch_response.text = mock_response_text

    # patch mock response
    with patch.object(client, "fetch", return_value=mock_fetch_response):
        fetch_ohlcv_data_to_csv(
            client=client,
            symbol="BTC",
            exchange_id="COINBASE",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 2),
            output_dir=str(output_dir),
        )

    # function should create one file
    created_files = list(output_dir.glob("*.csv"))
    assert (
        len(created_files) == 1
    ), "Expected exactly one CSV file in the output directory."

    csv_file_path = created_files[0]
    # read the CSV content
    with open(csv_file_path, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # checl header
    assert len(rows) == 2, f"Expected 2 rows (header + 1 data), found {len(rows)}"
    assert rows[0] == [
        "date",
        "close",
        "volumeTraded",
        "tradesCount",
    ], "Unexpected CSV header row"

    # check data row
    assert rows[1] == [
        "2023-01-01T23:59:59",
        "16700.1",
        "10.0",
        "5",
    ], "Unexpected data row in CSV"

    # 4) (Optional) Additional assertions
    # Check file name, if needed
    file_name = os.path.basename(csv_file_path)
    assert (
        "btc_usd_2023-01-01_to_2023-01-02.csv" in file_name.lower()
    ), "Unexpected CSV file naming."

    print(
        "Test passed: fetch_ohlcv_data_to_csv successfully created and wrote data to CSV."
    )
