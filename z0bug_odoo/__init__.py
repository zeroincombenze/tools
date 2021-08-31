# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function

import os
import sys
if eval(os.environ.get('TRAVIS_DEBUG_MODE', '0')) > 2:
    __version__ = '1.0.5'
    print('DEBUG: z0bug_odoo %s' % __version__)
    print('DEBUG: z0bug_odoo.sys.path=%s' % sys.path)
try:
    from . import test_common
except BaseException:
    pass
from . import z0bug_odoo_lib
from zerobug import Z0BUG
