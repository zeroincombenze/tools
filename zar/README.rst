=========
zar 2.0.7
=========



|Maturity| |license gpl|



Overview
========

Zeroincombenze® Archive Replica
-------------------------------

ZAR stand for Zeroincombenze® Archive Replica.
It is a tool kit to backup, restore, replicate files and/or database.

ZAR manages easily backup for Odoo database, keeps last nth copies and purges oldest copies.



Features
--------

* backup and restore odoo database
* backup and restore based on rules by configuration file
* restore database with automatic actions disabled
* multiple copies of database by configuration file
* automatic purging of oldest copies
* configuration based on host name: it works on duplicate host image too
* backup on same host or on remote host



Usage
=====

zar should be execute by postgres user

Execute zar_upd to install and configure.
Configuration file is zar.conf
Execute zar_bck to do backup or restore, based on host role
Execute zar_rest to do restore

To execute in cron, use zar_bck -k


There are avaiable two postgresql facilities:

* pg_db_active
* pg_db_reassign owner

`pg_db_active` show and kill postgres session. It can kill oldest session out of pool.

`pg_db_reassign_owner` can reassign owner to database. It reassign the ownership of all objects.



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

For stable version:

`pip install zar`

For current version:

`cd $HOME`
`git@github.com:zeroincombenze/tools.git`
`cd $HOME/tools`
`./install_tools.sh`



Upgrade
-------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install --upgrade zar

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd ./tools
    ./install_tools.sh -pUT
    source $HOME/devel/activate_tools



ChangeLog History
-----------------

2.0.7 (2024-12-30)
~~~~~~~~~~~~~~~~~~

* [IMP] pg_db_active with port for postgresql multi-version

2.0.6 (2024-08-21)
~~~~~~~~~~~~~~~~~~

* [IMP] pg_db_active with port for postgresql multi-version

2.0.5 (2024-05-22)
~~~~~~~~~~~~~~~~~~

* [FIX] zar_upd

2.0.4 (2023-09-08)
~~~~~~~~~~~~~~~~~~

* [IMP] Backup filestore
* [FIX] Remote copy to /dev/null

2.0.3 (2023-09-06)
~~~~~~~~~~~~~~~~~~

* [FIX] DB name with hyphen (-)

2.0.2 (2023-05-14)
~~~~~~~~~~~~~~~~~~

* [IMP] reassing_owner accept db_port

2.0.1 (2023-02-25)
~~~~~~~~~~~~~~~~~~

* [IMP] Remote bckdir different from local

2.0.0 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version



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

* `Antonio M. Vigliotti <info@shs-av.com>`__
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
    :target: https://wiki.zeroincombenze.org/en/Odoo/2.0.7/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/2.0.7/man
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
