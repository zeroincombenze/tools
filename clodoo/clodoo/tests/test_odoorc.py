# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""
    Clodoo Regression Test Suite
"""

# import pdb
import os
import sys
import re

from zerobug import z0test

try:
    from clodoo.clodoolib import build_odoo_param
except BaseException:
    from clodoolib import build_odoo_param


__version__ = "2.0.9"


MODULE_ID = "clodoo"
VERSIONS_TO_TEST = ["14.0", "13.0", "12.0", "11.0", "10.0", "9.0", "8.0", "7.0", "6.1"]
MAJVERS_TO_TEST = ["14", "13", "12", "11", "10", "9", "8", "7", "6"]
# VERSIONS_TO_TEST = ('7.0',)
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, testlib):
        self.Z = testlib

    def test_01(self, z0ctx):
        TRES = {
            "6": "6.1",
            "7": "7.0",
            "8": "8.0",
            "9": "9.0",
            "10": "10.0",
            "11": "11.0",
            "12": "12.0",
            "13": "13.0",
            "14": "14.0",
        }
        for ver in MAJVERS_TO_TEST:
            res = build_odoo_param("FULLVER", odoo_vid=ver)
            sts = self.Z.test_result(
                z0ctx, "Full version %s [python]" % ver, TRES[ver], res
            )
            if sts:
                break

            res = build_odoo_param("FULLVER", odoo_vid="v%s" % ver)
            sts = self.Z.test_result(
                z0ctx, "Full version v%s [python]" % ver, TRES[ver], res
            )
            if sts:
                break

            res = build_odoo_param("FULLVER", odoo_vid=TRES[ver])
            sts = self.Z.test_result(
                z0ctx, "Full version %s [python]" % TRES[ver], TRES[ver], res
            )
            if sts:
                break

            res = build_odoo_param("FULLVER", odoo_vid="v%s" % TRES[ver])
            sts = self.Z.test_result(
                z0ctx, "Full version v%s [python]" % TRES[ver], TRES[ver], res
            )
            if sts:
                break

            res = build_odoo_param("FULLVER", odoo_vid="V%s" % TRES[ver])
            sts = self.Z.test_result(
                z0ctx, "Full version V%s [python]" % TRES[ver], TRES[ver], res
            )
            if sts:
                break

            res = build_odoo_param("FULLVER", odoo_vid="VENV-%s" % TRES[ver])
            sts = self.Z.test_result(
                z0ctx, "Full version VENV-%s [python]" % TRES[ver], TRES[ver], res
            )
            if sts:
                break

            sts = self.Z.test_result(
                z0ctx, "Full version odoo-%s [python]" % TRES[ver], TRES[ver], res
            )
            if sts:
                break

            sts = self.Z.test_result(
                z0ctx, "Full version ODOO-%s [python]" % TRES[ver], TRES[ver], res
            )
            if sts:
                break
        return sts

    def test_02(self, z0ctx):
        TRES = {
            "6.1": 6,
            "7.0": 7,
            "8.0": 8,
            "9.0": 9,
            "10.0": 10,
            "11.0": 11,
            "12.0": 12,
            "13.0": 13,
            "14.0": 14,
        }
        for ver in VERSIONS_TO_TEST:
            res = build_odoo_param("MAJVER", odoo_vid=ver)
            sts = self.Z.test_result(
                z0ctx, "major version %s [python]" % ver, TRES[ver], res
            )
            if sts:
                break

            w = "V%s" % ver
            res = build_odoo_param("MAJVER", odoo_vid=w)
            sts = self.Z.test_result(
                z0ctx, "major version %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

            w = "OCB-%s" % ver
            res = build_odoo_param("MAJVER", odoo_vid=w)
            sts = self.Z.test_result(
                z0ctx, "major version %s [python]" % w, TRES[ver], res
            )
            if sts:
                break
        return sts

    def test_03(self, z0ctx):
        TRES = {
            "6": "/etc/odoo/openerp-server.conf",
            "7": "/etc/odoo/odoo-server.conf",
            "8": "/etc/odoo/odoo-server.conf",
            "9": "/etc/odoo/odoo-server.conf",
            "10": "/etc/odoo/odoo.conf",
            "11": "/etc/odoo/odoo.conf",
            "12": "/etc/odoo/odoo.conf",
            "13": "/etc/odoo/odoo.conf",
            "14": "/etc/odoo/odoo.conf",
            "v7": "/etc/odoo/openerp-server.conf",
        }
        for ver in MAJVERS_TO_TEST:
            res = build_odoo_param("CONFN", odoo_vid=ver)
            sts = self.Z.test_result(
                z0ctx, "config unique filename %s [python]" % ver, TRES[ver], res
            )
            if sts:
                break

            w = "VENV-%s" % ver
            res = build_odoo_param("CONFN", odoo_vid=w)
            sts = self.Z.test_result(
                z0ctx, "config unique filename %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        for ver in MAJVERS_TO_TEST + ["v7"]:
            if ver == "v7":
                w = ver
            elif ver == "6":
                w = "%s.1" % ver
            else:
                w = "%s.0" % ver
            res = build_odoo_param("CONFN", odoo_vid=w)
            sts = self.Z.test_result(
                z0ctx, "config unique filename %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        return sts

    def test_04(self, z0ctx):
        TRES = {
            "6": "/etc/odoo/odoo6-server.conf",
            "7": "/etc/odoo/odoo7-server.conf",
            "8": "/etc/odoo/odoo8-server.conf",
            "9": "/etc/odoo/odoo9-server.conf",
            "10": "/etc/odoo/odoo10.conf",
            "11": "/etc/odoo/odoo11.conf",
            "12": "/etc/odoo/odoo12.conf",
            "13": "/etc/odoo/odoo13.conf",
            "14": "/etc/odoo/odoo14.conf",
            "v7": "/etc/odoo/openerp-server.conf",
        }
        for ver in MAJVERS_TO_TEST:
            if ver == "6":
                continue
            res = build_odoo_param("CONFN", odoo_vid=ver, multi=True)
            sts = self.Z.test_result(
                z0ctx, "config multi filename %s [python]" % ver, TRES[ver], res
            )
            if sts:
                break

            w = "VENV-%s" % ver
            res = build_odoo_param("CONFN", odoo_vid=w, multi=True)
            sts = self.Z.test_result(
                z0ctx, "config multi filename %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        for ver in MAJVERS_TO_TEST + ["v7"]:
            if ver == "v7":
                w = ver
            elif ver == "6":
                # w = "%s.1" % ver
                continue
            else:
                w = "%s.0" % ver
            res = build_odoo_param("CONFN", odoo_vid=w, multi=True)
            sts = self.Z.test_result(
                z0ctx, "config multi filename %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        TRES = {
            "6": "/var/log/odoo/odoo6-server.log",
            "7": "/var/log/odoo/odoo7-server.log",
            "8": "/var/log/odoo/odoo8-server.log",
            "9": "/var/log/odoo/odoo9-server.log",
            "10": "/var/log/odoo/odoo10.log",
            "11": "/var/log/odoo/odoo11.log",
            "12": "/var/log/odoo/odoo12.log",
            "13": "/var/log/odoo/odoo13.log",
            "14": "/var/log/odoo/odoo14.log",
            "v7": "/var/log/odoo/openerp-server.log",
        }
        for ver in MAJVERS_TO_TEST + ["v7"]:
            if ver == "v7":
                w = ver
            elif ver == "6":
                # w = "%s.1" % ver
                continue
            else:
                w = "%s.0" % ver
            res = build_odoo_param("FLOG", odoo_vid=w, multi=True)
            sts = self.Z.test_result(
                z0ctx, "log filename %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        TRES = {
            "6": "/var/run/odoo/odoo6-server.pid",
            "7": "/var/run/odoo/odoo7-server.pid",
            "8": "/var/run/odoo/odoo8-server.pid",
            "9": "/var/run/odoo/odoo9-server.pid",
            "10": "/var/run/odoo/odoo10.pid",
            "11": "/var/run/odoo/odoo11.pid",
            "12": "/var/run/odoo/odoo12.pid",
            "13": "/var/run/odoo/odoo13.pid",
            "14": "/var/run/odoo/odoo14.pid",
            "v7": "/var/run/odoo/openerp-server.pid",
        }

        for ver in MAJVERS_TO_TEST + ["v7"]:
            if ver == "v7":
                w = ver
            elif ver == "6":
                # w = "%s.1" % ver
                continue
            else:
                w = "%s.0" % ver
            res = build_odoo_param("FPID", odoo_vid=w, multi=True)
            sts = self.Z.test_result(
                z0ctx, "pid filename %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        TRES = {
            "6": "/etc/init.d/odoo6-server",
            "7": "/etc/init.d/odoo7-server",
            "8": "/etc/init.d/odoo8-server",
            "9": "/etc/init.d/odoo9-server",
            "10": "/etc/init.d/odoo10",
            "11": "/etc/init.d/odoo11",
            "12": "/etc/init.d/odoo12",
            "13": "/etc/init.d/odoo13",
            "14": "/etc/init.d/odoo14",
            "v7": "/etc/init.d/openerp-server",
        }
        for ver in MAJVERS_TO_TEST + ["v7"]:
            if ver == "v7":
                w = ver
            elif ver == "6":
                # w = "%s.1" % ver
                continue
            else:
                w = "%s.0" % ver
            res = build_odoo_param("FULL_SVCNAME", odoo_vid=w, multi=True)
            sts = self.Z.test_result(
                z0ctx, "service script name %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        TRES = {
            "6": "odoo6-server",
            "7": "odoo7-server",
            "8": "odoo8-server",
            "9": "odoo9-server",
            "10": "odoo10",
            "11": "odoo11",
            "12": "odoo12",
            "13": "odoo13",
            "14": "odoo14",
            "v7": "openerp-server",
        }
        for ver in MAJVERS_TO_TEST + ["v7"]:
            if ver == "v7":
                w = ver
            elif ver == "6":
                # w = "%s.1" % ver
                continue
            else:
                w = "%s.0" % ver
            res = build_odoo_param("SVCNAME", odoo_vid=w, multi=True)
            sts = self.Z.test_result(
                z0ctx, "service name %s [python]" % w, TRES[ver], res
            )
            if sts:
                break

        # TRES = {
        #     "6": "/opt/odoo/6.1/server/openerp-server",
        #     "7": "/opt/odoo/7.0/openerp-server",
        #     "8": "/opt/odoo/8.0/openerp-server",
        #     "9": "/opt/odoo/9.0/openerp-server",
        #     "10": "/opt/odoo/10.0/odoo-bin",
        #     "11": "/opt/odoo/11.0/odoo-bin",
        #     "12": "/opt/odoo/12.0/odoo-bin",
        #     "13": "/opt/odoo/13.0/odoo-bin",
        #     "14": "/opt/odoo/14.0/odoo-bin",
        #     "v7": "/opt/odoo/v7/server/openerp-server",
        # }
        # for ver in MAJVERS_TO_TEST + ["v7"]:
        #     if ver == "v7":
        #         w = ver
        #     elif ver == "6":
        #         w = "%s.1" % ver
        #     else:
        #         w = "%s.0" % ver
        #     res = build_odoo_param("BIN", odoo_vid=w, multi=True)
        #     sts = self.Z.test_result(
        #         z0ctx, "run script name %s [python]" % w, TRES[ver], res
        #     )
        #     if sts:
        #         break

        # TRES = {
        #     "6.1": "/opt/odoo/VENV-6.1/odoo/server/openerp-server",
        #     "7.0": "/opt/odoo/VENV-7.0/odoo/openerp-server",
        #     "8.0": "/opt/odoo/VENV-8.0/odoo/openerp-server",
        #     "9.0": "/opt/odoo/VENV-9.0/odoo/openerp-server",
        #     "10.0": "/opt/odoo/VENV-10.0/odoo/odoo-bin",
        #     "11.0": "/opt/odoo/VENV-11.0/odoo/odoo-bin",
        #     "12.0": "/opt/odoo/VENV-12.0/odoo/odoo-bin",
        #     "13.0": "/opt/odoo/VENV-13.0/odoo/odoo-bin",
        #     "14.0": "/opt/odoo/VENV-14.0/odoo/odoo-bin",
        # }
        # for ver in VERSIONS_TO_TEST:
        #     w = "VENV-%s" % ver
        #     res = build_odoo_param("BIN", odoo_vid=w, multi=True)
        #     sts = self.Z.test_result(
        #         z0ctx, "run script name %s [python]" % w, TRES[ver], res
        #     )
        #     if sts:
        #         break

        TRES = {
            "6.1": "__openerp__.py",
            "7.0": "__openerp__.py",
            "8.0": "__openerp__.py",
            "9.0": "__openerp__.py",
            "10.0": "__manifest__.py",
            "11.0": "__manifest__.py",
            "12.0": "__manifest__.py",
            "13.0": "__manifest__.py",
            "14.0": "__manifest__.py",
            "v7": "__openerp__.py",
        }
        for ver in VERSIONS_TO_TEST + ["v7"]:
            res = build_odoo_param("MANIFEST", odoo_vid=ver, multi=True)
            sts = self.Z.test_result(
                z0ctx, "manifest %s [python]" % ver, TRES[ver], res
            )
            if sts:
                break

        TRES = {
            "6.1": 8166,
            "7.0": 8167,
            "8.0": 8168,
            "9.0": 8169,
            "10.0": 8170,
            "11.0": 8171,
            "12.0": 8172,
            "13.0": 8173,
            "14.0": 8174,
            "v7": 8069,
            "v8.0": 8069,
        }
        for ver in VERSIONS_TO_TEST + ["v7", "v8.0"]:
            res = build_odoo_param("RPCPORT", odoo_vid=ver, multi=True)
            sts = self.Z.test_result(z0ctx, "rpcport %s [python]" % ver, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6.1": 8166,
            "7.0": 8167,
            "8.0": 8168,
            "9.0": 8169,
            "10.0": 8170,
            "11.0": 8171,
            "12.0": 8172,
            "13.0": 8173,
            "14.0": 8174,
        }
        for ver in VERSIONS_TO_TEST:
            res = build_odoo_param("RPCPORT", odoo_vid=ver, multi=True)
            sts = self.Z.test_result(z0ctx, "rpcport %s [python]" % ver, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6.1": "odoo6",
            "7.0": "odoo7",
            "8.0": "odoo8",
            "9.0": "odoo9",
            "10.0": "odoo10",
            "11.0": "odoo11",
            "12.0": "odoo12",
            "13.0": "odoo13",
            "14.0": "odoo14",
            "v7": "odoo",
        }
        for ver in VERSIONS_TO_TEST + ["v7"]:
            res = build_odoo_param("USER", odoo_vid=ver, multi=True)
            sts = self.Z.test_result(z0ctx, "user %s [python]" % ver, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6": "odoo6",
            "7": "odoo7",
            "8": "odoo8",
            "9": "odoo9",
            "10": "odoo10",
            "11": "odoo11",
            "12": "odoo12",
            "13": "odoo13",
            "14": "odoo14",
        }
        for ver in MAJVERS_TO_TEST:
            w = "VENV-%s" % ver
            res = build_odoo_param("USER", odoo_vid=w, multi=True)
            sts = self.Z.test_result(z0ctx, "user %s [python]" % w, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6.1": "6.1",
            "7.0": "7.0",
            "8.0": "8.0",
            "9.0": "9.0",
            "10.0": "10.0",
            "11.0": "11.0",
            "12.0": "12.0",
            "13.0": "13.0",
            "14.0": "14.0",
        }
        for ver in VERSIONS_TO_TEST:
            w = "ODOO-%s" % ver
            res = build_odoo_param("FULLVER", odoo_vid=w, multi=True)
            sts = self.Z.test_result(z0ctx, "naming %s [python]" % w, TRES[ver], res)
            if sts:
                break

        return sts

    def __test_05(self, z0ctx):
        TRES = {
            "6.1": "/opt/odoo/6.1",
            "7.0": "/opt/odoo/7.0",
            "8.0": "/opt/odoo/8.0",
            "9.0": "/opt/odoo/9.0",
            "10.0": "/opt/odoo/10.0",
            "11.0": "/opt/odoo/11.0",
            "12.0": "/opt/odoo/12.0",
            "v7": "/opt/odoo/v7",
            "v8.0": "/opt/odoo/v8.0",
        }
        for ver in VERSIONS_TO_TEST + ["v7", "v8.0"]:
            res = build_odoo_param("ROOT", odoo_vid=ver, multi=True)
            sts = self.Z.test_result(z0ctx, "Root dir %s" % ver, TRES[ver], res)
            if sts:
                break

            res = build_odoo_param("ROOT", odoo_vid=ver, suppl="crm", multi=True)
            sts = self.Z.test_result(z0ctx, "Root dir %s/crm" % ver, TRES[ver], res)
            if sts:
                break

            res = build_odoo_param("HOME", odoo_vid=ver, suppl="OCB", multi=True)
            sts = self.Z.test_result(z0ctx, "Home dir %s/OCB" % ver, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6.1": "/opt/odoo/VENV-6.1/odoo",
            "7.0": "/opt/odoo/VENV-7.0/odoo",
            "8.0": "/opt/odoo/VENV-8.0/odoo",
            "9.0": "/opt/odoo/VENV-9.0/odoo",
            "10.0": "/opt/odoo/VENV-10.0/odoo",
            "11.0": "/opt/odoo/VENV-11.0/odoo",
            "12.0": "/opt/odoo/VENV-12.0/odoo",
        }
        for ver in VERSIONS_TO_TEST:
            w = "VENV-%s" % ver
            res = build_odoo_param("ROOT", odoo_vid=w, suppl="crm", multi=True)
            sts = self.Z.test_result(z0ctx, "Root dir %s" % w, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6.1": "/opt/odoo/6.1/openerp/filestore",
            "7.0": "/opt/odoo/7.0/openerp/filestore",
            "8.0": "/opt/odoo/.local/share/Odoo8",
            "9.0": "/opt/odoo/.local/share/Odoo9",
            "10.0": "/opt/odoo/.local/share/Odoo10",
            "11.0": "/opt/odoo/.local/share/Odoo11",
            "12.0": "/opt/odoo/.local/share/Odoo12",
            "VENV-10": "/opt/odoo/.local/share/Odoo",
            "v8.0": "/opt/odoo/.local/share/Odoo",
            "v7": "/opt/odoo/v7/openerp/filestore",
        }
        for ver in VERSIONS_TO_TEST + ["VENV-10", "v8.0", "v7"]:
            res = build_odoo_param("DDIR", odoo_vid=ver, multi=True)
            sts = self.Z.test_result(z0ctx, "Filestore  %s" % ver, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6.1": "/opt/odoo/6.1/crm",
            "7.0": "/opt/odoo/7.0/crm",
            "8.0": "/opt/odoo/8.0/crm",
            "9.0": "/opt/odoo/9.0/crm",
            "10.0": "/opt/odoo/10.0/crm",
            "11.0": "/opt/odoo/11.0/crm",
            "12.0": "/opt/odoo/12.0/crm",
            "v7": "/opt/odoo/v7/crm",
            "v8.0": "/opt/odoo/v8.0/crm",
        }
        for ver in VERSIONS_TO_TEST + ["v7", "v8.0"]:
            res = build_odoo_param("HOME", odoo_vid=ver, suppl="crm", multi=True)
            sts = self.Z.test_result(z0ctx, "Home %s/crm" % ver, TRES[ver], res)
            if sts:
                break

        TRES = {
            "6.1": "/opt/odoo/VENV-6.1/odoo/crm",
            "7.0": "/opt/odoo/VENV-7.0/odoo/crm",
            "8.0": "/opt/odoo/VENV-8.0/odoo/crm",
            "9.0": "/opt/odoo/VENV-9.0/odoo/crm",
            "10.0": "/opt/odoo/VENV-10.0/odoo/crm",
            "11.0": "/opt/odoo/VENV-11.0/odoo/crm",
            "12.0": "/opt/odoo/VENV-12.0/odoo/crm",
        }
        for ver in VERSIONS_TO_TEST:
            w = "VENV-%s" % ver
            res = build_odoo_param("HOME", odoo_vid=w, suppl="crm", multi=True)
            sts = self.Z.test_result(z0ctx, "Home %s/crm" % w, TRES[ver], res)
            if sts:
                break

        return sts

    def __test_06(self, z0ctx):
        repos = "OCB"
        TRES = {
            "zero-git": "git@github.com:zeroincombenze/%s" % repos,
            "zero-http": "https://github.com/zeroincombenze/%s" % repos,
            "oca": "https://github.com/OCA/%s" % repos,
            "librerp": "https://github.com/iw3hxn/server",
        }
        if re.match("shs[a-z0-9]+", os.environ["HOSTNAME"]):
            TRES["zero"] = TRES["zero-git"]
        else:
            TRES["zero"] = TRES["zero-http"]
        for org in ("zero", "zero-git", "zero-http", "oca", "librerp"):
            for ver in VERSIONS_TO_TEST:
                RES = build_odoo_param("URL", odoo_vid=ver, multi=False)
                sts = self.Z.test_result(z0ctx, "Root dir %s" % ver, TRES[org], RES)
            if sts:
                break

            RES = build_odoo_param(
                "GIT_URL", odoo_vid=ver, suppl=repos, git_org=org, multi=False
            )
            sts = self.Z.test_result(
                z0ctx, "GIT_URL %s/%s %s" % (org, repos, ver), TRES[org], RES
            )
            if sts:
                break

            RES = build_odoo_param(
                "URL_BRANCH", odoo_vid=ver, suppl=repos, git_org=org, multi=False
            )
            sts = self.Z.test_result(
                z0ctx, "URL_BRANCH %s/%s %s" % (org, repos, ver), TRES[org], RES
            )
            if sts:
                break

        TRES = {
            "zero-git": "git@github.com:zeroincombenze",
            "zero-http": "https://github.com/zeroincombenze",
            "oca": "https://github.com/OCA",
            "librerp": "https://github.com/iw3hxn",
        }
        if re.match("shs[a-z0-9]+", os.environ["HOSTNAME"]):
            TRES["zero"] = TRES["zero-git"]
        else:
            TRES["zero"] = TRES["zero-http"]
        for org in ("zero", "zero-git", "zero-http", "oca", "librerp"):
            for ver in VERSIONS_TO_TEST:
                RES = build_odoo_param(
                    "GIT_ORG", odoo_vid=ver, suppl=repos, git_org=org, multi=False
                )
                sts = self.Z.test_result(
                    z0ctx, "GIT_ORG %s/%s %s" % (org, repos, ver), TRES[org], RES
                )
            if sts:
                break

        TRES = {
            "zero-git": '"https://github.com/OCA/%s' % repos,
            "zero-http": '"https://github.com/OCA/%s' % repos,
            "oca": '"https://github.com/OCA/%s' % repos,
            "librerp": "https://github.com/iw3hxn/%s" % repos,
        }
        for org in ("zero", "zero-git", "zero-http", "oca", "librerp"):
            for ver in VERSIONS_TO_TEST:
                RES = build_odoo_param(
                    "UPSTREAM", odoo_vid=ver, suppl=repos, git_org=org, multi=False
                )
                if ver == "6.1" or repos == "oca" or repos == "librerp":
                    sts = self.Z.test_result(
                        z0ctx, "UPSTREAM %s/%s %s" % (org, repos, ver), TRES[org], ""
                    )
                else:
                    sts = self.Z.test_result(
                        z0ctx, "UPSTREAM %s/%s %s" % (org, repos, ver), TRES[org], RES
                    )
            if sts:
                break

        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
