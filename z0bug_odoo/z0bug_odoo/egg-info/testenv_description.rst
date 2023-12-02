TestEnv makes available a test environment ready to use in order to test your Odoo
module in quick and easy way.

The purpose of this software are:

* Create the Odoo test environment with records to use for your test
* Make available some useful functions to test your module (in z0bug_odoo)
* Simulate the wizard to test wizard functions (wizard simulator)
* Environment running different Odoo modules versions

Please, pay attention to test data: TestEnv use internal unicode even for python 2
based Odoo (i.e. 10.0). You should declare unicode date whenever is possible.

.. note::

    Odoo core uses unicode even on old Odoo version.

Tests are based on test environment created by module mk_test_env in
`repository <https://github.com/zeroincombenze/zerobug-test>`__