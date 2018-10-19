#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function
import ast
import os
import re
import sys
from datetime import datetime
import z0lib
from clodoo import build_odoo_param
# import pdb


__version__ = "0.2.1.56"

GIT_USER = {
    'zero': 'zeroincombenze',
    'oia': 'Odoo-Italia-Associazione',
    'oca': 'OCA',
}
DEFINED_SECTIONS = ['description', 'descrizione', 'installation',
                    'configuration', 'usage', 'known_issue',
                    'bug_tracker', 'credits', 'copyright_notes',
                    'features', 'certifications', 'history',
                    'OCA_diff',
]
DEFINED_TOKENS = ['name', 'summary', 'maturity',
                  'module_name', 'repos_name',
                  'today' ] + DEFINED_SECTIONS
DEFINED_GRYMB_SYMBOLS = {
    'it': ['flags/it_IT.png',
           'https://www.facebook.com/groups/openerp.italia/'],
    'en': ['flags/en_US.png',
           'https://www.facebook.com/groups/openerp.italia/'],
    'check': ['awesome/check.png', False],
    'no_check': ['awesome/no_check.png', False],
    'menu': ['awesome/menu.png', False],
    'right_do': ['awesome/right_do.png', False],
    'exclamation': ['awesome/exclamation.png', False],
    'warning': ['awesome/warning.png', False],
    'xml_schema': ['certificates/iso/icons/xml-schema.png',
                   'https://raw.githubusercontent.com/zeroincombenze/grymb' \
                   'certificates/iso/scope/xml-schema.md'],
    'DesktopTelematico':  ['certificates/ade/icons/DesktopTelematico.png',
                   'https://raw.githubusercontent.com/zeroincombenze/grymb' \
                   'certificates/ade/scope/DesktopTelematico.md'],
    'FatturaPA': ['certificates/ade/icons/fatturapa.png',
                   'https://raw.githubusercontent.com/zeroincombenze/grymb' \
                   'certificates/ade/scope/fatturapa.md'],
}
EXCLUDED_MODULES = ['lxml', ]
MANIFEST_ITEMS = ('name', 'version', 'category',
                  'author', 'website', 'summary',
                  'license', 'depends', 'data',
                  'demo', 'test', 'installable',
                  'maturity', 'description')


def get_template_path(ctx, template, ignore=None):
    for src_path in ('.',
                     './egg-info',
                     '/opt/odoo/dev/pypi/tools/templates',
                     '/opt/odoo/dev/templates'):
        if src_path.find('/dev/tools/') >= 0 and not ctx['dbg_template']:
            continue
        full_fn = os.path.join(src_path, template)
        if os.path.isfile(full_fn):
            break
    if not os.path.isfile(full_fn):
        if ignore:
            full_fn = ''
        else:
            raise IOError('Template %s not found' % template)
    return full_fn


def generate_description_file(ctx):
    full_fn = './egg-info/description.rst'
    if ctx['opt_verbose']:
        print("Writing %s" % full_fn)
    if not os.path.isdir('./egg-info'):
        os.makedirs('./egg-info')
    fd = open(full_fn, 'w')
    fd.write(ctx['description'])
    fd.close()


def get_default_installation(ctx):
    statements = '::\n'
    tool = '`Zeroincombenze Tools <https://github.com/zeroincombenze/tools>`__'
    full_fn = '../requirements.txt'
    if os.path.isfile(full_fn):
        fd = open(full_fn, 'rU')
        source = fd.read()
        fd.close()
        for module in source.split('\n'):
            if module and module[0] != '#' and module not in EXCLUDED_MODULES:
                statements += '\n    pip install %s' % module
    if ctx['odoo_level'] == 'ocb':
        text = """
Installation / Installazione
============================

+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| These instruction are just an   | Istruzioni di esempio valide solo per    |
| example to remember what        | distribuzioni Linux CentOS 7, Ubuntu 14+ |
| you have to do on Linux.        | e Debian 8+                              |
|                                 |                                          |
| Installation is based on:       | L'installazione è basata su:             |
+---------------------------------+------------------------------------------+
| %s         |
+---------------------------------+------------------------------------------+
| Suggested deployment is         | Posizione suggerita per l'installazione: |
+---------------------------------+------------------------------------------+
| **/opt/odoo/{{branch}}**                                                          |
+----------------------------------------------------------------------------+

|

%s
    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    export PATH=$HOME/dev:$PATH
    odoo_install_repository {{repos_name}} -b {{branch}} -O {{GIT_ORGID}}
    for pkg in os0 z0lib; do
        pip install $pkg -U
    done
    sudo manage_odoo requirements -b {{branch}} -vsy -o /opt/odoo/{{branch}}
"""
        return text % (tool, statements)

    text = """
Installation / Installazione
============================

+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| These instruction are just an   | Istruzioni di esempio valide solo per    |
| example to remember what        | distribuzioni Linux CentOS 7, Ubuntu 14+ |
| you have to do on Linux.        | e Debian 8+                              |
|                                 |                                          |
| Installation is based on:       | L'installazione è basata su:             |
+---------------------------------+------------------------------------------+
| %s         |
+---------------------------------+------------------------------------------+
| Suggested deployment is         | Posizione suggerita per l'installazione: |
+---------------------------------+------------------------------------------+
| /opt/odoo/{{branch}}/{{repos_name}}/{{module_name}}                               |
+----------------------------------------------------------------------------+

|

%s
    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    export PATH=$HOME/dev:$PATH
    odoo_install_repository {{repos_name}} -b {{branch}} -O {{GIT_ORGID}}


From UI: go to:
.. $versions 11.0 10.0

|menu| Setting > Activate Developer mode 

|menu| Apps > Update Apps List

|menu| Setting > Apps |right_do| Select **{{module_name}}** > Install
.. $versions 9.0

|menu| admin > About > Activate Developer mode

|menu| Setting > Modules > Update Modules List

|menu| Setting > Local Modules |right_do| Select **{{module_name}}** > Install
.. $versions 8.0 7.0 6.1

|menu| Setting > Modules > Update Modules List

|menu| Setting > Local Modules |right_do| Select **{{module_name}}** > Install
.. $versions all

|warning| If your Odoo instance crashes, you can do following instruction
to recover installation status:

``run_odoo_debug {{branch}} -um {{module_name}} -s -d MYDB``
"""
    return text % (tool, statements)


def get_default_credits(ctx):
    authors = ''
    full_fn = './egg-info/authors.txt'
    if os.path.isfile(full_fn):
        fd = open(full_fn, 'rU')
        source = fd.read()
        fd.close()
        for line in source.split('\n'):
            if line and line[0] != '#' and line not in EXCLUDED_MODULES:
                if line[0:2] == '* ':
                    line = line[2:]
                authors += '\n* `%s`__' % line
    else:
        authors = '* `SHS-AV s.r.l. <https://www.zeroincombenze.it/>`__'
    contributors = ''
    full_fn = './egg-info/contributors.txt'
    if os.path.isfile(full_fn):
        fd = open(full_fn, 'rU')
        source = fd.read()
        fd.close()
        for line in source.split('\n'):
            if line and line[0] != '#' and line not in EXCLUDED_MODULES:
                if line[0:2] != '* ':
                    contributors += '\n* %s' % line
                else:
                    contributors += '\n%s' % line
    else:
        contributors = '* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>'
    text = """
Credits
=======

Authors
-------

%s

Contributors
------------

%s

Maintainers
-----------

|Odoo Italia Associazione|

This module is maintained by the Odoo Italia Associazione.

To contribute to this module, please visit https://odoo-italia.org/.
"""
    return text % (authors, contributors)


def get_default_known_issue(ctx):
    return """
Known issues / Roadmap
======================

|warning| Questo modulo rimpiazza il modulo OCA. Leggete attentamente il
paragrafo relativo alle funzionalità e differenze.

"""

def get_default_bug_tracker(ctx):
    return """
Issue Tracker
=============

Bug reports are welcome! You can use the issue tracker to report bugs,
and/or submit pull requests on `GitHub Issues
<https://github.com/%s/%s/issues>`_.

In case of trouble, please check there if your issue has already been reported.


Proposals for enhancement
-------------------------

If you have a proposal to change this module, you may want to send an email to
<moderatore@odoo-italia.org> for initial feedback.
An Enhancement Proposal may be submitted if your idea gains ground.
""" % (GIT_USER[ctx['git_orgid']], ctx['repos_name'])


def get_default_copyright_notes(ctx):
    if ctx['git_orgid'] == 'oia':
        text = """
----------------

**Odoo** is a trademark of `Odoo S.A. <https://www.odoo.com/>`__
(formerly OpenERP)

**OCA**, or the `Odoo Community Association <http://odoo-community.org/>`__,
is a nonprofit organization whose mission is to support
the collaborative development of Odoo features and promote its widespread use.

**Odoo Italia Associazione**, or the `Associazione Odoo Italia <https://www.odoo-italia.org/>`__
is the nonprofit Italian Community Association whose mission
is to support the collaborative development of Odoo designed for Italian law and markeplace.
Since 2017 Odoo Italia Associazione issues modules for Italian localization not developed by OCA
or available only with Odoo Proprietary License.
Odoo Italia Associazione distributes code under `AGPL <https://www.gnu.org/licenses/agpl-3.0.html>`__
or `LGPL <https://www.gnu.org/licenses/lgpl.html>`__ free license.

`Odoo Italia Associazione <https://www.odoo-italia.org/>`__ è un'Associazione senza fine di lucro
che dal 2017 rilascia moduli per la localizzazione italiana non sviluppati da OCA
o disponibili solo con `Odoo Proprietary License <https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html>`__

Odoo Italia Associazione distribuisce il codice esclusivamente con licenza `AGPL <https://www.gnu.org/licenses/agpl-3.0.html>`__
o `LGPL <https://www.gnu.org/licenses/lgpl.html>`__
"""
    else:
        text = """
----------------

**Odoo** is a trademark of `Odoo S.A. <https://www.odoo.com/>`__
(formerly OpenERP)

**OCA**, or the `Odoo Community Association <http://odoo-community.org/>`__,
is a nonprofit organization whose mission is to support
the collaborative development of Odoo features and promote its widespread use.

**zeroincombenze®** is a trademark of `SHS-AV s.r.l. <https://www.shs-av.com/>`__
which distributes and promotes **Odoo** ready-to-use on own cloud infrastructure.
`Zeroincombenze® distribution of Odoo <https://wiki.zeroincombenze.org/en/Odoo>`__
is mainly designed for Italian law and markeplace.

Users can download from `Zeroincombenze® distribution <https://github.com/zeroincombenze/OCB>`__
and deploy on local server.
"""
    return text


def replace_macro(ctx, line):
    i = line.find('{{')
    j = line.find('}}')
    while i >=0 and j > i:
        token = line[i + 2: j]
        if token in DEFINED_TOKENS:
            value = ctx[token]
        elif token[0:12] == 'grymb_image_' and \
                token[12:] in DEFINED_GRYMB_SYMBOLS:
            value = 'https://raw.githubusercontent.com/zeroincombenze/grymb' \
                    '/master/%s' % DEFINED_GRYMB_SYMBOLS[token[12:]][0]
        elif token[0:10] == 'grymb_url_' and \
                token[10:] in DEFINED_GRYMB_SYMBOLS:
            value = DEFINED_GRYMB_SYMBOLS[token[10:]][1]
        elif token == 'branch':
            value = ctx['odoo_fver']
        elif token == 'icon':
            fmt = 'https://raw.githubusercontent.com/%s/%s/%s/%s/static/'
            if ctx['odoo_majver'] < 8:
                fmt += 'src/img/icon.png'
            else:
                fmt += 'description/icon.png'
            value = fmt % (GIT_USER[ctx['git_orgid']], ctx['repos_name'],
                           ctx['odoo_fver'], ctx['module_name'])
        elif token == 'GIT_URL':
            value = 'https://github.com/%s/%s.git' % (
                GIT_USER[ctx['git_orgid']], ctx['repos_name'])
        elif token == 'GIT_ORGID':
            value = ctx['git_orgid']
        elif token == 'badge-maturity':
            if ctx['maturity'].lower() == 'alfa':
                value = 'https://img.shields.io/badge/maturity-Alfa-red.png'
            elif ctx['maturity'].lower() == 'beta':
                value = 'https://img.shields.io/badge/maturity-Beta-yellow.png'
            else:
                value = 'https://img.shields.io/badge/maturity-Alfa-black.png'
        elif token == 'badge-gpl':
            value = build_odoo_param('LICENSE', odoo_vid=ctx['odoo_fver'])
            if value == 'AGPL':
                value = 'licence-%s--3-blue.svg' % value
            else:
                value = 'licence-%s--3-7379c3.svg' % value
        elif token == 'badge-status':
            value = 'https://travis-ci.org/%s/%s.svg' % (
                GIT_USER[ctx['git_orgid']], ctx['repos_name'])
        elif token == 'badge-coverage':
            value = 'https://coveralls.io/repos/github/%s/%s/badge.svg' % (
                GIT_USER[ctx['git_orgid']], ctx['repos_name'])
        elif token == 'badge-codecov':
            value = 'https://codecov.io/gh/%s/%s/branch/%s/graph/badge.svg' % (
                GIT_USER[ctx['git_orgid']], ctx['repos_name'], ctx['odoo_fver'])
        elif token == 'badge-OCA':
            value = 'https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-%d.svg' % (
                ctx['odoo_majver'])
        elif token == 'badge-doc':
            value = 'https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-%d.svg' % (
                ctx['odoo_majver'])
        elif token == 'badge-help':
            value = 'https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-%s.svg' % (
                ctx['odoo_majver'])
        elif token == 'badge-try_me':
            value = 'https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-%s.svg' % (
                ctx['odoo_majver'])
        elif token == 'maturity-URL':
            value = 'https://odoo-community.org/page/development-status'
        elif token == 'ci-travis-URL':
            value = 'https://travis-ci.org/%s/%s' % (
                GIT_USER[ctx['git_orgid']], ctx['repos_name'])
        elif token == 'coverage-URL':
            value = 'https://coveralls.io/github/%s/%s' % (
                GIT_USER[ctx['git_orgid']], ctx['repos_name'])
        elif token == 'codecov-URL':
            value = 'https://codecov.io/gh/%s/%s/branch/%s' % (
                GIT_USER[ctx['git_orgid']], ctx['repos_name'], ctx['odoo_fver'])
        elif token == 'OCA-URL':
            value = 'https://github.com/OCA/%s/tree/%s' % (
                ctx['repos_name'], ctx['odoo_fver'])
        elif token == 'doc-URL':
            value = 'https://wiki.zeroincombenze.org/en/Odoo/%s/dev' % (
                ctx['odoo_fver'])
        elif token == 'help-URL':
            value = 'https://wiki.zeroincombenze.org/it/Odoo/%s/man' % (
                ctx['odoo_fver'])
        elif token == 'try_me-URL':
            if ctx['git_orgid'] == 'oca':
                value = 'http://runbot.odoo.com/runbot'
            elif ctx['git_orgid'] == 'oia':
                value = 'https://odoo%s.odoo-italia.org' % (
                    ctx['odoo_majver'])
            else:
                value = 'https://erp%s.zeroincombenze.it' % (
                    ctx['odoo_majver'])
        elif token in ('gpl', 'GPL'):
            value = build_odoo_param('LICENSE', odoo_vid=ctx['odoo_fver'])
            if token == 'gpl':
                value = value.lower()
        else:
            value = token
        if value is False or value is None:
            print('Invalid macro %s' % token)
            value = ''
        line = line[0:i] + value + line[j +2:]
        i = line.find('{{')
        j = line.find('}}')
    return line


def parse_source(ctx, filename, ignore=None):
    def append_line(state, line, no_nl=None):
        nl = '' if no_nl else '\n'
        if state['cache']:
            text = state['cache'][0] * len(line) + '\n'
            state['cache'] = ''
            state['prior_line'] = line
            text += line + nl
        else:
            text = line + nl
            state['prior_line'] = line
        return state, text

    def parse_local_source(ctx, source, state=None):
        target = ''
        state = state or {'cache': '',
                          'prior_line': '',
                          'action': 'write'}
        for line in source.split('\n'):
            if line[0:13] == '.. $versions ':
                enable_versions = line[13:].strip()
                if enable_versions == 'all':
                    state['action'] = 'write'
                elif enable_versions.find(ctx['odoo_fver']) >= 0:
                    state['action'] = 'write'
                else:
                    state['action'] = 'susp'
            elif state['action'] != 'susp':
                if line[0:12] == '.. $include ':
                    filename = line[12:].strip()
                    state, text = parse_local_file(ctx,
                                                   filename,
                                                   state=state)
                    state, text = append_line(state, text, no_nl=True)
                    target += text
                elif line[0:12] == '.. $block ':
                    filename = line[12:].strip()
                    state, text = parse_local_file(ctx,
                                                   filename,
                                                   state=state)
                    state, text = append_line(state, text, no_nl=True)
                    target += text
                elif line and ((line == '=' * len(line)) or (
                        line == '-' * len(line))):
                    if not state['prior_line']:
                        state['cache'] = line
                    else:
                        if len(state['prior_line']) > 2:
                            line = line[0] * len(state['prior_line'])
                        state['prior_line'] = line
                        state, text = append_line(state, line)
                        target += text
                else:
                    text = replace_macro(ctx, line)
                    texts = text.split('\n')
                    if len(texts) > 1:
                        for text in texts:
                            state, text = parse_local_source(ctx, text,
                                                             state=state)
                            state, text = append_line(state, text, no_nl=True)
                            target += text
                    else:
                        state, text = append_line(state, text)
                    target += text
        return state, target

    def parse_local_file(ctx, filename, ignore=None, state=None):
        state = state or {'cache': '',
                          'prior_line': '',
                          'action': 'write'}
        full_fn = get_template_path(ctx, filename, ignore=ignore)
        if not full_fn:
            return state, ''
        if ctx['opt_verbose']:
            print("Reading %s" % full_fn)
        fd = open(full_fn, 'rU')
        source = fd.read()
        fd.close()
        return parse_local_source(ctx, source, state=None)

    return parse_local_file(ctx, filename, ignore=ignore)[1]


def read_manifest(ctx):
    if ctx['odoo_level'] != 'module':
        ctx['manifest'] = {}
        return
    if ctx['odoo_majver'] >= 10:
        if os.path.isfile('./__manifest__.py'):
            manifest_file = './__manifest__.py'
        elif os.path.isfile('./__openerp__.py'):
            manifest_file = './__openerp__.py'
        else:
            manifest_file = ''
            print('Warning: manifest file not found')
    else:
        if os.path.isfile('./__openerp__.py'):
            manifest_file = './__openerp__.py'
        else:
            manifest_file = ''
            print('Warning: manifest file not found')
    if manifest_file:
        ctx['manifest'] = ast.literal_eval(open(manifest_file).read())
        ctx['manifest_file'] = manifest_file
    else:
        ctx['manifest'] = {}


def manifest_contents(ctx):
    full_fn = ctx['manifest_file']
    source = ''
    if full_fn:
        fd = open(full_fn, 'rU')
        source = fd.read()
        fd.close()
    target = ''
    for line in source.split('\n'):
        if not line or line[0] != '#':
            break
        target += line + '\n'
    target += '{\n'
    for item in MANIFEST_ITEMS:
        if item == 'description':
            if ctx['odoo_majver'] < 8:
                text = parse_source(ctx, 'readme_manifest.rst')
                target += "    '%s': '''%s''',\n" % (item, text)
        elif item in ctx['manifest']:
            if isinstance(ctx['manifest'][item], basestring):
                text = ctx['manifest'][item].replace("'", '"')
                target += "    '%s': '%s',\n" % (item, text)
            else:
                text = str(ctx['manifest'][item])
                target += "    '%s': %s,\n" % (item, text)
    for item in ctx['manifest'].keys():
        if item not in ctx['manifest']:
            if isinstance(ctx['manifest'][item], basestring):
                text = ctx['manifest'][item].replace("'", '"')
                target += "    '%s': '%s',\n" % (item, text)
            else:
                text = str(ctx['manifest'][item])
                target += "    '%s': %s,\n" % (item, text)
    target += '}\n'
    return target


def generate_readme(ctx):
    # pdb.set_trace()
    if not ctx['module_name']:
        ctx['module_name'] = build_odoo_param('PKGNAME',
                                              odoo_vid=ctx['odoo_fver'])
    if ctx['odoo_level'] == 'ocb':
        ctx['repos_name'] = 'OCB'
    else:
        ctx['repos_name'] = build_odoo_param('REPOS',
                                             odoo_vid=ctx['odoo_fver'])
    ctx['dst_file'] = './README.rst'
    ctx['today'] = datetime.strftime(datetime.today(), '%Y-%m-%d')
    ctx['odoo_majver'] = int(ctx['odoo_fver'].split('.')[0])
    read_manifest(ctx)
    ctx['maturity'] = ctx['manifest'].get('development_status', 'Alfa')
    ctx['name'] = ctx['manifest'].get('name',
                                      ctx['module_name'].replace('_', ' '))
    ctx['summary'] = ctx['manifest'].get('summary', ctx['name'])
    for section in DEFINED_SECTIONS:
        ctx[section] = parse_source(ctx, '%s.rst' % section, ignore=True)
    if not ctx['description']:
        ctx['description'] = ctx['manifest'].get('description', '')
        generate_description_file(ctx)
    if not ctx['installation']:
        ctx['installation'] = get_default_installation(ctx)
    if not ctx['known_issue']:
        ctx['known_issue'] = get_default_known_issue(ctx)
    if not ctx['bug_tracker']:
        ctx['bug_tracker'] = get_default_bug_tracker(ctx)
    if not ctx['credits']:
        ctx['credits'] = get_default_credits(ctx)
    if not ctx['copyright_notes']:
        ctx['copyright_notes'] = get_default_copyright_notes(ctx)
    target = parse_source(ctx, 'readme_main_%s.rst' % ctx['odoo_level'])
    if ctx['rewrite_manifest']:
        target = manifest_contents(ctx)
        tmpfile = '%s.tmp' % ctx['manifest_file']
        bakfile = '%s.bak' % ctx['manifest_file']
        dst_file = ctx['manifest_file']
    else:
        tmpfile = '%s.tmp' % ctx['dst_file']
        bakfile = '%s.bak' % ctx['dst_file']
        dst_file = ctx['dst_file']
    fd = open(tmpfile, 'w')
    fd.write(target)
    fd.close()
    if os.path.isfile(bakfile):
        os.remove(bakfile)
    if os.path.isfile(dst_file):
        os.rename(dst_file, bakfile)
    os.rename(tmpfile, dst_file)


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Generate README",
                          "© 2018 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-b', '--odoo-branch',
                        action='store',
                        default='.',
                        dest='odoo_vid')
    parser.add_argument('-B', '--debug-template',
                        action='store_true',
                        dest='dbg_template')
    parser.add_argument('-G', '--git-org',
                        action='store',
                        dest='git_orgid')
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
    parser.add_argument('-R', '--rewrite-manifest',
                        action='store_true',
                        dest='rewrite_manifest')
    parser.add_argument('-V')
    parser.add_argument('-v')
    # parser.add_argument('src_file')
    # parser.add_argument('dst_file',
    #                     nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    if ctx['odoo_level'] not in ('ocb', 'module', 'repository'):
        print('Invalid level: use one of ocb|module|repository for -l switch')
        ctx['odoo_level'] = 'module'
    if not ctx['git_orgid']:
        ctx['git_orgid'] = build_odoo_param('GIT_ORGID', odoo_vid=ctx['odoo_vid'])
    if ctx['git_orgid'] not in ('zero', 'oia', 'oca'):
        print('Invalid git-org: use one of zero|oia|oca for -G switch')
        ctx['git_orgid'] = 'zero'
    ctx['odoo_fver'] = build_odoo_param('FULLVER', odoo_vid=ctx['odoo_vid'])
    if ctx['odoo_fver'] not in ('12.0', '11.0', '10.0',
                                '9.0', '8.0', '7.0', '6.1'):
        print('Invalid odoo version: please use -b switch')
        ctx['odoo_fver'] = '11.0'
    sts = generate_readme(ctx)
    sys.exit(sts)
