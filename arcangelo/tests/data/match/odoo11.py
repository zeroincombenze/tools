# flake8: noqa - pylint: skip-file
from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def unlink(self):
        return super().unlink()

    @api.one
    def compute(self, item):
        if isinstance(item, str):
            return "str"
        elif isinstance(item, (int, float)):
            return "num"
        elif isinstance(item, int):
            return "int"
        return False
