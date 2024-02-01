2.0.14 (2015-01-31)
~~~~~~~~~~~~~~~~~~~

* [IMP] build_cmd: enable coverage on sub process
* [FIX] Re-enable coverage statistics
* [FIX] Printing message: right sequence

2.0.13 (2023-12-21)
~~~~~~~~~~~~~~~~~~~

* [FIX] python2: argument signature
* [IMP] build_os_tree: compatible with unittest2
* [IMP] remove_os_tree: compatible with unittest2

2.0.12 (2023-11-27)
~~~~~~~~~~~~~~~~~~~

[FIX] python2: has_args

2.0.11 (2023-11-19)
~~~~~~~~~~~~~~~~~~~

* [IMP] Disabled sanity_check
* [IMP] Disabled some deprecated switches
* [FIX] Coverage data file
* [IMP] zerobug: test function signature like unittest2
* [IMP] zerobug: no more execution for count

2.0.10 (2023-11-10)
~~~~~~~~~~~~~~~~~~~~

* [REF] Partial refactoring
* [IMP] New functions assert* like unittest2
* [IMP] New switch -f failfast
* [IMP] Test signature like unittest2 and old zerobug signature
* [IMP] Test flow without return status (like unitest2)

2.0.9 (2023-07-12)
~~~~~~~~~~~~~~~~~~

* [IMP] zerobug implementation with unittest
* [FIX] z0testlib.py: build_odoo_env, odoo-bin / openerp-server are executable
* [FIX] z0testlib.py: minor fixes

2.0.7 (2023-05-14)
~~~~~~~~~~~~~~~~~~

* [IMP] travis_run_pypi_tests: new switch -p PATTERN

2.0.6 (2023-05-08)
~~~~~~~~~~~~~~~~~~

* [IMP] Now all_tests is ignored
* [IMP] Build Odoo environment for Odoo 16.0

2.0.5 (2023-03-24)
~~~~~~~~~~~~~~~~~~

* [FIX] travis_install_env: ensure list_requirements is executable
* [IMP] flake8 configuration
* [IMP] coveralls and codecov are not more dependencies
* [IMP] Test for Odoo 16.0

2.0.4 (2022-12-08)
~~~~~~~~~~~~~~~~~~

* [FIX] run_pypi_test: best recognition of python version
* [FIX] build_cmd: best recognition of python version
* [FIX] travis_install_env: ensure coverage version
* [IMP] odoo environment to test more precise

2.0.3 (2022-11-08)
~~~~~~~~~~~~~~~~~~

* [IMP] npm management

2.0.2.1 (2022-10-31)
~~~~~~~~~~~~~~~~~~~~

* [FIX] Odoo 11.0+
* [FIX] Ensure coverage 5.0+

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version

2.0.1.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~~~

* [IMP] minor improvements

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.2 (2022-10-05)
~~~~~~~~~~~~~~~~~~~~

* [IMP] travis_install_env: python2 tests

2.0.0.1 (2022-09-06)
~~~~~~~~~~~~~~~~~~~~

* [FIX] travis_install_env: minor fixes
* [IMP] z0testlib: show coverage result


2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [REF] Partial refactoring for shell scripts
