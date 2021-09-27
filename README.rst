
==========================
|Zeroincombenze| tools 0.1
==========================

|Build Status| |Coverage Status| |license gpl|




Overview / Panoramica
=====================

|en| Sparse python and bash source code

+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| name                     | brief                                                                                                                                                    |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| clodoo                   | Massive operations to multiple Odoo DBs in cloud. It is used to create configurate Odoo DB and to upgrade more DBs at the same time. No (yet) documented |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| lisa                     | Linux Installer Simple App. LAMP and odoo server installer from scratch.                                                                                 |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| maintainer-quality-tools | Forked OCA maintainer quality tools. It works with 6.1 and 7.0 Odoo version too                                                                          |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| os0                      | Simple os interface checked for OpenVMS too                                                                                                              |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| pytok                    | Simple python token parser (deprecated)                                                                                                                  |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| travis_emulator          | Travis Emulator on local machine. Check your project before release on TravisCi                                                                          |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| wok_code                 | Undocumented                                                                                                                                             |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| wok_news                 | Undocumented                                                                                                                                             |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| z0lib                    | General purpose bash & python library                                                                                                                    |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| zar                      | Zeroincombenze Archive and Replica. Backup your Odoo DBs                                                                                                 |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
| zerobug                  | testing & debug library                                                                                                                                  |
+--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+


|it| Strumenti Python & bash
----------------------------

Codice vario python & bash



|
|

Getting started
===============

|Try Me|


|

Installation
------------

Installation
------------

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


History
-------

python_plus: 1.0.3.3 (2021-09-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] vem: error message "riga 99: deactivate:"


clodoo: 0.3.35.3 (2021-09-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo: specific openpyxl for python2


travis_emulator: 1.0.2.1 (2021-09-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis: check for cached expired VME


python_plus: 1.0.3.2 (2021-09-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] vem: create vem with -I switch
[REF] vem refactoring


wok_code: 1.0.2.2.2 (2021-09-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] please: error sub2 sub3


clodoo: 0.3.35.1 (2021-09-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] powerp module transaltion


z0bug_odoo: 1.0.5.1 (2021-09-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] New powerp RC configuration


wok_code: 1.0.2.2.1 (2021-09-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] please: replace does not set protection bits; now -f is required
[IMP] please: wep does not set protection bits; now -f is required


python_plus: 1.0.3.1 (2021-09-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] vem: added click package
[FIX] vem: create with devel packages


clodoo: 0.3.35 (2021-09-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] python 3


wok_code: 1.0.2.2 (2021-08-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] gen_readme.py: search for authors in current README


wok_code: 1.0.2.2 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] ct_csv_coa.py: new command to manage Odoo CoA
[IMP] gen_readme.py: search for authors in current README


odoo_score: 1.0.2.1 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] odoo_shell.py: minor updates


clodoo: 0.3.33.4 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py: rcp login


z0bug_odoo: 1.0.5 (2021-08-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Stable version


travis_emulator: 1.0.2 (2021-08-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis: stable version


zerobug: 1.0.1.4 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis_install_env: echo indented command
[IMP] travis_install_env: new travis command testdeps


z0bug_odoo: 1.0.4.3 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] travis_run_test: new command testdeps


wok_code: 1.0.2.2 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] please: action docs shows recent history
[IMP] gen_readme.py: show recent history
[FIX] topep8: parse .travis.yml


travis_emulator: 1.0.1.8 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis: color change
[IMP] travis: new action testdeps
[FIX] travis: matrix selection


odoo_score: 1.0.2 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] Stable version


clodoo: 0.3.33.3 (2021-08-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] transodoo.xlsx: translation update


clodoo: 0.3.33.1 (2021-08-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] transodoo.xlsx: wrong translation of l10n_it_reverse_charge



zar: 1.3.35.3 (2021-08-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] pg_db_active: kill process


travis_emulator: 1.0.1.5 (2021-08-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis: summary return 1 if test failed or is broken
[IMP] travis: return status like summary
[IMP] travis: summary & show-log can show old logfile i.e.: travis summary old
[IMP] travis: osx emulatore return more info when error


clodoo: 0.3.31.16 (2021-08-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoorc: module list


clodoo: 0.3.31.15 (2021-08-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoorc: run in osx darwin


zerobug: 1.0.1.2 (2021-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] travis_run_pypi_test: run in osx darwin
[FIX] z0testrc: run in osx darwin


odoo_score: 1.0.1.4 (2021-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] run_odoo_debug: run in osx darwin


clodoo: 0.3.31.14 (2021-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoo_install_repository: run in osx darwin


wok_code: 1.0.2.2 (2021-08-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] please: changed the syntax of som actions
[IMP] pre-commit: regex var GIT_NO_CHECK with path to no check


travis_emulator: 1.0.1.4 (2021-08-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] devel_tools replaced by wok_code
[IMP] travis: summary return 1 if test failed


z0bug_odoo: 1.0.3.2 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] test data update


wok_code: 1.0.2.2 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[REF] Merged and renamed to wok_code


python_plus: 1.0.1.3 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: uninstall package with if package version with ">"


clodoo: 0.3.31.13 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] transodoo.py: tranlsation now can return None value
[IMP] transodoo.xlsx: upgrade translation



wok_code: 1.0.2.2 (2021-08-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] topep8: file list does not include .idea files
[IMP] please: action docs now set license file in current directory


wok_code: 1.0.2.2 (2021-08-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] gen_readme.py: parameter error


travis_emulator: 1.0.1.3 (2021-08-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] Show virtual enviroment name in summary


z0bug_odoo: 1.0.3.1 (2021-07-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] test data format xlsx (it replaces csv)
* [IMP] value "\N" in data file for not value


z0bug_odoo: 1.0.3 (2021-07-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] new test data


wok_code: 1.0.2.2 (2021-07-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoo_translation.py: xlrd (no more supported) replaced by openpyxl


python_plus: 1.0.1.2 (2021-07-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: exec in current directory





Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


|


Last Update / Ultimo aggiornamento: 2021-09-27

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
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
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=0.1
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.1/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/0.1
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-0.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/0.1/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-0.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/0.1/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-0.svg
    :target: https://erp0.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.1/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/0.1
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

