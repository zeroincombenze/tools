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
from past.builtins import long

# import sys
import os
import base64
import csv

from openpyxl import load_workbook

from python_plus import unicodes

__version__ = "2.0.17"


class Z0bugOdoo(object):
    def __init__(self, release=None):
        try:                                                        # pragma: no cover
            import odoo.release as release

            self.release = release
        except ImportError:
            try:
                import openerp.release as release

                self.release = release
            except ImportError:
                self.release = None
        self.model_list = []
        self.caller_data_dir = self.default_data_dir = None
        self.declare_data_dir()

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

    def get_pymodel(self, model):
        return model.replace('.', '_')

    def save_row(self, pymodel, row):
        if 'id' in row:
            for field in row.copy().keys():
                if row[field] == r'\N':
                    del row[field]
                elif row[field] == r'\\N':
                    row[field] = r'\N'
            if pymodel == "account_account" and isinstance(row["code"], (int, long)):
                row["code"] = "%s" % row["code"]
            getattr(self, pymodel)[row['id']] = unicodes(row)

    def get_data_file_xlsx(self, model, fqn, sheet_name=None):
        pymodel = self.get_pymodel(model)
        wb = load_workbook(fqn)
        sheet = wb.active if not sheet_name else wb[sheet_name]
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

    def get_data_file_csv(self, model, fqn):
        pymodel = self.get_pymodel(model)
        with open(fqn, 'r') as fd:
            hdr = True
            csv_obj = csv.DictReader(fd, fieldnames=[], restkey='undef_name')
            for row in csv_obj:
                if hdr:
                    hdr = False
                    csv_obj.fieldnames = row['undef_name']
                    setattr(self, pymodel, {})
                    continue
                self.save_row(pymodel, row)

    def match_file_type(self, fqn, bin_types=[]):
        bin_types = bin_types or ["xml", "xlsx", "csv", "png", "jpg"]
        if not hasattr(bin_types, "__iter__"):
            bin_types = [bin_types]                                 # pragma: no cover
        if not os.path.isfile(fqn):
            found = False
            for btype in bin_types:
                if os.path.isfile("%s.%s" % (fqn, btype)):
                    fqn = "%s.%s" % (fqn, btype)
                    found = True
                    break
            if not found:
                fqn = None
        return fqn

    def get_data_filename(self, filename, bin_types=[], raise_if_not_found=True):
        fqn = None
        if self.caller_data_dir:
            fqn = self.match_file_type(
                os.path.join(self.caller_data_dir, filename), bin_types=bin_types)
        if not fqn and self.default_data_dir:
            fqn = self.match_file_type(
                os.path.join(self.default_data_dir, filename), bin_types=bin_types)
        if not fqn and raise_if_not_found:
            raise KeyError('Filename %s not found!' % filename)
        return fqn

    def get_data_file(self, model, filename, raise_if_not_found=True):
        fqn = self.get_data_filename(
            filename, bin_types=["xlsx", "csv"], raise_if_not_found=raise_if_not_found)
        self.model_list.append(model)
        if fqn and fqn.endswith(".xlsx"):
            self.get_data_file_xlsx(model, fqn)
        elif fqn and fqn.endswith(".csv"):
            self.get_data_file_csv(model, fqn)
        else:
            setattr(self, self.get_pymodel(model), {})

    def get_test_xrefs(self, model):
        """Return model xref list"""
        pymodel = self.get_pymodel(model)
        if not hasattr(self, pymodel) or not getattr(self, pymodel):
            self.get_data_file(model, pymodel, raise_if_not_found=False)
        return list(getattr(self, pymodel).keys())

    def get_test_values(self, model, xref, raise_if_not_found=True):
        """Return model values for test"""
        xids = xref.split('.')
        if len(xids) == 1:
            xids[0], xids[1] = 'z0bug', xids[0]
        if xref not in self.get_test_xrefs(model):
            if xids[0] == 'z0bug' and raise_if_not_found:
                raise KeyError('Invalid xref %s for model %s!' % (xref, model))
            return {}
        return getattr(self, self.get_pymodel(model))[xref]

    def initialize_model(self, model, merge=False):
        """Write all record of model with test values"""
        pymodel = self.get_pymodel(model)
        if not merge and hasattr(self, pymodel):
            delattr(self, pymodel)

    def declare_data_dir(self, data_dir=None, merge=False, raise_if_not_found=True):
        if data_dir:
            if not os.path.isdir(data_dir):
                if raise_if_not_found:
                    raise KeyError("Directory %s not found in the system" % data_dir)
                return
        old_caller_data_dir = self.caller_data_dir
        self.caller_data_dir = data_dir
        old_default_data_dir = self.default_data_dir
        self.default_data_dir = (
            os.path.join(os.path.dirname(__file__), 'data')
            if merge or (self.caller_data_dir is None
                         and self.default_data_dir is None) else None)
        if (
                self.caller_data_dir != old_caller_data_dir
                or self.default_data_dir != old_default_data_dir
        ):
            for model in self.model_list:
                self.initialize_model(model, merge=merge)




