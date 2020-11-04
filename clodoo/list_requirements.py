#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from subprocess import PIPE, Popen
import ast
import sys
import os
import re
try:
    from z0lib import z0lib
except ImportError:
    import z0lib


__version__ = '0.3.28.6'
python_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])

#
# known incompatibilities:
# - requests: oca-maintainers-tools -> '==2.3.0',
#             codecov -> '>=2.7.9'
# Here we assume: Odoo 11.0 use python 3.5, Odoo 12.0 uses python 3.7
# If version is 2.7 or 3.5 otr 3.6 or 3.7 the it refers to python version
REQVERSION = {
    'acme_tiny': {'7.0': '>=4.0.3'},
    'argparse': {'0': '==1.2.1'},
    'astroid': {'2.7': '==1.6.5', '3.5': '==2.2.0'},     # Version by test pkgs
    'autopep8': {'0': '==1.2'},
    'Babel': {'7.0': '==1.3', '8.0': '==2.3.4'},
    'beautifulsoup': {'7.0': '==3.2.1'},
    'codicefiscale': {'7.0': '==0.9'},
    'coverage': {'0': '<5.0.0'},
    'cryptography': {'7.0': '>=2.2.2'},
    'decorator': {'7.0': '==3.4.0', '10.0': '==4.0.10'},
    'docutils': {'7.0': '==0.12', '0': '==0.14'},        # Version by test pkgs
    'ebaysdk': {'7.0': '==2.1.4'},
    'ERPpeek': {'0': '==1.6.1'},
    'feedparser': {'7.0': '==5.1.3', '10.0': '==5.2.1'},
    'flake8': {'7.0': '==3.4.1'},           # Tested 3.5.0; 3.6.0 does not work
    'gdata': {'7.0': '==2.0.18'},
    'gevent': {'7.0': '==1.0.2', '10.0': '==1.1.2',
               '12.0': '==1.3.4'},                       # With py3.7 -> 1.3.4
    'greenlet': {'7.0': '==0.4.10',
                 '12.0': '>=0.4.13'},                    # With py3.7 -> 0.4.13
    'ipy': {'7.0': '>=0.83'},
    'isort': {'0': '==4.3.4'},                           # Version by test pkgs
    'jcconv': {'7.0': '==0.2.3'},
    'Jinja2': {'7.0': '==2.7.3', '9.0': '==2.8.1', '10.0': '==2.10.1'},
    'lessc': {'0': '==3.0.4'},
    'lxml': {'7.0': '>=3.4.1', '0': '==4.2.3'},
    'Mako':  {'7.0': '==1.0.1', '8.0': '==1.0.4'},
    'MarkupSafe': {'7.0': '>=0.23'},                    # Tested 1.0
    'mock': {'7.0': '==1.0.1', '8.0': '==2.0.0'},
    'ofxparse': {'7.0': '==0.16'},
    'passlib': {'7.0': '==1.6.2', '10.0': '==1.6.5'},
    'Pillow': {'7.0': '==3.4.2', '8.0': '==3.4.1', '11.0': '==4.0.0',
               '12.0': '==6.1.0', '0': '==4.0.0'},        # With py3.7 -> 6.1.0
    'psutil': {'7.0': '==2.2.0', '8.0': '==4.3.1'},
    'psycogreen': {'7.0': '==1.0'},
    'psycopg2-binary': {# '7.0': '>=2.0.0',
                        # '8.0': '==2.5.4',
                        '12.0': '>=2.8.3',
                        '0': '>=2.7.4'},
    'pycodestyle': {'0': '==2.3.1'},
    'pydot': {'7.0': '==1.0.2', '8.0': '==1.2.3'},
    'Pygments': {'7.0': '==2.0.2', '0': '==2.2'},        # Version by test pkgs
    'pylint': {'2.7': '==1.9.3', '3.5': '==2.3.0'},
    'pylint-plugin-utils': {'2.7': '==0.4',
                            '3.5': '==0.5'},
    'pyopenssl': {'0': '>=16.2.0', },                    # by MQT
    'pyotp': {'2.7': '==2.3.0', '3.5': '>=2.4.0'},
    'pysftp': {'7.0': '>=0.2.9'},
    'pyparsing': {'7.0': '==2.0.3', '10.0': '==2.1.10'},
    'pyPdf': {'7.0': '==1.13'},
    'pyserial':  {'7.0': '==2.7', '10.0': '==3.1.1'},
    'Python-Chart': {'7.0': '==1.39'},
    'python-dateutil': {'7.0': '==2.4.0', '8.0': '==2.5.3'},
    'python-ldap': {'7.0': '==2.4.19',
                    '10.0': '==2.4.25',      # warning OCA declare 2.4.27!?
                    '11.0': '>=0.9.8.4'},
    'python-openid': {'7.0': '==2.2.5'},
    'python-stdnum': {'7.0': '>=1.8.1'},
    'pytz': {'7.0': '==2014.10', '10.0': '==2016.7'},
    'pyusb': {'7.0': '>=1.0.0b1', '10.0': '==1.0.0'},
    'pyxb': {'7.0':  '==1.2.5'},
    'PyWebDAV': {'7.0':  '<0.9.8'},
    'PyYAML': {'7.0': '==3.11', '8.0': '==3.12', '3.6': '>=5.1'},
    'qrcode': {'7.0': '==5.1', '10.0': '==5.3'},
    'restructuredtext_lint': {'7.0': '==0.12.2',
                              '0': '==1.1.3'},
    'reportlab': {'7.0': '==3.1.44', '10.0': '==3.3.0'},
    'requests': {'7.0': '==2.6.0', '10.0': '==2.11.1'},
    'simplejson': {'7.0': '==3.5.3'},
    'six': {'7.0': '==1.9.0',  '10.0': '==1.10.0'},
    'suds': {'7.0': '==0.4'},
    'suds-jurko': {'7.0': '==0.6'},
    'unicodecsv': {'7.0': '>=0.14.1'},
    'unidecode': {'7.0': '==0.4.17'},
    'unittest2': {'7.0': '==0.5.1', '11.0': '>=1.0.0'},
    'validate_email': {'7.0': '>=1.3'},
    'vatnumber': {'7.0': '==1.2'},
    'vobject': {'7.0': '==0.9.3'},                      # Tested 0.9.5
    'Werkzeug': {'7.0': '==0.9.6', '10.0': '==0.11.11', '11.0': '==0.11.15'},
    'wkhtmltopdf': {'7.0': '==0.12.1', '10.0': '==0.12.4', '12.0': '==0.12.5'},
    'wsgiref': {'7.0': '==0.1.2'},
    'XlsxWriter': {'7.0': '==0.9.3'},                   # Tested 1.0.2
    'xlrd': {'7.0': '==1.0.0'},
    'xlwt': {'7.0': '==0.7.5', '10.0': '==1.1.2', '12.0': '==1.3'},
}
ALIAS = {
    'babel': 'Babel',
    'click': 'Click',
    'crypto': 'pycrypto',
    'dateutil': 'python-dateutil',
    'jinja2': 'Jinja2',
    'ldap': 'python-ldap',
    'lxml': 'lxml',
    'mako': 'Mako',
    'markupsafe': 'MarkupSafe',
    'openid': 'python-openid',
    'past': 'future',
    'pillow': 'Pillow',
    'psycopg2': 'psycopg2-binary',
    'pychart': 'PyChart',
    'pypdf': 'pyPdf',
    'pypdf2': 'pyPDF2',
    'pygments': 'Pygments',
    'python-chart': 'Python-Chart',
    'python-docutils': 'docutils',
    'python-levenshtein': 'python-Levenshtein',
    'python-simplejson': 'simplejson',
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
ALIAS3 = {
    'PyWebDAV': 'PyWebDAV3',
    'python-ldap': 'python3-ldap',
    'pyPdf': 'pyPDF2',
}
PIP_TEST_PACKAGES = ['astroid',
                     'Click',
                     'configparser',
                     'codecov',
                     'coverage',
                     'coveralls',
                     'docopt',
                     'docutils',
                     'flake8',
                     'isort',
                     'lazy_object_proxy',
                     'lxml',
                     'MarkupSafe',
                     'mock',
                     'pbr',
                     'polib',
                     'pycodestyle',
                     'pycparser',
                     'pyflakes',
                     'Pygments',
                     'pylint',
                     'pylint-mccabe',
                     'pylint_odoo',
                     'pylint-plugin-utils',
                     'pyopenssl',
                     'python_plus',
                     'pyserial',
                     'pytest',
                     'PyWebDAV',
                     'PyYAML',
                     'QUnitSuite',
                     'restructuredtext_lint',
                     'rfc3986',
                     'setuptools',
                     'simplejson',
                     'unittest2',
                     'urllib3[secure]',
                     'websocket-client',
                     'whichcraft',
                     'wrapt',
                     'z0bug_odoo',
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
                     'chardet',
                     'configparser',
                     'decorator',
                     'docutils',
                     'feedparser',
                     'future',
                     'gdata',
                     'gevent',
                     'html2text',
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
PIP3_BASE_PACKAGES = []
BIN_BASE_PACKAGES = ['curl',
                     'lessc',
                     'less-plugin-clean-css',
                     'nodejs',
                     'npm',
                     'wkhtmltopdf',
                     'zlib1g',
                     ]
BIN_PACKAGES = ['git',
                'cups',
                # 'pychart',
                # 'PyChart',
                # 'pyvies',
                ]
PIP_WITH_DOT = ['py3o.',
                'anybox.',
                ]
# Retrieve python3 version
cmd = ['python3', '--version']
try:
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    res, err = p.communicate()
    res = res.decode()
    i = res.find('3.')
    if i >= 0:
        PY3ID = res[i] + res[i+2]
    else:
        PY3ID = "3"
except BaseException:
    PY3ID = "3"
PY3_DEV = 'python%s-dev' % PY3ID
DEPS = {
    'barcode': {'python': 'python-Levenshtein'},
    'astroid': {'python': 'six'},
    'Pillow': {'python': 'docutils'},
}
DEPS2 = {
    'lxml': {'bin': ('python-dev', 'libxml2-dev',
             'libxslt1-dev', 'zlib1g-dev')},
    'python-psycopg2': {'bin': ('python-dev', 'libpq-dev')},
}
DEPS3 = {
    'lxml': {'bin': (PY3_DEV, 'libxml2-dev',
            'libxslt1-dev', 'zlib1g-dev')},
    'python-psycopg2': {'bin': (PY3_DEV, 'libpq-dev')},
}
DEPS9 = ['pylint==1.9.3', 'pylint==1.9.5',
         'docutils==0.12', 'Pillow==3.4.1', 'Pygments==2.0.2',
         'pylint-plugin-utils==0.4']


def eval_requirement_cond(line, odoo_ver=None, pyver=None):
    odoo_ver = odoo_ver or '10.0'
    pyver = pyver or 3.7
    items = line.split(';')
    if len(items) == 1:
        return line.strip()
    testenv = {
        'sys_platform': sys.platform,
        'python_version': pyver,
    }
    if eval(items[1], testenv):
        return items[0].strip()
    return False


def parse_requirements(reqfile, odoo_ver=None, pyver=None):
    lines = open(reqfile, 'rU').read().split('\n')
    reqlist = []
    for line in lines:
        if line and line[0] != '#':
            item = eval_requirement_cond(line, odoo_ver=odoo_ver, pyver=pyver)
            if item:
                reqlist.append(item)
    return reqlist


def name_n_version(full_item, with_version=None, odoo_ver=None, pyver=None):
    item = re.split('[!=<>]', full_item)
    if len(item) == 1:
        full_item = ''
    item = item[0]
    item = os.path.basename(item)
    if not filter(lambda x: item.startswith(x), PIP_WITH_DOT):
        item = item.split('.')[0].lower()
    if item in ALIAS:
        item = ALIAS[item]
    if odoo_ver in ('13.0', '12.0', '11.0'):
        if item in ALIAS3:
            item = ALIAS3[item]
    defver = False
    if with_version:
        if item in REQVERSION:
            min_v = False
            valid_ver = False
            if pyver in REQVERSION[item]:
                min_v = pyver
            else:
                for v in ('3.7', '3.6', '3.5'):
                    if v in REQVERSION[item]:
                        min_v = v
                        break
            if not min_v:
                for v in ('0', '6.1', '7.0', '8.0', '9.0',
                          '10.0', '11.0', '12.0', '13.0'):
                    if v in REQVERSION[item]:
                        min_v = v
                        if v == odoo_ver or valid_ver or (not odoo_ver and
                                                          v == '0'):
                            break
                    elif v == odoo_ver:
                        valid_ver = True
                        if min_v:
                            break
            if min_v:
                full_item = '%s%s' % (item, REQVERSION[item][min_v])
                defver = True
    if item.startswith("'"):
        item = item[1: -1]
    if full_item.startswith("'"):
        full_item = full_item[1: -1]
    return item, full_item, defver


def add_package(deps_list, kw, item,
                with_version=None, odoo_ver=None, pyver=None):
    item, full_item, defver = name_n_version(item,
                                             with_version=with_version,
                                             odoo_ver=odoo_ver,
                                             pyver=pyver)
    if item in BIN_PACKAGES or \
            item in BIN_BASE_PACKAGES or \
            item in BIN_TEST_PACKAGES:
        kw = 'bin'
    if item not in deps_list[kw]:
        deps_list[kw].append(item)
        if kw == 'python':
            if with_version and full_item:
                if full_item in DEPS9:
                    kw = 'python9'
                else:
                    kw = 'python2'
                deps_list[kw].append(full_item)
            else:
                kw = 'python1'
                deps_list[kw].append(item)
            if item in DEPS:
                for kw1 in ('python', 'bin'):
                    if kw1 not in DEPS[item]:
                        continue
                    if isinstance(DEPS[item][kw1], (tuple, list)):
                        for itm in DEPS[item][kw1]:
                            deps_list = add_package(deps_list, kw1,
                                                    itm,
                                                    with_version=with_version,
                                                    odoo_ver=odoo_ver,
                                                    pyver=pyver)
                    else:
                        deps_list = add_package(deps_list, kw1,
                                                DEPS[item][kw1],
                                                with_version=with_version,
                                                odoo_ver=odoo_ver,
                                                pyver=pyver)
            if pyver and pyver.split('.')[0] == '2' and item in DEPS2:
                for kw1 in ('python', 'bin'):
                    if kw1 not in DEPS2[item]:
                        continue
                    if isinstance(DEPS2[item][kw1], (tuple, list)):
                        for itm in DEPS2[item][kw1]:
                            deps_list = add_package(deps_list, kw1,
                                                    itm,
                                                    with_version=with_version,
                                                    odoo_ver=odoo_ver,
                                                    pyver=pyver)
                    else:
                        deps_list = add_package(deps_list, kw1,
                                                DEPS2[item][kw1],
                                                with_version=with_version,
                                                odoo_ver=odoo_ver,
                                                pyver=pyver)
            if pyver and pyver.split('.')[0] == '3' and item in DEPS3:
                for kw1 in ('python', 'bin'):
                    if kw1 not in DEPS3[item]:
                        continue
                    if isinstance(DEPS3[item][kw1], (tuple, list)):
                        for itm in DEPS3[item][kw1]:
                            deps_list = add_package(deps_list, kw1,
                                                    itm,
                                                    with_version=with_version,
                                                    odoo_ver=odoo_ver,
                                                    pyver=pyver)
                    else:
                        deps_list = add_package(deps_list, kw1,
                                                DEPS3[item][kw1],
                                                with_version=with_version,
                                                odoo_ver=odoo_ver,
                                                pyver=pyver)
        elif kw == 'bin':
            if with_version and full_item:
                kw = 'bin2'
                deps_list[kw].append(full_item)
            else:
                kw = 'bin1'
                deps_list[kw].append(item)
    elif kw == 'python' and full_item:
        if item in deps_list['python1']:
            ii = deps_list['python1'].index(item)
            del deps_list['python1'][ii]
            if full_item in DEPS9:
                deps_list['python9'].append(full_item)
            else:
                deps_list['python2'].append(full_item)
        elif not defver and full_item not in deps_list['python2']:
            sys.stderr.write('Version mismatch: package %s\n' % full_item)
    elif kw == 'bin' and full_item:
        if item in deps_list['bin1']:
            ii = deps_list['bin1'].index(item)
            del deps_list['bin1'][ii]
            deps_list['bin2'].append(full_item)
        elif not defver and full_item not in deps_list['bin2']:
            sys.stderr.write('Version mismatch: package %s\n' % full_item)
    return deps_list


def package_from_list(deps_list, kw, PKG_LIST,
                      with_version=None, odoo_ver=None, pyver=None):
    for item in PKG_LIST:
        deps_list = add_package(deps_list, kw, item,
                                with_version=with_version,
                                odoo_ver=odoo_ver,
                                pyver=pyver)
    return deps_list


def package_from_manifest(deps_list, manifest_file,
                          with_version=None, odoo_ver=None, pyver=None):
    if manifest_file:
        try:
            manifest = ast.literal_eval(open(manifest_file, 'rU').read())
        except SyntaxError:
            print("!!Invalid manifest file %s!" % manifest_file)
            manifest = {}
        if manifest.get('external_dependencies'):
            deps = manifest['external_dependencies']
            for kw in ('python', 'bin'):
                if deps.get(kw):
                    for item in deps[kw]:
                        deps_list = add_package(deps_list,
                                                kw,
                                                item,
                                                with_version=with_version,
                                                odoo_ver=odoo_ver,
                                                pyver=pyver)
        if manifest.get('depends'):
            deps = manifest['depends']
            kw = 'modules'
            for item in deps:
                deps_list = add_package(deps_list,
                                        kw,
                                        item,
                                        with_version=with_version,
                                        odoo_ver=odoo_ver,
                                        pyver=pyver)
    return deps_list


def add_manifest(root, manifests, reqfiles, files):
    import_manifest = False
    manifest_imported = False
    for fn in files:
        if fn == '__init__.py':
            import_manifest = True
        if fn == '__openerp__.py':
            if not manifest_imported:
                manifest_imported = os.path.join(root, fn)
        elif fn == '__manifest__.py':
            manifest_imported = os.path.join(root, fn)
        elif fn == 'requirements.txt':
            reqfiles.append(os.path.join(root, fn))
    if import_manifest and manifest_imported:
        manifests.append(manifest_imported)
    return manifests, reqfiles


def swap(deps, itm1, itm2):
    itm1_id = -1
    itm2_id = -1
    for item in deps:
        if item.startswith(itm1):
            itm1_id = deps.index(item)
        elif item.startswith(itm2):
            itm2_id =  deps.index(item)
        if itm1_id >= 0 and itm2_id >= 0:
            break
    if itm1_id < itm2_id:
        item = deps[itm2_id]
        del deps[itm2_id]
        deps.insert(itm1_id, item)


def main():
    parser = z0lib.parseoptargs("List Odoo requirements",
                                "© 2017-2020 by SHS-AV s.r.l.",
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
    parser.add_argument("-O", "--output",
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
    parser.add_argument('-y', '--python-version',
                        action='store',
                        dest='pyver')
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    if ctx['odoo_ver'] and not ctx['pyver']:
        odoo_majver = int(ctx['odoo_ver'].split('.')[0])
        if odoo_majver <= 10:
            ctx['pyver'] = '2.7'
        elif odoo_majver == 11:
            ctx['pyver'] = '3.5'
        elif odoo_majver >= 12:
            ctx['pyver'] = '3.7'
    elif not ctx['odoo_ver'] and ctx['pyver']:
        py_majver = int(ctx['pyver'].split('.')[0])
        if py_majver == 3:
            ctx['odoo_ver'] = '12.0'
        else:
            ctx['odoo_ver'] = '10.0'
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
    if (not ctx['odoo_dir'] and ctx['odoo_ver'] and
            os.path.isdir(os.path.join(os.path.expanduser('~'),
                                       ctx['odoo_ver']))):
        ctx['odoo_dir'] = os.path.join(os.path.expanduser('~'),
                                       ctx['odoo_ver'])
    manifests = []
    reqfiles = []
    if ctx['manifests']:
        for item in ctx['manifests'].split(','):
            if item.endswith('.py'):
                manifests.append(os.path.expanduser(item))
            else:
                reqfiles.append(os.path.expanduser(item))
    elif ctx['odoo_dir']:
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
    deps_list = {}
    for kw in ('python', 'python1', 'python2', 'python9',
               'bin', 'bin1', 'bin2', 'modules'):
        deps_list[kw] = []
    for reqfile in reqfiles:
        requirements = parse_requirements(
            reqfile, odoo_ver=ctx['odoo_ver'], pyver=ctx['pyver'])
        deps_list = package_from_list(deps_list, 'python', requirements,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'],
                                      pyver=ctx['pyver'])
    for manifest_file in manifests:
        deps_list = package_from_manifest(deps_list,
                                          manifest_file,
                                          with_version=ctx['with_version'],
                                          odoo_ver=ctx['odoo_ver'],
                                          pyver=ctx['pyver'])
    if ctx['base_pkgs']:
        deps_list = package_from_list(deps_list, 'python', PIP_BASE_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'],
                                      pyver=ctx['pyver'])
        if ctx['odoo_ver'] in ('11.0', '12.0', '13.0'):
            deps_list = package_from_list(deps_list, 'python',
                                          PIP3_BASE_PACKAGES,
                                          with_version=ctx['with_version'],
                                          odoo_ver=ctx['odoo_ver'],
                                          pyver=ctx['pyver'])
        deps_list = package_from_list(deps_list, 'bin', BIN_BASE_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'],
                                      pyver=ctx['pyver'])
    if ctx['test_pkgs']:
        deps_list = package_from_list(deps_list, 'python', PIP_TEST_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'],
                                      pyver=ctx['pyver'])
        deps_list = package_from_list(deps_list, 'bin', BIN_TEST_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'],
                                      pyver=ctx['pyver'])
    if ctx['rpc_pkgs']:
        deps_list = package_from_list(deps_list, 'python', RPC_PACKAGES,
                                      with_version=ctx['with_version'],
                                      odoo_ver=ctx['odoo_ver'],
                                      pyver=ctx['pyver'])

    deps_list['python'] = sorted(
        sorted(deps_list['python1'], key=lambda s: s.lower()) + deps_list[
            'python2'], key=lambda s: s.lower()) + deps_list['python9']
    for ii, pkg in enumerate(deps_list['python']):
        if pkg.find('>') >= 0 or pkg.find('<') >= 0:
            deps_list['python'][ii] = "'%s'" % pkg
    deps_list['bin'] = sorted(
        sorted(deps_list['bin1'], key=lambda s: s.lower()) + deps_list[
            'bin2'], key=lambda s: s.lower())
    for ii, pkg in enumerate(deps_list['bin']):
        if pkg.find('>') >= 0 or pkg.find('<') >= 0:
            deps_list['bin'][ii] = "'%s'" % pkg
    for item in DEPS:
        if 'python' in DEPS[item]:
            if isinstance(DEPS[item]['python'], (tuple, list)):
                for itm in DEPS[item]['python']:
                    swap(deps_list['python'], item, itm)
            else:
                swap(deps_list['python'], item, DEPS[item]['python'])
    if ctx['pyver'] and ctx['pyver'].split('.')[0] == '2':
        for item in DEPS2:
            if 'python' in DEPS2[item]:
                if isinstance(DEPS2[item]['python'], (tuple, list)):
                    for itm in DEPS2[item]['python']:
                        swap(deps_list['python'], item, itm)
                else:
                    swap(deps_list['python'], item, DEPS2[item]['python'])
    if ctx['pyver'] and ctx['pyver'].split('.')[0] == '3':
        for item in DEPS3:
            if 'python' in DEPS3[item]:
                if isinstance(DEPS3[item]['python'], (tuple, list)):
                    for itm in DEPS3[item]['python']:
                        swap(deps_list['python'], item, itm)
                else:
                    swap(deps_list['python'], item, DEPS3[item]['python'])
    if ctx['out_file']:
        try:
            pkgs = open(ctx['opt_fn'], 'rU').read().split('\n')
        except BaseException:
            pkgs = []
        for pkg in deps_list['python']:
            if pkg not in pkgs:
                if pkg.startswith("'"):
                    naked_pkg = pkg[1: -1]
                    if naked_pkg not in pkgs:
                        pkgs.append(pkg)
                else:
                    pkgs.append(pkg)
        if len(pkgs):
            fd = open(ctx['opt_fn'], 'w')
            fd.write(ctx['sep'].join(sorted(pkgs)))
            fd.close()
        print("Updated %s file" % ctx['opt_fn'])
        print(ctx['sep'].join(pkgs))
    else:
        for kw in ('python', 'bin', 'modules'):
            if kw in deps_list:
                if kw == ctx['itypes'] or (ctx['itypes'] == 'both' and
                                           kw in ('python', 'bin')):
                    if ctx['opt_verbose']:
                        print('%s=%s' % (kw, ctx['sep'].join(deps_list[kw])))
                    else:
                        print(ctx['sep'].join(deps_list[kw]))


if __name__ == "__main__":
    sys.exit(main())
