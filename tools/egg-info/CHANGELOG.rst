z0lib: 2.0.7 (2023-07-20)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_traced return system exit code
* [IMP] run_traced: new rtime paramater, show rtime output


python_plus: 2.0.10 (2023-07-18)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: werkzeug for Odoo 16.0
* [FIX] vem create: sometimes "virtualenv create" fails for python 2.7


zerobug: 2.0.9 (2023-07-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] zerobug implementation with unittest
* [FIX] z0testlib.py: build_odoo_env, odoo-bin / openerp-server are executable
* [FIX] z0testlib.py: minor fixes


wok_code: 2.0.10 (2023-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


travis_emulator: 2.0.6 (2023-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] travis: check for dropped DB and abort if still exist
* [IMP] travis: action show as alias of show-log for please integration


clodoo: 2.0.6 (2023-07-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Incorporated new pypi oerlib3
* [IMP] Discriminate http_port and xmlrpc_port to avoid mistake
* [IMP] New param IS_MULTI


z0bug_odoo: 2.0.10 (2023-07-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: new feature, external reference with specific field value
* [REF] TestEnv: tomany casting refactoring


wok_code: 2.0.9 (2023-06-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_odoo_debug: recognize 'to upgrade' and 'to install' states
* [FIX] run_odoo_debug: check for dropped DB and abort if still exist
* [REF] odoo_translation: refactoring
* [REF] please: refactoring
* [IMP] deploy_odoo: new brief for status
* [IMP] deploy_odoo: new action unstaged e new status format
* [IMP] do_migrate renamed to arcangelo
* [IMP] gen_readme.py: manage CHANGELOG.rst too
* [IMP] argangelo: refactoring to run inside pre-commit


python_plus: 2.0.9 (2023-06-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: werkzeug for Odoo 16.0
* [IMP] list_requirements.py: best recognize mixed version odoo/python
* [FIX] vem: commands return application status


z0bug_odoo: 2.0.9 (2023-06-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: sometimes, validate_records does not match many2one fields
* [FIX[ TestEnv: sometime crash in wizard on Odoo 11.0+ due inexistent ir.default
* [FIX] TestEnv: default value in wizard creation, overlap default function
* [FIX] TestEnv: record not found for xref of other group
* [IMP] TestEnv: resource_bind is not more available: it is replaced by resource_browse


zar: 2.0.2 (2023-05-14)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] reassing_owner accept db_port


oerplib3: 0.8.4 (2023-05-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] First porting


odoo_score: 2.0.6 (2023-04-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Import class models.Model


os0: 2.0.1 (2022-10-20)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Stable version



lisa: 2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] liba_bld_ods: fixes & improvements



