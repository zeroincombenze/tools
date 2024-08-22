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

travis_emulator: 2.0.10 (2024-08-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Minor improvements


clodoo: 2.0.13 (2024-08-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Depends on z0lib>=2.0.11


zerobug: 2.0.18 (2024-08-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Some function now are move in z0lib>=2.0..1
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


python_plus: 2.0.15 (2024-07-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem.py: some packages line invoice2data on python 10.0
* [FIX] list_requirements.py: packages with similar name (numpy -> numpy-financial)
* [IMP] list_requirements.py: package versions improvements


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


z0bug_odoo: 2.0.16 (2024-02-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: nested +multi fields with Odoo cmd


wok_code: 2.0.15 (2024-02-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] do_git_checkout_new_branch: ignore symbolic links
* [FIX] deploy_odoo: minor fixes
* [IMP] do_git_checkout_new_branch: oddo 17.0
* [IMP] deploy_odoo: new action amend
* [IMP] deploy_odoo: new switch to link repositories
* [IMP] deploy_odoo: removed deprecated switches
* [IMP] New repositories selection
* [IMP] arcangelo improvements: new tests odoo from 8.0 to 17.0
* [IMP] arcangelo improvements: test odoo from 8.0 to 17.0
* [IMP] arcangelo switch -lll
* [IMP] arcaneglo: rules reorganization
* [IMP] arcangelo: trigger management and new param ctx
* [IMP] arcangelo: new switch -R to select rules to apply


wok_code: 2.0.14 (2024-02-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Quality rating formula
* [FIX] please install python --python=3.7
* [IMP] please publish marketplace
* [IMP] read-only repository
* [IMP] arcangelo improvements
* [IMP] gen_readme.py manifest rewrite improvements
* [IMP] cvt_csv_coa.py improvements
* [IMP] please test with new switch -D
* [IMP] run_odoo_debug improvements


python_plus: 2.0.11 (2024-02-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: show right python version if 3.10+
* [IMP] list_requirements.py improvements
* [IMP] new python version assignment from odoo version


odoo_score: 2.0.7 (2024-02-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [REF] set_workers refactoring


clodoo: 2.0.9 (2024-02-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] odoorc improvements


z0lib: 2.0.9 (2024-02-01)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Internal matadata


zerobug: 2.0.14 (2024-01-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] build_cmd: enable coverage on sub process
* [FIX] Re-enable coverage statistics
* [FIX] Printing message: right sequence


z0bug_odoo: 2.0.15 (2024-01-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Documentation typo corrections
* [IMP] Date range file .xlsx for TestEnv
* [IMP] TestEnv: local data dir new rules
* [FIX] TestEnv: 3 level xref, sometime fails with "_" in module name
* [FIX] TestEnv: caller environment more than 1 level
* [FIX] TestEnv: sometime is_action() fails
* [FIX] TestEnv: wizard active model
* [FIX] TestEnv: wizard module name is current module under test
* [IMP] TestEnv: binding model in view for Odoo 11.0+
* [IMP] TestEnv: write with xref can update xref id
* [IMP] TestEnv: warning if no setUp() declaration
* [IMP] TestEnv: resource_download, now default filed name is "data"



z0bug_odoo: 2.0.14 (2023-12-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: commit odoo data became internal feature
* [IMP] TestEnv: test on model asset.asset
* [IMP] TestEnv: detail external reference coding free
* [IMP] TestEnv: empty currency_id is set with company currency
* [FIX] TestEnv: minor fixes in mixed environment excel + zerobug
* [FIX] TestEnv: sometimes external.KEY did not work
* [FIX] TestEnv: 3 level xref fails when module ha "_" in its name
* [IMP] _check4deps.py: documentation clearing


zerobug: 2.0.13 (2023-12-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] python2: argument signature
* [IMP] build_os_tree: compatible with unittest2
* [IMP] remove_os_tree: compatible with unittest2


z0bug_odoo: 2.0.13 (2023-12-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: now you can declare you own source data directory
* [IMP] TestEnv: file account.account.xlsx with l10n_generic_oca + some useful records
* [IMP] TestEnv: file account.tax.xlsx with some italian taxes for l10n_generic_oca
* [IMP] TestEnv: simple expression for data value


travis_emulator: 2.0.8 (2023-12-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Translation excel file names



zerobug: 2.0.12 (2023-11-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] python2: has_args


wok_code: 2.0.13 (2023-11-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


zerobug: 2.0.11 (2023-11-19)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Disabled sanity_check
* [IMP] Disabled some deprecated switches
* [FIX] Coverage data file
* [IMP] zerobug: test function signature like unittest2
* [IMP] zerobug: no more execution for count


travis_emulator: 2.0.7 (2023-11-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Automatic python version for Odoo


clodoo: 2.0.8 (2023-11-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Discard odoorpc 0.10 which does not work


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


lisa: 2.0.3 (2023-09-07)
~~~~~~~~~~~~~~~~~~~~~~~~

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


oerplib3: 0.8.4 (2023-05-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] First porting


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
