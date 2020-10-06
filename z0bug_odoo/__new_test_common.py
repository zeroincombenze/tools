# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import print_function
from builtins import str

import sys
from datetime import date, datetime, timedelta
from os0 import os0
from z0bug_odoo_lib import Z0bugOdoo
try:
    import odoo.release as release
except ImportError:
    try:
        import openerp.release as release
    except ImportError:
        release = ''
if release:
    if int(release.major_version.split('.')[0]) < 10:
        import openerp.tests.common as test_common
        from openerp.modules.module import get_module_resource
        from openerp import workflow
    else:
        import odoo.tests.common as test_common
        from odoo.modules.module import get_module_resource
else:
    print('No Odoo environment found!')
    sys.exit(0)


__version__='1.0.0.2'


class Z0bugBaseCase(test_common.BaseCase):

    def pool_env(self, model):
        """Return model pool_environment"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model)
        return self.env[model]

    def create_id(self, model, values):
        """Create a new record for test"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).create(self.cr,
                                               self.uid,
                                               values)
        return self.env[model].create(values).id

    def create_rec(self, model, values):
        """Create a new record for test"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).browse(
                self.cr,
                self.uid,
                self.registry(model).create(self.cr,
                                            self.uid,
                                            values))
        return self.env[model].create(values)

    def write_rec(self, model, id, values):
        """Write existent record"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).write(self.cr, self.uid, [id], values)
        return self.env[model].search([('id', '=', id)]).write(values)

    def write_ref(self, xref, values):
        """Browse and write existent record"""
        return self.browse_ref(xref).write(values)

    def browse_rec(self, model, id):
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).browse(self.cr, self.uid, id)
        return self.env[model].browse(id)

    def search_rec(self, model, args):
        """Search records - Syntax search(model, *args)
        Warning! Do not use with Odoo 7.0: result may fails!"""
        if int(release.major_version.split('.')[0]) < 8:
            ir_model = self.registry(model)
            return ir_model.browse(self.cr, self.uid,
                ir_model.search(self.cr, self.uid, args))
        return self.env[model].search(args)

    def ref_id(self, xref):
        """Return reference id"""
        if int(release.major_version.split('.')[0]) < 8:
            if xref.startswith('base.state_it_'):
                # 7.0 compatibility
                try:
                    return ('l10n_it_base.it_%s' % xref[14:].lower())
                except BaseException:
                    pass
            return self.ref(xref)
        return self.env.ref(xref).id

    def ref(self, xref):
        """Return reference record"""
        if int(release.major_version.split('.')[0]) < 8:
            xrefs = xref.split('.')
            if len(xrefs) == 2:
                model = 'ir.model.data'
                rec = self.search_rec(model,
                                      [('module', '=', xrefs[0]),
                                       ('name', '=', xrefs[1])])
                if not rec and xref.startswith('base.state_it_'):
                    rec = self.search_rec(
                        [model,
                         ('module', '=', 'base'),
                         ('name', '=', 'it_%s' % xref[1][14:].lower())])
                return rec
        return self.env.ref(xref)

    def add_xref(self, xref, model, xid):
        xrefs = xref.split('.')
        if len(xrefs) == 2:
            vals = {
                'module': xrefs[0],
                'model': model,
                'name': xrefs[1],
                'res_id': id,
            }
            return self.create_rec('ir.model.data', vals)
        return False

    def get_ref_value(self, model, xref, parent_id=None, parent_model=None):
        if not hasattr(self, 'Z0bugOdoo'):
            self.Z0bugOdoo = Z0bugOdoo()
        return model, self.Z0bugOdoo.get_test_values(model, xref)

    # def build_model_data(self, model, xrefs):
    #     if not isinstance(xrefs, (list, tuple)):
    #         xrefs = [xrefs]
    #     for xref in sorted(xrefs):
    #         vals = self.get_ref_value(model, xref)
    #         if not vals:
    #             pass
    #         elif 'id' in vals:
    #             xids = xref.split('.')
    #             if len(xids) == 2:
    #                 try:
    #                     id = self.ref_id(xref)
    #                 except BaseException:
    #                     id = None
    #             elif vals['id']:
    #                 id = vals['id']
    #             else:
    #                 id = None
    #             del vals['id']
    #             if id:
    #                 self.write_rec(model, id, vals)
    #             else:
    #                 id = self.create_id(model, vals)
    #                 if len(xids) == 2:
    #                     vals = {
    #                         'module': xids[0],
    #                         'model': model,
    #                         'name': xids[1],
    #                         'res_id': id,
    #                     }
    #                     self.create_rec('ir.model.data', vals)
    #         else:
    #             raise KeyError('Invalid xref %s for model %s!' % (xref, model))

    def set_test_company(self, xref=None):
        """Set company to test"""
        if not xref:
            for xref1, model in (('z0bug.partner_mycompany', 'res.partner'),
                                 ('z0bug.mycompany', 'res.company')):
                self.build_model_data(model, xref1)
            xref = 'z0bug.mycompany'
        xref_id = self.ref_id(xref)
        # There are two separate write because "company_id" assignment fails if
        # company_id is not in "company_ids" at the time of the write
        if int(release.major_version.split('.')[0]) < 8:
            self.registry('res.user').write(
                self.cr, self.uid, [self.uid], {'company_ids': [(4, xref_id)]})
            self.registry('res.user').write(
                self.cr, self.uid, [self.uid], {'company_id': xref_id})
        else:
            self.env.user.write({'company_ids': [(4, xref_id)]})
            self.env.user.write({'company_id': xref_id})
        return xref_id

    def field_datetime(self, model, vals, company_id, field, attrs):
        return vals, False

    def field_date(self, model, vals, company_id, field, attrs):
        if vals[field].startswith('+'):
            vals[field] = str(
                date.today() + timedelta(int(vals[field][1:])))
        elif vals[field].startswith('-'):
            vals[field] = str(
                date.today() - timedelta(int(vals[field][1:])))
        elif vals[field].find('<#') >= 0:
            items = vals[field].split('-')
            for i, item in enumerate(items):
                if item == '<#':
                    if i == 0:
                        items[i] = date.today().year - 1
                    elif i == 1:
                        items[i] = date.today().month - 1
                    elif i == 2:
                        items[i] = date.today().day - 1
                    if item[i] == 0:
                        item[i] = 1
            vals[field] = '%04d-%02d-%02d' % (
                int(items[0]), int(items[1]), int(items[2]))
        elif vals[field].find('#>') >= 0:
            items = vals[field].split('-')
            for i, item in enumerate(items):
                if item == '#>':
                    if i == 0:
                        items[i] = date.today().year + 1
                    elif i == 1:
                        items[i] = date.today().month + 1
                        if item[i] > 12:
                            item[i] = 12
                    elif i == 2:
                        items[i] = date.today().day + 1
                        if item[i] > 31:
                            item[i] = 31
            vals[field] = '%04d-%02d-%02d' % (
                int(items[0]), int(items[1]), int(items[2]))
        elif vals[field].find('#') >= 0:
            items = vals[field].split('-')
            for i, item in enumerate(items):
                if item == '#':
                    if i == 0:
                        items[i] = date.today().year
                    elif i == 1:
                        items[i] = date.today().month
                    elif i == 2:
                        items[i] = date.today().day
            vals[field] = '%04d-%02d-%02d' % (
                int(items[0]), int(items[1]), int(items[2]))
        return vals, False

    def magic_field(self, model, vals, company_id, field, attrs):
        return vals, False

    def bind_fields(self, model, vals, company_id,
                parent_id=None, parent_model=None, how_id=None):
        """TODO: write implementation"""
        self.setup_model_structure(model)
        model_model = self.env[model]
        parent_name = ''
        for field in vals.copy():
            if how_id == 'del':
                del vals[field]
                continue
            elif how_id == 'keep':
                continue
            attrs = self.STRUCT[model].get(field, {})
            if not attrs:
                if (model == 'account.payment.term.line' and
                        field == 'months' and
                        vals[field]):
                    vals['days'] = (int(vals[field]) * 30) - 2
                del vals[field]
            vals, done = self.magic_field(model, vals, company_id, attrs)
            if done:
                continue
            elif field == 'id':
                continue
            elif parent_id and attrs.get('relation') == parent_model:
                vals[field] = parent_id
                parent_name = field
            elif field == 'company_id':
                vals[field] = company_id
                continue
            elif (attrs['ttype'] in (
                    'many2one', 'one2many', 'many2many') and
                  len(vals[field].split('.')) == 2):
                if attrs['ttype'] == 'many2one':
                    vals[field] = self.env_ref(vals[field])
                else:
                    vals[field] = [(6, 0, [self.env_ref(vals[field])])]
                continue
            elif attrs['ttype'] == 'boolean':
                vals[field] = os0.str2bool(vals[field], False)
            elif attrs['ttype'] == 'date':
                pass
            elif attrs['ttype'] == 'datetime':
                if vals[field].startswith('+'):
                    vals[field] = str(
                        datetime.today() + timedelta(int(vals[field][1:])))
                elif vals[field].startswith('-'):
                    vals[field] = str(
                        datetime.today() - timedelta(int(vals[field][1:])))
            elif attrs.get('relation'):
                self.setup_model_structure(attrs['relation'])
                value = self.get_domain_field(model, vals, company_id,
                                              field=field)
                if value:
                    vals[field] = value
                else:
                    del vals[field]


            if (field.ttype == 'many2one' and
                  isinstance(vals[name], str) and
                  len(vals[name].split('.')) == 2):
                vals[name] = self.ref_id(vals[name])
        return vals

    def drop_unchanged_fields(self, vals, model, xid):
        rec = None
        if model and xid:
            rec = self.browse_rec(model, xid)
        for field in vals.copy():
            attrs = self.STRUCT[model].get(field, {})
            if not attrs:
                del vals[field]
            if rec:
                if attrs['ttype'] == 'many2one':
                    if rec[field] and vals[field] == rec[field].id:
                        del vals[field]
                elif attrs['ttype'] == 'boolean':
                    if isinstance(
                            vals[field], bool) and vals[field] == rec[field]:
                        del vals[field]
                    elif os0.str2bool(vals[field], False) == rec[field]:
                        del vals[field]
                elif (isinstance(vals[field], (basestring, int)) and
                      vals[field] == rec[field]):
                    del vals[field]
        return vals

    def get_domain_field(self, model, vals, company_id,
                         parent_id=None, parent_name=None):
        """TODO: write implementation"""
        return False

    def write_diff(self, model, xid, vals):
        vals = self.drop_unchanged_fields(vals, model, xid)
        if vals:
            if 'id' in vals:
                del vals['id']
            return self.write_rec(model, xid, vals)

    def store_xref(self, xref, model, company_id,
                   parent_id=None, parent_model=None, force=None):
        if parent_id and parent_model:
            xid = False
        else:
            xid = self.ref_id(xref)
        if not xid or force:
            vals = self.get_ref_value(model, xref)
            if not vals:
                pass
            vals, parent_name = self.bind_fields(
                model, vals, company_id,
                parent_id=parent_id, parent_model=parent_model)
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
            xrefs = self.Z0bugOdoo.get_test_xrefs(model)
            if child_model and not child_alias:
                xrefs = xrefs + self.Z0bugOdoo.get_test_xrefs(child_model)
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
                    child_model = self.env[child_model]
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
                    self.env[model].browse(parent_id).compute_taxes()
                ref_ids.append(parent_id)
            elif parent_id:
                self.store_xref(xref, child_model, company_id,
                                parent_id=parent_id, parent_model=model,
                                force=force)
        return ref_ids


class TransactionCase(test_common.TransactionCase, Z0bugBaseCase):

    def setUp(self):
        Z0bugBaseCase.setUp(self)

    def pool_env(self, model):
        return Z0bugBaseCase.pool_env(self, model)

    def create_id(self, model, values):
        return Z0bugBaseCase.create_id(self, model, values)

    def create_rec(self, model, values):
        return Z0bugBaseCase.create_rec(self, model, values)

    def write_rec(self, model, id, values):
        return Z0bugBaseCase.write_rec(self, model, id, values)

    def write_ref(self, model, id, values):
        return Z0bugBaseCase.write_ref(self, model, id, values)

    def browse_rec(self, model, id):
        return Z0bugBaseCase.browse_rec(self, model, id)

    def search_rec(self, model, args):
        return Z0bugBaseCase.search_rec(self, model, args)

    def ref_id(self, xref):
        return Z0bugBaseCase.ref_id(self, xref)

    def bind_fields(self, model, vals, how_id=None):
        return Z0bugBaseCase.bind_fields(self, model, vals, how_id)

    def get_ref_value(self, model, xref):
        return Z0bugBaseCase.get_ref_value(self, model, xref)

    def build_model_data(self, model, xrefs):
        return Z0bugBaseCase.build_model_data(self, model, xrefs)

    def set_test_company(self, xref=None):
        return Z0bugBaseCase.set_test_company(self, xref)


class SingleTransactionCase(test_common.SingleTransactionCase, Z0bugBaseCase):

    def pool_env(self, model):
        return Z0bugBaseCase.pool_env(self, model)

    def create_id(self, model, values):
        return Z0bugBaseCase.create_id(self, model, values)

    def create_rec(self, model, values):
        return Z0bugBaseCase.create_rec(self, model, values)

    def write_rec(self, model, id, values):
        return Z0bugBaseCase.write_rec(self, model, id, values)

    def write_ref(self, model, id, values):
        return Z0bugBaseCase.write_ref(self, model, id, values)

    def browse_rec(self, model, id):
        return Z0bugBaseCase.browse_rec(self, model, id)

    def bind_fields(self, model, vals, how_id=None):
        return Z0bugBaseCase.bind_fields(self, model, vals, how_id)

    def get_ref_value(self, model, xref):
        return Z0bugBaseCase.get_ref_value(self, model, xref)

    def build_model_data(self, model, xrefs):
        return Z0bugBaseCase.build_model_data(self, model, xrefs)

    def set_test_company(self, xref=None):
        return Z0bugBaseCase.set_test_company(self, xref)
