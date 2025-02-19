import unittest
from datetime import datetime, timedelta, timezone
from sqlmodel import SQLModel

from src.models.reddit_db_analyzer import RedditAnalyzer
from src.models.schemas.post import Post
from src.models.schemas.comment import Comment

TEST_DATABASE_URL = "sqlite:///:memory:"


class TestRedditAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = RedditAnalyzer(TEST_DATABASE_URL)
        SQLModel.metadata.create_all(self.analyzer.engine)

        # Create sample data
        today = datetime.now(timezone.utc)
        yesterday = today - timedelta(days=1)

        post1 = Post(
            id="1",
            subreddit="subreddit1",
            title="Post 1",
            selftext="Content 1",
            author="author1",
            created_utc=int(today.timestamp()),
            num_comments=10,
            score=100,
            url="http://example.com/post1",
            archived=False,
            domain="example.com",
            permalink="/r/subreddit1/post1",
            is_video=False,
        )
        post2 = Post(
            id="2",
            subreddit="subreddit2",
            title="Post 2",
            selftext="Content 2",
            author="author2",
            created_utc=int(yesterday.timestamp()),
            num_comments=20,
            score=200,
            url="http://example.com/post2",
            archived=True,
            domain="example.com",
            permalink="/r/subreddit2/post2",
            is_video=True,
        )
        comment1 = Comment(
            id="1",
            subreddit="subreddit1",
            author="author1",
            body="Comment 1",
            created_utc=int(today.timestamp()),
            link_id="1",
            controversiality=0,
            ups=10,
            score=10,
            gilded=0,
            retrieved_on=int(today.timestamp()),
            distinguished=None,
            post_id="1",
        )
        comment2 = Comment(
            id="2",
            subreddit="subreddit2",
            author="author2",
            body="Comment 2",
            created_utc=int(yesterday.timestamp()),
            link_id="2",
            controversiality=1,
            ups=20,
            score=20,
            gilded=1,
            retrieved_on=int(today.timestamp()),
            distinguished="moderator",
            post_id="2",
        )

        self.analyzer.session.add_all([post1, post2, comment1, comment2])
        self.analyzer.session.commit()

    def tearDown(self):
        self.analyzer.close()

    def test_get_total_posts(self):
        total_posts = self.analyzer.get_total_posts()
        self.assertEqual(total_posts, 2)

    def test_get_total_comments(self):
        total_comments = self.analyzer.get_total_comments()
        self.assertEqual(total_comments, 2)

    def test_get_daily_posts_per_subreddit(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        result = self.analyzer.get_daily_posts_per_subreddit(yesterday, today)
        self.assertEqual(len(result), 2)
        self.assertIn(("subreddit1", 1), [(r[1], r[2]) for r in result])
        self.assertIn(("subreddit2", 1), [(r[1], r[2]) for r in result])

    def test_get_daily_comments_per_subreddit(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        result = self.analyzer.get_daily_comments_per_subreddit(yesterday, today)
        self.assertEqual(len(result), 2)
        self.assertIn(("subreddit1", 1), [(r[1], r[2]) for r in result])
        self.assertIn(("subreddit2", 1), [(r[1], r[2]) for r in result])

    def test_get_daily_unique_post_authors_per_subreddit(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        result = self.analyzer.get_daily_unique_post_authors_per_subreddit(
            yesterday, today
        )
        self.assertEqual(len(result), 2)
        self.assertIn(("subreddit1", 1), [(r[1], r[2]) for r in result])
        self.assertIn(("subreddit2", 1), [(r[1], r[2]) for r in result])

    def test_get_daily_avg_post_score(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        result = self.analyzer.get_daily_avg_post_score(yesterday, today)
        self.assertEqual(len(result), 2)
        self.assertIn(("subreddit1", 100.0), [(r[1], r[2]) for r in result])
        self.assertIn(("subreddit2", 200.0), [(r[1], r[2]) for r in result])

    def test_get_top_posts(self):
        result = self.analyzer.get_top_posts(limit=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].score, 200)  # Highest score post
        self.assertEqual(result[1].score, 100)  # Second highest score post

    def test_context_manager(self):
        with RedditAnalyzer(TEST_DATABASE_URL) as analyzer:
            SQLModel.metadata.create_all(analyzer.engine)
            post = Post(
                id="99",
                subreddit="some_sub",
                title="Another Post",
                author="someone",
                created_utc=int(datetime.now(timezone.utc).timestamp()),
                num_comments=0,
                score=0,
                url="http://example.com/another",
                archived=False,
                domain="example.com",
                permalink="/r/some_sub/another",
                is_video=False,
            )
            analyzer.session.add(post)
            analyzer.session.commit()
            self.assertEqual(analyzer.get_total_posts(), 1)


if __name__ == "__main__":
    unittest.main()
