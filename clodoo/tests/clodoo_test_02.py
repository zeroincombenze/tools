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
import re
# import os.path
import sys
from subprocess import PIPE, Popen

from os0 import os0

from zerobug import Z0test
from clodoo import clodoo
from clodoo.clodoolib import (crypt, decrypt)


__version__ = "0.3.5.13"


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
        self.module_2_test = 'crm'
        self.login_2_test = 'administrator'

    def check_4_db(self, dbname):
        cmd = ['psql'] + ['-Upostgres'] + ['-l']
        p = Popen(cmd,
                  stdin=PIPE,
                  stdout=PIPE,
                  stderr=PIPE)
        res, err = p.communicate()
        dbname = ' %s ' % dbname
        if res.find(dbname) >= 0:
            return True
        else:
            return False

    def check_4_module(self, oe_version):
        xmlrpc_port, dbname = self.param_by_db(oe_version)
        confn = '%s/test_clodoo2.conf' % self.Z.test_dir
        codefile = """[options]
xmlrpc_port=%d
oe_version=%s
""" % (xmlrpc_port, oe_version)
        fd = open(confn, 'w')
        fd.write(codefile)
        fd.close()
        oerp, uid, ctx = clodoo.oerp_set_env(confn=confn,
                                             db=dbname)
        model = 'ir.module.module'
        ids = clodoo.searchL8(ctx, model, [('name', '=', self.module_2_test),
                                           ('state', '=', 'installed')])
        if ids:
            return True
        else:
            return False

    def check_4_user(self, oe_version):
        user = self.param_by_db(oe_version, field='user')
        dbname = self.param_by_db(oe_version, field='dbname')
        sql = "select login from res_users" + \
              " where id=1;"
        cmd = 'psql -U%s %s -c"%s"' % (user, dbname, sql)
        p = Popen(cmd,
                  stdin=PIPE,
                  stdout=PIPE,
                  stderr=PIPE,
                  shell=True)
        res, err = p.communicate()
        login_name = ' %s' % self.login_2_test
        if res.find(login_name) >= 0:
            return True
        else:
            return False

    def param_by_db(self, oe_version, field=None):
        minor_ver = int(eval(oe_version))
        xmlrpc_port = 8160 + minor_ver
        dbname = self.dbtest + str(minor_ver)
        user = 'odoo%d' % minor_ver
        if field == 'dbname':
            return dbname
        elif field == 'user':
            return user
        return xmlrpc_port, dbname

    def bulk_cmd(self, oe_version):
        xmlrpc_port, dbname = self.param_by_db(oe_version)
        if not ctx['dry_run']:
            cmd = self.cmd + ['-d' + dbname]
            cmd = cmd + ['-b%s' % oe_version]
            cmd = cmd + ['-r%s' % xmlrpc_port]
            cmd = cmd + ['-p%s' % self.Z.test_dir]
            # cmd = cmd + ['-q']
        return cmd

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
            for oe_version in ('6.1', '7.0', '8.0', '9.0', '10.0'):
                xmlrpc_port = int(eval(oe_version)) + 8160
                if oe_version in ('6.1', '7.0', '8.0'):
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
                    if re.search('protocol *= *%s' % xml_prot, res):
                        res = True
                    else:
                        res = False
                else:
                    res = True
                sts = self.Z.test_result(z0ctx,
                                         "Show params -b%s" % oe_version,
                                         True,
                                         res)
        return sts

    def test_03(self, z0ctx):
        sts = TEST_SUCCESS
        if os.environ.get("HOSTNAME", "") == "shsdef16":
                #  or os.getcwd[0:19] != "/opt/odoo/dev/pypi/"):
            for oe_version in ('6.1', '7.0', '8.0', '9.0', '10.0'):
                if not ctx['dry_run']:
                    cmd = self.bulk_cmd(oe_version)
                    if os.environ.get("TRAVIS", "") != "true":
                        xmlrpc_port, dbname = self.param_by_db(oe_version)
                        os0.muteshell("/opt/odoo/tools/zar/pg_db_active -wa " +
                                      dbname)
                    os0.muteshell("dropdb -Upostgres --if-exists " + dbname)
                    cmd = cmd + ['-Anew_db']
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    res = self.check_4_db(dbname)
                else:
                    res = True
                sts = self.Z.test_result(z0ctx,
                                         "Create DB -b%s" % oe_version,
                                         True,
                                         res)

                if not ctx['dry_run']:
                    cmd = self.bulk_cmd(oe_version)
                    cmd = cmd + ['-Ashow_params']
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    if oe_version in ('6.1', '7.0', '8.0'):
                        xml_prot = 'xmlrpc'
                    elif oe_version in ('9.0', '10.0'):
                        xml_prot = 'jsonrpc'
                    if re.search('protocol *= *%s' % xml_prot, res):
                        res = True
                    else:
                        res = False
                    sts = self.Z.test_result(
                        z0ctx,
                        "Show db params -b%s" % oe_version,
                        True,
                        res)
        return sts

    def test_04(self, z0ctx):
        sts = TEST_SUCCESS
        confn = '%s/test_clodoo.conf' % self.Z.test_dir
        # datafn = 'res_users.csv'
        # dataffn = '%s/%s' % (self.Z.test_dir, datafn)
        if os.environ.get("HOSTNAME", "") == "shsdef16":
            for oe_version in ('6.1', '7.0', '8.0', '9.0', '10.0'):
                if not ctx['dry_run']:
                    res = self.check_4_module(oe_version)
                else:
                    res = False
                sts = self.Z.test_result(
                    z0ctx,
                    "Module -b%s %s" % (oe_version, self.module_2_test),
                    False,
                    res)
                if not ctx['dry_run']:
                    codefile = """[options]
actions=install_modules
install_modules=%s
""" % self.module_2_test
                    fd = open(confn, 'w')
                    fd.write(codefile)
                    fd.close()
                    cmd = self.bulk_cmd(oe_version)
                    cmd = cmd + ['-c%s' % confn]
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    res = self.check_4_module(oe_version)
                else:
                    res = True
                sts = self.Z.test_result(
                    z0ctx,
                    "Install -b%s %s" % (oe_version, self.module_2_test),
                    True,
                    res)
        return sts

    def test_05(self, z0ctx):
        sts = TEST_SUCCESS
        confn = '%s/test_clodoo.conf' % self.Z.test_dir
        datafn = 'res_users.csv'
        dataffn = '%s/%s' % (self.Z.test_dir, datafn)
        if os.environ.get("HOSTNAME", "") == "shsdef16":
            for oe_version in ('6.1', '7.0', '8.0', '9.0', '10.0'):
                if not ctx['dry_run']:
                    res = self.check_4_user(oe_version)
                else:
                    res = False
                sts = self.Z.test_result(
                    z0ctx,
                    "User -b%s" % (oe_version),
                    False,
                    res)
                if not ctx['dry_run']:
                    codefile = """[options]
actions=import_file
filename=%s
crypt_password=%s
model=res.users
""" % (datafn, crypt('admin'))
                    fd = open(confn, 'w')
                    fd.write(codefile)
                    fd.close()
                    cmd = self.bulk_cmd(oe_version)
                    cmd = cmd + ['-c%s' % confn]
                    datafile = """id,name,login,signature,email,tz,lang
base.user_root,Administrator,%s,"Amministratore","me@example.com",
"Europe/Rome","en_US"
""" % self.login_2_test
                    fd = open(dataffn, 'w')
                    fd.write(datafile)
                    fd.close()
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    res = self.check_4_user(oe_version)
                else:
                    res = True
                sts = self.Z.test_result(
                    z0ctx,
                    "Import user -b%s" % (oe_version),
                    True,
                    res)
        return sts

    def test_09(self, z0ctx):
        sts = TEST_SUCCESS
        confn = '%s/test_clodoo.conf' % self.Z.test_dir
        if os.environ.get("HOSTNAME", "") == "shsdef16":
            for oe_version in ('6.1', '7.0', '8.0', '9.0', '10.0'):
                if not ctx['dry_run']:
                    cmd = self.cmd
                    xmlrpc_port, dbname = self.param_by_db(oe_version)
                    codefile = """[options]
actions=drop_db
login_user=%s
db_name=%s
xmlrpc_port=%s
oe_version=%s
""" % (self.login_2_test, dbname, xmlrpc_port, oe_version)
                    # DB exists, but due -q switch no response returns False
                    fd = open(confn, 'w')
                    fd.write(codefile)
                    fd.close()
                    if os.environ.get("TRAVIS", "") != "true":
                        os0.muteshell("/opt/odoo/tools/zar/pg_db_active -wa " +
                                      dbname)
                    cmd = cmd + ['-c%s' % confn]
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    res = self.check_4_db(dbname)
                else:
                    res = False
                sts = self.Z.test_result(z0ctx,
                                         "Drop DB -b%s" % oe_version,
                                         False,
                                         res)
        return sts


#
if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)
