import unittest
import pandas as pd
from datetime import datetime
from src.cleaning import CryptoDataCleaner


class TestCryptoDataCleaner(unittest.TestCase):
    def setup(self):
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


if __name__ == "__main__":
    unittest.main()
