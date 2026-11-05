# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from datetime import timedelta

import pytest

from evolve_simulator.auth import (
    AuthError,
    check_authorization,
    make_headers,
    make_token,
    rome_now,
)

from .conftest import CLIENT_ID, CLIENT_KEY, call, cerca_request


def test_token_round_trip():
    now = rome_now().replace(microsecond=0)
    token = make_token(CLIENT_KEY, now=now)
    assert check_authorization("Bearer " + token, CLIENT_KEY, 300, now=now) == now


def test_token_expired():
    now = rome_now()
    token = make_token(CLIENT_KEY, now=now - timedelta(seconds=600))
    with pytest.raises(AuthError):
        check_authorization("Bearer " + token, CLIENT_KEY, 300, now=now)


def test_token_wrong_key():
    token = make_token("x" * 32)
    with pytest.raises(AuthError):
        check_authorization("Bearer " + token, CLIENT_KEY, 300)


@pytest.mark.parametrize(
    "authorization", ["", "Basic abc", "Bearer !!!", "Bearer QUJD"]
)
def test_token_malformed(authorization):
    with pytest.raises(AuthError):
        check_authorization(authorization, CLIENT_KEY, 300)


def test_call_authenticated(client, headers):
    data = call(client, "Cerca", cerca_request(1), headers)
    assert data["EsitoChiamata"] == 0
    assert data["Documenti"] == []


def test_call_wrong_key(client):
    data = call(client, "Cerca", cerca_request(1), make_headers(CLIENT_ID, "y" * 32))
    assert data["EsitoChiamata"] == 2
    assert "ErrorMessage" in data


def test_call_unknown_client(client):
    data = call(client, "Cerca", cerca_request(1), make_headers("nobody", CLIENT_KEY))
    assert data["EsitoChiamata"] == 2


def test_call_wrong_company(client, headers):
    req = cerca_request(1)
    req["IdAzienda"] = 99
    assert call(client, "Cerca", req, headers)["EsitoChiamata"] == 2


def test_call_no_auth_check(client):
    client.put("/sim/api/settings", json={"AUTH_CHECK": False})
    data = call(client, "Cerca", cerca_request(1), {"From": CLIENT_ID})
    assert data["EsitoChiamata"] == 0
