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
* OCA MQT is the only component to build environment and test Odoo. Zeroincombenze® MQT is part of [Zeroincombenze® tools](https://github.com/zeroincombenze/tools)
* As per prior rule, building test environment is made by clodoo and lisa tools. These commands can also build a complete Odoo environment out of the box.

Note you can execute OCA MQT if you prefer, setting follow statement in .travis.yml file:

    export MQT_TEST_MODE=oca


Sample travis configuration file (for version 7.0)
--------------------------------------------------

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
E123 | :x:     |         |         |        | :x: | [Closing bracket does not match indentation of opening bracket's line](https://lintlyci.github.io/Flake8Rules/rules/E123.html)
E128 | :x:     |         |         |        | :white_check_mark: | [Continuation line under-indented for visual indent](https://lintlyci.github.io/Flake8Rules/rules/E128.html)
E133 | :x:     |         |         |        | :x: | [Closing bracket is missing indentation](https://lintlyci.github.io/Flake8Rules/rules/E133.html)
E201 | :x:     |         |         |        | :white_check_mark: | [Whitespace after '('](https://lintlyci.github.io/Flake8Rules/rules/E201.html)
E202 | :x:     |         |         |        | :white_check_mark: | [Whitespace before ')'](https://lintlyci.github.io/Flake8Rules/rules/E202.html)
E203 | :x:     |         |         |        | :white_check_mark: | [Whitespace before ':'](https://lintlyci.github.io/Flake8Rules/rules/E203.html)
E221 | :x:     |         |         |        | :white_check_mark: | [Multiple spaces before operator](https://lintlyci.github.io/Flake8Rules/rules/E221.html)
E222 | :x:     |         |         |        | :white_check_mark: |
E225 | :x:     |         |         |        | :white_check_mark: |
E226 | :x:     |         |         |        | :x: |
E231 | :x:     |         |         |        | :white_check_mark: |
E241 | :x:     |         |         |        | :x: |
E242 | :x:     |         |         |        | :x: |
E251 | :x:     |         |         |        | :white_check_mark: |
E261 | :x:     |         |         |        | :white_check_mark: |
E262 | :x:     |         |         |        | :white_check_mark: |
E265 | :x:     |         |         |        | :white_check_mark: |
E266 | :x:     |         |         |        | :white_check_mark: | [too many leading '#' for block comment](https://lintlyci.github.io/Flake8Rules/rules/E266.html)
W291 | :x:     |         |         |        | :white_check_mark: |
W293 | :x:     |         |         |        | :white_check_mark: |
E302 | :x:     |         |         |        | :white_check_mark: | No __init__.py
E303 | :x:     |         |         |        | :white_check_mark: |
E305 | :x:     |         |         |        | :white_check_mark: |
F401 | :x:     |         |         |        | :white_check_mark: | module imported but unused
E501 | :x:     |         |         |        | :white_check_mark: |
W503 | :x:     |         |         |        | :x: | No __init__.py
W504 | :x:     |         |         |        | :x: | No __init__.py
F601 | :x:     |         |         |        | :x: | dictionary key name repeated with different values
F811 | :x:     |         |         |        | :x: | redefinition of unused name from line N (No __init__.py)



PYLINT (see http://pylint-messages.wikidot.com/all-codes for details)

Test  | MINIMAL | REDUCED | AVERAGE | NEARBY | OCA | Notes
------|---------|---------|---------|--------|-----|------
W0101 | :x:     |         |         |        | :white_check_mark: | [unreachable](http://pylint-messages.wikidot.com/messages:w0101)
W0312 | :white_check_mark: |        |        |     | :white_check_mark: | [wrong-tabs-instead-of-spaces](http://pylint-messages.wikidot.com/messages:w0312)
W0403 | :white_check_mark: |        |        |     | :white_check_mark: | relative-import
W1401 | :white_check_mark: |        |        |     | :white_check_mark: | anomalous-backslash-in-string
E7901 | :white_check_mark: |        |        |     | :white_check_mark: | [rst-syntax-error](https://pypi.org/project/pylint-odoo/1.4.0)
C7902 | :x:     |         |         |        | :white_check_mark: | missing-readme
W7903 | :x:     |         |         |        | :white_check_mark: | javascript-lint
W7908 | :white_check_mark: |        |        |     | :white_check_mark: | missing-newline-extrafiles
W7930 | :x:     |         |         |        | :white_check_mark: | [file-not-used](https://pypi.org/project/pylint-odoo/1.4.0)
W7935 | :x:     |         |         |        | :white_check_mark: | missing-import-error
C8103 | :x:     |         |         |        | :white_check_mark: | [manifest-deprecated-key](https://pypi.org/project/pylint-odoo/1.4.0)
C8104 | :x:     |         |         |        | :white_check_mark: | [class-camelcase](https://pypi.org/project/pylint-odoo/1.4.0)
C8105 | :x:     |         |         |        | :white_check_mark: | [license-allowed](https://pypi.org/project/pylint-odoo/1.4.0)
W8104 | :x:     |         |         |        | :white_check_mark: | api-one-deprecated
R8110 | :x:     |         |         |        | :white_check_mark: | old-api7-method-defined
N/A   | :x:     |         |         |        | :white_check_mark: | sql-injection
N/A   | :x:     |         |         |        | :white_check_mark: | duplicate-id-csv
N/A   | :x:     |         |         |        | :white_check_mark: | create-user-wo-reset-password
N/A   | :x:     |         |         |        | :white_check_mark: | dangerous-view-replace-wo-priority
N/A   | :x:     |         |         |        | :white_check_mark: | translation-required
N/A   | :x:     |         |         |        | :white_check_mark: | duplicate-xml-record-id
N/A   | :x:     |         |         |        | :white_check_mark: | no-utf8-coding-comment
N/A   | :x:     |         |         |        | :white_check_mark: | attribute-deprecated
N/A   | :x:     |         |         |        | :white_check_mark: | consider-merging-classes-inherited



Disable test
------------
If you want to make a build without tests, you can use the following directive:
`TEST_ENABLE="0"`

You will simply get the databases with packages installed, 
but whithout running any tests.


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
