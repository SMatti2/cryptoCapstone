from typing import Optional
from sqlmodel import SQLModel, Field


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
    over_18: bool = Field(default=False)
    permalink: str = Field()
    is_video: bool = Field(default=False)
