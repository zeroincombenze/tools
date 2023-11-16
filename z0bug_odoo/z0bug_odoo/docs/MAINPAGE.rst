
================
z0bug_odoo 2.0.7
================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Zeroincombenze® continuous testing for odoo
-------------------------------------------

This package is an plug-in of **zerobug** package and aim to easily create odoo tests.

It replaces OCA MQT with some nice additional features.

*z0bug_odoo* is built on follow concepts:

* Odoo version independent; it can test Odoo from 6.1 until 16.0
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
content of the `sample_files <https://github.com/zeroincombenze/tools/tree/master/travis_emulator/template_travis.yml>`_
to your project’s root directory.

Then execute the command:

::

    make_travis_conf <TOOLS_PATH>/travis_emulator/template_travis.yml .travis.yml

You can check travis syntax with the `lint checker <http://lint.travis-ci.org/>`_ of travis, if available.

Notice: if you do not use travisCi web site, you can avoid to set .travis.yml file.
Local travis emulator and z0bug_odoo create local .travis.yml dinamically.


Odoo test integration
~~~~~~~~~~~~~~~~~~~~~

Current Odoo project version is declared by **VERSION** variable.
If your Odoo module must be tested against Odoo core,
you can test specific github repository by **ODOO_REPO** variable.
You can test against:

* odoo/odoo
* OCA/OCB
* zeroincombenze/OCB
* librerp/OCB

You can test against specific Odoo core version with ODOO_BRANCH variable if differs from your project version:

::

    # Odoo Branch 16.0
    - VERSION="16.0" ODOO_REPO="odoo/odoo"

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
From Odoo 11.0, python3 is used. You can test against 3.5, 3.6, 3.7 and 3.8 python versions.
Currently, python 3.8 is not yet supported.
This is the declaration:

::

    python:
      - "3.5"
      - "3.6"
      - "3.7"
      - "3.8"

Notice: python 3.5 support is ended on 2020 and 3,6 is ended on 2021.
Python 3.8 is no yet full supported by Odoo (2021), so use python 3.7


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

+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| variable               | default value                                          | meaning                                                                   |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| CHROME_TEST            |                                                        | Set value to 1 to use chrome client to test                               |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| DATA_DIR               | ~/data_dir                                             | Odoo data directory (data_dir in config file)                             |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| EXCLUDE                |                                                        | Modules to exclude from test                                              |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| INCLUDE                |                                                        | Modules to test (all                                                      |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| INSTALL_OPTIONS        |                                                        | Options passed to odoo-bin/openerp-server to install modules              |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| MQT_DBSUER             | $USER                                                  | Database username                                                         |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| MQT_TEMPLATE_DB        | template_odoo                                          | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| MQT_TEST_DB            | test_odoo                                              | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| NPM_CONFIG_PREFIX      | \$HOME/.npm-global                                     | N/D                                                                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| ODOO_COMMIT_TEST       | 0                                                      | Test result will be committed; require specific code at tear_off function |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| ODOO_REPO              | odoo/odoo                                              | OCB repository against test repository                                    |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| ODOO_SETUPS            | __manifest__.py __openerp__.py __odoo__.py __terp__.py | Names of Odoo manifest files                                              |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| ODOO_TEST_SELECT       | ALL                                                    | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| ODOO_TNLBOT            | 0                                                      | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| OPTIONS                |                                                        | Options passed to odoo-bin/openerp-server to execute tests                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PHANTOMJS_VERSION      |                                                        | Version of PhantomJS                                                      |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PS_TXT_COLOR           | 0;97;40                                                | N/D                                                                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PS_RUN_COLOR           | 1;37;44                                                | N/D                                                                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PS_NOP_COLOR           | 34;107                                                 | N/D                                                                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PS_HDR1_COLOR          | 97;42                                                  | N/D                                                                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PS_HDR2_COLOR          | 30;43                                                  | N/D                                                                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PS_HDR3_COLOR          | 30;45                                                  | N/D                                                                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| PYPI_RUN_PYVER         | (2.7|3.5|3.6|3.7|3.8)                                  | python versions to run (only PYPI projects)                               |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| SERVER_EXPECTED_ERRORS |                                                        | # of expected errors after tests                                          |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| TEST_DEPENDENCIES      | 0                                                      | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| TRAVIS_DEBUG_MODE      | 0                                                      | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| TRAVIS_PDB             |                                                        | The value 'true' activates pdb in local 'travis -B'                       |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| UNBUFFER               | 1                                                      | Use unbuffer (colors) to log results                                      |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| UNIT_TEST              |                                                        | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| TEST                   |                                                        | Read above                                                                |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| VERSION                |                                                        | Odoo version to test (see above)                                          |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| WEBSITE_REPO           |                                                        | Load package for website tests                                            |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+
| WKHTMLTOPDF_VERSION    | 0.12.5                                                 | Version of wkhtmltopdf (value are 0.12.1                                  |
+------------------------+--------------------------------------------------------+---------------------------------------------------------------------------+





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

TestEnv: the test environment
-----------------------------

TestEnv makes available a test environment ready to use in order to test your Odoo
module in quick and easy way.

The purpose of this software are:

* Create the Odoo test environment with records to use for your test
* Make available some useful functions to test your module (in z0bug_odoo)
* Simulate the wizard to test wizard functions (wizard simulator)
* Environment running different Odoo modules versions

Please, pay attention to test data: TestEnv use internal unicode even for python 2
based Odoo (i.e. 10.0). You should declare unicode date whenever is possible.
Note, Odoo core uses unicode even on old Odoo version.

Tests are based on test environment created by module mk_test_env in repository
https://github.com/zeroincombenze/zerobug-test

Requirements
~~~~~~~~~~~~

Ths TestEnv software requires:

* python_plus PYPI package
* z0bug_odoo PYPI package
* python 2.7 / 3.6 / 3.7 / 3.8

TestEnv is full integrated with Zeroincombenze® tools.
See https://zeroincombenze-tools.readthedocs.io/
and https://github.com/zeroincombenze/tools.git
Zeroincombenze® tools help you to test Odoo module with pycharm.



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

Ths TestEnv software requires:

* python_plus PYPI package
* z0bug_odoo PYPI package
* python 2.7 / 3.6 / 3.7 / 3.8


Model data declaration
~~~~~~~~~~~~~~~~~~~~~~

Each model is declared in a dictionary which key which is the external
reference used to retrieve the record.
i.e. the following record is named 'z0bug.partner1' in res.partner:

::

    TEST_RES_PARTNER = {
        "z0bug.partner1": {
            "name": "Alpha",
            "street": "1, First Avenue",
            ...
        }
    )

Please, do not to declare 'product.product' records: they are automatically
created as child of 'product.template'. The external reference must contain
the pattern '_template' (see below).

Magic relationship
~~~~~~~~~~~~~~~~~~

Some models/tables should be managed together, i.e. 'account.move' and 'account.move.line'.
TestEnv manages these models/tables, called header/detail, just as a single object.
Where header record is created, all detail lines are created with header.
To do this job you must declare external reference as explained below (external reference).

Warning: you must declare header and lines data before create header record.

::

    TEST_SALE_ORDER = {
        "z0bug.order_1": {
            ...
        }
    }

    TEST_SALE_ORDER_LINE = {
        "z0bug.order_1_1": {
            ...
        }
    }

    TEST_SETUP_LIST = ["sale.order", "sale.order.line"]

    class MyTest(SingleTransactionCase):

        def test_something(self):
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            # Declare order data in specific group to isolate data
            self.declare_all_data(data, group="order")
            # Create the full sale order with lines
            self.resource_make(model, xref, group="order")

Another magic relationship is the 'product.template' (product) / 'product.product' (variant) relationship.
Whenever a 'product.template' (product) record is created,
Odoo automatically creates one variant (child) record for 'product.product'.
If your test module does not need to manage product variants you can avoid to declare
'product.product' data even if this model is used in your test data.

For example, you have to test 'sale.order.line' which refers to 'product.product'.
You simply declare a 'product.template' record with external reference uses "_template"
magic text.

::

    TEST_PRODUCT_TEMPLATE = {
        "z0bug.product_template_1": {
            "name": "Product alpha",
            ...
        }
    )

    ...

    TEST_SALE_ORDER_LINE = {
        "z0bug.order_1_1": {
            "product_id": "z0bug.product_product_1",
            ...
        }
    )

    ...

    # Get 'product.template' record
    self.resource_bind("z0bug.product_template_1")
    # Get 'product.product' record
    self.resource_bind("z0bug.product_product_1")

External reference
~~~~~~~~~~~~~~~~~~

Every record is tagged by an external reference.
The external reference may be:

* Ordinary Odoo external reference (a), format "module.name"
* Test reference, format "z0bug.name" (b)
* Key value, format "external.key" (c)
* 2 keys reference, for header/detail relationship (d)
* Magic reference for 'product.template' / 'product.product' (e)

Ordinary Odoo external reference (a) is a record of 'ir.model.data';
you can see them from Odoo GUI interface.

Test reference (b) are visible just in the test environment.
They are identified by "z0bug." prefix module name.

External key reference (c) is identified by "external." prefix followed by
the key value used to retrieve the record.
If key value is an integer it is the record "id".
The field "code" or "name" are used to search record;
for account.tax the "description" field is used.
Please set self.debug_level = 2 (or more) to log these field keys.

The 2 keys reference (d) needs to address child record inside header record
at 2 level model (header/detail) relationship.
The key MUST BE the same key of the parent record,
plus "_", plus line identifier (usually 'sequence' field).
i.e. "z0bug.move_1_3" means: line with sequence 3 of 'account.move.line'
which is child of record "z0bug.move_1" of 'account.move'.
Please set self.debug_level = 2 (or more) to log these relationships.

For 'product.template' (product) you must use '_template' text in reference (e).
TestEnv inherit 'product.product' (variant) external reference (read above 'Magic relationship).

Examples:

::

    TEST_ACCOUNT_ACCOUNT = {
        "z0bug.customer_account": {
            "code": "", ...
        }
        "z0bug.supplier_account": {
            "code": "111100", ...
        }
    )

    ...

    self.resource_edit(
        partner,
        web_changes = [
            ("country_id", "base.it"),       # Odoo external reference (type a)
            ("property_account_receivable_id",
             "z0bug.customer_account"),      # Test reference (type b)
            ("property_account_payable_id",
             "external.111100"),             # External key (type c)
        ],
    )

Module test execution session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module test execution workflow should be:

    #. Data declaration, in setUp() function
    #. Base data creation, in setUp() function
    #. Supplemental data declaration
    #. Supplemental data creation

Test data may be managed by one or more data group; if not declared,
"base" group name is used. The "base" group must be created at the setUp()
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
            # Add following statement just for get debug information
            self.debug_level = 2
            data = {"TEST_SETUP_LIST": TEST_SETUP_LIST}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            self.declare_all_data(data)     # TestEnv swallows the data
            self.setup_env()                # Create test environment

        def test_something(self):
            data = {"TEST_SETUP_LIST": ["sale.order", "sale.order.line"]}
            for resource in TEST_SETUP_LIST:
                item = "TEST_%s" % resource.upper().replace(".", "_")
                data[item] = globals()[item]
            # Declare order data in specific group to isolate data
            self.declare_all_data(data, group="order")
            # Create the full sale order with lines
            self.setup_env(group="order")

Note the external reference are globals and they are visible from any groups.
After base data is created it starts the real test session. You can simulate
various situation; the most common are:

    #. Simulate web form create record
    #. Simulate web form update record
    #. Simulate the multi-record windows action
    #. Download any binary data created by test
    #. Engage wizard

Notice: you can also create / update record with usually create() / write()
Odoo function but they do not really simulate the user behavior.
They do not engage the onchange methods, they do not load any view and so on.

The real best way to test a create session is like the follow example
based on res,partner model:

::

        record = self.resource_edit(
            resource="res.partner",
            web_changes=[
                ("name", "Adam"),
                ("country_id", "base.us"),
                ...
            ],
        )

You can also simulate the update session, issuing the record:

::

        record = self.resource_edit(
            resource=record,
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

Data values
~~~~~~~~~~~

Data values may be raw data (string, number, dates, etc.) or external reference
or some macro.
You can declare data value on your own but you can discover th full test environment
in https://github.com/zeroincombenze/zerobug-test/mk_test_env/ and get data
from this environment.

company_id
~~~~~~~~~~

If value is empty, user company is used.
When data is searched by resource_bind() function the "company_id" field
is automatically filled and added to search domain.
This behavior is not applied on
"res.users", "res.partner","product.template" and "product.product" models.
For these models you must fill the "company_id" field.
For these models resource_bind() function searches for record with company_id
null or equal to current user company.

boolean
~~~~~~~

You can declare boolean value:

* by python boolean False or True
* by integer 0 o 1
* by string "0" / "False" or "1" / "True"

::


    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "supplier": False,
                "customer": "True",
                "is_company": 1,
            }
        }
    )

char / text
~~~~~~~~~~~

Char and Text values are python string; please use unicode whenever is possible
even when you test Odoo 10.0 or less.

::


    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "name": "Alpha",
                "street": "1, First Avenue",
                ...
            }
        }
    )

integer / float / monetary
~~~~~~~~~~~~~~~~~~~~~~~~~~

Integer, Floating and Monetary values are python integer or float.
If numeric value is issued as string, it is internally converted
as integer/float.

::


    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "color": 1,
                "credit_limit": 500.0,
                "payment_token_count": "0",
            }
        }
    )

date / datetime
~~~~~~~~~~~~~~~

Date and Datetime value are managed in special way.
They are processed by compute_date() function (read below).
You can issue a single value or a 2 values list, 1st is the date,
2nd is the reference date.

::


    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "activity_date_deadline": "####-1>-##",    # Next month
                "signup_expiration": "###>-##-##",         # Next year
                "date": -1,                                # Yesterday
                "last_time_entries_checked":
                    [+2, another_date],                    # 2 days after another day
                "message_last_post": "2023-06-26",         # Specific date
            }
        }
    )

many2one
~~~~~~~~

You can issue an integer (if you exactly know the ID)
or an external reference. Read above about external reference.

::


    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "country_id": "base.it",                   # Odoo external reference
                "property_account_payable_id":
                    "z0bug.customer_account",              # Test record
                "title": "external.Mister"                 # Record with name=="Mister"
            }
        }
    )

one2many / many2many
~~~~~~~~~~~~~~~~~~~~

The one2many and many2many field may contains one or more ID;
every ID use the many2one notation using external reference.
Value may be a string (just 1 value) or a list.

::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "bank_ids":
                    [
                        "base.bank_partner_demo",
                        "base_iban.bank_iban_china_export",
                    ],
                "category_id": "base.res_partner_category_0",
            }
        }
    )

binary
~~~~~~

Binary file are supplied with os file name. Test environment load file and
get binary value. File must be located in ./tests/data directrory.
::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "image": "z0bug.partner1.png"
            }
        }
    )


Functions
---------

store_resource_data
~~~~~~~~~~~~~~~~~~~

Store a record data definition for furthermore use.
Data stored is used by setup_env() function and/or by:

* resource_create() without values
* resource_write() without values
* resource_make() without values

def store_resource_data(self, resource, xref, values, group=None, name=None):

    Args:
        resource (str): Odoo model name
        xref (str): external reference
        values (dict): record data
        group (str): used to manager group data; default is "base"
        name (str): label of dataset; default is resource name

compute_date
~~~~~~~~~~~~

Compute date or datetime against today or a reference date. Date may be:

* python date/datetime value
* string with ISO format "YYYY-MM-DD" / "YYYY-MM-DD HH:MM:SS"
* string value that is a relative date against today / reference date

Relative string format is like ISO, with 3 groups separated by '-' (dash).
Every group may be an integer or a special notation:

* starting with '<' meas subtract; i.e. '<2' means minus 2
* ending with '>' meas add; i.e. '2>' means plus 2
* '#' with '<' or '>' means 1; i.e. '<###' means minus 1
* all '#' means same value of reference date

A special notation '+N' and '-N', where N is an integer means add N days
or subtract N day from reference date.
Here, in following examples, are used python iso date convention:

* '+N': return date + N days to refdate (python timedelta)
* '-N': return date - N days from refdate (python timedelta)
* '%Y-%m-%d': strftime of issued value
* '%Y-%m-%dT%H:%M:%S': same datetime
* '%Y-%m-%d %H:%M:%S': same datetime
* '####-%m-%d': year from refdate (or today), month '%m', day '%d'
* '####-##-%d': year and month from refdate (or today), day '%d'
* '2022-##-##': year 2022, month and day from refdate (or today)
* '<###-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
* '<001-%m-%d': year -1  from refdate (or today), month '%m', day '%d'
* '<###-#>-%d': year -1  from refdate, month +1 from refdate, day '%d'
* '<005-2>-##': year -5, month +2 and day from refdate

Notes:
    Returns a ISO format string.
    Returned date is always a valid date; i.e. '####-#>-31',
    with ref month January result '####-02-31' becomes '####-03-03'
    To force last day of month, set '99': i.e. '####-<#-99' becomes the
    last day of previous month of refdate

def compute_date(self, date, refdate=None):

    date (date or string or integer): formula; read aboove
    refdate (date or string): reference date

resource_bind
~~~~~~~~~~~~~

Bind record by xref or searching it or browsing it.
This function returns a record using issued parameters. It works in follow ways:

* With valid xref it work exactly like self.env.ref()
* If xref is an integer it works exactly like self.browse()
* I xref is invalid, xref is used to search record
    * xref is searched in stored data
    * xref ("MODULE.NAME"): if MODULE == "external", NAME is the record key

def resource_bind(self, xref, raise_if_not_found=True, resource=None):

    Args:
        xref (str): external reference
        raise_if_not_found (bool): raise exception if xref not found or if more records found
        resource (str): Odoo model name, i.e. "res.partner"

    Returns:
        obj: the Odoo model record

    Raises:
        ValueError: if invalid parameters issued

resource_create
~~~~~~~~~~~~~~~

Create a test record and set external ID to next tests.
This function works as standard Odoo create() with follow improvements:

* It can create external reference too
* It can use stored data if no values supplied

def resource_create(self, resource, values=None, xref=None, group=None):

    Args:
        resource (str): Odoo model name, i.e. "res.partner"
        values (dict): record data (default stored data)
        xref (str): external reference to create
        group (str): used to manager group data; default is "base"

    Returns:
        obj: the Odoo model record, if created

resource_write
~~~~~~~~~~~~~~

Update a test record.
This function works as standard Odoo write() with follow improvements:

* If resource is a record, xref is ignored (it should be None)
* It resource is a string, xref must be a valid xref or an integer
* If values is not supplied, record is restored to stored data values

def resource_write(self, resource, xref=None, values=None, raise_if_not_found=True, group=None):

    Args:
        resource (str|obj): Odoo model name or record to update
        xref (str): external reference to update: required id resource is string
        values (dict): record data (default stored data)
        raise_if_not_found (bool): raise exception if xref not found or
                       if more records found
        group (str): used to manager group data; default is "base"

    Returns:
        obj: the Odoo model record

    Raises:
        ValueError: if invalid parameters issued

resource_make
~~~~~~~~~~~~~

Create or write a test record.
This function is a hook to resource_write() or resource_create().

def resource_make(self, resource, xref, values=None, group=None):

declare_resource_data
~~~~~~~~~~~~~~~~~~~~~

Declare data to load on setup_env().

def declare_resource_data(self, resource, data, name=None, group=None, merge=None)

    Args:
        resource (str): Odoo model name, i.e. "res.partner"
        data (dict): record data
        name (str): label of dataset; default is resource name
        group (str): used to manager group data; default is "base"
        merge (str): merge data with public data (currently just "zerobug")

    Raises:
        TypeError: if invalid parameters issued

declare_all_data
~~~~~~~~~~~~~~~~

Declare all data to load on setup_env().

def declare_resource_data(self, resource, data, name=None, group=None, merge=None)

    Args:
        message (dict): data message
            TEST_SETUP_LIST (list): resource list to load
            TEST_* (dict): resource data; * is the uppercase resource name where
                           dot are replaced by "_"; (see declare_resource_data)
        group (str): used to manager group data; default is "base"
        merge (str): merge data with public data (currently just "zerobug")

    Raises:
        TypeError: if invalid parameters issuedd

get_resource_data
~~~~~~~~~~~~~~~~~

Get declared resource data; may be used to test compare.

def get_resource_data(self, resource, xref, group=None):

    Args:
        resource (str): Odoo model name or name assigned, i.e. "res.partner"
        xref (str): external reference
        group (str): if supplied select specific group data; default is "base"

    Returns:
        dictionary with data or empty dictionary

get_resource_data_list
~~~~~~~~~~~~~~~~~~~~~~

Get declared resource data list.

def get_resource_data_list(self, resource, group=None):

    Args:
        resource (str): Odoo model name or name assigned, i.e. "res.partner"
        group (str): if supplied select specific group data; default is "base"

    Returns:
        list of data

get_resource_list
~~~~~~~~~~~~~~~~~

Get declared resource list.

def get_resource_list(self, group=None):

    Args:
        group (str): if supplied select specific group data; default is "base"

setup_company
~~~~~~~~~~~~~

Setup company values for current user.

This function assigns company to current user and / or can create xref aliases
and /or can update company values.
This function is useful in multi companies tests where different company values
will be used in different tests. May be used in more simple test where company
data will be updated in different tests.
You can assign partner_xref to company base by group; then all tests executed
after setup_env(), use the assigned partner data for company of the group.
You can also create more companies and assign one of them to test by group.

def setup_company(self, company, xref=None, partner_xref=None, values={}, group=None):

    Args:
        company (obj): company to update; if not supplied a new company is created
        xref (str): external reference or alias for main company
        partner_xref (str): external reference or alias for main company partner
        values (dict): company data to update immediately
        group (str): if supplied select specific group data; default is "base"

    Returns:
        default company for user

setup_env
~~~~~~~~~

Create all record from declared data.

This function starts the test workflow creating the test environment.
Test data must be declared before engage this function with declare_all_data()
function (see above).
setup_env may be called more times with different group value.
If it is called with the same group, it recreates the test environment with
declared values; however this feature might do not work for some reason: i.e.
if test creates a paid invoice, the setup_env() cannot unlink invoice.
If you want to recreate the same test environment, assure the conditions for
unlink of all created and tested records.
If you create more test environment with different group you can use all data,
even record created by different group.
In this way you can test a complex process the evolved scenario.

def setup_env(self, lang=None, locale=None, group=None):

    Args:
        lang (str): install & load specific language
        locale (str): install locale module with CoA; i.e l10n_it
        group (str): if supplied select specific group data; default is "base"

    Returns:
        None

resource_edit
~~~~~~~~~~~~~

Server-side web form editing.

Ordinary Odoo test use the primitive create() and write() function to manage
test data. These methods create an update records, but they do not properly
reflect the behaviour of user editing form with GUI interface.

This function simulates the client-side form editing in the server-side.
It works in the follow way:

* It can simulate the form create record
* It can simulate the form update record
* It can simulate the user data input
* It calls the onchange functions automatically
* It may be used to call button in the form

User action simulation:

The parameter <web_changes> is a list of user actions to execute sequentially.
Every element of the list is another list with 2 or 3 values:

* Field name to assign value
* Value to assign
* Optional function to execute (i.e. specific onchange)

If field is associate to an onchange function the relative onchange functions
are execute after value assignment. If onchange set another field with another
onchange the relative another onchange are executed until all onchange are
exhausted. This behavior is the same of the form editing.

Warning: because function are always executed at the server side the behavior
may be slightly different from actual form editing. Please take note of
following limitations:

* update form cannot simulate discard button
* some required data in create must be supplied by default parameter
* form inconsistency cannot be detected by this function
* nested function must be managed by test code (i.e. wizard from form)

See test_testenv module for test examples
https://github.com/zeroincombenze/zerobug-test/tree/12.0/test_testenv

def resource_edit(self, resource, default={}, web_changes=[], actions=[], ctx={}):

    Args:
        resource (str or obj): if field is a string simulate create web behavior of
                               Odoo model issued in resource;
                               if field is an obj simulate write web behavior on the
                               issued record
        default (dict): default value to assign
        web_changes (list): list of tuples (field, value); see <wiz_edit>

    Returns:
        windows action to execute or obj record

wizard
~~~~~~

Execute a full wizard.

Engage the specific wizard, simulate user actions and return the wizard result,
usually a windows action.

It is useful to test:

    * view names
    * wizard structure
    * wizard code

Both parameters <module> and <action_name> must be issued in order to
call <wiz_by_action_name>; they are alternative to act_windows.

*** Example of use ***

::

  XML view file:
      <record id="action_example" model="ir.actions.act_window">
          <field name="name">Example</field>
          <field name="res_model">wizard.example</field>
          [...]
      </record>

Python code:

::

    act_windows = self.wizard(module="module_example",
        action_name="action_example", ...)
    if self.is_action(act_windows):
        act_windows = self.wizard(act_windows=act_windows, ...)

User action simulation:

The parameter <web_changes> is a list of user actions to execute sequentially.
Every element of the list is another list with 2 or 3 values:

* Field name to assign value
* Value to assign
* Optional function to execute (i.e. specific onchange)

If field is associate to an onchange function the relative onchange functions
are execute after value assignment. If onchange set another field with another
onchange the relative another onchange are executed until all onchange are
exhausted. This behavior is the same of the form editing.

def wizard(self, module=None, action_name=None, act_windows=None, records=None, default=None, ctx={}, button_name=None, web_changes=[], button_ctx={},):

    Args:
        module (str): module name for wizard to test; if "." use current module name
        action_name (str): action name
        act_windows (dict): Odoo windows action (do not issue module & action_name)
        records (obj): objects required by the download wizard
        default (dict): default value to assign
        ctx (dict): context to pass to wizard during execution
        button_name (str): function name to execute at the end of then wizard
        web_changes (list): list of tuples (field, value); see above
        button_ctx (dict): context to pass to button_name function

    Returns:
        result of the wizard

    Raises:
        ValueError: if invalid parameters issued

validate_record
~~~~~~~~~~~~~~~

Validate records against template values.
During the test will be necessary to check result record values.
This function aim to validate all the important values with one step.
You have to issue 2 params: template with expected values and record to check.
You can declare just some field value in template which are important for you.
Both template and record are lists, record may be a record set too.
This function do following steps:

* matches templates and record, based on template supplied data
* check if all template are matched with 1 record to validate
* execute self.assertEqual() for every field in template
* check for every template record has matched with assert

def validate_records(self, template, records):

    Args:
         template (list of dict): list of dictionaries with expected values
         records (list or set): records to validate values

    Returns:
        list of matched coupled (template, record) + # of assertions

    Raises:
        ValueError: if no enough assertions or one assertion is failed

get_records_from_act_windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get records from a windows message.

def get_records_from_act_windows(self, act_windows):

    Args:
        act_windows (dict): Odoo windows action returned by a wizard

    Returns:
        records or False

    Raises:
        ValueError: if invalid parameters issued



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

2.0.7 (2023-04-08)
~~~~~~~~~~~~~~~~~~

* [NEW] TestEnv: assertion counter
* [IMP] TestEnv: is_xref recognizes dot name, i.e "zobug.external.10"
* [IMP] TestEnv: the field <description> is not mode key (only acount.tax)
* [IMP] TestEnv: 3th level xref may be a many2one field type

2.0.6 (2023-02-20)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: _get_xref_id recognize any group
* [FIX] TestEnv: datetime field more precise (always with time)
* [FIX] TestEnv: resource_make / resource_write fall in crash if repeated on headr/detail models
* [NEW] TestEnv: 2many fields accepts more xref values
* [IMP] TestEnv: debug message with more icons and more readable
* [IMP] TestEnv: cast_types with formatting for python objects
* [IMP] TestEnv: validate_record now uses intelligent algorithm to match pattern templates and records

2.0.5 (2023-01-25)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: in some rare cases, wizard crashes
* [NEW] TestEnv: get_records_from_act_windows()
* [IMP] TestEnv: resource_make now capture demo record if available
* [IMP] TestEnv: resource is not required for declared xref
* [IMP] TestEnv: self.module has all information about current testing module
* [IMP] TestEnv: conveyance functions for all fields (currenly jsust for account.payment.line)
* [IMP] TestEnv: fields many2one accept object as value
* [IMP] TestEnv: function validate_records() improvements
* [FIX] TestEnv: company_setup, now you can declare bank account
* [IMP] TesEnv: minor improvements

2.0.4 (2023-01-13)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: resource_create does not duplicate record
* [FIX] TestEnv: resource_write after save calls write() exactly like Odoo behavior
* [NEW] TestEnv: new function field_download()
* [NEW] TestEnv: new function validate_records()
* [IMP] TestEnv: convert_to_write convert binary fields too
* [IMP] TestEnv: minor improvements

2.0.3 (2022-12-29)
~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: more debug messages
* [IMP] TestEnv: more improvements
* [FIX] TestEnv: sometime crashes if default use context
* [FIX] TestEnv: bug fixes

2.0.2 (2022-12-09)
~~~~~~~~~~~~~~~~~~

* [FIX] Automatic conversion of integer into string for 'char' fields
* [IMP] TestEnv

2.0.1.1 (2022-11-03)
~~~~~~~~~~~~~~~~~~~~

* [REF] clone_oca_dependencies.py

2.0.1 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version

2.0.0.1 (2022-10-15)
~~~~~~~~~~~~~~~~~~~~

* [FIX] Crash in travis

2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [REF] Stable version



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
Contributors
------------



|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2023-04-15

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
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=2.0
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/2.0/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/2.0
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/2.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/2.0
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


