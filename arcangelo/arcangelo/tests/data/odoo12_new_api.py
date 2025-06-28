# flake8: noqa - pylint: skip-file
from odoo import fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def unlink(self, param):
        return super().unlink(param)

    def my_fun(self, param):
        super().my_fun(param)
        raise UserError("Example")
