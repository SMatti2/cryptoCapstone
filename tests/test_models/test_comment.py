import pytest
from src.models.schemas.comment import Comment


def test_comment_initialization():
    comment = Comment(
        id="123",
        subreddit="python",
        author="test_user",
        body="This is a test",
        created_utc=1638316800,
        link_id="t3_12345",
        controversiality=0,
        ups=10,
        score=10,
        gilded=0,
        retrieved_on=1638316800,
        distinguished="moderator",
    )
    assert comment.id == "123"
    assert comment.subreddit == "python"
    assert comment.author == "test_user"
    assert comment.body == "This is a test"
    assert comment.created_utc == 1638316800
    assert comment.link_id == "t3_12345"
    assert comment.controversiality == 0
    assert comment.ups == 10
    assert comment.score == 10
    assert comment.gilded == 0
    assert comment.retrieved_on == 1638316800
    assert comment.distinguished == "moderator"


def test_comment_partial_initialization():
    comment = Comment(
        id="789", subreddit="python", author="test_user", body="This is a test"
    )
    assert comment.id == "789"
    assert comment.subreddit == "python"
    assert comment.author == "test_user"
    assert comment.body == "This is a test"
    assert comment.created_utc is None
    assert comment.link_id is None
    assert comment.controversiality is None
    assert comment.ups is None
    assert comment.score is None
    assert comment.gilded is None
    assert comment.retrieved_on is None
    assert comment.distinguished is None


def test_comment_field_types():
    comment = Comment(
        id="131415",
        subreddit="python",
        author="test_user",
        body="This is a test",
        created_utc=1638316800,
        link_id="t3_12345",
        controversiality=0,
        ups=10,
        score=10,
        gilded=0,
        retrieved_on=1638316800,
        distinguished="moderator",
    )
    assert isinstance(comment.id, str)
    assert isinstance(comment.subreddit, str)
    assert isinstance(comment.author, str)
    assert isinstance(comment.body, str)
    assert isinstance(comment.created_utc, int)
    assert isinstance(comment.link_id, str)
    assert isinstance(comment.controversiality, int)
    assert isinstance(comment.ups, int)
    assert isinstance(comment.score, int)
    assert isinstance(comment.gilded, int)
    assert isinstance(comment.retrieved_on, int)
    assert isinstance(comment.distinguished, str)
