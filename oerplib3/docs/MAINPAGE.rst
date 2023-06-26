
================
odoo_score 2.0.5
================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Odoo supercore

odoo_score is a library that extends the odoo orm functionality and makes available a simple odoo shell.



odoo_shell
----------

Odoo shell is a simple line command shell to manager Odoo database using the internal Odoo functions.



|

Usage
=====



odoo_shell usage
----------------

::

    usage: odoo_shell.py [-h] [-A python_name] [-c file] [-d file] [-n] [-q] [-V]
                         [-v] [-w file] [-z name] [-1 PARAM_1] [-2 PARAM_2]
                         [-3 PARAM_3] [-4 PARAM_4] [-5 PARAM_5] [-6 PARAM_6]

    Odoo test environment

    optional arguments:
      -h, --help            show this help message and exit
      -A python_name, --action python_name
                            internal action to execute
      -c file, --config file
                            configuration command file
      -d file, --dbname file
                            DB name to connect
      -n, --dry-run         do nothing (dry-run)
      -q, --quiet           silent mode
      -V, --version         show program's version number and exit
      -v, --verbose         verbose mode
      -w file, --src-config file
                            Source DB configuration file
      -z name, --src-db_name name
                            Source database name
      -1 PARAM_1, --param-1 PARAM_1
                            value to pass to called function
      -2 PARAM_2, --param-2 PARAM_2
                            value to pass to called function
      -3 PARAM_3, --param-3 PARAM_3
                            value to pass to called function
      -4 PARAM_4, --param-4 PARAM_4
                            value to pass to called function
      -5 PARAM_5, --param-5 PARAM_5
                            value to pass to called function
      -6 PARAM_6, --param-6 PARAM_6
                            value to pass to called function




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

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install odoo_score

|

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

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install odoo_score -U

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

git 2.0.5 (2023-03-23)
~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_odoo_debug.sh: ODOO_COMMIT TEST not set when build template
* [IMP] run_odoo_debug.sh: simulate server_wide_modules parameter for Odoo 7.0-

2.0.4 (2023-01-13)
~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug.sh: test creates log

2.0.3 (2022-11-11)
~~~~~~~~~~~~~~~~~~

* [IMP] odoo_score: implementation of models and fields for Odoo 8-0+ modules

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [FIX] run_odoo_debug: test function improvements
* [IMP] run_odoo_debug: ODOO_COMMIT_TEST

2.0.1.1 (2022-10-13)
~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug: python stub
* [FIX] run_odoo_debug: crash in sime rare cases

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.3 (2022-10-05)
~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug: test via pycharm
* [FIX] run_odoo_debug: concurrent tests

2.0.0.2 (2022-09-22)
~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odo_debug: test with random rpcport for multiple tests
* [IMP] odoo_shell.py: new actions

2.0.0.1 (2022-09-07)
~~~~~~~~~~~~~~~~~~~~

* [FIX] run_odo_debug with debug
* [IMP] run_odoo_debug: experimental debug via pycharm

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

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
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


