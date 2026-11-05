# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .db import Base

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S"


def fmt_datetime(value):
    return value.strftime(DATETIME_FMT) if value else None


class Document(Base):
    """One document stored in one Evolve archive.

    The same invoice has a row in the sent archive (staging) and, after SdI
    delivery, a row with the same Uid in the out archive (or in archive for
    self invoices).
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False, index=True)
    company_id = Column(Integer, nullable=False, index=True)
    archive = Column(Integer, nullable=False, index=True)
    number = Column(String(64), index=True)
    date = Column(String(19))
    td = Column(String(4))
    file_name = Column(String(128))
    file_bytes = Column(Text)
    file_hash = Column(String(64))
    xml_valid = Column(Boolean, default=True)
    loaded_at = Column(DateTime, default=datetime.now)
    sdi_state = Column(String(128))
    invoice_state = Column(String(128))
    note = Column(Text)
    sdi_id = Column(Integer)
    received_at = Column(DateTime)
    downloaded_at = Column(DateTime)
    # Workflow (sent archive rows): 0=staged, 1=at SdI, 2=done
    step = Column(Integer, default=2, nullable=False)
    next_step_at = Column(DateTime)
    outcome = Column(String(128))

    def campi_dinamici(self):
        """Evolve dynamic fields, as returned by Cerca / Salva / Recupera"""
        values = [
            ("Uid", self.uid),
            ("NumeroFattura", self.number),
            ("DataFattura", self.date),
            ("TipoDocumento", self.td),
            ("NomeFile", self.file_name),
            ("DataCaricamento", fmt_datetime(self.loaded_at)),
            ("StatoInvioSdi", self.sdi_state),
            ("StatoFattura", self.invoice_state),
            ("IdentificativoSdi", self.sdi_id),
            ("DataRicezione", fmt_datetime(self.received_at)),
            ("DataDownload", fmt_datetime(self.downloaded_at)),
            ("Note", self.note),
        ]
        return [{"Nome": k, "Valore": v} for k, v in values if v is not None]

    def to_evolve(self):
        return {
            "Uid": self.uid,
            "IdArchivio": self.archive,
            "CampiDinamici": self.campi_dinamici(),
        }

    def to_file(self):
        return {
            "Nome": self.file_name,
            "Bytes": self.file_bytes,
            "MimeType": "text/xml",
            "Extension": (self.file_name or ".XML").split(".")[-1].upper(),
            "Hash": self.file_hash,
        }

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "company_id": self.company_id,
            "archive": self.archive,
            "number": self.number,
            "date": self.date,
            "td": self.td,
            "file_name": self.file_name,
            "xml_valid": self.xml_valid,
            "loaded_at": fmt_datetime(self.loaded_at),
            "sdi_state": self.sdi_state,
            "invoice_state": self.invoice_state,
            "note": self.note,
            "sdi_id": self.sdi_id,
            "received_at": fmt_datetime(self.received_at),
            "downloaded_at": fmt_datetime(self.downloaded_at),
            "step": self.step,
            "next_step_at": fmt_datetime(self.next_step_at),
            "outcome": self.outcome,
        }
