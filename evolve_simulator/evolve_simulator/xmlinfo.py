# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""Minimal FatturaPA reader: get document type, number and date"""

import xml.etree.ElementTree as ET


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def parse_invoice(content, file_name=""):
    """Return dict(valid, td, number, date) of a FatturaPA xml content.

    Signed files (.p7m) cannot be read and are assumed valid.
    """
    res = {"valid": True, "td": None, "number": None, "date": None}
    if (file_name or "").lower().endswith(".p7m"):
        return res
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        res["valid"] = False
        return res
    if _local(root.tag) != "FatturaElettronica":
        res["valid"] = False
        return res
    for elem in root.iter():
        if _local(elem.tag) == "DatiGeneraliDocumento":
            for child in elem:
                name = _local(child.tag)
                if name == "TipoDocumento":
                    res["td"] = (child.text or "").strip()
                elif name == "Numero":
                    res["number"] = (child.text or "").strip()
                elif name == "Data":
                    res["date"] = (child.text or "").strip()
            break
    return res


def normalize_date(value):
    """Return value as "%Y-%m-%dT%H:%M:%S" (Odoo sends "%Y-%m-%d")"""
    if not value:
        return None
    value = str(value).strip().replace(" ", "T")
    if len(value) == 10:
        value += "T00:00:00"
    return value[:19]
