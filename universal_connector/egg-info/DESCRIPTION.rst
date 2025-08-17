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
* Robust and easy to use (coverage >85%, >1K testpoints)
