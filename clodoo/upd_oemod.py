#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import pdb
# import os
import sys
import time
import oerplib
from z0lib import parseoptargs


__version__ = "0.1.1.4"


def initialize_params(ctx):
    xml_port = 8069
    database = 'demo'
    user = 'admin'
    passwd = 'admin'
    oe_version = '7.0'
    write_config_file = False
    opt_config = ctx.get('opt_config', './inv2draft_n_restore.conf')
    try:
        fd = open(opt_config, 'r')
        lines = fd.read().split('\n')
        for line in lines:
            tkn = line.split('=')
            if tkn[0] == 'login_user':
                user = tkn[1]
            elif tkn[0] == 'login_password':
                passwd = tkn[1]
            elif tkn[0] == 'db_name':
                database = tkn[1]
            elif tkn[0] == 'xml_port':
                xml_port = int(tkn[1])
            elif tkn[0] == 'oe_version':
                oe_version = tkn[1]
        fd.close()
    except:
        write_config_file = True
        if ctx.get('opt_db', None) is None:
            database = raw_input('database[def=demo]? ')
        user = raw_input('username[def=admin]? ')
        passwd = raw_input('password[def=admin]? ')
        p = raw_input('port[def=8069]? ')
        if p:
            xml_port = int(p)
        if ctx.get('oe_version', None) is None:
            p = raw_input('odoo version[def=7.0]? ')
            if p:
                oe_version = p
    if ctx.get('opt_db', None) is not None:
        database = ctx['opt_db']
    if ctx.get('oe_version', None) is not None:
        oe_version = ctx['oe_version']
    oerp = oerplib.OERP(port=xml_port, version=oe_version)
    uid = oerp.login(user=user,
                     passwd=passwd, database=database)
    if write_config_file:
        fd = open(opt_config, 'w')
        fd.write('login_user=%s\n' % user)
        fd.write('login_password=%s\n' % passwd)
        fd.write('db_name=%s\n' % database)
        if xml_port != 8069:
            fd.write('xml_port=%d\n' % xml_port)
        if oe_version:
            fd.write('oe_version=%s\n' % oe_version)
        fd.close()
    return oerp, uid


if __name__ == "__main__":
    parser = parseoptargs("upd_oemod",
                          "© 2017 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--branch',
                        action='store',
                        dest='oe_version',
                        default='7.0')
    parser.add_argument('-c', '--config',
                        action='store',
                        dest='opt_config',
                        default='./inv2draft_n_restore.conf')
    parser.add_argument('-d', '--database',
                        action='store',
                        dest='opt_db')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    oerp, uid = initialize_params(ctx)

    ctx['level'] = 4
    passed_file = './upd_oemod_passed.log'
    exclusion_file = './upd_oemod_exclude.log'
    passed_list = []
    try:
        fd = open(passed_file, 'r')
        lines = fd.read().split('\n')
        for line in lines:
            if line:
                passed_list.append(line)
        fd.close()
    except:
        pass

    exclusion_list = []
    try:
        fd = open(exclusion_file, 'r')
        lines = fd.read().split('\n')
        for line in lines:
            if line:
                exclusion_list.append(line)
        fd.close()
    except:
        pass

    model = 'ir.module.module'
    ids = oerp.search(model, [('state', '=', 'installed')], order='name')
    for id in ids:
        module = oerp.browse(model, id)
        if module.name not in passed_list + exclusion_list:
            # print module.name
            try:
                oerp.execute(model, "button_immediate_upgrade", [id])
                fd = open(passed_file, 'a')
                fd.write('%s\n' % module.name)
                fd.close()
                print "%s passed" % module.name
                time.sleep(1)
            except:
                fd = open(exclusion_file, 'a')
                fd.write('%s\n' % module.name)
                fd.close()
                print "%s not upgradable" % module.name
                sys.exit(1)
        else:
            print "%s passed or excluded!" % module.name
    sys.exit(0)
