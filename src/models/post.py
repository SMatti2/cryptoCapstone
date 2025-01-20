from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Post(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    subreddit: str = Field()
    title: str = Field()
    selftext: Optional[str] = Field(default=None, nullable=True)
    author: str = Field()
    created_utc: int = Field()
    num_comments: int = Field()
    score: int = Field()
    url: str = Field()
    archived: bool = Field(default=False)
    domain: Optional[str] = Field(default=None, nullable=True)
    permalink: str = Field()
    is_video: bool = Field(default=False)

    # Relationship to comments:
    comments: List["Comment"] = Relationship(back_populates="post")
