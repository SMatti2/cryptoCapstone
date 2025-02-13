import unittest
import os

from pathlib import Path
from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session

from src.processing.reddit_db_parser import get_daily_reddit_data
from src.models.schemas.post import Post
from src.models.schemas.comment import Comment

TEST_DB_FILE = Path(__file__).parent / "test_reddit.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_FILE}"


class TestGetDailyRedditDataIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(TEST_DB_URL, echo=False)
        SQLModel.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls):
        if TEST_DB_FILE.exists():
            TEST_DB_FILE.unlink()

    def setUp(self):
        self.session = Session(self.engine)
        self.session.query(Comment).delete()
        self.session.query(Post).delete()
        self.session.commit()

        # mock post and comments
        post1 = Post(
            id="p1",
            subreddit="bitcoin",
            title="Sample Post",
            author="satoshi",
            created_utc=int(datetime(2022, 1, 2, 10, 0).timestamp()),
            num_comments=2,
            score=50,
            url="http://example.com/p1",
            archived=False,
            domain="example.com",
            permalink="/r/bitcoin/p1",
            is_video=False,
        )
        comment1 = Comment(
            id="c1",
            subreddit="bitcoin",
            author="vitalik",
            body="Nice post!",
            created_utc=int(datetime(2022, 1, 3, 15, 30).timestamp()),
            post_id="p1",
            score=5,
        )
        self.session.add_all([post1, comment1])
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_get_daily_reddit_data(self):
        df = get_daily_reddit_data(
            start_date="2022-01-01",
            end_date="2022-01-04",
            subreddit="bitcoin",
            db_path=TEST_DB_URL,
        )

        self.assertEqual(len(df), 4)

        day1 = df.loc[df["date"] == "2022-01-01"].iloc[0]
        day2 = df.loc[df["date"] == "2022-01-02"].iloc[0]
        day3 = df.loc[df["date"] == "2022-01-03"].iloc[0]
        day4 = df.loc[df["date"] == "2022-01-04"].iloc[0]
        # day 1
        self.assertEqual(day1["postNumber"], 0)
        self.assertEqual(day1["commentNumber"], 0)
        self.assertEqual(day4["postNumber"], 0)
        self.assertEqual(day4["commentNumber"], 0)
        # day 2
        self.assertEqual(day2["postNumber"], 1)
        self.assertEqual(day2["commentNumber"], 0)

        # day3
        self.assertEqual(day3["postNumber"], 0)
        self.assertEqual(day3["commentNumber"], 1)


if __name__ == "__main__":
    unittest.main()
