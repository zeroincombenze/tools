#
# Copyright (C) 2018-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
try:
    from odoo import models as odoo_models                                 # noqa: F401
except ImportError:
    try:
        from openerp.osv.orm import models as odoo_models                  # noqa: F401
    except ImportError:
        pass

# class BaseModel(odoo_models.BaseModel):
#     __metaclass__ = odoo_models.BaseModel
