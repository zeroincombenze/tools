# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import print_function
from builtins import str

import sys
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


__version__='0.1.0.7'


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

    def settle_fields(self, model, vals, how_id=None):
        for name in vals.copy():
            if name == 'id':
                if how_id == 'del':
                    del vals[name]
                    continue
                elif how_id == 'keep':
                    continue
            field = self.search_rec('ir.model.fields',
                                    [('model', '=', model),
                                     ('name', '=', name)])
            if isinstance(field, (list, tuple)) and len(field):
                field = field[0]
            if not field:
                del vals[name]
            elif (field.ttype == 'many2one' and
                  isinstance(vals[name], str) and
                  len(vals[name].split('.')) == 2):
                vals[name] = self.ref_id(vals[name])
        return vals

    def get_ref_value(self, model, xref):
        if not hasattr(self, 'Z0bugOdoo'):
            self.Z0bugOdoo = Z0bugOdoo()
        return self.settle_fields(
            model, self.Z0bugOdoo.get_test_values(model, xref),
            how_id='keep')

    def build_model_data(self, model, xrefs):
        if not isinstance(xrefs, (list, tuple)):
            xrefs = [xrefs]
        for xref in xrefs:
            vals = self.get_ref_value(model, xref)
            if not vals:
                pass
            elif 'id' in vals:
                xids = xref.split('.')
                if len(xids) == 2:
                    try:
                        id = self.ref_id(xref)
                    except BaseException:
                        id = None
                elif vals['id']:
                    id = vals['id']
                else:
                    id = None
                del vals['id']
                if id:
                    self.write_rec(model, id, vals)
                else:
                    id = self.create_id(model, vals)
                    if len(xids) == 2:
                        vals = {
                            'module': xids[0],
                            'model': model,
                            'name': xids[1],
                            'res_id': id,
                        }
                        self.create_rec('ir.model.data', vals)
            else:
                raise KeyError('Invalid xref %s for model %s!' % (xref, model))

    def set_test_company(self, xref=None):
        '''Set company to test'''
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

    def settle_fields(self, model, vals, how_id=None):
        return Z0bugBaseCase.settle_fields(self, model, vals, how_id)

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

    def settle_fields(self, model, vals, how_id=None):
        return Z0bugBaseCase.settle_fields(self, model, vals, how_id)

    def get_ref_value(self, model, xref):
        return Z0bugBaseCase.get_ref_value(self, model, xref)

    def build_model_data(self, model, xrefs):
        return Z0bugBaseCase.build_model_data(self, model, xrefs)

    def set_test_company(self, xref=None):
        return Z0bugBaseCase.set_test_company(self, xref)
