# -*- coding: utf-8 -*-
# Copyright (C) 2018-2019 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

try:
    import odoo.release as release
except ImportError:
    import openerp.release as release
if int(release.major_version.split('.')[0]) < 10:
    import openerp.tests.common as test_common
    from openerp import workflow
    from openerp.modules.module import get_module_resource
else:
    import odoo.tests.common as test_common
    from odoo.modules.module import get_module_resource


__version__='0.1.0.1'

class SingleTransactionCase(test_common.SingleTransactionCase):

    def pool(self, model):
        """Return model pool"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model)
        return self.env[model]

    def create_id(self, model, values):
        """Create a new record for test"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.pool(model).create(self.cr,
                                           self.uid,
                                           values)
        return self.pool(model).create(values).id

    def create_rec(self, model, values):
        """Create a new record for test"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.pool(model).browse(self.cr,
                                           self.uid,
                                           self.pool(model).reate(self.cr,
                                                                  self.uid,
                                                                  values))
        return self.pool(model).create(values)

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

    def ref612(self, model):
        """Return reference id"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.ref(model)
        return self.env.ref(model).id

    def search612(self, model, *args):
        """Search record ids - Syntax search(model, *args)
        Warning! Do not use with Odoo 7.0: result may fails!"""
        return self.registry(model).search(self.cr, self.uid, *args)

    def write_ref(self, xid, values):
        """Browse and write existent record"""
        return self.browse_ref(xid).write(values)
