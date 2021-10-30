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
