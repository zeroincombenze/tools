# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
# Copyright 2013-26, Zeroincombenze srls <https://www.zeroincombenze.it>
from openerp.osv import osv, fields


class ResPartner(osv.Model):
    _inherit = 'res.partner'

    test_flag = fields.Boolean("Test")
