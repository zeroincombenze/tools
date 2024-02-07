# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""
    Clodoo Regression Test Suite
"""
import os
import sys

# import time
from configparser import ConfigParser

# from datetime import datetime

from zerobug import z0test

try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = "2.0.9"

ODOO_VERSION_TO_TEST = ("16.0", "12.0", "10.0", "8.0", "7.0")


def version():
    return __version__


class RegressionTest:
    def __init__(self, zarlib):
        self.Z = zarlib

    def setup(self, z0ctx):
        print("Connection test: it works only if odoo instances are running!")
        self.test_data_dir = os.path.join(self.Z.testdir, 'res')
        if not os.path.isdir(self.test_data_dir):
            os.mkdir(self.test_data_dir)
        config = ConfigParser()
        default_confn = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'default-odoo.conf')
        )
        config.read(default_confn)
        self.version_ctx = {}
        self.version_default = {}
        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            values = {
                param: config["options"].get("%s%d" % (param, odoo_major))
                or (val % odoo_major if "%" in val else val)
                for (param, val) in (
                    ("oe_version", odoo_version),
                    ("db_host", "localhost"),
                    ("db_port", "False"),
                    ("db_template", "template1"),
                    ("db_user", "odoo%d"),
                    ("login_user", "admin"),
                    ("password", "admin"),
                    ("db_name", "test%d"),
                    (
                        "xmlrpc_port" if odoo_major < 10 else "http_port",
                        str(
                            clodoo.build_odoo_param("RPCPORT", odoo_version, multi=True)
                        ),
                    ),
                    ("psycopg2", "1"),
                    ("svc_protocol", "xmlrpc" if odoo_major < 10 else "jsonrpc"),
                    ("admin_password", "admin"),
                    ("tmp_database", "test_clodoo_%d"),
                    ("admin_password", "admin"),
                )
            }
            if odoo_major >= 10:
                values["longpolling_port"] = str(
                    clodoo.build_odoo_param("LPPORT", odoo_version, multi=True)
                )
            self.version_default[odoo_version] = values
            print(
                "  ... Odoo %s should be run on %s:%s, DB=%s for %s login user!"
                % (
                    odoo_version,
                    values["db_host"],
                    values.get("http_port") or values["xmlrpc_port"],
                    values["db_name"],
                    values["login_user"],
                )
            )

    def test_01(self, z0ctx):
        sts = 0
        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = self.version_default[odoo_version]["db_name"]
            confn = os.path.join(self.test_data_dir, 'odoo%s.conf' % odoo_major)
            if not z0ctx.get('dry_run', False):
                config = ConfigParser()
                config["options"] = {}
                config["options"].update(self.version_default[odoo_version])
                config.write(open(confn, "w"))
            uid, ctx = clodoo.oerp_set_env(ctx={}, confn=confn, db=database)
            self.version_ctx[odoo_version] = ctx
            sts += self.Z.test_result(
                z0ctx,
                "Connect %s/%s (pypi: %s)" % (database, odoo_version, ctx["pypi"]),
                uid > 0,
                True,
            )
        return sts

    def test_02(self, z0ctx):
        sts = 0
        resource = "res.partner"
        partner_name = "Test clodoo"
        partner_updated = "Test updated partner"
        lang = "en_GB"

        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = self.version_default[odoo_version]["db_name"]
            ids = []
            if not z0ctx.get('dry_run', False):
                ids = clodoo.searchL8(self.version_ctx[odoo_version], resource, [])
            sts += self.Z.test_result(
                z0ctx, "(%s) SearchL8 %s" % (odoo_version, database), len(ids) > 0, True
            )

            id = False
            if not z0ctx.get('dry_run', False):
                id = clodoo.createL8(
                    self.version_ctx[odoo_version], resource, {"name": partner_name}
                )
            sts += self.Z.test_result(
                z0ctx, "    CreateL8 %s" % database, len(ids) > 0, True
            )
            ids = clodoo.searchL8(
                self.version_ctx[odoo_version], resource, [("id", "=", id)]
            )
            sts += self.Z.test_result(
                z0ctx, "    SearchL8 %s" % database, len(ids) > 0, True
            )

            partner = None
            if not z0ctx.get('dry_run', False):
                partner = clodoo.browseL8(self.version_ctx[odoo_version], resource, id)
            sts += self.Z.test_result(
                z0ctx,
                "    BrowseL8 %s" % database,
                partner.name if partner else partner,
                partner_name,
            )

            if not z0ctx.get('dry_run', False):
                clodoo.writeL8(
                    self.version_ctx[odoo_version],
                    resource,
                    id,
                    {"name": partner_updated},
                )
            sts += self.Z.test_result(
                z0ctx,
                "    WriteL8 %s" % database,
                clodoo.browseL8(self.version_ctx[odoo_version], resource, id).name,
                partner_updated,
            )

            if not z0ctx.get('dry_run', False):
                clodoo.unlinkL8(self.version_ctx[odoo_version], resource, id)
                ids = clodoo.searchL8(
                    self.version_ctx[odoo_version], resource, [("id", "=", id)]
                )
            sts += self.Z.test_result(z0ctx, "    UnlinkL8 %s" % database, ids, [])

            if not z0ctx.get('dry_run', False):
                ids = clodoo.searchL8(
                    self.version_ctx[odoo_version], "res.lang", [("code", "=", lang)]
                )
                if not ids:
                    ids = clodoo.searchL8(
                        self.version_ctx[odoo_version],
                        "res.lang",
                        [("code", "=", lang), ("active", "=", False)],
                    )
                if odoo_major >= 16:
                    id = clodoo.createL8(
                        self.version_ctx[odoo_version],
                        "base.language.install",
                        {
                            "lang_ids": ids,
                            "overwrite": False,
                        },
                    )
                else:
                    id = clodoo.createL8(
                        self.version_ctx[odoo_version],
                        "base.language.install",
                        {
                            "lang": lang,
                            "overwrite": False,
                        },
                    )
                act = clodoo.executeL8(
                    self.version_ctx[odoo_version],
                    "base.language.install",
                    "lang_install",
                    [id],
                )
                sts += self.Z.test_result(
                    z0ctx, "    lang_install(%s)" % ids, isinstance(act, dict), True
                )

                if odoo_major < 10:
                    id = clodoo.createL8(
                        self.version_ctx[odoo_version],
                        "base.update.translations",
                        {
                            "lang": lang,
                        },
                    )
                    act = clodoo.executeL8(
                        self.version_ctx[odoo_version],
                        "base.update.translations",
                        "act_update",
                        [id],
                    )
                    sts += self.Z.test_result(
                        z0ctx,
                        "    lang.act_update(%s)" % ids,
                        isinstance(act, dict),
                        True,
                    )
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )


