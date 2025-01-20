import pytest

from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import ValidationError

from src.models.post import Post


def test_post_initialization():
    post = Post(
        id="123",
        subreddit="python",
        title="Test Post",
        author="test_user",
        created_utc=1638316800,
        num_comments=10,
        score=100,
        url="https://example.com",
        permalink="/r/python/comments/123/test_post/",
    )

    assert post.id == "123"
    assert post.subreddit == "python"
    assert post.title == "Test Post"
    assert post.author == "test_user"
    assert post.created_utc == 1638316800
    assert post.num_comments == 10
    assert post.score == 100
    assert post.url == "https://example.com"
    assert post.permalink == "/r/python/comments/123/test_post/"
    assert post.archived is False
    assert post.domain is None
    assert post.over_18 is False
    assert post.is_video is False


def test_post_optional_fields():
    post = Post(
        id="456",
        subreddit="python",
        title="Test Post with Optional Fields",
        selftext="This is a test",
        author="test_user",
        created_utc=1638316800,
        num_comments=5,
        score=50,
        url="https://example.com",
        permalink="/r/python/comments/456/test_post_with_optional_fields/",
        archived=True,
        domain="example.com",
        over_18=True,
        is_video=True,
    )

    assert post.selftext == "This is a test"
    assert post.archived is True
    assert post.domain == "example.com"
    assert post.over_18 is True
    assert post.is_video is True


def test_post_default_values():
    post = Post(
        id="789",
        subreddit="python",
        title="Test Post with Default Values",
        author="test_user",
        created_utc=1638316800,
        num_comments=5,
        score=50,
        url="https://example.com",
        permalink="/r/python/comments/789/test_post_default_values/",
    )

    assert post.archived is False
    assert post.domain is None
    assert post.over_18 is False
    assert post.is_video is False
