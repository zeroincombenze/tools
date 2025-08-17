# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def unlink(self, param):
        return super(ResPartner, self).unlink(param)

    def my_fun(self, param):
        super(ResPartner, self).my_fun(param)
        raise UserError("Example")
