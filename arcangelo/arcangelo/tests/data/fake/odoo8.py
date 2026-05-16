# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from openerp import api
from openerp.osv import osv


class ResPartner(osv.Model):
    _inherit = "res.partner"

    @api.multi
    def unlink(self):
        return super().unlink()

    @api.one
    def compute(self):
        return True
