# -*- coding: utf-8 -*-
# Copyright (C) 2018-2020 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Base library for continous test of Odoo apps
This module is Odoo version indipendent and may be used outside Odoo app (i.e.
with odoorc package).
For this reason, this software does not contain functions with sql call, like
search or browse.

Funcionc with sql call are in test_common.py file.
"""

from __future__ import print_function,unicode_literals
from past.builtins import basestring
from python_plus import unicodes

import os
import sys
import base64
import csv
# from zerobug import Z0BUG
from os0 import os0

__version__ = "1.0.0.2"


class Z0bugOdoo(object):

    def __init__(self, cls=None):
        self.cls = cls

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
        '''Return model xref list'''
        pymodel = model.replace('.', '_')
        if not hasattr(self, pymodel):
            self.get_data_file(model, '%s.csv' % pymodel)
        return list(getattr(self, pymodel))

    def get_test_values(self, model, xref):
        '''Return model values for test'''
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
        '''Write all record of model with test values'''
        pymodel = model.replace('.', '_')
        if not hasattr(self, pymodel):
            self.get_data_file(model, '%s.csv' % pymodel)
        for xref in getattr(self, pymodel):
            pass

    def write_diff(self, model, xid, vals):
        # vals = self.drop_unchanged_fields(vals, model, xid)
        if vals:
            if 'id' in vals:
                del vals['id']
            return self.cls.write(model, xid, vals)

    def store_xref(self, xref, model, company_id,
                   parent_id=None, parent_model=None, force=None):
        if parent_id and parent_model:
            xid = False
        else:
            xid = self.cls.ref(xref).id
        if not xid or force:
            vals = self.get_test_values(model, xref)
            if not vals:
                pass
            # vals, parent_name = self.bind_fields(
            #     model, vals, company_id,
            #     parent_id=parent_id, parent_model=parent_model)
            if xid:
                self.write_diff(model, xid, vals)
            else:
                if vals.get('id') and isinstance(vals['id'], int):
                    xid = vals['id']
                else:
                    xid = self.get_domain_field(model, vals, company_id,
                                                parent_id=parent_id,
                                                parent_name=parent_name)
                if xid:
                    self.write_diff(model, xid, vals)
                else:
                    if 'id' in vals:
                        del vals['id']
                    xid = self.create_id(vals)
                if not parent_id or not parent_model:
                    self.add_xref(xref, model, xid)
        return xid

    def build_model_data(self, model, xrefs=None, company_id=None,
                         child_model=None, seq_field=None, child_alias=None,
                         force=None):
        """Create a table with full demo data"""
        if xrefs and not isinstance(xrefs, (list, tuple)):
            xrefs = [xrefs]
        else:
            xrefs = self.get_test_xrefs(model)
            if child_model and not child_alias:
                xrefs = xrefs + self.get_test_xrefs(child_model)
        ref_ids = []
        parent_id = False
        parent_id_len = 0
        for xref in sorted(xrefs):
            if (not parent_id_len or
                    len(xref) <= parent_id_len or
                    xref == 'z0bug.partner_mycompany'):
                if not parent_id_len:
                    parent_id_len = len(xref) + 1
                parent_id = self.store_xref(
                    xref, model, company_id, force=force)
                if not parent_id:
                    continue
                if seq_field:
                    seq = 10
                    child_model = self.cls.env[child_model]
                    for child in child_model.search(
                            [(seq_field, '=', parent_id)],
                            order='sequence,id'):
                        child.write({'sequence': seq})
                        seq += 10
                if child_alias:
                    xref2 = xref.replace(child_alias[0], child_alias[1])
                    self.store_xref(
                        xref2, child_model, company_id,
                        parent_id=parent_id, parent_model=model, force=force)
                if model == 'account.invoice':
                    self.cls.env[model].browse(parent_id).compute_taxes()
                ref_ids.append(parent_id)
            elif parent_id:
                self.store_xref(xref, child_model, company_id,
                                parent_id=parent_id, parent_model=model,
                                force=force)
        return ref_ids
