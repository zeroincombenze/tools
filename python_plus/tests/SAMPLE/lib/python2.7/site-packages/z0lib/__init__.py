from . import scripts
try:
    from . import z0librun as z0lib
except ImportError:
    from z0lib import z0librun as z0lib
