# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from flask import Flask, render_template

from .api import evolve_blueprint, sim_blueprint
from .config import Config
from .models import Client, init_db


def create_app(config=None):
    """Flask app factory.

    config may be a database URL (as web_server.create_app), a dict of
    settings or an object / class with upper case attributes.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    if isinstance(config, str):
        app.config["DATABASE_URL"] = config
    elif isinstance(config, dict):
        app.config.update(config)
    elif config is not None:
        app.config.from_object(config)

    engine, SessionLocal = init_db(app.config["DATABASE_URL"])
    app.extensions["evolve_simulator"] = {"engine": engine, "session": SessionLocal}
    _seed_client(app, SessionLocal)

    app.register_blueprint(evolve_blueprint, url_prefix=app.config["API_PREFIX"])
    app.register_blueprint(sim_blueprint, url_prefix="/sim/api")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


def _seed_client(app, SessionLocal):
    """Register the configured client, if not yet in database"""
    if not app.config.get("CLIENT_ID"):
        return
    db = SessionLocal()
    try:
        client = (
            db.query(Client).filter(Client.client_id == app.config["CLIENT_ID"]).first()
        )
        if not client:
            db.add(
                Client(
                    client_id=app.config["CLIENT_ID"],
                    client_key=app.config["CLIENT_KEY"],
                    company_id=app.config["COMPANY_ID"],
                )
            )
            db.commit()
    finally:
        db.close()
