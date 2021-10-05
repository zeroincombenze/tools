# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from import_partners import (init_n_connect, add_elem)
# import pdb


__version__ = "0.3.34.99"

MYDICT_C = {
    # 'is_company': 0,
    'old_customer_id': 0,
    'name': 1,
    'street': 2,
    'zip': 3,
    'city': 4,
    'state_id': 5,
    'country_id': 7,
    'vat': 8,
    'fiscalcode': 9,
    'comment': 11,
    'phone': 20,
    'mobile': 23,
    'email': 26,
}

MYDICT_S = {
    # 'is_company': 0,
    'old_customer_id': 0,
    'name': 1,
    'street': 2,
    'zip': 3,
    'city': 4,
    'state_id': 5,
    'country_id': 7,
    'vat': 8,
    'fiscalcode': 9,
    'comment': 11,
    'phone': 20,
    'mobile': 23,
    'email': 26,
}


if __name__ == "__main__":
    # pdb.set_trace()
    oerp, uid, ctx = init_n_connect(flavour='sicignano')
    print "Import data %s on DB %s" % (ctx['flavour'],
                                       ctx['db_name'])
    ctx['IN_country_id'] = 'name'
    dialect = 'excel'
    # pdb.set_trace()
    with open(ctx['csv_fn'], 'rbU') as f:
        hdr = False
        reader = csv.reader(f, dialect=dialect)
        for row in reader:
            if not hdr:
                hdr = True
                continue
            # print row[1]
            add_elem(row, ctx, MYDICT_C, MYDICT_S)
