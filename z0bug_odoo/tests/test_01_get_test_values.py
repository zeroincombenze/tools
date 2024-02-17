# -*- coding: utf-8 -*-
# Copyright (C) 2015-2021 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""
# import os
import sys
import os
sys.path.insert(0,
                os.path.dirname(os.path.dirname(os.getcwd()))
                if os.path.basename(os.getcwd()) == "tests"
                else os.path.dirname(os.getcwd()))

from z0bug_odoo import z0bugodoo                                           # noqa: E402
from zerobug import z0test                                                 # noqa: E402

__version__ = "2.0.16"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class RegressionTest:

    def test_01(self):
        res = z0bugodoo.get_test_values('res.partner', 'z0bug.res_partner_1')
        TESTBED_VALUES = {
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
        for nm in TESTBED_VALUES:
            self.assertEqual(res.get(nm), TESTBED_VALUES[nm],
                             msg_info='partner.%s' % nm)


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )



