# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import print_function,unicode_literals
from past.builtins import basestring

import os
import sys
import csv
from zerobug import Z0BUG


__version__ = "0.1.0.1.1"


class Z0bugOdoo(object):

    def get_data_file(self, model, csv_fn):
        # csv.register_dialect('z0bug',
        #                      delimiter=b',',
        #                      quotechar=b'"',
        #                      quoting=csv.QUOTE_MINIMAL)
        full_fn = os.path.join(os.path.dirname(__file__), 'data', csv_fn)
        pymodel = model.replace('.', '_')
        with open(full_fn, 'rb') as fd:
            hdr = False
            csv_obj = csv.DictReader(fd,
                                     fieldnames=[],
                                     restkey='undef_name',)
            # dialect='z0bug')
            for row in csv_obj:
                if not hdr:
                    hdr = True
                    csv_obj.fieldnames = row['undef_name']
                    setattr(self, pymodel, {})
                    continue
                if 'id' not in row:
                    continue
                getattr(self, pymodel)[row['id']] = row

    def get_test_values(self, model, xid):
        '''Return model values for test'''
        xrefs = xid.split('.')
        if len(xrefs) == 1:
            xrefs[0], xrefs[1] = 'z0bug', xrefs[0]
        if xrefs[0] == 'z0bug':
            pymodel = model.replace('.', '_')
            if not hasattr(self, pymodel):
                self.get_data_file(model, '%s.csv' % pymodel)
            if xid not in getattr(self, pymodel):
                raise KeyError('Invalid xid %s for model %s!' % (xid, model))
            return getattr(self, pymodel)[xid]
        return {}
