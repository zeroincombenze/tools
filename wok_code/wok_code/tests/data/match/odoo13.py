# flake8: noqa - pylint: skip-file
from odoo import api, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    # @api.multi
    def unlink(self):
        return super().unlink()

    # @api.one
    # TODO> Update code to multi or add self.ensure_one()
    def compute(self):
        return True
