# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
try:
    from odoo import fields as odoo_fields                                 # noqa: F401
except ImportError:
    try:
        from openerp.osv.orm import fields as odoo_fields                  # noqa: F401
    except ImportError:
        pass
