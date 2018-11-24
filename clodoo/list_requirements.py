#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from subprocess import PIPE, Popen
import ast
import sys
import os
import re
import z0lib


__version__ = '0.3.8'
python_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])

#
# known incompantibilities:
# - requests: oca-maintainers-tools -> '==2.3.0',
#             codecov -> '>=2.7.9'
REQVERSION = {
    'acme_tiny': {'7.0': '>=4.0.3'},
    'argparse': {'0': '==1.2.1'},
    'astroid': {'7.0': '==1.4.8', '0': '==1.6.3'},       # Version by test pkgs
    'autopep8': {'0': '==1.2'},
    'Babel': {'7.0': '==1.3', '8.0': '==2.3.4'},
    'beautifulsoup': {'7.0': '==3.2.1'},
    'codicefiscale': {'7.0': '==0.9'},
    'cryptography': {'7.0': '2.2.2'},
    'decorator': {'7.0': '==3.4.0', '10.0': '==4.0.10'},
    'docutils': {'7.0': '==0.12', '0': '==0.14'},        # Version by test pkgs
    'ebaysdk': {'7.0': '==2.1.4'},
    'ERPpeek': {'0': '==1.6.1'},
    'feedparser': {'7.0': '==5.1.3', '10.0': '==5.2.1'},
    'flake8': {'7.0': '==3.4.1'},           # Tested 3.5.0; 3.6.0 does not work
    'gdata': {'7.0': '==2.0.18'},
    'gevent': {'7.0': '==1.0.2', '10.0': '==1.1.2'},
    'greenlet': {'7.0': '==0.4.10'},
    'ipy': {'7.0': '>=0.83'},
    'isort': {'0': '==4.3.4'},                           # Version by test pkgs
    'jcconv': {'7.0': '==0.2.3'},
    'Jinja2': {'7.0': '==2.7.3', '10.0': '==2.8'},
    'lxml': {'7.0': '>=3.4.1', '10.0': '==3.5.0', '0': '==4.2.1'},
    'Mako':  {'7.0': '==1.0.1', '8.0': '==1.0.4'},
    'MarkupSafe': {'7.0': '>=0.23'},                    # Tested 1.0
    'mock': {'7.0': '==1.0.1', '8.0': '==2.0.0'},
    'ofxparse': {'7.0': '==0.16'},
    'passlib': {'7.0': '==1.6.2', '10.0': '==1.6.5'},
    'Pillow': {'7.0': '==3.4.2', '8.0': '==3.4.1', '0': '==3.4.2'},
    'psutil': {'7.0': '==2.2.0', '8.0': '==4.3.1'},
    'psycogreen': {'7.0': '==1.0'},
    'psycopg2-binary': {'7.0': '>=2.0.0',
                        # '8.0': '==2.5.4',
                        # '10.0': '==2.6.2',
                        '0': '==2.7.4'},
    'pydot': {'7.0': '==1.0.2', '8.0': '==1.2.3'},
    'Pygments': {'7.0': '==2.0.2', '0': '==2.2'},        # Version by test pkgs
    'pylint': {'7.0': '==1.6.4'},                        # Version by test pkgs
    'pylint-plugin-utils': {'7.0': '==0.2.4',
                            '0': '==0.2.4'},             # Version by test pkgs
    'pysftp': {'7.0': '>=0.2.9'},
    'pyparsing': {'7.0': '==2.0.3', '10.0': '==2.1.10'},
    'pyPdf': {'7.0': '==1.13'},
    'pyserial':  {'7.0': '==2.7', '10.0': '==3.1.1'},
    'Python-Chart': {'7.0': '==1.39'},
    'python-dateutil': {'7.0': '==2.4.0', '8.0': '==2.5.3'},
    'python-ldap': {'7.0': '==2.4.19',
                    '10.0': '==2.4.25'},        # warning OCA declare 2.4.27!?
    'python-openid': {'7.0': '==2.2.5'},
    'python-stdnum': {'7.0': '>=1.8.1'},
    'pytz': {'7.0': '==2014.10', '10.0': '==2016.7'},
    'pyusb': {'7.0': '>=1.0.0b1', '10.0': '==1.0.0'},
    'pyxb': {'7.0':  '==1.2.4'},
    'PyWebDAV': {'7.0':  '<0.9.8'},
    'PyYAML': {'7.0': '==3.11', '8.0': '==3.12'},
    'qrcode': {'7.0': '==5.1', '10.0': '==5.3'},
    'restructuredtext_lint': {'7.0': '==0.12.2',
                              '0': '==1.1'},             # Version by test pkgs
    'reportlab': {'7.0': '==3.1.44', '10.0': '==3.3.0'},
    'requests': {'7.0': '==2.6.0', '10.0': '==2.11.1'},
    'simplejson': {'7.0': '==3.5.3'},
    'six': {'7.0': '==1.9.0',  '10.0': '==1.10.0'},
    'suds': {'7.0': '==0.4'},
    'suds-jurko': {'7.0': '==0.6'},
    'unicodecsv': {'7.0': '>=0.14.1'},
    'unidecode': {'7.0': '==0.4.17'},
    'unittest2': {'7.0': '==0.5.1'},
    'validate_email': {'7.0': '>=1.3'},
    'vatnumber': {'7.0': '==1.2'},
    'vobject': {'7.0': '==0.9.3'},                      # Tested 0.9.5
    'Werkzeug': {'0': '==0.11.11', '7.0': '==0.9.6', '10.0': '==0.11.11'},
    'wkhtmltopdf': {'7.0': '==0.12.1', '10.0': '==0.12.4'},
    'wsgiref': {'7.0': '==0.1.2'},
    'XlsxWriter': {'7.0': '==0.9.3'},                   # Tested 1.0.2
    'xlrd': {'7.0': '==1.0.0'},
    'xlwt': {'7.0': '==0.7.5', '10.0': '==1.1.2'},
}
ALIAS = {
    'babel': 'Babel',
    'click': 'Click',
    'dateutil': 'python-dateutil',
    'jinja2': 'Jinja2',
    'ldap': 'python-ldap',
    'lxml': 'lxml',
    'mako': 'Mako',
    'markupsafe': 'MarkupSafe',
    'openid': 'python-openid',
    'pillow': 'Pillow',
    'psycopg2': 'psycopg2-binary',
    'pypdf': 'pyPdf',
    'pygments': 'Pygments',
    'python-chart': 'Python-Chart',
    'pywebdav': 'PyWebDAV',
    'pyyaml': 'PyYAML',
    'requests': 'requests[security]',
    'qunitsuite': 'QUnitSuite',
    'serial': 'pyserial',
    'stdnum': 'python-stdnum',
    'usb': 'pyusb',
    'werkzeug': 'Werkzeug',
    'xlsxwriter': 'XlsxWriter',
}
PIP_TEST_PACKAGES = ['astroid',
                     'Click',
                     'configparser',
                     'codecov',
                     'coveralls',
                     'docutils',
                     'flake8',
                     'isort',
                     'lazy_object_proxy',
                     'lxml',
                     'MarkupSafe',
                     'mock',
                     'pbr',
                     'pycparser',
                     'pyflakes',
                     'pylint',
                     'pylint-mccabe',
                     'pylint_odoo',
                     'pylint-plugin-utils',
                     'PyWebDAV',
                     'PyYAML',
                     'QUnitSuite',
                     'restructuredtext_lint',
                     'rfc3986',
                     'unittest2',
                     'urllib3[secure]',
                     'whichcraft',
                     'wrapt',
                     'zerobug',
                     ]
BIN_TEST_PACKAGES = ['build-essential',
                     'expect-dev',
                     'libffi-dev',
                     'libssl-dev',
                     'python-dev',
                     'python-setuptools',
                     ]
RPC_PACKAGES = ['clodoo',
                'odoorpc',
                'oerplib',
                'os0',
                ]
PIP_BASE_PACKAGES = ['Babel',
                     'configparser',
                     'decorator',
                     'docutils',
                     'feedparser',
                     'gdata',
                     'gevent',
                     'Jinja2',
                     'lxml',
                     'Mako',
                     'numpy',
                     'passlib',
                     'Pillow',
                     'psutil',
                     'psycogreen',
                     # 'psycopg2',
                     'psycopg2-binary',
                     'Python-Chart',
                     'python-ldap',
                     'python-dateutil',
                     'python-openid',
                     'pydot',
                     'pyparsing',
                     'pypdf',
                     'pyserial',
                     'pytz',
                     'reportlab',
                     'simplejson',
                     'six',
                     'stdnum',
                     'urllib3[secure]',
                     'vatnumber',
                     'Werkzeug',
                     ]
BIN_BASE_PACKAGES = ['curl',
                     'nodejs',
                     'npm',
                     # 'python-psycopg2',
                     'python-simplejson',
                     'wkhtmltopdf',
                     ]
BIN_PACKAGES = ['git',
                'cups',
                ]
cmd = ['python3', '--version']
try:
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    res, err = p.communicate()
    i = res.find('3.')
    if i >= 0:
        PY3ID = res[i] + res[i+2]
    else:
        PY3ID = "3"
except BaseException:
    PY3ID = "3"
PY3_DEV = 'python%s-dev' % PY3ID


def parse_requirements(reqfile):
    lines = open(reqfile, 'rU').read().split('\n')
    reqlist = []
    for line in lines:
        if line and line[0] != '#':
            items = line.split(';')
            if len(items) == 1 or eval(items[1].strip().replace(
                    '_', '.').replace('python.version', 'python_version')):
                item = items[0].strip()
                reqlist.append(item)
    return reqlist


def name_n_version(full_item, with_version=None, odoo_ver=None):
    item = re.split('[!=<>]', full_item)
    if len(item) == 1:
        full_item = ''
    item = item[0]
    item = os.path.basename(item)
    if item[0:5] != 'py3o.':
        item = item.split('.')[0].lower()
    if item in ALIAS:
        item = ALIAS[item]
    defver = False
    if with_version:
        if item in REQVERSION:
            min_v = False
            valid_ver = False
            for v in ('0', '12.0', '11.0', '10.0', '9.0', '8.0', '7.0', '6.1'):
                if v in REQVERSION[item]:
                    min_v = v
                    if v == odoo_ver or valid_ver or (not odoo_ver and
                                                      v == '0'):
                        break
                elif v == odoo_ver:
                    valid_ver = True
            if min_v:
                full_item = '%s%s' % (item, REQVERSION[item][min_v])
                if full_item.find('>') >= 0 or full_item.find('<') >= 0:
                    full_item = "'%s'" % full_item
                defver = True
    return item, full_item, defver


def add_package(deps_list, kw, item, with_version=None, odoo_ver=None):
    item, full_item, defver = name_n_version(item,
                                             with_version=with_version,
                                             odoo_ver=odoo_ver)
    if item in BIN_PACKAGES or \
            item in BIN_BASE_PACKAGES or \
            item in BIN_TEST_PACKAGES:
        kw = 'bin'
    if item not in deps_list[kw]:
        deps_list[kw].append(item)
        if kw == 'python':
            if with_version and full_item:
                kw = 'python2'
                deps_list[kw].append(full_item)
            else:
                kw = 'python1'
                deps_list[kw].append(item)
            if item == 'barcode':
                deps_list = add_package(deps_list, kw,
                                        'python-Levenshtein',
                                        with_version=with_version,
                                        odoo_ver=odoo_ver)
            elif item == 'simplejson':
                deps_list = add_package(deps_list, kw,
                                        'python-simplejson',
                                        with_version=with_version,
                                        odoo_ver=odoo_ver)
            elif item == 'lxml':
                if odoo_ver in ('11.0', '12.0'):
                    for itm in (PY3_DEV, 'libxml2-dev',
                                'libxslt1-dev', 'zlib1g-dev'):
                        deps_list = add_package(deps_list, 'bin', itm,
                                                with_version=with_version,
                                                odoo_ver=odoo_ver)
                else:
                    for itm in ('python-dev', 'libxml2-dev',
                                'libxslt1-dev', 'zlib1g-dev'):
                        deps_list = add_package(deps_list, 'bin', itm,
                                                with_version=with_version,
                                                odoo_ver=odoo_ver)
            elif item in ('lxml', 'python-psycopg2'):
                if odoo_ver in ('11.0', '12.0'):
                    for itm in (PY3_DEV, 'libpq-dev'):
                        deps_list = add_package(deps_list, 'bin', itm,
                                                with_version=with_version,
                                                odoo_ver=odoo_ver)
                else:
                    for itm in ('python-dev', 'libpq-dev'):
                        deps_list = add_package(deps_list, 'bin', itm,
                                                with_version=with_version,
                                                odoo_ver=odoo_ver)
    elif kw == 'python' and full_item:
        if item in deps_list['python1']:
            i = deps_list['python1'].index(item)
            del deps_list['python1'][i]
            deps_list['python2'].append(full_item)
        elif not defver and full_item not in deps_list['python2']:
            sys.stderr.write('Version mismatch: package %s\n' % full_item)
    return deps_list


def package_from_list(deps_list, kw, PKG_LIST,
                      with_version=None, odoo_ver=None):
    for item in PKG_LIST:
        deps_list = add_package(deps_list, kw, item,
                                with_version=with_version,
                                odoo_ver=odoo_ver)
    return deps_list


def package_from_manifest(deps_list, manifest_file,
                          with_version=None, odoo_ver=None):
    if manifest_file:
        manifest = ast.literal_eval(open(manifest_file, 'rU').read())
        if manifest.get('external_dependencies'):
            deps = manifest['external_dependencies']
            for kw in ('python', 'bin'):
                if deps.get(kw):
                    for item in deps[kw]:
                        deps_list = add_package(deps_list,
                                                kw,
                                                item,
                                                with_version=with_version,
                                                odoo_ver=odoo_ver)
        if manifest.get('depends'):
            deps = manifest['depends']
            kw = 'modules'
            for item in deps:
                deps_list = add_package(deps_list,
                                        kw,
                                        item,
                                        with_version=with_version,
                                        odoo_ver=odoo_ver)
    return deps_list


def add_manifest(root, manifests, reqfiles, files):
    for f in files:
        if f == '__openerp__.py':
            ffn = os.path.join(root, f)
            manifests.append(ffn)
        elif f == '__manifest__.py':
            ffn = os.path.join(root, f)
            manifests.append(ffn)
        elif f == 'requirements.txt':
            ffn = os.path.join(root, f)
            reqfiles.append(ffn)
    return manifests, reqfiles


def main():
    # global __version__
    parser = z0lib.parseoptargs("List Odoo requirements",
                                "© 2017-2018 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        dest='odoo_ver')
    parser.add_argument("-B", "--base-packages",
                        help="Add base packages",
                        action="store_true",
                        dest="base_pkgs")
    parser.add_argument("-d", "--dependencies-path",
                        help="Follow oca_dependencies.txt in directory",
                        metavar="directory list (comma separated)",
                        dest="oca_dependencies")
    parser.add_argument("-m", "--manifest",
                        help="Declare manifest files if no path supplied",
                        dest="manifests",
                        metavar="file list",
                        default="")
    parser.add_argument('-n')
    parser.add_argument("-o", "--output",
                        help="Write output to file requirements.txt",
                        dest="out_file",
                        action="store_true")
    parser.add_argument("-p", "--path",
                        help="Path where search manifest files",
                        dest="odoo_dir",
                        metavar="directory",
                        default="")
    parser.add_argument("-P", "--precise",
                        help="Add version to filename",
                        action="store_true",
                        dest="with_version")
    parser.add_argument('-q')
    parser.add_argument("-R", "--rpc-packages",
                        help="Add packages for xmlrpc/jsonrpc",
                        action="store_true",
                        dest="rpc_pkgs")
    parser.add_argument("-s", "--sep",
                        help="Separator character of list",
                        dest="sep",
                        metavar="character",
                        default=",")
    parser.add_argument("-t", "--type",
                        help="File type: may be bin,python,both or modules",
                        dest="itypes",
                        metavar="keyword",
                        default="both")
    parser.add_argument("-T", "--tests-packages",
                        help="Add packages for test",
                        action="store_true",
                        dest="test_pkgs")
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    if ctx['out_file']:
        if not ctx['odoo_dir']:
            sys.stderr.write(
                'Please, declare odoo path to write requirements.txt file!\n')
            sys.exit(1)
        ctx['sep'] = '\n'
        ctx['with_version'] = True
        ctx['itypes'] = 'python'
        ctx['opt_verbose'] = False
        ctx['base_pkgs'] = False
        ctx['rpc_pkgs'] = False
        ctx['test_pkgs'] = False
        ctx['oca_dependencies'] = False
        ctx['opt_fn'] = '/'.join([ctx['odoo_dir'], 'requirements.txt'])
    if ctx['odoo_dir']:
        manifests = []
        reqfiles = []
        if ctx['oca_dependencies']:
            for cdir in ctx['oca_dependencies'].split(','):
                for root, dirs, files in os.walk(cdir,
                                                 followlinks=True):
                    manifests, reqfiles = add_manifest(root,
                                                       manifests,
                                                       reqfiles,
                                                       files)
        for root, dirs, files in os.walk(ctx['odoo_dir']):
            manifests, reqfiles = add_manifest(root,
                                               manifests,
                                               reqfiles,
                                               files)
    else:
        manifests = ctx['manifests'].split(',')
        reqfiles = []
    deps_list = {}
    for kw in ('python', 'python1', 'python2', 'bin', 'modules'):
        deps_list[kw] = []
    for reqfile in reqfiles:
        requirements = parse_requirements(reqfile)
        deps_list = package_from_list(deps_list, 'python', requirements,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
    for manifest_file in manifests:
        deps_list = package_from_manifest(deps_list,
                                          manifest_file,
                                          with_version=ctx['with_version'],
                                          odoo_ver=ctx['odoo_ver'])
    if ctx['base_pkgs']:
        deps_list = package_from_list(deps_list, 'python', PIP_BASE_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
        deps_list = package_from_list(deps_list, 'bin', BIN_BASE_PACKAGES,
                                      with_version=False,
                                      odoo_ver=ctx['odoo_ver'])
    if ctx['test_pkgs']:
        deps_list = package_from_list(deps_list, 'python', PIP_TEST_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
        deps_list = package_from_list(deps_list, 'bin', BIN_TEST_PACKAGES,
                                      with_version=False,
                                      odoo_ver=ctx['odoo_ver'])
    if ctx['rpc_pkgs']:
        deps_list = package_from_list(deps_list, 'python', RPC_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'])
    if ctx['out_file']:
        try:
            pkgs = open(ctx['opt_fn'], 'rU').read().split('\n')
        except BaseException:
            pkgs = []
        for kw in ('python1', 'python2'):
            for p in deps_list[kw]:
                if p not in pkgs:
                    pkgs.append(p)
        if len(pkgs):
            fd = open(ctx['opt_fn'], 'w')
            fd.write(ctx['sep'].join(pkgs))
            fd.close()
        print("Updated %s file" % ctx['opt_fn'])
        print(ctx['sep'].join(pkgs))
    else:
        deps_list['python'] = deps_list['python1'] + deps_list['python2']
        for kw in ('python', 'bin', 'modules'):
            if kw in deps_list:
                if kw == ctx['itypes'] or (ctx['itypes'] == 'both' and
                                           kw in ('python', 'bin')):
                    if ctx['opt_verbose']:
                        print('%s=%s' % (kw, ctx['sep'].join(deps_list[kw])))
                    else:
                        print(ctx['sep'].join(deps_list[kw]))


if __name__ == "__main__":
    sts = main()
    sys.exit(sts)
