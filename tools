============================
|Zeroincombenze| tools 2.0.6
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
|                 | odoo_shell.py        | Odoo shell for Odoo versions from 6.1 to 17.0                                                                                                              | Development & maintenance |
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
| z0bug_odoo      | z0bug_odoo           | Integration of zerobug and Odoo. Initially forked form OCA maintainer quality tools. It works with all Odoo version, from 6.1 to 17.0                      | testing                   |
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

Zeroincombenze(R) tools requires:

* Linux Centos 7/8 or Debian 9/10/11 or Ubuntu 16/18/20/22/24
* python 2.7+, some tools require python 3.7+, best python 3.9+
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

z0lib: 2.0.15 (2025-01-18)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] simulate get_metadat in test environment


travis_emulator: 2.0.10 (2025-01-18)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Minor improvements
* [IMP] Python 3.10


z0lib: 2.0.14 (2025-01-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] os_system minor fixes


python_plus: 2.0.16 (2025-01-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem.py: some packages line invoice2data on python 10.0
* [FIX] vem: upgrade wkhtmltopdf naming
* [FIX] list_requirements.py: packages with similar name (numpy -> numpy-financial)
* [IMP] list_requirements.py: package versions improvements


oerplib3: 1.0.0 (2025-01-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Python 3.12 porting


zar: 2.0.7 (2024-12-30)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] pg_db_active with port for postgresql multi-version


z0lib: 2.0.13 (2024-10-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] os_system minor fixes


lisa: 2.0.6 (2024-10-04)
~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] lisa_bld_ods: replaced path owned by odoo


python_plus: 2.0.15 (2024-10-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem.py: some packages line invoice2data on python 10.0
* [FIX] list_requirements.py: packages with similar name (numpy -> numpy-financial)
* [IMP] list_requirements.py: package versions improvements


z0lib: 2.0.12 (2024-08-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] os_system with verbose


wok_code: 2.0.19 (2024-08-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] please python 3.9+
* [FIX] install_python_3_from_source.sh: fix bugs and improvements
* [FIX] ssh.py: store encrypted password
* [IMP] run_odoo_debug: now can replace modules
* [IMP] cvt_script executable
* [IMP] deploy_odooo: more improvements
* [IMP] please: minor improvements
* [IMP] please clen db: remove filestore directories too


clodoo: 2.0.13 (2024-08-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Depends on z0lib>=2.0.11


zerobug: 2.0.18 (2024-08-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Some function now are move in z0lib>=2.0.12
* [IMP] Python 3.6 deprecated


zar: 2.0.6 (2024-08-21)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] pg_db_active with port for postgresql multi-version


z0bug_odoo: 2.0.21 (2024-08-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Depends on z0lib>=2.0.11


oerplib3: 0.8.5 (2024-08-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Python 3.10 porting


odoo_score: 2.0.10 (2024-08-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Depends on z0lib>=2.0.11


lisa: 2.0.5 (2024-08-18)
~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] lisa_bld_ods: module replacements


lisa: 2.0.4 (2024-08-12)
~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] lisa_bld_ods: fixes & improvements


z0lib: 2.0.11 (2024-07-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] New function os_system
* [IMP] New function print_flush


z0bug_odoo: 2.0.20 (2024-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Offical _check4deps_.py
* [FIX] No more depends on os0
* [IMP] Python 3.6 deprecated


wok_code: 2.0.18 (2024-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] please python 3.9+
* [FIX] deploy_odoo update addons_path in config file
* [FIX] deploy_odoo update that requires checkout, requires -f switch
* [FIX] deploy_odoo default branch from repo in actions different from clone
* [IMP] deploy_odoo new action merge
* [IMP] deploy_odoo new action new-branch
* [IMP] deploy_odoo: new features on status
* [FIX] gen_readme now check for images value for marketplace
* [IMP] gen_readme now can use .jpg and .gif images
* [IMP] new pg_requirements.py
* [IMP] run_odoo_debug checks fro pg_requirements from __manifest__.rst
* [FIX] No more depends on os0
* [IMP] Python 3.6 deprecated


travis_emulator: 2.0.9 (2024-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] It does no more depends on os0
* [IMP] Python 3.6 deprecated


odoo_score: 2.0.9 (2024-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] It does no more depends on os0
* [IMP] Python 3.6 deprecated


python_plus: 2.0.14 (2024-07-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: package versions improvements
* [IMP] Python 3.6 deprecated


zerobug: 2.0.17 (2024-07-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] z0testlib: no more depends on os0
* [IMP] Python 3.6 deprecated


z0lib: 2.0.10 (2024-07-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] run_traced improvements
* [IMP] Python 3.6 deprecated


clodoo: 2.0.12 (2024-07-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Rpc with odoo < 10.0
* [IMP] It does no more depends on os0
* [IMP] Python 3.6 deprecated


zar: 2.0.5 (2024-05-22)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] zar_upd


zerobug: 2.0.16 (2024-05-14)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] z0testlib: no crash without coverage

~~~~~~~~~~~~~~~~~~~

* [FIX] build_cmd: command not in scripts directory


z0bug_odoo: 2.0.19 (2024-05-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Colored test results


wok_code: 2.0.17 (2024-05-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] odoo_translate.py various fixes
* [IMP] Log file of daemon process of test in tests/logs
* [IMP] run_odoo_debug: OCB repository does not search for other repositories
* [IMP] deploy_odoo now download empy repositories (to compatibility use --clean-empy-repo)


python_plus: 2.0.13 (2024-05-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: package versions improvements
* [FIX] list_requirements.py: in some rare cases wrong version to apply (factur-x)
* [IMP] vem: now pip<23 and setuptools<58 are applied just if neeeded
* [IMP] vem: pip is always updated to last version


z0bug_odoo: 2.0.18 (2024-04-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: no data loaded in some cases
* [FIX[ TestEnv: resource_edit manage read-only fields
* [QUA] TestEnv coverage 93% by test_test_env in https://github.com/zeroincombenze/zerobug-test


clodoo: 2.0.11 (2024-03-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Parameters review
* [FIX] No file during pip install
* [FIX] Call with context Odoo 10.0+


wok_code: 2.0.16 (2024-03-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] odoo_translation.py: case correction
* [FIX] run_odoo_debug: sometimes crashes on OCB/addons modules
* [FIX] gen_readme.py: Odoo repository documentation
* [FIX] gen_readme.py: thumbnail figure
* [FIX] please docs: count assertions
* [FIX] please test: switch -K --no-ext-test
* [FIX] deploy_odoo: crash when clone existing directory
* [IMP] deploy_odoo: new switch --continue-after-error
* [FIX] deploy_odoo/wget_odoo_repositories: store github query in cache


odoo_score: 2.0.8 (2024-03-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] set_workers: no automatic discover for odoo multi
* [IMP] Purged old unused code
* [IMP] New odooctl command


clodoo: 2.0.10 (2024-03-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [REF] Partial refactoring


python_plus: 2.0.12 (2024-02-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] New function str2bool()


z0bug_odoo: 2.0.17 (2024-02-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: minor improvements
* [FIX] TestEnv: crash if no account.journal in data
* [IMP] Data with date range 2024


os0: 2.0.1 (2022-10-20)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Stable version


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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.6/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.6/man
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
