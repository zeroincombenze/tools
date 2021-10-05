# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from import_partners import (init_n_connect, add_elem)
# import pdb


__version__ = "0.3.34.99"

MYDICT_C = {
    'is_company': 0,
    'old_customer_id': 1,
    'name': 2,
    'city': 3,
    'state_id': 4,
    'vat': 5,
    'email': 6,
    'street': 8,
    'zip': 9,
    'country_id': 12,
    'phone': 14,
    'mobile': 15,
    'fiscalcode': 18,
    'comment': 25,
}

MYDICT_S = {
    'is_company': 0,
    'old_supplier_id': 1,
    'name': 2,
    'city': 3,
    'state_id': 4,
    'vat': 5,
    'email': 6,
    'street': 7,
    'zip': 8,
    'country_id': 11,
    'phone': 13,
    'mobile': 14,
    'fiscalcode': 17,
    'comment': 28,
}


if __name__ == "__main__":
    # pdb.set_trace()
    oerp, uid, ctx = init_n_connect(flavour='merkatrade')
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
