# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2023 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
try:
    from odoo import models                                                # noqa: F401
except ImportError:
    from openerp.osv.orm import models                                     # noqa: F401
# import importlib
# try:
#     odoo_models = importlib.import_module(module)
# except NameError:
#     raise RuntimeError('No %s found!' % module)  # pragma: no cover


# class MetaModel(odoo_models.MetaModel):
#     pass
#
#
# class NewId(odoo_models.NewId):
#     pass
#
#
# class BaseModel(odoo_models.BaseModel):
#     pass
#
#
# class RecordCache(odoo_models.RecordCache):
#     pass
#
#
# class Model(models.Model):
#     pass
#
#
# class TransientModel(odoo_models.Model):
#     pass
