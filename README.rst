
==========================
|Zeroincombenze| tools 1.0
==========================

|Build Status| |Coverage Status| |license gpl|




Overview / Panoramica
=====================

|en| Multi-purpose python & bash tools
--------------------------------------

Multi-purpose python and bash source code.

These tools help to cover the following areas of software:

* Odoo deployment
* Odoo database maintenance (creation and upgrade, massive)
* Odoo database profiling (auto)
* Database check (auto & massive)
* Development
* Documentation
* Testing

Compatibility
~~~~~~~~~~~~~

These tools are designed to be used on Linux platforms.
They are tested on following distros:
* Ubuntu: from 12.0 to 20.0
* Debian: from 8.0 to 10.0
* CentOS: from 7 to 8
Currently the osx Darwin is in testing.

Components
~~~~~~~~~~

+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| Package         | Name                    | Brief                                                                                                                                                      | Area                      |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| clodoo          | check_4_seq.sh          | Check for postgres database index                                                                                                                          | maintenance               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | clodoo.py               | Massive operations on multiple Odoo DBs in cloud. It is used to create configurated Odoo DBs and to upgrade more DBs at the same time. No (yet) documented | maintenance               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | force_password.sh       | Force Odoo DB password                                                                                                                                     | maintenance               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | inv2draft_n_restore.py  | Force an invoice to draft state even if is paid and restore original state and payment (Odoo < 9.0)                                                        | maintenance               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | list_requirements.py    | List pypi and bin packages for an Odoo installation                                                                                                        | deployment                |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | manage_db               | Massive operations to multiple Odoo DBs in cloud, data based on csv files.                                                                                 | maintenance               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | manage_odoo             | Manage an Odoo installation                                                                                                                                | maintenance               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | odoo_install_repository | Install & upgrade odoo repository                                                                                                                          | Deployment & maintenance  |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | set_workers.sh          | Evaluate and set Odoo workers for best performance                                                                                                         | Deployment & maintenance  |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| lisa            | lisa                    | Linux Installer Simple App. LAMP and odoo server installer from scratch.                                                                                   | deployment                |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| odoo_score      | odoo_score.py           | Odoo ORM super core                                                                                                                                        | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | odoo_shell.py           | Odoo shell for Odoo versions from 6.1 to 13.0                                                                                                              | Development & maintenance |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| os0             |                         | Simple os interface checked for OpenVMS too                                                                                                                | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| python-plus     | python-plus             | Various features to python 2 and python 3 programs as integration of pypi future to help to port your code from Python 2 to Python 3                       | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | vem                     | Virtual Environment Manager: create, copy, move, merge and many other functions with virtual environments                                                  | Deployment & maintenance  |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| travis_emulator | travis                  | Travis Emulator on local machine. Check your project before release on TravisCi                                                                            | testing                   |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| wok_code        | cvt_csv_to_rst.py       | Convert a csv file into rst text file with table inside                                                                                                    | documentation             |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | cvt_csv_to_xml.py       | Convert a csv file into xml file for Odoo module data                                                                                                      | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | cvt_script              | Make bash script to standard                                                                                                                               | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | gen_readme.py           | Generate README.rst, index.html and __openerp__.py ,documentation                                                                                          | documentation             |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | odoo_dependencies.py    | Show Odoo module tree, ancestors and/or childs                                                                                                             | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | odoo_translation.py     | Load Odoo translation (deprecated, must be replaced by weblate)                                                                                            | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | please                  | Developer shell                                                                                                                                            | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | topep8                  | Convert python and xml file across Odoo versions                                                                                                           | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | vfdiff                  | Make difference between 2 files or directories                                                                                                             | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| wok_news        |                         | Undocumented (deprecated)                                                                                                                                  |                           |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0bug_odoo      | z0bug_odoo              | Integration of zerobug and Odoo. Initially forked form OCA maintainer quality tools. It works with all Odoo version, from 6.1 to 13.0                      | testing                   |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0lib           |                         | General purpose bash & python library                                                                                                                      | development               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zar             | zar                     | Zeroincombenze Archive and Replica. Backup your Odoo DBs                                                                                                   | maintenance               |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zerobug         | zerobug                 | testing & debug library                                                                                                                                    | testing                   |
+-----------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+




Odoo vid
~~~~~~~~

The odoo_vid is mainly the directory with a specific Odoo instance in multi instance environment.
Imagine a scenario with different Odoo instance running on the same host.
This is the development environment or the test environment.
Every instance of Odoo must have a own configuration file and packages.
Based on configuration file, every Odoo instance must have a own xmlrcp port, db user, log file, pid file, etcetera.

The odoo_vid provides a simple way to manage multiple Odoo instance.
Supplying odoo_vid you select the specific parameters values just in one item.

The odoo_vid item is composed by:

* Prefix "VENV" if virtual environment
* Prefix V to identify main instance
* Odoo distribution (for organizations with short name)
* Odoo version (full version or major version)
* Odoo distribution (all organizzations)
* User specific identification

Odoo distribution is on of: flectra,librerp,oca,powerp,zero or nothing

Odoo version is the Odoo specific version; it is one value of: 14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1

Examples of valid odoo_vid:

* 12.0 -> Odoo 12.0, unidentified distribution
* oca14 -> Odoo 14.0, distribution oca (short name)
* librerp6 -> Odoo 6.1, distribution librerp (short name)
* odoo14-oca -> Odoo 14.0, distribution oca (full name)
* odoo12-devel -> Odoo 12.0, odoo ditribution, user identification "devel"

Based on above information, tool software can assume the right value of specific Odoo instance.

This table shows the Odoo parameter values based on odoo_vid;
notice the symbol %M meaans Odoo major version and %V Odoo version.

+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| Parameter name             | standard value             | anonymous distro     | zeroincombenze d | oca distro      | axitec distro   | Note                                     |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| ROOT (Odoo root)           |                            | ~/%V                 | ~/zero%M         | ~/oca%M         | ~/odoo_%M       | i.e. ~/oca14                             |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| CONFN (configuration file) | odoo.conf odoo-server.conf | odoo%M-server.conf   | odoo%M-zero.conf | odoo%M-oca.conf | odoo%M-axi.conf | Directory /etc/odoo (see Odoo structure) |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| USER (db user)             | odoo                       | odoo%M               | odoo%M           | odoo%M          | odoo%M          | i.e odoo12                               |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| FLOG (log file)            | odoo.log odoo-server.log   | odoo%M-server.log    | odoo%M-zero.log  | odoo%M-oca.log  | odoo%M-axi.log  | Directory /var/log/odoo                  |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| FPID (pid file)            | odoo.pid odoo-server.pid   | odoo%M-server.pid    | odoo%M-zero.pid  | odoo%M-oca.pid  | odoo%M-axi.pid  | Directory /var/run/odoo                  |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| RPCPORT (xmlrpc port)      | 8069                       | 8160 + %M            | 8460 + %M        | 8260 + %M       | 8360 + %M       |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| LPPORT (longpolling)       | 8072                       | 8130 + %M            | 8430 + %M        | 8230 + %M       | 8330 + %M       |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+
| SVCNAME (service name)     | odoo odoo-server           | odoo%M odoo%M-server | odoo%M-zero      | odoo%M-oca      | odoo%M-axi      |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+-----------------+------------------------------------------+




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


History
-------

zerobug: 1.0.2.2 (2021-09-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] travis level update


z0bug_odoo: 1.0.4.4 (2021-09-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] travis level update


travis_emulator: 1.0.2.1 (2021-09-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis: switch -y forces python version


clodoo: 0.3.31.5 (2021-09-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] clodoo.py python2 migration


zerobug: 1.0.2.1 (2021-09-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] z0testlib.py: new functions to create Odoo repository and module tree


lisa: 0.3.2.1 (2021-09-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] lisa_bld: value from config file


wok_code: 1.0.2.2.2 (2021-09-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] gen_readme.py: setup with more import lines



python_plus: 1.0.2.1 (2021-09-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] vem: create python3 (due jsonlib)


odoo_score: 1.0.2.2 (2021-09-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] run_odoo_debug: manage http_port instead of xmlrcp_port


clodoo: 0.3.31.5 (2021-09-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py with python3 due wrong jsoblib dependency


wok_code: 1.0.2.2.1 (2021-09-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] please replace: set generic python in executable files
[FIX] dist_pkg: install_dev not found




wok_code: 1.0.2.2 (2021-08-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] gen_readme.py: search for authors in current README


clodoo: 0.3.31.2 (2021-08-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] odoorc: it does not use <git branch --show-current>


wok_code: 1.0.2.2 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] cvt_csv_coa.py: new command to manage Odoo CoA
[IMP] gen_readme.py: search for authors in current README


odoo_score: 1.0.2.1 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] odoo_shell.py: minor updates


clodoo: 0.3.33.4 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py: rcp login


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


odoo_score: 1.0.1.3 (2021-07-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] run_odoo_debug: -T and -k switches togheter
[FIX] odoo_score.py: crash with python 3 (due clodoo package)
[IMP] odoo_shell.py: removed old code


wok_code: 1.0.2.2 (2021-07-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] gen_readme.py: ignore setup directories
[IMP] gen_readme.py: new parameter -L to set local language (def it_IT)
[IMP] gen_readme.py: check for licenze incompatibility



lisa: 0.3.1.14 (2021-07-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] lisa_bld: error for odoo 6.1 with server directory


z0bug_odoo: 1.0.2.3 (2021-07-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] test data upgrade


wok_code: 0.1.17.3 (2021-07-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] wget_odoo_repositories.py: best debug mode: check for branch


python_plus: 1.0.1.1 (2021-07-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] vem: best odoo path findind





Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


|


Last Update / Ultimo aggiornamento: 2021-09-07

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
   :target: https://t.me/axitec_helpdesk

