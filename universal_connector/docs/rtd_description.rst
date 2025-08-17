.. toctree::
   :maxdepth: 2

Overview
========


Universal Connector is a powerful suite to support any kind of bi-directional electronic data interchange.

The suite is designed to multiple purposes:

    #. It can **Connect Odoo just in time** with many kinds of software instances (like OCA connector inherited modules)
    #. It can **migrate Odoo database** from a version to another (like Odoo EE migration service or OCA Openupgrade)
    #. It can **import data** from files in specific location using user configuration (powerful alternative to standard import)
    #. It provides a strong support to **migrate database from other software** into a fresh Odoo installation
    #. You can **populate the demo and test environment in very easy way**, from file and/or another Odoo database, in test > stage > production lifecycle
    #. You can create an **Odoo cluster instance**

Just in time connector
----------------------

Universal Connector can work like OCA Connector and can provide the same functionality. However, Universal Connector
and OCA Connector have a very different philosophy.

Universal Connector is a complete EDI environment, configurable via user interface; therefore, most behavior changes
do not require code updates.

Moreover Universal Connector  is not a monolithic software but it is a suite based on an EDI server and many
additional components to adapt synchronization workflow. You can also write your own addons for specific jobs.


Odoo database migration
-----------------------

Universal Connector can **migrate an Odoo database** like Odoo EE migration service or Openupgrade with some useful
features:

#. You can migrate database **without needing to stop customer activities**
#. You can try and retry the migration process
#. Log messages can help you to solve every trouble
#. You can migrate your specific module data

Import data
-----------

Universal Connector, with csv protocol, can act to **import data** from files in specific location and it is a
powerful alternative to standard import because importing before create a new record is able to search if record
is already present in database.

Odoo cluster
------------

Universal Connector has to capacity to create an **Odoo cluster**. Real time synchronization makes possible
to exchange data between two Odoo instances running on separate hosts.

This feature is not available with Standard Odoo.

Suite properties
----------------

* Multi-backend interchange
* Multi-protocols, like JSON, XMLRPC and CSV
* Push and/or Pull logic
* Many2one, One2Many and Many2Many acquired with remote references
* Recognition by external reference (only remote Odoo)
* Updatable configuration by GUI
* Anti-recurse checks
* Two phases creating in order to keep hierarchical record structure
* Integrated rules to database migration for Odoo since 6.1
* Configurable protection rules

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
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-1.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/1.3.16/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-1.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/1.3.16/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-1.svg
    :target: https://erp1.zeroincombenze.it
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
