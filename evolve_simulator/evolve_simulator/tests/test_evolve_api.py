# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from base64 import b64decode

from evolve_simulator.workflow import STATE_INVALID, STATE_STAGED

from .conftest import (
    call,
    campi,
    cerca_request,
    run_workflow,
    salva_request,
    xml_invoice,
)


def test_salva_stages_document(client, headers):
    data = call(client, "Salva", salva_request(), headers)
    assert data["EsitoChiamata"] == 0
    doc = campi(data["Documenti"][-1])
    assert doc["StatoInvioSdi"] == STATE_STAGED
    assert doc["NumeroFattura"] == "INV/2026/0001"
    assert doc["DataFattura"] == "2026-11-04T00:00:00"
    assert doc["Uid"]
    # Found in sent archive, not yet in out archive
    assert (
        len(
            call(client, "Cerca", cerca_request(3, "INV/2026/0001"), headers)[
                "Documenti"
            ]
        )
        == 1
    )
    assert (
        call(client, "Cerca", cerca_request(1, "INV/2026/0001"), headers)["Documenti"]
        == []
    )


def test_workflow_delivered(client, headers):
    uid = campi(call(client, "Salva", salva_request(), headers)["Documenti"][0])["Uid"]
    run_workflow(client)
    docs = call(client, "Cerca", cerca_request(1, "INV/2026/0001"), headers)[
        "Documenti"
    ]
    assert len(docs) == 1
    doc = campi(docs[0])
    assert doc["Uid"] == uid
    assert doc["StatoFattura"] == "Ricevuta di consegna"
    assert doc["IdentificativoSdi"]
    assert doc["DataFattura"] == "2026-11-04T00:00:00"


def test_workflow_by_delay(client, headers):
    client.put("/sim/api/settings", json={"SDI_DELAY": 0, "OUTCOME_DELAY": 0})
    call(client, "Salva", salva_request(), headers)
    # Due steps are run when the next request arrives
    docs = call(client, "Cerca", cerca_request(1), headers)["Documenti"]
    assert campi(docs[0])["StatoFattura"] == "Ricevuta di consegna"


def test_workflow_planned_outcome(client, headers):
    call(client, "Salva", salva_request(), headers)
    doc = client.get("/sim/api/documents?archive=3").get_json()[0]
    client.patch(
        "/sim/api/documents/%d" % doc["id"], json={"outcome": "Notifica di scarto"}
    )
    run_workflow(client)
    out = campi(call(client, "Cerca", cerca_request(1), headers)["Documenti"][0])
    assert out["StatoFattura"] == "Notifica di scarto"
    assert out["Note"]


def test_workflow_duplicate(client, headers):
    call(client, "Salva", salva_request(), headers)
    run_workflow(client)
    call(client, "Salva", salva_request(), headers)
    run_workflow(client)
    docs = [
        campi(d) for d in call(client, "Cerca", cerca_request(1), headers)["Documenti"]
    ]
    assert len(docs) == 2
    assert docs[0]["StatoFattura"] == "Ricevuta di consegna"
    assert docs[1]["StatoFattura"] == "Notifica di scarto"
    assert docs[1]["Note"] == "Fattura duplicata"


def test_workflow_invalid_xml(client, headers):
    call(client, "Salva", salva_request(content=b"<not-an-invoice/>"), headers)
    run_workflow(client)
    sent = campi(call(client, "Cerca", cerca_request(3), headers)["Documenti"][0])
    assert sent["StatoInvioSdi"] == STATE_INVALID
    assert call(client, "Cerca", cerca_request(1), headers)["Documenti"] == []


def test_workflow_self_invoice(client, headers):
    req = salva_request("AUTO/0001", content=xml_invoice("AUTO/0001", td="TD17"))
    call(client, "Salva", req, headers)
    run_workflow(client)
    assert call(client, "Cerca", cerca_request(1), headers)["Documenti"] == []
    docs = call(client, "Cerca", cerca_request(2, "AUTO/0001"), headers)["Documenti"]
    assert campi(docs[0])["TipoDocumento"] == "TD17"


def test_salva_hash_mismatch(client, headers):
    req = salva_request()
    req["Files"][0]["Hash"] = "0" * 64
    data = call(client, "Salva", req, headers)
    assert data["EsitoChiamata"] == 1
    assert "Hash" in data["ErrorMessage"]


def test_salva_wrong_archive(client, headers):
    assert (
        call(client, "Salva", salva_request(archive=1), headers)["EsitoChiamata"] == 1
    )


def test_salva_no_number(client, headers):
    req = salva_request()
    req["Documento"]["CampiDinamici"] = []
    assert call(client, "Salva", req, headers)["EsitoChiamata"] == 1


def test_cerca_filters(client, headers):
    client.post("/sim/api/inbox", json={"xml": xml_invoice("ACQ/1").decode()})
    filtri = [
        {"NomeCampo": "DataDownload", "Criterio": "nullo"},
        {
            "NomeCampo": "DataRicezione",
            "Criterio": ">",
            "FromValue": "2020-01-01T00:00:00",
        },
    ]
    docs = call(client, "Cerca", cerca_request(2, filtri=filtri), headers)["Documenti"]
    assert len(docs) == 1
    assert campi(docs[0])["NumeroFattura"] == "ACQ/1"
    bad = [{"NomeCampo": "Uid", "Criterio": "?", "FromValue": "x"}]
    assert (
        call(client, "Cerca", cerca_request(2, filtri=bad), headers)["EsitoChiamata"]
        == 1
    )


def test_recupera_purchase_invoice(client, headers):
    client.post("/sim/api/inbox", json={"xml": xml_invoice("ACQ/2").decode()})
    doc = campi(call(client, "Cerca", cerca_request(2), headers)["Documenti"][0])
    req = {
        "Documento": {
            "IdAzienda": 7,
            "IdArchivio": 2,
            "CampiDinamici": [{"Nome": "Uid", "Valore": doc["Uid"]}],
        },
        "Recupera": 2,
    }
    data = call(client, "Recupera", req, headers)
    assert data["EsitoChiamata"] == 0
    got = campi(data["Documenti"][0])
    file = [f for f in data["Files"] if f["Nome"] == got["NomeFile"]][0]
    assert b"ACQ/2" in b64decode(file["Bytes"])
    assert got["DataDownload"]
    # Downloaded invoice no more matched by "DataDownload nullo"
    filtri = [{"NomeCampo": "DataDownload", "Criterio": "nullo"}]
    assert (
        call(client, "Cerca", cerca_request(2, filtri=filtri), headers)["Documenti"]
        == []
    )


def test_unknown_action(client, headers):
    assert (
        client.post("/rest/api/v1/Elimina", json={}, headers=headers).status_code == 404
    )


def test_bad_json(client, headers):
    response = client.post("/rest/api/v1/Cerca", data="no json", headers=headers)
    assert response.get_json()["EsitoChiamata"] == 1
