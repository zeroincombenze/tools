wok_code: 1.0.2.1.1 (2021-09-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] please replace: set generic python in executable files
[FIX] dist_pkg: install_dev not found




clodoo: 0.3.31.3 (2021-09-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py with python3 due wrong jsoblib dependency


wok_code: 1.0.2.1 (2021-08-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] gen_readme.py: search for authors in current README


clodoo: 0.3.31.2 (2021-08-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] odoorc: it does not use <git branch --show-current>


wok_code: 1.0.2.1 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] cvt_csv_coa.py: new command to manage Odoo CoA
[IMP] gen_readme.py: search for authors in current README


odoo_score: 1.0.2.1 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] odoo_shell.py: minor updates


clodoo: 0.3.33.4 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py: rcp login


zerobug: 1.0.1.4 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis_install_env: echo indented command
[IMP] travis_install_env: new travis command testdeps


z0bug_odoo: 1.0.4.3 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] travis_run_test: new command testdeps


wok_code: 1.0.2.1 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] please: action docs shows recent history
[IMP] gen_readme.py: show recent history
[FIX] topep8: parse .travis.yml


travis_emulator: 1.0.1.8 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis: clor change
[IMP] travis: new action testdeps
[FIX] travis: matrix selection


odoo_score: 1.0.2 (2021-08-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] Stable version


clodoo: 0.3.33.3 (2021-08-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] transodoo.xlsx: translation update


clodoo: 0.3.33.1 (2021-08-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] transodoo.xlsx: wrong translation of l10n_it_reverse_charge



zar: 1.3.35.3 (2021-08-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] pg_db_active: kill process


travis_emulator: 1.0.1.5 (2021-08-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] travis: summary return 1 if test failed or is broken
[IMP] travis: return status like summary
[IMP] travis: summary & show-log can show old logfile i.e.: travis summary old
[IMP] travis: osx emulatore return more info when error


clodoo: 0.3.31.16 (2021-08-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoorc: module list


clodoo: 0.3.31.15 (2021-08-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoorc: run in osx darwin


zerobug: 1.0.1.2 (2021-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] travis_run_pypi_test: run in osx darwin
[FIX] z0testrc: run in osx darwin


odoo_score: 1.0.1.4 (2021-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] run_odoo_debug: run in osx darwin


clodoo: 0.3.31.14 (2021-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoo_install_repository: run in osx darwin


wok_code: 1.0.2.1 (2021-08-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] please: changed the syntax of som actions
[IMP] pre-commit: regex var GIT_NO_CHECK with path to no check


travis_emulator: 1.0.1.4 (2021-08-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] devel_tools replaced by wok_code
[IMP] travis: summary return 1 if test failed


z0bug_odoo: 1.0.3.2 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] test data update


wok_code: 1.0.2.1 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[REF] Merged and renamed to wok_code


python_plus: 1.0.1.3 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: uninstall package with if package version with ">"


clodoo: 0.3.31.13 (2021-08-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] transodoo.py: tranlsation now can return None value
[IMP] transodoo.xlsx: upgrade translation



wok_code: 1.0.2.1 (2021-08-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] topep8: file list does not include .idea files
[IMP] please: action docs now set license file in current directory


wok_code: 1.0.2.1 (2021-08-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] gen_readme.py: parameter error


travis_emulator: 1.0.1.3 (2021-08-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP] Show virtual enviroment name in summary


z0bug_odoo: 1.0.3.1 (2021-07-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] test data format xlsx (it replaces csv)
* [IMP] value "\N" in data file for not value


z0bug_odoo: 1.0.3 (2021-07-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] new test data


wok_code: 1.0.2.1 (2021-07-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoo_translation.py: xlrd (no more supported) replaced by openpyxl


python_plus: 1.0.1.2 (2021-07-29)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: exec in current directory


odoo_score: 1.0.1.3 (2021-07-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] run_odoo_debug: -T and -k switches togheter
[FIX] odoo_score.py: crash with python 3 (due clodoo package)
[IMP] odoo_shell.py: removed old code


wok_code: 1.0.2.1 (2021-07-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] gen_readme.py: ignore setup directories
[IMP] gen_readme.py: new parameter -L to set local language (def it_IT)
[IMP] gen_readme.py: check for licenze incompatibility



lisa: 0.3.1.14 (2021-07-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX] lisa_bld: error for odoo 6.1 with server directory


z0bug_odoo: 1.0.2.3 (2021-07-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] test data upgrade


wok_code: 0.1.17.3 (2021-07-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] wget_odoo_repositories.py: best debug mode: check for branch


python_plus: 1.0.1.1 (2021-07-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] vem: best odoo path findind



