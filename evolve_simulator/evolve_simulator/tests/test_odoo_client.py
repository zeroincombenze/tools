# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""Requests built exactly as l10n_it_fatturapa_evolve (Odoo 12) builds them"""

import hashlib
import json
from base64 import b64encode
from datetime import datetime

import pytz
from Crypto.Cipher import AES

from evolve_simulator.auth import pkcs7_pad

from .conftest import CLIENT_ID, CLIENT_KEY, campi, run_workflow, salva_request


def odoo_header():
    # Same code as SdIChannel.evolve_header()
    now = datetime.now(pytz.timezone("Europe/Rome")).strftime("%Y-%m-%d %H.%M.%S")
    aes = AES.new(CLIENT_KEY.encode(), AES.MODE_CBC, CLIENT_KEY[:16].encode())
    return {
        "Content-Type": "application/json",
        "From": CLIENT_ID,
        "Authorization": (b"Bearer " + b64encode(aes.encrypt(pkcs7_pad(now)))).decode(),
    }


def odoo_post(client, action, request):
    # Odoo posts json.dumps(..., ensure_ascii=False) as raw data
    response = client.post(
        "/rest/api/v1/" + action,
        headers=odoo_header(),
        data=json.dumps(request, ensure_ascii=False).encode("utf-8"),
    )
    assert response.status_code == 200
    return response.get_json()


def test_odoo_send_and_verify(client):
    # send_via_evolve(): search out + sent archive, then Salva
    cerca = {
        "Filtri": [
            {
                "NomeCampo": "NumeroFattura",
                "Criterio": "=",
                "FromValue": "INV/2026/0001",
            }
        ],
        "IdAzienda": 7,
        "IdArchivio": 1,
    }
    data = odoo_post(client, "Cerca", cerca)
    assert data["EsitoChiamata"] == 0 and not data["Documenti"]
    data = odoo_post(client, "Salva", salva_request())
    assert -data.get("EsitoChiamata", 99) == 0
    # Second send: invoice found in sent archive, no upload needed
    cerca["IdArchivio"] = 3
    assert odoo_post(client, "Cerca", cerca)["Documenti"]
    # verify_all_notifications(): out archive gives the final state
    run_workflow(client)
    cerca["IdArchivio"] = 1
    docs = odoo_post(client, "Cerca", cerca)["Documenti"]
    doc = campi(docs[0])
    assert doc["StatoFattura"] == "Ricevuta di consegna"
    # Odoo parses DataFattura with "%Y-%m-%dT%H:%M:%S"
    datetime.strptime(doc["DataFattura"], "%Y-%m-%dT%H:%M:%S")


def test_odoo10_send(client):
    """l10n_it_einvoice_send2sdi (Odoo 10, python 2): datas is base64 in lines"""
    from base64 import encodebytes

    from .conftest import xml_invoice

    content = xml_invoice("FT/0010") + b"<!-- pad -->" * 20
    datas = encodebytes(content).decode("ascii")
    assert "\n" in datas
    request = salva_request("FT/0010")
    request["Files"][0]["Bytes"] = datas
    request["Files"][0]["Hash"] = hashlib.sha256(content).hexdigest()
    # Odoo 10 sends invoice.date, False when not set
    request["Documento"]["CampiDinamici"][1]["Valore"] = False
    data = odoo_post(client, "Salva", request)
    assert data["EsitoChiamata"] == 0, data.get("ErrorMessage")
    stato = campi(data["Documenti"][-1])
    assert stato["StatoInvioSdi"]
    # Date taken from the XML file
    assert stato["DataFattura"] == "2026-11-04T00:00:00"
