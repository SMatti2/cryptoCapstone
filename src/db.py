from sqlmodel import create_engine
from config import config

engine = create_engine(config.DATABASE_URL, echo=False)
