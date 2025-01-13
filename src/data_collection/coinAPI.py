import os
import requests
import csv
from datetime import datetime, timedelta
from config import config
from src.models.client import Client


def fetch_ohlcv_data_to_csv(
    client: Client,
    symbol: str = "BTC",
    exchange_id: str = "COINBASE",
    start_date: datetime = None,
    end_date: datetime = None,
    output_dir: str = "data/data_raw/crypto_prices",
):
    # format symbol for coinAPI
    full_symbol = f"{symbol.upper()}_USD"

    # create output directory
    os.makedirs(output_dir, exist_ok=True)
    #  create filename
    filename = f"{full_symbol.lower()}_{start_date.date()}_to_{end_date.date()}.csv"
    filepath = os.path.join(output_dir, filename)

    # create csv file
    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["date", "close", "volumeTraded", "tradesCount"])

    # format for CoinAPI
    symbol_id = f"{exchange_id}_SPOT_{full_symbol.upper()}"

    current_date = start_date
    while current_date < end_date:
        start_iso = current_date.isoformat() + "Z"
        day_end = current_date + timedelta(days=1)
        end_iso = day_end.isoformat() + "Z"

        params = {
            "period_id": "1DAY",
            "time_start": start_iso,
            "time_end": end_iso,
            "include_empty_items": "false",
            "output_format": "csv",
        }

        response = client.fetch(f"/ohlcv/{symbol_id}/history", params)
        data_lines = response.text.strip().split("\n")

        if len(data_lines) <= 1:
            current_date = day_end
            continue

        reader = csv.reader(data_lines, delimiter=";")
        csv_headers = next(reader, None)  # skip header line
        col_index = {col: i for i, col in enumerate(csv_headers)}

        with open(filepath, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for row in reader:
                writer.writerow(
                    [
                        row[col_index[col]]
                        for col in [
                            "time_period_end",
                            "price_close",
                            "volume_traded",
                            "trades_count",
                        ]
                    ]
                )

        current_date = day_end

        print(f"✓ {current_date.date()} data saved to: {os.path.basename(filepath)}")


if __name__ == "__main__":
    fetch_ohlcv_data_to_csv(
        client=Client(
            base_url="https://rest.coinapi.io/v1",
            auth_header="X-CoinAPI-Key",
            api_key=config.COIN_API_KEY,
        ),
        symbol="ETH",
        start_date=datetime(2016, 9, 1),
        end_date=datetime(2016, 9, 3),
    )
