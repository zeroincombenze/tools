# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
import os

from evolve_simulator.app import create_app
from evolve_simulator.scripts import main as main_mod

from .conftest import CLIENT_ID, CLIENT_KEY, COMPANY_ID, xml_invoice


def test_filestore(tmp_path):
    (tmp_path / "IT01234567890_A0001.xml").write_bytes(xml_invoice("A/0001"))
    (tmp_path / "notes.txt").write_text("skip me")
    app = create_app(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "CLIENT_ID": CLIENT_ID,
            "CLIENT_KEY": CLIENT_KEY,
            "COMPANY_ID": COMPANY_ID,
            "FILESTORE": str(tmp_path),
            "TESTING": True,
        }
    )
    client = app.test_client()
    docs = client.get("/sim/api/documents?archive=2").get_json()
    assert len(docs) == 1
    assert docs[0]["number"] == "A/0001"
    assert docs[0]["file_name"] == "IT01234567890_A0001.xml"
    assert docs[0]["company_id"] == COMPANY_ID
    assert docs[0]["date"] == "2026-11-04T00:00:00"
    assert not (tmp_path / "IT01234567890_A0001.xml").exists()
    assert (tmp_path / "done" / "IT01234567890_A0001.xml").exists()
    assert (tmp_path / "notes.txt").exists()
    # Moved files are not imported again
    assert len(client.get("/sim/api/documents?archive=2").get_json()) == 1
    assert client.get("/sim/api/settings").get_json()["FILESTORE"] == str(tmp_path)


def test_pid_file(tmp_path, monkeypatch):
    pid_file = tmp_path / "evolve.pid"
    registered = []
    monkeypatch.setattr(main_mod.atexit, "register", registered.append)
    main_mod.write_pid_file(str(pid_file))
    assert pid_file.read_text().strip() == str(os.getpid())
    registered[0]()
    assert not pid_file.exists()


def test_bad_filestore(tmp_path):
    assert main_mod.main(["--filestore", str(tmp_path / "missing")]) == 1
