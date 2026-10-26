# flake8: noqa - pylint: skip-file
# Copyright 2018-26, Zeroincombenze srls <https://www.zeroincombenze.it>
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    test_flag = fields.Boolean("Test")
