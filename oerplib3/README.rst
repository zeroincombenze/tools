================
oerplib3 2.0.0.5
================



|Maturity| |license gpl|



Overview
========

OERPLib3 is a Python module providing an easy way to pilot
your OpenERP and Odoo servers through RPC.

It is a fork for python3 of `OERPLib project <https://github.com/osiell/oerplib>`__
by Sébastien Alix who have not participated to development of this module.



Features
--------

+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| Oerplib3                                                                                 | Oerplib                                                | OdooRPC                                    |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| XML-RPC protocols                                                                        |  XML-RPC and (legacy) Net-RPC protocols                | JSON RPC                                   |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| Transfer from Odoo >= 6.1 <= 9.0 to Odoo >= 11.0                                         | Transfer from Odoo >= 6.1 <= 9.0 to Odoo >= 6.1 <= 9.0 | Transfer from Odoo >= 10.0 to Odoo >= 10.0 |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| access to all methods proposed by a model class (even browse)                            | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| ability to use named parameters with such methods (Odoo >= 6.1)                          | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| user context automatically sent (Odoo >= 6.1) providing support for internationalization | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| browse records                                                                           | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| execute workflows                                                                        | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| manage databases                                                                         | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| reports downloading                                                                      | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+
| inspection capabilities                                                                  | |same|                                                 | |same|                                     |
+------------------------------------------------------------------------------------------+--------------------------------------------------------+--------------------------------------------+



Usage
=====

This module work exactly like original
`OERPLib <https://github.com/osiell/oerplib>`__

::

    import oerplib3 as oerplib

    # Prepare the connection to the server
    oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=8069)

    # Check available databases
    print(oerp.db.list())

    # Login (the object returned is a browsable record)
    user = oerp.login('user', 'passwd', 'db_name')
    print(user.name)            # name of the user connected
    print(user.company_id.name) # the name of its company

    # Simple 'raw' query
    user_data = oerp.execute('res.users', 'read', [user.id])
    print(user_data)

    # Use all methods of an OSV class
    order_obj = oerp.get('sale.order')
    order_ids = order_obj.search([])
    for order in order_obj.browse(order_ids):
        print(order.name)
        products = [line.product_id.name for line in order.order_line]
        print(products)

    # Update data through a browsable record
    user.name = "Brian Jones"
    oerp.write_record(user)



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

    pip install oerplib3

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

    pip install --upgrade oerplib3

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

0.8.5 (2024-08-21)
~~~~~~~~~~~~~~~~~~

* [FIX] Python 3.10 porting

0.8.4 (2023-05-06)
~~~~~~~~~~~~~~~~~~

* [FIX] First porting



FAQ
---

**Why this module was forked from OERPlib?**

OERPlib runs just with python2 and the author did not migrate
package on python3

**Why I should use this module? Was it better to use OdooRPC?**

OdooRPC runs on python3 but it does not support Odoo xmlrpc protocol.
So, if you have to read data from an old Odoo version database, you have to
use OERPlib3.



Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Authors
-------

* Sébastien Alix <False>
* `SHS-AV s.r.l. <https://www.zeroincombenze.it>`__



Contributors
------------

* `Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>`__


|
|

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-black.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.0/man
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
