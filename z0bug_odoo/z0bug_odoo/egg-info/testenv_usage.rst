You can locate the recent testenv.py in testenv directory of module
`z0bug_odoo <https://github.com/zeroincombenze/tools/tree/master/z0bug_odoo/testenv>`__

For full documentation visit:
`zero-tools <https://zeroincombenze-tools.readthedocs.io/en/latest/pypi_z0bug_odoo/index.html>`__
or
`z0bug_odoo <https://z0bug-odoo.readthedocs.io/en/latest/>`__
or
`zero-tools (github) <https://github.com/zeroincombenze/tools>`__
or
`github with example modules <https://github.com/zeroincombenze/zerobug-test>`__

Copy the testenv.py file in tests directory of your module.
Please copy the documentation testenv.rst file in your module too.

The __init__.py must import testenv.

::

    from . import testenv
    from . import test_<MY_TEST_FILE>

Your python test file have to contain some following example lines:

::

    import os
    import logging
    from .testenv import MainTest as SingleTransactionCase

    _logger = logging.getLogger(__name__)

    TEST_SETUP_LIST = ["res.partner", ]

    class MyTest(SingleTransactionCase):

        def setUp(self):
            super().setUp()
            # Add following statement just for get debug information
            self.debug_level = 2
            # keep data after tests
            self.odoo_commit_data = True
            self.setup_env()                # Create test environment

        def tearDown(self):
            super().tearDown()

        def test_mytest(self):
            _logger.info(
                "🎺 Testing test_mytest"    # Use unicode char to best log reading
            )
            ...

An important helper to debug is self.debug_level. When you begins your test cycle,
you are hinted to set self.debug_level = 3; then you can decrease the debug level
when you are developing stable tests.
Final code should have self.debug_level = 0.
TestEnv logs debug message with symbol "🐞 " so you can easily recognize them.
Another useful helper is the database keep data after test feature. You have to declare
self.odoo_commit_data = True and you have to set global bash environment

``global ODOO_COMMIT_DATA="1"``

Ths TestEnv software requires:

* python_plus PYPI package
* z0bug_odoo PYPI package version {{branch}}
* python 2.7 / 3.6 / 3.7 / 3.8 / 3.9 / 3.10
