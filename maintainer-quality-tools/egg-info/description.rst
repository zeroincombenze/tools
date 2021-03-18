QA Tools for Odoo maintainers (MQT)
===================================

The goal of Maintainer Quality Tools (MQT) is to provide helpers to ensure the quality of Odoo addons.

Differences between this Zeroincombenze® MQT and standard OCA version:

* Zeroincombenze® MQT can also test Odoo 6.1 and 7.0; OCA MQT fails with these versions
* Zeroincombenze® MQT is designed to run in local environment too, using `local travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_
* Zeroincombenze® MQT is designed to execute some debug statements (see below *MQT debug informations*)
* Zeroincombenze® MQT can run with reduced set of pylint tests (see below *LINT_CHECK_LEVEL*)
* Zeroincombenze® MQT can run with reduced set of Odoo tests (see below *ODOO_TEST_SELECT*)
* OCA MQT is the only component to build environment and test Odoo. Zeroincombenze® MQT is part of `Zeroincombenze® tools <https://github.com/zeroincombenze/tools>`_
* As per prior rule, building test environment is made by clodoo and lisa tools. These commands can also build a complete Odoo environment out of the box.

Note you can execute OCA MQT if you prefer, setting follow statement in .travis.yml file:

    export MQT_TEST_MODE=oca


Sample travis configuration file
--------------------------------

In order to setup TravisCI continuous integration for your project, just copy the
content of the `sample_files <https://github.com/zeroincombenze/tools/tree/master/maintainer-quality-tools/sample_files>`_
to your project’s root directory.

If your project depends on other OCA or other Github repositories, create a file called `oca_dependencies.txt` at the root of your project and list the dependencies there. One per line like so:

    project_name optional_repository_url optional_branch_name

During testbed setup, MQT will automatically download and place these repositories accordingly into the addon path.
Note on addons path ordering: They will be placed after your own repo, but before the odoo core repo.

Warning: if missed optional_repository_url, OCA MQT loads OCA repository while Zeroincombenze® MQT searches for repository with the same owner of tested project.


Check your .travis file for syntax issues.
------------------------------------------

The `lint checker <http://lint.travis-ci.org/>`_ of travis is off-line.

If you downloaded `Zeroincombenze® tools <https://github.com/zeroincombenze/tools>`_, you can create .travis.yml using `topep8` command.


Multiple values for environment variable VERSION
------------------------------------------------

You can use branch or pull request into environment variable VERSION:

    Branch 10.0

    \- VERSION="10.0" ODOO_REPO="odoo/odoo"

    Pull request odoo/odoo#143

    \-  VERSION="pull/143" ODOO_REPO="odoo/odoo"



Using custom branch inside odoo repository using ODOO_BRANCH
------------------------------------------------------------

You can use the custom branch into the ODOO_REPO using the environment variable ODOO_BRANCH:

    Branch saas-17

    \- ODOO_REPO="odoo/odoo" ODOO_BRANCH="saas-17"



Module unit tests
-----------------

MQT is also capable to test each module individually.
The intention is to check if all dependencies are correctly defined.
Activate it through the `UNIT_TEST` directive.
An additional line should be added to the `env:` section,
similar to this one:

    \- VERSION="8.0" UNIT_TEST="1"


Coveralls/Codecov configuration file
------------------------------------

`Coveralls <https://coveralls.io/>`_ and `Codecov <https://codecov.io/>`_ services provide information on the test coverage of your modules.
Currently both configurations are automatic (check default configuration `here <cfg/.coveragerc>`_.
So, as of today, you don't need to include a `.coveragerc` into the repository,
If you do it, it will be simply ignored.

**NOTE:** the current configuration automatically ignores `*_example` modules
from coverage check.
See `maintainer-tools CONTRIBUTING doc <https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md#tests>`_ for further info on tests.


Names used for the test databases
---------------------------------

MQT has a nice feature of organizing your testing databases.
You might want to do that if you want to double them up as 
staging DBs or if you want to work with an advanced set of
templates in order to speed up your CI pipeline.
Just specify at will:

`MQT_TEMPLATE_DB='mqt_odoo_template' MQT_TEST_DB='mqt_odoo_test'`.

Give us feedback on you experiences, and if you could share findings
from your use case, there might be some grateful people around.


Isolated pylint+flake8 checks
-----------------------------
If you want to make a build exclusive for these checks, you can add a line
on the `env:` section of the .travis.yml file with this content:

    \- VERSION="7.0" LINT_CHECK="1"

You will get a faster answer about these questions and also a fast view over
semaphore icons in Travis build view.

To avoid making again these checks on other builds, you have to add
LINT_CHECK="0" variable on the line:

    \- VERSION="7.0" ODOO_REPO="odoo/odoo" LINT_CHECK="0"


Reduced set of check
--------------------

You can execute reduced set of check, in order to gradually evolve your code quality
when you meet too many errors.

To enable reduced set of check add one of follow lines:

    \- LINT_CHECK="1" LINT_CHECK_LEVEL="MINIMAL"
    \- LINT_CHECK="1" LINT_CHECK_LEVEL="REDUCED"
    \- LINT_CHECK="1" LINT_CHECK_LEVEL="AVERAGE"
    \- LINT_CHECK="1" LINT_CHECK_LEVEL="NEARBY"

Look at follow table to understand which tests are disabled at specific level:

FLAKE8 (see http://flake8.pycqa.org/en/latest/user/error-codes.html for deatils)

.. $include flake8_error.csv


PYLINT (see http://pylint-messages.wikidot.com/all-codes for details)

.. $include pylint_error.csv


Reduced set of modules test
---------------------------

Last Odoo packages may fail in Travis CI or in local environment.
Currently Odoo OCB core tests fail; we are investigating for causes.
OCA workaround is following example statement:
`export INCLUDE=$(getaddons.py -m --only-applications ${TRAVIS_BUILD_DIR}/odoo/addons ${TRAVIS_BUILD_DIR}/addons)`

You can execute reduced set of tests adding one of follow lines:

    - TESTS="1" ODOO_TEST_SELECT="ALL"
    - TESTS="1" ODOO_TEST_SELECT="NO-CORE"
    - \....

Look at follow table to understand which set of tests are enabled or disabled:

.. $include test_level.csv


Disable pylint and/or flake8 checks
-----------------------------------

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

`self._cr.execute(      # pylint: disable=E8103`



Disable test
------------

If you want to make a build without tests, you can use the following directive:
`TEST_ENABLE="0"`

You will simply get the databases with packages installed, 
but without running any tests.


Other configurations
--------------------

You can highly customize you test: look at below table.

.. $include variables.csv



MQT debug informations
----------------------

If you declare the following directive in <env global> section:
`TRAVIS_DEBUG_MODE="n"`

where "n" means:

.. $include level_summary.csv

Note this feature does not work with OCA MQT. Local test and TravisCI test have slightly different behavior.

When MQT is execute in local environment the value
`TRAVIS_DEBUG_MODE="9"`

does not execute unit test. It is used to debug MQT itself.

See `local travis emulator <https://github.com/zeroincombenze/tools/tree/master/travis_emulator>`_


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

