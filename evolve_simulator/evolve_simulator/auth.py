# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""Evolve authentication.

The client sends:
    From: <client id>
    Authorization: Bearer base64(AES-CBC(key, iv=key[:16], PKCS7(now)))
where now is the Europe/Rome time formatted as "%Y-%m-%d %H.%M.%S".
"""

from base64 import b64decode, b64encode
from datetime import datetime

import binascii
import pytz
from Crypto.Cipher import AES

TOKEN_FMT = "%Y-%m-%d %H.%M.%S"
TIMEZONE = "Europe/Rome"
BLOCK_SIZE = 16


class AuthError(Exception):
    pass


def _b(text):
    return text.encode("utf-8") if not isinstance(text, bytes) else text


def pkcs7_pad(data, block_size=BLOCK_SIZE):
    data = _b(data)
    n = block_size - len(data) % block_size
    return data + bytes([n]) * n


def pkcs7_unpad(data, block_size=BLOCK_SIZE):
    if not data or len(data) % block_size:
        raise AuthError("Token di lunghezza non valida")
    n = data[-1]
    if n < 1 or n > block_size or data[-n:] != bytes([n]) * n:
        raise AuthError("Token con padding non valido")
    return data[:-n]


def _cipher(client_key):
    key = _b(client_key)
    if len(key) not in (16, 24, 32):
        raise AuthError("Client Key di lunghezza non valida (16, 24 o 32 caratteri)")
    return AES.new(key, AES.MODE_CBC, key[:16])


def rome_now():
    return datetime.now(pytz.timezone(TIMEZONE)).replace(tzinfo=None)


def make_token(client_key, now=None):
    """Return the Bearer token exactly as the Odoo client builds it"""
    now = now or rome_now()
    text = now.strftime(TOKEN_FMT)
    return b64encode(_cipher(client_key).encrypt(pkcs7_pad(text))).decode("ascii")


def make_headers(client_id, client_key, now=None):
    """HTTP headers of an Evolve call (for tests and client scripts)"""
    return {
        "Content-Type": "application/json",
        "From": client_id,
        "Authorization": "Bearer " + make_token(client_key, now=now),
    }


def decode_token(token, client_key):
    try:
        raw = b64decode(token, validate=True)
    except (binascii.Error, ValueError):
        raise AuthError("Token non in formato base64")
    if not raw or len(raw) % BLOCK_SIZE:
        raise AuthError("Token di lunghezza non valida")
    text = pkcs7_unpad(_cipher(client_key).decrypt(raw))
    try:
        return datetime.strptime(text.decode("utf-8"), TOKEN_FMT)
    except (UnicodeDecodeError, ValueError):
        raise AuthError("Token non decifrabile con la Client Key")


def check_authorization(authorization, client_key, tolerance, now=None):
    """Raise AuthError if Authorization header is not valid"""
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError("Header Authorization mancante o non Bearer")
    stamp = decode_token(authorization[7:].strip(), client_key)
    now = now or rome_now()
    delta = abs((now - stamp).total_seconds())
    if delta > tolerance:
        raise AuthError(
            "Token scaduto: orario %s, differenza %d secondi"
            % (stamp.strftime(TOKEN_FMT), delta)
        )
    return stamp
