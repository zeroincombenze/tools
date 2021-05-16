# -*- coding: utf-8 -*-
# Copyright (C) 2018-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Base library for continuous test of Odoo apps
This module is Odoo version independent and may be used outside Odoo app (i.e.
with odoorc package).
For this reason, this software does not contain functions with sql call, like
search or browse.

Functions with sql call are in test_common.py file.
"""

from __future__ import print_function,unicode_literals
# from past.builtins import basestring
from python_plus import unicodes

import os
# import sys
import base64
import csv
# from zerobug import Z0BUG
# from os0 import os0

__version__ = "1.0.2"


class Z0bugOdoo(object):

    def __init__(self, release=None):
        self.release = None

    def get_image_filename(self, xref):
        file_image = os.path.join(
            os.path.dirname(__file__),
            'data',
            '%s.png' % xref)
        if os.path.isfile(file_image):
            return file_image
        return False

    def get_image(self, xref):
        file_image = self.get_image_filename(xref)
        if file_image:
            with open(file_image, 'rb') as fd:
                image = fd.read()
            return base64.b64encode(image)
        return False

    def get_data_file(self, model, csv_fn):
        full_fn = os.path.join(os.path.dirname(__file__), 'data', csv_fn)
        pymodel = model.replace('.', '_')
        with open(full_fn, 'r') as fd:
            hdr = False
            csv_obj = csv.DictReader(fd,
                                     fieldnames=[],
                                     restkey='undef_name')
            for row in csv_obj:
                if not hdr:
                    hdr = True
                    csv_obj.fieldnames = row['undef_name']
                    setattr(self, pymodel, {})
                    continue
                if 'id' not in row:
                    continue
                getattr(self, pymodel)[row['id']] = unicodes(row)

    def get_test_xrefs(self, model):
        """Return model xref list"""
        pymodel = model.replace('.', '_')
        if not hasattr(self, pymodel):
            self.get_data_file(model, '%s.csv' % pymodel)
        return list(getattr(self, pymodel))

    def get_test_values(self, model, xref):
        """Return model values for test"""
        xids = xref.split('.')
        if len(xids) == 1:
            xids[0], xids[1] = 'z0bug', xids[0]
        if xids[0] == 'z0bug':
            pymodel = model.replace('.', '_')
            if not hasattr(self, pymodel):
                self.get_data_file(model, '%s.csv' % pymodel)
            if xref not in getattr(self, pymodel):
                raise KeyError('Invalid xref %s for model %s!' % (xref, model))
            return getattr(self, pymodel)[xref]
        return {}

    def initialize_model(self, model):
        """Write all record of model with test values"""
        pymodel = model.replace('.', '_')
        if not hasattr(self, pymodel):
            self.get_data_file(model, '%s.csv' % pymodel)
        for xref in getattr(self, pymodel):
            pass
