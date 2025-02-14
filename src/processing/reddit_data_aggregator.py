import pandas as pd
import csv

from datetime import datetime, timedelta, timezone

from src.models.reddit_db_analyzer import RedditAnalyzer
from config import config


def get_daily_reddit_data(
    start_date: str,
    end_date: str,
    subreddit: str = None,
    db_path: str = config.DATABASE_URL,
) -> pd.DataFrame:

    with RedditAnalyzer(db_path) as analyzer:
        daily_posts = analyzer.get_daily_posts_per_subreddit(
            start_date, end_date, subreddit
        )
        daily_comments = analyzer.get_daily_comments_per_subreddit(
            start_date, end_date, subreddit
        )
        daily_authors = analyzer.get_daily_unique_post_authors_per_subreddit(
            start_date, end_date, subreddit
        )
        daily_avg_score = analyzer.get_daily_avg_post_score(
            start_date, end_date, subreddit
        )

    # convert tuples to dfs
    posts_df = pd.DataFrame(daily_posts, columns=["date", "subreddit", "count"])
    comments_df = pd.DataFrame(daily_comments, columns=["date", "subreddit", "count"])
    authors_df = pd.DataFrame(daily_authors, columns=["date", "subreddit", "unique"])
    score_df = pd.DataFrame(daily_avg_score, columns=["date", "subreddit", "avg_score"])

    posts_grouped = (
        posts_df.assign(date=pd.to_datetime(posts_df["date"]))
        .groupby("date", as_index=False)["count"]
        .sum()
    )
    comments_grouped = (
        comments_df.assign(date=pd.to_datetime(comments_df["date"]))
        .groupby("date", as_index=False)["count"]
        .sum()
    )
    authors_grouped = (
        authors_df.assign(date=pd.to_datetime(authors_df["date"]))
        .groupby("date", as_index=False)["unique"]
        .sum()
    )
    score_grouped = (
        score_df.assign(date=pd.to_datetime(score_df["date"]))
        .groupby("date", as_index=False)["avg_score"]
        .mean()
    )

    # merge
    merged_df = pd.merge(
        posts_grouped,
        comments_grouped,
        on="date",
        how="outer",
        suffixes=("_posts", "_comments"),
    ).fillna(0)

    merged_df.rename(
        columns={"count_posts": "postNumber", "count_comments": "commentNumber"},
        inplace=True,
    )

    merged_df = pd.merge(merged_df, authors_grouped, on="date", how="outer").fillna(0)
    merged_df.rename(columns={"unique": "uniqueAuthors"}, inplace=True)

    merged_df = pd.merge(merged_df, score_grouped, on="date", how="outer").fillna(0)
    merged_df.rename(columns={"avg_score": "averagePostScore"}, inplace=True)

    # reindex and sort
    date_range = pd.date_range(start=start_date, end=end_date)
    merged_df = (
        merged_df.set_index("date")
        .reindex(date_range, fill_value=0)
        .rename_axis("date")
        .reset_index()
    ).sort_values("date")

    # print some stats
    zero_posts = (merged_df["postNumber"] == 0).sum()
    zero_comments = (merged_df["commentNumber"] == 0).sum()
    zero_authors = (merged_df["uniqueAuthors"] == 0).sum()
    zero_score = (merged_df["averagePostScore"] == 0).sum()

    print(f"Days with no posts: {zero_posts}")
    print(f"Days with no comments: {zero_comments}")
    print(f"Days with no unique authors: {zero_authors}")
    print(f"Days with no average score: {zero_score}")

    return merged_df


import pandas as pd
from datetime import datetime, timezone


def get_top_scored_posts(
    start_date: str,
    end_date: str,
    subreddit: str = None,
    db_path: str = config.DATABASE_URL,
    limit: int = 5,
) -> pd.DataFrame:

    with RedditAnalyzer(db_path) as analyzer:
        top_posts = analyzer.get_top_posts(
            limit=None,
            start_date=start_date,
            end_date=end_date,
            subreddit=subreddit,
        )

    # convert the list of Posts objects to a df
    posts_data = [
        {
            "date": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).strftime(
                "%Y-%m-%d"
            ),
            "title": post.title,
            "selftext": post.selftext,
            "score": post.score,
        }
        for post in top_posts
    ]

    df = pd.DataFrame(posts_data)
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])

    df.sort_values(by=["date", "score"], ascending=[True, False], inplace=True)
    # group and filter the top posts
    df = df.groupby("date").head(limit)

    df.sort_values(by=["date", "score"], ascending=[True, False], inplace=True)
    return df[["date", "title", "selftext", "score"]]
