Module test execution workflow should be:

    #. Data declaration, in file .csv or .xlszìx or in source code
    #. Base data creation, in setUp() function
    #. Tests execution
    #. Supplemental data creation, during test execution, by group name

Test data may be managed by one or more data group; if not declared,
"base" group name is used. The "base" group will be created at the setUp()
level: it is the base test data.
Testing function may declare and manage other group data. Look at the
following example:

::

    import os
    import logging
    from .testenv import MainTest as SingleTransactionCase

    _logger = logging.getLogger(__name__)

    TEST_PRODUCT_TEMPLATE = {
        "z0bug.product_template_1": {...}
    }
    TEST_RES_PARTNER = {
        "z0bug.partner1": {...}
    )
    TEST_SETUP_LIST = ["res.partner", "product.template"]

    TEST_SALE_ORDER = {
        "z0bug.order_1": {
            "partner_id": "z0bug.partner1",
            ...
        }
    }
    TEST_SALE_ORDER_LINE = {
        "z0bug.order_1_1": {
            "product_id": "z0bug.product_product_1",
            ...
        }
    )

    class MyTest(SingleTransactionCase):

        def setUp(self):
            super().setUp()
            self.debug_level = 2
            self.setup_env()                # Create base test environment

        def test_something(self):
            # Now add Sale Order data, group "order"
            self.setup_env(group="order", setup_list=["sale.order", "sale.order.line"])

Note the external reference are globals and they are visible from any groups.
After base data is created, the real test session can begin. You can simulate
various situation; the most common are:

    #. Simulate web form create record
    #. Simulate web form update record
    #. Simulate the multi-record windows action
    #. Download any binary data created by test
    #. Engage wizard

.. note::

    You can also create / update record with usually create() / write() Odoo function,
    but they do not really simulate the user behavior because they do not engage the
    onchange methods, they do not load any view and so on.

The real best way to test a create record is like the follow example
based on **res.partner model**:

::

        partner = self.resource_edit(
            resource="res.partner",
            web_changes=[
                ("name", "Adam"),
                ("country_id", "base.us"),
                ...
            ],
        )

You can also simulate the update session, issuing the record:

::

        partner = self.resource_edit(
            resource=partner,
            web_changes=[
                ("name", "Adam Prime"),
                ...
            ],
        )

Look at resource_edit() documentation for furthermore details.

In you test session you should need to test a wizard. This test is very easy
to execute as in the follow example that engage the standard language install
wizard:

::

        # We engage language translation wizard with "it_IT" language
        # see "<ODOO_PATH>/addons/base/module/wizard/base_language_install*"
        _logger.info("🎺 Testing wizard.lang_install()")
        act_windows = self.wizard(
            module="base",
            action_name="action_view_base_language_install",
            default={
                "lang": "it_IT"
                "overwrite": False,
            },
            button_name="lang_install",
        )
        self.assertTrue(
            self.is_action(act_windows),
            "No action returned by language install"
        )
        # Now we test the close message
        self.wizard(
            act_windows=act_windows
        )
        self.assertTrue(
            self.env["res.lang"].search([("code", "=", "it_IT")]),
            "No language %s loaded!" % "it_IT"
        )

Look at wizard() documentation for furthermore details.
