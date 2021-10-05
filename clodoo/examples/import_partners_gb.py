# flake8: noqa
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from import_partners import (init_n_connect, add_elem)
# import pdb


__version__ = "0.3.34.99"

MYDICT_C = {
    'is_company': 0,
    # 'old_customer_id': 3,
    'name': 4,
    'name2': 5,
    'street': 6,
    'zip': 7,
    'city': 8,
    'state_id': 9,
    'phone': 10,
    'fax': 11,
    'email': 12,
    'vat': 13,
    'comment': 16,
}

MYDICT_S = {
    'is_company': 0,
    # 'old_customer_id': 3,
    'name': 4,
    'name2': 5,
    'street': 6,
    'zip': 7,
    'city': 8,
    'state_id': 9,
    'phone': 10,
    'fax': 11,
    'vat': 12,
}


if __name__ == "__main__":
    # pdb.set_trace()
    oerp, uid, ctx = init_n_connect(flavour='gb')
    print "Import data %s on DB %s" % (ctx['flavour'],
                                       ctx['db_name'])
    ctx['IN_country_id'] = 'name'
    dialect = 'excel'
    with open(ctx['csv_fn'], 'rbU') as f:
        hdr = False
        reader = csv.reader(f, dialect=dialect)
        for row in reader:
            if not hdr:
                hdr = True
                continue
            # print row[1]
            add_elem(row, ctx, MYDICT_C, MYDICT_S)
