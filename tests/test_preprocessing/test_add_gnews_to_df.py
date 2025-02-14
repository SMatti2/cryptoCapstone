import unittest, json
import pandas as pd
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.llm.loaders.gnews_loader import load_and_process_news_data


class TestLoadAndProcessNewsData(unittest.TestCase):
    def setUp(self):
        # create temp JSON file
        self.sample_data = {
            "2023-10-01": [
                {"title": "Title 1", "subtitle": "Subtitle 1"},
                {"title": "Title 2", "subtitle": "Subtitle 2"},
            ],
            "2023-10-02": [
                {"title": "Title 3", "subtitle": "Subtitle 3"},
            ],
        }
        self.temp_file = NamedTemporaryFile(delete=False, mode="w", suffix=".json")
        json.dump(self.sample_data, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        # delete temp file
        Path(self.temp_file.name).unlink()

    def test_load_and_process_news_data(self):
        df_news = load_and_process_news_data(self.temp_file.name)

        # check number of rows
        self.assertEqual(len(df_news), 3)

        # check if date is correctly parsed and set as index
        self.assertTrue(isinstance(df_news.index, pd.DatetimeIndex))

        # check complete_text column
        self.assertEqual(df_news.iloc[0]["complete_text"], "Title 1 Subtitle 1")
        self.assertEqual(df_news.iloc[1]["complete_text"], "Title 2 Subtitle 2")
        self.assertEqual(df_news.iloc[2]["complete_text"], "Title 3 Subtitle 3")

        # check word_count column is correctly calculated
        self.assertEqual(df_news.iloc[0]["word_count"], 4)
