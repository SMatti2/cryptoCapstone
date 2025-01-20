# tests/test_models/test_post.py
import pytest
from src.models.post import Post
from src.models.comment import Comment


def test_post_initialization():
    post = Post(
        id="123",
        subreddit="python",
        title="Test Post",
        selftext="This is a test post",
        author="test_user",
        created_utc=1638316800,
        num_comments=10,
        score=100,
        url="https://example.com",
        archived=False,
        domain="example.com",
        permalink="/r/python/comments/12345/test_post/",
        is_video=False,
    )

    assert post.id == "123"
    assert post.subreddit == "python"
    assert post.title == "Test Post"
    assert post.selftext == "This is a test post"
    assert post.author == "test_user"
    assert post.created_utc == 1638316800
    assert post.num_comments == 10
    assert post.score == 100
    assert post.url == "https://example.com"
    assert post.archived is False
    assert post.domain == "example.com"
    assert post.permalink == "/r/python/comments/12345/test_post/"
    assert post.is_video is False
    assert post.comments == []  # Relationship should be empty initially


def test_post_partial_initialization():
    post = Post(
        id="456",
        subreddit="python",
        title="Partial Test Post",
        author="test_user",
        created_utc=1638316800,
        num_comments=5,
        score=50,
        url="https://example.com",
        permalink="/r/python/comments/67890/partial_test_post/",
    )

    assert post.id == "456"
    assert post.subreddit == "python"
    assert post.title == "Partial Test Post"
    assert post.author == "test_user"
    assert post.created_utc == 1638316800
    assert post.num_comments == 5
    assert post.score == 50
    assert post.url == "https://example.com"
    assert post.permalink == "/r/python/comments/67890/partial_test_post/"
    assert post.selftext is None
    assert post.archived is False
    assert post.domain is None
    assert post.is_video is False
    assert post.comments == []  # Relationship should be empty initially


def test_post_field_types():
    post = Post(
        id="789",
        subreddit="python",
        title="Test Post",
        selftext="This is a test post",
        author="test_user",
        created_utc=1638316800,
        num_comments=10,
        score=100,
        url="https://example.com",
        archived=False,
        domain="example.com",
        permalink="/r/python/comments/12345/test_post/",
        is_video=False,
    )

    assert isinstance(post.id, str)
    assert isinstance(post.subreddit, str)
    assert isinstance(post.title, str)
    assert isinstance(post.selftext, str)
    assert isinstance(post.author, str)
    assert isinstance(post.created_utc, int)
    assert isinstance(post.num_comments, int)
    assert isinstance(post.score, int)
    assert isinstance(post.url, str)
    assert isinstance(post.archived, bool)
    assert isinstance(post.domain, str)
    assert isinstance(post.permalink, str)
    assert isinstance(post.is_video, bool)
    assert isinstance(post.comments, list)  # Relationship should be a list


def test_post_relationship():
    post = Post(
        id="123",
        subreddit="python",
        title="Test Post",
        author="test_user",
        created_utc=1638316800,
        num_comments=10,
        score=100,
        url="https://example.com",
        permalink="/r/python/comments/12345/test_post/",
    )

    comment = Comment(
        id="456",
        subreddit="python",
        author="test_user",
        body="This is a comment",
        post_id="123",
    )

    post.comments.append(comment)

    assert len(post.comments) == 1
    assert post.comments[0].id == "456"
    assert post.comments[0].post_id == "123"
