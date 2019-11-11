
=================================
maintainer-quality-tools 0.2.2.41
=================================



|Maturity| |Build Status| |Coverage Status| |license gpl|


.. contents::


Overview
========

[![Build Status](https://travis-ci.org/OCA/maintainer-quality-tools.svg)](https://travis-ci.org/OCA/maintainer-quality-tools)
[![Coverage Status](https://coveralls.io/repos/OCA/maintainer-quality-tools/badge.svg)](https://coveralls.io/r/OCA/maintainer-quality-tools)

QA Tools for Odoo maintainers (MQT)
===================================

The goal of Maintainer Quality Tools (MQT) is to provide helpers to ensure the quality of Odoo addons.

Differences between this Zeroincombenze® MQT and standard OCA version:

* Zeroincombenze® MQT can also test Odoo 6.1 and 7.0; OCA MQT fails with these versions
* Zeroincombenze® MQT is designed to run in local environment too, using [local travis emulator](https://github.com/zeroincombenze/tools/tree/master/travis_emulator)
* Zeroincombenze® MQT is designed to execute some debug statements (see below *MQT debug informations*)
* Zeroincombenze® MQT can run with reduced set of pylint tests (see below *LINT_CHECK_LEVEL*)
* Zeroincombenze® MQT can run with reduced set of Odoo tests (see below *ODOO_TEST_SELECT*)
* OCA MQT is the only component to build environment and test Odoo. Zeroincombenze® MQT is part of [Zeroincombenze® tools](https://github.com/zeroincombenze/tools)
* As per prior rule, building test environment is made by clodoo and lisa tools. These commands can also build a complete Odoo environment out of the box.

Note you can execute OCA MQT if you prefer, setting follow statement in .travis.yml file:

    export MQT_TEST_MODE=oca


Sample travis configuration file
--------------------------------

In order to setup TravisCI continuous integration for your project, just copy the
content of the [`/sample_files`](https://github.com/zeroincombenze/tools/tree/master/maintainer-quality-tools/sample_files)
to your project’s root directory.

If your project depends on other OCA or other Github repositories, create a file called `oca_dependencies.txt` at the root of your project and list the dependencies there. One per line like so:

    project_name optional_repository_url optional_branch_name

During testbed setup, MQT will automatically download and place these repositories accordingly into the addon path.
Note on addons path ordering: They will be placed after your own repo, but before the odoo core repo.

Warning: if missed optional_repository_url, OCA MQT loads OCA repository while Zeroincombenze® MQT searches for repository with the same owner of tested project.


Check your .travis file for syntax issues.
------------------------------------------

The [lint checker](http://lint.travis-ci.org/) of travis is off-line.

If you downloaded [Zeroincombenze® tools](https://github.com/zeroincombenze/tools), you can create .travis.yml using `topep8` command.


Multiple values for environment variable VERSION
------------------------------------------------

You can use branch or pull request into environment variable VERSION:

- Branch 10.0
```
    VERSION="10.0" ODOO_REPO="odoo/odoo"
```

- Pull request odoo/odoo#143
```
    VERSION="pull/143" ODOO_REPO="odoo/odoo"
```


Using custom branch inside odoo repository using ODOO_BRANCH
------------------------------------------------------------

You can use the custom branch into the ODOO_REPO using the environment variable ODOO_BRANCH:


- Branch saas-17
```
  ODOO_REPO="odoo/odoo" ODOO_BRANCH="saas-17"
```


Module unit tests
-----------------

MQT is also capable to test each module individually.
The intention is to check if all dependencies are correctly defined.
Activate it through the `UNIT_TEST` directive.
An additional line should be added to the `env:` section,
similar to this one:

    - VERSION="8.0" UNIT_TEST="1"


Coveralls/Codecov configuration file
------------------------------------

[Coveralls](https://coveralls.io/) and [Codecov](https://codecov.io/) services provide information on the test coverage of your modules.
Currently both configurations are automatic (check default configuration [here](cfg/.coveragerc)).
So, as of today, you don't need to include a `.coveragerc` into the repository,
If you do it, it will be simply ignored.

**NOTE:** the current configuration automatically ignores `*_example` modules
from coverage check.
See [maintainer-tools CONTRIBUTING doc](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md#tests) for further info on tests.


Names used for the test databases
---------------------------------

MQT has a nice feature of organizing your testing databases.
You might want to do that if you want to double them up as 
staging DBs or if you want to work with an advanced set of
templates in order to speed up your CI pipeline.
Just specify at will:
`MQT_TEMPLATE_DB='mqt_odoo_template' MQT_TEST_DB='mqt_odoo_test'`.
Give us feedback on you experiences, and if you could share findings
from your use case, there might be some grateful people arround.


Isolated pylint+flake8 checks
-----------------------------
If you want to make a build exclusive for these checks, you can add a line
on the `env:` section of the .travis.yml file with this content:

    - VERSION="7.0" LINT_CHECK="1"

You will get a faster answer about these questions and also a fast view over
semaphore icons in Travis build view.

To avoid making again these checks on other builds, you have to add
LINT_CHECK="0" variable on the line:

    - VERSION="7.0" ODOO_REPO="odoo/odoo" LINT_CHECK="0"


Reduced set of check
--------------------

You can execute reduced set of check, in order to gradually evolve your code quality
when you meet too many errors.

To enable reduced set of check add one of follow lines:

    - LINT_CHECK="1" LINT_CHECK_LEVEL="MINIMAL"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="REDUCED"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="AVERAGE"
    - LINT_CHECK="1" LINT_CHECK_LEVEL="NEARBY"

Look at follow table to understand which tests are disabled at specific level:

FLAKE8 (see http://flake8.pycqa.org/en/latest/user/error-codes.html for deatils)

Test | MINIMAL | REDUCED | AVERAGE | NEARBY | OCA | Note
-----|---------|---------|---------|--------|-----|------
E121 | :x:     | :x:     |         |        | :x: | [continuation line under-indented for hanging indent](https://lintlyci.github.io/Flake8Rules/rules/E121.html)
E123 | :x:     | :x:     |         |        | :x: | [Closing bracket does not match indentation of opening bracket's line](https://lintlyci.github.io/Flake8Rules/rules/E123.html)
E124 | :x:     | :x:     |         |        | :white_check_mark: | [Closing bracket does not match visual indentation](https://lintlyci.github.io/Flake8Rules/rules/E124.html)
E126 | :x:     | :x:     |         |        | :white_check_mark: | [Continuation line over-indented for hanging indent](https://lintlyci.github.io/Flake8Rules/rules/E126.html)
E127 | :x:     | :x:     |         |        | :white_check_mark: | [continuation line over-indented for visual indent](https://lintlyci.github.io/Flake8Rules/rules/E127.html)
E128 | :x:     | :x:     |         |        | :white_check_mark: | [Continuation line under-indented for visual indent](https://lintlyci.github.io/Flake8Rules/rules/E128.html)
E131 | :x:     | :x:     |         |        | :x: | [continuation line unaligned for hanging indent](https://lintlyci.github.io/Flake8Rules/rules/E131.html)
E133 | :x:     | :x:     |         |        | :x: | [Closing bracket is missing indentation](https://lintlyci.github.io/Flake8Rules/rules/E133.html)
E201 | :x:     | :white_check_mark: |         |        | :white_check_mark: | [Whitespace after '('](https://lintlyci.github.io/Flake8Rules/rules/E201.html)
E202 | :x:     | :white_check_mark: |         |        | :white_check_mark: | [Whitespace before ')'](https://lintlyci.github.io/Flake8Rules/rules/E202.html)
E203 | :x:     | :white_check_mark: |         |        | :white_check_mark: | [Whitespace before ':'](https://lintlyci.github.io/Flake8Rules/rules/E203.html)
E211 | :x:     | :white_check_mark: |         |        | :white_check_mark: | [whitespace before '('](https://lintlyci.github.io/Flake8Rules/rules/E211.html)
E221 | :x:     | :white_check_mark: |         |        | :white_check_mark: | [Multiple spaces before operator](https://lintlyci.github.io/Flake8Rules/rules/E221.html)
E222 | :x:     | :x:     |         |        | :white_check_mark: |
E225 | :x:     | :x:     |         |        | :white_check_mark: |
E226 | :x:     | :x:     |         |        | :x: |
E231 | :x:     | :x:     |         |        | :white_check_mark: |
E241 | :x:     | :x:     |         |        | :x: |
E242 | :x:     | :x:     |         |        | :x: |
E251 | :x:     | :x:     |         |        | :white_check_mark: |
E261 | :x:     | :x:     |         |        | :white_check_mark: |
E262 | :x:     | :x:     |         |        | :white_check_mark: |
E265 | :x:     | :x:     |         |        | :white_check_mark: |
E266 | :x:     | :x:     |         |        | :white_check_mark: | [too many leading '#' for block comment](https://lintlyci.github.io/Flake8Rules/rules/E266.html)
E271 | :x:     | :x:     |         |        | :white_check_mark: | [multiple spaces after keyword](https://lintlyci.github.io/Flake8Rules/rules/E271.html)
E272 | :x:     | :x:     |         |        | :white_check_mark: | [multiple spaces before keyword](https://lintlyci.github.io/Flake8Rules/rules/E272.html)
W291 | :x:     | :x:     |         |        | :white_check_mark: |
W292 | :x:     | :x:     |         |        | :white_check_mark: | [no newline at end of file](https://lintlyci.github.io/Flake8Rules/rules/W292.html)
W293 | :x:     | :x:     |         |        | :white_check_mark: |
E301 | :x:     | :x:     |         |        | :white_check_mark: | [Expected 1 blank line][https://lintlyci.github.io/Flake8Rules/rules/E301.html)
E302 | :x:     | :x:     |         |        | :white_check_mark: | No __init__.py
E303 | :x:     | :x:     |         |        | :white_check_mark: |
E305 | :x:     | :x:     |         |        | :white_check_mark: |
W391 | :x:     | :white_check_mark: |         |        | :white_check_mark: | blank line at end of file
F401 | :x:     | :white_check_mark: |         |        | :x: | module imported but unused
E501 | :x:     | :x:     |         |        | :white_check_mark: |
E502 | :x:     | :x:     |         |        | :white_check_mark: | [the backslash is redundant between brackets](https://lintlyci.github.io/Flake8Rules/rules/E502.html)
W503 | :x:     | :x:     |         |        | :x: | No __init__.py
W504 | :x:     | :x:     |         |        | :x: | No __init__.py
F601 | :x:     | :x:     |         |        | :x: | dictionary key name repeated with different values
E701 | :x:     | :x:     |         |        | :white_check_mark: | multiple statements on one line (colon)
E722 | :x:     | :x:     |         |        | :white_check_mark: | do not use bare except
F811 | :x:     | :x:     |         |        | :x: | redefinition of unused name from line N (No __init__.py)
F841 | :x:     | :x:     |         |        | :x: | [local variable 'context' is assigned to but never used](https://lintlyci.github.io/Flake8Rules/rules/F841.html)


PYLINT (see http://pylint-messages.wikidot.com/all-codes for details)

Test  | MINIMAL | REDUCED | AVERAGE | NEARBY | OCA | Notes
------|---------|---------|---------|--------|-----|------
W0101 | :x:     |         |         |        | :white_check_mark: | [unreachable](http://pylint-messages.wikidot.com/messages:w0101)
W0312 | :white_check_mark: |        |        |     | :white_check_mark: | [wrong-tabs-instead-of-spaces](http://pylint-messages.wikidot.com/messages:w0312)
W0403 | :white_check_mark: |        |        |     | :white_check_mark: | relative-import
W1401 | :x:     | :white_check_mark: |         |        | :white_check_mark: | anomalous-backslash-in-string
E7901 | :white_check_mark: |        |        |     | :white_check_mark: | [rst-syntax-error](https://pypi.org/project/pylint-odoo/1.4.0)
C7902 | :x:     | :white_check_mark: |         |        | :white_check_mark: | missing-readme
W7903 | :x:     |         |         |        | :white_check_mark: | javascript-lint
W7908 | :white_check_mark: |        |        |     | :white_check_mark: | missing-newline-extrafiles
W7909 | :x:     |         |         |        | :white_check_mark: | redundant-modulename-xml
W7910 | :x:     | :white_check_mark: |         |        | :white_check_mark: | wrong-tabs-instead-of-spaces
W7930 | :x:     |         |         |        | :white_check_mark: | [file-not-used](https://pypi.org/project/pylint-odoo/1.4.0)
W7935 | :x:     |         |         |        | :white_check_mark: | missing-import-error
W7950 | :x:     |         |         |        | :white_check_mark: | odoo-addons-relative-import
C8103 | :x:     |         |         |        | :white_check_mark: | [manifest-deprecated-key](https://pypi.org/project/pylint-odoo/1.4.0)
C8104 | :x:     |         |         |        | :white_check_mark: | [class-camelcase](https://pypi.org/project/pylint-odoo/1.4.0)
W8104 | :x:     |         |         |        | :white_check_mark: | api-one-deprecated
C8105 | :x:     |         |         |        | :white_check_mark: | [license-allowed](https://pypi.org/project/pylint-odoo/1.4.0)
C8108 | :x:     |         |         |        | :white_check_mark: | method-compute
R8110 | :x:     |         |         |        | :white_check_mark: | old-api7-method-defined
W8202 | :x:     |         |         |        | :white_check_mark: | use-vim-comment
N/A   | :x:     |         |         |        | :white_check_mark: | sql-injection
N/A   | :x:     |         |         |        | :white_check_mark: | duplicate-id-csv
N/A   | :x:     |         |         |        | :white_check_mark: | create-user-wo-reset-password
N/A   | :x:     |         |         |        | :white_check_mark: | dangerous-view-replace-wo-priority
N/A   | :x:     |         |         |        | :white_check_mark: | translation-required
N/A   | :x:     |         |         |        | :white_check_mark: | duplicate-xml-record-id
N/A   | :x:     |         |         |        | :white_check_mark: | no-utf8-coding-comment
N/A   | :x:     |         |         |        | :white_check_mark: | attribute-deprecated
N/A   | :x:     |         |         |        | :white_check_mark: | consider-merging-classes-inherited



Reduced set of modules test
---------------------------

Last Odoo packages may fail in Travis CI or in local environment.
Currently Odoo OCB core tests fail; we are investigating for causes.
OCA workaround is following example statement:
`export INCLUDE=$(getaddons.py -m --only-applications ${TRAVIS_BUILD_DIR}/odoo/addons ${TRAVIS_BUILD_DIR}/addons)`

You can execute reduced set of tests adding one of follow lines:

    - TESTS="1" ODOO_TEST_SELECT="ALL"
    - TESTS="1" ODOO_TEST_SELECT="NO-CORE"
    ....

Look at follow table to understand which set of tests are enabled or disabled:

   statement     |    application     | module l10n_*      |    odoo/addons     | addons + dependencies
-----------------|--------------------|--------------------|--------------------|-----------------------
     ALL         | :white_check_mark: | :white_check_mark: | :white_check_mark: |  :white_check_mark:
  APPLICATIONS   | :white_check_mark: | :x:                | :x:                |  Only if application
  LOCALIZATION   | :x:                | :white_check_mark: | :x:                |  Only module l10n_*
     CORE        | :x:                | :x:                | :white_check_mark: |  :x:
 NO-APPLICATION  | :x:                | :white_check_mark: | :white_check_mark: |  No if application
 NO-LOCALIZATION | :white_check_mark: | :x:                | :white_check_mark: |  No if module l10n_*
   NO-CORE       | :white_check_mark: | :white_check_mark: | :x:                |  :white_check_mark:


Disable test
------------

If you want to make a build without tests, you can use the following directive:
`TEST_ENABLE="0"`

You will simply get the databases with packages installed, 
but without running any tests.


Other configurations
--------------------

You can highly customize you test: look at below table.

 variable               | default value | meaning
------------------------|---------------|--------------------------------------------------------------
 DATA_DIR               | ~/data_dir    | Odoo data directory (data_dir in config file)
 EXCLUDE                |               | Modules to exclude from test
 INCLUDE                |               | Modules to test (all, if empty)
 INSTALL_OPTIONS        |               | Options passed to odoo-bin/openerp-server to install modules
 MQT_TEMPLATE_DB        |               | Read above
 MQT_TEST_DB            |               | Read above
 ODOO_REPO              | odoo/odoo     | OCB repository against test repository
 ODOO_TEST_SELECT       | ALL           | Read above
 ODOO_TNLBOT            | 0             | No yet documented
 OPTIONS                |               | Options passed to odoo-bin/openerp-server to execute tests
 SERVER_EXPECTED_ERRORS |               | # of expected errors after tests
 TRAVIS_DEBUG_MODE      | 0             | Read above
 UNBUFFER               | True          | Use unbuffer (colors) to log results
 UNIT_TEST              |               | Read above
 TEST                   |               | Read above
 VERSION                |               | Odoo version to test (see above)
 WKHTMLTOPDF_VERSION    | 0.12.4        | Version of wkhtmltopdf (value are 0.12.1 and 0.12.5)


MQT debug informations
----------------------

If you declare the following directive in <env global> section:
`TRAVIS_DEBUG_MODE="1"`

enable debug mode execution during local session of test.
Note this feature does not work with OCA MQT. Local test and TravisCI test have slightly different behavior.

When MQT is execute in local environment the value
`TRAVIS_DEBUG_MODE="2"`

does not execute unit test. It is used to debug MQT itself.

See [local travis emulator](https://github.com/zeroincombenze/tools/tree/master/travis_emulator)


Some differences between MQTs
-----------------------------

Zeroincombenze® MQT and standard MQT OCA have some different behaviour;
see following sections documentation:

Zeroincombenze® OCB use submodules. When test in starting, submodules should not be upgraded.
Use this statements:
`- git:`
`  submodules: false`

OCA does not use before_install section. Zeroincombenze® MQT requires before_install section like this:
`before_install:`
`  - export TRAVIS_DEBUG_MODE="1"`

Zeroincombenze® MQT set security environment. You have not to add security statements
(with OCA MQT you must remove comment):
`#  - pip install urllib3[secure] --upgrade; true`

Zeroincombenze® MQT do some code upgrade; using OCA MQT you must do these code by .travis.yml.
When ODOO_TEST_SELECT="APPLICATIONS":
`# sed -i "s/self.url_open(url)/self.url_open(url, timeout=100)/g" ${TRAVIS_BUILD_DIR}/addons/website/tests/test_crawl.py;`
When ODOO_TEST_SELECT="LOCALIZATION":
`# sed -i "/'_auto_install_l10n'/d" ${TRAVIS_BUILD_DIR}/addons/account/__manifest__.py`


Tree directory
--------------

While travis is running this is the tree directory:

    ${HOME}
    |
    \___ build (by TravisCI)
    |    |
    |    \___ ${TRAVIS_BUILD_DIR}  (by TravisCI}
    |    |    # github tested project
    |    |
    |    \___ ${ODOO_REPO} (by travis_install_env / travis_install_nightly of .travis.yml)
    |         # same behavior of OCA MQT (2)
    |         # travis_install_env ignore this value, if OCB tested
    |         # Odoo or OCA/OCB to check compatibility of tested project
    |
    \___ maintainer-quality-tools (by .travis.yml) (1)
    |    # same behavior of OCA MQT
    |    # moved from ${HOME}/tools/maintainer-quality-tools
    |    |
    |    \___ travis (child of maintainer-quality-tools), in PATH
    |
    \___ ${ODOO_REPO}-${VERSION} (by .travis.yml)
    |    # same behavior of OCA MQT
    |    # symlnk of ${HOME}/build/{ODOO_REPO}
    |    # Odoo or OCA repository to check with
    |
    \___ dependencies (by travis_install_env / travis_install_nightly of .travis.yml)
    |    # Odoo dependencies (2)
    |
    \___ tools (by .travis.yml)   # clone of this project
         |
         \___ maintainer-quality-tools (child of tools)
              # moved to ${HOME}/maintainer-quality-tools 

    (1) Done by .travis.yml in before install section with following statements:
        - git clone https://github.com/zeroincombenze/tools.git ${HOME}/tools --depth=1
        - mv ${HOME}/tools/maintainer-quality-tools ${HOME}
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}
        Above statements replace OCA statements:
        - git clone https://github.com/OCA/maintainer-quality-tools.git ${HOME}/maintainer-quality-tools --depth=1
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}

    (2) Done by .travis.yml in install section with following statements:
        - travis_install_env
        Above statements replace OCA statements:
        - travis_install_nightly
        You can create OCA environment using travis_install_nightly with follow stattements:
        - export MQT_TEST_MODE=oca
        - travis_install_env
        Or else
        - travis_install_env oca


|
|

Quick start
===========


|

Installation
------------


Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/dev/activate_tools

|
|

Get involved
============

|
|

Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Contributors
------------

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>

|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2019-11-11

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alfa
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=.
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=.
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=.
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/./graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/.
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-0.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/./dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-0.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/./man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-0.svg
    :target: https://erp0.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/./graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/.
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
   :target: https://tawk.to/85d4f6e06e68dd4e358797643fe5ee67540e408b

