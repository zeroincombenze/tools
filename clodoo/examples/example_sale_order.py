# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function, unicode_literals
from __future__ import print_function

import sys
# import time
# import re
# import getpass
# from symbol import except_clause
import platform
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib


__version__ = "0.3.34.99"

parser = z0lib.parseoptargs("Create an  Odoo sale.order example",
                            "© 2017-2018 by SHS-AV s.r.l.",
                            version=__version__)
parser.add_argument('-h')
parser.add_argument("-c", "--config",
                    help="configuration command file",
                    dest="conf_fn",
                    metavar="file",
                    default='./example.conf')
parser.add_argument("-d", "--dbname",
                    help="DB name to connect",
                    dest="db_name",
                    metavar="file",
                    default='')
parser.add_argument('-n')
parser.add_argument('-q')
parser.add_argument('-V')
parser.add_argument('-v')

UPDATE = True
# Connect to DB
print("Connect to DB")
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                               db=ctx['db_name'],
                               ctx=ctx)
print('0> Begin transaction\n   host=%s\n   protocol=%s' % (
    ctx['db_host'],
    ctx['svc_protocol']))

# Recognize environment
hostname = platform.node()
if hostname[0:3] == 'shs':
    model = 'res.company'
    company_id = clodoo.searchL8(ctx, model,
                                 [('name', 'ilike', 'La Tua Azienda')])[0]
else:
    company_id = 3
PRODUCT_TMPL_ID = 2
PRODUCT_ID = 2
MYNAME = 'Nicola Bee'

print('1> Manage res.partner %s' % MYNAME)
model = 'res.partner'
customer_info = {
    'name': MYNAME,
    'street': 'Via San Primo, 1',
    'customer': True,
    'vat': 'IT12345670017'
}
partner_id = clodoo.executeL8(ctx, model, 'synchro', customer_info)
if partner_id < 0:
    print('Error %d synchronizing %s' % (partner_id, model))
    exit(1)

shipping_info = {
    'name'  :MYNAME,
    'parent_id': partner_id,
    'type': 'delivery',
}
shipping_id = clodoo.executeL8(ctx, model, 'synchro', shipping_info)

model = 'product.template'
product_tmpl_id = clodoo.searchL8(ctx, model,
                                  [('default_code', '=', 'vg7')])
if not product_tmpl_id:
    product_tmpl_id = clodoo.searchL8(ctx, model,
        [('name', 'ilike', 'prodotto/generico')])
if not product_tmpl_id:
    product_tmpl_id = clodoo.searchL8(ctx, model,
                                      [('name', 'ilike', 'test')])
product_tmpl_id = product_tmpl_id[0] if product_tmpl_id else False
if not product_tmpl_id:
    product_tmpl_id = PRODUCT_TMPL_ID
model = 'product.product'
product_id = clodoo.searchL8(ctx, model,
                             [('product_tmpl_id', '=', product_tmpl_id)])
product_id = product_id[0] if product_id else False
if not product_id:
    product_id = PRODUCT_ID
#
QTY_INV = 1
QTY_SELL = 15
PRC_TOTAL = 123.40
PRC_UNIT = PRC_TOTAL / QTY_SELL
#
model = 'sale.order'
model_line = 'sale.order.line'
order_info = {
    'company_id': company_id,
    'partner_id': partner_id,
    # 'user_id': uid,
}
if shipping_id:
    order_info['partner_shipping_id'] = shipping_id
order_number = 'order1'
order_info['name'] = order_number
print("Synchonize order %s ..." % order_number)
order1_id = clodoo.executeL8(ctx, model, 'synchro', order_info)
if order1_id < 0:
    print('Error %d synchronizing sale.order' % order1_id)
    exit(1)

line_info = {
    'product_id': product_id,
    'name': 'Prodotto specifico N.%d\n'
            '%d pz * %10.5f EUR' % (1,
                                    QTY_SELL,
                                    PRC_UNIT),
    'company_id': company_id,
    'price_unit': PRC_TOTAL,
    'product_uom_qty': QTY_INV,
    'product_uos_qty': QTY_SELL,
    'sequence': 10,
}

print("Synchronize line ...")
line_info['order_id'] = order1_id
line1_id = clodoo.executeL8(ctx, model_line, 'synchro', line_info)

print("Ended")
