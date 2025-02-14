import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional

from src.models.bart_sentiment_analyzer import UniversalSentimentAnalyzer
from config import config


def analyze_reddit_posts(
    df: pd.DataFrame,
    subreddit: str,
    start_date: str = "2017-01-01",
    end_date: str = "2022-12-31",
    output_path: Optional[str] = None,
) -> pd.DataFrame:

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # fill missing values with empty string
    df["title"] = df["title"].fillna("")
    df["selftext"] = df.get("selftext", "").fillna("")
    df["subreddit"] = subreddit

    analyzer = UniversalSentimentAnalyzer(
        text_columns=["title", "selftext"],
        hypotheses=[
            f"This post expresses positive sentiment about {subreddit}.",
            f"This post expresses negative sentiment about {subreddit}.",
        ],
        date_column="date",
        device="cpu",
        threshold=0.25,
        batch_size=8,
        verbose=True,
        output_path=output_path,
        output_columns=["date", "title", "selftext", "score"],
    )

    # sentiment analysis
    result_df = analyzer.analyze(df, start_date=start_date, end_date=end_date)

    return result_df[out_columns]
