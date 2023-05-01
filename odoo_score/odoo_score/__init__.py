# -*- coding: utf-8 -*-
import sys
from . import scripts
try:
    _o = "odoo."
    _release = __import__(_o + "release", fromlist=[None])
except ImportError:
    try:
        _o = "openerp."
        _release = __import__(_o + "release", fromlist=[None])
    except ImportError:
        _o = _release = ""
        _suffix = str(sys.version_info[0])
if _release:
    _suffix = _release.major_version.split(".")[0]
    try:
        models = __import__("odoo_score.models_" + _suffix, fromlist=[None]).odoo_models
    except ImportError:
        _suffix = str(sys.version_info[0])
        models = __import__("odoo_score.models_" + _suffix, fromlist=[None]).odoo_models
    for name in models.__dict__:
        if callable(getattr(models, name)):
            globals()[name] = getattr(models, name)
