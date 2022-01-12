#!/usr/bin/env python
# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from __future__ import absolute_import
# from __future__ import division
from future import standard_library
from builtins import *                                             # noqa: F403
import csv
from import_records import (init_n_connect, import_from_csv, copy_db)
standard_library.install_aliases()                                 # noqa: E402


__version__ = "1.0.1"

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
    uid, ctx, src_uid, src_ctx = init_n_connect(flavour='rigoli')
    skeys = SKEYS[ctx['model']]
    if src_ctx:
        print("Copy data %s from DB %s to DB %s" % (ctx['model'],
                                                    src_ctx['src_db_name'],
                                                    ctx['db_name']))
        import pdb
        pdb.set_trace()
        ctr = copy_db(ctx, src_ctx, MYDICT_C, MYDICT_S, TNL, skeys)
    else:
        print("Import data %s from %s into DB %s" % (ctx['model'],
                                                     ctx['csv_fn'],
                                                     ctx['db_name']))
        ctr = import_from_csv(ctx, MYDICT_C, MYDICT_S, TNL, skeys)
    print('%d record added ...' % ctr)
