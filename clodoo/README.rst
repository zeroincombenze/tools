
===============
clodoo 0.3.8.68
===============



|Maturity| |Build Status| |Coverage Status| |license gpl|


.. contents::


Overview
========

clodoo
======

Massive operations on Zeroincombenze(R) / Odoo databases
--------------------------------------------------------


Clodoo is a tool can do massive operation on 1 or more Odoo database base on
different Odoo versions. Main operation are:

- create consistent database to run tests
- repeat consistent action on many db with same or different Odoo version
- repeat above actions on every new database

It is called by bash console, there is no funcional web/GUI interface.

It requires OERPLIB and ODOORPC.

Tool syntax:

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
-----------

Import file loads data from a csv file into DB. This action works as standard
Odoo but has some enhanced features.
Field value may be:
- external identifier, format module.name (as Odoo standard)
  i.e. 'base.main_company'
- text with macros, format ${macro} (no Odoo standard), dictionary passed
  i.e. '${company_id}'
  text may contains one or more macros
- text with DB extraction, format ${model:values} (w/o company, no Odoo std)
  i.e. '${res.company:your company}'
  data is searched by name
- text with DB extraction, format ${model::values} (with company, no Odoo std)
  i.e. '${res.partner::Odoo SA}'
  data is searched by name, company from ctx['company_id']
- text with DB extraction, format ${model(params):values} (w/o company)
  i.e. '${res.company(zip):1010}'
  data is searched by param(s)
- text with function, format ${function(params)::values} (add company)
  i.e. '${res.partner(zip)::1010}'
  data is searched by param(s), company from ctx['company_id']
- full text function, format ${function[field](params):values} (w/o company)
  full text function, format ${function[field](params)::values} (add company)
  i.e. '${res.partner[name](zip)::1010}'
  data is searched as in above function;
  returned value is not id but `field`
- crypted data, begins with $1$!
  i.e '$1$!abc'
- expression, begin with = (deprecated)
- odoo multiversion text, format model.constant.0 (in model replace '.' by '_')
  i.e. 'res_groups.SALES.0'
- odoo versioned value, format model.value.majversion
  i.e. 'res_groups.Sales.8'

Predefines macros (in ctx):
company_id     default company_id
company_name   name of default company (if company_id not valid)
country_code   ISO-3166 default country (see def_country_id)
customer-supplier if field contains 'customer' or 'client' set customer=True
                  if it contains 'supplier' or 'vendor' or 'fornitore'
                      set supplier=True
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
TNL_DICT       dictionary with field translation, format csv_name: field_name;
               i.e {'partner_name': 'name'}
               or csv_position: field_name, i.e. {'0': 'name'}
TNL_VALUE      dictionary with value translation for field;
               format is field_name: {csv_value: field_value, ...}
               i.e. {'country': {'Inghilterra': 'Regno Unito'}}
               special value '$BOOLEAN' return True or False
DEFAULT        dictionary with default value, format field_name: value
EXPR           evaluate value from expression, format csv_name: expression;
               expression can refer to other fields of csv record in format
               csv[field_name]
               or other fields of record in format row[field_name]
               i.e. {'is_company': 'row["ref"] != ""'}
                    {'is_company': 'csv["CustomerRef"] != ""'}
MANDATORY      dictionary with mandatory field names


Import searches for existing data (this behavior differs from Odoo standard)
Search is based on <o_model> dictionary;
default field to search is 'name' or 'id', if passed.

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

|
|

Quick start
===========


|

Installation
------------

For stable version:

`pip install clodoo`

For current version:

`cd $HOME`
`git@github.com:zeroincombenze/tools.git`
`cd $HOME/tools`
`./install_tools.sh`

|
|

Get involved
============

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

Last Update / Ultimo aggiornamento: 2019-11-11

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alfa
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=.
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=.
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=.
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/./graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/.
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-0.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/./dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-0.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/./man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-0.svg
    :target: https://erp0.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/./graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/.
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
   :target: https://tawk.to/85d4f6e06e68dd4e358797643fe5ee67540e408b

