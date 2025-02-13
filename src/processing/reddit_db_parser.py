import pandas as pd
from datetime import datetime, timedelta

from src.models.reddit_analyzer import RedditAnalyzer
from config import config


def get_daily_reddit_data(
    start_date: str,
    end_date: str,
    subreddit: str = None,
    db_path: str = config.DATABASE_URL,
) -> pd.DataFrame:
    # convert dates to timestamps
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = (
        datetime.strptime(end_date, "%Y-%m-%d")
        + timedelta(days=1)
        - timedelta(seconds=1)
    )

    with RedditAnalyzer(db_path) as analyzer:
        daily_posts = analyzer.get_daily_posts_per_subreddit(
            start_date, end_date, subreddit
        )
        daily_comments = analyzer.get_daily_comments_per_subreddit(
            start_date, end_date, subreddit
        )

    # create dfs
    posts_df = pd.DataFrame(daily_posts, columns=["date", "subreddit", "count"])
    comments_df = pd.DataFrame(daily_comments, columns=["date", "subreddit", "count"])

    # convert date into datetime and group by date and sum counts
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

    # merge posts and comments on date and fill empty with 0
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

    all_dates = pd.date_range(start=start_date, end=end_date)
    merged_df = (
        merged_df.set_index("date")
        .reindex(all_dates, fill_value=0)
        .rename_axis("date")
        .reset_index()
    )

    # print 0 count days
    empty_posts = (merged_df["postNumber"] == 0).sum()
    empty_comments = (merged_df["commentNumber"] == 0).sum()
    print(f"Number of days with no posts: {empty_posts}")
    print(f"Number of days with no comments: {empty_comments}")

    return merged_df
