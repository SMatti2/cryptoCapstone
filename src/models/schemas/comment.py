from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from src.models.schemas.post import Post


class Comment(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    subreddit: Optional[str] = Field(default=None, nullable=True)
    author: Optional[str] = Field(default=None, nullable=True)
    body: Optional[str] = Field(default=None, nullable=True)
    created_utc: Optional[int] = Field(default=None, nullable=True)
    link_id: Optional[str] = Field(default=None, nullable=True)
    controversiality: Optional[int] = Field(default=None, nullable=True)
    ups: Optional[int] = Field(default=None, nullable=True)
    score: Optional[int] = Field(default=None, nullable=True)
    gilded: Optional[int] = Field(default=None, nullable=True)
    retrieved_on: Optional[int] = Field(default=None, nullable=True)
    distinguished: Optional[str] = Field(default=None, nullable=True)

    post_id: Optional[str] = Field(default=None, foreign_key="post.id")
    post: Optional["Post"] = Relationship(back_populates="comments")
