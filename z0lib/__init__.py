# -*- coding: utf-8 -*-
from . import scripts
# try:
#     from .scripts import get_metadata
# except ImportError:
#     from scripts import get_metadata

try:
    from . import z0librun as z0lib
except ImportError:
    from z0lib import z0librun as z0lib
