# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""Evolve REST API: Cerca, Salva, Recupera.

Every call is a POST with a JSON body; the reply is always HTTP 200 with
EsitoChiamata = 0 (ok), 1 (error) or 2 (authentication error).
"""

import hashlib
import logging
import re
import uuid
from base64 import b64decode
from datetime import datetime

import binascii
from flask import Blueprint, abort, current_app, jsonify, request

from .. import workflow
from ..auth import AuthError, check_authorization
from ..models import Call, Client, Document, session_scope
from ..xmlinfo import normalize_date, parse_invoice

_logger = logging.getLogger(__name__)

evolve_blueprint = Blueprint("evolve", __name__)

ESITO_OK = 0
ESITO_ERROR = 1
ESITO_AUTH = 2

DATE_FIELDS = ("DataFattura", "DataCaricamento", "DataRicezione", "DataDownload")


def decode_base64(value):
    """Decode base64 ignoring whitespace: Odoo 10 (python 2) splits it in lines"""
    if not isinstance(value, str):
        raise ValueError("base64 value must be a string")
    return b64decode(re.sub(r"\s+", "", value), validate=True)


class EvolveError(Exception):
    def __init__(self, message, esito=ESITO_ERROR):
        super(EvolveError, self).__init__(message)
        self.message = message
        self.esito = esito


def _authenticate(db, config):
    client_id = request.headers.get("From", "")
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not config["AUTH_CHECK"]:
        return client or db.query(Client).first()
    if not client:
        raise EvolveError("Client ID '%s' non registrato" % client_id, ESITO_AUTH)
    try:
        check_authorization(
            request.headers.get("Authorization", ""),
            client.client_key,
            config["AUTH_TOLERANCE"],
        )
    except AuthError as e:
        raise EvolveError("Autenticazione fallita: %s" % e, ESITO_AUTH)
    return client


def _ids(data):
    """IdAzienda and IdArchivio, either in Documento or at top level"""
    container = (
        data.get("Documento") if isinstance(data.get("Documento"), dict) else data
    )
    return container.get("IdAzienda"), container.get("IdArchivio")


def _campi(documento):
    res = {}
    for campo in documento.get("CampiDinamici") or []:
        if isinstance(campo, dict) and campo.get("Nome"):
            res[campo["Nome"]] = campo.get("Valore")
    return res


def _match(values, filtro):
    name = filtro.get("NomeCampo")
    criterio = (filtro.get("Criterio") or "=").strip().lower()
    value = values.get(name)
    expected = filtro.get("FromValue")
    if name in DATE_FIELDS:
        expected = normalize_date(expected)
    if criterio == "nullo":
        return value is None
    if criterio in ("non nullo", "nonnullo", "not null"):
        return value is not None
    if value is None:
        return False
    value, expected = str(value), str(expected)
    if criterio == "=":
        return value == expected
    if criterio in ("<>", "!="):
        return value != expected
    if criterio == ">":
        return value > expected
    if criterio == ">=":
        return value >= expected
    if criterio == "<":
        return value < expected
    if criterio == "<=":
        return value <= expected
    if criterio in ("like", "contiene"):
        return expected.lower().strip("%") in value.lower()
    raise EvolveError("Criterio '%s' non supportato" % filtro.get("Criterio"))


def do_cerca(db, config, client, data, archive):
    filtri = data.get("Filtri") or []
    if not isinstance(filtri, list):
        raise EvolveError("Filtri deve essere una lista")
    docs = (
        db.query(Document)
        .filter(Document.archive == archive, Document.company_id == client.company_id)
        .order_by(Document.loaded_at, Document.id)
        .all()
    )
    res = []
    for doc in docs:
        values = {c["Nome"]: c["Valore"] for c in doc.campi_dinamici()}
        if all(_match(values, f) for f in filtri):
            res.append(doc.to_evolve())
    return {"Documenti": res}, "%d documenti" % len(res)


def do_salva(db, config, client, data, archive):
    if archive != config["ARCHIVE_SENT"]:
        raise EvolveError("Archivio %s non abilitato al caricamento" % archive)
    documento = data.get("Documento")
    files = data.get("Files")
    if not isinstance(documento, dict):
        raise EvolveError("Documento mancante")
    if not files or not isinstance(files, list):
        raise EvolveError("Nessun file allegato")
    campi = _campi(documento)
    number = campi.get("NumeroFattura")
    if not number:
        raise EvolveError("Campo NumeroFattura obbligatorio")
    file = files[0]
    try:
        content = decode_base64(file.get("Bytes") or "")
    except (binascii.Error, ValueError, TypeError):
        raise EvolveError("Bytes del file non in formato base64")
    if not content:
        raise EvolveError("File vuoto")
    digest = hashlib.sha256(content).hexdigest()
    if file.get("Hash") and file["Hash"].lower() != digest:
        raise EvolveError("Hash del file non corrispondente")
    info = parse_invoice(content, file.get("Nome"))
    doc = Document(
        uid=uuid.uuid4().hex,
        company_id=client.company_id,
        archive=archive,
        number=number,
        date=normalize_date(campi.get("DataFattura") or info["date"]),
        td=info["td"],
        file_name=file.get("Nome") or "%s.xml" % number,
        file_bytes=file.get("Bytes"),
        file_hash=digest,
        xml_valid=info["valid"],
        **workflow.stage(config)
    )
    db.add(doc)
    db.commit()
    return {"Documenti": [doc.to_evolve()]}, "Salvato %s" % number


def do_recupera(db, config, client, data, archive):
    documento = data.get("Documento")
    if not isinstance(documento, dict):
        raise EvolveError("Documento mancante")
    uid = _campi(documento).get("Uid")
    if not uid:
        raise EvolveError("Campo Uid obbligatorio")
    doc = (
        db.query(Document)
        .filter(
            Document.uid == uid,
            Document.archive == archive,
            Document.company_id == client.company_id,
        )
        .first()
    )
    if not doc:
        raise EvolveError("Documento %s non trovato nell'archivio %s" % (uid, archive))
    if archive == config["ARCHIVE_IN"]:
        doc.downloaded_at = datetime.now()
        db.commit()
    return {
        "Documenti": [doc.to_evolve()],
        "Files": [doc.to_file()],
    }, "Recuperato %s" % uid


ACTIONS = {
    "Cerca": do_cerca,
    "Salva": do_salva,
    "Recupera": do_recupera,
}


def _log(db, action, client_id, archive, esito, message):
    db.add(
        Call(
            action=action,
            client_id=client_id,
            archive=archive if isinstance(archive, int) else None,
            esito=esito,
            message=message,
        )
    )
    db.commit()


@evolve_blueprint.route("/<action>", methods=["POST"])
def evolve_call(action):
    if action not in ACTIONS:
        abort(404)
    config = current_app.config
    client_id = request.headers.get("From", "")
    with session_scope() as db:
        archive = None
        try:
            if config["FAULT"] == "http500":
                _log(db, action, client_id, None, -1, "Errore HTTP 500 simulato")
                abort(500)
            data = request.get_json(force=True, silent=True)
            if not isinstance(data, dict):
                raise EvolveError("Richiesta JSON non valida")
            company_id, archive = _ids(data)
            if config["FAULT"] == "auth":
                raise EvolveError("Autenticazione fallita (simulata)", ESITO_AUTH)
            client = _authenticate(db, config)
            if not client:
                raise EvolveError("Nessun cliente configurato", ESITO_AUTH)
            if config["FAULT"] == "esito1":
                raise EvolveError("Errore generico simulato")
            try:
                company_id = int(company_id)
                archive = int(archive)
            except (TypeError, ValueError):
                raise EvolveError("IdAzienda e IdArchivio obbligatori")
            if company_id != client.company_id:
                raise EvolveError("Azienda %s non abilitata" % company_id, ESITO_AUTH)
            if archive not in (
                config["ARCHIVE_OUT"],
                config["ARCHIVE_IN"],
                config["ARCHIVE_SENT"],
            ):
                raise EvolveError("Archivio %s inesistente" % archive)
            workflow.advance(db, config)
            result, message = ACTIONS[action](db, config, client, data, archive)
        except EvolveError as e:
            _logger.info("Evolve.%s -> %s %s", action, e.esito, e.message)
            _log(db, action, client_id, archive, e.esito, e.message)
            return jsonify({"EsitoChiamata": e.esito, "ErrorMessage": e.message})
        _log(db, action, client_id, archive, ESITO_OK, message)
        result["EsitoChiamata"] = ESITO_OK
        return jsonify(result)
