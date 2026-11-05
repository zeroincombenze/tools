# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""Simulator control API, used by the web page and by tests"""

import binascii

from flask import Blueprint, current_app, jsonify, request

from .. import workflow
from ..config import FAULTS, RUNTIME_SETTINGS
from ..models import Call, Client, Document, session_scope
from .evolve import decode_base64, normalize_date

sim_blueprint = Blueprint("sim", __name__)

DOCUMENT_FIELDS = ("sdi_state", "invoice_state", "note", "outcome")


def _error(message, status=400):
    return jsonify({"error": message}), status


@sim_blueprint.route("/settings", methods=["GET"])
def get_settings():
    config = current_app.config
    res = {key: config[key] for key in RUNTIME_SETTINGS}
    res.update(
        {
            "API_PREFIX": config["API_PREFIX"],
            "ARCHIVE_OUT": config["ARCHIVE_OUT"],
            "ARCHIVE_IN": config["ARCHIVE_IN"],
            "ARCHIVE_SENT": config["ARCHIVE_SENT"],
            "FILESTORE": config["FILESTORE"],
            "outcomes": list(workflow.OUTCOMES),
            "faults": list(FAULTS),
        }
    )
    return jsonify(res)


@sim_blueprint.route("/settings", methods=["PUT"])
def put_settings():
    data = request.get_json(silent=True) or {}
    values = {}
    for key, value in data.items():
        if key not in RUNTIME_SETTINGS:
            return _error("Unknown setting %s" % key)
        cast = RUNTIME_SETTINGS[key]
        try:
            values[key] = bool(value) if cast is bool else cast(value)
        except (TypeError, ValueError):
            return _error("Invalid value for %s" % key)
    if "FAULT" in values and values["FAULT"] not in FAULTS:
        return _error("FAULT must be one of %s" % ", ".join(FAULTS))
    if (
        "DEFAULT_OUTCOME" in values
        and values["DEFAULT_OUTCOME"] not in workflow.OUTCOMES
    ):
        return _error("Unknown outcome %s" % values["DEFAULT_OUTCOME"])
    current_app.config.update(values)
    return get_settings()


@sim_blueprint.route("/clients", methods=["GET"])
def get_clients():
    with session_scope() as db:
        return jsonify([c.to_dict() for c in db.query(Client).order_by(Client.id)])


@sim_blueprint.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json(silent=True) or {}
    client_id = (data.get("client_id") or "").strip()
    client_key = (data.get("client_key") or "").strip()
    if not client_id or len(client_key) not in (16, 24, 32):
        return _error("client_id required, client_key must be 16, 24 or 32 chars")
    try:
        company_id = int(data.get("company_id") or 1)
    except ValueError:
        return _error("company_id must be an integer")
    with session_scope() as db:
        client = db.query(Client).filter(Client.client_id == client_id).first()
        if not client:
            client = Client(client_id=client_id)
            db.add(client)
        client.client_key = client_key
        client.company_id = company_id
        db.commit()
        return jsonify(client.to_dict()), 201


@sim_blueprint.route("/documents", methods=["GET"])
def get_documents():
    with session_scope() as db:
        workflow.advance(db, current_app.config)
        query = db.query(Document)
        if request.args.get("archive"):
            query = query.filter(Document.archive == int(request.args["archive"]))
        docs = query.order_by(Document.id.desc()).all()
        return jsonify([d.to_dict() for d in docs])


@sim_blueprint.route("/documents/<int:doc_id>", methods=["PATCH"])
def patch_document(doc_id):
    data = request.get_json(silent=True) or {}
    with session_scope() as db:
        doc = db.get(Document, doc_id)
        if not doc:
            return _error("Document not found", 404)
        for key in DOCUMENT_FIELDS:
            if key in data:
                setattr(doc, key, data[key] or None)
        db.commit()
        return jsonify(doc.to_dict())


@sim_blueprint.route("/documents/<int:doc_id>/advance", methods=["POST"])
def advance_document(doc_id):
    """Run the next workflow step now"""
    with session_scope() as db:
        doc = db.get(Document, doc_id)
        if not doc:
            return _error("Document not found", 404)
        if not workflow.advance_document(db, current_app.config, doc):
            return _error("Workflow of document already done")
        db.commit()
        return jsonify(doc.to_dict())


@sim_blueprint.route("/documents/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    with session_scope() as db:
        doc = db.get(Document, doc_id)
        if not doc:
            return _error("Document not found", 404)
        db.delete(doc)
        db.commit()
        return jsonify({"status": "ok"})


@sim_blueprint.route("/inbox", methods=["POST"])
def add_inbox():
    """Put a purchase invoice in the in archive, as received from SdI"""
    config = current_app.config
    data = request.get_json(silent=True) or {}
    if data.get("xml"):
        content = data["xml"].encode("utf-8")
    else:
        try:
            content = decode_base64(data.get("bytes") or "")
        except (binascii.Error, ValueError):
            return _error("bytes must be base64")
    if not content:
        return _error("xml or bytes required")
    with session_scope() as db:
        doc = workflow.inbound_document(
            db,
            config,
            content,
            file_name=data.get("file_name"),
            company_id=data.get("company_id"),
        )
        if data.get("number"):
            doc.number = data["number"]
        if data.get("date"):
            doc.date = normalize_date(data["date"])
        db.commit()
        return jsonify(doc.to_dict()), 201


@sim_blueprint.route("/calls", methods=["GET"])
def get_calls():
    with session_scope() as db:
        calls = db.query(Call).order_by(Call.id.desc()).limit(100).all()
        return jsonify([c.to_dict() for c in calls])


@sim_blueprint.route("/reset", methods=["POST"])
def reset():
    """Delete all documents and the call log; clients are kept"""
    with session_scope() as db:
        db.query(Document).delete()
        db.query(Call).delete()
        db.commit()
    return jsonify({"status": "ok"})
