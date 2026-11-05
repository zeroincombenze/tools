# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from contextlib import contextmanager

from flask import current_app

from .db import Base, make_engine, make_session
from .call import Call
from .client import Client
from .document import Document

__all__ = ["Base", "Call", "Client", "Document", "init_db", "session_scope"]


def init_db(database_url):
    engine = make_engine(database_url)
    SessionLocal = make_session(engine)
    Base.metadata.create_all(bind=engine)
    return engine, SessionLocal


@contextmanager
def session_scope():
    """Database session of the current Flask app"""
    db = current_app.extensions["evolve_simulator"]["session"]()
    try:
        yield db
    finally:
        db.close()
