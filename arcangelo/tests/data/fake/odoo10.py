# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def unlink(self):
        return super(ResPartner, self).unlink()

    @api.one
    def compute(self, item):
        if isinstance(item, basestring):
            return "str"
        elif isinstance(item, (int, long, float)):
            return "num"
        elif isinstance(item, (int, long)):
            return "int"
        return False
