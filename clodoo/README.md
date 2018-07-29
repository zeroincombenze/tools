[![Build Status](https://travis-ci.org/OCA/maintainer-quality-tools.svg)](https://travis-ci.org/OCA/maintainer-quality-tools)
[![Coverage Status](https://coveralls.io/repos/OCA/maintainer-quality-tools/badge.svg)](https://coveralls.io/r/OCA/maintainer-quality-tools)

ODOO CLOUD TOOLS
================

clodoo is a set of tools to manage multiple Odoo installations with many DBs,
i.e. in cloud environment.

All clodoo tools have to be execute by command line, there is no web feature.

clodoo is also a PYPI package to simplify RPC connection to Odoo.
The PYPI package is a hub to oerplib and odoorpc packages, so generic python client
can execute any command to any Odoo version server (from 6.1 to 11.0)


### Features

Function | Status | Note
--- | --- | ---
Add new repository | :white_check_mark: | addsubm.sh
Update paid invoice | :white_check_mark: | inv2draft_n_restore.py
List requirement of Odoo | :white_check_mark: | list_requirements.py
Create full configurated Odoo DB | :white_check_mark: | manage_db
Manage Odoo installation | :white_check_mark: | manage_odoo
Set Odoo Skin (backoffice) | :white_check_mark: | odoo_skin.sh
Run Odoo instance to debug | :white_check_mark: | run_odoo_debug.sh
Manage version depending names | :white_check_mark: | transodoo.py
General Purpose RPC | :white_check_mark: | clodoo.py


Installation
------------

Install using odoo user.

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    ./tools/install_foreign.sh
    PATH=~/dev:$PATH


Configuration
-------------

    please config . global


Usage
-----

Type command with -h switch.

### Installation of Odoo Packages

Odoo requires a lot of PIP/binary packages to run correctly.
Many of these packages must be installed with a specific version and
requirements can change after every upgrade by OCA or partners
so is very difficult to keep th good requirements.

The script manage_odoo helps to do this job.
Type follow command by authorized user (may install some packages):

    manage_odoo -b{odoo_vid} -d{odoo_path} requirements

read below, about odoo_vid; switch -d must be supplied if installation does not attend odoo_vid rules.
If your machine is multi-version odoo environment, you can avoid -b switch and script tries to install package version can meet all Odoo versions requirements.
However, installed package version can conflict against some Odoo version.

Use virtual env to avoid conflict.


Multiple Odoo installations/versions
------------------------------------

All the tools manage multiple Odoo installations and versions.

When you type any tools commmand, you can issue Odoo Version Identificator
called vid; by Odoo vid tools can assume Odoo version, directory tree
and other configuration values. You can override any value.

### Odoo vid

Odoo vid may be:

* Full Odoo version, i.e. *11.0*
* Major Odoo version, i.e. *11*
* One of above version prefixed by one upper/lowercase of: 'v', 'odoo', 'oca', 'oia' followed by an optional hyphen; i.e. *odoo-11*, *OCA-11.0*, *v11*

### Directory Tree

    /opt/odoo/{vid}
                  \- server     (only in old 6.1/7.0 installations)
                          \- openerp
                  \- openerp    (7.0, 8.0 and 9.0)
                  \- odoo        (10.0, 11.0)
                        \- {repository}

## Rules by vid

In local filesystem may exist one or more Odoo installations.
Only one instance may be used as official installation and must be prefixed
by 'v' or 'V' letter, followed by Odoo version, i.e. *v11* or *V11* or *v11.0*, etc.
See above about vid.

Example of default parameters from vid (values may be slightly different):

Parameter | <no vid> | v | oca | Note
----------|----------------------|------|-----------------------|------
xml_port  | 8160 + major version | 8069 |  8260 + major version |
db_user   | odoo{major_version} | odoo | odoo{major_version} | i.e *odoo11*
config    | odoo{major_version}-server.conf | odoo.conf | odoo{major_version}-oca.conf | Directory /etc/odoo
logfile   | odoo{major_version}-server.log | odoo-server.log | odoo{major_version}-oca.log | Directory /var/log/odoo

Examples:
* Official odoo 11.0: vid=v11 -> Directory=/opt/odoo/v11, xmlport=8069, config=/etc/odoo/odoo.conf
* Backup odoo 11.0: vid=11.0 -> Directory=/opt/odoo/11.0, xmlport=8171, config=/etc/odoo/odoo11.conf
* Odoo OCA 10.0 to test: vid=oca-10.0 -> Directory=/opt/odoo/oca-10.0, xmlport=8270, config=/etc/odoo/odoo10-oca.conf
* Odoo 8.0 with old data: vid=8.0 -> Directory=/opt/odoo/8.0, xmlport=8168, config=/etc/odoo/odoo8-server.conf


Bug Tracker
-----------

Have a bug? Please visit https://odoo-italia.org/index.php/kunena/home


Credits
-------

### Contributors

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>

### Funders

This module has been financially supported by

* SHS-AV s.r.l. <https://www.zeroincombenze.it/>

### Maintainer

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>

[//]: # (copyright)

----

**Odoo** is a trademark of [Odoo S.A.](https://www.odoo.com/) (formerly OpenERP, formerly TinyERP)

**OCA**, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

**zeroincombenze®** is a trademark of [SHS-AV s.r.l.](http://www.shs-av.com/)
which distributes and promotes **Odoo** ready-to-use on its own cloud infrastructure.
[Zeroincombenze® distribution](http://wiki.zeroincombenze.org/en/Odoo)
is mainly designed for Italian law and markeplace.
Everytime, every Odoo DB and customized code can be deployed on local server too.

[//]: # (end copyright)