# -*- coding: utf-8 -*-
## from . import scripts
# # Comment follow lines if package version < 2.0.4
# from odoo.tools.translate import _                                         # noqa: F403
# try:
#     from odoo.models import *                                              # noqa: F403
# except ImportError:
#     try:
#         from openerp.osv.orm.model import *                                # noqa: F403
#     except ImportError:
#         pass
#
# try:
#     from odoo.fields import *                                              # noqa: F403
# except ImportError:
#     try:
#         from openerp.osv.orm.fields import *                               # noqa: F403
#     except ImportError:
#         pass
#
# try:
#     from odoo.api import *                                                 # noqa: F403
# except ImportError:
#     pass
#     # raise RuntimeError('No odoo / openerp environment found!')  # pragma: no cover
#
# from . import models
# from . import fields
# from . import api
try:
    _o = "odoo."
    _release = __import__(_o + "release", fromlist=[None])
except ImportError:
    try:
        _o = "openerp."
        _release = __import__(_o + "release", fromlist=[None])
    except ImportError:
        _o = _release = ""
        _suffix = "barely"
else:
    _suffix = _release.major_version.split(".")[0]
#
try:
    models = __import__("odoo_score.models_" + _suffix, fromlist=[None]).models
except ImportError:
    models = __import__("odoo_score.models_barely", fromlist=[None]).models
for name in models.__dict__:
    if callable(getattr(models, name)):
        globals()[name] = getattr(models, name)
