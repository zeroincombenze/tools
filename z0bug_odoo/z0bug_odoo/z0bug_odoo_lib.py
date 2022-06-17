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

from __future__ import print_function, unicode_literals

# import sys
import base64
import csv
import os

from openpyxl import load_workbook

# from past.builtins import basestring
from python_plus import unicodes

__version__ = "1.0.16"


class Z0bugOdoo(object):
    def __init__(self, release=None):
        try:
            import odoo.release as release

            self.release = release
        except ImportError:
            try:
                import openerp.release as release

                self.release = release
            except ImportError:
                self.release = None

    def get_image_filename(self, xref):
        file_image = os.path.join(os.path.dirname(__file__), 'data', '%s.png' % xref)
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

    def save_row(self, model, row):
        if 'id' in row:
            for field in row.copy().keys():
                if row[field] == r'\N':
                    del row[field]
                elif row[field] == r'\\N':
                    row[field] = r'\N'
            getattr(self, model)[row['id']] = unicodes(row)

    def get_data_file_xlsx(self, model, full_fn):
        pymodel = model.replace('.', '_')
        wb = load_workbook(full_fn)
        for sheet in wb:
            break
        colnames = []
        for column in sheet.columns:
            colnames.append(column[0].value)
        hdr = True
        for line in sheet.rows:
            if hdr:
                hdr = False
                setattr(self, pymodel, {})
                continue
            row = {}
            for column, cell in enumerate(line):
                row[colnames[column]] = cell.value
            self.save_row(pymodel, row)

    def get_data_file_csv(self, model, full_fn):
        pymodel = model.replace('.', '_')
        with open(full_fn, 'r') as fd:
            hdr = True
            csv_obj = csv.DictReader(fd, fieldnames=[], restkey='undef_name')
            for row in csv_obj:
                if hdr:
                    hdr = False
                    csv_obj.fieldnames = row['undef_name']
                    setattr(self, pymodel, {})
                    continue
                self.save_row(pymodel, row)

    def get_data_file(self, model, filename):
        full_fn = os.path.join(os.path.dirname(__file__), 'data', filename)
        if os.path.isfile('%s.xlsx' % full_fn):
            return self.get_data_file_xlsx(model, '%s.xlsx' % full_fn)
        else:
            return self.get_data_file_csv(model, '%s.csv' % full_fn)

    def get_test_xrefs(self, model):
        """Return model xref list"""
        pymodel = model.replace('.', '_')
        if not hasattr(self, pymodel):
            self.get_data_file(model, pymodel)
        return list(getattr(self, pymodel))

    def get_test_values(self, model, xref):
        """Return model values for test"""
        xids = xref.split('.')
        if len(xids) == 1:
            xids[0], xids[1] = 'z0bug', xids[0]
        pymodel = model.replace('.', '_')
        if not hasattr(self, pymodel):
            self.get_data_file(model, pymodel)
        if xref not in getattr(self, pymodel):
            if xids[0] == 'z0bug':
                raise KeyError('Invalid xref %s for model %s!' % (xref, model))
            return {}
        return getattr(self, pymodel)[xref]

    def initialize_model(self, model):
        """Write all record of model with test values"""
        pymodel = model.replace('.', '_')
        if not hasattr(self, pymodel):
            self.get_data_file(model, pymodel)
        for xref in getattr(self, pymodel):
            pass
