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
try:
    from clodoo import clodoo
    from clodoo.clodoolib import crypt
except BaseException:
    import clodoo
    from clodoolib import crypt


__version__ = "0.3.8.7"


MODULE_ID = 'clodoo'
# VERSIONS_TO_TEST = ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1')
VERSIONS_TO_TEST = ('11.0', '10.0', '8.0', '7.0')
# VERSIONS_TO_TEST = ('12.0',)
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
        self.new_password = 'newpwd'
        self.new_partner = 'Test Company A'
        codefile = """[options]
actions=unit_test
"""
        fd = open(self.Z.pkg_dir + '/clodoo.conf', 'w')
        fd.write(codefile)
        fd.close()

    def check_4_db(self, dbname):
        cmd = ['psql'] + ['-Upostgres'] + ['-tl']
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
        uid, ctx = clodoo.oerp_set_env(confn=confn,
                                       db=dbname)
        model = 'ir.module.module'
        ids = clodoo.searchL8(ctx, model, [('name', '=', self.module_2_test),
                                           ('state', '=', 'installed')])
        if ids:
            return True
        else:
            return False

    def check_4_user(self, oe_version, id=None, login_name=False):
        user = self.param_by_db(oe_version, field='user')
        dbname = self.param_by_db(oe_version, field='dbname')
        if not id:
            sql = "select res_id from ir_model_data"
            sql += " where module='base' and name='user_root';"
            cmd = 'psql -At -U%s %s -c"%s"' % (user, dbname, sql)
            p = Popen(cmd,
                      stdin=PIPE,
                      stdout=PIPE,
                      stderr=PIPE,
                      shell=True)
            res, err = p.communicate()
            id = eval(res) or 1
        sql = "select login from res_users" + \
              " where id=%d;" % id
        cmd = 'psql -At -U%s %s -c"%s"' % (user, dbname, sql)
        p = Popen(cmd,
                  stdin=PIPE,
                  stdout=PIPE,
                  stderr=PIPE,
                  shell=True)
        res, err = p.communicate()
        login_name = '%s\n' % (login_name or self.login_2_test)
        if res.find(login_name) >= 0:
            return True
        else:
            return False

    def check_4_partner(self, oe_version, id=None, name=False, byname=False):
        user = self.param_by_db(oe_version, field='user')
        dbname = self.param_by_db(oe_version, field='dbname')
        id = id or 1
        name = name or 'admin'
        if name and byname:
            sql = "select name from res_partner" + \
                  " where name='%s';" % name
        else:
            sql = "select name from res_partner" + \
                  " where id=%d;" % id
        cmd = 'psql -t -U%s %s -c"%s"' % (user, dbname, sql)
        p = Popen(cmd,
                  stdin=PIPE,
                  stdout=PIPE,
                  stderr=PIPE,
                  shell=True)
        res, err = p.communicate()
        if res.find(name) >= 0:
            return True
        else:
            return False

    def search_alias(self, oe_version, ref):
        user = self.param_by_db(oe_version, field='user')
        dbname = self.param_by_db(oe_version, field='dbname')
        refs = ref.split('.')
        sql = "select res_id from ir_model_data"
        sql += " where module='%s' and name='%s';" % (refs[0], refs[1])
        cmd = 'psql -At -U%s %s -c"%s"' % (user, dbname, sql)
        p = Popen(cmd,
                  stdin=PIPE,
                  stdout=PIPE,
                  stderr=PIPE,
                  shell=True)
        res, err = p.communicate()
        return eval(res)

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
        if os.environ.get("HOSTNAME", "") in ("shsdef16", "shs17fid"):
            for oe_version in VERSIONS_TO_TEST:
                majver = int(eval(oe_version))
                xmlrpc_port = 8160 + majver
                if majver < 9:
                    xml_prot = 'xmlrpc'
                else:
                    xml_prot = 'jsonrpc'
                if not ctx['dry_run']:
                    # TODO: remove -d param
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
        if os.environ.get("HOSTNAME", "") in ("shsdef16", "shs17fid"):
                #  or os.getcwd[0:19] != "/opt/odoo/dev/pypi/"):
            for oe_version in VERSIONS_TO_TEST:
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
                    majver = int(eval(oe_version))
                    if majver < 9:
                        xml_prot = 'xmlrpc'
                    else:
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
        if os.environ.get("HOSTNAME", "") in ("shsdef16", "shs17fid"):
            for oe_version in VERSIONS_TO_TEST:
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
        if os.environ.get("HOSTNAME", "") in ("shsdef16", "shs17fid"):
            for oe_version in VERSIONS_TO_TEST:
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
hide_cid=True
alias_field=partner_id
alias_model2=res.partner
""" % (datafn, crypt('admin'))
                    fd = open(confn, 'w')
                    fd.write(codefile)
                    fd.close()
                    cmd = self.bulk_cmd(oe_version)
                    cmd = cmd + ['-c%s' % confn]
                    if oe_version == '6.1':
                        datafile = """id,name,login,signature,email,tz,new_password
base.user_root,Administrator,%s,"Ammin.","me@example.com","Europe/Rome",None
base.user_admin2,Admin,admin2,"Amministratore2","me2@example.com",,%s
""" % (self.login_2_test, self.new_password)
                    else:
                        datafile = """id,name,login,signature,email,tz,partner_id,new_password
base.user_root,Administrator,%s,"Ammin.","me@example.com","Europe/Rome",None,None
base.user_admin2,Admin,admin2,"Amministratore2","me2@example.com",,base.partner_user2,%s
""" % (self.login_2_test, self.new_password)
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
                if not ctx['dry_run']:
                    res = self.search_alias(oe_version, 'base.user_admin2')
                    res = self.check_4_user(oe_version,
                                            id=res,
                                            login_name='admin2')
                else:
                    res = True
                sts = self.Z.test_result(
                    z0ctx,
                    "Add user -b%s" % (oe_version),
                    True,
                    res)
                if not ctx['dry_run'] and oe_version != '6.1':
                    res = self.search_alias(oe_version, 'base.partner_user2')
                    res = self.check_4_partner(oe_version,
                                               id=res,
                                               name='Admin')
                else:
                    res = True
                sts = self.Z.test_result(
                    z0ctx,
                    "Add user -b%s" % (oe_version),
                    True,
                    res)
        return sts

    def test_06(self, z0ctx):
        sts = TEST_SUCCESS
        confn = '%s/test_clodoo.conf' % self.Z.test_dir
        if os.environ.get("HOSTNAME", "") in ("shsdef16", "shs17fid"):
            for oe_version in VERSIONS_TO_TEST:
                xmlrpc_port, dbname = self.param_by_db(oe_version)
                if not ctx['dry_run']:
                    codefile = """[options]
actions=show_db_params
login_user=admin2
crypt_password=%s
""" % crypt(self.new_password)
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
                    if res.find(dbname) >= 0:
                        res = True
                    else:
                        res = False
                else:
                    res = True
                sts = self.Z.test_result(
                    z0ctx,
                    "Connect user admin2 -b%s" % (oe_version),
                    True,
                    res)
        return sts

    def test_07(self, z0ctx):
        sts = TEST_SUCCESS
        confn = '%s/test_clodoo.conf' % self.Z.test_dir
        datafn = 'res_partner.csv'
        dataffn = '%s/%s' % (self.Z.test_dir, datafn)
        if os.environ.get("HOSTNAME", "") in ("shsdef16", "shs17fid"):
            for oe_version in VERSIONS_TO_TEST:
                if not ctx['dry_run']:
                    res = self.check_4_partner(oe_version,
                                               name=self.new_partner,
                                               byname=True)
                else:
                    res = False
                sts = self.Z.test_result(
                    z0ctx,
                    "Partner -b%s" % (oe_version),
                    False,
                    res)
                if not ctx['dry_run']:
                    codefile = """[options]
login_user=admin2
crypt_password=%s
actions=import_file
filename=%s
model=res.partner
hide_cid=True
""" % (crypt(self.new_password), datafn)
                    fd = open(confn, 'w')
                    fd.write(codefile)
                    fd.close()
                    cmd = self.bulk_cmd(oe_version)
                    cmd = cmd + ['-c%s' % confn]
                    if oe_version == '6.1':
                        datafile = """id,name
base.partner_A,%s
""" % self.new_partner
                    else:
                        datafile = """id,name
base.partner_A,%s
""" % self.new_partner
                    fd = open(dataffn, 'w')
                    fd.write(datafile)
                    fd.close()
                    p = Popen(cmd,
                              stdin=PIPE,
                              stdout=PIPE,
                              stderr=PIPE)
                    res, err = p.communicate()
                    res = self.check_4_partner(oe_version,
                                               name=self.new_partner,
                                               byname=True)
                else:
                    res = True
                sts = self.Z.test_result(
                    z0ctx,
                    "Import partner -b%s" % (oe_version),
                    True,
                    res)
        return sts

    def test_09(self, z0ctx):
        sts = TEST_SUCCESS
        confn = '%s/test_clodoo.conf' % self.Z.test_dir
        if os.environ.get("HOSTNAME", "") in ("shsdef16", "shs17fid"):
            for oe_version in VERSIONS_TO_TEST:
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
