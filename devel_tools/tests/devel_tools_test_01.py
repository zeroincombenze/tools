#!/usr/bin/env python
# Copyright (C) 2018-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
    Devel tools Regression Test Suite
"""
from __future__ import print_function, unicode_literals

# import pdb
import sys
from zerobug import Z0BUG
from pull_from_oca import rsync_module


MODULE_ID = 'devel_tools'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "1.0.0.5"


def version():
    return __version__


class Test():

    def __init__(self, zarlib):
        self.Z = zarlib

    def setup_file_base_oca(self):
        with open('%s/__manifest__.py' % self.BASE_OCA, 'w') as fd:
            fd.write('''{'version': '10.0.1.0.0.5'}''')
        with open('%s/__init__.py' % self.BASE_OCA, 'w') as fd:
            fd.write('''# 10.0.1.0.0.5''')

    def setup_file_base_z0(self):
        with open('%s/__manifest__.py' % self.BASE_Z0, 'w') as fd:
            fd.write('''{'version': '10.0.1.0.1'}''')
        with open('%s/__init__.py' % self.BASE_Z0, 'w') as fd:
            fd.write('''# 10.0.1.0.1''')

    def setup_file_midea_oca(self):
        with open('%s/__manifest__.py' % self.MIDEA_OCA, 'w') as fd:
            fd.write('''{'version': '10.0.1.2.3'}''')
        with open('%s/__init__.py' % self.MIDEA_OCA, 'w') as fd:
            fd.write('''# 10.0.1.2.3''')

    def setup_file_midea_z0(self):
        with open('%s/__manifest__.py' % self.MIDEA_Z0, 'w') as fd:
            fd.write('''{'version': '10.0.1.2.4'}''')
        with open('%s/__init__.py' % self.MIDEA_Z0, 'w') as fd:
            fd.write('''# 10.0.1.2.4''')

    def setup(self, z0ctx):
        self.BASE = 'odoo/addons/base'
        self.MIDEA = 'my_repo/midea'
        self.ADDONS = 'addons'
        self.os_tree = []
        for ver in ('10.0', 'oca10'):
            self.os_tree.append('%s/%s' % (ver, self.BASE))
            self.os_tree.append('%s/%s' % (ver, self.MIDEA))
            self.os_tree.append('%s/%s' % (ver, self.ADDONS))
        self.root = self.Z.build_os_tree(z0ctx, self.os_tree)
        self.ROOT_OCA = '%s/oca10' % self.root
        self.ROOT_Z0 = '%s/10.0' % self.root
        self.BASE_OCA = '%s/%s' % (self.ROOT_OCA, self.BASE)
        self.BASE_Z0 = '%s/%s' % (self.ROOT_Z0, self.BASE)
        self.MIDEA_OCA = '%s/%s' % (self.ROOT_OCA, self.MIDEA)
        self.MIDEA_Z0 = '%s/%s' % (self.ROOT_Z0, self.MIDEA)
        self.setup_file_base_oca()
        self.setup_file_base_z0()
        self.setup_file_midea_oca()
        self.setup_file_midea_z0()

    def test_01(self, z0ctx):
        self.setup(z0ctx)
        res = True
        rsync_module(self.ROOT_OCA,
                     )
        
        sts = self.Z.test_result(z0ctx,
                                 "Test 1",
                                 True,
                                 res)
        return sts


if __name__ == "__main__":
    exit(Z0BUG.main_local(
        Z0BUG.parseoptest(
            sys.argv[1:],
            version=version()),
        Test))
