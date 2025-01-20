import os
import json
import unittest
from unittest.mock import patch, MagicMock

# Adjust these imports to match your actual project paths
from src.data_collection.reddit import (
    generate_new_id,
    create_post_instance,
    create_comment_instance,
    process_batch,
    read_zstd_reddit_data,
    read_posts,
    read_comments,
    process_zst_files_in_directory,
    inspect_zst_file_headers,
    Post,
    Comment,
    Session,
    Zreader,
    engine,
)


class TestRedditIngestion(unittest.TestCase):

    def test_generate_new_id(self):
        original = "abc123"
        new_id = generate_new_id(original)
        self.assertTrue(new_id.startswith("abc123_"))
        self.assertEqual(len(new_id), len("abc123_") + 8)

    @patch("src.data_collection.reddit.Session", autospec=True)
    def test_process_batch_no_conflict(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        items = [Post(id="post1"), Post(id="post2")]
        process_batch(mock_session, items, Post)

        self.assertEqual(mock_session.add.call_count, 2)
        self.assertTrue(mock_session.flush.called)
        mock_session.commit.assert_called_once()

    @patch("src.data_collection.reddit.Session", autospec=True)
    def test_process_batch_conflict(self, mock_session_cls):
        from sqlalchemy.exc import IntegrityError

        mock_session = mock_session_cls.return_value
        mock_session.flush.side_effect = [IntegrityError("duplicate", None, None), None]

        item = Post(id="postABC")
        process_batch(mock_session, [item], Post)

        self.assertEqual(mock_session.flush.call_count, 2)
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_called_once()
        self.assertTrue(item.id.startswith("postABC_"))
        self.assertEqual(len(item.id), len("postABC_") + 8)

    @patch("src.data_collection.reddit.Session", autospec=True)
    @patch("src.data_collection.reddit.Zreader", autospec=True)
    def test_read_zstd_reddit_data(self, mock_zreader_cls, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_zreader = mock_zreader_cls.return_value
        mock_zreader.readlines.return_value = [
            json.dumps({"id": "p1", "subreddit": "A", "title": "T1"}),
            json.dumps({"id": "p2", "subreddit": "B", "title": "T2"}),
            json.dumps({"subreddit": "NoID"}),  # malformed
            "Invalid JSON",
        ]

        with patch("src.data_collection.reddit.process_batch", autospec=True) as mb:
            read_zstd_reddit_data("fake.zst", lambda d: Post(**d), Post, batch_size=2)
            mb.assert_called_once()
            mock_zreader.close.assert_called_once()

    @patch(
        "os.listdir",
        return_value=["2021-submissions.zst", "2021-comments.zst", "random.txt"],
    )
    @patch("src.data_collection.reddit.read_posts", autospec=True)
    @patch("src.data_collection.reddit.read_comments", autospec=True)
    def test_process_zst_files_in_directory(
        self, mock_read_comments, mock_read_posts, mock_listdir
    ):
        data_folder = "fake_folder"
        process_zst_files_in_directory(data_folder)

        mock_read_posts.assert_called_once_with(
            os.path.join(data_folder, "2021-submissions.zst")
        )
        mock_read_comments.assert_called_once_with(
            os.path.join(data_folder, "2021-comments.zst")
        )


if __name__ == "__main__":
    unittest.main()
