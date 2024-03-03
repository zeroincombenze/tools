# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
from . import scripts
from . import travis
from . import z0bug_odoo_lib

z0bugodoo = z0bug_odoo_lib.Z0bugOdoo()
# TODO> Remove early
Z0BUG = z0bugodoo
try:
    import odoo.release as release
    # from . import test_common
except ImportError:
    try:
        import openerp.release as release
        # from . import test_common
    except ImportError:
        release = ''

__version__ = '2.0.17'
if eval(os.environ.get('TRAVIS_DEBUG_MODE', '0')) > 2:
    print('DEBUG: z0bug_odoo %s' % __version__)
    print('DEBUG: z0bug_odoo.sys.path=%s' % sys.path)
    if release:
        print('DEBUG: Odoo version detected: %s' % release.version)
    else:
        print('DEBUG: No Odoo environment found!')






