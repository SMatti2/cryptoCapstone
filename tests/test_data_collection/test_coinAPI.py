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
