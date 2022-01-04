
=============
clodoo 0.3.55
=============



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

Introduction
____________

Clodoo is a set of tools to manage to manage multiple Odoo installations with many DBs.

With clodoo you can do massive operations on 1 or more Odoo databases based on
different Odoo versions. Main operation are:

* create consistent database to run tests
* repeat consistent action on many db with same or different Odoo version
* repeat above actions on every new database

clodoo is also a PYPI package to simplify RPC connection to Odoo.
The PYPI package is a hub to oerplib and odoorpc packages, so generic python client
can execute any command to any Odoo version server (from 6.1 to 13.0)

Available commands & features are:

+----------------------------------+------------------------------+
| Function                         | Note                         |
+----------------------------------+------------------------------+
| Add new repository               | odoo_install_repository      |
+----------------------------------+------------------------------+
| Update paid invoice              | inv2draft_n_restore.py       |
+----------------------------------+------------------------------+
| List requirement of Odoo         | list_requirements.py         |
+----------------------------------+------------------------------+
| Create full configurated Odoo DB | manage_db                    |
+----------------------------------+------------------------------+
| Manage Odoo installation         | manage_odoo                  |
+----------------------------------+------------------------------+
| Set Odoo Skin (backoffice)       | odoo_skin.sh                 |
+----------------------------------+------------------------------+
| Run Odoo instance to debug       | run_odoo_debug               |
+----------------------------------+------------------------------+
| Manage version depending names   | transodoo.py                 |
+----------------------------------+------------------------------+
| General Purpose RPC              | clodoo.py                    |
+----------------------------------+------------------------------+
| Export Odoo model to test file   | export_db_model.py           |
+----------------------------------+------------------------------+
| Migrate Odoo                     | migrate_odoo.py (deprecated) |
+----------------------------------+------------------------------+
| Examples                         | example*.py                  |
+----------------------------------+------------------------------+





clodoo.py: general Purpose RPC
------------------------------

clodoo.py ia general purpose xmlrpc / json interface.
It is called by bash console, there is no funcional web/GUI interface.


    $ usage: clodoo.py [-h] [-A actions] [-b version] [-c file] [-d regex] [-D]
                 [-l iso_lang] [-n] [-p dir] [-P password] [-q] [-r port]
                 [-U username] [-u list] [-v] [-V] [-x]

    optional arguments:
      -h, --help            show this help message and exit
      -A actions, --action-to-do actions
                            action to do (use help to dir)
      -b version, --odoo-branch version
                            talk server Odoo version
      -c file, --config file
                            configuration command file
      -d regex, --dbfilter regex
                            DB filter
      -D, --with-demo       create db with demo data
      -l iso_lang, --lang iso_lang
                            user language
      -n, --dry-run         test execution mode
      -p dir, --data-path dir
                            Import file path
      -P password, --pwd password
                            login password
      -q, --quiet           run silently
      -r port, --xmlrpc-port port
                            xmlrpc port
      -U username, --user username
                            login username
      -u list, --upgrade-modules list
                            Module list to upgrade
      -v, --verbose         run with debugging output
      -V, --version         show program's version number and exit
      -x, --exit-on-error   exit on error



Import_file
~~~~~~~~~~~

Import file loads data from a csv file into DB. This action works as standard
Odoo but has some enhanced features.
Field value may be:

* external identifier, format module.name (as Odoo standard)
  i.e. 'base.main_company'
* text with macros, format ${macro} (no Odoo standard), dictionary passed
  i.e. '${company_id}'
  text may contains one or more macros
* text with DB extraction, format ${model:values} (w/o company, no Odoo std)
  i.e. '${res.company:your company}'
  data is searched by name
* text with DB extraction, format ${model::values} (with company, no Odoo std)
  i.e. '${res.partner::Odoo SA}'
  data is searched by name, company from ctx['company_id']
* text with DB extraction, format ${model(params):values} (w/o company)
  i.e. '${res.company(zip):1010}'
  data is searched by param(s)
* text with function, format ${function(params)::values} (add company)
  i.e. '${res.partner(zip)::1010}'
  data is searched by param(s), company from ctx['company_id']
* full text function, format ${function[field](params):values} (w/o company)
  full text function, format ${function[field](params)::values} (add company)
  i.e. '${res.partner[name](zip)::1010}'
  data is searched as in above function;
  returned value is not id but `field`
* crypted data, begins with $1$!
  i.e '$1$!abc'
* expression, begin with = (deprecated)
* odoo multiversion text, format model.constant.0 (in model replace '.' by '_')
  i.e. 'res_groups.SALES.0'
* odoo versioned value, format model.value.majversion
  i.e. 'res_groups.Sales.8'

Predefines macros (in ctx):

        company_id     default company_id
        company_name   name of default company (if company_id not valid)
        country_code   ISO-3166 default country (see def_country_id)
        customer-supplier if field contains 'customer' or 'client' set customer=True if it contains 'supplier' or 'vendor' or 'fornitore' set supplier=True
        def_country_id default country id (from company or from user)
        def_email      default mail; format: {username}{majversion}@example.com
        full_model     load all field values, even if not in csv
        header_id      id of header when import header/details files
        lang           language, format lang_COUNTRY, i.e. it_IT (default en_US)
        name2          if present, is merged with name
        name_first     if present with name last, are merged to compose name
        name_last      if present with name first, are merged to compose name
        street2        if present and just numeric, is merged with street
        zeroadm_mail   default user mail from conf file or <def_mail> if -D switch
        zeroadm_login  default admin username from conf file
        oneadm_mail    default user2 mail from conf file or <def_mail> if -D switch
        oneadm_login   default admin2 username from conf file
        botadm_mail    default bot user mail from conf file or <def_mail> if -D switch
        botadm_login   default bot username from conf file
        _today         date.today()
        _current_year  date.today().year
        _last_year'    date.today().year - 1
        TNL_DICT       dictionary with field translation, format csv_name: field_name; i.e {'partner_name': 'name'} or csv_position: field_name, i.e. {'0': 'name'}
        TNL_VALUE      dictionary with value translation for field; format is field_name: {csv_value: field_value, ...} i.e. {'country': {'Inghilterra': 'Regno Unito'}} special value '$BOOLEAN' return True or False
        DEFAULT        dictionary with default value, format field_name: value
        EXPR           evaluate value from expression, format csv_name: expression; expression can refer to other fields of csv record in format csv[field_name] or other fields of record in format row[field_name] i.e. {'is_company': 'row["ref"] != ""'} {'is_company': 'csv["CustomerRef"] != ""'}
        MANDATORY      dictionary with mandatory field names


Import searches for existing data (this behavior differs from Odoo standard)
Search is based on <o_model> dictionary;
default field to search is 'name' or 'id', if passed.

::

    File csv can contain some special fields:
    db_type: select record if DB name matches db type; values are
        'D' for demo,
        'T' for test,
        'Z' for zeroincombenze production,
        'V' for VG7 customers
        'C' other customers
    oe_versions: select record if matches Odoo version
        i.e  +11.0+10.0 => select record if Odoo 11.0 or 10.0
        i.e  -6.1-7.0 => select record if Odoo is not 6.1 and not 7.0


odoo_install_repository: manage repositories
--------------------------------------------

::

    Usage: odoo_install_repository [-h][-b branch][-c file][-CDjLmn][-O git-org][-o path][-qrU][-u username][-Vvy1] git_repo odoo_vid new_odoo_vid
    Add or duplicate odoo repository into local filesystem
     -h              this help
     -b branch       default odoo branch
     -c file         configuration file (def .travis.conf)
     -C              do not touch configuration file (conflict with -D)
     -D              update default values in /etc configuration file before creating script (conflict with -C)
     -j              install only repository owned by git organization
     -L              create symbolic link rather copy files (if new_odoo_ver supplied)
     -m              multi-version odoo environment
     -n              do nothing (dry-run)
     -O git-org      git organization, one of oca oia[-git|-http] zero[-git|-http] (def zero)
     -o path         odoo directory
     -q              silent mode
     -r              do just update remote info (if no new_odoo_ver supplied)
     -U              do not install, do upgrade
     -u username     execute as username (def=odoo)
     -V              show version
     -v              verbose mode
     -y              assume yes
     -1              if clone depth=1


odoorc: general purpose bash function
-------------------------------------

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


Translate Odoo entinty name across versions.



|

Usage
=====





|
|

Getting started
===============


|

Installation
------------

Installation
------------

Zeroincombenze tools require:

* Linux Centos 7/8 or Debian 9/10 or Ubuntu 18/20
* python 2.7, some tools require python 3.6+
* bash 5.0+

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install clodoo

|

Current version via Git
~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    source /opt/odoo/devel/activate_tools


Upgrade
-------

Upgrade
-------

Stable version via Python Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pip install clodoo -U

|

Current stable version
~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -U
    source /opt/odoo/devel/activate_tools

Current development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    cd $HOME
    ./install_tools.sh -Ud
    source /opt/odoo/devel/activate_tools


History
-------

0.3.53.4 (2021-11-30)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo: full python3 functionality

0.3.36.1 (2021-10-16)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] run_odoo_debug with no standard db port

0.3.36 (2021-09-29)
~~~~~~~~~~~~~~~~~~~

* [IMP] stable version

0.3.35.4 (2021-09-29)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] odoorc: do not use git --show-current
* [IMP] odoorc: now it a command too

0.3.35.3 (2021-09-26)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo: specific openpyxl for python2

0.3.35.2 (2021-09-24)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] transodoo.xlsx

0.3.35.1 (2021-09-24)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] powerp module transaltion

0.3.35 (2021-09-23)
~~~~~~~~~~~~~~~~~~~

* [FIX] python 3

0.3.33.4 (2021-08-30)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] clodoo.py: rcp login

0.3.33.3 (2021-08-25)
~~~~~~~~~~~~~~~~~~~~~

* [IMP] transodoo.xlsx: translation update

0.3.33.1 (2021-08-23)
~~~~~~~~~~~~~~~~~~~~~

* [FIX] transodoo.xlsx: wrong translation of l10n_it_reverse_charge


0.3.31.16 (2021-08-11)
~~~~~~~~~~~~~~~~~~~~~~

[FIX] odoorc: module list



|
|

Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Contributors
------------

* Antonio M. Vigliotti <info@shs-av.com>
|
This module is part of tools project.
Last Update / Ultimo aggiornamento: 2021-10-06
.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
:target: https://odoo-community.org/page/development-status
:alt:
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=master
:target: https://travis-ci.com/zeroincombenze/tools
:alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
:target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
:alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
:target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
:alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=master
:target: https://coveralls.io/github/zeroincombenze/tools?branch=0.3
:alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.3/graph/badge.svg
:target: https://codecov.io/gh/zeroincombenze/tools/branch/0.3
:alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-0.svg
:target: https://wiki.zeroincombenze.org/en/Odoo/0.3/dev
:alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-0.svg
:target: https://wiki.zeroincombenze.org/it/Odoo/0.3/man
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-0.svg
:target: https://erp0.zeroincombenze.it
:alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.3/graph/badge.svg
:target: https://codecov.io/gh/OCA/tools/branch/0.3
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
:target: https://odoo-italia.org
:alt: Odoo Italia Associazione
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
:target: https://www.zeroincombenze.it/
:alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
:target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
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
Last Update / Ultimo aggiornamento: 2021-11-01
:target: https://t.me/Assitenza_clienti_powERP
Last Update / Ultimo aggiornamento: 2021-11-10
Last Update / Ultimo aggiornamento: 2021-11-11
Last Update / Ultimo aggiornamento: 2021-11-13
Last Update / Ultimo aggiornamento: 2021-12-02
Last Update / Ultimo aggiornamento: 2021-12-03
Last Update / Ultimo aggiornamento: 2021-12-04
Last Update / Ultimo aggiornamento: 2021-12-05
Last Update / Ultimo aggiornamento: 2021-12-11
Last Update / Ultimo aggiornamento: 2021-12-19
:target: https://odoo-community.org/page/development-status
:alt:
:target: https://travis-ci.com/zeroincombenze/tools
:alt: github.com
:target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
:alt: License: AGPL-3
:target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
:alt: License: OPL
:target: https://coveralls.io/github/zeroincombenze/tools?branch=0.3
:alt: Coverage
:target: https://codecov.io/gh/zeroincombenze/tools/branch/0.3
:alt: Codecov
:target: https://wiki.zeroincombenze.org/en/Odoo/0.3/dev
:alt: Technical Documentation
:target: https://wiki.zeroincombenze.org/it/Odoo/0.3/man
:target: https://erp0.zeroincombenze.it
:alt: Try Me
:target: https://codecov.io/gh/OCA/tools/branch/0.3
:target: https://odoo-italia.org
:alt: Odoo Italia Associazione
:target: https://www.zeroincombenze.it/
:alt: Zeroincombenze
:target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
:target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
:target: https://t.me/Assitenza_clienti_powERP


|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2021-12-21

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=master
    :target: https://travis-ci.com/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=master
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=0.3
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.3/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/0.3
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-0.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/0.3/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-0.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/0.3/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-0.svg
    :target: https://erp0.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.3/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/0.3
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
   :target: https://t.me/Assitenza_clienti_powERP


