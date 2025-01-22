from pydantic_settings import BaseSettings
from pathlib import Path

dtype_dict = {
    "open": float,
    "high": float,
    "low": float,
    "close": float,
    "volume": float,
    "marketCap": float,
}


class AppConfig(BaseSettings):
    COIN_API_KEY: str
    DATABASE_URL: str
    DATA_DIR: Path = Path(__file__).resolve().parent / "data"
    EXCLUDE_VARIABLES: list[str] = [
        "localMin_7",
        "localMax_7",
        "localMin_14",
        "localMax_14",
        "localMin_21",
        "localMax_21",
        "dayOfWeek_Sin",
        "dayOfWeek_Cos",
        "priceMovement",
        "PSAR_down",
        "PSAR_up",
        "AO",
        "PPO_Histogram",
        "PVO_Histogram",
        "ROC",
        "TRIX",
        "RSI_14",
        "Stoch_RSI_K",
        "Stoch_RSI_D",
        "Stoch_K",
        "Stoch_D",
        "MFI",
        "WilliamsR",
    ]

    class Config:
        # Loads the environment variables from a '.env' file
        env_file = ".env"
        env_file_encoding = "utf-8"


config = AppConfig()
# Example of using the configuration
if __name__ == "__main__":
    config = AppConfig()
    print(config.COIN_API_KEY)
    print(config.DATABASE_URL)
    print(config.DATA_DIR)
