# flake8: noqa - pylint: skip-file
# Copyright 2010-25, SHS-AV s.r.l. <https://www.zeroincombenze.it>
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    test_flag = fields.Boolean("Test")
