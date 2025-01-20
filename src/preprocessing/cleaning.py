import pandas as pd
from typing import List, Optional


class CryptoDataCleaner:
    def __init__(
        self,
        date_col: str = "timeClose",
        drop_cols: Optional[List[str]] = None,
        round_decimals: int = 3,
        date_format: Optional[str] = None,
        rename_map: Optional[dict] = None,
    ):
        """
        Parameters
        ----------
        date_col : str
            The column containing datetime information from which we extract the date.
        drop_cols : List[str], optional
            Columns to drop from the DataFrame
        round_decimals : int
            Decimal places to round numeric columns
        date_format : str, optional
            If provided, can be used to ensure date parsing with a specific format
        rename_map : dict, optional
            A dictionary mapping old column names to new ones
        """
        if drop_cols is None:
            drop_cols = [
                "timeOpen",
                "timeClose",
                "timestamp",
                "timeHigh",
                "timeLow",
                "name",
            ]

        self.date_col = date_col
        self.drop_cols = drop_cols
        self.round_decimals = round_decimals
        self.date_format = date_format
        self.rename_map = rename_map or {}

    def convert_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts the date column to datetime and extracts the date
        into a new column called 'date'
        """
        if self.date_col not in df.columns:
            raise ValueError(f"Column '{self.date_col}' not found in DataFrame.")

        # if date_format is specified, try converting using that format
        if self.date_format and not pd.api.types.is_datetime64_any_dtype(
            df[self.date_col]
        ):
            df[self.date_col] = pd.to_datetime(
                df[self.date_col], format=self.date_format
            )

        if not pd.api.types.is_datetime64_any_dtype(df[self.date_col]):
            raise ValueError(
                f"Column '{self.date_col}' is not a datetime type after processing."
            )

        df["date"] = df[self.date_col].dt.date
        return df

    def drop_unwanted_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.drop(columns=self.drop_cols, errors="ignore", inplace=True)
        return df

    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.rename_map:
            df.rename(columns=self.rename_map, inplace=True)
        return df

    def set_date_index(self, df: pd.DataFrame) -> pd.DataFrame:
        if "date" not in df.columns:
            raise ValueError(
                "No 'date' column found. Ensure convert_date() was called first."
            )
        df.set_index("date", inplace=True)
        df.sort_index(ascending=True, inplace=True)
        return df

    def round_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.round(self.round_decimals)
        return df

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.convert_date(df)
        df = self.drop_unwanted_columns(df)
        df = self.rename_columns(df)
        df = self.set_date_index(df)
        df = self.round_values(df)
        return df
