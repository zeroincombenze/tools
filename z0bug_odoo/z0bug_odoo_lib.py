# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function,unicode_literals
from past.builtins import basestring

import os
import sys
from zerobug import Z0BUG

__version__ = "0.1.0.1"

MODULE_ID = 'z0bug_odoo'
TEST_FAILED = 1
TEST_SUCCESS = 0


class Z0bugOdoo(Z0BUG):

    def __init__(self):
        self.tree_odoo10 = ['10.0',
                            '10.0/l10n-italy',
                            '10.0/l10n-italy/l10n_it_base',
        ]


    def build_os_tree_odoo(self, ctx, os_tree):
        """Create a filesytem tree to test odoo
        """
        root = False
        for path in os_tree:
            if isinstance(path,basestring):
                if path == 'odoo10':
                    pass
            else:
                root = Z0BUG.build_os_tree(ctx, os_tree)
        return root