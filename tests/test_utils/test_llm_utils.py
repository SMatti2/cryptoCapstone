import os, csv, tempfile, unittest
import pandas as pd
import numpy as np
from src.utils.llm_utils import (
    initialize_output_file,
    append_news_scores_to_csv,
    add_daily_aggregates,
)


class TestLLMUtils(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # delete temporary dirs and files
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_initialize_output_file(self):
        test_file = os.path.join(self.test_dir, "test_output.csv")
        headers = ["date", "title", "subtitle", "score"]

        initialize_output_file(test_file, headers)

        # check if file exists and contains correct headers
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, "r") as f:
            reader = csv.reader(f)
            file_headers = next(reader)
            self.assertEqual(headers, file_headers)

    def test_append_news_scores_to_csv(self):
        test_file = os.path.join(self.test_dir, "test_append.csv")
        headers = ["date", "title", "subtitle", "score"]
        initialize_output_file(test_file, headers)

        # mock df
        data = {
            "date": [pd.Timestamp("2023-05-01"), pd.Timestamp("2023-05-02")],
            "title": ["Test Title 1", "Test Title 2"],
            "subtitle": ["Test Subtitle 1", "Test Subtitle 2"],
            "score": [7.5, np.nan],
        }
        df = pd.DataFrame(data)

        append_news_scores_to_csv(test_file, df)

        with open(test_file, "r") as f:
            reader = csv.reader(f)
            next(reader)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(
                rows[0], ["2023-05-01", "Test Title 1", "Test Subtitle 1", "7.5"]
            )
            self.assertEqual(
                rows[1], ["2023-05-02", "Test Title 2", "Test Subtitle 2", "nan"]
            )

    def test_add_daily_aggregates(self):
        # mock df
        data = {
            "date": [
                pd.Timestamp("2023-05-01"),
                pd.Timestamp("2023-05-01"),
                pd.Timestamp("2023-05-02"),
            ],
            "score": [7.5, 8.5, 6.0],
        }
        df = pd.DataFrame(data)

        result = add_daily_aggregates(df)

        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["date"], pd.Timestamp("2023-05-01"))
        self.assertEqual(result.iloc[0]["average_score"], 8.0)
        self.assertEqual(result.iloc[0]["article_count"], 2)
        self.assertEqual(result.iloc[0]["relevant_articles"], 2)
        self.assertEqual(result.iloc[1]["date"], pd.Timestamp("2023-05-02"))
        self.assertEqual(result.iloc[1]["average_score"], 6.0)
        self.assertEqual(result.iloc[1]["article_count"], 1)
        self.assertEqual(result.iloc[1]["relevant_articles"], 1)


if __name__ == "__main__":
    unittest.main()
