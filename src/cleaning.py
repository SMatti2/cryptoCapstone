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
