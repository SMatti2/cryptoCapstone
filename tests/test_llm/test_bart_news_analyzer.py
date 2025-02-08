import unittest
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

    def test_batch_predict(self):
        texts = ["This is a test text.", "Another test text."]
        probabilities = self.analyzer._batch_predict(texts)
        self.assertEqual(probabilities.shape, (len(texts), 2))

    def test_calculate_scores(self):
        bull_probs = np.array([0.8, 0.2])
        bear_probs = np.array([0.1, 0.7])
        scores = self.analyzer._calculate_scores(bull_probs, bear_probs)
        self.assertTrue(np.all(scores >= 0) and np.all(scores <= 10))

    def test_add_daily_aggregates(self):
        data = {
            "title": ["Title1", "Title2", "Title3"],
            "subtitle": ["Subtitle1", "Subtitle2", "Subtitle3"],
            "date": ["2023-03-15", "2023-03-15", "2023-03-16"],
            "score": [5, 7, 3],
        }
        df = pd.DataFrame(data)
        result = self.analyzer._add_daily_aggregates(df)
        self.assertTrue("average_score" in result.columns)
        self.assertTrue("article_count" in result.columns)
        self.assertTrue("relevant_articles" in result.columns)


if __name__ == "__main__":
    unittest.main()
