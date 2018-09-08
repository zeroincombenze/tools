#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from import_products import (init_n_connect, add_elem)
# import pdb


__version__ = "0.2.0"

MYDICT = {
    'default_code': 0,
    'lst_price': 1,
    'name': 2,
    'partner_ref': 6,
    'description': 11,
}


if __name__ == "__main__":
    oerp, uid, ctx = init_n_connect(flavour='gb')
    print "Import data %s on DB %s" % (ctx['flavour'],
                                       ctx['db_name'])
    dialect = 'excel'
    with open(ctx['csv_fn'], 'rbU') as f:
        hdr = False
        reader = csv.reader(f, dialect=dialect)
        for row in reader:
            if not hdr:
                hdr = True
                continue
            # print row[1]
            add_elem(row, ctx, MYDICT)
