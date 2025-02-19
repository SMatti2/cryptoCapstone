import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.llm.langchain_news_analyzer import CryptoNewsSentimentAnalyzer


@pytest.fixture
def sample_df():
    data = {
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "title": ["Bitcoin high", "Crypto volatile", "New regulations"],
        "subtitle": ["Optimistic", "Cautious", "Concerned"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def analyzer():
    return CryptoNewsSentimentAnalyzer(verbose=False)


def test_classify_article(analyzer):
    with patch.object(analyzer, "chain") as mock_chain:
        mock_chain.invoke.return_value = "7"
        score = analyzer.classify_article("Test Title", "Test Subtitle")
        assert score == 7.0

        mock_chain.invoke.return_value = "0"
        score = analyzer.classify_article("Irrelevant", "Irrelevant")
        assert np.isnan(score)


def test_analyze_articles_in_range(analyzer, sample_df):
    with patch.object(analyzer, "classify_article", side_effect=[8.0, 5.0, 3.0]):
        result = analyzer.analyze_articles_in_range(
            sample_df, "2023-01-01", "2023-01-03"
        )

    assert len(result) == 3
    assert result.loc[0, "average_score"] == 8.0
    assert result.loc[1, "average_score"] == 5.0
    assert result.loc[2, "average_score"] == 3.0
