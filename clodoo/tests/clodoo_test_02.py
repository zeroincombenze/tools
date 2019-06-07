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
# import os.path
import sys
from datetime import datetime
from subprocess import PIPE, Popen

from zerobug import Z0test
# import oerplib
try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = "0.3.8.34"


MODULE_ID = 'clodoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib
        self.ctx = {}
        self.uid = False
        self.db = 'clodoo_test'

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

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        # if os.environ.get("HOSTNAME", "") not in ("shsdef16", "shs17fid"):
        #     return sts
        if not z0ctx['dry_run']:
            self.uid, self.ctx = clodoo.oerp_set_env(
                db=self.db,
                ctx={'oe_version': '*',
                     'no_login': True,
                     'conf_fn': './no_filename.conf',})
            self.ctx['test_unit_mode'] = True
            clodoo.act_drop_db(self.ctx)
            sts = clodoo.act_new_db(self.ctx)
            res = self.check_4_db(self.db)
        else:
            res = True
        sts = self.Z.test_result(z0ctx,
                                 "new_db(%s)" % self.db,
                                 TEST_SUCCESS,
                                sts)
        sts = self.Z.test_result(z0ctx,
                                 "new_db(%s)" % self.db,
                                 True,
                                 res)
        if not z0ctx['dry_run']:
            self.uid, self.ctx = clodoo.oerp_set_env(
                db='clodoo_test',
                ctx={'oe_version': self.ctx['oe_version'],
                     'conf_fn': './no_filename.conf',})
            self.ctx['test_unit_mode'] = True
        return sts

    def test_02(self, z0ctx):
        sts = TEST_SUCCESS
        if os.environ.get("HOSTNAME", "") not in ("shsdef16", "shs17fid"):
            return sts
        ctx = self.ctx
        if not z0ctx['dry_run']:
            ids = clodoo.searchL8(ctx, 'res.users', [])
        else:
            ids = [1]
        sts = self.Z.test_result(z0ctx,
                                 'searchL8(res.users)',
                                 True,
                                 1 in ids)
        if sts == TEST_SUCCESS:
            model = 'res.users'
            if not z0ctx['dry_run']:
                user = clodoo.browseL8(ctx, 'res.users', 1)
                user_id = user.id
            else:
                user_id = 1
            sts = self.Z.test_result(z0ctx,
                                     'browseL8(res.users)',
                                     1,
                                     user_id)
        if sts == TEST_SUCCESS:
            if not z0ctx['dry_run']:
                RES = clodoo.get_val_from_field(ctx, model, user, 'login')
            else:
                RES = 'admin'
            sts = self.Z.test_result(z0ctx,
                                     'user[login] (char)',
                                     'admin',
                                     RES)
        if sts == TEST_SUCCESS:
            if not z0ctx['dry_run']:
                RES = clodoo.get_val_from_field(ctx, model, user, 'active')
            else:
                RES = True
            sts = self.Z.test_result(z0ctx,
                                     'user[active] (bool)',
                                     True,
                                     RES)
        if sts == TEST_SUCCESS:
            if not z0ctx['dry_run']:
                RES = clodoo.get_val_from_field(ctx, model, user, 'company_id')
            else:
                RES = True
            sts = self.Z.test_result(z0ctx,
                                     'user[company_id] (m2o)',
                                     True,
                                     RES)
        if sts == TEST_SUCCESS:
            if not z0ctx['dry_run']:
                RES = clodoo.get_val_from_field(ctx, model, user,
                                                'company_ids')
            else:
                RES = [1]
            sts = self.Z.test_result(z0ctx,
                                     'user[company_ids] (m2m)',
                                     [1],
                                     RES)
        if sts == TEST_SUCCESS:
            if not z0ctx['dry_run']:
                RES = clodoo.get_val_from_field(ctx, model, user,
                                                'company_ids', format='cmd')
            else:
                RES = [(6, 0, [1])]
            sts = self.Z.test_result(z0ctx,
                                     'user[company_ids] (cmd)',
                                     [(6, 0, [1])],
                                     RES)
        if sts == TEST_SUCCESS:
            if not z0ctx['dry_run']:
                RES = clodoo.get_val_from_field(ctx, model, user,
                                                'login_date')
            else:
                RES = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sts = self.Z.test_result(z0ctx,
                                     'user[login_date] (date[time])',
                                     datetime.now().strftime('%Y-%m-%d'),
                                     str(RES)[0:10])
        if sts == TEST_SUCCESS:
            if not z0ctx['dry_run']:
                RES = clodoo.get_val_from_field(ctx, model, user,
                                                'login_date', format='cmd')
            else:
                RES = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sts = self.Z.test_result(z0ctx,
                                     'user[login_date] (date[time])',
                                     datetime.now().strftime('%Y-%m-%d'),
                                     RES[0:10])
        return sts

    def test_03(self, z0ctx):
        sts = TEST_SUCCESS
        if os.environ.get("HOSTNAME", "") not in ("shsdef16", "shs17fid"):
            return sts
        ctx = self.ctx
        if not z0ctx['dry_run']:
            model = 'ir.model'
            rec = clodoo.browseL8(ctx, model,
                                  clodoo.searchL8(
                                      ctx, model,
                                      [('model', '=', 'res.users')])[0])
            RES = clodoo.get_val_from_field(ctx, model, rec,
                                            'field_id')
        else:
            RES = [1,2,3]
        sts = self.Z.test_result(z0ctx,
                                 'ir_model[field_id] (o2m)',
                                 True,
                                 isinstance(RES, list) and len(RES) > 1)
        if sts == TEST_SUCCESS:
            record_list = RES
            if not z0ctx['dry_run']:
                model = 'ir.model'
                RES = clodoo.get_val_from_field(ctx, model, rec,
                                                'field_id', format='cmd')
            else:
                RES = [(6, 9, record_list)]
            sts = self.Z.test_result(z0ctx,
                                     'ir_model[field_id] (cmd)',
                                     [(6, 0, record_list)],
                                     RES)
        return sts

    def test_04(self, z0ctx):
        sts = TEST_SUCCESS
        if os.environ.get("HOSTNAME", "") not in ("shsdef16", "shs17fid"):
            return sts
        ctx = self.ctx
        model = 'res.users'
        vals = {
            'name': 'admin',
            'partner_id': 1,
            'email': 'myname@example.com'
        }
        for tgt_ver in ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1'):
            for name in vals:
                if not z0ctx['dry_run']:
                    new_name, RES = clodoo.cvt_value_from_ver_to_ver(
                        ctx,
                        model,
                        name,
                        vals[name],
                        '7.0',
                        tgt_ver)
                else:
                    RES = new_name = True
                if name == 'name':
                    TRES = vals[name]
                    sts = self.Z.test_result(z0ctx,
                                             'cvt(%s)' % name,
                                             TRES,
                                             RES)
                elif name == 'partner_id':
                    if tgt_ver == '6.1':
                        TRES = False
                    else:
                        TRES = vals[name]
                    sts = self.Z.test_result(z0ctx,
                                             'cvt(%s)' % name,
                                             TRES,
                                             RES)
                elif name == 'email':
                    if tgt_ver == '6.1':
                        TRES = 'user_email'
                    else:
                        TRES = name
                    sts = self.Z.test_result(z0ctx,
                                             'cvt(%s)' % name,
                                             TRES,
                                             new_name)
        return sts

    def test_05(self, z0ctx):
        sts = TEST_SUCCESS
        if os.environ.get("HOSTNAME", "") not in ("shsdef16", "shs17fid"):
            return sts
        ctx = self.ctx
        model = 'res.users'
        vals = {
            'name': 'admin',
            'partner_id': 1,
            'email': 'myname@example.com'
        }
        for tgt_ver in ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1'):
            if not z0ctx['dry_run']:
                new_vals = clodoo.cvt_from_ver_2_ver(ctx,
                                                     model,
                                                     '7.0',
                                                     tgt_ver,
                                                     vals)
            else:
                new_vals = vals
            if tgt_ver == '6.1':
                TRES = ['name', 'user_email']
            else:
                TRES = sorted(vals.keys())
            sts = self.Z.test_result(z0ctx,
                                     'cvt_rec(res.users)',
                                     TRES,
                                     sorted(new_vals.keys()))
        return sts


if __name__ == "__main__":
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)
