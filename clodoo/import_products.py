# -*- coding: utf-8 -*-
# Import file library
"""
Import Product from CSV

This program supplies functions to import products.
#
# Example of client software:
#
import csv
from import_products import (init_n_connect, add_elem)
MYDICT_C = {
    'name': 1,
}

def main():
    odoo, uid, ctx = init_n_connect(flavour='myname')
    ctx['IN_country_id'] = 'name'
    dialect = 'excel'
    with open(ctx['csv_fn'], 'rbU') as f:
        hdr = False
        reader = csv.reader(f, dialect=dialect)
        for row in reader:
            if not hdr:
                hdr = True
                continue
            add_elem(row, ctx, MYDICT_C, MYDICT_S)


Parameters as key of ctx:
    default_XXX: value for field XXX if not in csv file
    trx_XXX: borderline translation dictionary for field XXX (1)
    company_name: company name to import data
    flavour: suffix to compose csv filename

Field in csv files:

(1) Borderline Translation dictionary:
Some fields require to convert source value into local Odoo value.
To do automatic translation supply a dictionary in form:
trx_XXX = {'original_value': 'Odoo_value', ...}
When field XXX in file csc contains value 'original_value' is written into
local Odoo DB as 'Odoo_value'.
"""
import sys
# import os
import time
import clodoo
import z0lib
# import pdb


__version__ = "0.1.0"


msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print text
        msg_time = time.time()


def get_company_id(ctx):
    model = 'res.company'
    company_name = ctx.get('company_name', 'La % Azienda')
    ids = clodoo.searchL8(ctx, model, [('name', 'ilike', company_name)])
    if not ids:
        ids = clodoo.searchL8(ctx, model, [('id', '>', 1)])
    if ids:
        return ids[0]
    else:
        return 1


def write_log(msg):
    fd = open('./import_products.log', 'a')
    fd.write('%s\n' % msg)
    fd.close()
    print msg


def add_elem(row, ctx, MYDICT):
    def cvt_val(ctx, field_name, value):
        x = 'trx_%s' % field_name
        if x in ctx:
            trx_dict = ctx[x]
            if value in trx_dict:
                value = trx_dict[value]
            else:
                value = value.strip()
        elif field_name == 'company_id':
            value = get_company_id(ctx)
        else:
            value = value.strip()
        return value

    def add_val(row, ctx, MYDICT, field_name):
        def_field_name = 'default_%s' % field_name
        if field_name in MYDICT:
            idx = MYDICT[field_name]
            if idx >= len(row):
                print 'Invalid translation field %d' % idx
                return
            vals[field_name] = cvt_val(ctx, field_name, row[idx])
        elif def_field_name in ctx:
            vals[field_name] = ctx[def_field_name]

    msg_burst('Reading %s ...' % row[MYDICT['name']])
    model = 'product.product'
    vals = {}
    add_val(row, ctx, MYDICT, 'name')
    for field_id in clodoo.searchL8(ctx, 'ir.model.fields',
                                    [('model', '=', model)]):
        field_name = clodoo.browseL8(ctx, 'ir.model.fields', field_id).name
        add_val(row, ctx, MYDICT, field_name)

    if 'name' not in vals:
        vals['name'] = 'PRODUCT'
    if 'company_id' not in vals:
        vals['company_id'] = get_company_id(ctx)

    ids = []
    if vals.get('code'):
        ids = clodoo.searchL8(ctx, model, [('default_code',
                                            '=',
                                            vals['code'])])
    if not ids and vals.get('default_code'):
        ids = clodoo.searchL8(ctx, model, [('default_code',
                                            '=',
                                            vals['default_code'])])
    if not ids:
        ids = clodoo.searchL8(ctx, model, [('name', '=', vals['name'])])
    if ids:
        product_id = ids[0]
        try:
            clodoo.writeL8(ctx, model, [product_id], vals)
        except BaseException:
            write_log("Cannot import %s" % vals['name'])
            try:
                clodoo.writeL8(ctx, model, [product_id], vals)
            except BaseException:
                pass
    else:
        try:
            product_id = clodoo.createL8(ctx, model, vals)
        except BaseException:
            write_log("Cannot create %s" % vals['name'])
            try:
                product_id = clodoo.createL8(ctx, model, vals)
            except BaseException:
                pass


def init_n_connect(flavour=None):
    title = 'Import products %s' % flavour or ''
    parser = z0lib.parseoptargs(title,
                                "© 2017-2018 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-c", "--config",
                        help="configuration command file",
                        dest="conf_fn",
                        metavar="file",
                        default='./import_products.conf')
    parser.add_argument("-d", "--dbname",
                        help="DB name",
                        dest="db_name",
                        metavar="file",
                        default='demo8')
    parser.add_argument("-f", "--filename",
                        help="Filename to import",
                        dest="csv_fn",
                        metavar="file",
                        default=False)
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    # Connect to DB
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    ctx['flavour'] = flavour
    if not ctx['csv_fn']:
        if flavour:
            sfx = '_'
        else:
            sfx = ''
        ctx['csv_fn'] = 'products%s%s.csv' % (sfx, flavour or '')
    oerp, uid, ctx = clodoo.oerp_set_env(confn=ctx['conf_fn'],
                                         db=ctx['db_name'],
                                         ctx=ctx)
    return oerp, uid, ctx
