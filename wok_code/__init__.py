# -*- coding: utf-8 -*-


__version__ = '1.0.2.99'

from . import license_mgnt
try:
    from . import z0librun as z0lib
except ImportError:
    from z0lib import z0librun as z0lib
