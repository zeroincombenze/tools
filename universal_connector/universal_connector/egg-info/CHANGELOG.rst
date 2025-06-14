2.0.22 (2025-05-31)
~~~~~~~~~~~~~~~~~~~

* [FIX] arcangelo: sometimes wrong format .rst files
* [FIX] please translate: new algorithm
* [FIX] lint_2_compare: minor bug fixing
* [IMP] lint_2_compare: automatic detecting version from source path
* [IMP] run_odoo_debug: new -A switch
* [IMP] deploy_odoo: minor improvements
* [UPD] Esteem quality rate: new algorithm

2.0.21 (2025-04-26)
~~~~~~~~~~~~~~~~~~~

* [IMP] please translation: modified algorithm
* [FIX] run_odoo_debug: module replacements

2.0.20 (2025-03-01)
~~~~~~~~~~~~~~~~~~~

* [FIX] gen_readme.py: read-only repositories
* [FIX] gen_readme.py: new odoo14+ nomenclature
* [FIX] please: new odoo14+ nomenclature
* [FIX] run_odoo_debug: new odoo14+ nomenclature

2.0.19 (2025-03-01)
~~~~~~~~~~~~~~~~~~~

* [FIX] please python 3.9+
* [FIX] install_python_3_from_source.sh: fix bugs and improvements
* [FIX] ssh.py: store encrypted password
* [IMP] run_odoo_debug: now can replace modules
* [IMP] cvt_script executable
* [IMP] deploy_odooo: more improvements
* [IMP] please: minor improvements
* [IMP] please clen db: remove filestore directories too

2.0.18 (2024-07-10)
~~~~~~~~~~~~~~~~~~~

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

2.0.17 (2024-05-11)
~~~~~~~~~~~~~~~~~~~

* [FIX] odoo_translate.py various fixes
* [IMP] Log file of daemon process of test in tests/logs
* [IMP] run_odoo_debug: OCB repository does not search for other repositories
* [IMP] deploy_odoo now download empy repositories (to compatibility use --clean-empy-repo)

2.0.16 (2024-03-26)
~~~~~~~~~~~~~~~~~~~

* [FIX] odoo_translation.py: case correction
* [FIX] run_odoo_debug: sometimes crashes on OCB/addons modules
* [FIX] gen_readme.py: Odoo repository documentation
* [FIX] gen_readme.py: thumbnail figure
* [FIX] please docs: count assertions
* [FIX] please test: switch -K --no-ext-test
* [FIX] deploy_odoo: crash when clone existing directory
* [IMP] deploy_odoo: new switch --continue-after-error
* [FIX] deploy_odoo/wget_odoo_repositories: store github query in cache

2.0.15 (2024-02-17)
~~~~~~~~~~~~~~~~~~~

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

2.0.14 (2024-02-07)
~~~~~~~~~~~~~~~~~~~

* [FIX] Quality rating formula
* [FIX] please install python --python=3.7
* [IMP] please publish marketplace
* [IMP] read-only repository
* [IMP] arcangelo improvements
* [IMP] gen_readme.py manifest rewrite improvements
* [IMP] cvt_csv_coa.py improvements
* [IMP] please test with new switch -D
* [IMP] run_odoo_debug improvements

2.0.13 (2023-11-27)
~~~~~~~~~~~~~~~~~~~

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
