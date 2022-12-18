Copy the testenv.py file in tests directory of your module.
You can locate testenv.py in testenv directory of this module (z0bug_odoo)
Please copy the documentation testenv.rst file in your module too.
The __init__.py must import testenv.
Your python test file have to contain some following example lines:

::

    import os
    import logging
    from .testenv import MainTest as SingleTransactionCase

    _logger = logging.getLogger(__name__)

    TEST_RES_PARTNER = {...}
    TEST_SETUP_LIST = ["res.partner", ]

    class MyTest(SingleTransactionCase):

        def setUp(self):
            super().setUp()
            # Add following statement just for get debug information
            self.debug_level = 2
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            self.declare_all_data(data)     # TestEnv swallows the data
            self.setup_env()                # Create test environment

        def tearDown(self):
            super().tearDown()
            if os.environ.get("ODOO_COMMIT_TEST", ""):
                # Save test environment, so it is available to dump
                self.env.cr.commit()     # pylint: disable=invalid-commit
                _logger.info("✨ Test data committed")

        def test_mytest(self):
            _logger.info(
                "🎺 Testing test_mytest"    # Use unicode char to best log reading
            )
            ...

        def test_mywizard(self):
            self.wizard(...)                # Test requires wizard simulator

An important helper to debug is self.debug_level. When you begins your test cycle,
you are hinted to set self.debug_level = 3; then you can decrease the debug level
when you are developing stable tests.
Final code should have self.debug_level = 0.
TestEnv logs debug message with symbol "🐞 " so you can easily recognize them.

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
    # Copyright 2017-23 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
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
