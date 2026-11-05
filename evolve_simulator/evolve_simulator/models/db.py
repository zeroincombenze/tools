# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()


def make_engine(database_url):
    kwargs = {}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in database_url or database_url == "sqlite://":
            # Share the one in-memory database among all sessions (tests)
            kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


def make_session(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
