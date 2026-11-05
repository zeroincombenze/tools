# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
import os


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() not in ("0", "false", "no", "off", "")


class Config(object):
    """Default settings; every key can be overridden by an EVOLVE_SIM_<KEY> env var"""

    DATABASE_URL = os.getenv(
        "EVOLVE_SIM_DATABASE_URL",
        "sqlite:///%s" % os.path.join(os.getcwd(), "evolve_simulator.db"),
    )
    # REST endpoints prefix: Odoo "Sender URL" is http://<host>:<port><API_PREFIX>/
    API_PREFIX = os.getenv("EVOLVE_SIM_API_PREFIX", "/rest/api/v1")
    # Credentials seeded at start-up (Odoo: Client ID / Client Key / Company ID)
    CLIENT_ID = os.getenv("EVOLVE_SIM_CLIENT_ID", "test.odoo@zeroincombenze.it")
    CLIENT_KEY = os.getenv("EVOLVE_SIM_CLIENT_KEY", "0123456789abcdef0123456789abcdef")
    COMPANY_ID = _env_int("EVOLVE_SIM_COMPANY_ID", 93)
    # Authentication: check Bearer token and accept clock skew of AUTH_TOLERANCE secs
    AUTH_CHECK = _env_bool("EVOLVE_SIM_AUTH_CHECK", True)
    AUTH_TOLERANCE = _env_int("EVOLVE_SIM_AUTH_TOLERANCE", 300)
    # Archives (same defaults of Odoo SdI channel)
    ARCHIVE_OUT = _env_int("EVOLVE_SIM_ARCHIVE_OUT", 1)
    ARCHIVE_IN = _env_int("EVOLVE_SIM_ARCHIVE_IN", 2)
    ARCHIVE_SENT = _env_int("EVOLVE_SIM_ARCHIVE_SENT", 3)
    # SdI workflow: seconds before delivery to SdI and before final outcome
    SDI_DELAY = _env_int("EVOLVE_SIM_SDI_DELAY", 10)
    OUTCOME_DELAY = _env_int("EVOLVE_SIM_OUTCOME_DELAY", 60)
    DEFAULT_OUTCOME = os.getenv("EVOLVE_SIM_DEFAULT_OUTCOME", "Ricevuta di consegna")
    # Directory scanned for xml files to receive as inbound invoices ("" = none)
    FILESTORE = os.getenv("EVOLVE_SIM_FILESTORE", "")
    # Fault injection: "" (none), "http500", "esito1" (generic error), "auth"
    FAULT = os.getenv("EVOLVE_SIM_FAULT", "")


# Settings changeable at run time by simulator API / web page
RUNTIME_SETTINGS = {
    "AUTH_CHECK": bool,
    "AUTH_TOLERANCE": int,
    "SDI_DELAY": int,
    "OUTCOME_DELAY": int,
    "DEFAULT_OUTCOME": str,
    "FAULT": str,
}
FAULTS = ("", "http500", "esito1", "auth")
