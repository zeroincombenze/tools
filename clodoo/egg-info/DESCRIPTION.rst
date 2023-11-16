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