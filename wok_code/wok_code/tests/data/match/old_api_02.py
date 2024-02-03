# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from openerp.osv import fields, orm
from openerp.osv.osv import except_osv

class ResExample(orm.Model):
    def my_fun(self, cr, uid, param, context=None):
        super(ResExample, self).my_fun(cr, uid, param, context=context)
        raise except_osv("Error", "Example")
