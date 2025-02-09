import unittest, os, tempfile
import pandas as pd
import numpy as np

from src.llm.bart_news_analyzer import CryptoNewsAnalyzer


class TestCryptoNewsAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CryptoNewsAnalyzer(device="cpu", batch_size=4)

    def test_prepare_texts(self):
        titles = ["Title1", "Title2"]
        subtitles = ["Subtitle1", "Subtitle2"]
        expected_output = ["Title1. Subtitle1", "Title2. Subtitle2"]
        self.assertEqual(
            self.analyzer._prepare_texts(titles, subtitles), expected_output
        )

    def test_batch_classify(self):
        texts = ["This is a test text.", "Another test text."]
        probabilities = self.analyzer._batch_classify(texts)
        self.assertEqual(probabilities.shape, (len(texts), 2))

    def test_calculate_scores(self):
        bull_probs = np.array([0.8, 0.2])
        bear_probs = np.array([0.1, 0.7])
        scores = self.analyzer._calculate_scores(bull_probs, bear_probs)
        self.assertTrue(np.all(np.isnan(scores) | ((scores >= 1) & (scores <= 10))))

    def test_analyze_articles(self):
        data = {
            "title": ["Title1", "Title2", "Title3"],
            "subtitle": ["Subtitle1", "Subtitle2", "Subtitle3"],
            "date": ["2023-03-15", "2023-03-15", "2023-03-16"],
        }
        df = pd.DataFrame(data)
        start_date = "2023-03-15"
        end_date = "2023-03-16"
        result = self.analyzer.analyze_articles(df, start_date, end_date)
        self.assertTrue("average_score" in result.columns)
        self.assertTrue("article_count" in result.columns)
        self.assertTrue("relevant_articles" in result.columns)

    def test_analyze_articles_empty_result(self):
        data = {
            "title": ["Title1"],
            "subtitle": ["Subtitle1"],
            "date": ["2023-03-14"],
        }
        df = pd.DataFrame(data)
        start_date = "2023-03-15"
        end_date = "2023-03-16"
        result = self.analyzer.analyze_articles(df, start_date, end_date)
        self.assertTrue(result.empty)
        self.assertEqual(
            list(result.columns),
            ["date", "average_score", "article_count", "relevant_articles"],
        )


def test_analyze_articles_with_output_file(self):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
        temp_file_path = tmp.name

    try:
        analyzer_with_output = CryptoNewsAnalyzer(
            device="cpu", batch_size=4, output_file_path=temp_file_path
        )
        data = {
            "title": ["Title1", "Title2", "Title3"],
            "subtitle": ["Subtitle1", "Subtitle2", "Subtitle3"],
            "date": ["2023-03-15", "2023-03-15", "2023-03-16"],
        }
        df = pd.DataFrame(data)
        start_date = "2023-03-15"
        end_date = "2023-03-16"
        result = analyzer_with_output.analyze_articles(df, start_date, end_date)

        self.assertTrue(os.path.exists(temp_file_path))
        with open(temp_file_path, "r") as f:
            content = f.read().strip().split("\n")
            self.assertEqual(len(content), 3)
            for i, row in enumerate(content):
                parts = row.split(",")
                self.assertEqual(len(parts), 4)
                self.assertEqual(parts[0], data["date"][i])
                self.assertEqual(parts[1], data["title"][i])
                self.assertEqual(parts[2], data["subtitle"][i])
                # check if score is a number or 'nan'
                self.assertTrue(
                    parts[3].replace(".", "").isdigit() or parts[3] == "nan"
                )

        self.assertTrue("average_score" in result.columns)
        self.assertTrue("article_count" in result.columns)
        self.assertTrue("relevant_articles" in result.columns)

    finally:
        os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
