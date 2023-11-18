=====================
travis_emulator 2.0.7
=====================



|Maturity| |license gpl|



Overview
========

Travis emulator can emulate TravisCi parsing the **.travis.yml** file in local
Linux machine and it is osx/darwin compatible.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in ``travis.yml**``;
all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all builds created.
Please note that log file is a binary file with escape ANSI screen code.
If you want to see the log use one of following command:

::

    travis show

    less -R ~/travis_log/<build_name>.log

A travis build executes the following steps:

+-----------------------------------------------------------------+--------------------+----------+-----+
| Description                                                     | name               | local    | web |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Initialize from .travis.conf                                    | travis.conf        | ✔        | ✗   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Matrix initialization (python version too)                      | matrix             | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Build job                                                       | build              | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional install packages `apt addons`                          | addons.apt.package | simulate | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional install packages `cache`                               |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Set global values `env global`                                  | env.global         | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute code `before_install`                                   | before_install     | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `install`                                    |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `before_script`                              |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `script`                                     | script             | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build `before_cache` (only if cache is effective)       |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute build code `after_success`                              |                    | ✔        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Or execute `after_failure`                                      |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional code `before_deploy` (only if deployment is effective) |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional code `deploy`                                          |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Optional code `after_deploy` (only if deployment is effective)  |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Execute code `after_script`                                     |                    | ✗        | ✔   |
+-----------------------------------------------------------------+--------------------+----------+-----+
| Wep from local .travis.conf                                     |                    | ✔        | ✗   |
+-----------------------------------------------------------------+--------------------+----------+-----+



Read furthermore info read `travis-ci phase <https://docs.travis-ci.com/user/job-lifecycle/>`__


Difference between local travis and web site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The travis emulator works mostly like TravisCi web site. However you ha to consider
some points where you run local tests:

Local software is not published

    When you test on your local PC, the software is not yet publishd.
    Perhaps you prefer test local packages or local modules.
    The travis emulator with z0bug_odoo replace the commands ``git clone`` with
    local `ln -s` creating logical link with local repository, if possible.
    Local module are searched in the testing module directory. See Odoo structure
    for furthermore info.

Your PC is not TravisCi web site

    Probability you have just one python interpreter and your user is not sudo enabled.
    The travis emulator run build just with Odoo interpreter installed even if your
    .travis.yml file contains more python version to test.
    The travis emulator does not try to install global packages because
    it does not change the PC configuration.
    Please, install manually all the global packages using apt-get, yum, dnf or your local installer software.



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



Usage
=====

Travis emulator usage
---------------------

::

    Usage: travis [-h][-A regex][-BC][-D number][-E][-e iso][-Ffk][-j pyver][-L number][-l dir][-mn][-O git-org][-P file:line][-p pattern][-Q file][-qr][-S false|true][-T regex][-Vv][-X 0|1][-Y file][-Z] action sub sub2
    Travis-ci emulator for local developer environment
    Action may be: (help,emulate,force-lint,lint,force-test,test,force-test-multi,test-multi,force-testdeps,testdeps,force-translate,translate,chkconfig,parseyaml,show,show-log,show-color,summary,wep-db)
     -h --help            this help
     -A --trace-after regex
                          travis stops after executed yaml statement
     -B --debug           debug mode: do not create log
     -C --no-cache        do not use stored PYPI
     -D --debug-level number
                          travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)
     -E --no-savenv       do not save virtual environment into ~/VME/... if does not exist
     -e --locale iso
                          use locale
     -F --full            run final travis with full features
     -f --force           force to create stored VME or remove recent log (wep-db)
     -k --keep            keep DB and virtual environment before and after tests
     -j --python pyver
                          test with specific python versions (comma separated)
     -L --lint-level number
                          lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml
     -l --logdir dir
                          log directory (def=/home/odoo/travis_log)
     -m --missing         show missing line in report coverage
     -n --dry-run         do nothing (dry-run)
     -O --org git-org
                          git organization to test, i.e. oca or zeroincombenze
     -P --python-brk file:line
                          set python breakpoint at file:linenumber
     -p --pattern pattern
                          pattern to apply for test files (comma separated)
     -Q --config file
                          configuration file (def .z0tools.conf)
     -q --quiet           silent mode
     -r                   run restricted mode (deprecated)
     -S --syspkg false|true
                          use python system packages (def yaml dependents)
     -T --trace regex
                          trace stops before executing yaml statement
     -V --version         show version
     -v --verbose         verbose mode
     -X --translation 0|1
                          enable translation test (def yaml dependents)
     -Y --yaml-file file
                          file yaml to process (def .travis.yml)
     -Z --zero            use local zero-tools
    
    © 2015-2022 by zeroincombenze®
    https://zeroincombenze-tools.readthedocs.io/
    Author: antoniomaria.vigliotti@gmail.com
    


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
| dbtemplate        | Default value for MQT_TEMPLATE_DB                  | template_odoo                                                                                |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| dbname            | Default value for MQT_TEST_DB                      | test_odoo                                                                                    |
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
| LOCAL_PKGS        | N/D                                                | clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+
| PYTHON_MATRIX     | Python version available to test (space separated) |                                                                                              |
+-------------------+----------------------------------------------------+----------------------------------------------------------------------------------------------+



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

    pip install travis_emulator

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

    pip install --upgrade travis_emulator


Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



Troubleshooting
---------------

*Message "Denied inquire with psql [-U<name>]"*

    User <name> cannot execute psql command.
    Travis emulator cannot drop test database after build completation.
    Please configure postgresql and enable user <name> to use psql via shell.
    If user is not *odoo* declare username with following command:

    ``please config global``

    and then set *dbuser* parameter value.


*Message "false;   # Warning! TODO> apt-get install <pkg>*

    The package <pkg> is not installed on your system.
    Travis emulator run at low security level and cannot install debian or rpm packages.
    Please install the package <pkg> via *apt-get* or *yum* or *dnf* based on your distro.
    You can use *lisa* to install package <pkg> on all distribution with following command:

    ``lisa install <pkg>``


ChangeLog History
-----------------

2.0.7 (2023-11-17)
~~~~~~~~~~~~~~~~~~

* [IMP] Automatic python version for Odoo

2.0.6 (2023-07-10)
~~~~~~~~~~~~~~~~~~

* [FIX] travis: check for dropped DB and abort if still exist
* [IMP] travis: action show as alias of show-log for please integration

2.0.5 (2023-05-14)
~~~~~~~~~~~~~~~~~~

* [IMP] New -p parameter to select specific test to execute
* [IMP] Switch -M removed
* [IMP] Switch -d set default "test" action
* [IMP] Removes osx support

2.0.4 (2023-03-24)
~~~~~~~~~~~~~~~~~~

* [IMP] Added python 3.9 to test
* [IMP] Detect python versions from setup.py
* [IMP] Option switch for python version become -j
* [IMP} make_travis recognizes verbose option

2.0.3 (2022-12-09)
~~~~~~~~~~~~~~~~~~

* [FIX] Best python version recognition

2.0.2.2 (2022-11-08)
~~~~~~~~~~~~~~~~~~~~

* [IMP] npm management

2.0.2.1 (2022-11-02)
~~~~~~~~~~~~~~~~~~~~

* [REF] travis: partial refactoring
* [IMP] travis: recognition of local/librerp

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [IMP] database name: (test|template)_odoo
* [IMP] With -k switch set ODOO_COMMIT_TEST

2.0.1.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~~~

* [IMP] travis: change logfile name

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.2 (2022-10-04)
~~~~~~~~~~~~~~~~~~~~

* [IMP] travis: python2 tests


2.0.0.1 (2022-09-06)
~~~~~~~~~~~~~~~~~~~~

* [IMP] travis: new improvements (-f -k switches)


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

* `Antonio M. Vigliotti <info@shs-av.com>`__
* `Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>`__


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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.7/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.7/man
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
