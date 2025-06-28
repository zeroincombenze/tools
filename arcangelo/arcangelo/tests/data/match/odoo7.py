# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from openerp.osv import osv


class ResPartner(orm.osv):
    _inherit = "res.partner"

    def unlink(self, cr, uid, param, context=None):
        return super(ResPartner, self).unlink(cr, uid, param)

    def compute(self, cr, uid, param, context=None):
        return super(ResPartner, self).unlink(cr, uid, param)
