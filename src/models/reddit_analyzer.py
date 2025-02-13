from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select, func
from typing import List, Tuple

from src.models.schemas.post import Post
from src.models.schemas.comment import Comment

from config import config


class RedditAnalyzer:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.session = Session(self.engine)

    # GENERAL
    def get_total_posts(self) -> int:
        return self.session.exec(select(func.count(Post.id))).one()

    def get_total_comments(self) -> int:
        return self.session.exec(select(func.count(Comment.id))).one()

    def get_daily_posts_per_subreddit(
        self, start_date: str, end_date: str, subreddit: str = None
    ):
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = (
            datetime.strptime(end_date, "%Y-%m-%d")
            + timedelta(days=1)
            - timedelta(seconds=1)
        )

        query = (
            select(
                func.strftime(
                    "%Y-%m-%d", func.datetime(Post.created_utc, "unixepoch")
                ).label("date"),
                Post.subreddit,
                func.count().label("count"),
            )
            .where(
                Post.created_utc.between(
                    int(start_dt.timestamp()), int(end_dt.timestamp())
                )
            )
            .group_by("date", "subreddit")
            .order_by("date", "subreddit")
        )

        if subreddit:
            query = query.where(func.lower(Post.subreddit) == subreddit.lower())

        return self.session.exec(query).all()

    def get_daily_comments_per_subreddit(
        self, start_date: str, end_date: str, subreddit: str = None
    ) -> List[Tuple[str, str, int]]:
        # convert dates to timestamps
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

        query = (
            select(
                func.strftime(
                    "%Y-%m-%d", func.datetime(Comment.created_utc, "unixepoch")
                ).label("date"),
                Comment.subreddit,
                func.count().label("count"),
            )
            .where(
                Comment.created_utc.is_not(None),
                Comment.created_utc.between(start_timestamp, end_timestamp),
            )
            .group_by("date", "subreddit")
            .order_by("date", "subreddit")
        )

        # subreddit filter
        if subreddit:
            query = query.where(Comment.subreddit == subreddit)

        return self.session.exec(query).all()

    # utility methods
    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
