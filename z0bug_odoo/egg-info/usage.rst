Code example:
::

    # -*- coding: utf-8 -*-
    #
    # Copyright 2017-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
    #
    # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
    #
    from z0bug_odoo import test_common

    class ExampleTest(test_common.SingleTransactionCase):

        def setUp(self):
            super(ExampleTest, self).setUp()
            self.set_test_company()
            # Assure 2 res.partner records
            self.build_model_data('res.partner', ['base.res_partner_2',
                                                  'z0bug.res_partner_2'])

        def test_example(self):
            partner = self.browse_ref(self.ref612('base.res_partner_2'))
            partner = self.browse_ref(self.ref612('z0bug.res_partner_2'))




Following function are avaiable.

`set_test_company(self)`

Create or update company to test and assign it to current user as default company. This function should be put in setUp().


`create_id(model, values)`

Create a record of the model and return id (like Odoo 7.0- API).


`create_rec(model, values)`

Create a record of the model and return record itself (like Odoo 8.0+ API).


`write_rec(model, id, values)`

Write the record of model with passed id and return record itself.


`browse_rec(model, id)`

Return the record of model with passed id.


`env612(model)`

Return env/pool of model (like pool of Odoo 7.0- API or env of Odoo 8.0+ API)


`ref_value(model, xid)`

Return values of specific xid. If xid is Odoo standard xid, i.e. "base.res_partner_1",
return current record values that may be different from original demo data.
If xid begins with "z0bug." return default values even if they are update form previous tests.
See valid xid from this document.


`build_model_data(model, xrefs)`

Assure records of model with reference list xrefs.
For every item of xrefs, a record is created o updated.
Function ref_value is used to retrieve values of each record (see above).


::

    # -*- coding: utf-8 -*-
    #
    # Copyright 2017-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
    #
    # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
    #
    from zerobug import Z0testOdoo

    class ExampleTest():

        def test_example(self):
            res = Z0bugOdoo().get_test_values(
                'res.partner','z0bug.res_partner_1')


`get_test_values(self, model, xid)`

Return values of specific xid. If xid is Odoo standard xid, i.e. "base.res_partner_1",
return empty dictionary.
If xid begins with "z0bug." return default values to use in test.
This function is used by `ref_value` to get default values.
Warning: returned values may contain some field of uninstalled module.


`get_data_file(self, model, csv_fn)`

Load data of model from csv_fn. Internal use only.
