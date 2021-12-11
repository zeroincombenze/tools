# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys

if eval(os.environ.get('TRAVIS_DEBUG_MODE', '0')) > 2:
    __version__ = '1.0.7.3'
    print('DEBUG: z0bug_odoo %s' % __version__)
    print('DEBUG: z0bug_odoo.sys.path=%s' % sys.path)

from . import scripts
from . import travis
from . import z0bug_odoo_lib
z0bugodoo = z0bug_odoo_lib.Z0bugOdoo()
try:
    import odoo.release as release
    from . import test_common
except ImportError:
    try:
        import openerp.release as release
        from . import test_common
    except ImportError:
        release = ''
if eval(os.environ.get('TRAVIS_DEBUG_MODE', '0')) > 2:
    if release:
        print('DEBUG: Odoo version detected: %s' % release.version)
    else:
        print('DEBUG: No Odoo environment found!')