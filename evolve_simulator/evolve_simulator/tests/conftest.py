# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
import hashlib
from base64 import b64encode

import pytest

from evolve_simulator.app import create_app
from evolve_simulator.auth import make_headers

CLIENT_ID = "test"
CLIENT_KEY = "abcdefghijklmnopabcdefghijklmnop"
COMPANY_ID = 7

INVOICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica versione="FPR12"
    xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2">
  <FatturaElettronicaHeader/>
  <FatturaElettronicaBody>
    <DatiGenerali>
      <DatiGeneraliDocumento>
        <TipoDocumento>{td}</TipoDocumento>
        <Divisa>EUR</Divisa>
        <Data>2026-11-04</Data>
        <Numero>{number}</Numero>
      </DatiGeneraliDocumento>
    </DatiGenerali>
  </FatturaElettronicaBody>
</p:FatturaElettronica>
"""


@pytest.fixture
def app():
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CLIENT_ID": CLIENT_ID,
            "CLIENT_KEY": CLIENT_KEY,
            "COMPANY_ID": COMPANY_ID,
            "SDI_DELAY": 3600,
            "OUTCOME_DELAY": 3600,
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def headers():
    return make_headers(CLIENT_ID, CLIENT_KEY)


def xml_invoice(number="INV/2026/0001", td="TD01"):
    return INVOICE_XML.format(number=number, td=td).encode("utf-8")


def salva_request(number="INV/2026/0001", content=None, archive=3, name=None):
    """Salva body, built as l10n_it_fatturapa_evolve does"""
    content = content if content is not None else xml_invoice(number)
    return {
        "Files": [
            {
                "Bytes": b64encode(content).decode("ascii"),
                "MimeType": "text/xml",
                "Nome": name or "IT00000000000_%s.xml" % number[-4:],
                "Extension": "XML",
                "Hash": hashlib.sha256(content).hexdigest(),
            }
        ],
        "Documento": {
            "Visible": True,
            "CampiDinamici": [
                {"Nome": "NumeroFattura", "CriterioPredefinito": "=", "Valore": number},
                {
                    "Nome": "DataFattura",
                    "CriterioPredefinito": "=",
                    "Valore": "2026-11-04",
                },
            ],
            "IdAzienda": COMPANY_ID,
            "IdArchivio": archive,
        },
    }


def cerca_request(archive, number=None, filtri=None):
    req = {"IdAzienda": COMPANY_ID, "IdArchivio": archive}
    if number:
        req["Filtri"] = [
            {"NomeCampo": "NumeroFattura", "Criterio": "=", "FromValue": number}
        ]
    if filtri is not None:
        req["Filtri"] = filtri
    return req


def campi(doc):
    return {c["Nome"]: c["Valore"] for c in doc["CampiDinamici"]}


def call(client, action, body, headers):
    response = client.post("/rest/api/v1/" + action, json=body, headers=headers)
    assert response.status_code == 200
    return response.get_json()


def run_workflow(client):
    """Make every pending step due now and run it"""
    client.put("/sim/api/settings", json={"SDI_DELAY": 0, "OUTCOME_DELAY": 0})
    for doc in client.get("/sim/api/documents").get_json():
        while doc["step"] < 2:
            doc = client.post("/sim/api/documents/%d/advance" % doc["id"]).get_json()
