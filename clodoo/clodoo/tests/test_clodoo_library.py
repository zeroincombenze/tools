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


__version__ = "2.0.5"

ODOO_VERSION_TO_TEST = ("16.0", "12.0", "10.0", "7.0")


def version():
    return __version__


class RegressionTest:
    def __init__(self, zarlib):
        self.Z = zarlib
        self.test_data_dir = os.path.join(self.Z.testdir, 'res')

    def test_01(self, z0ctx):
        sts = 0
        if not z0ctx.get('dry_run', False):
            print("Connection test: it works only if odoo instances are running!")
            if not os.path.isdir(self.test_data_dir):
                os.mkdir(self.test_data_dir)
            for odoo_version in ODOO_VERSION_TO_TEST:
                odoo_major = int(odoo_version.split(".")[0])
                confn = os.path.join(self.test_data_dir, 'odoo%s.conf' % odoo_major)
                config_dict = {
                    "db_host": "localhost",
                    "db_port": "False",
                    "db_template": "template1",
                    "db_user": "odoo%d" % odoo_major,
                    "login_user": "zeroadm,admin",
                    "dbfilter": "test%d" % odoo_major,
                    "xmlrpc_port": str(
                        clodoo.build_odoo_param("RPCPORT",
                                                odoo_version,
                                                multi=True)),
                    "psycopg2": "1",
                    "oe_version": odoo_version,
                }
                config = ConfigParser()
                config["options"] = {}
                config["options"].update(config_dict)
                config.write(open(confn, "w"))
                print("  ... Odoo %s must be running!" % odoo_version)
        for odoo_version in ODOO_VERSION_TO_TEST:
            odoo_major = int(odoo_version.split(".")[0])
            database = "test%d" % odoo_major
            confn = os.path.join(self.test_data_dir, 'odoo%s.conf' % odoo_major)
            uid, ctx = clodoo.oerp_set_env(ctx={}, confn=confn, db=database)
            sts += self.Z.test_result(
                z0ctx, "Connect %s/%s" % (database, odoo_version), uid > 0, True)
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
