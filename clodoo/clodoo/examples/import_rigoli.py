#!/usr/bin/env python
# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from __future__ import absolute_import
# from __future__ import division
from future import standard_library
from builtins import *                                             # noqa: F403
import csv
from import_records import (init_n_connect, set_header, add_item)
standard_library.install_aliases()                                 # noqa: E402


__version__ = "0.3.34.99"

MYDICT_C = {
}

MYDICT_S = {
}

TNL = {
    'type': {
        'Shipping': 'delivery',
        'Contact': 'contact',
        'Invoice': 'invoice',
        'Stockable Product': 'product',
        'Consumable': 'consu',
        'Service': 'service',
    },
    'codice_destinatario': {'0': '0000000'},
}

SKEYS = {
    'res.partner': ['name', 'vat', 'codicefiscale', 'type'],
    'product.template': ['name', 'default_code', 'type'],
}


if __name__ == "__main__":
    uid, ctx = init_n_connect(flavour='rigoli')
    print("Import data from %s on DB %s" % (ctx['model'],
                                            ctx['db_name']))
    skeys = SKEYS[ctx['model']]
    ctr = 0
    with open(ctx['csv_fn'], 'rbU') as fd:
        hdr = False
        reader = csv.reader(fd, dialect='excel')
        for row in reader:
            if not hdr:
                set_header(
                    ctx, row, ctx['model'], MYDICT_C, MYDICT_S, TNL, skeys)
                hdr = True
                continue
            add_item(ctx, row)
            ctr += 1
    print('%d record added ...' % ctr)
