
=================
z0bug_odoo 1.0.15
=================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Zeroincombenze® continuous testing for odoo
-------------------------------------------

This package is an plug-in of **zerobug** package and aim to easily create odoo tests.

It replaces OCA MQT with some nice additional features.

*z0bug_odoo* is built on follow concepts:

* Odoo version independent; it can test Odoo from 6.1 until 13.0
* It is designed to run in local environment too, using `local travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_
* It can run with full or reduced set of pylint tests
* Test using ready-made database records
* Quality Check Id


travis ci support
-----------------

The goal of z0bug_odoo is to provide helpers to ensure the quality of Odoo addons.
The code was forked from OCA MQT but some improvements were added.
This package and OCA MQT differ by:

* z0bug_odoo can also test Odoo 6.1 and 7.0 where OCA MQT fails with these versions
* z0bug_odoo is designed to execute some debug statements, mainly in local environment
* z0bug_odoo has more options to run with reduced set of lint tests
* OCA MQT is the only component to build environment and test Odoo while z0bug_odoo is part of `Zeroincombenze® tools <https://github.com/zeroincombenze/tools>`_
* As per prior rule, building test environment is made by `vem <https://github.com/zeroincombenze/tools/tree/master/https://github.com/zeroincombenze/tools/tree/master/python_plus>`_, `clodoo <https://github.com/zeroincombenze/tools/tree/master/https://github.com/zeroincombenze/tools/tree/master/clodoo>`_ and `lisa <https://github.com/zeroincombenze/tools/tree/master/https://github.com/zeroincombenze/tools/tree/master/lisa>`_. These commands can also build a complete Odoo environment out of the box

To make a complete test on TravisCI your project following 3 files are required:

* .travis.yml
* requirements.txt
* oca_dependencies.txt


File .travis.yml
~~~~~~~~~~~~~~~~

In order to setup TravisCI continuous integration for your project, just copy the
content of the `sample_files <https://github.com/zeroincombenze/tools/tree/master/zerobug/sample_files/.travis.yml>`_
to your project’s root directory.

Then execute the command:

::

    topep8 -b<odoo_version> .travis.yml

You can check travis syntax with the `lint checker <http://lint.travis-ci.org/>`_ of travis, if available.


Odoo test integration
~~~~~~~~~~~~~~~~~~~~~

Current Odoo project version is declared by **VERSION** variable.
If your Odoo module must be tested against Odoo core,
you can test specific github repository by **ODOO_REPO** variable.
You can test against:

* odoo/odoo
* OCA/OCB
* zeroincombenze/OCB

You can test against specific Odoo core version with ODOO_BRANCH variable if differs from your project version:

::

    # Odoo Branch 10.0
    - VERSION="10.0" ODOO_REPO="odoo/odoo"

    # Pull request odoo/odoo#143
    -  VERSION="pull/143" ODOO_REPO="OCA/OCB"

    # Branch saas-17
    - ODOO_REPO="odoo/odoo" ODOO_BRANCH="saas-17"


OCB / core test
~~~~~~~~~~~~~~~

Zeroincombenze® OCB uses submodules. When test is starting, travis-ci upgrades repository and submodules.
To avoid submodules upgrade use this directive compatible with OCA MQT:

::

    - git:
      submodules: false

z0bg_odoo set security environment. You do not need to add any security statements.
You can avoid the following OCA MQT directive:

::

    - pip install urllib3[secure] --upgrade; true

z0bg_odoo does some code upgrade.
You can avoid following directive in ODOO_TEST_SELECT="APPLICATIONS":

::

    - sed -i "s/self.url_open(url)/self.url_open(url, timeout=100)/g" ${TRAVIS_BUILD_DIR}/addons/website/tests/test_crawl.py;

You can avoid following directive in ODOO_TEST_SELECT="LOCALIZATION":

::

    - sed -i "/'_auto_install_l10n'/d" ${TRAVIS_BUILD_DIR}/addons/account/__manifest__.py


Python version
~~~~~~~~~~~~~~

Odoo version from 6.1 to 10.0 are tested with python 2.7
From Odoo 11.0, python3 is used. You can test against 3.5, 3.6 and 3.7 python versions.
Currently, python 3.8 is not yet supported.
This is the declaration:

::

    python:
      - "3.5"
      - "3.6"
      - "3.7"

Notice: python 3.5 support is ended on 2020 and 3,6 is ended on 2021.
Python 3.8 is no yet support by Odoo (2021), so use python 3.7


Deployment and setup environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to deploy test environment and setup code you have to declare some .travis.yml directives divides in following 3 parts:

* Linux packages needed
* PYPI packages
* Odoo repositories dependencies

Linux packages must be declared in `<addons/apt>` section of .travis.yml using Ubuntu namespace.
If you run test in local environment, travis emulator automatically translate Ubuntu names into your local distro names, if necessary.
See `travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_ guide for furthermore info.

The PYPI packages, installable by PIP are declared in standard PIP way, using **requirements.txt** file.

If your project depends on other Odoo Github repositories like OCA, create a file called **oca_dependencies.txt** at the root of your project and list the dependencies there.
One per line like so:

    project_name optional_repository_url optional_branch_name

During testbed setup, z0bug_odoo will automatically download and place these repositories accordingly into the addon path.
Note on addons path ordering: they will be placed after your own repo, but before the odoo core repo.

If missed optional_repository_url, the repository is searched for repository with the same owner of tested project.
Please note this behaviour differs from OCA MQT.
OCA MQT always loads OCA repository while z0bug_odoo searches for current owner repository.
So you will test both with z0bug_ood and both OCA MQT, always insert the full repository URL.

Test execution
~~~~~~~~~~~~~~

Tests run by travis_run_test command. The script is deployed in _travis directory of **zerobug** package.
Command have to be in `<script>` section of .travis.yml file:

::

    script:
        - travis_run_tests


Isolated pylint+flake8 checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to make a build for these checks, you can add a line
on the `<env>` section of the .travis.yml file with this content:

::

    - VERSION="12.0" LINT_CHECK="1"

To avoid making again these checks on other builds, you have to add
LINT_CHECK="0" variable on the line:

::

    - VERSION="12.0" ODOO_REPO="odoo/odoo" LINT_CHECK="0"

You can superset above options in local travis emulator.


Reduced set of lint check
~~~~~~~~~~~~~~~~~~~~~~~~~

You can execute reduced set of check, in order to gradually evolve your code quality
when you meet too many errors.

To enable reduced set of check add one of follow lines:

::

    - LINT_CHECK="1" LINT_CHECK_LEVEL="MINIMAL"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="REDUCED"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="AVERAGE"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="NEARBY"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="OCA"

Odoo core has internal pylint test that checks for all modules even the dependecies.
So if some dependecies module does not meet this test, then the full travis test fails without testing the target repository.

Please, add test_lint to EXCLUDE variable to avoid this fail-over. See below for furthermore informations.

Look at follow table to understand which tests are disabled at specific level:

FLAKE8 (see http://flake8.pycqa.org/en/latest/user/error-codes.html for deatils)

+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| Test | MINIMAL    | REDUCED    | AVERAGE | NEARBY | OCA        | Note                                                                                                                             |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E117 | |no_check| | |no_check| |         |        | |no_check| | over-indented                                                                                                                    |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E121 | |no_check| | |no_check| |         |        | |no_check| | `continuation line under-indented for hanging indent <https://lintlyci.github.io/Flake8Rules/rules/E121.html>`_                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E123 | |no_check| | |no_check| |         |        | |no_check| | `Closing bracket does not match indentation of opening bracket's line <https://lintlyci.github.io/Flake8Rules/rules/E123.html>`_ |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E124 | |no_check| | |no_check| |         |        | |check|    | `Closing bracket does not match visual indentation <https://lintlyci.github.io/Flake8Rules/rules/E124.html>`_                    |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E126 | |no_check| | |no_check| |         |        | |check|    | `Continuation line over-indented for hanging indent <https://lintlyci.github.io/Flake8Rules/rules/E126.html>`_                   |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E127 | |no_check| | |no_check| |         |        | |check|    | `continuation line over-indented for visual indent <https://lintlyci.github.io/Flake8Rules/rules/E127.html>`_                    |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E128 | |no_check| | |no_check| |         |        | |check|    | `Continuation line under-indented for visual indent <https://lintlyci.github.io/Flake8Rules/rules/E128.html>`_                   |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E131 | |no_check| | |no_check| |         |        | |no_check| | `continuation line unaligned for hanging indent <https://lintlyci.github.io/Flake8Rules/rules/E131.html>`_                       |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E133 | |no_check| | |no_check| |         |        | |no_check| | `Closing bracket is missing indentation <https://lintlyci.github.io/Flake8Rules/rules/E133.html>`_                               |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E201 | |no_check| | |check|    |         |        | |check|    | `Whitespace after '(' <https://lintlyci.github.io/Flake8Rules/rules/E201.html>`_                                                 |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E202 | |no_check| | |check|    |         |        | |check|    | `Whitespace before ')' <https://lintlyci.github.io/Flake8Rules/rules/E202.html>`_                                                |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E203 | |no_check| | |check|    |         |        | |check|    | `Whitespace before ':' <https://lintlyci.github.io/Flake8Rules/rules/E203.html>`_                                                |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E211 | |no_check| | |check|    |         |        | |check|    | `whitespace before '(' <https://lintlyci.github.io/Flake8Rules/rules/E211.html>`_                                                |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E221 | |no_check| | |check|    |         |        | |check|    | `Multiple spaces before operator <https://lintlyci.github.io/Flake8Rules/rules/E221.html>`_                                      |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E222 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E225 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E226 | |no_check| | |no_check| |         |        | |no_check| |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E231 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E241 | |no_check| | |no_check| |         |        | |no_check| |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E242 | |no_check| | |no_check| |         |        | |no_check| |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E251 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E261 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E262 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E265 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E266 | |no_check| | |no_check| |         |        | |check|    | `too many leading '#' for block comment <https://lintlyci.github.io/Flake8Rules/rules/E266.html>`_                               |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E271 | |no_check| | |no_check| |         |        | |check|    | `multiple spaces after keyword <https://lintlyci.github.io/Flake8Rules/rules/E271.html>`_                                        |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E272 | |no_check| | |no_check| |         |        | |check|    | `multiple spaces before keyword <https://lintlyci.github.io/Flake8Rules/rules/E272.html>`_                                       |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| W291 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| W292 | |no_check| | |no_check| |         |        | |check|    | `no newline at end of file <https://lintlyci.github.io/Flake8Rules/rules/W292.html>`_                                            |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| W293 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E301 | |no_check| | |no_check| |         |        | |check|    | `Expected 1 blank line <https://lintlyci.github.io/Flake8Rules/rules/E301.html>`_                                                |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E302 | |no_check| | |no_check| |         |        | |check|    | No __init__.py                                                                                                                   |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E303 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E305 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| W391 | |no_check| | |no_check| |         |        | |check|    | blank line at end of file                                                                                                        |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| F401 | |no_check| | |check|    |         |        | |no_check| | module imported but unused                                                                                                       |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E501 | |no_check| | |no_check| |         |        | |check|    |                                                                                                                                  |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E502 | |no_check| | |no_check| |         |        | |check|    | `the backslash is redundant between brackets <https://lintlyci.github.io/Flake8Rules/rules/E502.html>`_                          |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| W503 | |no_check| | |no_check| |         |        | |no_check| | No __init__.py                                                                                                                   |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| W504 | |no_check| | |no_check| |         |        | |no_check| | No __init__.py                                                                                                                   |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| F601 | |no_check| | |no_check| |         |        | |no_check| | dictionary key name repeated with different values                                                                               |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E701 | |no_check| | |no_check| |         |        | |check|    | multiple statements on one line (colon)                                                                                          |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| E722 | |no_check| | |no_check| |         |        | |check|    | do not use bare except                                                                                                           |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| F811 | |no_check| | |no_check| |         |        | |no_check| | redefinition of unused name from line N (No __init__.py)                                                                         |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+
| F841 | |no_check| | |no_check| |         |        | |no_check| | `local variable 'context' is assigned to but never used <https://lintlyci.github.io/Flake8Rules/rules/F841.html>`_               |
+------+------------+------------+---------+--------+------------+----------------------------------------------------------------------------------------------------------------------------------+




PYLINT (see http://pylint-messages.wikidot.com/all-codes for details)

+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| Test  | MINIMAL    | REDUCED    | AVERAGE | NEARBY | OCA     | Notes                                                                               |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W0101 | |no_check| | |no_check| |         |        | |check| | `unreachable <http://pylint-messages.wikidot.com/messages:w0101>`_                  |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W0312 | |no_check| | |check|    |         |        | |check| | `wrong-tabs-instead-of-spaces <http://pylint-messages.wikidot.com/messages:w0312>`_ |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W0403 | |no_check| | |no_check| |         |        | |check| | relative-import                                                                     |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W1401 | |no_check| | |check|    |         |        | |check| | anomalous-backslash-in-string                                                       |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| E7901 | |no_check| | |no_check| |         |        | |check| | `rst-syntax-error <https://pypi.org/project/pylint-odoo/1.4.0>`_                    |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C7902 | |no_check| | |check|    |         |        | |check| | missing-readme                                                                      |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7903 | |no_check| | |no_check| |         |        | |check| | javascript-lint                                                                     |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7908 | |no_check| | |no_check| |         |        | |check| | missing-newline-extrafiles                                                          |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7909 | |no_check| | |no_check| |         |        | |check| | redundant-modulename-xml                                                            |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7910 | |no_check| | |check|    |         |        | |check| | wrong-tabs-instead-of-spaces                                                        |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7930 | |no_check| | |no_check| |         |        | |check| | `file-not-used <https://pypi.org/project/pylint-odoo/1.4.0>`_                       |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7935 | |no_check| | |no_check| |         |        | |check| | missing-import-error                                                                |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7940 | |no_check| | |no_check| |         |        | |check| | dangerous-view-replace-wo-priority                                                  |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7950 | |no_check| | |no_check| |         |        | |check| | odoo-addons-relative-import                                                         |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| E8102 | |no_check| | |check|    |         |        | |check| | invalid-commit                                                                      |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8103 | |no_check| | |check|    |         |        | |check| | `manifest-deprecated-key <https://pypi.org/project/pylint-odoo/1.4.0>`_             |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W8103 | |no_check| | |no_check| |         |        | |check| | translation-field                                                                   |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8104 | |no_check| | |no_check| |         |        | |check| | `class-camelcase <https://pypi.org/project/pylint-odoo/1.4.0>`_                     |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W8104 | |no_check| | |no_check| |         |        | |check| | api-one-deprecated                                                                  |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8105 | |no_check| | |check|    |         |        | |check| | `license-allowed <https://pypi.org/project/pylint-odoo/1.4.0>`_                     |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8108 | |no_check| | |no_check| |         |        | |check| | method-compute                                                                      |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| R8110 | |no_check| | |check|    |         |        | |check| | old-api7-method-defined                                                             |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W8202 | |no_check| | |check|    |         |        | |check| | use-vim-comment                                                                     |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |check|    |         |        | |check| | sql-injection                                                                       |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |check|    |         |        | |check| | duplicate-id-csv                                                                    |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |no_check| |         |        | |check| | create-user-wo-reset-password                                                       |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |no_check| |         |        | |check| | dangerous-view-replace-wo-priority                                                  |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |no_check| |         |        | |check| | translation-required                                                                |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |check|    |         |        | |check| | duplicate-xml-record-id                                                             |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |no_check| |         |        | |check| | no-utf8-coding-comment                                                              |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |check|    |         |        | |check| | attribute-deprecated                                                                |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| | |no_check| |         |        | |check| | consider-merging-classes-inherited                                                  |
+-------+------------+------------+---------+--------+---------+-------------------------------------------------------------------------------------+




Disable some pylint and/or flake8 checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can disable some specific test or some file from lint checks.

To disable flake8 checks on specific file you can add following line at the beginning of python file:

::

    # flake8: noqa

To disable pylint checks on specific file you can add following line at the beginning of python file:

::

    # pylint: skip-file

To disable both flake8 and pylint checks on specific file you can add following line at the beginning of python file:

::

    # flake8: noqa - pylint: skip-file

To disable pylint checks on specific XML file you can add following line in XML file after xml declaration:

::

    <!-- pylint:disable=deprecated-data-xml-node -->

You can disable specific flake8 check in some source part of python file adding a comment at the same statement to disable check. Here an example to disable sql error (notice comment must be at beginning of the statement):

::

    from builtins import *  # noqa: F403

If you have to disable more than one error you can add following declaration:

::

    from builtins import *  # noqa

You can also disable specific pylint check in some source part of python file adding a comment at the same statement to disable check. Here an example to disable sql error (notice comment must be at beginning of the statement):

::

    self._cr.execute()      # pylint: disable=E8103


Disable unit test
~~~~~~~~~~~~~~~~~

If you want to make a build without tests, you can use the following directive:
`TEST_ENABLE="0"`

You will simply get the databases with packages installed,
but without running any tests.


Reduced set of unit test
~~~~~~~~~~~~~~~~~~~~~~~~

Odoo modules may fail in Travis CI or in local environment.
Currently Odoo OCB core tests fail; we are investigating for the causes.
However you can use a simple workaround, disabling some test.
Currently tests fail are:

* test_impex
* test_ir_actions
* test_lint
* test_main_flows
* test_search
* test_user_has_group

Example:

::

    - export EXCLUDE=test_impex,test_ir_actions,test_lint,test_main_flows,test_search,test_user_has_group
    - TESTS="1" ODOO_TEST_SELECT="ALL"
    - TESTS="1" ODOO_TEST_SELECT="NO-CORE"
    - ....

You can set parameter local GBL_EXCLUDE to disable these test for all repositories.
You will be warned that local GBL_EXCLUDE has only effect for local emulation.
To avoid these test on web travis-ci you have to set EXCLUDE value in .travis.yml file.

Look at follow table to understand which set of tests are enabled or disabled:

+-----------------+-------------+---------------+-------------+---------------------+
| statement       | application | module l10n_* | odoo/addons | addons + dependenci |
+-----------------+-------------+---------------+-------------+---------------------+
| ALL             | |check|     | |check|       | |check|     | |check|             |
+-----------------+-------------+---------------+-------------+---------------------+
| APPLICATIONS    | |check|     | |no_check|    | |no_check|  | Only if application |
+-----------------+-------------+---------------+-------------+---------------------+
| LOCALIZATION    | |no_check|  | |check|       | |no_check|  | Only module l10n_*  |
+-----------------+-------------+---------------+-------------+---------------------+
| CORE            | |no_check|  | |no_check|    | |check|     | |no_check|          |
+-----------------+-------------+---------------+-------------+---------------------+
| NO-APPLICATION  | |no_check|  | |check|       | |check|     | No if application   |
+-----------------+-------------+---------------+-------------+---------------------+
| NO-LOCALIZATION | |check|     | |no_check|    | |check|     | No if module l10n_* |
+-----------------+-------------+---------------+-------------+---------------------+
| NO-CORE         | |check|     | |check|       | |no_check|  | |check|             |
+-----------------+-------------+---------------+-------------+---------------------+




Dependencies test
~~~~~~~~~~~~~~~~~

Since late Summer 2021, z0bug_odoo checks for dependencies.
This test is a sub test of unit test. This is the directive:

::

    - TESTS="1" TEST_DEPENDENCIES="1"


Module unit tests
~~~~~~~~~~~~~~~~~

z0bug_odoo is also capable to test each module individually.
The intention is to check if all dependencies are correctly defined.
Activate it through the `UNIT_TEST` directive.
An additional line should be added to the `env:` section,
similar to this one:

::

    - VERSION="12.0" UNIT_TEST="1"


Automatic module translation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since late Summer 2021, z0bug_odoo activate automatic module translation after test ended with success.
This is the directive:

::

    - VERSION="12.0" ODOO_TNLBOT="1"

This feature is still experimental.


Names used for the test databases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

z0bug_odoo has a nice feature of organizing your testing databases.
You might want to do that if you want to double them up as
staging DBs or if you want to work with an advanced set of
templates in order to speed up your CI pipeline.
Just specify at will:

`MQT_TEMPLATE_DB='odoo_template' MQT_TEST_DB='odoo_test'`.

In your local travis you can declare the default value but these values are not applied in web TravisCi web site.

Database user is the current username. This behavior works both in local test both in TravisCi web site.
However, sometimes, local user and db username can be different. You can set the default value in travis emulator.


Coveralls/Codecov configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Coveralls <https://coveralls.io/>`_ and `Codecov <https://codecov.io/>`_ services provide information on the test coverage of your modules.
Currently both configurations are automatic (check default configuration `here <cfg/.coveragerc>`_.
So, as of today, you don't need to include a `.coveragerc` into the repository,
If you do it, it will be simply ignored.


Other configurations
~~~~~~~~~~~~~~~~~~~~

You can highly customize you test: look at below table.

+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| variable               | default value                                          | meaning                                                      |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| CHROME_TEST            |                                                        | Set value to 1 to use chrome client to test                  |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| DATA_DIR               | ~/data_dir                                             | Odoo data directory (data_dir in config file)                |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| EXCLUDE                |                                                        | Modules to exclude from test                                 |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| INCLUDE                |                                                        | Modules to test (all                                         |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| INSTALL_OPTIONS        |                                                        | Options passed to odoo-bin/openerp-server to install modules |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| MQT_DBSUER             | $USER                                                  | Database username                                            |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| MQT_TEMPLATE_DB        | openerp_template                                       | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| MQT_TEST_DB            | openerp_test                                           | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| NPM_CONFIG_PREFIX      | \$HOME/.npm-global                                     | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_REPO              | odoo/odoo                                              | OCB repository against test repository                       |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_SETUPS            | __manifest__.py __openerp__.py __odoo__.py __terp__.py | Names of Odoo manifest files                                 |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_TEST_SELECT       | ALL                                                    | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_TNLBOT            | 0                                                      | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| OPTIONS                |                                                        | Options passed to odoo-bin/openerp-server to execute tests   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PHANTOMJS_VERSION      |                                                        | Version of PhantomJS                                         |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_TXT_COLOR           | 0;97;40                                                | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_RUN_COLOR           | 1;37;44                                                | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_NOP_COLOR           | 34;107                                                 | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_HDR1_COLOR          | 97;42                                                  | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_HDR2_COLOR          | 30;43                                                  | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_HDR3_COLOR          | 30;45                                                  | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PYPI_RUN_PYVER         | (2.7|3.5|3.6|3.7|3.8)                                  | python versions to run (only PYPI projects)                  |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| SERVER_EXPECTED_ERRORS |                                                        | # of expected errors after tests                             |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| TEST_DEPENDENCIES      | 0                                                      | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| TRAVIS_DEBUG_MODE      | 0                                                      | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| TRAVIS_PDB             |                                                        | The value 'true' activates pdb in local 'travis -B'          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| UNBUFFER               | 1                                                      | Use unbuffer (colors) to log results                         |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| UNIT_TEST              |                                                        | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| TEST                   |                                                        | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| VERSION                |                                                        | Odoo version to test (see above)                             |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| WEBSITE_REPO           |                                                        | Load package for website tests                               |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| WKHTMLTOPDF_VERSION    | 0.12.5                                                 | Version of wkhtmltopdf (value are 0.12.1                     |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+





Debug information
~~~~~~~~~~~~~~~~~

If you declare the following directive in <env global> section:

`TRAVIS_DEBUG_MODE="n"`

where "n" means:

+------------------------+------------+------------+------------+---------+-------------+
| Parameter              | 0          | 1          | 2          | 3       | 9           |
+------------------------+------------+------------+------------+---------+-------------+
| Informative messages   | |no_check| | |check|    | |check|    | |check| | |check|     |
+------------------------+------------+------------+------------+---------+-------------+
| Inspect internal data  | |no_check| | |no_check| | |check|    | |check| | |check|     |
+------------------------+------------+------------+------------+---------+-------------+
| MQT tests              | |no_check| | |no_check| | |no_check| | |check| | |check|     |
+------------------------+------------+------------+------------+---------+-------------+
| Installation log level | ERROR      | WARN       | INFO       | INFO    | |no_check|  |
+------------------------+------------+------------+------------+---------+-------------+
| Execution log level    | INFO       | TEST       | TEST       | TEST    | |no_check|  |
+------------------------+------------+------------+------------+---------+-------------+



Note this feature does not work with OCA MQT. Local test and TravisCI test have slightly different behavior.

When MQT is execute in local environment the value

`TRAVIS_DEBUG_MODE="9"`

does not execute unit test. It is used to debug MQT itself.

See `local travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_


Tree directory
~~~~~~~~~~~~~~

While travis is running this is the tree directory:

::

    ${HOME}                         # home of virtual environment (by TravisCI)
    ┣━━ build                       # build root (by TravisCI)
    ┃    ┣━━ ${TRAVIS_BUILD_DIR}    # testing repository (by TravisCI)
    ┃    ┗━━ ${ODOO_REPO}           # odoo or OCB repository to check with       (0) (1) (2)
    ┃
    ┣━━ ${ODOO_REPO}-${VERSION}     # symlink of ${HOME}/build/{ODOO_REPO}       (0) (1)
    ┃
    ┣━━ dependencies                # Odoo dependencies of repository            (0) (3)
    ┃
    ┣━━ tools                       # clone of Zeroincombenze tools              (3) (4)
    ┃    ┃
    ┃    ┣━━ zerobug                # z0bug testing library
    ┃    ┃       ┗━━ _travis        # testing commands
    ┃    ┗━━ z0bug_odoo             # Odoo testing library
    ┃            ┗━━ travis         # testing commands
    ┃
    ┗━━ maintainer-quality-tools    # OCA testing library
         ┗━━ travis                 # testing commands

    (0) Same behavior of OCA MQT
    (1) Cloned odoo/odoo or OCA/OCB repository to check compatibility of testing modules
    (2) If the testing project is OCB, travis_install_env ignore this directory
    (3) Done by then following statements in .travis.yml:
        - travis_install_env
        Above statements replace the OCA statements:
        - travis_install_nightly
    (4) Done by following statements in .travis.yml::
        - git clone https://github.com/zeroincombenze/tools.git ${HOME}/tools --depth=1
        - \${HOME}/tools/install_tools.sh -qpt
        - source ${HOME}/devel/activate_tools -t
        Above statements replace OCA following statements:
        - git clone https://github.com/OCA/maintainer-quality-tools.git ${HOME}/maintainer-quality-tools --depth=1
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}

qci
---

+-------------+-----------------------------------------------------------------------------------+
| qci         | description                                                                       |
+-------------+-----------------------------------------------------------------------------------+
| acc.uRB     | Insoluto RiBA                                                                     |
+-------------+-----------------------------------------------------------------------------------+
| acc.VAT_rc  | Reverse Charge / Inversione contabile                                             |
+-------------+-----------------------------------------------------------------------------------+
| acc.VAT_sp  | Split Payment / Scissione pagamenti                                               |
+-------------+-----------------------------------------------------------------------------------+
| acc.VAT_wt  | Withholding tax / Ritenuta d’acconto                                              |
+-------------+-----------------------------------------------------------------------------------+
| acc.VATpu   | Undeductible VAT / IVA parzialmente indetraibile                                  |
+-------------+-----------------------------------------------------------------------------------+
| acc.VATu    | Full Undeductible VAT / IVA totalmente indetraibile                               |
+-------------+-----------------------------------------------------------------------------------+
| einvo.ind   | E-invoice to individual / Fattura elettronica a privato                           |
+-------------+-----------------------------------------------------------------------------------+
| einvo.stamp | E-invoice with virtual stamp / Fattura elettronica con bollo virtuale             |
+-------------+-----------------------------------------------------------------------------------+
| inv.asalem  | Corrispettivi misti                                                               |
+-------------+-----------------------------------------------------------------------------------+
| inv.asalex  | Corrispettivi ripartiti (ventilazione)                                            |
+-------------+-----------------------------------------------------------------------------------+
| inv.asset   | Invoice with asset/Fattura di beni strumentali                                    |
+-------------+-----------------------------------------------------------------------------------+
| invi.enas   | Purchase invoice with enasarco / Fattura da fornitore con ensarco                 |
+-------------+-----------------------------------------------------------------------------------+
| invi.eu     | Purchase invoice from EU partner / Fattura di acquisto intraUE                    |
+-------------+-----------------------------------------------------------------------------------+
| invi.rc     | Purchase invoice with reverse charge / Fattura di acquisto con reverse charge     |
+-------------+-----------------------------------------------------------------------------------+
| invi.sp     | Purchase invoice with split payment / Fattura di acquisto con split-payment       |
+-------------+-----------------------------------------------------------------------------------+
| invi.VAT_li | Purchase invoice with lettera di intento / Fattura di acquisto lettera di intento |
+-------------+-----------------------------------------------------------------------------------+
| invi.wht    | Purchase invoice with withholding / Fattura da fornitore con ritenuta d'acconto   |
+-------------+-----------------------------------------------------------------------------------+
| invi.xeu    | Purchase invoice fromxEU partner / Fattura di acquisto extraUE                    |
+-------------+-----------------------------------------------------------------------------------+
| invo.enas   | Sale invoice with enasarco / Fattura di vendita con ensarco                       |
+-------------+-----------------------------------------------------------------------------------+
| invo.eu     | Sale invoice to EU partner / Fattura di vendita intraUE                           |
+-------------+-----------------------------------------------------------------------------------+
| invo.li     | Sale invoice with lettera di intento / Fattura di vendita lettera di intento      |
+-------------+-----------------------------------------------------------------------------------+
| invo.long   | Sale invoice with 30+ lines (multipage-print)                                     |
+-------------+-----------------------------------------------------------------------------------+
| invo.N1     | Sale invoice with out of vat / Fattura di vendita con FC art. 15                  |
+-------------+-----------------------------------------------------------------------------------+
| invo.rc     | Sale invoice with reverse charge / Fattura di vendita con reverse charge          |
+-------------+-----------------------------------------------------------------------------------+
| invo.sp     | Sale invoice with split payment / Fattura di vendita con split-payment            |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat1   | Sale invoice with vat 4% / Fattura di vendita con IVA 4%                          |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat2   | Sale invoice with vat 10% / Fattura di vendita con IVA 10%                        |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat3   | Sale invoice with vat 22% / Fattura di vendita con IVA 22%                        |
+-------------+-----------------------------------------------------------------------------------+
| invo.wh     | Sale invoice with withholding / Fattura di vendita ritenuta d'acconto             |
+-------------+-----------------------------------------------------------------------------------+
| invo.xeu    | Sale invoice to xEU partner / Fattura di vendita extraUE                          |
+-------------+-----------------------------------------------------------------------------------+
| part.eu     | EU partner / Cliente intraUE                                                      |
+-------------+-----------------------------------------------------------------------------------+
| part.it     | Local partner (Italy) / Cliente italiano                                          |
+-------------+-----------------------------------------------------------------------------------+
| part.PA     | Partner is PA                                                                     |
+-------------+-----------------------------------------------------------------------------------+
| part.pt1    | Partner with one date payment / Cliente con pagamento in unica soluzione          |
+-------------+-----------------------------------------------------------------------------------+
| part.pt2    | Partner with multiple date payment / Cliente con pagamento di più scadenze        |
+-------------+-----------------------------------------------------------------------------------+
| part.xeu    | Extra-EU partner / Cliente extraUE                                                |
+-------------+-----------------------------------------------------------------------------------+
| pay.RB      | RiBA payment / Pagamento RiBA (IT)                                                |
+-------------+-----------------------------------------------------------------------------------+
| pay.SCT     | Credit Transfer payment / Pagamento bonifico                                      |
+-------------+-----------------------------------------------------------------------------------+
| pay.SDD     | Sepa Direct Debit / Pagamento Sepa DD                                             |
+-------------+-----------------------------------------------------------------------------------+




partner qci
-----------

+----------------------+------------------------------------+-------------------+----------------------------+
| id                   | name                               | side              | icq                        |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_1  | Prima Distribuzione S.p.A.         | customer/supplier | icq_0002 icq_0006 icq_pa11 |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_10 | Notaio Libero Jackson              | supplier          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_11 | Nebula Caffè S.p.A.                | supplier          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_12 | Freie Universität Berlin           | supplier          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_13 | Axelor GmbH                        | customer          | icq_pa12                   |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_14 | SS Carrefur                        | supplier          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_15 | Ente Porto                         | customer          | icq_0002 icq_pa14 icq_pa16 |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_16 | Viking Office Depot Italia s.r.l.  | customer/supplier |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_17 | Vexor BV                           | supplier          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_2  | Agro Latte Due  s.n.c.             | customer          | icq_0002 icq_0007          |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_3  | Import Export Trifoglio s.r.l.     | customer          | icq_0001 icq_0006          |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_4  | Delta 4 s.r.l.                     | supplier          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_5  | Five Stars Hotel                   | supplier          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_6  | Esa Electronic S.p.A               | customer          | icq_0003                   |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_7  | Università della Svizzera Italiana | customer          | icq_pa13                   |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_8  | Global Solution s.r.l.             | customer          | icq_pa15                   |
+----------------------+------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_9  | Mario Rossi                        | customer          |                            |
+----------------------+------------------------------------+-------------------+----------------------------+




|

Features
--------

Data to use in tests are store in csv files in data directory.
File names are tha name of the models (table) with characters '.' (dot) replaced by '_' (underscore)

Header of file must be the names of table fields.

Rows can contains value to store or Odoo external reference or macro.

For type char, text, html, int, float, monetary: value are constants inserted as is.

For type many2one: value may be an integer (record id) or Odoo external reference (format "module.name").

For type data, datetime: value may be a constant or relative date





|

Usage
=====

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


|
|

Getting started
===============


|

Installation
------------

For stable version:

`pip install z0bug_odoo`

For current version:

`cd $HOME`
`git@github.com:zeroincombenze/tools.git`
`cd $HOME/tools`
`./install_tools.sh`


Upgrade
-------

Upgrade
-------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install z0bug_odoo -U

|

Current stable version
~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -U
    source /opt/odoo/devel/activate_tools

Current development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -Ud
    source /opt/odoo/devel/activate_tools


History
-------

1.0.13 (2022-03-29)
~~~~~~~~~~~~~~~~~~~

* [IMP] Invoice data

1.0.12 (2022-03-14)
~~~~~~~~~~~~~~~~~~~

* [IMP] Stable version
* [IMP] comfiguration file for PYPI lint

1.0.11.1 (2022-03-12)
~~~~~~~~~~~~~~~~~~~~~

* [IMP] New file account_banking_manadate.xlsx
* [IMP] New file product_supplierinfo.xlsx
* [IMP] New test data
* [IMP] New tests

1.0.11 (2022-02-23)
~~~~~~~~~~~~~~~~~~~

* [IMP] Stable version

1.0.9.1 (2022-01-11)
~~~~~~~~~~~~~~~~~~~~

* [IMP] New test data

1.0.9 (2022-01-09)
~~~~~~~~~~~~~~~~~~

* [IMP] New test data

1.0.8.2 (2022-01-09)
~~~~~~~~~~~~~~~~~~~~

* [IMP] New test data

1.0.8.1 (2022-01-07)
~~~~~~~~~~~~~~~~~~~~

* [IMP] New test data

1.0.8 (2022-01-05)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version

1.0.6.2 (2021-11-16)
~~~~~~~~~~~~~~~~~~~~

* [IMP] Test data: inventory data
* [IMP] Test data: inventory data

1.0.5.4 (2021-10-18)
~~~~~~~~~~~~~~~~~~~~

* [IMP] Test data: supplier invoice with 22a / Codice IVA in fattura fornitore dati test

1.0.5.3 (2021-10-15)
~~~~~~~~~~~~~~~~~~~~

* [FIX] python3 failure



|
|

Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Contributors
------------

* Antonio M. Vigliotti <info@shs-av.com>


|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2022-06-05

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=master
    :target: https://travis-ci.com/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=master
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=1.0
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/1.0/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/1.0
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-1.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/1.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-1.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/1.0/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-1.svg
    :target: https://erp1.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/1.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/1.0
    :alt: Codecov
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
   :target: https://odoo-italia.org
   :alt: Odoo Italia Associazione
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


