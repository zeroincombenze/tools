#!/home/odoo/11.0/venv_odoo/bin/python
import os.path
import sys
import re
from configparser import ConfigParser

import psycopg2


ARGS = {
    'b': 'tgt_ver',
    'c': 'confn',
    'd': 'dbname',
    'p': 'dbport',
    'G': 'src_org',
    'O': 'tgt_org',
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
            print('%s' % sys.args[0])
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
    if not params['tgt_ver']:
        print('No Odoo target version declared!! Use -b VER')
        return 1
    params['src_ver'] = '%s.%s' % (
        str(int(params['tgt_ver'].split('.')[0]) - 1),
        params['tgt_ver'].split('.')[1])
    return params


def ismodule(path):
    if os.path.isdir(path):
        if ((os.path.join(path, '__manifest__.py') or
                os.path.join(path, '__openerp__.py')) and
                os.path.join(path, '__init__.py')):
            return True
    return False


def get_modules_info(params, config, installed_modules=None):

    def search_module(params, addons_path, offn):
        module = os.path.basename(offn)
        ffn = offn.replace(params['src_ver'], params['tgt_ver'])
        if ismodule(ffn):
            return True
        for path in addons_path:
            ffn = os.path.join(path, module)
            if ismodule(ffn):
                return True
        return False

    installed_modules = installed_modules or []
    addons_path = config.get('options', 'addons_path').split(',')
    oupg_path = os.path.join(os.path.dirname(__file__), params['tgt_ver'])
    new_addon_path = [os.path.join(oupg_path, 'scripts')]
    modules_list = []
    modules_2_ignore = []
    odoo_root = None
    for path in addons_path:
        repo = os.path.basename(path)
        if repo == 'setup':
            continue
        opath = path.replace(params['tgt_ver'], params['src_ver'])
        if repo == 'addons':
            if os.path.basename(os.path.dirname(path)) == 'odoo':
                odoo_root = os.path.dirname(os.path.dirname(path))
                path = os.path.join(oupg_path, 'odoo', 'addons')
            else:
                path = os.path.join(oupg_path, 'addons')
        if os.path.isdir(path):
            new_addon_path.append(path)
        for fn in os.listdir(opath):
            if fn.startswith('.') or fn.startswith('_'):
                continue
            if installed_modules and fn not in installed_modules:
                continue
            offn = os.path.join(opath, fn)
            if not ismodule(offn):
                continue
            if search_module(params, addons_path, offn):
                modules_list.append(fn)
            else:
                modules_2_ignore.append(fn)
    return odoo_root, oupg_path, new_addon_path, modules_list, modules_2_ignore


def copy_confn(params, oupg_path, addons_path):
    with open(params['confn'], 'r') as fd:
        config = fd.read()
    config = re.sub(
        '^addons_path *=.*',
        'addons_path = %s' % ','.join(addons_path),
        config,
        flags=re.MULTILINE)
    config = re.sub(
        '^db_user *=.*',
        'db_user = odoo',
        config,
        flags=re.MULTILINE)
    new_confn = os.path.join(oupg_path, 'odoo.conf')
    with open(new_confn, 'w') as fd:
        fd.write(config)
    return new_confn


def main(args):
    params = get_optargs(args, {
        'tgt_ver': '11.0',
        'src_org': 'zero',
        'tgt_org': 'oca',
    })
    if isinstance(params, int):
        return params
    config = ConfigParser({})
    config.read(params['confn'])
    cnx = connect_db(params, config)
    installed_modules = exec_sql(
        cnx,
        "select name from ir_module_module where state='installed'",
        inquire=True)
    if installed_modules:
        installed_modules = [x[0] for x in installed_modules]
    (odoo_root, oupg_path, addon_path,
     modules_list, modules_2_ignore) = get_modules_info(
        params, config, installed_modules=installed_modules)
    # exec_sql(
    #     cnx,
    #     "update ir_module_module set state='uninstalled' where name in (%s)" %
    #     ','.join('\'%s\'' % x for x in modules_2_ignore)
    # )
    confn = copy_confn(params, oupg_path, addon_path)
    cmd = 'source %s/venv_odoo/bin/activate; ' % odoo_root
    cmd += '%s/odoo-bin' % oupg_path
    cmd += ' --update=%s' % ','.join(modules_list)
    cmd += ' --stop-after-init --load=base,web'
    cmd += ' -p %s' % params['dbport']
    cmd += ' -c %s' % confn
    cmd += ' -d %s' % params['dbname']
    # cmd += ' --log-handler=:DEBUG'
    print(cmd)
    return os.system(cmd)


if __name__ == "__main__":
    exit(main(sys.argv[1:]))
