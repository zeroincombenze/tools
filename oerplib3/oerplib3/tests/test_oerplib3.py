# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.it>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""
    Oerplib3 Regression Test Suite
"""
import os
import sys

from configparser import ConfigParser

from zerobug import z0test
import oerplib3

__version__ = "1.0.0"

ODOO_VERSION_TO_TEST = ("7.0", "8.0")


def build_odoo_param(param, odoo_version, multi=True):
    odoo_major = int(odoo_version.split(".")[0])
    if param == "RPCPORT":
        return 8160 + odoo_major
    elif param == "LPPORT":
        return 8130 + odoo_major
    else:
        raise


def version():
    return __version__


class RegressionTest:

    def setup(self):
        print("Connection test: it works only if odoo instances are running!")
        self.test_data_dir = os.path.join(self.Z.testdir, 'res')
        if not os.path.isdir(self.test_data_dir):
            os.mkdir(self.test_data_dir)
        config = ConfigParser()
        default_confn = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'default-odoo.conf')
        )
        config.read(default_confn)
        if not config.has_section("options"):
            config.add_section("options")
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
                            build_odoo_param("RPCPORT", odoo_version, multi=True)
                        ),
                    ),
                    ("psycopg2", "1"),
                    ("svc_protocol", "xmlrpc"),
                    ("admin_password", "admin"),
                    ("tmp_database", "test_oerplib3_%d"),
                    ("admin_password", "admin"),
                )
            }
            if odoo_major >= 10:
                values["longpolling_port"] = str(
                    build_odoo_param("LPPORT", odoo_version, multi=True)
                )
            self.version_default[odoo_version] = values
            print(
                "  ... Odoo %s should be run on %s port with %s db_user!"
                % (
                    odoo_version,
                    values.get("http_port") or values["xmlrpc_port"],
                    values["db_user"],
                )
            )

    def test_01(self, z0ctx):
        sts = 0
        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            confn = os.path.join(self.test_data_dir, 'odoo%s.conf' % odoo_major)

            config = ConfigParser()
            config["options"] = {}
            config["options"].update(self.version_default[odoo_version])
            config.write(open(confn, "w"))
            self.odoo_cnx = oerplib3.OERP(
                server=self.version_default[odoo_version]["db_host"],
                protocol=self.version_default[odoo_version]["svc_protocol"],
                port=self.version_default[odoo_version]["xmlrpc_port"],
            )
            sts += self.Z.test_result(
                z0ctx,
                "Connect %s:%s/%s" % (
                    self.version_default[odoo_version]["db_host"],
                    self.version_default[odoo_version]["xmlrpc_port"],
                    odoo_version),
                odoo_version,
                ".".join(self.odoo_cnx.version.split(".")[:2]),
            )

            self.user = self.odoo_cnx.login(
                database=self.version_default[odoo_version]["db_name"],
                user=self.version_default[odoo_version]["login_user"],
                passwd=self.version_default[odoo_version]["password"],
            )
            sts += self.Z.test_result(
                z0ctx,
                "Login %s/%s/%s" % (
                    self.version_default[odoo_version]["db_name"],
                    self.version_default[odoo_version]["login_user"],
                    odoo_version),
                True,
                bool(self.user),
            )
        return sts

    def test_02(self, z0ctx):
        sts = 0
        resource = "res.partner"
        # partner_updated = "Test updated partner"
        # lang = "en_GB"

        for odoo_version in ODOO_VERSION_TO_TEST:
            ids = []
            if not z0ctx.get('dry_run', False):
                ids = self.odoo_cnx.search(resource, [])
            sts += self.Z.test_result(
                z0ctx, "(%s).search(%s, [])" % (odoo_version, resource),
                len(ids) > 0,
                True
            )
        return sts

    def test_03(self, z0ctx):
        sts = 0
        self.resource = "res.partner"
        self.ids = {}
        partner_name = "Test oerplib3"

        for odoo_version in ODOO_VERSION_TO_TEST:
            self.ids[odoo_version] = False
            if not z0ctx.get('dry_run', False):
                self.ids[odoo_version] = self.odoo_cnx.create(
                    self.resource, {"name": partner_name}
                )
            sts += self.Z.test_result(
                z0ctx, "(%s).create(%s, {})" % (odoo_version, self.resource),
                self.ids[odoo_version] > 0,
                True
            )
            ids = self.odoo_cnx.search(
                self.resource, [("id", "=", self.ids[odoo_version])]
            )
            sts += self.Z.test_result(
                z0ctx,
                "(%s).search(%s, [('id', '=', %s)])" % (odoo_version,
                                                        self.resource,
                                                        self.ids[odoo_version]),
                len(ids) > 0,
                True
            )

        return sts

    def test_04(self, z0ctx):
        sts = 0
        partner_name = "Test oerplib3"
        partner_updated = "Test updated partner"

        for odoo_version in ODOO_VERSION_TO_TEST:
            partner = None
            if not z0ctx.get('dry_run', False):
                partner = self.odoo_cnx.browse(self.resource, self.ids[odoo_version])
            sts += self.Z.test_result(
                z0ctx, "(%s).browse(%s, %s)" % (odoo_version,
                                                self.resource,
                                                self.ids[odoo_version]),
                partner.name if partner else partner,
                partner_name,
            )

            if not z0ctx.get('dry_run', False):
                self.odoo_cnx.write(
                    self.resource,
                    self.ids[odoo_version],
                    {"name": partner_updated},
                )
            if not z0ctx.get('dry_run', False):
                partner = self.odoo_cnx.browse(self.resource, self.ids[odoo_version])
            sts += self.Z.test_result(
                z0ctx,
                "(%s).write(%s, %s, {})" % (odoo_version,
                                            self.resource,
                                            self.ids[odoo_version]),
                partner.name if partner else partner,
                partner_updated,
            )

        return sts

    def test_05(self, z0ctx):
        sts = 0

        for odoo_version in ODOO_VERSION_TO_TEST:
            if not z0ctx.get('dry_run', False):
                self.odoo_cnx.unlink(self.resource, [self.ids[odoo_version]])
            ids = self.odoo_cnx.search(
                self.resource, [("id", "=", self.ids[odoo_version])]
            )
            sts += self.Z.test_result(
                z0ctx,
                "(%s).unlink(%s, [%s])" % (odoo_version,
                                           self.resource,
                                           self.ids[odoo_version]),
                [],
                ids,
            )

        return sts

    def test_06(self, z0ctx):
        sts = 0
        self.lang = "en_GB"
        wiz_resource = "base.language.install"
        resource = "lang_install"

        for odoo_version in ODOO_VERSION_TO_TEST:
            act = None
            if not z0ctx.get('dry_run', False):
                id = self.odoo_cnx.create(
                    wiz_resource,
                    {
                        "lang": self.lang,
                        "overwrite": False,
                    },
                )
                act = self.odoo_cnx.execute(
                    wiz_resource,
                    resource,
                    [id],
                )
            sts += self.Z.test_result(
                z0ctx,
                "(%s).lang_install(%s)" % (odoo_version, self.lang),
                isinstance(act, dict),
                True
            )

        wiz_resource = "base.update.translations"
        if not z0ctx.get('dry_run', False):
            id = self.odoo_cnx.create(
                wiz_resource,
                {
                    "lang": self.lang,
                },
            )
            act = self.odoo_cnx.execute(
                wiz_resource,
                "act_update",
                [id],
            )
        sts += self.Z.test_result(
            z0ctx,
            "(%s).lang.act_update(%s)" % (odoo_version, self.lang),
            isinstance(act, dict),
            True
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
