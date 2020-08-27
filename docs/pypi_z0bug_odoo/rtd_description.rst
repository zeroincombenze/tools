.. toctree::
   :maxdepth: 2

Zeroincombenze® continuous testing for odoo
-------------------------------------------

This package is an plug-in of zerobug and aim to easily create odoo tests.

The package replaces OCA MQT with some nice additional features.

*z0bug_odoo* is built on follow concepts:

* Odoo version independent; it can also test Odoo 6.1 and 7.0
* It is designed to run in local environment too, using `local travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_
* It can run with reduced set of pylint tests (see below *LINT_CHECK_LEVEL*)
* Ready-made database
* Quality Check Id

travis support
--------------

Another goal of z0bug_odoo is to provide helpers to ensure the quality of Odoo addons.
This function was forked from OCA MQT. However this package and OCA MQT differ by:

* z0bug_odoo can also test Odoo 6.1 and 7.0; OCA MQT fails with these versions
* z0bug_odoo is designed to run in local environment too, using `local travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_
* z0bug_odoo is designed to execute some debug statements (see below *MQT debug informations*)
* z0bug_odoo can run with reduced set of pylint tests (see below *LINT_CHECK_LEVEL*)
* z0bug_odoo can run with reduced set of Odoo tests (see below *ODOO_TEST_SELECT*)
* OCA MQT is the only component to build environment and test Odoo. Zeroincombenze® MQT is part of `Zeroincombenze® tools <https://github.com/zeroincombenze/tools>`_
* As per prior rule, building test environment is made by clodoo and lisa tools. These commands can also build a complete Odoo environment out of the box.

Other differences between z0bg_odoo and OCA MQT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Zeroincombenze® OCB use submodules. When test in starting, submodules should not be upgraded.
Use this statements:

::

    - git:
      submodules: false

OCA does not use before_install section while z0bg_odoo requires before_install:

z0bg_odoo set security environment. You have not to add security statements
(with OCA MQT you must remove comment):

`#  - pip install urllib3[secure] --upgrade; true`

z0bg_odoo do some code upgrade; using OCA MQT you must do these code by .travis.yml.
When ODOO_TEST_SELECT="APPLICATIONS":

`# sed -i "s/self.url_open(url)/self.url_open(url, timeout=100)/g" ${TRAVIS_BUILD_DIR}/addons/website/tests/test_crawl.py;`

When ODOO_TEST_SELECT="LOCALIZATION":

`# sed -i "/'_auto_install_l10n'/d" ${TRAVIS_BUILD_DIR}/addons/account/__manifest__.py`


Sample travis configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to setup TravisCI continuous integration for your project, just copy the
content of the `sample_files <https://github.com/zeroincombenze/tools/tree/master/zerobug/sample_files/.travis.yml>`_
to your project’s root directory.

Then execute the command:

::

    topep8 -b<odoo_version> .travis.yml

You can check travis syntax with the `lint checker <http://lint.travis-ci.org/>`_ of travis if available.

If your project depends on other Odoo Github repositories like OCA, create a file called `oca_dependencies.txt` at the root of your project and list the dependencies there.
One per line like so:

    project_name optional_repository_url optional_branch_name

During testbed setup, z0bug_odo will automatically download and place these repositories accordingly into the addon path.
Note on addons path ordering: They will be placed after your own repo, but before the odoo core repo.

If missed optional_repository_url, the repository is searched for repository with the same owner of tested project.
OCA MQT loads OCA repository while Zeroincombenze® MQT searches for


Multiple values for environment variable VERSION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use branch or pull request into environment variable VERSION:

::

    Branch 10.0
    - VERSION="10.0" ODOO_REPO="odoo/odoo"

    Pull request odoo/odoo#143
    -  VERSION="pull/143" ODOO_REPO="odoo/odoo"


Using custom branch inside odoo repository using ODOO_BRANCH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the custom branch into the ODOO_REPO using the environment variable ODOO_BRANCH:

::

    Branch saas-17
    - ODOO_REPO="odoo/odoo" ODOO_BRANCH="saas-17"



Module unit tests
~~~~~~~~~~~~~~~~~

z0bug_odoo is also capable to test each module individually.
The intention is to check if all dependencies are correctly defined.
Activate it through the `UNIT_TEST` directive.
An additional line should be added to the `env:` section,
similar to this one:

::

    - VERSION="12.0" UNIT_TEST="1"


Coveralls/Codecov configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Coveralls <https://coveralls.io/>`_ and `Codecov <https://codecov.io/>`_ services provide information on the test coverage of your modules.
Currently both configurations are automatic (check default configuration `here <cfg/.coveragerc>`_.
So, as of today, you don't need to include a `.coveragerc` into the repository,
If you do it, it will be simply ignored.



Names used for the test databases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

z0bug_odoo has a nice feature of organizing your testing databases.
You might want to do that if you want to double them up as
staging DBs or if you want to work with an advanced set of
templates in order to speed up your CI pipeline.
Just specify at will:

`MQT_TEMPLATE_DB='mqt_odoo_template' MQT_TEST_DB='mqt_odoo_test'`.


Isolated pylint+flake8 checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to make a build exclusive for these checks, you can add a line
on the `env:` section of the .travis.yml file with this content:

::

    - VERSION="7.0" LINT_CHECK="1"

You will get a faster answer about these questions and also a fast view over
semaphore icons in Travis build view.

To avoid making again these checks on other builds, you have to add
LINT_CHECK="0" variable on the line:

::

    - VERSION="7.0" ODOO_REPO="odoo/odoo" LINT_CHECK="0"

You can superset above options in local travis emulator.


Reduced set of check
~~~~~~~~~~~~~~~~~~~~

You can execute reduced set of check, in order to gradually evolve your code quality
when you meet too many errors.

To enable reduced set of check add one of follow lines:

::

    - LINT_CHECK="1" LINT_CHECK_LEVEL="MINIMAL"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="REDUCED"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="AVERAGE"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="NEARBY"

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
| W391 | |no_check| | |check|    |         |        | |check|    | blank line at end of file                                                                                                        |
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

+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| Test  | MINIMAL    | REDUCED | AVERAGE | NEARBY | OCA     | Notes                                                                               |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W0101 | |no_check| |         |         |        | |check| | `unreachable <http://pylint-messages.wikidot.com/messages:w0101>`_                  |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W0312 | |check|    |         |         |        | |check| | `wrong-tabs-instead-of-spaces <http://pylint-messages.wikidot.com/messages:w0312>`_ |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W0403 | |no_check| |         |         |        | |check| | relative-import                                                                     |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W1401 | |no_check| | |check| |         |        | |check| | anomalous-backslash-in-string                                                       |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| E7901 | |check|    |         |         |        | |check| | `rst-syntax-error <https://pypi.org/project/pylint-odoo/1.4.0>`_                    |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C7902 | |no_check| | |check| |         |        | |check| | missing-readme                                                                      |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7903 | |no_check| |         |         |        | |check| | javascript-lint                                                                     |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7908 | |check|    |         |         |        | |check| | missing-newline-extrafiles                                                          |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7909 | |no_check| |         |         |        | |check| | redundant-modulename-xml                                                            |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7910 | |no_check| | |check| |         |        | |check| | wrong-tabs-instead-of-spaces                                                        |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7930 | |no_check| |         |         |        | |check| | `file-not-used <https://pypi.org/project/pylint-odoo/1.4.0>`_                       |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7935 | |no_check| |         |         |        | |check| | missing-import-error                                                                |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7940 | |no_check| |         |         |        | |check| | dangerous-view-replace-wo-priority                                                  |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W7950 | |no_check| |         |         |        | |check| | odoo-addons-relative-import                                                         |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| E8102 | |no_check| |         |         |        | |check| | invalid-commit                                                                      |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8103 | |no_check| |         |         |        | |check| | `manifest-deprecated-key <https://pypi.org/project/pylint-odoo/1.4.0>`_             |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W8103 | |no_check| |         |         |        | |check| | translation-field                                                                   |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8104 | |no_check| |         |         |        | |check| | `class-camelcase <https://pypi.org/project/pylint-odoo/1.4.0>`_                     |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W8104 | |no_check| |         |         |        | |check| | api-one-deprecated                                                                  |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8105 | |no_check| |         |         |        | |check| | `license-allowed <https://pypi.org/project/pylint-odoo/1.4.0>`_                     |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| C8108 | |no_check| |         |         |        | |check| | method-compute                                                                      |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| R8110 | |no_check| |         |         |        | |check| | old-api7-method-defined                                                             |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| W8202 | |no_check| |         |         |        | |check| | use-vim-comment                                                                     |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | sql-injection                                                                       |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | duplicate-id-csv                                                                    |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | create-user-wo-reset-password                                                       |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | dangerous-view-replace-wo-priority                                                  |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | translation-required                                                                |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | duplicate-xml-record-id                                                             |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | no-utf8-coding-comment                                                              |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | attribute-deprecated                                                                |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+
| N/A   | |no_check| |         |         |        | |check| | consider-merging-classes-inherited                                                  |
+-------+------------+---------+---------+--------+---------+-------------------------------------------------------------------------------------+




Reduced set of modules test
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Last Odoo packages may fail in Travis CI or in local environment.
Currently Odoo OCB core tests fail; we are investigating for causes.
OCA workaround is following example statement:
`export INCLUDE=$(getaddons.py -m --only-applications ${TRAVIS_BUILD_DIR}/odoo/addons ${TRAVIS_BUILD_DIR}/addons)`

You can execute reduced set of tests adding one of follow lines:

::

    - TESTS="1" ODOO_TEST_SELECT="ALL"
    - TESTS="1" ODOO_TEST_SELECT="NO-CORE"
    - ....

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




Disable pylint and/or flake8 checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can disable some specific test or some file from lint checks.

To disable flake8 checks on specific file you can add following line at the beginning of python file:

`# flake8: noqa`

To disable pylint checks on specific file you can add following line at the beginning of python file:

`# pylint: skip-file`

To disable both flake8 and pylint checks on specific file you can add following line at the beginning of python file:

`# flake8: noqa - pylint: skip-file`

To disable pylint checks on specific XML file you can add following line in XML file after xml declaration:

`<!-- pylint:disable=deprecated-data-xml-node -->`

You can also disable specific pylint check in some source part of python file adding a comment at the same statement to disable check. Here an example to disable sql error (notice comment must be at beginning of the statement):

::

    self._cr.execute()      # pylint: disable=E8103



Disable test
~~~~~~~~~~~~

If you want to make a build without tests, you can use the following directive:
`TEST_ENABLE="0"`

You will simply get the databases with packages installed,
but without running any tests.


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
| MQT_TEMPLATE_DB        |                                                        | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| MQT_TEST_DB            |                                                        | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| NPM_CONFIG_PREFIX      | \$HOME/.npm-global                                     | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_REPO              | odoo/odoo                                              | OCB repository against test repository                       |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_SETUPS            | __manifest__.py __openerp__.py __odoo__.py __terp__.py | Names of Odoo manifest files                                 |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_TEST_SELECT       | ALL                                                    | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| ODOO_TNLBOT            | 0                                                      | No yet documented                                            |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| OPTIONS                |                                                        | Options passed to odoo-bin/openerp-server to execute tests   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PHANTOMJS_VERSION      |                                                        | Version of PhantomJS                                         |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_TXT_COLOR           | 0;97;40                                                | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_RUN_COLOR           | 1;36;48;5                                              | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_NOP_COLOR           | 31;105                                                 | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_HDR1_COLOR          | 97;48;5;22                                             | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_HDR2_COLOR          | 30;43                                                  | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PS_HDR3_COLOR          | 30;47                                                  | N/D                                                          |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| PYPI_RUN_PYVER         | (2.7|3.5|3.6|3.7|3.8)                                  | python versions to run (only PYPI projects)                  |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| SERVER_EXPECTED_ERRORS |                                                        | # of expected errors after tests                             |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| TRAVIS_DEBUG_MODE      | 0                                                      | Read above                                                   |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| TRAVIS_PDB             |                                                        | Activate pdb to local test (experimental)                    |
+------------------------+--------------------------------------------------------+--------------------------------------------------------------+
| UNBUFFER               | True                                                   | Use unbuffer (colors) to log results                         |
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





Debug informations
~~~~~~~~~~~~~~~~~~

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

    ${HOME}
    |
    |___ build (by TravisCI)
    |    |
    |    |___ ${TRAVIS_BUILD_DIR}  (by TravisCI)
    |    |    # testing project repository
    |    |
    |    \___ ${ODOO_REPO} (by travis_install_env / travis_install_nightly of .travis.yml)
    |         # Odoo or OCA/OCB repository to check compatibility of testing project
    |         # same behavior of OCA MQT (2)
    |         # if testing OCB, travis_install_env ignore this directory
    |
    |___ ${ODOO_REPO}-${VERSION} (by .travis.yml)
    |    # same behavior of OCA MQT
    |    # symlnk of ${HOME}/build/{ODOO_REPO}
    |    # Odoo or OCA repository to check with
    |
    |___ dependencies (by travis_install_env / travis_install_nightly of .travis.yml)
    |    # Odoo dependencies (2)
    |
    \___ tools (by .travis.yml)   # clone of this project
         |
         \___ maintainer-quality-tools (by .travis.yml) (1)
              # same behavior of OCA MQT
              |
              \___ travis (child of maintainer-quality-tools), in PATH

::

    (1) Done by .travis.yml in before install section with following statements:
        - git clone https://github.com/zeroincombenze/tools.git ${HOME}/tools --depth=1
        - mv ${HOME}/tools/maintainer-quality-tools ${HOME}
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}
        Above statements replace OCA statements:
        - git clone https://github.com/OCA/maintainer-quality-tools.git ${HOME}/maintainer-quality-tools --depth=1
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}

::

    (2) Done by .travis.yml in install section with following statements:
        - travis_install_env
        Above statements replace OCA statements:
        - travis_install_nightly
        You can also create OCA environment using travis_install_nightly with follow statements:
        - export MQT_TEST_MODE=oca
        - travis_install_env
        Or else
        - travis_install_env oca



qci
---

+-------------+-----------------------------------------------------------------------------------+
| qci         | description                                                                       |
+-------------+-----------------------------------------------------------------------------------+
| pay.SCT     | Credit Transfer payment / Pagamento bonifico                                      |
+-------------+-----------------------------------------------------------------------------------+
| pay.RB      | RiBA payment / Pagamento RiBA (IT)                                                |
+-------------+-----------------------------------------------------------------------------------+
| pay.SDD     | Sepa Direct Debit / Pagamento Sepa DD                                             |
+-------------+-----------------------------------------------------------------------------------+
| part.pt1    | Partner with one date payment / Cliente con pagamento in unica soluzione          |
+-------------+-----------------------------------------------------------------------------------+
| part.pt2    | Partner with multiple date payment / Cliente con pagamento di più scadenze        |
+-------------+-----------------------------------------------------------------------------------+
| part.it     | Local partner (Italy) / Cliente italiano                                          |
+-------------+-----------------------------------------------------------------------------------+
| part.eu     | EU partner / Cliente intraUE                                                      |
+-------------+-----------------------------------------------------------------------------------+
| part.xeu    | Extra-EU partner / Cliente extraUE                                                |
+-------------+-----------------------------------------------------------------------------------+
| acc.rc      | Reverse Charge                                                                    |
+-------------+-----------------------------------------------------------------------------------+
| acc.sp      | Split Payment                                                                     |
+-------------+-----------------------------------------------------------------------------------+
| part.PA     | Partne is PA                                                                      |
+-------------+-----------------------------------------------------------------------------------+
| acc.uVAT    | Full Undeductible VAT / IVA totalmente indetraibile                               |
+-------------+-----------------------------------------------------------------------------------+
| acc.puVAT   | Undeductible VAT / IVA parzialmente indetraibile                                  |
+-------------+-----------------------------------------------------------------------------------+
| inv.asset   | Invoice with asset/Fattura di beni strumentali                                    |
+-------------+-----------------------------------------------------------------------------------+
| inv.asalem  | Corrispettivi misti                                                               |
+-------------+-----------------------------------------------------------------------------------+
| inv.asalex  | Corrispettivi ripartiti (ventilazione)                                            |
+-------------+-----------------------------------------------------------------------------------+
| acc.uRB     | Insoluto RiBA                                                                     |
+-------------+-----------------------------------------------------------------------------------+
| invo.sp     | Sale invoice with split payment / Fattura di vendita con split-payment            |
+-------------+-----------------------------------------------------------------------------------+
| invo.rc     | Sale invoice with reverse charge / Fattura di vendita con reverse charge          |
+-------------+-----------------------------------------------------------------------------------+
| invo.eu     | Sale invoice to EU partner / Fattura di vendita intraUE                           |
+-------------+-----------------------------------------------------------------------------------+
| invo.xeu    | Sale invoice to xEU partner / Fattura di vendita extraUE                          |
+-------------+-----------------------------------------------------------------------------------+
| invo.li     | Sale invoice with lettera di intento / Fattura di vendita lettera di intento      |
+-------------+-----------------------------------------------------------------------------------+
| invo.wht    | Sale invoice with withholding / Fattura di vendita ritenuta d'acconto             |
+-------------+-----------------------------------------------------------------------------------+
| invo.enas   | Sale invoice with enasarco / Fattura di vendita con ensarco                       |
+-------------+-----------------------------------------------------------------------------------+
| invi.sp     | Purchase invoice with split payment / Fattura di acquisto con split-payment       |
+-------------+-----------------------------------------------------------------------------------+
| invi.rc     | Purchase invoice with reverse charge / Fattura di acquisto con reverse charge     |
+-------------+-----------------------------------------------------------------------------------+
| invi.eu     | Purchase invoice from EU partner / Fattura di acquisto intraUE                    |
+-------------+-----------------------------------------------------------------------------------+
| invi.xeu    | Purchase invoice fromxEU partner / Fattura di acquisto extraUE                    |
+-------------+-----------------------------------------------------------------------------------+
| invi.li     | Purchase invoice with lettera di intento / Fattura di acquisto lettera di intento |
+-------------+-----------------------------------------------------------------------------------+
| invi.wht    | Purchase invoice with withholding / Fattura da fornitore con ritenuta d'acconto   |
+-------------+-----------------------------------------------------------------------------------+
| invi.enas   | Purchase invoice with enasarco / Fattura da fornitore con ensarco                 |
+-------------+-----------------------------------------------------------------------------------+
| einvo.ind   | E-invoice to individual / Fattura elettronica a privato                           |
+-------------+-----------------------------------------------------------------------------------+
| einvo.stamp | E-invoice with virtual stamp / Fattura elettronica con bollo virtuale             |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat3   | Sale invoice with vat 22% / Fattura di vendita con IVA 22%                        |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat2   | Sale invoice with vat 10% / Fattura di vendita con IVA 10%                        |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat1   | Sale invoice with vat 4% / Fattura di vendita con IVA 4%                          |
+-------------+-----------------------------------------------------------------------------------+
| invo.N1     | Sale invoice with out of vat / Fattura di vendita con FC art. 15                  |
+-------------+-----------------------------------------------------------------------------------+




partner qci
-----------

+----------------------+-------------------------------------+-------------------+----------------------------+
| id                   | name                                | side              | icq                        |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_1  | Prima Distribuzione S.p.A.          | customer/supplier | icq_0002 icq_0006 icq_pa11 |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_10 | Notaio Libero Jackson               | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_11 | Nebula Caffè S.p.A.                 | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_12 | Freie Universität Berlin            | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_13 | Axelor GmbH                         | customer          | icq_pa12                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_14 | SS Carrefur                         | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_15 | Ente Porto                          | customer          | icq_0002 icq_pa14 icq_pa16 |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_16 | Viking Office Depot Italia s.r.l.   | customer/supplier |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_17 | Vexor BV                            | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_2  | Agro Latte Due  s.n.c.              | customer          | icq_0002 icq_0007          |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_3  | Import Export Trifoglio s.r.l.      | customer          | icq_0001 icq_0006          |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_4  | Delta 4 s.r.l.                      | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_5  | Five Stars Hotel                    | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_6  | Esa Electronic S.p.A                | customer          | icq_0003                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_7  | Università della Svizzera Italiana  | customer          | icq_pa13                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_8  | Global Solution s.r.l.              | customer          | icq_pa15                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_9  | Mario Rossi                         | customer          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+




|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2020-08-27

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=master
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=0.2.3.13
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=0.2.3.13
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.13/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.13
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/0.2.3.13/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/0.2.3.13/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.2.3.13/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/0.2.3.13
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
   :target: https://t.me/axitec_helpdesk


