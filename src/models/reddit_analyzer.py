from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from sqlmodel import Session, create_engine, select, func

from src.models.schemas.post import Post
from src.models.schemas.comment import Comment


class RedditAnalyzer:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.session = Session(self.engine)

    def get_total_posts(self) -> int:
        return self.session.exec(select(func.count(Post.id))).one()

    def get_total_comments(self) -> int:
        return self.session.exec(select(func.count(Comment.id))).one()

    def get_daily_posts_per_subreddit(
        self, start_date: str, end_date: str, subreddit: str = None
    ) -> List[Tuple[str, str, int]]:
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) + 86399

        query = (
            select(
                func.strftime(
                    "%Y-%m-%d", func.datetime(Post.created_utc, "unixepoch")
                ).label("date"),
                Post.subreddit,
                func.count().label("count"),
            )
            .where(Post.created_utc.between(start_timestamp, end_timestamp))
            .group_by("date", Post.subreddit)
            .order_by("date", Post.subreddit)
        )

        if subreddit:
            query = query.where(func.lower(Post.subreddit) == subreddit.lower())

        return self.session.exec(query).all()

    def get_daily_comments_per_subreddit(
        self, start_date: str, end_date: str, subreddit: str = None
    ) -> List[Tuple[str, str, int]]:
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) + 86399

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

        if subreddit:
            query = query.where(func.lower(Comment.subreddit) == subreddit.lower())

        return self.session.exec(query).all()

    def get_daily_unique_post_authors_per_subreddit(
        self, start_date: str, end_date: str, subreddit: str = None
    ) -> List[Tuple[str, str, int]]:
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) + 86399

        query = (
            select(
                func.strftime(
                    "%Y-%m-%d", func.datetime(Post.created_utc, "unixepoch")
                ).label("date"),
                Post.subreddit,
                func.count(func.distinct(Post.author)).label("unique_authors"),
            )
            .where(
                Post.created_utc.between(start_timestamp, end_timestamp),
                Post.author.is_not(None),
            )
            .group_by("date", "subreddit")
            .order_by("date", "subreddit")
        )

        if subreddit:
            query = query.where(func.lower(Post.subreddit) == subreddit.lower())

        return self.session.exec(query).all()

    def get_daily_avg_post_score(
        self, start_date: str, end_date: str, subreddit: str = None
    ) -> List[Tuple[str, str, float]]:
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) + 86399

        query = (
            select(
                func.strftime(
                    "%Y-%m-%d", func.datetime(Post.created_utc, "unixepoch")
                ).label("date"),
                Post.subreddit,
                func.avg(Post.score).label("avg_score"),
            )
            .where(Post.created_utc.between(start_timestamp, end_timestamp))
            .group_by("date", Post.subreddit)
            .order_by("date", Post.subreddit)
        )

        if subreddit:
            query = query.where(func.lower(Post.subreddit) == subreddit.lower())

        return self.session.exec(query).all()

    def get_top_posts(
        self,
        limit: int = 5,
        start_date: str = None,
        end_date: str = None,
        subreddit: str = None,
    ) -> List[Post]:
        query = select(Post).where(Post.selftext != "").order_by(Post.score.desc())

        if start_date and end_date:
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_timestamp = (
                int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) + 86399
            )
            query = query.where(
                Post.created_utc.between(start_timestamp, end_timestamp)
            )
        elif start_date:
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            query = query.where(Post.created_utc >= start_timestamp)
        elif end_date:
            end_timestamp = (
                int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()) + 86399
            )
            query = query.where(Post.created_utc <= end_timestamp)

        if subreddit:
            query = query.where(func.lower(Post.subreddit) == subreddit.lower())

        query = query.limit(limit)

        return self.session.exec(query).all()

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
