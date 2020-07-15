
==============================
|Zeroincombenze| tools 0.2.3.4
==============================

|Coverage Status| |license gpl|




Overview
========

Python & bash tools
-------------------

Sparse python and bash source code.

These tools help to cover following areas of software:

* Odoo deployment
* Odoo database maintenance (creation and upgrade, massive)
* Odoo database profiling (auto)
* Database check (auto & massive)
* Development
* Documentation
* Testing


Components
~~~~~~~~~~

+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| Package                  | Name                    | brief                                                                                                                                                      | Area                      |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| clodoo                   | check_4_seq.sh          | Check for postgres database index                                                                                                                          | maintenance               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | clodoo.py               | Massive operations on multiple Odoo DBs in cloud. It is used to create configurated Odoo DBs and to upgrade more DBs at the same time. No (yet) documented | maintenance               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | force_password.sh       | Force Odoo DB password                                                                                                                                     | maintenance               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | inv2draft_n_restore.py  | Force an invoice to draft state even if is paid and restore original state and payment (Odoo < 9.0)                                                        | maintenance               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | list_requirements.py    | List pypi and bin packages for an Odoo installation                                                                                                        | deployment                |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | manage_db               | Massive operations to multiple Odoo DBs in cloud, data based on csv files.                                                                                 | maintenance               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | manage_odoo             | Manage an Odoo installation                                                                                                                                | maintenance               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_install_repository | Install & upgrade odoo repository                                                                                                                          | Deployment & maintenance  |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | set_workers.sh          | Evaluate and set Odoo workers for best performance                                                                                                         | Deployment & maintenance  |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| devel_tools              | cvt_csv_to_rst.py       | Convert a csv file into rst text file with table inside                                                                                                    | documentation             |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | cvt_csv_to_xml.py       | Convert a csv file into xml file for Odoo module data                                                                                                      | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | cvt_script              | Make bash script to standard                                                                                                                               | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | gen_readme.py           | Generate README.rst, index.html and __openerp__.py ,documentation                                                                                          | documentation             |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_dependencies.py    | Show Odoo module tree, ancestors and/or childs                                                                                                             | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_translation.py     | Load Odoo translation (deprecated, must be replaced by weblate)                                                                                            | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | please                  | Developer shell                                                                                                                                            | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | topep8                  | Convert python and xml file across Odoo versions                                                                                                           | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | vfdiff                  | Make difference between 2 files or directories                                                                                                             | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| lisa                     | lisa                    | Linux Installer Simple App. LAMP and odoo server installer from scratch.                                                                                   | deployment                |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| maintainer-quality-tools |                         | Forked OCA maintainer quality tools. It works with 6.1 and 7.0 Odoo version too                                                                            | testing                   |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| odoo_score               | odoo_score.py           | Odoo super core ORM                                                                                                                                        | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | odoo_shell.py           | Odoo shell for Odoo versions from 6.1 to 13.0                                                                                                              | Development & maintenance |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| os0                      |                         | Simple os interface checked for OpenVMS too                                                                                                                | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| python-plus              | python-plus             | Various features to python 2 and python 3 programs as integration of pypi future to help to port your code from Python 2 to Python 3                       | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
|                          | vem                     | Virtual Environment Manager: create, copy, move, merge and many other functions with virtual environments                                                  | Deployment & maintenance  |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| pytok                    |                         | Simple python token parser (deprecated)                                                                                                                    |                           |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| travis_emulator          | travis                  | Travis Emulator on local machine. Check your project before release on TravisCi                                                                            | testing                   |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| wok_code                 |                         | Undocumented (deprecated)                                                                                                                                  |                           |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| wok_news                 |                         | Undocumented (deprecated)                                                                                                                                  |                           |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0bug_odoo               | z0bug_odoo              | Integration of zerobug and Odoo                                                                                                                            | testing                   |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| z0lib                    |                         | General purpose bash & python library                                                                                                                      | development               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zar                      | zar                     | Zeroincombenze Archive and Replica. Backup your Odoo DBs                                                                                                   | maintenance               |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+
| zerobug                  | zerobug                 | testing & debug library                                                                                                                                    | testing                   |
+--------------------------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------+




Odoo structure
~~~~~~~~~~~~~~

All the tools serving Odoo are based on follow file system structure (flat layout):

::

    etc
     ┗━ odoo
          ┣━ odoo.conf                   (1)(3)
          ┣━ odoo-server.conf            (2)(3)
          ┣━ odoo{majver}.conf           (1)(4)
          ┣━ odoo{majver}-server.conf    (2)(4)
          ┗━ odoo{majver}-{org}.conf     (4)

    {vid}
      ┣━ addons                          (3)
      ┣━ ...                             (3)
      ┣━ odoo                            (1)(3)
      ┃    ┣━ ...                        (3)
      ┃    ┗━ addons                     (3)
      ┣━ openerp                         (2)(3)
      ┃    ┣━ ...                        (3)
      ┃    ┗━ addons                     (3)
      ┣━ server                          (5)
      ┃    ┗━ openerp
      ┃        ┣━ ...
      ┃        ┗━ addons
      ┣━ {repository}
      ┃    ┣━ {module}
      ┃    ┃    ┣━ __init__.py
      ┃    ┃    ┣━ __manifest__.py
      ┃    ┃    ┗━ ...
      ┃    ┗━ {module} ...
      ┃         ┗━ ...
      ┗━ {repository} ...
           ┗━ ...

    {venv}
      ┣━ ....
      ┗━ odoo                             (link)

    Notes:
    (1) Odoo version >= 10.0
    (2) Odoo version < 10.0
    (3) Odoo standard files / directory
    (4) Multi-version environment
    (5) Some old 6.1 and 7.0 installations
    {majver} Odoo major version, i.e. 12 for 12.0
    {org} Organization, i.e. oca axitec zero
    {vid} Odoo root (see about Odoo vid)
    {repository} Odoo/OCA or any repository
    {venv} Virtual directory


This is the hierarchical layout):

::

    {vid}
      ┣━ odoo
      ┃   ┣━ addons                      (3)
      ┃   ┣━ ...                         (3)
      ┃   ┣━ odoo                        (1)(3)
      ┃   ┃    ┣━ ...                    (3)
      ┃   ┃    ┗━ addons                 (3)
      ┃   ┗━ openerp                     (2)(3)
      ┃        ┣━ ...                    (3)
      ┃        ┗━  addons                (3)
      ┣━ extra
      ┃    ┣━ {repository}
      ┃    ┃    ┣━ {module}
      ┃    ┃    ┃    ┣━ __init__.py
      ┃    ┃    ┃    ┣━ __manifest__.py
      ┃    ┃    ┃    ┗━ ...
      ┃    ┃    ┗━ {module} ...
      ┃    ┃         ┗━ ...
      ┃    ┗━ {repository} ...
      ┃              ┗━ ...
      ┣━ private-addons
      ┃    ┣━ {customized-addons}
      ┃    ┃    ┣━ __init__.py
      ┃    ┃    ┣━ __manifest__.py
      ┃    ┃    ┗━ ...
      ┃    ┗━ {customized-addons} ...
      ┃         ┗━ ...
      ┣━ etc
      ┃    ┗━ *.conf                     (link)
      ┣━ axidoo
      ┃    ┣━ deploy
      ┃    ┣━ generic
      ┃    ┃    ┣━ {profile-modules}
      ┃    ┃    ┃     ┗━ ...
      ┃    ┃    ┗━ {profile-modules} ...
      ┃    ┃          ┗━ ...
      ┃    ┗━ accounting
      ┃         ┣━ {axitec-modules}
      ┃         ┃     ┗━ ...
      ┃         ┗━ {axitec-modules} ...
      ┃               ┗━ ...
      ┗━ venv_odoo                       (4)

    Notes:
    (1) Odoo version >= 10.0
    (2) Odoo version < 10.0
    (3) Odoo standard files / directory
    (4) Virtual directory
    {vid} Odoo root (see about Odoo vid)
    {repository} Odoo/OCA repository
    {customized-addons} Customized modules
    {axitec-modules} Italian localization modules


Odoo Version Identification (vid)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the tools manage multiple Odoo installations and versions.

When you type any tools command, you can issue Odoo Version Identificator
called **vid**; with Odoo vid, tools can assume Odoo version, directory tree
and other configuration values. You can override any value.

Odoo vid may be:

* Full Odoo version, i.e. **12.0**
* Major Odoo version, i.e. **12**
* One of above version prefixed by one upper/lowercase of: 'v', 'odoo', 'oca' followed by an optional hyphen or underscore; i.e. **odoo-12**, **odoo_12**, **oca12**, **v12**

+-------------+---------+--------------------+---------------------------------+------------------------------+------------------------------------------+
| Parameter   | name    | standard value     | versioned value                 | reserved to oca              | Note                                     |
+-------------+---------+--------------------+---------------------------------+------------------------------+------------------------------------------+
| xmlrpc port | RPCPORT | 8069               | 8160 + major version            | 8260 + major version         |                                          |
+-------------+---------+--------------------+---------------------------------+------------------------------+------------------------------------------+
| db_user     | USER    | odoo               | odoo{major_version}             | odoo{major_version}          | i.e odoo12                               |
+-------------+---------+--------------------+---------------------------------+------------------------------+------------------------------------------+
| config file | CONFN   | odoo[-server].conf | odoo{major_version}-server.conf | odoo{major_version}-oca.conf | Directory /etc/odoo (see Odoo structure) |
+-------------+---------+--------------------+---------------------------------+------------------------------+------------------------------------------+
| log file    | FLOG    | odoo[-server].log  | odoo{major_version}-server.log  | odoo{major_version}-oca.log  | Directory /var/log/odoo                  |
+-------------+---------+--------------------+---------------------------------+------------------------------+------------------------------------------+
| pid file    | FPID    | odoo[-server].pid  | odoo{major_version}-server.pid  | odoo{major_version}-oca.pid  | Directory /var/run/odoo                  |
+-------------+---------+--------------------+---------------------------------+------------------------------+------------------------------------------+




Example of multi-version environment

::

    odoo-root
      ┣━ 12.0               (Backup odoo 12.0)
      ┃   ┗━ ...
      ┣━ v12                (Official odoo)
      ┃   ┗━ ...
      ┣━ oca10              (Odoo OCA 10.0)
      ┃   ┗━ ...
     ...

Generic command:  **tool -b12.0**

* It uses directory /odoo-root/12.0
* Instance uses port 8172, config file */etc/odoo/odoo12.conf*

Generic command:  **tool -bv12**

* It uses directory /odoo-root/v12
* Instance uses port 8069, config file */etc/odoo/odoo.conf*

Generic command:  **tool -boca10**

* It uses directory /odoo-root/oca10
* Instance uses port 8270, config file */etc/odoo/odoo10-oca.conf*




|
|

Getting started
===============

|Try Me|


|

Installation
------------


Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::
    pip install repos_name

|

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/devel/activate_tools


Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


|


Last Update / Ultimo aggiornamento: 2020-07-15

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alfa
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=0.2.3.4
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=0.2.3.4
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=0.2.3.4
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.4/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.4
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/0.2.3.4/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/0.2.3.4/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.2.3.4/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/0.2.3.4
    :alt: Codecov
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
   :target: https://odoo-italia.org
   :alt: Odoo Italia Associazione
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
   :target: https://t.me/axitec_helpdesk

