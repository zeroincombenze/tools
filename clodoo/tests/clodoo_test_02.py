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
# import os
# import os.path
import sys
from os0 import os0
from subprocess import Popen, PIPE
from zerobug import Z0test

__version__ = "0.2.69.13"

MODULE_ID = 'clodoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib
        self.cmd = ['python'] + [self.Z.pkg_dir + '/clodoo.py'] + ['-q']
        self.dbtest = 'clodoo_test'

    def check_4_db(self):
        cmd = ['psql'] + ['-l']
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
        if not ctx['dry_run']:
            os0.muteshell("/opt/odoo/dev/pypi/zar/zar/pg_db_active -wa " +
                          self.dbtest)
            os0.muteshell("dropdb -Upostgres --if-exists " + self.dbtest)
            cmd = self.cmd + ['-A=new_db'] + ['-d=' + self.dbtest]
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
            os0.muteshell("/opt/odoo/dev/pypi/zar/zar/pg_db_active -wa " +
                          self.dbtest)
            cmd = self.cmd + ['-A=drop_db'] + ['-d=' + self.dbtest]
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
#
# Run main if executed as a script
if __name__ == "__main__":
    # pdb.set_trace()
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
