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
from clodoo import build_odoo_param
# import pdb


__version__ = "0.2.1.55"

GIT_USER = {
    'zero': 'zeroincombenze',
    'oia': 'Odoo-Italia-Associazione',
    'oca': 'OCA',
}

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
        print("Writingg %s" % full_fn)
    if not os.path.isdir('./egg-info'):
        os.makedirs('./egg-info')
    fd = open(full_fn, 'w')
    fd.write(ctx['description'])
    fd.close()


def get_default_installation(ctx):
    text = """
Installation
============

These instruction are just an example to remember what you have to do.
Installation is based on `Zeroincombenze Tools <https://github.com/zeroincombenze/tools>`__
Deployment is ODOO_DIR/REPOSITORY_DIR/MODULE_DIR where:

| ODOO_DIR is root Odoo directory, i.e. /opt/odoo/{{branch}}
| REPOSITORY_DIR is downloaded git repository directory, currently is: {{repos_name}}
| MODULE_DIR is module directory, currently is: {{module_name}}
| MYDB is the database name
|

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd $HOME
    ./install_tools.sh -p
    export PATH=$HOME/dev:$PATH
    odoo_install_repository {{repos_name}} -b {{branch}} -O {{GIT_ORGID}}


From UI: go to:
.. $versions 11.0 10.0

* Setting > Activate Developer mode 
* Apps > Update Apps List
* Setting > Apps > Select {{module_name}} > Install
.. $versions 9.0 8.0 7.0 6.1

* admin > About > Activate Developer mode
* Setting > Modules > Update Modules List
* Setting > Local Modules > Select {{module_name}} > Install
.. $versions all

Warning: if your Odoo instance crashes, you can do following instruction
to recover installation:

``run_odoo_debug {{branch}} -um {{module_name}} -s -d MYDB``
"""
    return text


def get_default_credits(ctx):
    text = """
Credits
=======

Authors
-------

* `SHS-AV s.r.l. <https://www.zeroincombenze.it/>`__


Contributors
------------

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>


Funders
-------

The development of this module has been financially supported by:

* `SHS-AV s.r.l. <https://www.zeroincombenze.it/>`__


Maintainers
-----------

|Odoo Italia Associazione|

This module is maintained by the Odoo Italia Associazione.

To contribute to this module, please visit https://odoo-italia.org/.
"""
    return text


def get_default_known_issue(ctx):
    return """
|it| Known issues / Roadmap
===========================

Warning: Questo modulo rimpiazza il modulo OCA. Leggete attentamente il
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

**zeroincombenze®** is a trademark of `SHS-AV s.r.l. <http://www.shs-av.com/>`__
which distributes and promotes **Odoo** ready-to-use on own cloud infrastructure.
`Zeroincombenze® distribution of Odoo <http://wiki.zeroincombenze.org/en/Odoo>`__
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
        if token in ('name', 'summary', 'maturity',
                     'description', 'descrizione', 'module_name',
                     'repos_name', 'installation', 'configuration',
                     'usage', 'known_issue', 'bug_tracker',
                     'credits', 'copyright_notes'):
            value = ctx[token]
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
            value = 'http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-%d.svg' % (
                ctx['odoo_majver'])
        elif token == 'badge-doc':
            value = 'http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-%d.svg' % (
                ctx['odoo_majver'])
        elif token == 'badge-help':
            value = 'http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-%s.svg' % (
                ctx['odoo_majver'])
        elif token == 'badge-try_me':
            value = 'http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-%s.svg' % (
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
            value = 'http://wiki.zeroincombenze.org/en/Odoo/%s/dev' % (
                ctx['odoo_fver'])
        elif token == 'help-URL':
            value = 'http://wiki.zeroincombenze.org/it/Odoo/%s/man' % (
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
    if os.path.isfile('./__manifest__.py'):
        manifest_file = './__manifest__.py'
    elif os.path.isfile('./__openerp__.py'):
        manifest_file = './__openerp__.py'
    else:
        manifest_file = ''
        print('Warning: manifest file not found')
    if manifest_file:
        ctx['manifest'] = ast.literal_eval(open(manifest_file).read())
    else:
        ctx['manifest'] = {}


def generate_readme(ctx):
    if not ctx['module_name']:
        ctx['module_name'] = build_odoo_param('PKGNAME',
                                              odoo_vid=ctx['odoo_fver'])
    read_manifest(ctx)
    ctx['repos_name'] = build_odoo_param('REPOS', odoo_vid=ctx['odoo_fver'])
    ctx['dst_file'] = './README.rst'
    ctx['odoo_majver'] = int(ctx['odoo_fver'].split('.')[0])
    ctx['maturity'] = ctx['manifest'].get('development_status', 'Alfa')
    ctx['name'] = ctx['manifest'].get('name',
                                      ctx['module_name'].replace('_', ' '))
    ctx['summary'] = ctx['manifest'].get('summary', ctx['name'])
    for section in ('description', 'descrizione', 'installation',
                    'configuration', 'usage', 'known_issue',
                    'bug_tracker', 'credits', 'copyright_notes'):
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
    parser.add_argument('-V')
    parser.add_argument('-v')
    # parser.add_argument('src_file')
    # parser.add_argument('dst_file',
    #                     nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    if ctx['odoo_level'] not in ('ocb', 'module', 'repository'):
        print('Invalid level: use one of ocb|module|repository for -l switch')
        ctx['odoo_level'] = 'module'
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
