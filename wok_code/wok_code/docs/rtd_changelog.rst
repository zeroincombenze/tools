.. toctree::
   :maxdepth: 2

ChangeLog History
=================


2.1.0 (2026-07-10)
~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug: disable test on depending modules
* [FIX] gevent_port in run_odoo_debug.sh for Odoo 16+
* [FIX] Sometimes wrong db user was used
* [IMP] Install python2.7 in Ubuntu 26.04
* [IMP] Quality message on pypi packages
* [IMP] Quality message on pypi packages

2.0.23 (2025-08-14)
~~~~~~~~~~~~~~~~~~~

* [IMP] arcangelo became a pypi package
* [IMP] please install python: now can install python 3.12
* [FIX] please version does not add line at the end of file
* [FIX] please: best recognition of read-only repositories
* [FIX] please test: check on templates to use
* [FIX] No crash if invalid modules declaration
* [FIX] License declaration compatible with pypi

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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.1.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.1.0/man
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
