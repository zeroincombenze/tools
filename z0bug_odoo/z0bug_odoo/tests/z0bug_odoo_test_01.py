# -*- coding: utf-8 -*-
# Copyright (C) 2015-2021 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
# import os
import sys

from z0bug_odoo import z0bugodoo
from zerobug import z0test

__version__ = "2.0.0.1"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:
    def __init__(self, z0bug):
        self.Z = z0bug

    def test_01(self, z0ctx):
        # sts = TEST_SUCCESS
        res = {}
        if not z0ctx['dry_run']:
            res = z0bugodoo.get_test_values('res.partner', 'z0bug.res_partner_1')
        sts = self.Z.test_result(z0ctx, 'get_test_values()', bool(res), True)
        TEST = {
            'customer': 'True',
            'name': 'Prima Alpha S.p.A.',
            'street': 'Via I Maggio, 101',
            'zip': '20022',
            'city': 'Castano Primo',
            'email': 'info@prima-alpha.it',
            'website': 'http://www.prima-alpha.it',
            'phone': '+39 0255582285',
            'vat': 'IT00115719999',
        }
        for nm in TEST:
            sts += self.Z.test_result(z0ctx, 'partner.%s' % nm, res.get(nm), TEST[nm])
        return sts


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
