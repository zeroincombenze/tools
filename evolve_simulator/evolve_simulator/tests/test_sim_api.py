# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from .conftest import call, cerca_request, salva_request


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Evolve Simulator" in response.data


def test_settings(client):
    data = client.get("/sim/api/settings").get_json()
    assert data["ARCHIVE_SENT"] == 3
    assert "Ricevuta di consegna" in data["outcomes"]
    data = client.put("/sim/api/settings", json={"SDI_DELAY": "5"}).get_json()
    assert data["SDI_DELAY"] == 5
    assert client.put("/sim/api/settings", json={"FAULT": "boom"}).status_code == 400
    assert client.put("/sim/api/settings", json={"NOPE": 1}).status_code == 400


def test_fault_http500(client, headers):
    client.put("/sim/api/settings", json={"FAULT": "http500"})
    response = client.post("/rest/api/v1/Cerca", json=cerca_request(1), headers=headers)
    assert response.status_code == 500


def test_fault_esito(client, headers):
    client.put("/sim/api/settings", json={"FAULT": "esito1"})
    assert call(client, "Salva", salva_request(), headers)["EsitoChiamata"] == 1
    client.put("/sim/api/settings", json={"FAULT": "auth"})
    assert call(client, "Salva", salva_request(), headers)["EsitoChiamata"] == 2
    client.put("/sim/api/settings", json={"FAULT": ""})
    assert call(client, "Salva", salva_request(), headers)["EsitoChiamata"] == 0


def test_clients(client):
    assert (
        client.post(
            "/sim/api/clients", json={"client_id": "x", "client_key": "short"}
        ).status_code
        == 400
    )
    response = client.post(
        "/sim/api/clients",
        json={"client_id": "x", "client_key": "k" * 16, "company_id": 3},
    )
    assert response.status_code == 201
    assert len(client.get("/sim/api/clients").get_json()) == 2


def test_patch_delete_reset(client, headers):
    call(client, "Salva", salva_request(), headers)
    doc = client.get("/sim/api/documents").get_json()[0]
    data = client.patch(
        "/sim/api/documents/%d" % doc["id"], json={"note": "hello"}
    ).get_json()
    assert data["note"] == "hello"
    assert client.delete("/sim/api/documents/%d" % doc["id"]).status_code == 200
    assert client.delete("/sim/api/documents/%d" % doc["id"]).status_code == 404
    call(client, "Salva", salva_request(), headers)
    assert len(client.get("/sim/api/calls").get_json()) == 2
    client.post("/sim/api/reset")
    assert client.get("/sim/api/documents").get_json() == []
    assert client.get("/sim/api/calls").get_json() == []
