z0bug_odoo: 2.0.5 (2023-01-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: in some rare cases, wizard crashes
* [NEW] TestEnv: get_records_from_act_windows()
* [IMP] TestEnv: resource_make now capture demo record if available
* [IMP] TestEnv: resource is not required for declared xref
* [IMP] TestEnv: self.module has all information about current testing module
* [IMP] TestEnv: conveyance functions for all fields (currenly jsust for account.payment.line)
* [IMP] TestEnv: fields many2one accept object as value
* [IMP] TestEnv: function validate_records() improvements
* [FIX] TestEnv: company_setup, now you can declare bank account
* [IMP] TesEnv: minor improvements


python_plus: 2.0.5.1 (2023-01-20)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: cryptography, pypdf2, requests & urllib3 version adjustment


z0bug_odoo: 2.0.4 (2023-01-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: resource_create does not duplicate record
* [FIX] TestEnv: resource_write after save calls write() exactly like Odoo behavior
* [NEW] TestEnv: new function field_download()
* [NEW] TestEnv: new function validate_records()
* [IMP] TestEnv: convert_to_write convert binary fields too
* [IMP] TestEnv: minor improvements


wok_code: 2.0.5 (2023-01-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] please: wep now delete old travis-emulator logs
* [IMP] install_python_3_from_source.sh: now can install python 3.9
* [IMP] please: action docs, minor improvements
* [IMP] deploy_odoo: format output list


odoo_score: 2.0.4 (2023-01-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug.sh: test creates log



z0bug_odoo: 2.0.3 (2022-12-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: more debug messages
* [IMP] TestEnv: more improvements
* [FIX] TestEnv: sometime crashes if default use context
* [FIX] TestEnv: bug fixes


python_plus: 2.0.5 (2022-12-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: refactoring version control
* [IMP] vem: now amend can check current version (with -f switch)


z0lib: 2.0.3 (2022-12-22)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_traced: --switch sometime crashes


z0lib: 2.0.2.1 (2022-12-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_traced: alias function


python_plus: 2.0.4 (2022-12-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Package version adjustment
* [IMP] vem: amend show current package version
* [IMP] vem: no python2 warning in linux kernel 3
* [FIX] vem: best recognition of python version


travis_emulator: 2.0.3.1 (2022-12-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Added python 3.9 to test
* [IMP] Detect python versions from setup.py


z0bug_odoo: 2.0.2 (2022-12-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Automatic conversion of integer into string for 'char' fields
* [IMP] TestEnv


wok_code: 2.0.4 (2022-12-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] deploy_odoo: update from path
* [FIX] build_cmd: best recognition of python version
* [FIX] set_python_version.sh: best recognition of python version


travis_emulator: 2.0.3 (2022-12-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Best python version recognition


clodoo: 2.0.3 (2022-12-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] odoorc: GIT_BRANCH sometimes fails


zerobug: 2.0.4 (2022-12-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_pypi_test: best recognition of python version
* [FIX] build_cmd: best recognition of python version
* [FIX] travis_install_env: ensure coverage version
* [IMP] odoo environment to test more precise


z0lib: 2.0.2 (2022-12-07)
~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] best recognition of python version
* [FIX] run_traced: fail with python 2



