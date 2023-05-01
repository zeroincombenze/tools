
==========================
|Zeroincombenze| tools 2.0
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

You can find more info at https://zeroincombenze-tools.readthedocs.io/

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

The odoo_vid is the name of one specific Odoo configuration in multi instances
environment. It is mainly the directory for the specific Odoo instance.
Imagine a scenario with different Odoo instances running on the same host.
This is the development environment or the test environment.
Every instance of Odoo must have an own configuration file and packages.
Based on configuration file, every Odoo instance must have a own xmlrcp port,
db user, log file, pid file, etcetera.

The odoo_vid provides a simple way to manage multiple Odoo instance.
Supplying odoo_vid you select the specific parameters values just in one item.

The odoo_vid item is composed by:

* Prefix "VENV" if virtual environment (deprecated)
* Prefix V to identify main instance (deprecated)
* Odoo distribution (for organizations which have short name)
* Odoo version (full version or major version)
* Odoo distribution (all organizations)
* User specific identification

Odoo distribution may be one of: librerp,oca,zero or nothing

Odoo version is the Odoo specific version; it is one value of:
16.0 15.0 14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1

Examples of valid odoo_vid:

* 12.0 -> Odoo 12.0, unidentified distribution
* oca14 -> Odoo 14.0, distribution oca (short name)
* librerp6 -> Odoo 6.1, distribution librerp (short name)
* odoo14-oca -> Odoo 14.0, distribution oca (full name)
* odoo12-devel -> Odoo 12.0, odoo distribution, user identification "devel"

Based on above information, tool software can assume the right value of specific Odoo instance.

This table shows the Odoo parameter values based on odoo_vid;
please notice the symbol PUID is the personal user identification,
symbol %M means Odoo major version and %V Odoo full version.

+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| Parameter name             | standard value             | unidentified distro  | zeroincombenze(R | oca distro      | personal distro  | Note                                     |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| ROOT (Odoo root)           |                            | ~/%V                 | ~/zero%M         | ~/oca%M         | ~/odoo_%M        | i.e. ~/oca14                             |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| CONFN (configuration file) | odoo.conf odoo-server.conf | odoo%M-server.conf   | odoo%M-zero.conf | odoo%M-oca.conf | odoo%M-PUID.conf | Directory /etc/odoo (see Odoo structure) |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| USER (db user)             | odoo                       | odoo%M               | odoo%M           | odoo%M          | odoo%M           | i.e odoo12                               |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| FLOG (log file)            | odoo.log odoo-server.log   | odoo%M-server.log    | odoo%M-zero.log  | odoo%M-oca.log  | odoo%M-PUID.log  | Directory /var/log/odoo                  |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| FPID (pid file)            | odoo.pid odoo-server.pid   | odoo%M-server.pid    | odoo%M-zero.pid  | odoo%M-oca.pid  | odoo%M-PUID.pid  | Directory /var/run/odoo                  |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| RPCPORT (xmlrpc port)      | 8069                       | 8160 + %M            | 8460 + %M        | 8260 + %M       | 8360 + %M        |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| LPPORT (longpolling)       | 8072                       | 8130 + %M            | 8430 + %M        | 8230 + %M       | 8330 + %M        |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+
| SVCNAME (service name)     | odoo odoo-server           | odoo%M odoo%M-server | odoo%M-zero      | odoo%M-oca      | odoo%M-PUID      |                                          |
+----------------------------+----------------------------+----------------------+------------------+-----------------+------------------+------------------------------------------+




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

z0bug_odoo: 2.0.7.1 (2023-04-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: multiple actione on the same records


odoo_score: 2.0.6 (2023-04-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Import class models.Model


z0lib: 2.0.4 (2023-04-10)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_traced: cd does not work w/o alias
* [IMP] coveralls and codecov are not more dependencies


z0bug_odoo: 2.0.7 (2023-04-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [NEW] TestEnv: assertion counter
* [IMP] TestEnv: is_xref recognizes dot name, i.e "zobug.external.10"
* [IMP] TestEnv: the field <description> is not mode key (only acount.tax)
* [IMP] TestEnv: 3th level xref may be a many2one field type


clodoo: 2.0.4 (2023-03-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] odoorc: minor improvements
* [IMP] odoorc: test for Odoo 16.0
* [IMP] transodoo.py: minor improvements


zerobug: 2.0.5 (2023-03-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] travis_install_env: ensure list_requirements is executable
* [IMP] flake8 configuration
* [IMP] coveralls and codecov are not more dependencies
* [IMP] Test for Odoo 16.0


travis_emulator: 2.0.4 (2023-03-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Added python 3.9 to test
* [IMP] Detect python versions from setup.py
* [IMP] Option switch for python version become -j
* [IMP} make_travis recognizes verbose option


python_plus: 2.0.6 (2023-03-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: cryptography, pypdf2, requests & urllib3 version adjustment
* [IMP] list_requirements.py: pypdf and pypdf2 version adjustment
* [IMP] list_requirements.py: best resolution when versions conflict
* [IMP] vem: set list_requirements.py executable


odoo_score: 2.0.5 (2023-03-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug.sh: moved to package wok_code






Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


|


Last Update / Ultimo aggiornamento: 2023-05-01

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

