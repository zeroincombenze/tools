=================
odoo_score 2.0.10
=================



|Maturity| |license gpl|



Overview
========

Odoo supercore

odoo_score is a library that extends the odoo orm functionality and makes available
a simple odoo shell even for older Odoo version.

Regression tests of this package do not guarantee full features coverage.
In order to complete all tests, it required to run test of the
Odoo module test_odoo_score-* in repository
`zerobug_test <https://github.com/zeroincombenze/zerobug-test.git>`__



Getting started
===============


Prerequisites
-------------

Zeroincombenze tools requires:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20/22
* python 2.7+, some tools require python 3.6+, best python 3.8+
* bash 5.0+



Installation
------------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install odoo_score

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

    pip install --upgrade odoo_score

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

2.0.10 (2024-08-21)
~~~~~~~~~~~~~~~~~~~

* [IMP] Depends on z0lib>=2.0.11

2.0.9 (2024-07-10)
~~~~~~~~~~~~~~~~~~

* [IMP] It does no more depends on os0
* [IMP] Python 3.6 deprecated

2.0.8 (2024-03-26)
~~~~~~~~~~~~~~~~~~

* [IMP] set_workers: no automatic discover for odoo multi
* [IMP] Purged old unused code
* [IMP] New odooctl command

2.0.7 (2024-02-05)
~~~~~~~~~~~~~~~~~~

* [REF] set_workers refactoring

2.0.6 (2023-04-16)
~~~~~~~~~~~~~~~~~~

* [FIX] Import class models.Model

2.0.5 (2023-03-23)
~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug.sh: moved to package wok_code

2.0.4 (2023-01-13)
~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug.sh: test creates log

2.0.3 (2022-11-11)
~~~~~~~~~~~~~~~~~~

* [IMP] odoo_score: implementation of models and fields for Odoo 8-0+ modules

2.0.2 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [FIX] run_odoo_debug: test function improvements
* [IMP] run_odoo_debug: ODOO_COMMIT_TEST

2.0.1.1 (2022-10-13)
~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug: python stub
* [FIX] run_odoo_debug: crash in sime rare cases

2.0.1 (2022-10-12)
~~~~~~~~~~~~~~~~~~

* [IMP] stable version

2.0.0.3 (2022-10-05)
~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odoo_debug: test via pycharm
* [FIX] run_odoo_debug: concurrent tests

2.0.0.2 (2022-09-22)
~~~~~~~~~~~~~~~~~~~~

* [IMP] run_odo_debug: test with random rpcport for multiple tests
* [IMP] odoo_shell.py: new actions

2.0.0.1 (2022-09-07)
~~~~~~~~~~~~~~~~~~~~

* [FIX] run_odo_debug with debug
* [IMP] run_odoo_debug: experimental debug via pycharm

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

* `Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>`__


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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.10/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.10/man
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
