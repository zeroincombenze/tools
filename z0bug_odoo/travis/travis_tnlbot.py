#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

# import sys

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
try:
    from clodoo import clodoo
except ImportError:
    import clodoo
try:
    from travis_helpers import print_flush
except ImportError:
    from .travis_helpers import print_flush


def main(argv=None, database=None):
    odoo_version = os.environ.get("VERSION")
    if int(odoo_version.split('.')[0]) < 10:
        src_confn = os.path.expanduser('~/.openerp_serverrc')
    else:
        src_confn = os.path.expanduser('~/.odoorc')
    fname_conf = os.path.expanduser('./clodoo.conf')
    config = ConfigParser.ConfigParser()
    config.read(src_confn)
    if not config.has_section('options'):
        config.add_section('options')
    data = {'login_user': 'admin', 'psycopg2': '1', 'oe_version': odoo_version}
    for key, value in data.items():
        config.set('options', key, value)
    with open(fname_conf, 'w') as configfile:
        config.write(configfile)
    ctx = {}
    uid, ctx = clodoo.oerp_set_env(confn=fname_conf, db=database, ctx=ctx)
    if not uid:
        print_flush(
            'ERROR: Cannot connect to DB %s with user %s!'
            % (database, data['login_user'])
        )
        return 1
    if ctx['_cr']:
        print_flush(
            'ERROR: Cannot connect to DB %s via sql with user %s|'
            % (database, config.get('options', 'db_user'))
        )
        return 1
    query = "select name from ir_module_module where state='installed'"
    rows = clodoo.exec_sql(ctx, query, response=True)
    for row in rows:
        print_flush('Module %s' % row[0])
    return 0


if __name__ == "__main__":
    database = os.environ.get('MQT_TEST_DB', 'test_odoo')
    exit(main(database=database))
