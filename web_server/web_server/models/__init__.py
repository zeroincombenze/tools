from .db import Base, make_engine, make_session
from .message import Message

def init_db(database_url):
    engine = make_engine(database_url)
    SessionLocal = make_session(engine)
    Base.metadata.create_all(bind=engine)
    return engine, SessionLocal
