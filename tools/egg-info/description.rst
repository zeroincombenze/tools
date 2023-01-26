Multi-purpose python & bash tools
---------------------------------

Multi-purpose python and bash source code.

These tools help to cover the following areas of software:

* Odoo deployment
* Odoo database maintenance (creation and upgrade, massive)
* Odoo database profiling (auto)
* Database check (auto & massive)
* Development
* Documentation
* Testing

You can find more info at https://zeroincombenze-tools.readthedocs.io/

Compatibility
~~~~~~~~~~~~~

These tools are designed to be used on Linux platforms.
They are tested on following distros:
* Ubuntu: from 12.0 to 20.0
* Debian: from 8.0 to 10.0
* CentOS: from 7 to 8
Currently the osx Darwin is in testing.

Components
~~~~~~~~~~

.. $include description_pkgs.csv


Odoo vid
~~~~~~~~

The odoo_vid is the name of one specific Odoo configuration in multi instances
environment. It is mainly the directory for the specific Odoo instance.
Imagine a scenario with different Odoo instances running on the same host.
This is the development environment or the test environment.
Every instance of Odoo must have an own configuration file and packages.
Based on configuration file, every Odoo instance must have a own xmlrcp port,
db user, log file, pid file, etcetera.

The odoo_vid provides a simple way to manage multiple Odoo instance.
Supplying odoo_vid you select the specific parameters values just in one item.

The odoo_vid item is composed by:

* Prefix "VENV" if virtual environment (deprecated)
* Prefix V to identify main instance (deprecated)
* Odoo distribution (for organizations which have short name)
* Odoo version (full version or major version)
* Odoo distribution (all organizations)
* User specific identification

Odoo distribution may be one of: librerp,oca,zero or nothing

Odoo version is the Odoo specific version; it is one value of:
16.0 15.0 14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1

Examples of valid odoo_vid:

* 12.0 -> Odoo 12.0, unidentified distribution
* oca14 -> Odoo 14.0, distribution oca (short name)
* librerp6 -> Odoo 6.1, distribution librerp (short name)
* odoo14-oca -> Odoo 14.0, distribution oca (full name)
* odoo12-devel -> Odoo 12.0, odoo distribution, user identification "devel"

Based on above information, tool software can assume the right value of specific Odoo instance.

This table shows the Odoo parameter values based on odoo_vid;
please notice the symbol PUID is the personal user identification,
symbol %M means Odoo major version and %V Odoo full version.

.. $include description_vid.csv
