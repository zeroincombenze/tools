# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
# Copyright 2014-26, Zeroincombenze srls <https://www.zeroincombenze.it>
from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    test_flag = fields.Boolean("Test")
