Introduction
------------

Clodoo is a set of tools to manage to manage multiple Odoo installations with many DBs.

With clodoo you can do massive operations on 1 or more Odoo databases based on
different Odoo versions. Main operation are:

* create consistent database to run tests
* repeat consistent action on many db with same or different Odoo version
* repeat above actions on every new database

clodoo is also a PYPI package to simplify RPC connection to Odoo.
The PYPI package is a hub to oerplib and odoorpc packages, so generic python client
can execute any command to any Odoo version server (from 6.1 to 13.0)


odoorc: general purpose bash library
------------------------------------

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
