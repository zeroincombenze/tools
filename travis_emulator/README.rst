
=====================
travis_emulator 1.0.4
=====================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Emulate travis to test application before pushing to git
--------------------------------------------------------

Travis emulator can emulate TravisCi parsing the **.travis.yml** file in local Linux machine and it is osx/darwin compatible.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in **.travis.yml**; all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all builds created.
Please note that log file is a binary file with escape ANSI screen code.
If you want to see the log use one of following command:

    `travis show`

    `less -R ~/travis_log/<build_name>.log`

A travis build executes the following steps:

$include travis_phases.csv

Read furthermore info read `travis-ci phase <https://docs.travis-ci.com/user/job-lifecycle/>`__


Difference between local travis and web site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The travis emulator works mostly like TravisCi web site. However you ha to consider some points where you run local tests:

Local software is not published

    When you test on your local PC, the software is not yet publishd. Perhaps you prefer test
    local packages or local modules.
    The travis emulator with z0bug_odoo replace the commands `git clone` with local `ln -s` creating
    logical link with local repository, if possible.
    Local module are searched in the testing module directory. See Odoo structure for furthermore info.

Your PC is not TravisCi web site

    Probability you have just one python interpreter and your user is not sudo enabled.
    The travis emulator run build just with Odoo interpreter installed even if your
    .travis.yml file contains more python version to test.
    The travis emulator does not try to install global packages because
    it does not change the PC configuration.
    Please, install manually all the global packages using apt-get, yum, dnf or your local installer software.



|

Features
--------

+--------------------------------------+--------------------+--------------------------------------+
| Function                             | Status             | Note                                 |
+--------------------------------------+--------------------+--------------------------------------+
| Execute tests in virtual environment | |check|            | As TravisCI                          |
+--------------------------------------+--------------------+--------------------------------------+
| Python 2 test                        | |check|            | If installed in local machine        |
+--------------------------------------+--------------------+--------------------------------------+
| Python 3 test                        | |check|            | If installed in local machine        |
+--------------------------------------+--------------------+--------------------------------------+
| Bash test                            | |check|            | Using zerobug package                |
+--------------------------------------+--------------------+--------------------------------------+
| Matrix                               | |check|            | Test sequentialized                  |
+--------------------------------------+--------------------+--------------------------------------+
| Show coverage result                 | |check|            | If installed in local machine        |
+--------------------------------------+--------------------+--------------------------------------+
| Quality check                        | |check|            | With zerobug and z0bug_odoo packages |
+--------------------------------------+--------------------+--------------------------------------+
| Stored images                        | |check|            | In ~/VME/ directory (see -C switch)  |
+--------------------------------------+--------------------+--------------------------------------+
| Debug information                    | |check|            | See -B and -D switches               |
+--------------------------------------+--------------------+--------------------------------------+
| Keep DB after test                   | |check|            | See -k switch                        |
+--------------------------------------+--------------------+--------------------------------------+
| Lint level                           | |check|            | With zerobug, see -L switch          |
+--------------------------------------+--------------------+--------------------------------------+
| Build selection                      | |check|            | See -O switch                        |
+--------------------------------------+--------------------+--------------------------------------+
| System packages                      | |check| |no_check| | See -S switch                        |
+--------------------------------------+--------------------+--------------------------------------+
| Use specific python version          | |check|            | See -y switch                        |
+--------------------------------------+--------------------+--------------------------------------+


|

Usage
=====

Travis emulator usage
---------------------

::

    Usage: travis [-hBC][-c file][-D number][-dEFfjk][-L number][-l dir][-Mmn][-O git-org][-pqr][-S false|true][-Vv][-X 0|1][-Y file][-y pyver][-Z] action sub sub2
    Travis-ci emulator for local developer environment
    Action may be: [force-]lint, [force-]test, emulate (default), (new|chk|cp|mv|merge)_vm, chkconfig or parseyaml
     -h --help            this help
     -B --debug           debug mode: do not create log
     -C --no-cache        do not use stored PYPI
     -c --conf file
                          configuration file (def .travis.conf)
     -D --debug-level number
                          travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)
     -d --osx             emulate osx-darwin
     -E --no-savenv       do not save virtual environment into ~/VME/... if does not exist
     -F --full            run final travis with full features
     -f --force           force yaml to run w/o cmd subst
     -j                   execute tests in project dir rather in test dir (or expand macro if parseyaml)
     -k --keep            keep DB and virtual environment after tests
     -L --lint-level number
                          lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml
     -l --logdir dir
                          log directory (def=/home/antoniomaria/odoo/travis_log)
     -M                   use local MQT (deprecated)
     -m --missing         show missing line in report coverage
     -n --dry-run         do nothing (dry-run)
     -O --org git-org
                          git organization, i.e. oca or zeroincombenze
     -p --pytest          prefer python test over bash test when avaiable
     -q --quiet           silent mode
     -r                   run restricted mode (deprecated)
     -S --syspkg false|true
                          use python system packages (def yaml dependents)
     -V --version         show version
     -v --verbose         verbose mode
     -X 0|1               enable translation test (def yaml dependents)
     -Y --yaml-file file
                          file yaml to process (def .travis.yml)
     -y --pyver pyver
                          test with specific python versions (comma separated)
     -Z --zero            use local zero-tools


Tree directory
~~~~~~~~~~~~~~

While travis is running this is the tree directory:

::

    ${HOME}
    ┣━━ build                       # build root (by TravisCI)
    ┃    ┣━━ ${TRAVIS_BUILD_DIR}    # testing project repository (by TravisCI)
    ┃    ┗━━ ${ODOO_REPO}           # Odoo or OCA/OCB repository to check with    (1) (2)
    ┃
    ┣━━ ${ODOO_REPO}-${VERSION}     # symlnk of ${HOME}/build/{ODOO_REPO}         (1)
    ┃
    ┣━━ dependencies                # Odoo dependencies                           (3)
    ┃
    ┗━━ tools                       # clone of Zeroincombenze tools               (3) (4)
         ┃
         ┣━━ zerobug                # testing library
         ┃       ┗━━ _travis        # testing commands
         ┗━━ z0bug_odoo             # Odoo testing library
                 ┗━━ _travis        # testing commands

    (1) Directory with Odoo or OCA/OCB repository to check compatibility of testing project
    (2) If testing project is OCB, travis_install_env ignore this directory
    (3) Done by then following statements in .travis.yml:
        - travis_install_env
        Above statements replace the OCA statements:
        - travis_install_nightly
    (4) Done by following statements in .travis.yml::
        - git clone https://github.com/zeroincombenze/tools.git ${HOME}/tools --depth=1
        - \${HOME}/tools/install_tools.sh -qp
        - source ${HOME}/dev/activate_tools
        Above statements replace OCA following statements:
        - git clone https://github.com/OCA/maintainer-quality-tools.git ${HOME}/maintainer-quality-tools --depth=1
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}


Configuration file
~~~~~~~~~~~~~~~~~~

Values in configuration file are:

+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| Parameter         | Descriptio                                         | Default value                                                                                |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| CHAT_HOME         | URL to web chat to insert in documentation         |                                                                                              |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| ODOO_SETUPS       | Names of Odoo manifest files                       | __manifest__.py __openerp__.py __odoo__.py __terp__.py                                       |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| dbtemplate        | Default value for MQT_TEMPLATE_DB                  | openerp_template                                                                             |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| dbname            | Default value for MQT_TEST_DB                      | openerp_test                                                                                 |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| dbuser            | Postgresql user: default value for MQT_DBUSER      | $USER                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| UNBUFFER          | Use unbuffer                                       | 0                                                                                            |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| virtualenv_opts   | Default option to create virtual environment       |                                                                                              |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| NPM_CONFIG_PREFIX | N/D                                                | \$HOME/.npm-global                                                                           |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_TXT_COLOR      | N/D                                                | 0;97;40                                                                                      |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_RUN_COLOR      | N/D                                                | 1;37;44                                                                                      |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_NOP_COLOR      | N/D                                                | 31;100                                                                                       |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_HDR1_COLOR     | N/D                                                | 97;42                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_HDR2_COLOR     | N/D                                                | 30;43                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PS_HDR3_COLOR     | N/D                                                | 30;45                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PKGS_LIST         | N/D                                                | clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PYTHON_MATRIX     | Python version available to test (space separated) |                                                                                              |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+




|
|

Getting started
===============


|

Installation
------------

Installation
------------

Zeroincombenze tools require:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20
* python 2.7, some tools require python 3.6+
* bash 5.0+

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/devel/activate_tools


Upgrade
-------

Upgrade
-------

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


Troubleshooting
---------------

*Message "Denied inquire with psql [-U<name>]"*

    User <name> cannot execute psql command.
    Travis emulator cannot drop test database after build completation.
    Please configure postgresql and enable user <name> to use psql via shell.
    If user is not *odoo* declare username with following command:

    `please config global`

    and then set *dbuser* parameter value.


*Message "false;   # Warning! TODO> apt-get install <pkg>*

    The package <pkg> is not installed on your system.
    Travis emulator run at low security level and cannot install debian or rpm packages.
    Please install the package <pkg> via *apt-get* or *yum* or *dnf* based on your distro.
    You can use *lisa* to install package <pkg> on all distribution with following command:

    `lisa install <pkg>`


History
-------

1.0.3.3 (2021-11-10)
~~~~~~~~~~~~~~~~~~~~

* [FIX] travis: match python version limited to 2 levels

1.0.2.2 (2021-10-08)
~~~~~~~~~~~~~~~~~~~~

* [FIX] travis: crash if invalid Odoo project

1.0.2.1 (2021-09-25)
~~~~~~~~~~~~~~~~~~~~

* [IMP] travis: check for cached expired VME

1.0.2 (2021-08-27)
~~~~~~~~~~~~~~~~~~

* [IMP] travis: stable version

1.0.1.8 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~

* [IMP] travis: color change
* [IMP] travis: new action testdeps
* [FIX] travis: matrix selection
* [IMP] travis: switch -y forces python version

1.0.1.5 (2021-08-11)
~~~~~~~~~~~~~~~~~~~~

* [IMP] travis: summary return 1 if test failed or is broken
* [IMP] travis: return status like summary
* [IMP] travis: summary & show-log can show old logfile i.e.: travis summary old
* [IMP] travis: osx emulatore return more info when error

1.0.1.4 (2021-08-06)
~~~~~~~~~~~~~~~~~~~~

* [IMP] devel_tools replaced by wok_code
* [IMP] travis: summary return 1 if test failed

1.0.1.3 (2021-08-03)
~~~~~~~~~~~~~~~~~~~~

* [IMP] Show virtual enviroment name in summary

1.0.1.2 (2021-05-31)
~~~~~~~~~~~~~~~~~~~~

* [FIX] readlink error

1.0.1.1 (2021-05-24)
~~~~~~~~~~~~~~~~~~~~

* [IMP] Local travis full emulator

1.0.0.14 (2021-04-07)
~~~~~~~~~~~~~~~~~~~~~

* [IMP] Change message level showing

1.0.0.13 (2021-04-06)
~~~~~~~~~~~~~~~~~~~~~

* [IMP] travis: show stack execution



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
Last Update / Ultimo aggiornamento: 2021-08-31
.. |Maturity| image:: https://img.shields.io/badge/maturity-Mature-green.png
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
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-1.svg
:target: https://erp1.zeroincombenze.it
:alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/1.0/graph/badge.svg
:target: https://codecov.io/gh/OCA/tools/branch/1.0
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
:target: https://odoo-italia.org
:alt: Odoo Italia Associazione
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
:target: https://www.zeroincombenze.it/
:alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
:target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
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
Last Update / Ultimo aggiornamento: 2021-09-25
Last Update / Ultimo aggiornamento: 2021-09-26
Last Update / Ultimo aggiornamento: 2021-09-27
Last Update / Ultimo aggiornamento: 2021-09-29
Last Update / Ultimo aggiornamento: 2021-10-06
.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
Last Update / Ultimo aggiornamento: 2021-10-08
Last Update / Ultimo aggiornamento: 2021-10-09
Last Update / Ultimo aggiornamento: 2021-10-12
Last Update / Ultimo aggiornamento: 2021-11-18
:target: https://t.me/Assitenza_clienti_powERP
Last Update / Ultimo aggiornamento: 2021-12-04
Last Update / Ultimo aggiornamento: 2021-12-05
Last Update / Ultimo aggiornamento: 2021-12-09
Last Update / Ultimo aggiornamento: 2021-12-10
Last Update / Ultimo aggiornamento: 2021-12-11
Last Update / Ultimo aggiornamento: 2021-12-19
:target: https://odoo-community.org/page/development-status
:alt:
:target: https://travis-ci.com/zeroincombenze/tools
:alt: github.com
:target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
:alt: License: AGPL-3
:target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
:alt: License: OPL
:target: https://coveralls.io/github/zeroincombenze/tools?branch=1.0
:alt: Coverage
:target: https://codecov.io/gh/zeroincombenze/tools/branch/1.0
:alt: Codecov
:target: https://wiki.zeroincombenze.org/en/Odoo/1.0/dev
:alt: Technical Documentation
:target: https://wiki.zeroincombenze.org/it/Odoo/1.0/man
:target: https://erp1.zeroincombenze.it
:alt: Try Me
:target: https://codecov.io/gh/OCA/tools/branch/1.0
:target: https://odoo-italia.org
:alt: Odoo Italia Associazione
:target: https://www.zeroincombenze.it/
:alt: Zeroincombenze
:target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
:target: https://t.me/Assitenza_clienti_powERP


|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2021-12-21

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


