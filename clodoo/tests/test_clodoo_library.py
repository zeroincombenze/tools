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

ODOO_VERSION_TO_TEST = ("12.0", "10.0", "8.0", "7.0", "14.0")


def version():
    return __version__


class RegressionTest:
    def setup(self):
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
                    ("login_password", "admin"),
                    ("db_name", "test%d"),
                    (
                        "xmlrpc_port" if odoo_major < 10 else "http_port",
                        str(
                            clodoo.build_odoo_param("RPCPORT", odoo_version, multi=True)
                        ),
                    ),
                    ("psycopg2", "1"),
                    ("protocol", "xmlrpc" if odoo_major < 10 else "jsonrpc"),
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
        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = self.version_default[odoo_version]["db_name"]
            confn = os.path.join(self.test_data_dir, 'odoo%s.conf' % odoo_major)

            config = ConfigParser()
            config["options"] = {}
            config["options"].update({
                k: v
                for (k, v) in self.version_default[odoo_version].items()
                if k not in ("db_name", "protocol")
            })
            config.write(open(confn, "w"))
            uid, ctx = clodoo.oerp_set_env(ctx={}, confn=confn, db=database)
            self.version_ctx[odoo_version] = ctx
            self.assertTrue(
                uid > 0,
                msg_info="Connect DB=%s (version=%s pypi=%s)" % (database,
                                                                 odoo_version,
                                                                 ctx["pypi"]))

    def test_02(self):
        resource = "res.partner"
        partner_name = "Test clodoo"
        partner_updated = "Test updated partner"
        res_lang = "res.lang"
        lang = "en_GB"
        res_lang_xtl = "base.language.install"
        res_lang_upd = "base.update.translations"

        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = self.version_default[odoo_version]["db_name"]
            margin = " " * (len(database) + len(odoo_version) + 1)
            ids = clodoo.searchL8(self.version_ctx[odoo_version], resource, [])
            self.assertTrue(
                len(ids) > 1,
                msg_info="%s/%s> searchL8(%s)" % (database, odoo_version, resource))

            id = clodoo.createL8(
                self.version_ctx[odoo_version], resource, {"name": partner_name}
            )
            self.assertTrue(
                id > 0,
                msg_info="%s> createL8(%s, ...)" % (margin, resource))

            ids = clodoo.searchL8(
                self.version_ctx[odoo_version], resource, [("id", "=", id)]
            )
            self.assertTrue(
                len(ids) == 1,
                msg_info="%s> searchL8(%s, %d)" % (margin, resource, id))

            partner = clodoo.browseL8(self.version_ctx[odoo_version], resource, id)
            self.assertEqual(
                partner.name if partner else partner,
                partner_name,
                msg_info="%s> browseL8(%s, %d)" % (margin, resource, id)
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
                msg_info="%s> writeL8(%s, %d, ...)" % (margin, resource, id)
            )

            clodoo.unlinkL8(self.version_ctx[odoo_version], resource, id)
            ids = clodoo.searchL8(
                self.version_ctx[odoo_version], resource, [("id", "=", id)]
            )
            self.assertEqual(
                ids,
                [],
                msg_info="%s> unlinkL8(%s, [%d])" % (margin, resource, id)
            )

            ids = clodoo.searchL8(
                self.version_ctx[odoo_version],
                res_lang,
                [("code", "=", lang)]
            )
            if not ids:
                ids = clodoo.searchL8(
                    self.version_ctx[odoo_version],
                    res_lang,
                    [("code", "=", lang), ("active", "=", False)],
                )
            if odoo_major == 7:
                continue
            elif odoo_major >= 16:
                id = clodoo.createL8(
                    self.version_ctx[odoo_version],
                    res_lang_xtl,
                    {
                        "lang_ids": ids,
                        "overwrite": False,
                    },
                )
            else:
                id = clodoo.createL8(
                    self.version_ctx[odoo_version],
                    res_lang_xtl,
                    {
                        "lang": lang,
                        "overwrite": False,
                    },
                )
            act = clodoo.executeL8(
                self.version_ctx[odoo_version],
                res_lang_xtl,
                "lang_install",
                [id],
            )
            self.assertTrue(
                isinstance(act, dict),
                msg_info="%s> execute(%s, lang_install, %d)" % (margin,
                                                                res_lang_xtl,
                                                                id)
            )

            if odoo_major < 10:
                id = clodoo.createL8(
                    self.version_ctx[odoo_version],
                    res_lang_upd,
                    {
                        "lang": lang,
                    },
                )
                act = clodoo.executeL8(
                    self.version_ctx[odoo_version],
                    res_lang_upd,
                    "act_update",
                    [id],
                )
                self.assertTrue(
                    isinstance(act, dict),
                    msg_info="%s> execute(%s, act_update, %d)" % (margin,
                                                                  res_lang_upd,
                                                                  id)
                )

    def test_03(self):
        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = self.version_default[odoo_version]["db_name"]
            confn = os.path.join(self.test_data_dir, 'odoo%s.conf' % odoo_major)

            odoo = clodoo.Clodoo(confn=confn, db_name=database)
            self.version_ctx[odoo_version] = odoo
            self.assertTrue(
                odoo,
                msg_info="Connect DB=%s (version=%s pypi=%s)" % (database,
                                                                 odoo_version,
                                                                 odoo.pypi))

    def test_04(self):
        resource = "res.partner"
        partner_name = "Test clodoo"
        partner_updated = "Test updated partner"

        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            if odoo_major < 10:
                continue
            database = self.version_default[odoo_version]["db_name"]
            margin = " " * (len(database) + len(odoo_version) + 1)
            Partner = self.version_ctx[odoo_version].env[resource]
            ids = Partner.search([])
            self.assertTrue(
                len(ids) > 1,
                msg_info="%s/%s> %s.search()" % (database, odoo_version, resource))

            id = Partner.create({"name": partner_name})
            self.assertTrue(
                id > 0,
                msg_info="%s> %s.create(...)" % (margin, resource))

            ids = Partner.search([("id", "=", id)])
            self.assertTrue(
                len(ids) == 1,
                msg_info="%s> %ssearch(%d)" % (margin, resource, id))

            Partner.write(id, {"name": partner_updated})
            self.assertEqual(
                Partner.browse(id).name,
                partner_updated,
                msg_info="%s> %s.write(%d, ...)" % (margin, resource, id)
            )

            Partner.unlink(id)
            ids = Partner.search([("id", "=", id)])
            self.assertEqual(
                ids,
                [],
                msg_info="%s> %s.unlink(%d)" % (margin, resource, id)
            )


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
