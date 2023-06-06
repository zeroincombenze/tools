
=====================
travis_emulator 2.0.5
=====================



|Maturity| |license gpl|




Overview
========

=====================
travis_emulator 2.0.5
=====================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

=====================
travis_emulator 2.0.5
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
|



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
|

Getting started
===============


Installation
------------

Zeroincombenze tools require:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20/22
* python 2.7+, some tools require python 3.6+
* bash 5.0+

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source $HOME/devel/activate_tools


Upgrade
-------

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -U
    source $HOME/devel/activate_tools


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
* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
Contributors
------------



|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2023-05-21

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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0/man
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


