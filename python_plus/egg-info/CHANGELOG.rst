2.0.12 (2024-02-29)
~~~~~~~~~~~~~~~~~~~

* [IMP] New function str2bool()

2.0.11 (2024-02-05)
~~~~~~~~~~~~~~~~~~~

* [FIX] vem: show right python version if 3.10+
* [IMP] list_requirements.py improvements
* [IMP] new python version assignment from odoo version

2.0.10 (2023-07-18)
~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: werkzeug for Odoo 16.0
* [FIX] vem create: sometimes "virtualenv create" fails for python 2.7
* [IMP] pip install packages with use2to3 is backupgrdae to < 23

2.0.9 (2023-06-26)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: werkzeug for Odoo 16.0
* [IMP] list_requirements.py: best recognize mixed version odoo/python
* [FIX] vem: commands return application status

2.0.7 (2023-05-08)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: upgrade version for Odoo 16.0
* [REF] vem: partial refactoring
* [IMP] Mots coverage test

2.0.6 (2023-03-24)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: cryptography, pypdf2, requests & urllib3 version adjustment
* [IMP] list_requirements.py: pypdf and pypdf2 version adjustment
* [IMP] list_requirements.py: best resolution when versions conflict
* [IMP] vem: set list_requirements.py executable

2.0.5 (2022-12-23)
~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: refactoring version control
* [IMP] vem: now amend can check current version (with -f switch)

2.0.4 (2022-12-15)
~~~~~~~~~~~~~~~~~~

* [IMP] Package version adjustment
* [IMP] vem: amend show current package version
* [IMP] vem: no python2 warning in linux kernel 3
* [FIX] vem: best recognition of python version

2.0.3 (2022-11-08)
~~~~~~~~~~~~~~~~~~

* [IMP] npm management
* [IMP] compute_date: refdate may be a string

2.0.2.1 (2022-11-01)
~~~~~~~~~~~~~~~~~~~~

* [FIX] Ensure coverage 5.0+

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [FIX] vem: wrong behavior with > o < in version
* [IMP] list_requirements.py: "Crypto.Cipher": "pycrypto"

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.3 (2022-09-14)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: install package with list_requirements.py

2.0.0.2 (2022-09-10)
~~~~~~~~~~~~~~~~~~~~

* [FIX] vem: no input inquire

2.0.0.1 (2022-09-06)
~~~~~~~~~~~~~~~~~~~~

* [IMP] vem: new switch -d for Odoo dependencies path
* [FIX] vem: create with best package list
* [FIX] vem: install odoo/openerp


2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version
