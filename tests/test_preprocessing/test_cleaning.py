import unittest
import pandas as pd
from datetime import datetime
from src.preprocessing.cleaning import CryptoDataCleaner


class TestCryptoDataCleaner(unittest.TestCase):
    def setUp(self):
        # df for testing
        self.df = pd.DataFrame(
            {
                "timeClose": ["2023-10-01 12:00", "2023-10-02 12:00"],
                "timeOpen": ["2023-10-01 11:00", "2023-10-02 11:00"],
                "timestamp": [1696161600, 1696248000],
                "timeHigh": [50000.123456, 51000.123456],
                "timeLow": [49000.123456, 50000.123456],
                "name": ["Bitcoin", "Ethereum"],
                "price": [50000.123456, 51000.123456],
            }
        )

    def test_convert_date(self):
        cleaner = CryptoDataCleaner(date_col="timeClose", date_format="%Y-%m-%d %H:%M")
        df = cleaner.convert_date(self.df)
        self.assertTrue("date" in df.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["timeClose"]))
        self.assertEqual(df["date"].iloc[0], datetime(2023, 10, 1).date())

    def test_drop_unwanted_columns(self):
        cleaner = CryptoDataCleaner(
            drop_cols=[
                "timeOpen",
                "timeClose",
                "timestamp",
                "timeHigh",
                "timeLow",
                "name",
            ]
        )
        df = cleaner.drop_unwanted_columns(self.df)
        self.assertNotIn("timeOpen", df.columns)
        self.assertNotIn("timeClose", df.columns)
        self.assertNotIn("timestamp", df.columns)
        self.assertNotIn("timeHigh", df.columns)
        self.assertNotIn("timeLow", df.columns)
        self.assertNotIn("name", df.columns)

    def test_rename_columns(self):
        cleaner = CryptoDataCleaner(rename_map={"price": "value"})
        df = cleaner.rename_columns(self.df)
        self.assertIn("value", df.columns)
        self.assertNotIn("price", df.columns)

    def test_set_date_index(self):
        cleaner = CryptoDataCleaner(date_col="timeClose", date_format="%Y-%m-%d %H:%M")
        df = cleaner.convert_date(self.df)
        df = cleaner.set_date_index(df)
        self.assertEqual(df.index.name, "date")
        self.assertTrue(df.index.is_monotonic_increasing)

    def test_round_values(self):
        cleaner = CryptoDataCleaner(round_decimals=3)
        df = cleaner.round_values(self.df)
        self.assertEqual(df["timeHigh"].iloc[0], 50000.123)
        self.assertEqual(df["timeLow"].iloc[0], 49000.123)
        self.assertEqual(df["price"].iloc[0], 50000.123)

    def test_clean(self):
        cleaner = CryptoDataCleaner(
            date_col="timeClose",
            drop_cols=[
                "timeOpen",
                "timeClose",
                "timestamp",
                "timeHigh",
                "timeLow",
                "name",
            ],
            round_decimals=3,
            date_format="%Y-%m-%d %H:%M",
            rename_map={"price": "value"},
        )
        df_cleaned = cleaner.clean(self.df)
        self.assertNotIn("timeOpen", df_cleaned.columns)
        self.assertIn("value", df_cleaned.columns)
        self.assertEqual(df_cleaned.index.name, "date")
        self.assertEqual(df_cleaned["value"].iloc[0], 50000.123)


if __name__ == "__main__":
    unittest.main()
