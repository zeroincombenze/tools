#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import sys
import os
import z0lib


__version__ = '0.3.5.11'


REQVERSION = {
    'astroid': '==1.4.8',
    'Babel': '>=1.0',
    'gevent': '==1.0.2',
    'Pillow': '==3.4.2',
    'psycopg2': '>=2.2',
    'pygments': '==2.0.2',
    'pylint': '==1.6.4',
    'pylint-plugin-utils': '==0.3.5.11',
    'pyparsing': '<2',
    'pyxb': '==1.2.4',
    'restructuredtext_lint': '==0.12.2',
}
PIP_TEST_PACKAGES = ['astroid',
                     'coveralls',
                     'flake8',
                     'pylint',
                     'PyYAML',
                     'mock',
                     # 'pylint-plugin-utils',
                     'QUnitSuite',
                     'restructuredtext_lint',
                     'unittest2']
RPC_PACKAGES = ['odoorpc',
                'oerplib',
                'os0']
PIP_BASE_PACKAGES = ['Babel',
                     'configparser',
                     'decorator',
                     'docutils',
                     'feedparser',
                     'gevent',
                     'Jinja2',
                     'lxml',
                     'Mako',
                     'passlib',
                     'Pillow',
                     'psutil',
                     'psycogreen',
                     'psycopg2',
                     'psycopg2-binary',
                     'Python-Chart',
                     'python-dateutil',
                     'pydot',
                     'pyparsing',
                     'pypdf',
                     'pyserial',
                     'pytz',
                     'reportlab',
                     'werkzeug']

BIN_BASE_PACKAGES = ['python-simplejson',
                     'python-ldap']


def name_n_version(item, with_version=None):
    item = os.path.basename(item).split('.')[0]
    if with_version and item in REQVERSION:
        item = '%s%s' % (item, REQVERSION[item])
    return item


def print_deps(manifest_file, deps_list=None, with_version=None):
    deps_list = deps_list or {}
    if manifest_file:
        manifest = ast.literal_eval(open(manifest_file).read())
        if manifest.get('external_dependencies'):
            deps = manifest['external_dependencies']
            for kw in ('python', 'bin'):
                if deps.get(kw):
                    if kw not in deps_list:
                        deps_list[kw] = []
                    for item in deps[kw]:
                        full_item = name_n_version(item,
                                                   with_version=with_version)
                        if full_item not in deps_list[kw]:
                            deps_list[kw].append(full_item)
    return deps_list


def main():
    # global __version__
    parser = z0lib.parseoptargs("List Odoo requirements",
                                "© 2017-2018 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument("-B", "--base-packages",
                        help="Add base packages",
                        action="store_true",
                        dest="base_pkgs")
    parser.add_argument("-m", "--manifest",
                        help="Declare manifest files if no path supplied",
                        dest="manifests",
                        metavar="file list",
                        default="")
    parser.add_argument('-n')
    parser.add_argument("-p", "--path",
                        help="Path to search manifest files",
                        dest="odoo_dir",
                        metavar="directory",
                        default="")
    parser.add_argument("-P", "--precise",
                        help="Add version to filename",
                        action="store_true",
                        dest="with_version")
    parser.add_argument('-q')
    parser.add_argument("-R", "--rpc-packages",
                        help="Add packages to use xmlrpc/jsonrpc",
                        action="store_true",
                        dest="rpc_pkgs")
    parser.add_argument("-s", "--sep",
                        help="Separator character of list",
                        dest="sep",
                        metavar="character",
                        default=",")
    parser.add_argument("-t", "--type",
                        help="Type of files; may be bin,python or both",
                        dest="itypes",
                        metavar="keyword",
                        default="both")
    parser.add_argument("-T", "--tests-packages",
                        help="Add packages to test",
                        action="store_true",
                        dest="test_pkgs")
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    deps_list = {}
    if ctx['odoo_dir']:
        manifests = []
        for root, dirs, files in os.walk(ctx['odoo_dir']):
            for f in files:
                if f == '__openerp__.py':
                    ffn = '%s/%s' % (root, f)
                    manifests.append(ffn)
                elif f == '__manifest__.py':
                    ffn = '%s/%s' % (root, f)
                    manifests.append(ffn)
    else:
        manifests = ctx['manifests'].split(',')
    if ctx['base_pkgs']:
        kw = 'python'
        if kw not in deps_list:
            deps_list[kw] = []
        for item in PIP_BASE_PACKAGES:
            deps_list[kw].append(
                name_n_version(item,
                               with_version=ctx['with_version']))
    if ctx['test_pkgs']:
        kw = 'python'
        if kw not in deps_list:
            deps_list[kw] = []
        for item in PIP_TEST_PACKAGES:
            deps_list[kw].append(
                name_n_version(item,
                               with_version=ctx['with_version']))
    if ctx['rpc_pkgs']:
        kw = 'python'
        if kw not in deps_list:
            deps_list[kw] = []
        for item in RPC_PACKAGES:
            deps_list[kw].append(
                name_n_version(item,
                               with_version=ctx['with_version']))
    for manifest_file in manifests:
        deps_list = print_deps(manifest_file,
                               deps_list=deps_list,
                               with_version=ctx['with_version'])
    for kw in ('python', 'bin'):
        if (ctx['itypes'] == 'both' or kw == ctx['itypes']) and \
                kw in deps_list:
            if ctx['opt_verbose']:
                print '%s=%s' % (kw, ctx['sep'].join(deps_list[kw]))
            else:
                print ctx['sep'].join(deps_list[kw])


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)
