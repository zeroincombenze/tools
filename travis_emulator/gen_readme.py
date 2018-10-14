#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import ast
import os
import re
import sys
import z0lib


__version__ = "0.2.1.54"


def get_template_path(ctx, template):
    for src_path in ('.',
                     '/opt/odoo/dev/pypi/tools/templates',
                     '/opt/odoo/dev/templates'):
        if src_path.find('/dev/tools/') >= 0 and not ctx['dbg_template']:
            continue
        full_fn = os.path.join(src_path, template)
        if os.path.isfile(full_fn):
            break
    if not os.path.isfile(full_fn):
        raise IOError('Template %s not found' % template)
    return full_fn


def write_footer(ctx):
    pass


def parse_source(ctx, filename):
    full_fn = get_template_path(ctx, filename)
    if ctx['opt_verbose']:
        print("Reading %s" % full_fn)
    fd = open(full_fn, 'rU')
    source = fd.read()
    fd.close()
    target = ''
    for line in source.split('\n'):
        if line[0:12] == '.. $include ':
            filename = line[12:].strip()
            text = parse_source(ctx, filename)
            target += text
        else:
            target += line
            target += '\n'
    return target


def generate_readme(ctx):
    ctx['dst_file'] = './README.rst'
    target = parse_source(ctx, 'readme_main_%s.rst' % ctx['odoo_level'])
    tmpfile = '%s.tmp' % ctx['dst_file']
    bakfile = '%s.bak' % ctx['dst_file']
    fd = open(tmpfile, 'w')
    fd.write(target)
    fd.close()
    if os.path.isfile(bakfile):
        os.remove(bakfile)
    if os.path.isfile(ctx['dst_file']):
        os.rename(ctx['dst_file'], bakfile)
    os.rename(tmpfile, ctx['dst_file'])


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Generate README",
                          "© 2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument('-B', '--debug-template',
                        action='store_true',
                        dest='dbg_template')
    parser.add_argument('-l', '--level',
                        action='store',
                        help='ocb|module|repository',
                        dest='odoo_level')
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
    if ctx['odoo_level'] not in ('ocb', 'module', 'repository'):
        print('Invalid level: user one of ocb|module|repository')
        ctx['odoo_level'] = 'module'
    sts = generate_readme(ctx)
    sys.exit(sts)
