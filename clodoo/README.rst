=============
clodoo 2.0.14
=============



|Maturity| |license gpl|



Overview
========

Clodoo is a set of tools to manage to manage multiple Odoo installations with many DBs.

With clodoo you can do massive operations on 1 or more Odoo databases based on
different Odoo versions. Main operation are:

* create consistent database to run tests
* repeat consistent action on many db with same or different Odoo version
* repeat above actions on every new database

clodoo is also a PYPI package to simplify RPC connection to Odoo.
The PYPI package is a hub to oerplib and odoorpc packages, so generic python client
can execute any command to any Odoo version server (from 6.1 to 13.0)


odoorc: general purpose bash library
------------------------------------

The bash file odoorc is a general purpose Odoo library. It supplies some Odoo values from odoo_vid or from odoo directory.
Some values may depends by environment:

- ODOO_DB_USER is the rule to return db username (def odoo%(MAJVER)s)
- ODOO_GIT_HOSTNAME is the git hostname (def github.com)
- ODOO_GIT_SHORT -> regex of git organizzations with vid short name (def /(oca)/, see odoo-vid)

Usage:

    . odoorc
    RES=$(build_odoo_param PARAM odoo_vid [(search|DEBUG|default|tree|SERVER|<rptname>|<modname>)] [oca|zero|zero-http|zero-git|librerp|flectra] [(search|DEBUG|default|tree|SERVER)])

where:

    PARAM is one of (ALL|BIN|CONFN|DB_USER|DDIR|FLOG|FPID|FULLVER|FULL_SVCNAME|GIT_BRANCH|GIT_OPTS|GIT_ORG|GIT_ORGNM|GIT_PROT|GIT_URL|HOME|INVALID_MODNAMES|INVALID_MODNAMES_RE|LICENSE|LCONFN|MAJVER|MANIFEST|OCB_SUBDIRS|OCB_SUBDIRS_RE|OPTS_ASM|PARENTDIR|PKGNAME|PKGPATH|REPOS|ROOT|RORIGIN|RPCPORT|RUPSTREAM|SVCNAME|UPSTREAM|URL|URL_BRANCH|USER|VCS|VDIR|VENV)



Features
--------

+------------------------------------------------------------+-------------------------+
| Function                                                   | Note                    |
+------------------------------------------------------------+-------------------------+
| Manage version depending names                             | transodoo.py            |
+------------------------------------------------------------+-------------------------+
| Odoo general purpose library                               | odoorc                  |
+------------------------------------------------------------+-------------------------+
| Examples                                                   | example*.py             |
+------------------------------------------------------------+-------------------------+



Getting started
===============


Prerequisites
-------------

Zeroincombenze(R) tools requires:

* Linux Centos 7/8 or Debian 9/10/11 or Ubuntu 16/18/20/22/24
* python 2.7+, some tools require python 3.7+, best python 3.9+
* bash 5.0+



Installation
------------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install clodoo

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    [[ ! -d ./tools ]] && git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



Upgrade
-------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install --upgrade clodoo

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

2.0.14 (2025-06-14)
~~~~~~~~~~~~~~~~~~~

* [IMP] odoorc: new option NOLINK
* [IMP] odoorc: Odoo 17.0 and 18.0
* [IMP] powerp is not more a default gitorg
* [FIX] License declaration compatible with pypi
* [IMP+ python 3.11

2.0.13 (2024-08-22)
~~~~~~~~~~~~~~~~~~~

* [IMP] Depends on z0lib>=2.0.11

2.0.12 (2024-07-03)
~~~~~~~~~~~~~~~~~~~

* [FIX] Rpc with odoo < 10.0
* [IMP] It does no more depends on os0
* [IMP] Python 3.6 deprecated

2.0.11 (2024-03-31)
~~~~~~~~~~~~~~~~~~~

* [IMP] Parameters review
* [FIX] No file during pip install
* [FIX] Call with context Odoo 10.0+

2.0.10 (2024-03-26)
~~~~~~~~~~~~~~~~~~~

* [REF] Partial refactoring

2.0.9 (2024-02-02)
~~~~~~~~~~~~~~~~~~

* [IMP] odoorc improvements

2.0.8 (2023-11-16)
~~~~~~~~~~~~~~~~~~

* [FIX] Discard odoorpc 0.10 which does not work

2.0.7 (2023-09-26)
~~~~~~~~~~~~~~~~~~

* [FIX] Some fixes due old wrong code (id -> name)

2.0.6 (2023-07-10)
~~~~~~~~~~~~~~~~~~

* [IMP] Incorporated new pypi oerlib3
* [IMP] Discriminate http_port and xmlrpc_port to avoid mistake
* [IMP] New param IS_MULTI

2.0.5 (2023-05-08)
~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py: minor fixes
* [IMP] odoorc: odoo version 16.0

2.0.4 (2023-03-29)
~~~~~~~~~~~~~~~~~~

* [IMP] odoorc: minor improvements
* [IMP] odoorc: test for Odoo 16.0
* [IMP] transodoo.py: minor improvements

2.0.3 (2022-12-09)
~~~~~~~~~~~~~~~~~~

* [FIX] odoorc: GIT_BRANCH sometimes fails

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [FIX] odoorc: GITORGID and other value, sometimes are wrong

2.0.1.1 (2022-10-15)
~~~~~~~~~~~~~~~~~~~~

* [IMP] Minor improvements

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.3 (2022-10-06)
~~~~~~~~~~~~~~~~~~~~

* [IMP] odoorc: best virtual environment recognize
* [FIX] odoorc: SVCNAME

2.0.0.2 (2022-09-14)
~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: get data from setup.py od Odoo

2.0.0.1 (2022-09-06)
~~~~~~~~~~~~~~~~~~~~

* [IMP] list_requirements.py: new option -S for secure packages

2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [REF] Stable version



Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Authors
-------

* `SHS-AV s.r.l. <https://www.zeroincombenze.it>`__



Contributors
------------

* `Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>`__


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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.14/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.14/man
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
