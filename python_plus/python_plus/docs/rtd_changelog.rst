.. toctree::
   :maxdepth: 2

ChangeLog History
=================


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

|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Mature-green.png
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
