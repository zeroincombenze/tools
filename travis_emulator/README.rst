
========================
travis_emulator 0.2.2.18
========================



|Maturity| |Build Status| |Coverage Status| |license gpl|


.. contents::


Overview / Panoramica
=====================

|en| travis_emulator
====================

Travis emulator to test application before pushing to git
---------------------------------------------------------

Travis emulator can execute a .travis.yml file in local Linux machine.
You can test your application before push code into TravisCI web site.


|

|it| 

|

Features / Caratteristiche
--------------------------

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

Usage / Utilizzo
----------------

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

(C) 2015-2019 by zeroincombenze(R)
http://wiki.zeroincombenze.org/en/Linux/dev
Author: antoniomaria.vigliotti@gmail.com
