# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import print_function

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


__version__='0.1.0.1.1'


class BaseCase(test_common.BaseCase):

    def pool(self, model):
        """Return model pool"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model)
        return self.env[model]


class TransactionCase(test_common.TransactionCase):

    def setUp(self):
        return super(TransactionCase, self).setUp()


    def pool(self, model):
        """Return model pool"""
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
                self.pool(model).create(self.cr,
                                        self.uid,
                                        values))
        return self.env[model].create(values)

    def write_rec(self, model, id, values):
        """Write existent record"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).write(self.cr, self.uid, [id], values)
        return self.env[model].search([('id', '=', id)]).write(values)

    def browse_rec(self, model, id):
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).browse(self.cr, self.uid, id)
        return self.env[model].browse(id)

    def env612(self, model):
        """Return model pool"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model)
        return self.env[model]

    def ref612(self, xid):
        """Return reference id"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.ref(xid)
        return self.env.ref(xid).id

    def search612(self, model, args):
        """Search record ids - Syntax search(model, *args)
        Warning! Do not use with Odoo 7.0: result may fails!"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).search(self.cr, self.uid, args)
        return self.env[model].search(args)

    def write_ref(self, xid, values):
        """Browse and write existent record"""
        return self.browse_ref(xid).write(values)

    def get_ref_value(self, model, xid):
        if not hasattr(self, 'Z0bugOdoo'):
            self.Z0bugOdoo = Z0bugOdoo()
        return self.Z0bugOdoo.get_test_values(model, xid)

    def build_model_data(self, model, xrefs):
        if not isinstance(xrefs, (list, tuple)):
            xrefs = [xrefs]
        for xid in xrefs:
            vals = self.get_ref_value(model, xid)
            if not vals:
                pass
            elif 'id' in vals:
                xids = xid.split('.')
                ids = self.search612('ir.model.data',
                                     [('module', '=', xids[0]),
                                      ('name', '=', xids[1])])
                del vals['id']
                if ids:
                    id = ids[0]
                    self.write_rec(model, id, vals)
                else:
                    id = self.create_id(model, vals)
                    vals = {
                        'module': xid[0],
                        'model': model,
                        'name': xid[1],
                        'res_id': id,
                    }
                    self.create_rec('ir.model.data', vals)
            else:
                raise KeyError('Invalid xid %s for model %s!' % (xid, model))

class SingleTransactionCase(test_common.SingleTransactionCase):


    def pool(self, model):
        """Return model pool"""
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
                self.pool(model).create(self.cr,
                                        self.uid,
                                        values))
        return self.env[model].create(values)

    def write_rec(self, model, id, values):
        """Write existent record"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).write(self.cr, self.uid, [id], values)
        return self.env[model].search([('id', '=', id)]).write(values)

    def browse_rec(self, model, id):
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).browse(self.cr, self.uid, id)
        return self.env[model].browse(id)

    def env612(self, model):
        """Return model pool"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model)
        return self.env[model]

    def ref612(self, xid):
        """Return reference id"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.ref(xid)
        return self.env.ref(xid).id

    def search612(self, model, args):
        """Search record ids - Syntax search(model, *args)
        Warning! Do not use with Odoo 7.0: result may fails!"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).search(self.cr, self.uid, args)
        return self.env[model].search(args)

    def write_ref(self, xid, values):
        """Browse and write existent record"""
        return self.browse_ref(xid).write(values)

    def get_ref_value(self, model, xid):
        if not hasattr(self, 'Z0bugOdoo'):
            self.Z0bugOdoo = Z0bugOdoo()
        return self.Z0bugOdoo.get_test_values(model, xid)

    def build_model_data(self, model, xrefs):
        if not isinstance(xrefs, (list, tuple)):
            xrefs = [xrefs]
        for xid in xrefs:
            vals = self.get_ref_value(model, xid)
            if not vals:
                pass
            elif 'id' in vals:
                xids = xid.split('.')
                ids = self.search612('ir.model.data',
                                     [('module', '=', xids[0]),
                                      ('name', '=', xids[1])])
                del vals['id']
                if ids:
                    id = ids[0]
                    self.write_rec(model, id, vals)
                else:
                    id = self.create_id(model, vals)
                    vals = {
                        'module': xid[0],
                        'model': model,
                        'name': xid[1],
                        'res_id': id,
                    }
                    self.create_rec('ir.model.data', vals)
            else:
                raise KeyError('Invalid xid %s for model %s!' % (xid, model))
