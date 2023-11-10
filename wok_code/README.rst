===============
wok_code 2.0.12
===============



|Maturity| |license gpl|



Overview
========

Various tools at your fingertips.

The available tools are:

* cvt_csv_2_rst.py: convert csv file into rst file
* cvt_csv_2_xml.py: convert csv file into xml file
* cvt_script: parse bash script and convert to meet company standard
* gen_readme.py: generate documentation files, mainly README.rst
* odoo_dependency.py: show odoo dependencies and/or Odoo module tree
* odoo_translation.py: manage Odoo translation
* pep8: parse source .py file to meet pep8 and convert across Odoo versions
* please: developer shell
* wget_odoo_repositories.py: get repository names from github.com



Usage
=====

Module usage
------------



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

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install wok_code

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

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install --upgrade wok_code


Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

2.0.12 (2023-08-29)
~~~~~~~~~~~~~~~~~~~

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

2.0.10 (2023-07-10)
~~~~~~~~~~~~~~~~~~~

* [IMP] gen_readme.py: do not create .bak file; now it can be used in pre-commit process
* [IMP] please replace now do "please docs" before
* [IMP] please docs now do "please clean" after
* [IMP] please lint and zerobug now do "pre-commit run" before (--no-verify)
* [IMP] please test and zerobug now do "please translate" after (--no-translate)
* [IMP] please update: new switches --vme --odoo-venv
* [IMP] please clean db: new action replace old wep-db
* [IMP] please version: new interface
* [IMP] please show docs: new interface
* [REF] run_odoo_debug: partial refactoring
* [IMP] run_odoo_debug: new switch --daemon
* [IMP] arcangelo: new swicth --string-normalization
* [FIX] please test / run_odoo_debug: minor fixes

2.0.9 (2023-06-26)
~~~~~~~~~~~~~~~~~~

* [FIX] run_odoo_debug: recognize 'to upgrade' and 'to install' states
* [FIX] run_odoo_debug: check for dropped DB and abort if still exist
* [REF] odoo_translation: refactoring
* [REF] please: refactoring
* [IMP] deploy_odoo: new brief for status
* [IMP] deploy_odoo: new action unstaged e new status format
* [IMP] do_migrate renamed to arcangelo
* [IMP] gen_readme.py: manage CHANGELOG.rst too
* [IMP] argangelo: refactoring to run inside pre-commit

2.0.8 (2023-05-09)
~~~~~~~~~~~~~~~~~~

* [FIX] Install run_odoo_debug
* [FIX] Install do_git_ignore
* [IMP] lint_2_compare: ignore odoo/openerp test string and LICENSE files
* [IMP] lint_2_compare: new switch ---purge do not load identical files (quick diff)

2.0.7 (2023-05-08)
~~~~~~~~~~~~~~~~~~

* [IMP] deply_odoo: new action git-push
* [REF] odoo_translation: new implementation
* [FIX] run_odoo_debug: minor fixes
* [NEW] do_git_checkout_new_branch: new command
* [IMP] install_python3_from_source: improvements
* [FIX] ssh.py: scp with port not 22

2.0.6 (2023-02-23)
~~~~~~~~~~~~~~~~~~

* [IMP] ssh.py: -m -s switches accept path with user and host
* [IMP] deploy_odoo: new property status to display
* [IMP] deploy_odoo: new switches -l and -x
* [NEW] do_git_checkout_new_branch.py
* [IMP] do_migrate.py: new features
* [IMP] run_odoo_debug.sh imported from odoo_score
* [FIX] run_odoo_debug.sh: ODOO_COMMIT TEST not set when build template
* [IMP] run_odoo_debug.sh: simulate server_wide_modules parameter for Odoo 7.0-


2.0.5 (2023-01-13)
~~~~~~~~~~~~~~~~~~

* [IMP] please: wep now delete old travis-emulator logs
* [IMP] install_python_3_from_source.sh: now can install python 3.9
* [IMP] please: action docs, minor improvements
* [IMP] deploy_odoo: format output list

2.0.4 (2022-12-09)
~~~~~~~~~~~~~~~~~~

* [FIX] deploy_odoo: update from path
* [FIX] build_cmd: best recognition of python version
* [FIX] set_python_version.sh: best recognition of python version

2.0.3 (2022-11-22)
~~~~~~~~~~~~~~~~~~

* [REF] odoo_translation

2.0.2.1 (2022-10-31)
~~~~~~~~~~~~~~~~~~~~

* [IMP] lint_2_compare: ignoring .git .idea egg-info and setup directories
* [IMP] lint_2_compare: new ignore switches
* [FIX] please translate: do not execute export

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [IMP] Clearing code

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] minor improvements

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.4 (2022-10-05)
~~~~~~~~~~~~~~~~~~~~

* [IMP] New lint_2_compare command
* [IMP] odoo_dependecies.py: minor upgrade

2.0.0.3 (2022-09-14)
~~~~~~~~~~~~~~~~~~~~

* [FIX] deploy_odoo: show actual branch and organization
* [FIX] deploy_odoo: update read from directory
* [IMP] deploy_odoo: new command list repo info
* [IMP] deploy_odoo: new feature link to repositories

2.0.0.2 (2022-09-10)
~~~~~~~~~~~~~~~~~~~~

* [FIX] deploy_odoo: add path in addons_path of directory exists
* [FIX] deploy_odoo: clone oca repositories with --single-branch option
* [IMP] manage_pypi: improvements
* [FIX] please lint|test

2.0.0.1 (2022-09-07)
~~~~~~~~~~~~~~~~~~~~

* [FIX] please test: with debug

2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [REF] Refactoring



Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Authors
-------

* SHS-AV s.r.l. <https://www.zeroincombenze.it>



Contributors
------------

* Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>


|
|

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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.12/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.12/man
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
