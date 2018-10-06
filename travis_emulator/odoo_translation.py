#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import io
import ast
import os
import re
import sys
from os0 import os0
import z0lib


__version__ = "0.2.1.53"

TNL_DICT = {}
TNL_ACTION = {}
SYNTAX = {
    'string': re.compile(u'"([^"\\\n]|\\.|\\\n)*"'),
}

def change_name(ctx, filename, version):
    filename = filename.replace(ctx['odoo_ver'], version)
    majver = int(ctx['odoo_ver'].split('.')[0])
    if majver >= 10:
        filename = filename.replace('/openerp/addons/', '/odoo/addons/')
    else:
        filename = filename.replace('/odoo/addons/', '/openerp/addons/')
    return filename

def load_dictionary_from_file(source):
    if os.path.isfile(source):
        if ctx['opt_verbose']:
            print("Reading %s into dictionary" % source)
        fd = io.open(source, mode='r', encoding='utf-8')
        source = fd.read()
        fd.close()
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
                            elif dummy == 'N':
                                TNL_DICT[msgid] = msgstr
                            else:
                                TNL_ACTION[msgid] = dummy
                    else:
                        TNL_DICT[msgid] = msgstr


def parse_source(source):
    if os.path.isfile(source):
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
            new_source += '%s\n' % line
        if new_source[-2:] == '\n\n':
            new_source = new_source[0:-1]
        if new_source == source:
            fdiff = False
        else:
            fdiff = True
        return fdiff, new_source
    return False, ''


def load_dictionary(ctx):
    for version in ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0'):
        src_file = change_name(ctx, ctx['src_file'], version)
        load_dictionary_from_file(src_file)
    # if ctx['opt_verbose']:
    #     print(TNL_DICT)
    return 0


def parse_file(ctx):
    for version in ('12.0', '11.0', '10.0', '9.0', '8.0', '7.0'):
        src_file = change_name(ctx, ctx['src_file'], version)
        fdiff, target = parse_source(src_file)
        if not fdiff:
            if ctx['opt_verbose']:
                print("No change done")
        else:
            if ctx['dst_file'] and ctx['dst_file'] != ctx['src_file']:
                dst_file = change_name(ctx, ctx['dst_file'], version)
            else:
                dst_file = src_file
            if dst_file != src_file:
                if ctx['opt_verbose']:
                    print("Writing %s" % ctx['dst_file'])
                fd = open(ctx['dst_file'], 'w')
                fd.write(os0.b(target))
                fd.close()
            else:
                tmpfile = '%s.tmp' % dst_file
                bakfile = '%s.bak' % dst_file
                fd = open(tmpfile, 'w')
                fd.write(os0.b(target))
                fd.close()
                if os.path.isfile(bakfile):
                    os.remove(bakfile)
                os.rename(src_file, bakfile)
                os.rename(tmpfile, dst_file)
    return 0


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Translate Odoo Package",
                          "© 2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('src_file')
    parser.add_argument('dst_file',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    sts = load_dictionary(ctx)
    sts = parse_file(ctx)
    sys.exit(sts)
