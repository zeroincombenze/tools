=============
zerobug 2.0.9
=============



|Maturity| |license gpl|



Overview
========

This library can run unit test of target package software.
Supported languages are *python* (through z0testlib.py) and *bash* (through z0testrc)

*zerobug* supports test automation, aggregation of tests into collections
and independence of the tests from the reporting framework.
The *zerobug* module provides all code that make it easy to support testing
both for python programs both for bash scripts.
*zerobug* shows execution test with a message like "n/tot message"
where *n* is current unit test and *tot* is the total unit test to execute,
that is a sort of advancing test progress.

You can use z0bug_odoo that is the odoo integration to test Odoo modules.

*zerobug* is built on follow concepts:

* test main - it is a main program to executes all test runners
* test runner - it is a program to executes one or more test suites
* test suite - it is a collection of test cases
* test case - it is a smallest unit test

The main file is the command **zerobug** of this package; it searches for test runner files
named `[id_]test_` where 'id' is the shor name of testing package.

Test suite is a collection of test case named `test_[0-9]+` inside the runner file,
executed in sorted order.

Every suit can contains one or more test case, the smallest unit test;
every unit test terminates with success or with failure.

Because **zerobug** can show total number of unit test to execute, it runs tests
in 2 passes. In the first pass it counts the number of test, in second pass executes really
it. This behavior can be overridden by -0 switch.



Features
--------

* Test execution log
* Autodiscovery test modules and functions
* Python 2.7+ and 3.5+
* coverage integration
* travis integration



Usage
=====

::

    usage: zerobug [-h] [-B] [-C] [-e] [-J] [-k] [-l file] [-N] [-n] [-O]
                   [-p file_list] [-q] [-r number] [-s number] [-V] [-v] [-x] [-X]
                   [-z number] [-0] [-1] [-3]

    Regression test on z0bug_odoo

    optional arguments:
      -h, --help            show this help message and exit
      -B, --debug           trace msgs in zerobug.tracehis
      -C, --no-coverage     run tests without coverage
      -e, --echo            enable echoing even if not interactive tty
      -J                    load travisrc
      -k, --keep            keep current logfile
      -l file, --logname file
                            set logfile name
      -N, --new             create new logfile
      -n, --dry-run         count and display # unit tests
      -O                    load odoorc
      -p file_list, --search-pattern file_list
                            test file pattern
      -q, --quiet           run tests without output (quiet mode)
      -r number, --restart number
                            set to counted tests, 1st one next to this
      -s number, --start number
                            deprecated
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -x, --qsanity         like -X but run silently
      -X, --esanity         execute test library sanity check and exit
      -z number, --end number
                            display total # tests when execute them
      -0, --no-count        no count # unit tests
      -1, --coverage        run tests for coverage (obsolete)
      -3, --python3         use python3



Getting started
===============


Prerequisites
-------------

Zeroincombenze tools requires:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20/22
* python 2.7+, some tools require python 3.6+, best python 3.8+
* bash 5.0+



Installation
------------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install zerobug

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    [[ ! -d ./tools ]] && git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



Upgrade
-------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install --upgrade zerobug


Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

2.0.9.1 (2023-09-08)
~~~~~~~~~~~~~~~~~~~~

* [REF] Partial refactoring
* [IMP] New functions: assertEqual, assertTrue and assertFalse

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



Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Authors
-------

* `SHS-AV s.r.l. <https://www.zeroincombenze.it>`__



Contributors
------------

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
* Antonio Maria Vigliotti <info@shs-av.com>
* | <False>
* This module is part of tools project. <False>
* Last Update / Ultimo aggiornamento: 2023-08-14 <False>
* .. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png <False>
* :target: https://odoo-community.org/page/development-status <False>
* :alt: <False>
* .. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg <False>
* :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html <False>
* :alt: License: AGPL-3 <False>
* .. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg <False>
* :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html <False>
* :alt: License: OPL <False>
* .. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg <False>
* :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.9/dev <False>
* :alt: Technical Documentation <False>
* .. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg <False>
* :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.9/man <False>
* :alt: Technical Documentation <False>
* .. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg <False>
* :target: https://erp2.zeroincombenze.it <False>
* :alt: Try Me <False>
* .. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4 <False>
* :target: https://www.zeroincombenze.it/ <False>
* :alt: Zeroincombenze <False>
* .. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png <False>
* :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/ <False>
* .. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png <False>
* .. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png <False>
* .. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png <False>
* .. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png <False>
* .. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png <False>
* .. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png <False>
* .. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png <False>
* .. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png <False>
* .. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png <False>
* .. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png <False>
* .. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md <False>
* .. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md <False>
* .. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png <False>
* :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md <False>
* .. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif <False>
* :target: https://t.me/Assitenza_clienti_powERP <False>


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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.9/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.9/man
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
