# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from import_partners import (init_n_connect, add_elem)
# import pdb


__version__ = "0.3.34.99"

MYDICT_C = {
    'old_customer_id': 0,
    'name': 4,
    'vat': 7,
    'fiscalcode': 8,
    'is_company': 15,
    'street': 17,
    'country_id': 19,
    'city': 21,
    'state_id': 22,
    'zip': 23,
    'phone': 26,
    'mobile': 28,
    'email': 30,
    'website': 31,
    'individual': 34,
}

MYDICT_S = {
    'is_company': 0,
    'old_supplier_id': 0,
    'name': 5,
    'vat': 8,
    'fiscalcode': 9,
    'street': 18,
    'zip': 20,
    'city': 21,
    'state_id': 23,
    'country_id': 24,
    'individual': 27,
    'phone': 127,
    'mobile': 129,
    'email': 131,
    'website': 132,
}


if __name__ == "__main__":
    # pdb.set_trace()
    oerp, uid, ctx = init_n_connect(flavour='fitness')
    print "Import data %s on DB %s" % (ctx['flavour'],
                                       ctx['db_name'])
    ctx['IN_country_id'] = 'code'
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
