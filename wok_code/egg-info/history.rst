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
~~~~~~~~~~~~~~~~~~~~

* [IMP] Clearing code

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~~~

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
