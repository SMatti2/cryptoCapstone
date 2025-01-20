from sqlmodel import create_engine, SQLModel
from config import config

from src.models.post import Post
from src.models.comment import Comment

engine = create_engine(config.DATABASE_URL, echo=False)

# create all tables defined in SQLModel classes
SQLModel.metadata.create_all(engine)
print("Tables created successfully!")
