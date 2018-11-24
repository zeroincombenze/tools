[![Build Status](https://travis-ci.org/OCA/maintainer-quality-tools.svg)](https://travis-ci.org/OCA/maintainer-quality-tools)
[![Coverage Status](https://coveralls.io/repos/OCA/maintainer-quality-tools/badge.svg)](https://coveralls.io/r/OCA/maintainer-quality-tools)

TRAVIS EMULATOR FOR LOCAL LINUX MACHINE
=======================================

Travis emulator can execute a .travis.yml file in local Linux machine.
You can test your application before push code into TravisCI web site.


### Features

Function | Status | Note
--- | --- | ---
Execute in virtual environment | :white_check_mark: | As TravisCI
Python 2 test | :white_check_mark: | If installed in local machine
Python 3 test | :white_check_mark: | If installed in local machine
Bash test | :white_check_mark: |
Matrix | :white_check_mark: | Test sequentialized
Coveralls | :white_check_mark: | If installed in local machine
MQT | :white_check_mark: | Test using Odoo MQT


Installation
------------

Install using odoo user.

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    ./tools/install_foreign.sh
    PATH=~/dev:$PATH


Configuration
-------------

    please config global


Usage
-----

    cd <repository_to_test>
    travis [options] [actions]

    Usage: travis [-hBC][-c file][-D number][-Efjk][-L number][-l dir][-Mmn][-O git-org][-pqrVvW] action sub
    Travis-ci emulator for local developer environment
    Action may be: lint, test, emulate (default), setup, chkconfig or parseyaml
     -h              this help
     -B              debug mode: do not create log
     -C              do not use cached PYPI
     -c file         configuration file (def .travis.conf)
     -D number       travis_debug_mode: may be 0,1,2; w/o value from .travis.yml
     -E              save virtual environment as ~/VME/VME{version}
     -f              force yaml to run w/o cmd subst
     -j              execute tests in project dir rather in test dir (or expand macro if parseyaml)
     -k              keep DB and virtual environment after tests
     -L number       lint_check_level: may be minimal,reduced,average,nearby,oca; w/o value from .travis.yml
     -l dir          log directory (def=~/travis_log)
     -M              use local MQT
     -m              show missing line in report coverage
     -n              do nothing (dry-run)
     -O git-org      git organization, i.e. oca or zeroincombenze
     -p              prefer python test over bash test when avaiable
     -q              silent mode
     -r              run restricted mode (w/o parsing travis.yml file)
     -V              show version
     -v              verbose mode
     -W              do not use virtualenv to run tests


VME
---

Creation of local VM requires a lot of time. Travis Emulator can create, save and use local VME (Virtual Machine Environment).

To create a new VME use -C switch.

To save locally VME use -E switch.


MQT
---

Travis emulator support both [OCA MQT](https://github.com/OCA/maintainer-quality-tools) both [Zeroincombenze® MQT](https://github.com/zeroincombenze/tools/tree/master/maintainer-quality-tools). 

To avoid long time test in matrix against odoo/OCA repository,
Travis emulator execute just local repository (if in .travis.yml file) or OCA repository.
Look at follow .travis.yml example:

    matrix:
      - LINT_CHECK="1" LINT_CHECK_LEVEL="MINIMAL"
      - TESTS="1" ODOO_REPO="odoo/odoo"
      - TESTS="1" ODOO_REPO="OCA/OCB"
      - TESTS="1" ODOO_REPO="my_repository/OCB" 

Travis Emulator execute matrix <LINT_CHECK="1" LINT_CHECK_LEVEL="MINIMAL">
and <TESTS="1" ODOO_REPO="my_repository/OCB"> while <TESTS="1" ODOO_REPO="odoo/odoo">
and <TESTS="1" ODOO_REPO="OCA/OCB"> are ignored.

Use -O switch to select another repository to test.


Reduced set of check
--------------------

Using [Zeroincombenze® MQT](https://github.com/zeroincombenze/tools/tree/master/maintainer-quality-tools)
you can execute reduced set of check, in order to gradually evolve your code quality
when you meet too many errors.

Use -L swicth to override LINT_CHECK_LEVEL declaration of .travis.yml file.

You can also execute just lint check or regression test. To test only lint check type:

    travis lint

To test only Odoo test, type:

    travis test


MQT debug informations
----------------------

Using [Zeroincombenze® MQT](https://github.com/zeroincombenze/tools/tree/master/maintainer-quality-tools)
you can debug local test with follow statement in .travis.yml file:

    TRAVIS_DEBUG_MODE="2"

Use -D switch to can override debug level.


Dump Test Environment
---------------------

Test Environment created by Travis Emulator is dropped after test.
You can read log file in ~/travis_log directory, if you did not use -B switch.

Use -k switch to keep created Test Environment.


Emergency execution
-------------------

If your .travis.yml cannot work, you can execute test withou parsing .travis.yml file.

Use -r switch to execute predefined test set.


Bug Tracker
-----------

Have a bug? Please visit https://odoo-italia.org/index.php/kunena/home


Credits
-------

### Contributors

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>

### Funders

This module has been financially supported by

* SHS-AV s.r.l. <https://www.zeroincombenze.it/>

### Maintainer

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>

[//]: # (copyright)

----

**Odoo** is a trademark of [Odoo S.A.](https://www.odoo.com/) (formerly OpenERP, formerly TinyERP)

**zeroincombenze®** is a trademark of [SHS-AV s.r.l.](http://www.shs-av.com/)
which distributes and promotes **Odoo** ready-to-use on its own cloud infrastructure.
[Zeroincombenze® distribution](http://wiki.zeroincombenze.org/en/Odoo)
is mainly designed for Italian law and markeplace.
Everytime, every Odoo DB and customized code can be deployed on local server too.

[//]: # (end copyright)
