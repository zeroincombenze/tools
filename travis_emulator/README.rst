
========================
travis_emulator 0.2.3.11
========================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Emulate travis to test application before pushing to git
--------------------------------------------------------

Travis emulator can emulate TravisCi parsing the **.travis.yml** file in local Linux machine.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in **.travis.yml**; all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all then build created.
Please note that log file is a binary file with escape ANSI screen code.
If you want to see the log use the following command:

    `less -R ~/travis_log/<build_name>.log`

A travis build executes the following steps:

* Initialize from local .travis.conf (not in travis-ci.org)
* Optional install packages `apt addons` (emulatore makes just the check)
* Optional install packages `cache`
* Set global values `env global`
* Execute code `before_install`
* Execute matrix initialization, included python version
* Execute build code `install`
* Execute build code `before_script`
* Execute build code `script`
* Execute build `before_cache` (only if cache is effective, not emulated)
* Execute build code `after_success` (emulated) or `after_failure` (not emulated)
* Optional code `before_deploy` (only if deployment is effective, not emulated)
* Optional code `deploy` (not emulated)
* Optional code `after_deploy` (only if deployment is effective, not emulated)
* Execute code `after_script` (not emulated)
* Wep from local .travis.conf (not in travis-ci.org)

Read furthermore info read `travis-ci phase <https://docs.travis-ci.com/user/job-lifecycle/>`__



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

    Usage: travis [-hBC][-c file][-D number][-EFfjk][-L number][-l dir][-Mmn][-O git-org][-pqr][-S false|true][-Vv][-X 0|1][-Y file][-y pyver][-Z] action sub sub2
    Travis-ci emulator for local developer environment
    Action may be: [force-]lint, [force-]test, emulate (default), (new|chk|cp|mv|merge)_vm, chkconfig or parseyaml
     -h                      this help
     -B                      debug mode: do not create log
     -C                      do not use stored PYPI
     -c file                 configuration file (def .travis.conf)
     -D number               travis_debug_mode: may be 0,1,2 or 9 (def yaml dependents)
     -E                      save virtual environment as ~/VME/VME{version}
     -F                      run final travis with full features
     -f                      force yaml to run w/o cmd subst
     -j                      execute tests in project dir rather in test dir (or expand macro if parseyaml)
     -k                      keep DB and virtual environment after tests
     -L number               lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml
     -l dir                  log directory (def=~/travis_log)
     -M                      use local MQT (deprecated)
     -m                      show missing line in report coverage
     -n                      do nothing (dry-run)
     -O git-org              git organization, i.e. oca or zeroincombenze
     -p                      prefer python test over bash test when avaiable
     -q                      silent mode
     -r                      run restricted mode (def parsing travis.yml file)
     -S false|true           use python system packages (def yaml dependents)
     -V                      show version
     -v                      verbose mode
     -X 0|1                  enable translation test (def yaml dependents)
     -Y file                 file yaml to process (def .travis.yml)
     -y pyver                test with specific python versions (comma separated)
     -Z                      use local zero-tools


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
        - \${HOME}/tools/install_tools.sh -qopt
        - source ${HOME}/dev/activate_tools
        Above statements replace OCA following statements:
        - git clone https://github.com/OCA/maintainer-quality-tools.git ${HOME}/maintainer-quality-tools --depth=1
        - export PATH=${HOME}/maintainer-quality-tools/travis:${PATH}


Configuration file
~~~~~~~~~~~~~~~~~~

Values in configuration file are:

+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| Parameter         | Descriptio                                         | Default value                                                                                            |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| CHAT_HOME         | URL to web chat to insert in documentation         |                                                                                                          |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| ODOO_SETUPS       | Names of Odoo manifest files                       | __manifest__.py __openerp__.py __odoo__.py __terp__.py                                                   |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| dbtemplate        | Default value for MQT_TEMPLATE_DB                  | openerp_template                                                                                         |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| dbname            | Default value for MQT_TEST_DB                      | openerp_test                                                                                             |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| dbuser            | Postgresql user: default value for MQT_DBUSER      | $USER                                                                                                    |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| UNBUFFER          | Use unbuffer                                       | 0                                                                                                        |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| virtualenv_opts   | Default option to create virtual environment       |                                                                                                          |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| NPM_CONFIG_PREFIX | N/D                                                | \$HOME/.npm-global                                                                                       |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PS_TXT_COLOR      | N/D                                                | 0;97;40                                                                                                  |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PS_RUN_COLOR      | N/D                                                | 1;36;48;5                                                                                                |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PS_NOP_COLOR      | N/D                                                | 31;105                                                                                                   |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PS_HDR1_COLOR     | N/D                                                | 97;48;5;22                                                                                               |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PS_HDR2_COLOR     | N/D                                                | 30;43                                                                                                    |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PS_HDR3_COLOR     | N/D                                                | 30;47                                                                                                    |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PKGS_LIST         | N/D                                                | clodoo devel_tools lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| PYTHON_MATRIX     | Python version available to test (space separated) |                                                                                                          |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------------------+




|
|

Getting started
===============


|

Installation
------------


Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -op
    source /opt/odoo/dev/activate_tools


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

Last Update / Ultimo aggiornamento: 2020-08-31

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
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=master
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=0.2.3.11
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.11/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.11
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/0.2.3.11/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/0.2.3.11/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.2.3.11/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/0.2.3.11
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


