.. toctree::
   :maxdepth: 2

ChangeLog History
=================


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
~~~~~~~~~~~~~~~~~~~

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

|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.14/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.14/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
   :target: https://www.zeroincombenze.it/
   :alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png
.. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png
.. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png
.. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png
.. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png
.. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png
.. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png
.. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png
.. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png
.. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png
.. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
.. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
.. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
.. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif
   :target: https://t.me/Assitenza_clienti_powERP
