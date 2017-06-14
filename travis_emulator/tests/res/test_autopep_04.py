""" Copyright (C) openerp-italia.org
"""

Namespace = pyxb.namespace.NamespaceForURI('urn:www.agenziaentrate.gov.it:specificheTecniche:sco:ivp', create_if_missing=True)

class example():
    _columns = {
        'debit_credit_vat_account_line_ids': fields.one2many('debit.credit.vat.account.line', 'statement_id', 'Debit/Credit VAT', help='The accounts containing the debit/credit VAT amount', states={'confirmed': [('readonly', True)], 'paid': [('readonly', True)], 'draft': [('readonly', False)]}),
    }
    def test(self):
        p = 1 * (2
            + 3)
