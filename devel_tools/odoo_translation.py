#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import os
import time
import re
import sys
import csv
from subprocess import PIPE, Popen
from babel.messages import pofile
from os0 import os0
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = "0.2.2.11"

MAX_RECS = 100
TNL_DICT = {}
TNL_ACTION = {}
SYNTAX = {
    'string': re.compile(u'"([^"\\\n]|\\.|\\\n)*"'),
}
msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if (t > 3):
        print(text)
        msg_time = time.time()


def set_odoo_path(ctx, version):
    odoo_path = '/opt/odoo/%s' % version
    if not os.path.exists(odoo_path):
        print('Paths of Odoo %s not found' % version)
        return False
    return odoo_path


def change_name(ctx, filename, version):
    filename = filename.replace(ctx['odoo_ver'], version)
    majver = int(ctx['odoo_ver'].split('.')[0])
    if majver >= 10:
        filename = filename.replace('/openerp/addons/', '/odoo/addons/')
    else:
        filename = filename.replace('/odoo/addons/', '/openerp/addons/')
    return filename


def load_default_dictionary(source):
    ctr = 0
    if os.path.isfile(source):
        if ctx['opt_verbose']:
            print("Reading %s into dictionary" % source)
        csv.register_dialect('dict',
                             delimiter='\t',
                             quotechar='\"',
                             quoting=csv.QUOTE_MINIMAL)
        csv_fd = open(source, 'rU')
        hdr_read = False
        csv_obj = csv.DictReader(csv_fd,
                                 fieldnames=[],
                                 restkey='undef_name',
                                 dialect='dict')
        for row in csv_obj:
            if not hdr_read:
                hdr_read = True
                csv_obj.fieldnames = row['undef_name']
                continue
            msgid = os0.u(row['msgid'].strip())
            TNL_DICT[msgid] = os0.u(row['msgstr'])
            TNL_ACTION[msgid] = 'C'
            if msgid == msgid[0].upper() + msgid[1:].lower():
                msg2 = msgid.lower()
                TNL_DICT[msg2] = os0.u(row['msgstr']).lower()
                TNL_ACTION[msg2] = 'C'
            if msgid[-1] == ':':
                msg2 = msgid[:-1]
                if row['msgstr'][-1] == ':':
                    des2 = row['msgstr'][:-1]
                else:
                    des2 = row['msgstr']
            else:
                msg2 = msgid + ':'
                if row['msgstr'][-1] == ':':
                    des2 = row['msgstr']
                else:
                    des2 = row['msgstr'][:-1]
            TNL_DICT[msg2] = des2
            TNL_ACTION[msg2] = 'C'
            if msgid[-1] == '.':
                msg2 = msgid[:-1]
                if row['msgstr'][-1] == '.':
                    des2 = row['msgstr'][:-1]
                else:
                    des2 = row['msgstr']
            else:
                msg2 = msgid + '.'
                if row['msgstr'][-1] == '.':
                    des2 = row['msgstr']
                else:
                    des2 = row['msgstr'][:-1]
            TNL_DICT[msg2] = des2
            TNL_ACTION[msg2] = 'C'
            ctr += 1
        if ctx['opt_verbose']:
            print(" ... Read %d records" % ctr)
    return ctr


def load_dictionary_from_file(pofn):
    ctr = 0
    if os.path.isfile(pofn):
        if ctx['opt_verbose']:
            print("Reading %s into dictionary" % pofn)
        catalog = pofile.read_po(open(pofn, 'r'))
        for message in catalog:
            msgid = message.id
            msgstr = message.string
            if msgid in TNL_DICT:
                if msgstr != TNL_DICT[msgid]:
                    print('  Duplicate key "%s"' % msgid)
                    print('    Current="%s"' % TNL_DICT[msgid])
                    print('    New="%s"' % msgstr)
                    dummy = ''
                    if '*' in TNL_ACTION:
                        dummy = TNL_ACTION['*']
                    elif msgid in TNL_ACTION:
                        dummy = TNL_ACTION[msgid]
                    while dummy not in ('C', 'N', 'E', 'I') and \
                            len(dummy) <= 3:
                        dummy = raw_input(
                            '>>> (Current,New,End,Ignore,<Text>)? ')
                    if dummy == 'E':
                        TNL_ACTION['*'] = dummy
                        return
                    elif dummy == 'I':
                        TNL_ACTION[msgid] = dummy
                        continue
                    elif len(dummy) >= 3:
                        TNL_DICT[msgid] = dummy
                        ctr += 1
                    elif dummy == 'N':
                        TNL_DICT[msgid] = msgstr
                        ctr += 1
                    else:
                        TNL_ACTION[msgid] = dummy
                else:
                    TNL_DICT[msgid] = msgstr
                    ctr += 1
        if ctx['opt_verbose']:
            print(" ... Read %d new records" % ctr)
    return ctr


def parse_pofile(source):
    if os.path.isfile(source):
        ctr = 0
        if ctx['opt_verbose']:
            print("Reading %s for upgrade" % source)
        fdiff = False
        catalog = pofile.read_po(open(source, 'r'))
        for message in catalog:
            msgid = os0.u(message.id)
            msgstr = os0.u(message.string)
            if msgid in TNL_DICT and msgstr != TNL_DICT[msgid]:
                for k, value in message.__dict__.iteritems():
                    if k == 'string':
                        message.string = TNL_DICT[msgid]
                    elif value:
                        setattr(message, k, value)
                ctr += 1
                fdiff = True
        if ctx['opt_verbose']:
            print(" ... %d records to update" % ctr)
        return fdiff, catalog
    return False, ''


def rewrite_pofile(ctx, pofn, target, version):
    if ctx['opt_verbose']:
        print("Writing %s " % pofn)
    tmpfile = '%s.tmp' % pofn
    bakfile = '%s.bak' % pofn
    pofile.write_po(open(tmpfile, 'w'), target)
    cmd = ['makepo_it.py',
           '-b%s' % version,
           '-m%s' % ctx['module_name'],
           tmpfile]
    out, err = Popen(cmd,
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     shell=False).communicate()
    fd = open(pofn, 'rB')
    lefts = fd.read().split('\n')
    fd.close()
    fd = open(tmpfile, 'rB')
    rights = fd.read().split('\n')
    jj = 0
    for ii in range(len(lefts)):
        line = lefts[ii]
        if line[0:2] == '#.':
            while jj < len(rights) and rights[jj] != line:
                jj += 1
            if jj < len(rights) and rights[jj] == line:
                ii += 1
                while lefts[ii][0:2] == '#:':
                    jj += 1
                    rights.insert(jj, lefts[ii])
                    ii += 1
                jj += 1
    fd = open(tmpfile, 'w')
    fd.write('\n'.join(rights))
    fd.close()
    if os.path.isfile(bakfile):
        os.remove(bakfile)
    if os.path.isfile(pofn):
        os.rename(pofn, bakfile)
    os.rename(tmpfile, pofn)


def load_dictionary(ctx):
    if ctx['dbg_template']:
        dict_name = '/opt/odoo/dev/pypi/tools/odoo_default_tnl.csv'
    else:
        dict_name = '/opt/odoo/dev/odoo_default_tnl.csv'
    ctr = load_default_dictionary(dict_name)
    ctx['pofiles'] = {}
    ctx['ctrs'] = {'0': ctr}
    if ctx['branch']:
        versions = [ctx['branch']]
    else:
        versions = ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1')
    for version in versions:
        odoo_path = set_odoo_path(ctx, version)
        if odoo_path:
            module_path = False
            for root, dirs, files in os.walk(odoo_path):
                if root.find('__to_remove') < 0:
                    if os.path.basename(root) == ctx['module_name']:
                        module_path = root
                        break
            if not module_path:
                print('*** Module %s not found in Odoo %s !!!' % (
                    ctx['module_name'], version))
                continue
            print('Found path %s' % module_path)
            pofn = os.path.join(module_path, 'i18n', 'it.po')
            if not os.path.isfile(pofn):
                print('*** File %s not found !!!' % pofn)
                return 0
            ctx['pofiles'][version] = pofn
            ctr = load_dictionary_from_file(pofn)
            ctx['ctrs'][version] = ctr
    return 0


def set_header_pofile(ctx, pofile):
    polines = pofile.split('\n')
    potext = ''
    for line in polines:
        if line.startswith('"#\t*'):
            potext += r'"# %s\n"' % ctx['module_name'] + '\n'
        elif line.startswith('"# *'):
            potext += r'"# %s\n"' % ctx['module_name'] + '\n'
        elif line.startswith('"Project-Id-Version:'):
            potext += r'"Project-Id-Version: Odoo (%s)\n"' % ctx(
                'branch', '') + '\n'
        elif line.startswith('"Last-Translator:'):
            potext += r'"Last-Translator: %s <%s>\n"' % (
                'Antonio M. Vigliotti',
                'antoniomaria.vigliotti@gmail.com') + '\n'
        elif line.startswith('"Language-Team:'):
            potext += r'"Language-Team: %s (%s)\n"' % (
                'Zeroincombenze',
                'https://www.zeroincombenze.it/') + '\n'
            potext += r'"Language: it_IT\n"' + '\n'
        elif line.startswith('"Language:'):
            pass
        elif line.startswith('"language'):
            pass
        elif line.startswith('"Plural-Forms:'):
            potext += r'"Plural-Forms: nplurals=2; plural=(n != 1);\n"' + '\n'
        else:
            potext += line + '\n'
    return potext


def parse_file(ctx):
    for version in ctx['pofiles'].keys():
        pofn = ctx['pofiles'][version]
        fdiff, target = parse_pofile(pofn)
        if not fdiff:
            if ctx['opt_verbose']:
                print("No change done")
        else:
            rewrite_pofile(ctx, pofn, target, version)
    return 0


def upgrade_db(ctx):
    for version in ctx['pofiles'].keys():
        ctr = 0
        dbname = ctx['db_prefix']
        if ctx['opt_verbose']:
            print("Upgrade DB %s" % dbname)
        xmlrpc_port = 8160 + int(version.split('.')[0])
        ctx['svc_protocol'] = ''
        db_found = False
        try:
            uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                           db=dbname,
                                           xmlrpc_port=xmlrpc_port,
                                           oe_version=version)
            db_found = True
        except:
            dbname = '%s%s' % (ctx['db_prefix'], version.split('.')[0])
        if not db_found:
            try:
                uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                               db=dbname,
                                               xmlrpc_port=xmlrpc_port,
                                               oe_version=version)
                db_found = True
            except:
                print("No DB %s found" % ctx['db_prefix'])
                return
        model = 'ir.translation'
        clodoo.unlinkL8(
            ctx, model, clodoo.searchL8(
                ctx, model, [('lang', '=', 'it_IT'),
                             ('name', 'in', ('ir.module.module,description'
                                             'ir.module.module,shortdesc',
                                             'ir.module.module,summary'))]))
        for msgid in TNL_DICT:
            ids = clodoo.searchL8(ctx, model,
                                  [('lang', '=', 'it_IT'),
                                   ('type', 'in', ('field', 'model',
                                                   'report', 'help')),
                                   ('src', '=', msgid)])
            if ids and len(ids) < MAX_RECS:
                msg_burst(msgid)
                try:
                    clodoo.writeL8(ctx, model, ids, {'value': TNL_DICT[msgid]})
                    ctr += len(ids)
                except IOError:
                    print("*** Error writing %s !!!" % TNL_DICT[msgid])
            ids = clodoo.searchL8(
                ctx, model,
                [('lang', '=', 'it_IT'),
                 ('name', 'in', ('ir.actions.act_window,name',
                                 'ir.model,name',
                                 'ir.module.category,name',
                                 'ir.module.module,description'
                                 'ir.module.module,shortdesc',
                                 'ir.module.module,summary',
                                 'ir.ui.menu,name',
                                 )),
                 ('src', '=', msgid)])
            if ids and len(ids) < MAX_RECS:
                msg_burst(msgid)
                try:
                    clodoo.writeL8(ctx, model, ids, {'value': TNL_DICT[msgid]})
                    ctr += len(ids)
                except IOError:
                    print("*** Error writing %s !!!" % TNL_DICT[msgid])
        if ctx['opt_verbose']:
            print(" ... %d record upgraded" % ctr)
        if ctx['load_language']:
            clodoo.act_install_language(ctx)


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Translate Odoo Package",
                                "© 2018-2019 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-B', '--debug-template',
                        action='store_true',
                        dest='dbg_template')
    parser.add_argument("-b", "--branch",
                        help="Odoo branch",
                        dest="branch",
                        metavar="version")
    parser.add_argument("-c", "--config",
                        help="configuration file",
                        dest="conf_fn",
                        metavar="file",
                        default='./clodoo.conf')
    parser.add_argument("-d", "--dbname",
                        help="DB name",
                        dest="db_prefix",
                        metavar="dbname",
                        default='')
    parser.add_argument('-h')
    parser.add_argument('-l', '--load-language',
                        action='store_true',
                        dest='load_language')
    parser.add_argument('-m', '--module_name',
                        action='store',
                        help='filename',
                        dest='module_name')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    if not ctx['module_name']:
        print('*** Missing module name! Please, use -m switch !!!')
        sys.exit(1)
    sts = load_dictionary(ctx)
    if sts == 0:
        sts = parse_file(ctx)
    if sts == 0 and ctx['db_prefix']:
        sts = upgrade_db(ctx)
    sys.exit(sts)
