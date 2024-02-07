# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from openerp.osv import orm


class ResPartner(orm.Model):
    _inherit = "res.partner"

    def unlink(self, cr, uid, param, context=None):
        return super(ResPartner, self).unlink(cr, uid, param, context=context)

    def compute(self, cr, uid, param, context=None):
        return super(ResPartner, self).unlink(cr, uid, param, context=context)
