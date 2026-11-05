# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""Simulated SdI workflow.

A document saved in the sent archive goes through:
  step 0  staged: "Il documento è in fase di invio"
  step 1  after SDI_DELAY: delivered to SdI, a row with the same Uid is
          created in the out archive (in archive for self invoices)
          with state "Inviato"
  step 2  after OUTCOME_DELAY: the out row gets the final outcome
Steps are processed lazily, when any request reaches the server.
"""

import hashlib
import os
import uuid
from base64 import b64encode
from datetime import datetime, timedelta

from .models import Client, Document
from .xmlinfo import normalize_date, parse_invoice

STATE_STAGED = "Il documento è in fase di invio"
STATE_AT_SDI = "Inviata a Sdi"
STATE_SENT = "Inviato"
STATE_INVALID = "Il documento non ha superato i controlli di validazione"
STATE_DISCARD = "Notifica di scarto"
STATE_RECEIVED = "Ricevuta"
SELF_INVOICE_TD = ("TD17", "TD18", "TD19")

# Final outcomes with the note SdI usually attaches
OUTCOMES = {
    "Ricevuta di consegna": "Fattura consegnata al destinatario",
    "Notifica di scarto": "00305 - IdFiscaleIVA del CessionarioCommittente non valido",
    "Notifica di mancata consegna": (
        "Fattura non consegnata: disponibile in consultazione nell'area riservata"
    ),
    "Notifica di esito: documento accettato": "Fattura accettata dalla PA",
    "Notifica di esito: documento rifiutato dalla PA": "Fattura rifiutata dalla PA",
    "Notifica di decorrenza termini": "Decorsi i termini senza esito dalla PA",
    "Errore": "Errore interno del sistema di interscambio",
}


def target_archive(config, doc):
    if doc.td in SELF_INVOICE_TD:
        return config["ARCHIVE_IN"]
    return config["ARCHIVE_OUT"]


def delivered_row(db, doc):
    return (
        db.query(Document)
        .filter(Document.uid == doc.uid, Document.id != doc.id)
        .first()
    )


def _is_duplicate(db, archive, doc):
    return (
        db.query(Document)
        .filter(
            Document.archive == archive,
            Document.company_id == doc.company_id,
            Document.number == doc.number,
            Document.uid != doc.uid,
            Document.invoice_state != STATE_DISCARD,
        )
        .count()
        > 0
    )


def _to_sdi(db, config, doc, now):
    if not doc.xml_valid:
        doc.sdi_state = STATE_INVALID
        doc.note = "File XML non conforme al tracciato FatturaPA"
        doc.step = 2
        doc.next_step_at = None
        return
    archive = target_archive(config, doc)
    if _is_duplicate(db, archive, doc):
        doc.outcome = STATE_DISCARD
        doc.note = "Fattura duplicata"
    out = Document(
        uid=doc.uid,
        company_id=doc.company_id,
        archive=archive,
        number=doc.number,
        date=doc.date,
        td=doc.td,
        file_name=doc.file_name,
        file_bytes=doc.file_bytes,
        file_hash=doc.file_hash,
        xml_valid=doc.xml_valid,
        loaded_at=now,
        invoice_state=STATE_SENT,
        received_at=now if archive == config["ARCHIVE_IN"] else None,
        step=2,
    )
    db.add(out)
    db.flush()
    out.sdi_id = 10000000 + out.id
    doc.sdi_state = STATE_AT_SDI
    doc.sdi_id = out.sdi_id
    doc.step = 1
    doc.next_step_at = now + timedelta(seconds=config["OUTCOME_DELAY"])


def _set_outcome(db, config, doc, now):
    outcome = doc.outcome or config["DEFAULT_OUTCOME"]
    out = delivered_row(db, doc)
    if out:
        out.invoice_state = outcome
        out.note = doc.note if doc.note else OUTCOMES.get(outcome, "")
    doc.step = 2
    doc.next_step_at = None


def advance_document(db, config, doc, now=None):
    """Run the next workflow step of one document; return True if done"""
    now = now or datetime.now()
    if doc.step == 0:
        _to_sdi(db, config, doc, now)
    elif doc.step == 1:
        _set_outcome(db, config, doc, now)
    else:
        return False
    return True


def inbound_document(db, config, content, file_name=None, company_id=None, now=None):
    """Put a purchase invoice in the in archive, as received from SdI"""
    now = now or datetime.now()
    file_name = file_name or "IT00000000000_%s.xml" % uuid.uuid4().hex[:5]
    info = parse_invoice(content, file_name)
    if not company_id:
        client = db.query(Client).first()
        company_id = client.company_id if client else 1
    doc = Document(
        uid=uuid.uuid4().hex,
        company_id=int(company_id),
        archive=config["ARCHIVE_IN"],
        number=info["number"],
        date=normalize_date(info["date"]),
        td=info["td"],
        file_name=file_name,
        file_bytes=b64encode(content).decode("ascii"),
        file_hash=hashlib.sha256(content).hexdigest(),
        xml_valid=info["valid"],
        loaded_at=now,
        received_at=now,
        invoice_state=STATE_RECEIVED,
        step=2,
    )
    db.add(doc)
    return doc


def scan_filestore(db, config, now=None):
    """Import every xml file of FILESTORE as inbound invoice.

    Imported files are moved into the "done" sub-directory;
    return the number of files imported.
    """
    path = config.get("FILESTORE")
    if not path or not os.path.isdir(path):
        return 0
    done = os.path.join(path, "done")
    count = 0
    for name in sorted(os.listdir(path)):
        full_name = os.path.join(path, name)
        if not name.lower().endswith(".xml") or not os.path.isfile(full_name):
            continue
        try:
            with open(full_name, "rb") as fd:
                content = fd.read()
            if not os.path.isdir(done):
                os.makedirs(done)
            os.replace(full_name, os.path.join(done, name))
        except OSError:
            continue
        inbound_document(db, config, content, file_name=name, now=now)
        count += 1
    return count


def advance(db, config, now=None):
    """Run every workflow step that is due; return the number of steps run.

    Inbound xml files of FILESTORE are imported first.
    """
    now = now or datetime.now()
    count = scan_filestore(db, config, now=now)
    while True:
        due = (
            db.query(Document)
            .filter(Document.step < 2, Document.next_step_at <= now)
            .order_by(Document.id)
            .all()
        )
        if not due:
            break
        for doc in due:
            if advance_document(db, config, doc, now=now):
                count += 1
        # Session has no autoflush: write steps before querying again
        db.flush()
    if count:
        db.commit()
    return count


def stage(config, now=None):
    """Values of a new document saved in the sent archive"""
    now = now or datetime.now()
    return {
        "loaded_at": now,
        "sdi_state": STATE_STAGED,
        "step": 0,
        "next_step_at": now + timedelta(seconds=config["SDI_DELAY"]),
    }
