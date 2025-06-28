# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.osv.orm import except_orm


class ResPartner(osv.Model):
    _inherit = "res.partner"

    def unlink(self, cr, uid, param, context=None):
        return super(ResPartner, self).unlink(cr, uid, param)

    def my_fun(self, cr, uid, param, context=None):
        super(ResPartner, self).my_fun(cr, uid, param)
        raise except_orm("Error", "Example")
