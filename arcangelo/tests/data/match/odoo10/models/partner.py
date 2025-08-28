# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
# Copyright 2016-25, SHS-AV s.r.l. <https://www.zeroincombenze.it>
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    test_flag = fields.Boolean("Test")
