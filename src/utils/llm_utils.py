import os, csv
import pandas as pd
import numpy as np


def initialize_output_file(output_file_path, headers):
    if not os.path.exists(output_file_path):
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def append_news_scores_to_csv(output_file_path, partial_df):
    with open(output_file_path, "a", newline="") as f:
        writer = csv.writer(f)
        for _, row in partial_df.iterrows():
            writer.writerow(
                [
                    row["date"].strftime("%Y-%m-%d"),
                    row["title"],
                    row["subtitle"],
                    f"{row['score']:.1f}" if not pd.isna(row["score"]) else "nan",
                ]
            )


def limit_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) > max_words:
        words = words[:max_words]
    return " ".join(words)


def add_daily_aggregates(df: pd.DataFrame):
    """group by day and compute average_score, article_count, relevant_articles."""
    df["date"] = pd.to_datetime(df["date"])
    grouped = (
        df.groupby(pd.Grouper(key="date", freq="D"))
        .agg(
            average_score=("score", "mean"),
            article_count=("score", "size"),
            relevant_articles=("score", lambda x: np.count_nonzero(~np.isnan(x))),
        )
        .reset_index()
    )
    return grouped[["date", "average_score"]]


def replace_nans_and_zeros_with_rolling_mean(df, window=10):
    numeric_columns = df.select_dtypes(include=[np.number]).columns

    for column in numeric_columns:
        df[column] = df[column].replace(0, np.nan)

        rolling_mean = df[column].rolling(window=window, min_periods=1).mean()
        df[column] = df[column].fillna(rolling_mean)

        if pd.isna(df[column].iloc[0]):
            df.loc[df.index[0], column] = df[column].dropna().iloc[0]

    return df
