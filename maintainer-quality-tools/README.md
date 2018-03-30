[![Build Status](https://travis-ci.org/OCA/maintainer-quality-tools.svg)](https://travis-ci.org/OCA/maintainer-quality-tools)
[![Coverage Status](https://coveralls.io/repos/OCA/maintainer-quality-tools/badge.svg)](https://coveralls.io/r/OCA/maintainer-quality-tools)

QA Tools for Odoo maintainers (MQT)
===================================

The goal of Maintainer Quality Tools (MQT) is to provide helpers to ensure the quality of Odoo addons.

Differences between this Zeroincombenze® MQT and standard OCA version:

* Zeroincombenze® MQT can aldo test Odoo 6.1 and 7.0; OCA version fails with these versions
* Zeroincombenze® MQT is designed to run in local environment too, using [local travis emulator](https://github.com/zeroincombenze/tools/tree/master/travis_emulator)
* Zeroincombenze® MQT is designed to execute some debug statements (see below *MQT debug informations*)
* OCA MQT is the only component to build environment and test Odoo. Zeroincombenze® MQT is part of [Zeroincombenze® tools](https://github.com/zeroincombenze/tools)


Sample travis configuration file (for version 7.0)
--------------------------------------------------

In order to setup TravisCI continuous integration for your project, just copy the
content of the [`/sample_files`](https://github.com/zeroincombenze/tools/tree/master/maintainer-quality-tools/sample_files)
to your project’s root directory.

If your project depends on other OCA or other Github repositories, create a file called `oca_dependencies.txt` at the root of your project and list the dependencies there. One per line like so:

    project_name optional_repository_url optional_branch_name

During testbed setup, MQT will automatically download and place these repositories accordingly into the addon path.
Note on addons path ordering: They will be placed after your own repo, but before the odoo core repo.

Check your .travis file for syntax issues.
------------------------------------------

The [lint checker](http://lint.travis-ci.org/) of travis is off-line.

If you downloaded [Zeroincombenze® tools](https://github.com/zeroincombenze/tools), you can parse .travis.yml using `topep8` command.


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
Note this feature is does not work with OCA MQT. Local test and TravisCI test slightly different behavior.

When MQT is execute in local environment the value
`TRAVIS_DEBUG_MODE="2"`

does not execute unit test. It is used to debug MQT itself.

See [local travis emulator](https://github.com/zeroincombenze/tools/tree/master/travis_emulator)

Tree directory
--------------

While travis is running this is the tree directory:

    ${HOME}
    |
    \___ build (by Travis CI)
    |    |
    |    \___ ${TRAVIS_BUILD_DIR}  (by Travis CI}
    |    |    # github tested project
    |    |
    |    \___ ${ODOO_REPO} (by travis_install_nightly of .travis.yml)
    |         # same of OCA .travis.yml
    |         # Odoo or OCA server to check tested project
    |
    \___ maintainer-quality-tools (by .travis.yml)
    |    # same of OCA .travis.yml
    |    # moved from ${HOME}/tools/maintainer-quality-tools
    |    |
    |    \___ travis (child of maintainer-quality-tools), in PATH
    |
    \___ ${ODOO_REPO}-${VERSION} (by .travis.yml)
    |    # same of OCA .travis.yml
    |    # symlnk of ${HOME}/build/{ODOO_REPO}
    |    # Odoo or OCA repository to check with
    |
    \___ dependencies (by travis_install_nightly of .travis.yml)
    |    # Odoo dependencies
    |
    \___ tools (by .travis.yml)   # clone of this project
         |
         \___ maintainer-quality-tools (child of tools)
              # moved to ${HOME}/maintainer-quality-tools 
