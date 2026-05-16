from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def make_engine(database_url):
    return create_engine(database_url, future=True)

def make_session(engine):
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True
    )
