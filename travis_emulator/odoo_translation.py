#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import io
import ast
import os
import time
import re
import sys
from os0 import os0
import z0lib
import clodoo


__version__ = "0.2.1.55"

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
        fd = io.open(source, mode='r', encoding='utf-8')
        source = fd.read()
        for line in source.split('\n'):
            if line and line[0] != '#':
                i = line.find('\t')
                if i > 0:
                    msgid = line[0:i]
                    msgstr = line[i + 1:]
                    TNL_DICT[msgid] = msgstr
                    ctr += 1
                    TNL_ACTION[msgid] = 'C'
        if ctx['opt_verbose']:
            print("... Read %d records" % ctr)
    return ctr


def load_dictionary_from_file(po_file):
    ctr = 0
    if os.path.isfile(po_file):
        if ctx['opt_verbose']:
            print("Reading %s into dictionary" % po_file)
        fd = io.open(po_file, mode='r', encoding='utf-8')
        source = fd.read()
        fd.close()
        msgid = ''
        msgstr = ''
        for line in source.split('\n'):
            # print(line)
            if line[0:5] == 'msgid':
                token = line[5:].strip()
                x = SYNTAX['string'].match(token)
                msgid = token[1:x.end() - 1]
                msgstr = ''
            elif line[0:6] == 'msgstr':
                token = line[6:].strip()
                x = SYNTAX['string'].match(token)
                msgstr = token[1:x.end() - 1]
                if msgid:
                    if msgid in TNL_DICT:
                        if msgstr != TNL_DICT[msgid]:
                            print('* Duplicate key "%s"' % msgid)
                            print('--- Current="%s"' % TNL_DICT[msgid])
                            print('--- New="%s"' % msgstr)
                            dummy = ''
                            if '*' in TNL_ACTION:
                                dummy = TNL_ACTION['*']
                            elif msgid in TNL_ACTION:
                                dummy = TNL_ACTION[msgid]
                            while dummy not in ('C', 'N', 'E', 'I') and \
                                    len(dummy) <= 3:
                                dummy=raw_input('>>> (Current,New,End,Ignore,<Text>)? ')
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
            else:
                token = line.strip()
                if token:
                    x = SYNTAX['string'].match(token)
                    if x:
                        token = token[1:x.end() - 1]
                        if msgstr:
                            msgstr += token
                        elif msgid:
                            msgid += token
        if ctx['opt_verbose']:
            print("... Read %d records" % ctr)
    return ctr


def parse_po_file(source):
    if os.path.isfile(source):
        ctr = 0
        if ctx['opt_verbose']:
            print("Reading %s for upgrade" % source)
        fd = io.open(source, mode='r', encoding='utf-8')
        source = fd.read()
        fd.close()
        new_source = ''
        for line in source.split('\n'):
            # print(line)
            if line[0:5] == 'msgid':
                token = line[5:].strip()
                x = SYNTAX['string'].match(token)
                msgid = token[1:x.end() - 1]
                msgstr = ''
            elif line[0:6] == 'msgstr':
                token = line[6:].strip()
                x = SYNTAX['string'].match(token)
                msgstr = token[1:x.end() - 1]
                if msgid in TNL_DICT and msgstr != TNL_DICT[msgid]:
                    line = line.replace(msgstr, TNL_DICT[msgid])
                    ctr += 1
            else:
                token = line.strip()
                if token:
                    x = SYNTAX['string'].match(token)
                    if x:
                        line = ''
            new_source += '%s\n' % line
        if new_source[-2:] == '\n\n':
            new_source = new_source[0:-1]
        if new_source == source:
            fdiff = False
        else:
            fdiff = True
        if ctx['opt_verbose']:
            print("... %d record rewritten" % source)
        return fdiff, new_source
    return False, ''


def load_dictionary(ctx):
    ctr = load_default_dictionary('/opt/odoo/dev/odoo_default_tnl.csv')
    ctx['po_files'] = {}
    ctx['ctrs'] = {'0': ctr}
    for version in ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1'):
        odoo_path = set_odoo_path(ctx, version)
        if odoo_path:
            module_path = False
            for root, dirs, files in os.walk(odoo_path):
                if root.find('__to_remove') < 0:
                    if os.path.basename(root) == ctx['module_name']:
                        module_path = root
                        break
            if not module_path:
                raise IOError('Module %s not found in Odoo %s' % (
                    ctx['module_name'], version))
            print('Found path %s' % module_path)
            po_file = os.path.join(module_path,'i18n', 'it.po')
            if not os.path.isfile(po_file):
                print('File %s not found!' % po_file)
                return 0
            ctx['po_files'][version] = po_file
            ctr = load_dictionary_from_file(po_file)
            ctx['ctrs'][version] = ctr
    return 0


def parse_file(ctx):
    for version in ctx['po_files'].keys():
        po_file = ctx['po_files'][version]
        fdiff, target = parse_po_file(po_file)
        if not fdiff:
            if ctx['opt_verbose']:
                print("No change done")
        else:
            if ctx['opt_verbose']:
                print("Writing %s " % po_file)
            tmpfile = '%s.tmp' % po_file
            bakfile = '%s.bak' % po_file
            fd = open(tmpfile, 'w')
            fd.write(os0.b(target))
            fd.close()
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            if os.path.isfile(po_file):
                os.rename(po_file, bakfile)
            os.rename(tmpfile, po_file)
    return 0


def upgrade_db(ctx):
    for version in ctx['po_files'].keys():
        ctr = 0
        dbname = '%s%s' % (ctx['db_prefix'], version.split('.')[0])
        if ctx['opt_verbose']:
            print("Upgrade DB %s" % dbname)
        xmlrpc_port = 8160 + int(version.split('.')[0])
        ctx['svc_protocol'] = ''
        uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                       db=dbname,
                                       xmlrpc_port=xmlrpc_port,
                                       oe_version=version)
        model = 'ir.translation'
        for msgid in TNL_DICT:
            ids = clodoo.searchL8(ctx, model,
                                  [('lang', '=', 'it_IT'),
                                   ('type', 'in', ('field', 'model',
                                                   'report', 'help')),
                                   ('src', '=', msgid)])
            if ids and len(ids) < MAX_RECS:
                msg_burst(msgid)
                clodoo.writeL8(ctx, model, ids, {'value': TNL_DICT[msgid]})
                ctr += len(ids)
        if ctx['opt_verbose']:
            print("... %d record upgraded" % ctr)


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Translate Odoo Package",
                          "© 2018 by SHS-AV s.r.l.",
                          version=__version__)
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
    parser.add_argument('-m', '--module_name',
                        action='store',
                        help='filename',
                        dest='module_name')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    # parser.add_argument('src_file')
    # parser.add_argument('dst_file',
    #                     nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    if not ctx['module_name']:
        print('Missing module name! Please, use -m switch')
        sys.exit(1)
    sts = load_dictionary(ctx)
    # if sts == 0:
    #     sts = parse_file(ctx)
    if sts == 0 and ctx['db_prefix']:
        sts = upgrade_db(ctx)
    sys.exit(sts)
