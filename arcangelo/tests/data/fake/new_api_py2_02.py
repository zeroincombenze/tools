# flake8: noqa - pylint: skip-file
# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class ResExample(models.Model):
    def my_fun(self, param):
        super(ResExample, self).my_fun(param)
        raise UserError("Example")
