# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp.osv.orm import except_orm


class ResExample(orm.Model):
    def my_fun(self, cr, uid, param, context=None):
        super(ResExample, self).my_fun(cr, uid, param, context=context)
        raise except_orm("Error", "Example")
