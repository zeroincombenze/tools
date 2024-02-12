# flake8: noqa - pylint: skip-file
from odoo import fields, models
from odoo.exceptions import UserError


class ResExample(models.Model):
    def my_fun(self, param):
        super().my_fun(param)
        raise UserError("Example")
