# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
# Copyright 2013-25, SHS-AV s.r.l. <https://www.zeroincombenze.it>
from openerp.osv import osv, fields


class ResPartner(osv.Model):
    _inherit = 'res.partner'

    test_flag = fields.Boolean("Test")
