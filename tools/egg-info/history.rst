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
* [IMP] transodoo.py: minor improvements


zerobug: 2.0.5 (2023-03-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] travis_install_env: ensure list_requirements is executable
* [IMP] flake8 configuration
* [IMP] coveralls and codecov are not more dependenciesple


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

* [FIX] run_odoo_debug.sh: ODOO_COMMIT TEST not set when build template
* [IMP] run_odoo_debug.sh: simulate server_wide_modules parameter for Odoo 7.0-



zar: 2.0.1 (2023-02-25)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Remote bckdir different from local


wok_code: 2.0.6 (2023-02-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] ssh.py: -m -s switches accept path with user and host
* [IMP] deploy_odoo: new property status to display
* [IMP] deploy_odoo: new switches -l and -x
* [NEW] do_git_checkout_new_branch.py
* [IMP] do_migrate.py: new features



