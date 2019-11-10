
========================
travis_emulator 0.2.2.21
========================



|Maturity| |Build Status| |Coverage Status| |license gpl|


.. contents::


Overview
========

travis_emulator
===============

Travis emulator to test application before pushing to git
---------------------------------------------------------

Travis emulator can execute a .travis.yml file in local Linux machine.
You can test your application before push code into TravisCI web site.



|

Features
--------

+--------------------------------+---------+-------------------------------+
| Function                       | Status  | Note                          |
+--------------------------------+---------+-------------------------------+
| Execute in virtual environment | |check| | As TravisCI                   |
+--------------------------------+---------+-------------------------------+
| Python 2 test                  | |check| | If installed in local machine |
+--------------------------------+---------+-------------------------------+
| Python 3 test                  | |check| | If installed in local machine |
+--------------------------------+---------+-------------------------------+
| Bash test                      | |check| |                               |
+--------------------------------+---------+-------------------------------+
| Matrix                         | |check| | Test sequentialized           |
+--------------------------------+---------+-------------------------------+
| Coveralls                      | |check| | If installed in local machine |
+--------------------------------+---------+-------------------------------+
| MQT                            | |check| | Test using Odoo MQT           |
+--------------------------------+---------+-------------------------------+

|
|

Quick start
===========


|

Installation
------------

For current version:

`cd $HOME`
`git@github.com:zeroincombenze/tools.git`
`cd $HOME/tools`
`./install_tools.sh`


|

Usage
=====

::

    Usage: travis [-hBC][-c file][-D number][-EFfjk][-L number][-l dir][-Mmn][-O git-org][-pqr][-S false|true][-VvW][-X 0|1][-Y file][-3] action sub sub2
    Travis-ci emulator for local developer environment
    Action may be: [force-]lint, [force-]test, emulate (default), (new|chk|cp|mv|merge)_vm, chkconfig or parseyaml
     -h              this help
     -B              debug mode: do not create log
     -C              do not use stored PYPI
     -c file         configuration file (def .travis.conf)
     -D number       travis_debug_mode: may be 0,1,2 or 9 (def yaml dependents)
     -E              save virtual environment as ~/VME/VME{version}
     -F              run final travis with full features
     -f              force yaml to run w/o cmd subst
     -j              execute tests in project dir rather in test dir (or expand macro if parseyaml)
     -k              keep DB and virtual environment after tests
     -L number       lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml
     -l dir          log directory (def=~/travis_log)
     -M              use local MQT
     -m              show missing line in report coverage
     -n              do nothing (dry-run)
     -O git-org      git organization, i.e. oca or zeroincombenze
     -p              prefer python test over bash test when avaiable
     -q              silent mode
     -r              run restricted mode (def parsing travis.yml file)
     -S false|true   use python system packages (def yaml dependents)
     -V              show version
     -v              verbose mode
     -W              do not use virtualenv to run tests
     -X 0|1          enable translation test (def yaml dependents)
     -Y file         file yaml to process (def .travis.yml)
     -3              use python3


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

* Antonio M. Vigliotti <info@shs-av.com>


|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2019-11-01

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

