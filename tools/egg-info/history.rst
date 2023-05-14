wok_code: 2.0.7.1 (2023-05-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Install run_odoo_debug


zerobug: 2.0.6 (2023-05-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Now all_tests is ignored
* [IMP] Build Odoo environment for Odoo 16.0


wok_code: 2.0.7 (2023-05-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] deply_odoo: new action git-push
* [REF] odoo_translation: new implementation
* [FIX] run_odoo_debug: minor fixes
* [NEW] do_git_checkout_new_branch: new command
* [IMP] install_python3_from_source: improvements
* [FIX] ssh.py: scp with port not 22


python_plus: 2.0.7 (2023-05-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: upgrade version for Odoo 16.0
* [REF] vem: partial refactoring
* [IMP] Mots coverage test


clodoo: 2.0.5 (2023-05-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py: minor fixes
* [IMP] odoord: odoo version 16.0


z0bug_odoo: 2.0.7.1 (2023-04-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: multiple action on the same records


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




