# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
    Clodoo Regression Test Suite
"""

# import pdb
import os
# import os.path
import sys
import re
from os0 import os0
from subprocess import Popen, PIPE
from zerobug import Z0test

__version__ = "0.2.77.2"

MODULE_ID = 'clodoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib
        self.cmd = ['python'] + [self.Z.pkg_dir + '/clodoo.py'] + \
            ['-q']  # + [ '-c' + self.Z.test_dir + '/clodoo.conf' ]
        self.dbtest = 'clodoo_test'

    def check_4_db(self):
        cmd = ['psql'] + ['-Upostgres'] + ['-l']
        p = Popen(cmd,
                  stdin=PIPE,
                  stdout=PIPE,
                  stderr=PIPE)
        res, err = p.communicate()
        dbname = ' ' + self.dbtest + ' '
        if res.find(dbname) >= 0:
            return True
        else:
            return False

    def test_01(self, z0ctx):
        req_version = 'clodoo.py %s' % __version__
        if not ctx['dry_run']:
            cmd = self.cmd + ['-V']
            p = Popen(cmd,
                      stdin=PIPE,
                      stdout=PIPE,
                      stderr=PIPE)
            res, err = p.communicate()
            if not res:
                res = err.strip()
        else:
            res = req_version
        sts = self.Z.test_result(z0ctx,
                                 "Version",
                                 req_version,
                                 res)
        return sts

    def test_02(self, z0ctx):
        sts = TEST_SUCCESS
        if os.environ.get("HOSTNAME", "") == "shsdef16":
                #  or os.getcwd[0:19] != "/opt/odoo/dev/pypi/"):
            if not ctx['dry_run']:
                if os.environ.get("TRAVIS", "") != "true":
                    os0.muteshell("/opt/odoo/tools/zar/pg_db_active -wa " +
                                  self.dbtest)
                os0.muteshell("dropdb -Upostgres --if-exists " + self.dbtest)
                cmd = self.cmd + ['-Anew_db'] + ['-d' + self.dbtest]
                p = Popen(cmd,
                          stdin=PIPE,
                          stdout=PIPE,
                          stderr=PIPE)
                res, err = p.communicate()
                res = self.check_4_db()
            else:
                res = True
            sts = self.Z.test_result(z0ctx,
                                     "Create DB",
                                     True,
                                     res)
            if not ctx['dry_run']:
                os0.muteshell("/opt/odoo/tools/zar/pg_db_active -wa " +
                              self.dbtest)
                cmd = self.cmd + ['-Adrop_db'] + ['-d' + self.dbtest]
                p = Popen(cmd,
                          stdin=PIPE,
                          stdout=PIPE,
                          stderr=PIPE)
                res, err = p.communicate()
                res = self.check_4_db()
            else:
                res = False
            sts = self.Z.test_result(z0ctx,
                                     "Drop DB",
                                     False,
                                     res)
        return sts

    def test_03(self, z0ctx):
        sts = TEST_SUCCESS
        if os.environ.get("HOSTNAME", "") == "shsdef16":
            for oe_version in ('7.0', '8.0', '9.0', '10.0'):
                xmlrpc_port = int(eval(oe_version)) + 8160
                if oe_version in ('7.0', '8.0'):
                    xml_prot = 'xmlrpc'
                elif oe_version in ('9.0', '10.0'):
                    xml_prot = 'jsonrpc'
                if not ctx['dry_run']:
                    cmd = self.cmd + ['-d' + self.dbtest]
                    cmd = cmd + ['-b%s' % oe_version]
                    cmd = cmd + ['-r%s' % xmlrpc_port]
                    cmd = cmd + ['-Ashow_params']
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    if re.search('protocol *= *%s' % xml_prot,res):
                        res = True
                    else:
                        res = False
                else:
                    res = True
                sts = self.Z.test_result(z0ctx,
                                         "Show db param -b%s" % oe_version,
                                         True,
                                         res)
            for oe_version in ('7.0', '8.0', '9.0', '10.0'):
                xmlrpc_port = int(eval(oe_version)) + 8160
                dbname = 'demo%d' % int(eval(oe_version))
                if not ctx['dry_run']:
                    cmd = self.cmd + ['-d' + dbname]
                    cmd = cmd + ['-c%s' % '/opt/odoo/clodoo/clodoo.conf']
                    cmd = cmd + ['-b%s' % oe_version]
                    cmd = cmd + ['-r%s' % xmlrpc_port]
                    cmd = cmd + ['-Ashow_db_params']
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    if re.search('DB name *= *%s' % dbname,res):
                        res = True
                    else:
                        res = False
                        # res = True   #debug temporary
                else:
                    res = True
                sts = self.Z.test_result(z0ctx,
                                         "Show param -b%s" % oe_version,
                                         True,
                                         res)


#
# Run main if executed as a script
if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
