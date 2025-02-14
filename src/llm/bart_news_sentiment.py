import pandas as pd

from src.models.bart_sentiment_analyzer import UniversalSentimentAnalyzer
from config import config


def analyze_news_articles(df: pd.DataFrame, crypto: str) -> pd.DataFrame:
    analyzer = UniversalSentimentAnalyzer(
        text_columns=["title", "subtitle"],
        hypotheses=[
            "This example is bullish for cryptocurrency prices.",
            "This example is bearish for cryptocurrency prices.",
        ],
        output_columns=["date", "title", "subtitle", "sentiment"],
        output_path=config.DATA_DIR / "temp" / f"news_sentiment_{crypto.lower()}.csv",
        device="cpu",
        batch_size=8,
        verbose=True,
    )

    return analyzer.analyze(df, "2017-01-01", "2022-12-31")
