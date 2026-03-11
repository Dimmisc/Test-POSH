from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db import Base

engine = create_engine("sqlite:///site.db", echo=False)

Base.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)