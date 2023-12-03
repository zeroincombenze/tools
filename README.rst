============================
|Zeroincombenze| tools 2.0.4
============================

|license gpl|



Overview
========

Sparse python and bash source code

+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| Package         | Name                 | Brief                                                                                                                                                      | Area                      |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| clodoo          | check_4_seq.sh       | Check for postgres database index                                                                                                                          | maintenance               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | clodoo.py            | Massive operations on multiple Odoo DBs in cloud. It is used to create configurated Odoo DBs and to upgrade more DBs at the same time. No (yet) documented | maintenance               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | force_password.sh    | Force Odoo DB password                                                                                                                                     | maintenance               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | set_workers.sh       | Evaluate and set Odoo workers for best performance                                                                                                         | Deployment & maintenance  |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| lisa            | lisa                 | Linux Installer Simple App. LAMP and odoo server installer from scratch.                                                                                   | deployment                |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| odoo_score      | odoo_score.py        | Odoo ORM super core                                                                                                                                        | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | odoo_shell.py        | Odoo shell for Odoo versions from 6.1 to 13.0                                                                                                              | Development & maintenance |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| os0             |                      | Simple os interface checked for OpenVMS too                                                                                                                | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| python-plus     | python-plus          | Various features to python 2 and python 3 programs as integration of pypi future to help to port your code from Python 2 to Python 3                       | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | vem                  | Virtual Environment Manager: create, copy, move, merge and many other functions with virtual environments                                                  | Deployment & maintenance  |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | list_requirements.py | List pypi and bin packages for an Odoo installation                                                                                                        | deployment                |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| travis_emulator | travis               | Travis Emulator on local machine. Check your project before release on TravisCi                                                                            | testing                   |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| wok_code        | cvt_csv_to_rst.py    | Convert a csv file into rst text file with table inside                                                                                                    | documentation             |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | cvt_csv_to_xml.py    | Convert a csv file into xml file for Odoo module data                                                                                                      | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | cvt_script           | Make bash script to standard                                                                                                                               | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | gen_readme.py        | Generate README.rst, index.html and __openerp__.py ,documentation                                                                                          | documentation             |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | odoo_dependencies.py | Show Odoo module tree, ancestors and/or childs                                                                                                             | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | odoo_translation.py  | Load Odoo translation (deprecated, must be replaced by weblate)                                                                                            | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                 | please               | Developer shell                                                                                                                                            | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0bug_odoo      | z0bug_odoo           | Integration of zerobug and Odoo. Initially forked form OCA maintainer quality tools. It works with all Odoo version, from 6.1 to 13.0                      | testing                   |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0lib           |                      | General purpose bash & python library                                                                                                                      | development               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zar             | zar                  | Zeroincombenze Archive and Replica. Backup your Odoo DBs                                                                                                   | maintenance               |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zerobug         | zerobug              | testing & debug library                                                                                                                                    | testing                   |
+-----------------+----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+





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

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

z0bug_odoo: 2.0.13 (2023-12-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: now you can declare you own source data directory
* [IMP] TestEnv: file account.account.xlsx with l10n_generic_oca + some useful records
* [IMP] TestEnv: file account.tax.xlsx with some italian taxes for l10n_generic_oca
* [IMP] TestEnv: simple expression for data value


zerobug: 2.0.12 (2023-11-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] python2: has_args


zerobug: 2.0.11 (2023-11-19)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Disabled sanity_check
* [IMP] Disabled some deprecated switches
* [FIX] Coverage data file
* [IMP] zerobug: test function signature like unittest2
* [IMP] zerobug: no more execution for count


wok_code: 2.0.12.1 (2023-11-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] please install python, now can install python 3.10
* [IMP] arcangelo: new python version assignment from odoo version
* [IMP] please version: now show compare with last entry of history
* [FIX] please docs: faq
* [FIX] please help cwd
* [FIX] gen_readme.py: sometimes lost history
* [FIX] gen_readme.py: error reading malformed table
* [IMP] odoo_translation.py: new regression tests
* [FIX] odoo_translation.py: punctuation at the end of term
* [FIX] odoo_translation.py: first character case
* [FIX] odoo_translation.py: cache file format is Excel
* [FIX] run_odoo_debug: path with heading space
* [IMP] please test now can update account.account.xlsx


travis_emulator: 2.0.7 (2023-11-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Automatic python version for Odoo


python_plus: 2.0.10.1 (2023-11-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] new python version assignment from odoo version


clodoo: 2.0.8 (2023-11-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] Discard odoorpc 0.10 which does not work


zerobug: 2.0.10 (2023-11-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [REF] Partial refactoring
* [IMP] New functions assert* like unittest2
* [IMP] New switch -f failfast
* [IMP] Test signature like unittest2 and old zerobug signature
* [IMP] Test flow without return status (like unitest2)


z0lib: 2.0.8 (2023-10-16)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] parseopt


clodoo: 2.0.7 (2023-09-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Some fixes due old wrong code (id -> name)


z0bug_odoo: 2.0.12 (2023-09-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: validate_records with 2 identical template records


zar: 2.0.4 (2023-09-08)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Backup filestore
* [FIX] Remote copy to /dev/null


lisa: 2.0.3 (2023-09-07
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] lisa_bld_ods: fixes & improvements



zar: 2.0.3 (2023-09-06)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] DB name with hyphen (-)


wok_code: 2.0.12 (2023-08-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] gen_readme.py: minor fixes
* [IMP] gen_readme.py: manifest author priority
* [FIX] gen_readme.py: coverage in CHANGELOG.rst"
* [IMP] gen_readme.py: link to authors on README.rst and index.html
* [IMP] gen_readme.py: history tailoring keeps minimal 2 items
* [FIX] license_mgnt: best organization recognition
* [IMP] license_mgnt: powerp renamed to librerp
* [FIX] run_odoo_debug: no doc neither translate after test error
* [IMP] arcangelo: new rules
* [IMP] arcangelo: new git conflict selection
* [IMP] arcangelo: merge gen_readme.py formatting
* [IMP] arcangelo: new switch --string-normalization
* [FIX] deploy_odoo: minor fixes
* [FIX] odoo_translation: sometime did not translate
* [IMP] odoo_translation: best performance


z0lib: 2.0.7 (2023-07-20)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_traced return system exit code
* [IMP] run_traced: new rtime parameter to show rtime output
* [IMP] New main


python_plus: 2.0.10 (2023-07-18)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: werkzeug for Odoo 16.0
* [FIX] vem create: sometimes "virtualenv create" fails for python 2.7
* [IMP] pip install packages with use2to3 is backupgrdae to < 23


travis_emulator: 2.0.6 (2023-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] travis: check for dropped DB and abort if still exist
* [IMP] travis: action show as alias of show-log for please integration


oerplib3: 0.8.4 (2023-05-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] First porting


odoo_score: 2.0.6 (2023-04-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Import class models.Model


odoo_score: 2.0.5 (2023-03-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug.sh: moved to package wok_code


os0: 2.0.1 (2022-10-20)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Stable version


lisa: 2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] lisa_bld_ods: fixes & improvements


os0: 1.0.3.1 (2021-12-23)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] python compatibility



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

* `Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>`__


|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.4/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.4/man
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
