# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
# import os
# import time
import platform
import clodoo
# import clodoocore
# import clodoolib
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
# import pdb


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
print "Connect to DB"
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
oerp, uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                     db=ctx['db_name'],
                                     ctx=ctx)
# pdb.set_trace()
# Recognize environment
hostname = platform.node()
if hostname[0:3] == 'shs':
    model = 'res.company'
    company_id = oerp.search(model, [('name', 'ilike', 'La Tua Azienda')])[0]
else:
    company_id = 1

model = 'stock.location.route'
rout_ids = oerp.search(model, [('name', 'ilike', 'Make To Order')])

product_info = {
    'name': 'prodotto/generico',
    'default_code': 'vg7',
    'company_id': company_id,
    'type': 'consu',
    'route_ids': [(6, 0, rout_ids)],
}
model = 'account.tax'
tax_ids = oerp.search(model, [('description', '=', '22v'),
                              ('company_id', '=', company_id)])
product_info['taxes_id'] = [(6, 0, tax_ids)]
tax_ids = oerp.search(model, [('description', '=', '22a'),
                              ('company_id', '=', company_id)])
product_info['supplier_taxes_id'] = [(6, 0, tax_ids)]
kname = {'expense': 'prime',
         'income': 'merci'}
for t in ('expense', 'income'):
    model = 'account.account.type'
    acctype_ids = oerp.search(model, [('code', '=', t)])
    model = 'account.account'
    acc_ids = oerp.search(model, [('user_type', 'in', acctype_ids),
                                  ('type', '!=', 'view'),
                                  ('name', 'like', kname[t])])
    if acc_ids:
        product_info['property_account_%s' % t] = acc_ids[0]


model = 'product.template'
ids = oerp.search(model, [('name', 'ilike', 'prodotto/generico')])
if ids:
    print 'Product template already exists'
    template_id = ids[0]
    oerp.write(model, template_id, product_info)
    product_info['product_tmpl_id'] = template_id
    model = 'product.product'
    ids = oerp.search(model, [('product_tmpl_id', '=', template_id)])
    if ids:
        print 'Product already exists'
        product_id = ids[0]
        oerp.write(model, product_id, product_info)
    else:
        print 'Create product'
        product_id = oerp.create(model, product_info)
else:
    print 'Create product template'
    template_id = oerp.create(model, product_info)
    model = 'product.product'
    product_info['parent_id'] = template_id
    print 'Create product'
    product_id = oerp.create(model, product_info)
