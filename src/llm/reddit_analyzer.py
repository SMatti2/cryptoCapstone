from sqlmodel import Session, create_engine, select
from sqlalchemy import func
from typing import List, Optional

# Import your models as needed.
from src.models.post import Post
from src.models.comment import Comment


def create_engine_and_session(database_url: str):
    engine = create_engine(database_url, echo=False)
    session = Session(engine)
    return engine, session


def get_total_posts(session: Session) -> int:
    statement = select(func.count(Post.id))
    result = session.exec(statement).one()
    return result[0] if isinstance(result, tuple) else result


def get_total_comments(session: Session) -> int:
    statement = select(func.count(Comment.id))
    result = session.exec(statement).one()
    return result[0] if isinstance(result, tuple) else result


def get_earliest_posts(session: Session, limit: int = 5) -> List[Post]:
    statement = select(Post).order_by(Post.created_utc.asc()).limit(limit)
    return session.exec(statement).all()


def get_earliest_comments(session: Session, limit: int = 5) -> List[Comment]:
    statement = select(Comment).order_by(Comment.created_utc.asc()).limit(limit)
    return session.exec(statement).all()


def print_post_samples(posts: List[Post]):
    for i, post in enumerate(posts, start=1):
        print(
            f"{i}. ID: {post.id}, Subreddit: {post.subreddit}, "
            f"Title: {post.title[:50]}..., Created UTC: {post.created_utc}"
        )


def print_comment_samples(comments: List[Comment]):
    for i, comment in enumerate(comments, start=1):
        body_excerpt = comment.body[:50] + "..." if comment.body else "No content"
        print(
            f"{i}. ID: {comment.id}, Subreddit: {comment.subreddit}, "
            f"Body: {body_excerpt}, Created UTC: {comment.created_utc}"
        )


def show_post_details(posts: List[Post], max_text_len: int = 80):
    print(f"Showing details for {len(posts)} posts:")
    print("=" * 80)
    for i, post in enumerate(posts, start=1):
        # Truncate the selftext if too long
        if post.selftext:
            text_snippet = (
                post.selftext[:max_text_len] + "..."
                if len(post.selftext) > max_text_len
                else post.selftext
            )
        else:
            text_snippet = "(No selftext)"

        print(f"{i}. Post ID: {post.id}")
        print(f"   Subreddit: {post.subreddit}")
        print(f"   Title: {post.title}")
        print(f"   Author: {post.author}")
        print(f"   Created UTC: {post.created_utc}")
        print(f"   Score: {post.score}")
        print(f"   Number of Comments (as per the post object): {post.num_comments}")
        print(f"   Archived: {post.archived}")
        print(f"   Domain: {post.domain or '(none)'}")
        print(f"   URL: {post.url}")
        print(f"   Permalink: {post.permalink}")
        print(f"   Is Video: {post.is_video}")
        print(f"   Selftext Snippet: {text_snippet}")
        print("-" * 80)


def show_comment_details(comments: List[Comment], max_body_len: int = 80):
    print(f"Showing details for {len(comments)} comments:")
    print("=" * 80)
    for i, comment in enumerate(comments, start=1):
        # Truncate the body text if too long
        if comment.body:
            body_snippet = (
                comment.body[:max_body_len] + "..."
                if len(comment.body) > max_body_len
                else comment.body
            )
        else:
            body_snippet = "(No body)"

        print(f"{i}. Comment ID: {comment.id}")
        print(f"   Subreddit: {comment.subreddit or '(none)'}")
        print(f"   Author: {comment.author or '(unknown)'}")
        print(f"   Created UTC: {comment.created_utc}")
        print(f"   Score: {comment.score}")
        print(f"   Controversiality: {comment.controversiality}")
        print(f"   Gilded: {comment.gilded}")
        print(f"   Distinuguished: {comment.distinguished or '(none)'}")
        print(f"   Link ID: {comment.link_id or '(none)'}")
        print(f"   Post ID: {comment.post_id or '(none)'}")
        print(f"   Body Snippet: {body_snippet}")
        print("-" * 80)
