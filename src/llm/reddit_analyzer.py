from datetime import datetime
from sqlmodel import Session, create_engine, select, func

from src.models.post import Post
from src.models.comment import Comment


class RedditAnalyzer:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.session = Session(self.engine)

    # GENERAL
    def get_total_posts(self) -> int:
        return self.session.exec(select(func.count(Post.id))).one()

    def get_total_comments(self) -> int:
        return self.session.exec(select(func.count(Comment.id))).one()

    # utility methods
    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
