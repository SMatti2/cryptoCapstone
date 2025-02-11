import pytest
from sqlmodel import Session, SQLModel, create_engine
from src.llm.reddit_analyzer import (
    get_total_posts,
    get_total_comments,
    get_earliest_posts,
    get_earliest_comments,
    print_post_samples,
    print_comment_samples,
    show_post_details,
    show_comment_details,
)
from src.models.post import Post
from src.models.comment import Comment


@pytest.fixture(scope="module")
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def sample_data(session):
    posts = [
        Post(
            id="1",
            subreddit="test",
            title="Test Post 1",
            created_utc=1000,
            author="test_author1",
            num_comments=0,
            score=1,
            archived=False,
            is_video=False,
            url="https://example.com/post1",
            permalink="/r/test/comments/1/test_post_1",
        ),
        Post(
            id="2",
            subreddit="test",
            title="Test Post 2",
            created_utc=2000,
            author="test_author2",
            num_comments=0,
            score=1,
            archived=False,
            is_video=False,
            url="https://example.com/post2",
            permalink="/r/test/comments/2/test_post_2",
        ),
    ]
    comments = [
        Comment(id="1", subreddit="test", body="Test Comment 1", created_utc=1500),
        Comment(id="2", subreddit="test", body="Test Comment 2", created_utc=2500),
    ]
    session.add_all(posts + comments)
    session.commit()


def test_get_total_posts(session, sample_data):
    assert get_total_posts(session) == 2


def test_get_total_comments(session, sample_data):
    assert get_total_comments(session) == 2


def test_get_earliest_posts(session, sample_data):
    earliest_posts = get_earliest_posts(session)
    assert len(earliest_posts) == 2
    assert earliest_posts[0].created_utc == 1000


def test_get_earliest_comments(session, sample_data):
    earliest_comments = get_earliest_comments(session)
    assert len(earliest_comments) == 2
    assert earliest_comments[0].created_utc == 1500


def test_print_post_samples(capsys, sample_data):
    posts = [Post(id="1", subreddit="test", title="Test Post", created_utc=1000)]
    print_post_samples(posts)
    captured = capsys.readouterr()
    assert "1. ID: 1, Subreddit: test" in captured.out


def test_print_comment_samples(capsys, sample_data):
    comments = [
        Comment(id="1", subreddit="test", body="Test Comment", created_utc=1000)
    ]
    print_comment_samples(comments)
    captured = capsys.readouterr()
    assert "1. ID: 1, Subreddit: test" in captured.out


def test_show_post_details(capsys, sample_data):
    posts = [Post(id="1", subreddit="test", title="Test Post", created_utc=1000)]
    show_post_details(posts)
    captured = capsys.readouterr()
    assert "Post ID: 1" in captured.out
    assert "Subreddit: test" in captured.out


def test_show_comment_details(capsys, sample_data):
    comments = [
        Comment(id="1", subreddit="test", body="Test Comment", created_utc=1000)
    ]
    show_comment_details(comments)
    captured = capsys.readouterr()
    assert "Comment ID: 1" in captured.out
    assert "Subreddit: test" in captured.out
