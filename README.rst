
==============================
|Zeroincombenze| tools 0.2.3.2
==============================

|Coverage Status| |license gpl|




Overview
========

Python & bash tools
-------------------

Sparse python and bash source code.

These tools help to cover following areas of software:

* Odoo deployment
* Odoo database maintenance (creation and upgrade, massive)
* Odoo database profiling (auto)
* Database check (auto & massive)
* Development
* Documentation
* Testing

+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| Package                  | Name                    | brief                                                                                                                                                    | Area                      |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| clodoo                   | check_4_seq.sh          | Check for postgres database index                                                                                                                        | maintenance               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | clodoo.py               | Massive operations to multiple Odoo DBs in cloud. It is used to create configurate Odoo DB and to upgrade more DBs at the same time. No (yet) documented | maintenance               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | force_password.sh       | Force Odoo DB password                                                                                                                                   | maintenance               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | inv2draft_n_restore.py  | Force an invoice to draft state even if is paid and restore original state and paiment (Odoo < 9.0)                                                      | maintenance               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | list_requirements.py    | List pypi and bin packages of an Odoo installation                                                                                                       | deployment                |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | manage_db               | Massive operations to multiple Odoo DBs in cloud, data based on csv files.                                                                               | maintenance               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | manage_odoo             | Manage an Odoo installation                                                                                                                              | maintenance               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_install_repository | Install & upgrade odoo repository                                                                                                                        | Deployment & maintenance  |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | set_workers.sh          | Evaluate workers for best performance                                                                                                                    | Deployment & maintenance  |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| devel_tools              | cvt_csv_to_rst.py       | Convert a csv file into table in rst text file                                                                                                           | documentation             |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | cvt_csv_to_xml.py       | Convert a csv file into xml file to Odoo module data                                                                                                     | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | cvt_script              | Make bash script to standard                                                                                                                             | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | gen_readme.py           | Generate README.rst index.html and __openerp__.py                                                                                                        | documentation             |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_dependencies.py    | Show Odoo module tree, ancestors and/or childs                                                                                                           | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_translation.py     | Load Odoo translation (deprecated, must be replaced by weblate)                                                                                          | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | please                  | Developer shell                                                                                                                                          | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | topep8                  | Convert python and xml file across Odoo versions                                                                                                         | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | vfdiff                  | Make difference between 2 files or directories                                                                                                           | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| lisa                     | lisa                    | Linux Installer Simple App. LAMP and odoo server installer from scratch.                                                                                 | deployment                |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| maintainer-quality-tools |                         | Forked OCA maintainer quality tools. It works with 6.1 and 7.0 Odoo version too                                                                          | testing                   |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| odoo_score               | odoo_score.py           | Odoo super core ORM                                                                                                                                      | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_shell.py           | Odoo shell for Odoo versions from 6,1 to 13.0                                                                                                            | Development & maintenance |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| os0                      |                         | Simple os interface checked for OpenVMS too                                                                                                              | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| python-plus              | python-plus             | Various features to python 2 and python 3 programs as integration of pypi future to help to port your code from Python 2 to Python 3. run on Python 2.   | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | vem                     | Virtual Environment Manager: create, copy, move, merge and many other functions with virtual environments                                                | Deployment & maintenance  |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| pytok                    |                         | Simple python token parser (deprecated)                                                                                                                  |                           |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| travis_emulator          | travis                  | Travis Emulator on local machine. Check your project before release on TravisCi                                                                          | testing                   |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| wok_code                 |                         | Undocumented (deprecated)                                                                                                                                |                           |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| wok_news                 |                         | Undocumented (deprecated)                                                                                                                                |                           |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0bug_odoo               | z0bug_odoo              | Integration of zerobug and Odoo                                                                                                                          | testing                   |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0lib                    |                         | General purpose bash & python library                                                                                                                    | development               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zar                      | zar                     | Zeroincombenze Archive and Replica. Backup your Odoo DBs                                                                                                 | maintenance               |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zerobug                  | zerobug                 | testing & debug library                                                                                                                                  | testing                   |
+--------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+





|
|

Getting started
===============

|Try Me|


|

Installation
------------


Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::
    pip install repos_name

|

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/devel/activate_tools


Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


|


Last Update / Ultimo aggiornamento: 2020-07-10

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alfa
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=0.2.3.2
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=0.2.3.2
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=0.2.3.2
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.2/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.2
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/0.2.3.2/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/0.2.3.2/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.2.3.2/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/0.2.3.2
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

