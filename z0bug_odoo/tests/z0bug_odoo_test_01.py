#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import sys
from zerobug import Z0BUG
# from z0bug_odoo import test_common
from zerobug import Z0testOdoo

__version__ = "0.1.0.1.2"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest():

    def __init__(self, z0bug):
        self.Z = z0bug

    def test_01(self, z0ctx):
        sts = TEST_SUCCESS
        res = {}
        if not z0ctx['dry_run']:
            # Build Odoo enviroment
            self.root = Z0BUG.build_os_tree(z0ctx, [])
            remote = 'OCA'
            reponame = 'OCB'
            branch = '10.0'
            odoo_path = os.path.join(self.root, branch)
            Z0testOdoo.git_clone(remote, reponame, branch, odoo_path)
            sys.path.append(odoo_path)
            from z0bug_odoo import z0bug_odoo_lib
            res = z0bug_odoo_lib.Z0bugOdoo().get_test_values(
                'res.partner','z0bug.res_partner_1')
        sts = self.Z.test_result(z0ctx,
                                 'get_test_values()',
                                 bool(res),
                                 True)
        TEST = {'customer': 'True',
                'name': 'Prima Distribuzione S.p.A.',
                'street': 'Via I Maggio, 11',
                'zip': '20022', 
                'city': 'Castano Primo',
                'email': 'info@prima-distribuzione.it',
                'website': 'www.prima-distribuzione.it',
                'phone': '+39 0255582285',
                'vat': 'IT00115719999'}
        for nm in TEST:
            sts = self.Z.test_result(z0ctx,
                                     'partner.%s' % nm,
                                     res.get(nm),
                                     TEST[nm])
        return sts


if __name__ == "__main__":
    ctx = Z0BUG.parseoptest(sys.argv[1:],
                             version=version())
    sts = Z0BUG.main_local(ctx, RegressionTest)
    exit(sts)
