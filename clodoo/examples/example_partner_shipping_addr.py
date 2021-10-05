# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example of Odoo management from external source

Primitive search, browse, create and write using xmlrcp or jsonrpc
This example may be used by PHP external source or by python external source
With python, oerplib and odoorpc PYPI packages are needed
With PHP you need som library like ripcord or phpxmlrpc;
URL to connect is to Odoo 6.1 or 7.0 is "$ODOO_URL/xmlrpc/common"
URL to connect is to Odoo 8.0+ is "$ODOO_URL/xmlrpc/2/common"
You must convert python data like follow example:
<--  python -->          | <-- PHP -->
vals = {                 | $vals = array(
    'name': 'John Doe',  |     "name" => new xmlrpcval("John Doe", "string"),
    'city': 'Torino',    |     "city" => new xmlrpcval("Torino", "string"),
    'team_id': 1,        |     "team_id" => new xmlrpcval(1, "int"),
}                        | );

With python you have to use xmlrpc protocol to connect Odoo 8.0 or less,
to connect Odoo 9.0 + you have to use jsonrpc

From PHP you can use just xmlrpc protocol

"""
from __future__ import print_function
import sys
import clodoo
try:
    from z0lib import z0lib
except ImportError:
    import z0lib


MYNAME = 'Nicola Bee'

__version__ = "0.2.1"


def searchL8(ctx, model, where, order=None, context=None):
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].search(where, order=order,
                                                     context=context)
    else:
        return ctx['odoo_session'].search(model, where, order=order,
                                          context=context)


def browseL8(ctx, model, id, context=None):
    if ctx['svc_protocol'] == 'jsonrpc':
        res = ctx['odoo_session'].env[model].browse(id)
    else:
        res = ctx['odoo_session'].browse(model, id, context=context)
    return res


def createL8(ctx, model, vals):
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].create(vals)
    else:
        return ctx['odoo_session'].create(model, vals)


def write_recordL8(ctx, record):
    if ctx['svc_protocol'] == 'jsonrpc':
        ctx['odoo_session'].write(record)
    else:
        ctx['odoo_session'].write_record(record)


def writeL8(ctx, model, ids, vals):
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].write(ids,
                                                    vals)
    else:
        return ctx['odoo_session'].write(model,
                                         ids,
                                         vals)


def unlinkL8(ctx, model, ids):
    if ctx['svc_protocol'] == 'jsonrpc':
        return ctx['odoo_session'].env[model].unlink(ids)
    else:
        return ctx['odoo_session'].unlink(model, ids)


def executeL8(ctx, model, action, *args):
    return ctx['odoo_session'].execute(model,
                                       action,
                                       *args)


parser = z0lib.parseoptargs("Code example to create an Odoo partner",
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

# import pdb
# pdb.set_trace()
# Get command line paramaters & Connect to DB
ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                               confn=ctx['conf_fn'],
                               db=ctx['db_name'])
oerp = ctx['odoo_session']

print('0> Begin transaction\n   host=%s\n   protocol=%s' % (
    ctx['db_host'],
    ctx['svc_protocol']))
model = 'res.partner'
customer_info = {
    'name': MYNAME,
    'street': 'Via San Primo, 1',
    'is_company': True,
    'customer': True,
}
shipping_info = {
    'name': 'Casa di %s' % MYNAME,
    'street': 'Via San Secondo, 2',
    'type': 'delivery',
    'customer': False,   # It is better, because Odoo default is customer=True
}

ids = searchL8(ctx, model, [('name', 'ilike', MYNAME)])
if ids:
    print('1> Partner %s already exists' % customer_info['name'])
    id = ids[0]
    writeL8(ctx, model, id, customer_info)
    ids = searchL8(ctx, model, [('parent_id', '=', id)])
    if ids:
        id_ship = ids[0]
        print('2> Shipping address already exists')
    else:
        shipping_info['parent_id'] = id
        print('2> Create shipping address')
        id_ship = createL8(ctx, model, shipping_info)
else:
    print('1> Create partner %s' % customer_info['name'])
    id = createL8(ctx, model, customer_info)
    shipping_info['parent_id'] = id
    print('2> Create shipping address')
    id_ship = createL8(ctx, model, shipping_info)

# Search lower(name) like lower('%Nicola Bee%')
id = searchL8(ctx, model, [('name', 'ilike', MYNAME),
                           ('is_company', '=', True)])[0]
customer_info['city'] = 'Castano Primo'
print('3> Update partner address')
writeL8(ctx, model, id, customer_info)
id_ship = searchL8(ctx, model, [('name', 'ilike', MYNAME),
                                ('type', '=', 'delivery'),
                                ('parent_id', '=', id)])[0]
shipping_info['city'] = 'San Secondo'
print('4> Update shipping address')
writeL8(ctx, model, id_ship, shipping_info)

print('99> Transaction ended')
