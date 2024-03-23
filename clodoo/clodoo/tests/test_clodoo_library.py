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

from configparser import ConfigParser

from zerobug import z0test

try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = "2.0.9"

ODOO_VERSION_TO_TEST = ("12.0", "10.0", "8.0")


def version():
    return __version__


class RegressionTest:
    # def __init__(self, zarlib):
    #     self.Z = zarlib

    def setup(self):
        # print("Connection test: it works only if odoo instances are running!")
        os.system(os.path.join(os.path.dirname(__file__), "before_test.sh"))
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

    def test_01(self):
        sts = 0
        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = self.version_default[odoo_version]["db_name"]
            confn = os.path.join(self.test_data_dir, 'odoo%s.conf' % odoo_major)

            config = ConfigParser()
            config["options"] = {}
            config["options"].update(self.version_default[odoo_version])
            config.write(open(confn, "w"))
            uid, ctx = clodoo.oerp_set_env(ctx={}, confn=confn, db=database)
            self.version_ctx[odoo_version] = ctx
            self.assertTrue(
                uid > 0,
                msg_info="Connect %s/%s (pypi: %s)" % (database,
                                                       odoo_version,
                                                       ctx["pypi"]))
        return sts

    def test_02(self):
        sts = 0
        resource = "res.partner"
        partner_name = "Test clodoo"
        partner_updated = "Test updated partner"
        lang = "en_GB"

        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = self.version_default[odoo_version]["db_name"]
            ids = clodoo.searchL8(self.version_ctx[odoo_version], resource, [])
            self.assertTrue(
                len(ids) > 0,
                msg_info="(%s) SearchL8 %s" % (odoo_version, database))

            id = clodoo.createL8(
                self.version_ctx[odoo_version], resource, {"name": partner_name}
            )
            self.assertTrue(id > 0, msg_info="    CreateL8 %s" % database)

            ids = clodoo.searchL8(
                self.version_ctx[odoo_version], resource, [("id", "=", id)]
            )
            self.assertTrue(len(ids) > 0, msg_info="    SearchL8 %s" % database)

            partner = clodoo.browseL8(self.version_ctx[odoo_version], resource, id)
            self.assertEqual(
                partner.name if partner else partner,
                partner_name,
                msg_info="    BrowseL8 %s" % database,
            )

            clodoo.writeL8(
                self.version_ctx[odoo_version],
                resource,
                id,
                {"name": partner_updated},
            )
            self.assertEqual(
                clodoo.browseL8(self.version_ctx[odoo_version], resource, id).name,
                partner_updated,
                msg_info="    WriteL8 %s" % database,
            )

            clodoo.unlinkL8(self.version_ctx[odoo_version], resource, id)
            ids = clodoo.searchL8(
                self.version_ctx[odoo_version], resource, [("id", "=", id)]
            )
            self.assertEqual(
                ids,
                [],
                msg_info="    UnlinkL8 %s" % database,
            )

            ids = clodoo.searchL8(
                self.version_ctx[odoo_version],
                "res.lang",
                [("code", "=", lang)]
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
            self.assertTrue(isinstance(act, dict),
                            msg_info="    lang_install(%s)" % ids)

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
                self.assertTrue(isinstance(act, dict),
                                msg_info="    lang.act_update(%s)" % ids)

        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
