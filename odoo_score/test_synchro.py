#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()                                 # noqa: E402
from past.builtins import basestring
from builtins import *                                             # noqa
from builtins import input

import os
import sys
from datetime import date, datetime
import time
from os0 import os0
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib
# import pdb      # pylint: disable=deprecated-module

__version__ = "1.0.0.3"

L_NUM_FATT1 = 'FAT/2020/0001'
L_NUM_FATT2 = 'FAT/2020/0002'
X_NUM_DDT = '1234'
# X_NUM_ORDER = '1234'
L_NUM_ORDER = 'SO002'

CANDIDATE_KEYS = (
    'acc_number', 'login','default_code', 'code', 'key',
    'serial_number', 'description', 'comment', 'name', 'dim_name',
)
RESET_FIELD = (
    'id', 'prezzo_unitario', 'goods_description_id', 'carriage_condition_id',
    'transportation_method_id', 'country_id', 'state_id', 'vat', 'fiscalcode',
    'electronic_invoice_subjected', 'firstname', 'lastname',
)
WRONG_DATA = {
    'region': ['TO', '(TO)'],
    'street': ['Via Porta Nuova', 'Via Porta Vecchia'],
}
SOME_DEFAULT = {
    'res.country.state': [
        {
            'domain': ['code', 'in', ['TO', 'MI', 'BO']],
            'value': ['country_id', 'res.country.IT']
        }
    ],
    'product.product': [
        {
            'domain': ['default_code', '=~', 'AA'],
            'value': ['product_tmpl_id', 'product.template.A'],
        },
        {
            'domain': ['default_code', '=~', 'BB'],
            'value': ['product_tmpl_id', 'product.template.B'],
        },
        {
            'domain': ['default_code', '=~', 'CC'],
            'value': ['product_tmpl_id', 'product.template.C'],
        },
    ],
}
SET_SOME_DEFAULT = {
    'res.country': [
        {
            'domain': ['code', '=', 'IT'],
            'value': 'res.country.IT',
        }
    ],
    'product.template': [
        {
            'domain': ['default_code', '=~', 'AA'],
            'value': 'product.template.A',
        },
        {
            'domain': ['default_code', '=~', 'BB'],
            'value': 'product.template.B',
        },
        {
            'domain': ['default_code', '=~', 'CC'],
            'value': 'product.template.C',
        },
    ],
}
NAME_REFS = {
    'account.account.type': [
        {
            'domain': ['name', '=', 'Receivable'],
            'value': ['name', 'Crediti clienti']
        },
        {
            'domain': ['name', '=', 'Payable'],
            'value': ['name', 'Debiti fornitori']
        },
        {
            'domain': ['name', '=', 'Bank and Cash'],
            'value': ['name', 'Banca o cassa']
        },
        {
            'domain': ['name', '=', 'Credit Card'],
            'value': ['name', 'Carta di Credito']
        },
        {
            'domain': ['name', '=', 'Current Assets'],
            'value': ['name', 'Attività correnti']
        },
        {
            'domain': ['name', '=', 'Non-current Assets'],
            'value': ['name', 'Attività non correnti']
        },
        {
            'domain': ['name', '=', 'Prepayments'],
            'value': ['name', 'Risconti']
        },
        {
            'domain': ['name', '=', 'Fixed Assets'],
            'value': ['name', 'Immobilizzazioni']
        },
        {
            'domain': ['name', '=', 'Current Liabilities'],
            'value': ['name', 'Passività correnti']
        },
        {
            'domain': ['name', '=', 'Non-current Liabilities'],
            'value': ['name', 'Passività non correnti']
        },
        {
            'domain': ['name', '=', 'Equity'],
            'value': ['name', 'Capitale']
        },
        {
            'domain': ['name', '=', 'Current Year Earnings'],
            'value': ['name', 'Risultato operativo']
        },
        {
            'domain': ['name', '=', 'Income'],
            'value': ['name', 'Ricavi']
        },
        {
            'domain': ['name', '=', 'Other Income'],
            'value': ['name', 'Altri ricavi operativi']
        },
        {
            'domain': ['name', '=', 'Depreciation'],
            'value': ['name', 'Ammortamento']
        },
        {
            'domain': ['name', '=', 'Expenses'],
            'value': ['name', 'Costi']
        },
        {
            'domain': ['name', '=', 'Cost of Revenue'],
            'value': ['name', 'Costi operativi']
        },
    ],
    'product.template': [
        {
            'domain': ['default_code', '=~', 'AA'],
            'value': ['name', 'Prodotto Alpha'],
        },
        {
            'domain': ['default_code', '=~', 'BB'],
            'value': ['name', 'Prodotto Beta'],
        },
        {
            'domain': ['default_code', '=~', 'CC'],
            'value': ['name', 'Prodotto Chi'],
        },
    ],
}

TNL_VG7_TABLES = {
    'account.account': '',
    'account.account.type': '',
    'account.invoice': '',
    'account.invoice.line': '',
    'account.payment.term': 'payments',
    'account.tax': 'tax_codes',
    # 'crm.team': '',
    'italy.conai.product.category': 'conai',
    'italy.conai.partner.category': 'esenzione_conai',
    'product.product': 'products',
    'product.template': '',
    'product.uom': 'ums',
    'res.currency': '',
    'res.country': 'countries',
    'res.country.state': 'regions',
    'res.partner': 'customers',
    'res.partner.shipping': 'customers_shipping_addresses',
    'res.partner.supplier': 'suppliers',
    'stock.picking.package.preparation': 'ddt',
    'stock.picking.package.preparation.line': '',
    'stock.picking.transportation_reason': '',
    'sale.order': '',
    'sale.order.line': '',
}

TNL_OE8_TABLES = {
}

TNL_VG7_DICT = {
    'account.account': {
    },
    'account.invoice': {
        'number': 'move_name',
    },
    'account.invoice.line': {
        'partner_id': False,
        'vg7_partner_id': False,
    },
    'account.payment.term': {
        'code': False,
        'description': 'name',
    },
    'account.payment.term.line': {
        'scadenza': False,
        'fine_mese': False,
        'giorni_fine_mese': 'payment_days',
    },
    'account.tax': {
        'aliquota': 'amount',
        'code': ['name', 'nounknown'],
        'description': ['name', 'nounknown'],
    },
    'italy.conai.product.category': {
        'description': 'name',
        'prezzo_unitario': 'conai_price_unit',
    },
    'product.product': {
        'conai_id': 'conai_category_id',
        'code': 'default_code',
        'description': 'name',
    },
    'product.template': {
        'conai_id': False,
        'code': 'default_code',
        'description': 'name',
    },
    'product.uom': {
        'code': 'name',
    },
    'res.country': {
        'description': ['name', 'nocase'],
    },
    'res.country.state': {
        'description': ['name', 'nocase'],
    },
    'res.partner': {
        'bank_id': False,
        'billing_pec': 'pec_destinatario',
        'cf': 'fiscalcode',
        'codice_univoco': 'codice_destinatario',
        'company': 'name',
        'country': 'country_id',
        'customer_id': 'parent_id',
        'customer_billing_id': 'vg7_id',
        'customer_shipping_id': 'vg7_id',
        'esonerato_fe': 'electronic_invoice_subjected',
        'name': 'firstname',
        'note': 'invoice_warn_msg',
        'payment_id': 'property_payment_term_id',
        'piva': 'vat',
        'postal_code': 'zip',
        'region': 'state_id',
        'region_id': 'state_id',
        'surename': 'lastname',
        'tax_code_id': False,
        'telephone2': 'mobile',
        'telephone': 'phone',
        'street_number': False,
    },
    'res.partner.bank': {
        'IBAN': 'acc_number',
        'customer_id': 'partner_id',
        'description': False,
    },
    'sale.order': {
        'name': 'client_order_ref',
        'date': 'date_order',
        'order_number': ['name', 'nounknown'],
        'customer_id': 'partner_id',
        'payment_id': 'payment_term_id',
        'customer_shipping_id': 'partner_shipping_id',
        'courier_id': False,
        'agent_id': False
    },
    'sale.order.line': {
        'product_name': 'name',
        'unitary_price': 'price_unit',
        'quantity': 'product_uom_qty',
        'partner_id': False,
        'vg7_partner_id': False,
    },
    'stock.picking.package.preparation': {
        'numero_colli': 'parcels',
        'customer_id': 'partner_id',
        'customer_shipping_id': 'partner_shipping_id',
        'vettori_prima_riga': False,
        'voce_doganale': False,
        'aspetto_esteriore_dei_beni': 'goods_description_id',
        'causal_id': 'transportation_reason_id',
        'vettori_seconda_riga': False,
        'note': False,
        'peso_netto': False,
        'tipo_porto': False,
        'peso_lordo': False,
        'ora_ritiro': False,
        'data_emissione': 'date',
        'data_ritiro': 'date_done',
        'mezzo': False,
    },
    'stock.picking.package.preparation.line': {
        # 'ddt_id': 'package_preparation_id',
        'ddt_id': False,
        'descrizione': 'name',
        'quantita': 'product_uom_qty',
        'prezzo_unitario': 'price_unit',
        'order_id': 'sale_id',
        'order_row_id': 'sale_line_id',
        'vg7:tax_code_id': 'tax_ids',
        'product_id': False,
        'tax_code_id': False,
        'tax_id': False,
        'peso': 'weight',
        'um': False,
        'um_id': 'product_uom_id',
        # 'um_id': False,
        'conai_id': 'conai_category_id',
    },
    'stock.picking.transportation_reason': {
        'description': 'name',
    },
}

TNL_OE8_DICT = {
    'account.account.type': {
        'code': False,
        'report_type': 'type',
    },
}

TABLE_OF_REF_FIELD = {
    'company_id': 'res.company',
    'country_id': 'res.country',
    'conai_category_id': 'italy.conai.product.category',
    'goods_description_id': 'stock.picking.goods_description',
    'invoice_id': 'account.invoice',
    'journal_id': 'account.journal',
    'order_id': 'sale.order',
    'partner_id': 'res.partner',
    'partner_shipping_id': 'res.partner',
    'payment_term_id': 'account.payment.term',
    'product_id': 'product.product',
    'product_tmpl_id': 'product.template',
    'product_uom_id': 'product.uom',
    'property_payment_term_id': 'account.payment.term',
    'sale_id': 'sale.order',
    'sale_line_id': 'sale.order.line',
    'state_id': 'res.country.state',
    'transportation_reason_id': 'stock.picking.transportation_reason',
    'user_type_id': 'account.account.type',
}
MODULE_LIST = [
    'account', 'account_payment_term_extension', 'date_range', 'purchase',
    'sale', 'stock', 'l10n_it_fiscal',
    'l10n_it_fiscalcode', 'l10n_it_ddt',
    'l10n_it_einvoice_out', 'l10n_it_ricevute_bancarie',
    'connector_vg7',
    'partner_bank',
    'mk_test_env'
]

# Warning! Data name not ending with "_DEF" is saved into csv file so every
# record must be contains all fields e and all fields must be in the same order
RES_COUNTRY_VG7 = [
    {'id': 39, 'code': 'IT', 'description': 'Italia'},
]
RES_COUNTRY_OE8 = [
    {'id': 39, 'code': 'IT', 'name': 'Italia'},
]
RES_COUNTRY_STATE_VG7 = [
    {'id': 2, 'code': 'MI', 'description': 'Milano'},
    {'id': 11, 'code': 'TO', 'description': 'Torino'},
    {'id': 54, 'code': 'BO', 'description': 'Bologna'},
]
RES_COUNTRY_STATE_OE8 = [
    {'id': 2, 'country_id': 39, 'code': 'MI', 'name': 'Milano'},
    {'id': 11, 'country_id': 39, 'code': 'TO', 'name': 'Torino'},
    {'id': 54, 'country_id': 39, 'code': 'BO', 'name': 'Bologna'},
]
ACCOUNT_ACCOUNT_TYPE_DEF = [
    {'id': 'account.data_account_type_receivable',
     'name': 'Receivable', 'type': 'receivable'},
    {'id': 'account.data_account_type_payable',
     'name': 'Payable', 'type': 'payable'},
    {'id': 'account.data_account_type_liquidity',
     'name': 'Bank and Cash', 'type': 'liquidity'},
    {'id': 'account.data_account_type_credit_card',
     'name': 'Credit Card', 'type': 'liquidity'},
    {'id': 'account.data_account_type_current_assets',
     'name': 'Current Assets', 'type': 'other'},
    {'id': 'account.data_account_type_non_current_assets',
     'name': 'Non-current Assets', 'type': 'other'},
    {'id': 'account.data_account_type_prepayments',
     'name': 'Prepayments', 'type': 'other'},
    {'id': 'account.data_account_type_fixed_assets',
     'name': 'Fixed Assets', 'type': 'other'},
    {'id': 'account.data_account_type_current_liabilities',
     'name': 'Current Liabilities', 'type': 'other'},
    {'id': 'account.data_account_type_non_current_liabilities',
     'name': 'Non-current Liabilities', 'type': 'other'},
    {'id': 'account.data_account_type_equity',
     'name': 'Equity', 'type': 'other'},
    {'id': 'account.data_unaffected_earnings',
     'name': 'Current Year Earnings', 'type': 'other'},
    {'id': 'account.data_account_type_other_income',
     'name': 'Other Income', 'type': 'other'},
    {'id': 'account.data_account_type_revenue',
     'name': 'Income', 'type': 'other'},
    {'id': 'account.data_account_type_depreciation',
     'name': 'Depreciation', 'type': 'other'},
    {'id': 'account.data_account_type_expenses',
     'name': 'Expenses', 'type': 'other'},
    {'id': 'account.data_account_type_direct_costs',
     'name': 'Cost of Revenue', 'type': 'other'},
]
ACCOUNT_ACCOUNT_TYPE_OE8 = [
    {'id': 1,
     'code': 'receivable', 'name': 'Receivable', 'report_type': 'receivable'},
    {'id': 2, 'code': 'payable', 'name': 'Payable', 'report_type': 'payable'},
    {'id': 3, 'code': 'bank', 'name': 'Bank', 'report_type': 'liquidity'},
    {'id': 4, 'code': 'cash', 'name': 'Cash', 'report_type': 'liquidity'},
    {'id': 5, 'code': 'asset', 'name': 'Assets', 'report_type': 'other'},
    {'id': 6, 'code': 'liability', 'name': 'Liability',
     'report_type': 'other'},
    {'id': 7, 'code': 'income', 'name': 'Income', 'report_type': 'other'},
    {'id': 8, 'code': 'expense', 'name': 'Expense', 'report_type': 'other'},
    {'id': 9,
     'code': 'credit_card', 'name': 'Credit Card', 'report_type': 'liquidity'},
    {'id': 10, 'code': 'equity', 'name': 'Equity', 'report_type': 'other'},
]
ACCOUNT_TAX_VG7 = [
    {'id': 22, 'code': '22%', 'description': '', 'aliquota': 22},
    {'id': 4, 'code': '4%', 'description': '', 'aliquota': 4},
    {'id': 101, 'code': 'a101', 'description': 'Forfettario art 101',
     'aliquota': 0},
]
ACCOUNT_TAX_OE8 = [
    {'id': 1, 'description': '22v', 'name': 'IVA 22%', 'amount': 22,
     'type_tax_use': 'sale'},
    {'id': 4, 'description': '4v', 'name': 'IVA 4%', 'amount': 4,
     'type_tax_use': 'sale'},
    {'id': 2, 'description': '22a', 'name': 'IVA 22%', 'amount': 22,
     'type_tax_use': 'purchase'},
]
ACCOUNT_PAYMENT_TERM = [
    {'id': 30, 'code': '30', 'description': 'RiBA 30GG/FM'},
    {'id': 3060, 'code': '31', 'description': 'RiBA 30/60 GG/FM'},
]
ACCOUNT_CONAI_DEF = [
    {'code': 'CA', 'name': 'Carta', 'conai_price_unit': 30},
]
ACCOUNT_CONAI_VG7 = [
    {'id': 1, 'code': 'CA',
     'description': 'Carta ondulata', 'prezzo_unitario': 35},
]
PRODUCT_PRODUCT_DEF = [
    {'id': 'z0bug.product_product_1',
     'default_code': 'AAA', 'name': 'Product Alpha', 'conai_id': False},
    {'id': 'z0bug.product_product_2',
     'default_code': 'BBB', 'name': 'Product Beta', 'conai_id': False},
    {'id': 'z0bug.product_product_3',
     'default_code': 'CCC', 'name': 'Product CC', 'conai_id': False},
]
PRODUCT_PRODUCT_VG7 = [
    {'id': 1, 'code': 'AAA', 'description': 'Product Alpha', 'conai_id': 1},
    {'id': 2, 'code': 'BBB', 'description': 'Product Beta', 'conai_id': 1},
    {'id': 3, 'code': 'CCC', 'description': 'Product CC', 'conai_id': False},
]
PRODUCT_TEMPLATE_DEF = [
    {'id': 'z0bug.product_template_1',
     'default_code': 'AA', 'name': 'Product Alpha', 'conai_id': False},
    {'id': 'z0bug.product_template_2',
     'default_code': 'BB', 'name': 'Product Beta', 'conai_id': False},
    {'id': 'z0bug.product_template_3',
     'default_code': 'CC', 'name': 'Product Chi', 'conai_id': False},
]
PRODUCT_TEMPLATE_VG7 = [
    {'id': 1, 'code': 'AA', 'description': 'Product Alpha', 'conai_id': 1},
    {'id': 2, 'code': 'BB', 'description': 'Product Beta', 'conai_id': 1},
    {'id': 3, 'code': 'CC', 'description': 'Product CC', 'conai_id': False},
]
RES_PARTNER_SHIPPING = [
    {'customer_shipping_id': 101, 'customer_id': 1,
     'shipping_name': 'Partner A', 'shipping_surename': '',
     'shipping_country_id': 39, 'shipping_region_id': 11,
     'shipping_postal_code': '35100',
     'shipping_city': 'Padova',
     },
    {'customer_shipping_id': 102, 'customer_id': 2,
     'shipping_name': 'Magazzino', 'shipping_surename': '',
     'shipping_country_id': 39, 'shipping_region_id': 11,
     'shipping_postal_code': '10061',
     'shipping_city': 'S. Secondo fraz. Pinasca',
     },
]
RES_PARTNER_BILLING = [
    {'customer_billing_id': 1, 'customer_id': 1,
     'billing_country_id': 39, 'billing_name': ' ',
     'billing_postal_code': '',
     'billing_city': 'Torino',
     'billing_piva': '00385870480'
     },
    {'customer_billing_id': 2, 'customer_id': 2,
     'billing_country_id': 39, 'billing_name': ' ',
     'billing_postal_code': '',
     'billing_city': '',
     'billing_piva': ''
     },
]
RES_PARTNER_DEF = [
    {
        'id': 'z0bug.res_partner_2',
        'name': 'Agro Latte Due  s.n.c.',
        'street': 'Via II Giugno, 22',
        'country_id': 'base.it',
        'zip': '10060',
        'city': 'S. Secondo Pinerolo',
        'state_id': 'base.state_it_to',
        'vat': 'IT02345670018',
        'goods_description_id': 'l10n_it_ddt.goods_description_SFU',
        'carriage_condition_id': 'l10n_it_ddt.carriage_condition_PAF',
        'transportation_method_id': 'l10n_it_ddt.transportation_method_COR',
    }
]
RES_PARTNER_VG7 = [
    {
        'id': 1, 'company': 'Partner A', 'name': None, 'surename': None,
        'street': 'Via Porta Nuova', 'street_number': '13',
        'postal_code': '10100', 'city': 'Torino',
        'region': 'TORINO', 'region_id': 11,
        'country_id': 'Italia',
        'esonerato_fe': '1',
        'piva': '00385870480', 'cf': '',
        'payment_id': 30,
        'goods_description_id': False,
        'carriage_condition_id': False,
        'transportation_method_id': False,
        'splitmode': None,
    },
    {
        'id': 2, 'company': None, 'name': None, 'surename': None,
        'street': None, 'street_number': None,
        'postal_code': None, 'city': None,
        'region': None, 'region_id': None,
        'country_id': None,
        'esonerato_fe': None,
        'piva': '02345670018', 'cf': '',
        'payment_id': None,
        'goods_description_id': None,
        'carriage_condition_id': None,
        'transportation_method_id': None,
        'splitmode': None,
    },
    {
        'id': 7, 'company': None, 'name': None, 'surename': None,
        'street': None, 'street_number': None,
        'postal_code': None, 'city': None,
        'region': None, 'region_id': None,
        'country_id': None,
        'esonerato_fe': None,
        'piva': None, 'cf': None,
        'payment_id': None,
        'goods_description_id': 'l10n_it_ddt.goods_description_SFU',
        'carriage_condition_id': 'l10n_it_ddt.carriage_condition_PAF',
        'transportation_method_id': 'l10n_it_ddt.transportation_method_COR',
        'splitmode': None,
    },
    {
        'id': 17, 'company': None, 'name': 'Mario', 'surename': 'Rossi',
        'street': None, 'street_number': None,
        'postal_code': None, 'city': None,
        'region': None, 'region_id': None,
        'country_id': None,
        'esonerato_fe': None,
        'piva': None, 'cf': 'RSSMRA69C02D612M',
        'payment_id': None,
        'goods_description_id': False,
        'carriage_condition_id': False,
        'transportation_method_id': False,
        'splitmode': 'LF',
    },
]
STOCK_PICKING_PACKAGE_PREPARATION = [
    {
        'id': 7,
        'ddt_number': '1234',
        'numero_colli': 1,
        'customer_id': 7,
        'vettori_prima_riga': '',
        'vettori_seconda_riga': '',
        'voce_doganale': '',
        'aspetto_esteriore_dei_beni': 'BANCALI',
        'causal_id': 3,
        'note': '',
        'peso_netto': 9.0,
        'tipo_porto': 'FRANCO',
        'peso_lordo': 10.0,
        'ora_ritiro': '18:30:00',
        'data_emissione': '2020-11-30',
        'data_ritiro': '2020-11-30',
        'mezzo': u'MITTENTE'
    }
]

def env_ref(ctx, xref, retxref_id=None):
    xrefs = xref.split('.')
    if len(xrefs) == 2:
        model = 'ir.model.data'
        ids = clodoo.searchL8(ctx, model, [('module', '=', xrefs[0]),
                                           ('name', '=', xrefs[1])])
        if ids:
            if retxref_id:
                return ids[0]
            return clodoo.browseL8(ctx, model, ids[0]).res_id
    return False


def write_log(ctx, mesg, eol=None):
    with open(ctx['logfn'], 'a') as fd:
        if eol:
            fd.write('%s\n' % mesg)
        else:
            fd.write(mesg)


def compare_some(dict_item, vals, field=None):
    field = field or dict_item['domain'][0]
    if ((dict_item['domain'][1] == '=' and
         vals[field] == dict_item['domain'][2]) or
            (dict_item['domain'][1] == '=~' and
             vals[field].startswith(dict_item['domain'][2])) or
            (dict_item['domain'][1] == 'in' and
             vals[field] in dict_item['domain'][2])):
        return True
    return False


def delete_record(ctx, model, domains, multi=False, action=None,
                  childs=None, company_id=False):
    print('Delete records %s of model %s ...' % (domains, model))
    excl_list = [rec.res_id for rec in clodoo.browseL8(
        ctx, 'ir.model.data', clodoo.searchL8(
            ctx, 'ir.model.data', [('model', '=', model)]))]
    if not isinstance(domains, (list, tuple)):
        domains = [domains]
    single_query = True
    for domain in domains:
        if isinstance(domain, (basestring, int)):
            single_query = False
            break
        elif isinstance(domain, (list, tuple)):
            break
    if single_query:
        domains = [domains]
    for domain in domains:
        rec_ids = []
        if isinstance(domain, basestring):
            rec_ids = env_ref(ctx, domain)
            rec_ids = [rec_ids] if rec_ids else []
        elif isinstance(domain, int):
            full_domain = []
            for test_prefix in ('vg7:', 'oe8:'):
                ext_name = '%s_id' % test_prefix.split(
                    ':')[0] if test_prefix else False
                if domain == -1:
                    leaf = [(ext_name, '!=', False), (ext_name, '!=', 0)]
                else:
                    leaf = [(ext_name, '=', domain)]
                if not full_domain:
                    full_domain = leaf
                else:
                    if len(leaf) > 1:
                        leaf.insert(0, '&')
                    if len(full_domain) == 2:
                        full_domain.insert(0, '&')
                    full_domain.insert(0, '|')
                    full_domain.extend(leaf)
            domain = full_domain
        if not rec_ids:
            if company_id:
                domain.append(('company_id', '=', company_id))
            if excl_list:
                domain.append(('id', 'not in', excl_list))
            rec_ids = clodoo.searchL8(ctx, model, domain)
        if (not multi and len(rec_ids) == 1) or (multi and len(rec_ids)):
            if action:
                if not isinstance(action, (list, tuple)):
                    action = [action]
                for act in action:
                    if act == 'move_name=':
                        clodoo.writeL8(ctx, model, rec_ids, {'move_name': ''})
                    else:
                        try:
                            clodoo.executeL8(ctx, model, act, rec_ids)
                        except BaseException:
                            print('Warning! Cannot execute %s.%s' % (
                                model, act
                            ))
            if childs:
                for parent in clodoo.browseL8(ctx, model, rec_ids):
                    for rec in parent[childs]:
                        if rec.id in rec_ids:
                            continue
                        try:
                            clodoo.unlinkL8(ctx, model, rec.id)
                            write_log(ctx,
                                '>>> %s.unlink(%s)' % (model, rec.id))
                        except BaseException as e:
                            print('Error %s removing records ...' % e)
            try:
                clodoo.unlinkL8(ctx, model, rec_ids)
                write_log(ctx,
                    '>>> %s.unlink(%s)' % (model, rec_ids))
            except BaseException as e:
                print('Error %s removing records ...' % e)
                if ctx['ask']:
                    input('Press RET to continue')
                else:
                    exit(1)


def write_record(ctx, model, domain, vals, company_id=False, create=None,
                 unique=None):
    if isinstance(domain, basestring):
        ids = env_ref(ctx, domain)
        ids = [ids] if ids else []
    else:
        if company_id:
            domain.append(('company_id', '=', company_id))
        ids = clodoo.searchL8(ctx, model, domain)
    if ids:
        clodoo.writeL8(ctx, model, ids, vals)
        if unique and len(ids) > 1:
            print('Warning: Too many records "%s.%s"' % (model, domain))
            delete_record(
                ctx, model, [('id', 'in', ids[1:])])
    elif create:
        ids = [clodoo.createL8(ctx, model, vals)]
    return ids


def reset_ext_id(model):
    domain = ['|']
    if model == 'res.partner':
        domain.append('|')
    for nm in ('vg7_id', 'oe8_id'):
        domain.append((nm, '>', 0))
    if model == 'res.partner':
        domain.append(('vg72_id', '>', '0'))
    vals = {
        'vg7_id': False,
        'oe8_id': False,
    }
    if model == 'res.partner':
        vals['vg72_id'] = False
    ids = clodoo.searchL8(ctx, model, domain)
    for id in ids:
        clodoo.writeL8(ctx, model, id, vals)


def rm_file_2_pull(ext_model):
    if os.path.isfile(os.path.expanduser('~/clodoo/%s.csv' % ext_model)):
        os.unlink(os.path.expanduser('~/clodoo/%s.csv' % ext_model))


def set_sequence(ctx, domain, next_number, multi=False, company_id=False):
    model = 'ir.sequence'
    if company_id:
        domain.append(('company_id', '=', company_id))
    ids = clodoo.searchL8(ctx, model, domain)
    if (not multi and len(ids) == 1) or (multi and len(ids)):
        for rec in clodoo.browseL8(ctx, model, ids):
            clodoo.writeL8(
                ctx, model, ids, {'number_next_actual': next_number,
                                  'number_next': next_number})
            for rec1 in rec.date_range_ids:
                if rec1.date_from < date.today() <= rec1.date_to:
                    clodoo.writeL8(
                        ctx, '%s.date_range' % model, rec1.id,
                        {'number_next_actual': next_number,
                         'number_next': next_number})


def store_vg7id(ctx, model, id, vg7_id):
    if model not in TNL_VG7_DICT:
        TNL_VG7_DICT[model] = {}
    if 'EXT' not in TNL_VG7_DICT[model]:
        TNL_VG7_DICT[model]['LOC'] = {}
        TNL_VG7_DICT[model]['EXT'] = {}
    if isinstance(vg7_id, basestring):
        TNL_VG7_DICT[model]['LOC'][id] = eval(vg7_id)
        TNL_VG7_DICT[model]['EXT'][eval(vg7_id)] = id
    else:
        TNL_VG7_DICT[model]['LOC'][id] = vg7_id
        TNL_VG7_DICT[model]['EXT'][vg7_id] = id


def store_oe8id(ctx, model, id, oe8_id):
    if model not in TNL_VG7_DICT:
        TNL_VG7_DICT[model] = {}
    if 'EXT' not in TNL_VG7_DICT[model]:
        TNL_VG7_DICT[model]['LOC'] = {}
        TNL_VG7_DICT[model]['EXT'] = {}
    if isinstance(oe8_id, basestring):
        TNL_VG7_DICT[model]['LOC'][id] = eval(oe8_id)
        TNL_VG7_DICT[model]['EXT'][eval(oe8_id)] = id
    else:
        TNL_VG7_DICT[model]['LOC'][id] = oe8_id
        TNL_VG7_DICT[model]['EXT'][oe8_id] = id


def write_file_2_pull(ext_model, vals, mode=None, identity=None):
    mode = mode or 'w'
    if mode == 'a':
        data = '%s\n' % (
            ','.join(map(lambda x: str(vals[x]), vals.keys()))
        )
    else:
        data = '%s\n%s\n' % (
            ','.join(vals.keys()),
            ','.join(map(lambda x: str(vals[x]), vals.keys()))
        )
    if identity:
        fn = os.path.expanduser('~/clodoo/%s/%s.csv' % (identity, ext_model))
    else:
        fn = os.path.expanduser('~/clodoo/%s.csv' % ext_model)
    with open(fn, mode) as fd:
        fd.write(data)


def get_vg7id_from_id(ctx, model, id):
    return clodoo.browseL8(ctx, model, id).vg7_id


def get_id_from_vg7id(ctx, model, vg7_id, name=None):
    name = name or 'vg7_id'
    ids = clodoo.searchL8(ctx, model, [(name, '=', vg7_id)])
    if ids:
        return ids[0]
    return -1


def is_untranslable(loc_name, ext_ref, vals):
    if (loc_name in RESET_FIELD and ext_ref in vals and
            (vals[ext_ref] is False or
             (isinstance(vals[ext_ref], basestring) and
              len(vals[ext_ref].split('.')) == 2))):
        return True
    return False


def jacket_vals(vals, prefix=None):
    prefix = prefix or 'vg7:'
    for nm in vals.copy():
        if is_untranslable(nm, nm, vals):
            continue
        if not nm.startswith('%s'):
            vals['%s%s' % (prefix, nm)] = vals[nm]
            del vals[nm]
    return vals


def shirt_vals(vals):
    for nm in vals.copy():
        if nm in ('customer_shipping_id', 'customer_billing_id'):
            continue
        new_name = nm.replace('billing_', '').replace('shipping_', '')
        if new_name != nm:
            vals[new_name] = vals[nm]
            del vals[nm]
    return vals


def get_loc_name(model, field, test_pfx):
    mode = False
    loc_name = field
    if field in ('vg7:id', 'oe8:id'):
        loc_name = 'id'
    elif test_pfx.startswith('vg7'):
        if (model and model in TNL_VG7_DICT and
                field in TNL_VG7_DICT[model]):
            loc_name = TNL_VG7_DICT[model][field]
            if loc_name and isinstance(loc_name, (tuple, list)):
                mode = loc_name[1]
                loc_name = loc_name[0]
    elif test_pfx.startswith('oe8'):
        if (model and model in TNL_OE8_DICT and
                field in TNL_OE8_DICT[model]):
            loc_name = TNL_OE8_DICT[model][field]
            if loc_name and isinstance(loc_name, (tuple, list)):
                mode = loc_name[1]
                loc_name = loc_name[0]
    return loc_name, mode


def get_loc_value(
        ctx, model, loc_rec, ext_ref, ext_name, loc_name, vals, test_pfx, spec):
    mode = False
    if loc_name.endswith('_id'):
        try:
            loc_value = getattr(loc_rec, loc_name).id
        except BaseException:
            loc_value = getattr(loc_rec, loc_name)
        ckstr = False
        if loc_name in TABLE_OF_REF_FIELD:
            ref_model = TABLE_OF_REF_FIELD[loc_name]
            if (TABLE_OF_REF_FIELD[loc_name] in TNL_VG7_DICT and
                    'LOC' in TNL_VG7_DICT[ref_model]):
                loc_value = TNL_VG7_DICT[
                    ref_model]['LOC'].get(loc_value,
                    loc_value)
            ckstr = True
        elif loc_name == 'parent_id':
            if model in TNL_VG7_DICT:
                loc_value = TNL_VG7_DICT[
                    model]['LOC'].get(loc_value, loc_value)
            ckstr = True
        if ckstr and isinstance(vals[ext_ref], basestring):
            ids = clodoo.searchL8(
                ctx, ref_model,
                [('name', 'ilike', vals[ext_ref])],
                context={'lang': 'it_IT'})
            if not ids:
                ids = clodoo.searchL8(
                    ctx, ref_model,
                    [('name', 'ilike', vals[ext_ref])])
            if len(ids) >= 1:
                if len(ids) > 1:
                    print('Warning: '
                          'multiple records %s.%s detected' % (
                              ref_model, vals[ext_ref]))
                if ref_model in TNL_VG7_DICT:
                    vals[ext_ref] = TNL_VG7_DICT[
                        ref_model]['LOC'].get(ids[0],
                        ids[0])
                else:
                    vals[ext_ref] = ids[0]
    else:
        loc_value = getattr(loc_rec, loc_name)
        if isinstance(loc_value, datetime):
            if ext_ref in ('vg7:data_emissione',
                           'vg7:data_ritiro'):
                loc_value = datetime.strftime(
                    loc_value, '%Y-%m-%d')
            else:
                loc_value = datetime.strftime(
                    loc_value, '%Y-%m-%d %H:%M:%S')
        elif isinstance(loc_value, date):
            loc_value = datetime.strftime(
                loc_value, '%Y-%m-%d')
        elif model == 'product.uom' and loc_value == 'Unità':
            loc_value = 'Unit(s)'
        elif (model == 'account.invoice' and loc_name == 'number' and
              loc_rec.state != 'draft'):
            mode = 'nounknown'
    return loc_value, mode


def get_ext_value(
        ctx, model, ext_ref, ext_name, loc_name, vals, spec, test_pfx=None):
    mode = False
    field_pfx = False
    if ext_ref.startswith('vg7:') or ext_ref.startswith('oe8:'):
        field_pfx = ext_ref[0:4]
    ext_value = vals[ext_ref]
    if (ext_ref in ('vg7:id', 'vg7_id', 'oe8:id', 'oe8_id') and
            (isinstance(vals[ext_ref], basestring) and
             vals[ext_ref].isdigit())):
        ext_value = eval(vals[ext_ref])
    elif spec in ('delivery', 'invoice') and loc_name in ('vat', 'fiscalcode'):
        ext_value = False
    elif loc_name == 'company_id':
        ext_value = env_ref(ctx, 'z0bug.mycompany')
    elif (loc_name.endswith('_id') and
            isinstance(vals[ext_ref], basestring) and
            vals[ext_ref].isdigit()):
        ext_value = eval(vals[ext_ref])
    elif loc_name == 'street' and field_pfx == 'vg7:':
        ext_value = '%s, %s' % (
            vals[ext_ref],
            vals.get('vg7:street_number', vals.get('street_number', '')))
    elif ext_ref == 'state' and field_pfx:
        ext_value = 'draft'
    elif loc_name == 'vat' and (field_pfx == 'vg7:' or test_pfx == 'vg7:'):
        if vals[ext_ref]:
            ext_value = 'IT%s' % vals[ext_ref]
    elif model == 'account.tax' and loc_name in ('name', 'description'):
        ext_value = vals[ext_ref]
        mode = 'nounknown'
    elif (model == 'res.partner' and
          loc_name == 'electronic_invoice_subjected' and
          field_pfx == 'vg7:'):
        ext_value = not os0.str2bool(vals[ext_ref], 0)
    elif is_untranslable(loc_name, ext_ref, vals) and not field_pfx:
        ext_value = env_ref(ctx, vals[ext_ref])
    if (model == 'res.partner' and ext_ref == 'vg7:name' and
            vals.get('vg7_id') == 17):
        mode = 'individual'
    return ext_value, mode


def reset_cache(ctx):
    lifetime = clodoo.executeL8(ctx,
        'ir.model.synchro.cache',
        'clean_cache',
        0,
        None,  # channel_id
        None,  # model
        60)  # cache lifetime
    if lifetime != 60:
        raise IOError('Invalid cache lifetime setup!!!')
    ctx['ctr'] += 1


def test_function_synchro(ctx, model, vals, test_pfx=None, ext_id=None):
    if test_pfx:
        vals = jacket_vals(vals, test_pfx)
    write_log(ctx, '>>> synchro(ctx, %s, %s)' % (model, vals))
    rec_id = clodoo.executeL8(ctx,
                              model,
                              'synchro',
                              vals)
    write_log(ctx, ' => %s' % rec_id, eol=True)
    if ext_id and rec_id > 0:
        if test_pfx.startswith('vg7'):
            store_vg7id(ctx, model, rec_id, ext_id)
        elif test_pfx.startswith('oe8'):
            store_oe8id(ctx, model, rec_id, ext_id)
    return rec_id, vals


def test_function_trigger(ctx, ext_model, vals, test_pfx, ext_id):
    write_log(ctx, '>>> trigger_one_record(ctx, %s, %s, %s)' % (
            ext_model, ext_id, test_pfx))
    rec_id = clodoo.executeL8(ctx,
                              'ir.model.synchro',
                              'trigger_one_record',
                              ext_model,
                              test_pfx,
                              ext_id)
    if ext_id and rec_id > 0:
        if test_pfx.startswith('vg7'):
            store_vg7id(ctx, ext_model, rec_id, ext_id)
        elif test_pfx.startswith('oe8'):
            store_oe8id(ctx, ext_model, rec_id, ext_id)
    vals = jacket_vals(vals, test_pfx)
    write_log(ctx, ' => %s, %s' % (rec_id, vals), eol=True)
    return rec_id, vals


def load_n_test_model(
        ctx, model, default, mode=None, store=None, test_pfx=None,
        test_suppl=None, fct_test=None):
    fct_test = fct_test or 'synchro'
    write_log(ctx, 'load_n_test_model(ctx, %s, default, mode=%s, pfx=%s)\n' % (
                model, mode, test_pfx))

    def get_shipping_vals(vg7_id):
        for item in RES_PARTNER_SHIPPING:
            if item['customer_id'] == vg7_id:
                return item
        return {}

    def get_billing_vals(vg7_id):
        for item in RES_PARTNER_BILLING:
            if item['customer_id'] == vg7_id:
                return item
        return {}

    if test_pfx.startswith('vg7') and model in TNL_VG7_TABLES:
        ext_model = TNL_VG7_TABLES[model]
    elif test_pfx.startswith('oe8'):
        ext_model = model
    else:
        ext_model = model
        model = False
    main_ext_id = False
    wa = 'w'
    for datas in default:
        vals = datas.copy()
        test_vals = {}
        if model in SOME_DEFAULT:
            for dict_item in SOME_DEFAULT[model]:
                field = dict_item['domain'][0]
                if test_pfx.startswith('vg7'):
                    for x in TNL_VG7_DICT[model].items():
                        if x[1] == dict_item['domain'][0]:
                            field = x[0]
                            break
                if compare_some(dict_item, vals, field=field):
                    test_vals[dict_item['value'][0]] = ctx[dict_item['value'][1]]
        if ext_model in ('customers_shipping_addresses',
                         'customers_billing_addresses',):
            shirt_vals(vals)
        for field in datas:
            if field in vals and vals[field] is None:
                del vals[field]
                continue
            loc_name, dummy = get_loc_name(model, field, test_pfx)
            if not ctx['conai'] and field == 'conai_id':
                del vals[field]
                continue
            if ((test_pfx and is_untranslable(loc_name, field, vals)) or
                    (not test_pfx and
                     not is_untranslable(loc_name, field, vals))):
                del vals[field]

        if test_pfx == 'vg7:' and model == 'res.partner':
            if mode != 'wrong':
                vals_shipping = get_shipping_vals(vals.get('id'))
                vals_billing = get_billing_vals(vals.get('id'))
                vals['shipping'] = vals_shipping
                vals['billing'] = vals_billing
                if vals_billing:
                    for field in ('piva', 'city'):
                        if vals_billing['billing_%s' % field]:
                            vals[field] = ''

        if not main_ext_id and vals.get('id'):
            main_ext_id = vals['id']
        if store:
            write_file_2_pull(ext_model, vals, wa)
            wa = 'a'
        if mode == 'upper' and 'description' in vals:
            vals['description'] = vals['description'].upper()
        if test_pfx == 'vg7:' and mode == 'wrong':
            for nm in WRONG_DATA:
                if nm in vals and vals[nm] == WRONG_DATA[nm][0]:
                    vals[nm] = WRONG_DATA[nm][1]
                    if nm == 'region' in vals and 'region_id' in vals:
                        del vals['region_id']
        ext_id = False
        if vals.get('id'):
            ext_id = vals['id']
        if mode == 'only_amount':
            del vals['code']
        if model:
            if fct_test == 'synchro':
                rec_id, vals = test_function_synchro(ctx, model, vals,
                    test_pfx=test_pfx,   ext_id=ext_id)
            else:
                rec_id, vals = test_function_trigger(
                    ctx, ext_model, vals, test_pfx, ext_id)
            if test_pfx == 'vg7:' and model == 'res.partner' and ext_id == 7:
                if rec_id == -7:
                    ctx['ctr'] += 1
                    continue
                raise IOError('!!%s.syncro(%d) failed!' % (model, rec_id))
            if test_vals:
                vals.update(test_vals)
            general_check(ctx, model, rec_id, vals, mode=mode)
            if model == 'product.product':
                rec_id = clodoo.browseL8(ctx, model, rec_id).product_tmpl_id.id
                for field in test_vals.keys():
                    del vals[field]
                general_check(ctx, 'product.template', rec_id, vals)
    return main_ext_id


def reset_model(ctx, model, default,
                company_id=None, test_pfx=None, tnl=None, only_def=None):
    print('Reset model %s (%s) ...' % (model, test_pfx))
    ext_id = False
    loc_id = False
    if test_pfx:
        ext_name = '%s_id' % test_pfx.split(':')[0]
    rec_ids = []
    for datas in default:
        vals = {}
        for field in datas:
            if datas[field] is None:
                continue
            if test_pfx:
                loc_name, dummy = get_loc_name(model, field, test_pfx)
            else:
                loc_name = field
            if loc_name == 'id':
                if not test_pfx:
                    loc_id, dummy = get_ext_value(
                        ctx, model, field, field, 'id', datas, '',
                        test_pfx=test_pfx)
                elif test_pfx and ext_name:
                    ext_id, dummy = get_ext_value(
                        ctx, model, field, field, 'id', datas, '',
                        test_pfx=test_pfx)
                continue
            if not ctx['conai'] and field == 'conai_id':
                loc_name = False
            if loc_name:
                vals[loc_name], dummy = get_ext_value(
                    ctx, model, field, field, loc_name, datas, '',
                    test_pfx=test_pfx)
        if not vals:
            continue
        if model in SOME_DEFAULT:
            for item in SOME_DEFAULT[model]:
                if compare_some(item, vals):
                    vals[item['value'][0]] = ctx[item['value'][1]]
        domain = ids = []
        if loc_id:
            ids = [loc_id]
        elif ext_id:
            domain = [(ext_name, '=', ext_id)]
            ids = clodoo.searchL8(ctx, model, domain)
        if not ids:
            for kk in CANDIDATE_KEYS:
                if kk in vals:
                    if kk in ('default_code', 'name'):
                        domain = [(kk, 'like', vals[kk])]
                    else:
                        domain = [(kk, '=', vals[kk])]
                    break
            if domain:
                if model == 'res.country.state':
                    domain.append(('country_id', '=', ctx['res.country.IT']))
        if domain:
            if company_id:
                domain.append(('company_id', '=', company_id))
        if domain:
            ids = clodoo.searchL8(ctx, model, domain)
        if ids:
            rec_ids += ids
            if len(ids) > 1:
                print('Warning: Too many records "%s.%s"' % (model, domain))
            if tnl:
                clodoo.writeL8(
                    ctx, model, ids, vals)
                write_log(ctx, '>>> %s.write(%s, %s, ctx="en_US")' % (
                    model, ids, vals), eol=True)
                if model in NAME_REFS:
                    done_tnl =False
                    for item in NAME_REFS[model]:
                        if compare_some(item, vals):
                            done_tnl = True
                            vals[item['value'][0]] = item['value'][1]
                    if done_tnl:
                        clodoo.writeL8(
                            ctx, model, ids, vals, context={'lang': tnl})
                        write_log(ctx, '>>> %s.write(%s, %s, ctx="%s")' % (
                            model, ids, vals, tnl), eol=True)
            else:
                clodoo.writeL8(ctx, model, ids, vals)
                write_log(ctx, '>>> %s.write(%s, %s)' % (
                    model, ids, vals), eol=True)
            if model in SET_SOME_DEFAULT:
                for item in SET_SOME_DEFAULT[model]:
                    if compare_some(item, vals):
                        ctx[item['value']] = ids[0]
        else:
            print('Warning: No records found "%s.%s"' % (model, domain))
    if test_pfx:
        if test_pfx.startswith('vg7'):
            ext_model = TNL_VG7_TABLES[model]
        else:
            ext_model = TNL_OE8_TABLES.get(model, model)
        rm_file_2_pull(ext_model)
    reset_ext_id(model)
    if only_def and rec_ids:
        delete_record(ctx, model, [('id', 'not in', rec_ids)],
            multi=True, company_id=company_id)


def get_invalid_partners(ctx):
    return clodoo.searchL8(ctx, 'res.partner',
        [('parent_id', '=', False),
         '|', ('name', '=', False),
         '|', ('name', '=', ''),
         ('name', '=', ' ')])


def get_unknown_partners(ctx):
    return clodoo.searchL8(ctx, 'res.partner',
        [('name', 'ilike', 'Unknown')])

def init_test(ctx):
    write_log(ctx, 'init_test(ctx)', eol=True)
    if ctx['conai']:
        MODULE_LIST.append('connector_vg7_conai')
    print('This test requires following modules installed:')
    line = ''
    ctr = 0
    for module in MODULE_LIST:
        if len(line) > 40:
            print(line)
            line = ''
        if not line:
            ctr += 1
            line = '%d. ' % ctr
        else:
            line += ', '
        line += module
    if ctx['ask']:
        input('Requirements are satisfied?')
    # Log level debug
    clodoo.executeL8(ctx,
        'ir.model.synchro.cache',
        'set_loglevel',
        0,
        'debug')
    reset_cache(ctx)

    model = 'ir.module.module'
    if ctx['chk_module']:
        for modname in MODULE_LIST:
            vals = {'name': modname}
            clodoo.executeL8(ctx,
                model,
                'synchro',
                vals)
        time.sleep(4)
    if not ctx['conai']:
        MODULE_LIST.append('connector_vg7_conai')
    for modname in MODULE_LIST:
        print('checking module %s ...' % modname)
        module_ids = clodoo.searchL8(ctx, model,
            [('name', '=', modname)])
        if modname == 'connector_vg7_conai' and not ctx['conai']:
            pass
        elif not module_ids:
            raise IOError('Module %s does not exist!!!' % modname)
        module = clodoo.browseL8(ctx, model, module_ids[0])
        if modname == 'connector_vg7_conai':
            if ctx['conai'] and module.state != 'installed':
                raise IOError('Module %s not installed!!!' % modname)
            elif not ctx['conai'] and module.state == 'installed':
                raise IOError(
                    'Module %s installed! Please use --conai option' %
                    modname)
        elif module.state != 'installed':
            raise IOError('Module %s not installed!!!' % modname)

    model = 'res.lang'
    if ctx['lang'] not in ('en_US', '.'):
        vals = {'code': ctx['lang']}
        print('Installing language %s ...' % vals['code'])
        clodoo.executeL8(ctx,
            model,
            'synchro',
            vals)

    company_id = env_ref(ctx, 'z0bug.mycompany')
    if not company_id:
        raise IOError('!!Internal error: no company to test found!')

    print('Initializing environment ...')
    model = 'res.company'
    company = clodoo.browseL8(ctx, model, company_id)
    if not company.country_id:
        clodoo.writeL8(
            ctx, model, company_id, {'country_id': env_ref(ctx, 'base.it')})

    # Default values for current user
    vals = {'company_id': company_id}
    if ctx['lang'] != '.':
        vals['lang'] = ctx['lang']
    clodoo.writeL8(ctx, 'res.users', ctx['user_id'], vals)
    write_log(ctx, '>>> res.users.write(%s, %s)' % (
        ctx['user_id'], vals), eol=True)
    ctx['lang'] = clodoo.browseL8(ctx, model, ctx['user_id']).lang
    # Set message note
    ctx['company_note'] = 'Si prega di controllate i dati entro le 24h.'
    vals = {'sale_note': ctx['company_note']}
    clodoo.writeL8(ctx, 'res.company', company_id, vals)
    write_log(ctx, '>>> res.company.write(%s, %s)' % (
        company_id, vals), eol=True)
    # Configure VG7 channel
    # Wrong method. Will be set forward, in order to test cache too
    model = 'synchro.channel'
    write_record(ctx, model, [], {
        'method': 'JSON',
        'exchange_path': os.path.expanduser('~/clodoo'),
        'tracelevel': '4',
    })
    if not ctx.get('_cr'):
        print('No sql support found!')
        if ctx['ask']:
            input('Press RET to continue')
    else:
        for query in (
                'delete from procurement_order',
                'delete from stock_pack_operation',
                'delete from stock_move'
        ):
            try:
                clodoo.exec_sql(ctx, query)
            except BaseException:
                pass
    # model = 'account.account.type'
    # clear_pfx(model)
    # for item in ACCOUNT_TYPE_NAME_REF:
    #     if not item.startswith('-'):
    #         loc_id = env_ref(ctx, ACCOUNT_TYPE_NAME_REF[item])
    #         if not loc_id:
    #             continue
    #         vals = {'name': item}
    #         clodoo.writeL8(ctx, model, loc_id, vals, context={'lang': 'en_US'})
    #         write_log(ctx, '>>> write(%s, %s, %s, ctx="en_US")' % (
    #             model, loc_id, vals), eol=True)
    #         vals = {'name': ACCOUNT_TYPE_NAME_TNL[item]}
    #         clodoo.writeL8(ctx, model, loc_id, vals, context={'lang': 'it_IT'})
    #         write_log(ctx, '>>> write(%s, %s, %s, ctx="it_IT")' % (
    #             model, loc_id, vals), eol=True)
    for model, domains, company_id, multi, childs, action in (
            ('account.invoice', -1, company_id, True, None,
             ['move_name=', 'action_invoice_cancel']),
            ('stock.picking.package.preparation',
             -1, company_id, True, None, None),
            ('sale.order', -1, company_id, True, None, 'action_cancel'),
            ('purchase.order', -1, company_id, True, None, 'button_cancel'),
            ('account.move', -1, company_id, True, None, 'button_cancel'),
            ('res.partner', -1, False, True, 'child_ids', None),
            ('res.partner',
             [('name', 'like', 'Partner A%'),
              ('type', '=', 'contact')], False, True, 'child_ids', None),
            ('res.partner',
             [('name', '=', 'La Romagnola srl'),
              ('type', '=', 'contact')], False, True, 'child_ids', None),
            ('res.partner',
             [('fiscalcode', '=', 'RSSMRA60T45L219M')],
             False, True, 'child_ids', None),
            ('account.payment.term',
             -1, company_id, True, None, None),
            ('account.tax', -1, company_id, True, None, None),
            ('res.country.state', -1, False, True, None, None),
            ('stock.picking.goods_description', -1, False, True, None, None),
            ('crm.team',
             [('name', '=', 'Sale Example Team')], False, False, None, None),
            ('account.account',
             [('code', '=', '180111')], company_id, False, None, None),
            ('ir.model.synchro.data', [], False, True, None, None),
    ):
        delete_record(ctx, model, domains, multi=multi, action=action,
            childs=childs, company_id=company_id)
    for model, datas, test_pfx, company, tnl, only_def in (
            ('account.account.type',
             ACCOUNT_ACCOUNT_TYPE_DEF, False, False, 'it_IT', True),
            ('res.country', RES_COUNTRY_OE8, 'oe8:', False, False, False),
            ('res.country.state',
             RES_COUNTRY_STATE_OE8, 'oe8:', False, False, False),
            ('res.partner', RES_PARTNER_DEF, False, False, False, False),
            ('italy.conai.product.category',
             ACCOUNT_CONAI_DEF, False, False, False, False),
            ('product.template',
             PRODUCT_TEMPLATE_DEF, False, False, 'it_IT', False),
            ('product.product',
             PRODUCT_PRODUCT_DEF, False, False, False, False),
            # ('account.payment.term',
            #  ACCOUNT_PAYMENT_TERM, 'vg7:', company_id, False, False),
            # ('account.tax', ACCOUNT_TAX_OE8, False, company_id, False, False),
    ):
        reset_model(ctx, model, datas,
            company_id=company, test_pfx=test_pfx, tnl=tnl, only_def=only_def)
    for model, domain, company_id, vals in (
            ('res.partner', [('name', 'like', 'Rossi')], False,
             {'individual': True}),
            ('account.journal', [], company_id, {'update_posted': True}),
    ):
        write_record(ctx, model, domain, vals, company_id=company_id)

    channel_ids = clodoo.searchL8(
        ctx, 'synchro.channel', [('identity', '!=', 'odoo')])
    if channel_ids:
        model = 'synchro.channel.model'
        delete_record(
            ctx, model, [('synchro_channel_id', '!=', channel_ids[0])],
            multi=True)
    return ctx, company_id


def compare(ctx, rec_value, ext_value, mode):
    if mode == 'nounknown':
        return not rec_value.startswith('Unknown')
    elif mode == 'unknown':
        return rec_value.startswith('Unknown')
    elif mode == 'individual':
        return rec_value in ctx['partner_MR_ids']
    elif mode == 'nocase':
        return rec_value.lower() == ext_value.lower()
    elif mode == 'delivery':
        return rec_value == ext_value + 100000000
    elif mode == 'invoice':
        return rec_value == ext_value + 200000000
    elif rec_value or ext_value:
        return rec_value == ext_value
    return True


def general_check(ctx, model, loc_id, vals, mode=None):
    write_log(ctx,
        '>>> %s.general_check(%s, %s)' % (model, loc_id, vals), eol=True)
    if not loc_id or loc_id < 1:
        raise IOError('!!%s.syncro(%d) failed!' % (model, loc_id))
    spec = False
    if model.startswith('res.partner.'):
        spec = {'shipping': 'delivery',
                'billing': 'invoice'}[model.split('.')[2]]
        model = 'res.partner'
    loc_rec = clodoo.browseL8(ctx, model, loc_id)
    if spec:
        if not compare(ctx, loc_rec.type, spec, False):
            raise IOError(
                '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                    model, loc_id, 'type', loc_rec.type, spec))
        ctx['ctr'] += 1
    test_pfx = False
    for ext_ref in vals:
        if ext_ref in (
                'vg7:date_scadenza', 'vg7:shipping', 'vg7:billing',
                'vg7:surename', 'vg7:name', 'id', 'vg7:street_number'):
            continue
        # Odoo BUG !?
        if (model == 'res.partner' and
                ext_ref == 'vg7:piva' and loc_rec.type != 'contact'):
            continue
        loc_name = ext_name = ext_ref
        mode2 = False
        if ext_ref in ('vg7:id', 'oe8:id'):
            loc_name = ext_ref.replace(':', '_')
            ext_name = 'id'
        elif (ext_ref.startswith('vg7:') or
              ext_ref.startswith('oe8:')):
            test_pfx = ext_ref[0:4]
            ext_name = ext_ref[4:]
            loc_name, mode2 = get_loc_name(model, ext_ref, test_pfx)
            if loc_name == ext_ref:
                loc_name, mode2 = get_loc_name(model, ext_name, test_pfx)
        if not loc_name:
            continue
        mode_compare = False
        if mode == 'upper' and mode2 == 'nocase':
            mode_compare = mode2
        elif mode == 'only_amount' and mode2 == 'nounknown':
            mode_compare = mode2

        loc_value, mode2 = get_loc_value(ctx, model,
            loc_rec, ext_ref, ext_name, loc_name, vals, test_pfx, spec)
        mode_compare = mode_compare or mode2
        ext_value, mode2 = get_ext_value(
            ctx, model, ext_ref, ext_name, loc_name, vals, spec)
        mode_compare = mode_compare or mode2
        if loc_name == 'vg7_id':
            mode_compare = spec
        if vals[ext_ref] == '' and not mode:
            continue
        if not compare(ctx, loc_value, ext_value, mode_compare):
            raise IOError(
                '!!Field %s[%s].%s: invalid value <%s> expected <%s> # %s' % (
                    model, loc_id, loc_name, loc_value, ext_value, mode))
        ctx['ctr'] += 1
        if model == 'account.account.type' and loc_name == 'name':
            for item in ACCOUNT_ACCOUNT_TYPE_DEF:
                if loc_rec.name == item['name']:
                    xref = item['id']
                    id = env_ref(ctx, xref)
                    if loc_id != id:
                        raise IOError(
                            '!!Field %s[%s].%s: invalid value <%s> expected <%s> # %s' % (
                                model, loc_id, loc_name, loc_id, id, loc_rec.name))
                    ctx['ctr'] += 1
        if mode == 'individual':
            if not compare(ctx, loc_rec.name, 'Rossi Mario', False):
                raise IOError(
                    '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                        model, loc_id, 'name', loc_rec.name, 'Rossi Mario'))
            ctx['ctr'] += 1
            if not compare(ctx, loc_rec.individual, True, False):
                raise IOError(
                    '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                        model, loc_id, 'individual', loc_rec.individual, False))
            ctx['ctr'] += 1
    if model == 'res.partner' and loc_rec.type == 'contact':
        if not compare(ctx, loc_rec.is_company, True, False):
            raise IOError(
                '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                    model, loc_id, 'is_company', loc_rec.is_company, True))
        ctx['ctr'] += 1
    if model == 'res.partner' and loc_rec.type != 'contact':
        if not compare(ctx, loc_rec.is_company, bool(loc_rec.name), False):
            raise IOError(
                '!!Field %s[%s].%s: invalid value <%s> expected <%s>' % (
                    model, loc_id, 'is_company', loc_rec.is_company,
                    bool(loc_rec.name)))
        ctx['ctr'] += 1


def test_synchro_vg7(ctx):
    print('Test synchronization VG7 module')
    ctx['ctr'] = 0

    def test_country(ctx, mode=None, test_pfx=None, fct_test=None):
        test_pfx = test_pfx or 'vg7:'
        model = 'res.country'
        print('Write %s (%s) ...' % (model, test_pfx))
        vg7_id = load_n_test_model(ctx, model,
            RES_COUNTRY_VG7 if test_pfx == 'vg7:' else RES_COUNTRY_OE8,
            mode=mode, store=not mode, test_pfx=test_pfx, fct_test=fct_test)
        if test_pfx == 'vg7:':
            ctx['res.country.IT'] = vg7_id

        model = 'res.country.state'
        print('Write %s (%s) ...' % (model, test_pfx))
        vg7_id = load_n_test_model(ctx, model,
            RES_COUNTRY_STATE_VG7
            if test_pfx == 'vg7:' else RES_COUNTRY_STATE_OE8,
            mode=mode, store=not mode, test_pfx=test_pfx, fct_test=fct_test,
            test_suppl='country_id')
        if test_pfx == 'vg7:':
            ctx['res.country.state.MI'] = vg7_id

    def test_tax(ctx, mode=None, test_pfx=None, fct_test=None):
        test_pfx = test_pfx or 'vg7:'
        model = 'account.tax'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model,
            ACCOUNT_TAX_VG7 if test_pfx == 'vg7:' else ACCOUNT_TAX_OE8,
            mode=mode, store=not mode, test_pfx=test_pfx, fct_test=fct_test)
        ctx['account.tax.22v'] = vg7_id

    def write_payment(ctx, mode=None):
        model = 'account.payment.term'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, ACCOUNT_PAYMENT_TERM,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['account.payment.term.30GG'] = vg7_id

    def test_conai(ctx, mode=None):
        model = 'italy.conai.product.category'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, ACCOUNT_CONAI_VG7,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['italy.conai.product.category.CA'] = vg7_id

    def test_product(ctx, mode=None):
        model = 'product.product'
        print('Write %s ...' % model)
        vg7_id = load_n_test_model(ctx, model, PRODUCT_TEMPLATE_VG7,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['product.product.A'] = vg7_id

    def test_partner(ctx, mode=None):
        model = 'res.partner'
        print('Write %s ...' % model)
        if not mode:
            load_n_test_model(ctx, 'res.partner.shipping',
                RES_PARTNER_SHIPPING,
                mode=mode, store=not mode, test_pfx='vg7:')
            load_n_test_model(ctx, 'customers_billing_addresses',
                RES_PARTNER_SHIPPING,
                mode=mode, store=not mode, test_pfx='vg7:')
        vg7_id = load_n_test_model(ctx, model, RES_PARTNER_VG7,
            mode=mode, store=not mode, test_pfx='vg7:')
        ctx['res.partner.A'] = vg7_id

    def test_account_type(ctx, mode=None):
        model = 'account.account.type'
        print('Write %s ...' % model)
        load_n_test_model(ctx, model, ACCOUNT_ACCOUNT_TYPE_OE8,
            mode=mode, store=not mode, test_pfx='oe8:', fct_test='trigger')

    ctx, company_id = init_test(ctx)
    #
    # Repeat tests 2 times to check correct synchronization
    #
    print('*** Starting VG7 test ***')

    test_country(ctx, test_pfx='vg7:')
    test_country(ctx, mode='upper', test_pfx='vg7:')

    test_tax(ctx, mode='only_amount', test_pfx='vg7:')
    test_tax(ctx, test_pfx='vg7:')

    write_payment(ctx)
    write_payment(ctx, mode=True)

    if ctx['conai']:
        test_conai(ctx)
        test_conai(ctx, mode=True)

    test_product(ctx)
    test_product(ctx, mode=True)

    test_partner(ctx, mode='wrong')
    test_partner(ctx)

    print('*** Starting OE8 test ***')

    # Set method CSV and reset cache
    model = 'synchro.channel'
    clodoo.writeL8(ctx, model, clodoo.searchL8(
        ctx, model, []), {
                       'method': 'CSV',
                       'exchange_path': os.path.expanduser('~/clodoo'),
                       'tracelevel': '4',
                   })
    reset_cache(ctx)

    test_country(ctx, test_pfx='oe8:', fct_test='trigger')
    test_account_type(ctx)
    test_tax(ctx, test_pfx='oe8:', fct_test='trigger')

    # Final checks
    ids = get_invalid_partners(ctx)
    ids += get_unknown_partners(ctx)
    if ids:
        raise IOError(
            '!!Found invalid or unknown res.partner records %s!' % ids)
    ctx['ctr'] += 2

    print('%d tests connector_vg7 successfully ended' % ctx['ctr'])
    return


parser = z0lib.parseoptargs("Odoo test environment",
                            "© 2020-2021 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--config",
                    help="configuration command file",
                    dest="conf_fn",
                    metavar="file",
                    default='./inv2draft_n_restore.conf')
parser.add_argument("-d", "--dbname",
                    help="DB name to connect",
                    dest="db_name",
                    metavar="file",
                    default='')
parser.add_argument("-L", "--logfile",
                    help="test logfile",
                    dest="logfn",
                    metavar="file",
                    default='./test_synchro.log')
parser.add_argument('-l', "--lang",
                    help="language translation",
                    metavar="iso-3166 or '.'",
                    dest="lang",
                    default='it_IT')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')
parser.add_argument('-1', "--conai",
                    action="store_true",
                    help="enable test conai module",
                    dest="conai",
                    default=False)
parser.add_argument('-2', "--no-conai",
                    action="store_false",
                    help="disable test conai module",
                    dest="conai")
parser.add_argument('-3', "--no-ask",
                    action="store_false",
                    help="ask for some tests",
                    dest="ask",
                    default=True)
parser.add_argument('-4', "--ask",
                    action="store_true",
                    help="execute tests w/o ask",
                    dest="ask")
parser.add_argument('-5', "--no-module",
                    action="store_false",
                    help="do not check for modules",
                    dest="chk_module",
                    default=True)
parser.add_argument('-6', "--module",
                    action="store_true",
                    help="check for modules",
                    dest="chk_module")

ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                               db=ctx['db_name'],
                               ctx=ctx)
msg_time = time.time()
os0.set_tlog_file('./odoo_shell.log', echo=True)
if os.path.isfile(ctx['logfn']):
    os.unlink(ctx['logfn'])
test_synchro_vg7(ctx)
exit(0)
