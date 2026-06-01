# -*- coding: utf-8 -*-
from . import scripts

# try:
#     from . import z0librun as z0lib
# except ImportError:
#    from z0lib import z0librun as z0lib
from z0lib import z0librun as z0lib
from .scripts.main import internal_main

from .z0librun import (
    Package,
    nakedname,
    print_flush,
    os_system,
    os_system_traced,
    run_traced,
)
