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
# import os
# import os.path
import sys

from zerobug import Z0test
try:
    from clodoo.clodoolib import build_odoo_param
except BaseException:
    from clodoolib import build_odoo_param


__version__ = "0.3.8.4"


MODULE_ID = 'clodoo'
VERSIONS_TO_TEST = ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1')
MAJVERS_TO_TEST = ('12', '11', '10', '9', '8', '7', '6')
# VERSIONS_TO_TEST = ('7.0',)
TEST_FAILED = 1
TEST_SUCCESS = 0


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib

    def test_01(self, z0ctx):
        TRES = {
            '6': '6.1',
            '7': '7.0',
            '8': '8.0',
            '9': '9.0',
            '10': '10.0',
            '11': '11.0',
            '12': '12.0',
        }
        for ver in MAJVERS_TO_TEST:
            res = build_odoo_param('FULLVER', odoo_vid=ver)
            sts = self.Z.test_result(z0ctx,
                                     'Full version %s' % ver,
                                     TRES[ver],
                                     res)
            if sts:
                break
            res = build_odoo_param('FULLVER', odoo_vid='V%s' % ver)
            sts = self.Z.test_result(z0ctx,
                                     'Full version V%s' % ver,
                                     TRES[ver],
                                     res)
            if sts:
                break
            res = build_odoo_param('FULLVER', odoo_vid=TRES[ver])
            sts = self.Z.test_result(z0ctx,
                                     'Full version %s' % TRES[ver],
                                     TRES[ver],
                                     res)
            if sts:
                break
            res = build_odoo_param('FULLVER', odoo_vid='v%s' % TRES[ver])
            sts = self.Z.test_result(z0ctx,
                                     'Full version v%s' % TRES[ver],
                                     TRES[ver],
                                     res)
            if sts:
                break
        return sts


if __name__ == "__main__":
    # import pdb
    # pdb.set_trace()
    Z = Z0test
    ctx = Z.parseoptest(sys.argv[1:],
                        version=version())
    sts = Z.main_local(ctx, Test)
    exit(sts)
