#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function, unicode_literals
import ast
import os
import re
import sys
from datetime import datetime
from lxml import etree
from os0 import os0
import z0lib
from clodoo import build_odoo_param
# import pdb


__version__ = "0.2.1.67"

GIT_USER = {
    'zero': 'zeroincombenze',
    'oia': 'Odoo-Italia-Associazione',
    'oca': 'OCA',
}
DEFINED_SECTIONS = ['description', 'descrizione', 'features',
                    'oca_diff', 'certifications', 'prerequisites',
                    'installation', 'configuration', 'upgrade',
                    'support', 'usage', 'maintenance',
                    'troubleshooting', 'known_issues',
                    'proposals_for_enhancement', 'history', 'faq',
                    'sponsor', 'copyright_notes', 'avaiable_addons',
                    'contact_us',
]
DEFINED_TAG = ['name', 'summary', 'maturity',
                  'module_name', 'repos_name',
                  'today',
                  'authors', 'contributors', 'acknowledges',
]
DEFINED_TOKENS = DEFINED_TAG + DEFINED_SECTIONS
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
    'late': ['awesome/late.png', False],
    'same': ['awesome/same.png', False],
    'warning': ['awesome/warning.png', False],
    'info': ['awesome/info.png', False],
    'halt': ['awesome/halt.png', False],
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
MANIFEST_ITEMS = ('name', 'summary', 'version',
                  'category','author', 'website',
                  'license', 'depends', 'data',
                  'demo', 'test', 'installable',
                  'external_dependencies', 'maturity', 'description')
RST2HTML = {
    # &': '&amp;',
    '©': '&copy',
    '®': '&reg',
    'à': '&agrave;',
    'á': '&aacute;',
    'è': '&egrave;',
    'é': '&eacute;',
    'ì': '&igrave;',
    'í': '&iacute;',
    'ò': '&ograve;',
    'ó': '&oacute;',
    'ù': '&ugrave;',
    'ú': '&uacute;',
}
RST2HTML_GRYMB = {
    '|check|': '<span class="fa fa-check-square-o" style="color:green"/>',
    '|no_check|': '<span class="fa fa-close" style="color:red"/>',
    '|menu|': '<span class="fa fa-navicon"/>',
    '|right_do|': '<span class="fa fa-caret-right"/>',
    '|exclamation|': '<span class="fa fa-exclamation" style="color:orange"/>',
    '|late|': '<span class="fa fa-calendar-times-o" style="color:red"/>',
    '|same|': '<span class="fa fa-retweet"  style="color:blue"/>',
    '|warning|':
        '<span class="fa fa-exclamation-triangle" style="color:orange"/>',
    '|info|': '<span class="fa fa-info-circle" style="color:blue"/>',
    '|halt|': '<span class="fa fa-minus-circle" style="color:red"/>',
    '|circle|': '<span class="fa fa-circle"/>',
    '|xml_schema|': '<span class="fa fa-file-code-o"/>',
    '|DesktopTelematico|': '<span class="fa fa-wpforms"/>',
    '|FatturaPA|': '<span class="fa fa-euro"/>',
}


def get_template_fn(ctx, template, ignore_ntf=None):
    found = False
    layered_template = '%s_%s' % (ctx['odoo_layer'], template)
    no_body = False
    if template[0:7] in ('header_', 'footer_'):
        no_body = True
    for src_path in ('.',
                     './egg-info',
                     '/opt/odoo/dev/pypi/tools/templates',
                     '/opt/odoo/dev/templates'):
        if src_path.find('/dev/pypi/tools/') >= 0 and not ctx['dbg_template']:
            continue
        if no_body and src_path.find('./egg-info') >= 0:
            continue
        if not no_body:
            full_fn = os.path.join(src_path, layered_template)
            if os.path.isfile(full_fn):
                found = True
                break
        full_fn = os.path.join(src_path, template)
        if os.path.isfile(full_fn):
            found = True
            break
        if template == 'acknowledges.txt':
            full_fn = os.path.join(src_path, 'contributors.txt')
            if os.path.isfile(full_fn):
                found = True
                break
    if no_body:
        if not found:
            full_fn = ''
        return full_fn
    if not found:
        def_template = 'default_' + template
        for src_path in ('.',
                         '/opt/odoo/dev/pypi/tools/templates',
                         '/opt/odoo/dev/templates'):
            if src_path.find('/dev/pypi/tools/') >= 0 and not ctx[
                    'dbg_template']:
                continue
            full_fn = os.path.join(src_path, def_template)
            if os.path.isfile(full_fn):
                found = True
                break
    if not found:
        if ignore_ntf:
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
    fd.write(os0.b(ctx['description']))
    fd.close()


def get_default_avaiable_addons(ctx):
    if 'addons_info' not in ctx:
        return ''
    text = ''
    text += 'Avaiable Addons / Moduli disponibili\n'
    text += '------------------------------------\n'
    text += '\n'
    lol = 0
    for pkg in ctx['addons_info'].keys():
        if len(pkg) > lol:
            lol = len(pkg)
    if lol > 36:
        lol = 36
    fmt = '| %%-%d.%ds | %%-10.10s | %%-10.10s | %%-50.50s |\n' % (lol, lol)
    lne = fmt % ('', '', '', '')
    lne = lne.replace(' ', '-').replace('|', '+')
    text += lne
    text += fmt % ('Name / Nome',
                   'Version',
                   'OCA Ver.',
                   'Description / Descrizione')
    text += lne
    for pkg in  sorted(ctx['addons_info'].keys()):
        if not ctx['addons_info'][pkg].get('oca_installable', True):
            oca_version = '|halt|'
        elif ctx['addons_info'][pkg]['version'] == ctx[
                'addons_info'][pkg]['oca_version']:
            oca_version = '|same|'
        elif ctx['addons_info'][pkg]['oca_version'] == 'N/A':
            oca_version = '|no_check|'
        else:
            oca_version = ctx['addons_info'][pkg]['oca_version']
        if not ctx['addons_info'][pkg].get('installable', True):
            version = '|halt|'
        elif ctx['addons_info'][pkg]['version'] == 'N/A':
            version = '|no_check|'
        else:
            version = ctx['addons_info'][pkg]['version']
        text += fmt % (pkg,
                       version,
                       oca_version,
                       ctx['addons_info'][pkg]['summary'].strip())
        text += lne
    return text


def tohtml(text):
    # pdb.set_trace()
    i = text.find('`')
    j = text.find('`__')
    while i > 0 and j > i:
        t = text[i + 1: j]
        ii = t.find('<')
        jj = t.find('>')
        if ii > 0 and jj > ii:
            url = t[ii + 1: jj]
            if (j + 3) < len(text):
                text = u'%s\aa href="%s"\h%s\a/a\h%s' % (
                    text[0:i],
                    url,
                    t[0: ii - 1].strip(),
                    text[j + 3:]
                )
            else:
                text = u'%s\aa href="%s"\h%s\a/a\h' % (
                    text[0:i],
                    url,
                    t[0: ii - 1].strip()
                )
        else:
            break
        i = text.find('`')
        j = text.find('`__')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('\a', '<').replace('\h', '>')
    lines = text.split('\n')
    while len(lines) > 1 and not lines[-1]:
        del lines[-1]
    while len(lines) and not lines[0]:
        del lines[0]
    if len(lines) > 2:
        if lines[1] and lines[1][0] in ('=', '-'):
            del lines[0]
            del lines[0]
            while not lines[0]:
                del lines[0]
    # is_list = True
    # for line in lines:
    #     if line[0:2] not in ('* ', '..'):
    #         is_list = False
    #         break
    # if is_list:
    #     for i in range(len(lines)):
    #         if lines[i][0:2] != '..':
    #             lines[i] = '<li>%s</li>' % lines[i][2:]
    #     lines.insert(0, '<ul>')
    #     lines.append('</ul>')
    # else:
    hdr_foo = False
    if len(lines) > 1 and lines[0].find('<p>') < 0:
        hdr_foo = True
    is_list = False
    in_list = False
    i = 0
    while i < len(lines):
        if lines[i][0:2] != '..':
            if lines[i][0:2] == '* ' and not in_list:
                in_list = True
            elif lines[i][0:2] != '* ' and in_list:
                in_list = False
        if not in_list and is_list:
            lines.insert(i, '</ul>')
            is_list = in_list
            i += 1
        elif in_list and not is_list:
            lines.insert(i, '<ul>')
            is_list = in_list
            i += 1
        if in_list:
            if lines[i][0:2] != '..':
                lines[i] = '<li>%s</li>' % lines[i][2:]
        else:
            if lines[i] == '':
                lines[i] = '</p><p align="justify">'
                hdr_foo = True
            else:
                for t in RST2HTML_GRYMB.keys():
                    lines[i] = lines[i].replace(t,RST2HTML_GRYMB[t])
        i += 1
    if is_list:
        lines.append('</ul>')
    if hdr_foo:
        lines.insert(0, '<p align="justify">')
        lines.append('</p>')
    return '\n'.join(lines)


def expand_macro(ctx, token, out_fmt=None):
    out_fmt = out_fmt or 'rst'
    if token[0:12] == 'grymb_image_' and \
            token[12:] in DEFINED_GRYMB_SYMBOLS:
        value = 'https://raw.githubusercontent.com/zeroincombenze/grymb' \
                '/master/%s' % DEFINED_GRYMB_SYMBOLS[token[12:]][0]
    elif token[0:10] == 'grymb_url_' and \
            token[10:] in DEFINED_GRYMB_SYMBOLS:
        value = DEFINED_GRYMB_SYMBOLS[token[10:]][1]
    elif token == 'branch':
        value = ctx['odoo_fver']
    elif token == 'prior_branch':
        if ctx['odoo_majver'] > 7:
            value = '%d.0' % (ctx['odoo_majver'] - 1)
        else:
            value = '%d.1' % (ctx['odoo_majver'] - 1)
    elif token == 'icon':
        fmt = 'https://raw.githubusercontent.com/%s/%s/%s/%s/static/'
        if ctx['odoo_majver'] < 8:
            fmt += 'src/img/icon.png'
        else:
            fmt += 'description/icon.png'
        value = fmt % (GIT_USER[ctx['git_orgid']], ctx['repos_name'],
                       ctx['odoo_fver'], ctx['module_name'])
    elif token == 'GIT_URL_ROOT':
        value = 'https://github.com/%s/%s' % (
            GIT_USER[ctx['git_orgid']], ctx['repos_name'])
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
    elif token in ctx:
        value = ctx[token]
    else:
        value = 'Unknown %s' % token
    return value


def expand_macro_in_line(ctx, line, state=None):
    state = state or _init_state()
    out_fmt = state.get('out_fmt', 'rst')
    i = line.find('{{')
    j = line.find('}}')
    while i >=0 and j > i:
        tokens = line[i + 2: j].split(':')
        value = expand_macro(ctx, tokens[0], out_fmt=out_fmt)
        if value is False or value is None:
            print('Invalid macro %s' % token)
            value = ''
        elif len(value.split('\n')) > 1:
            state, value = parse_source(ctx, value, state=state)
        if out_fmt == 'html':
            value = tohtml(value)
        if len(tokens) > 1:
            fmt = tokens[1]
            line = line[0:i] + (fmt % value) + line[j +2:]
        else:
            line = line[0:i] + value + line[j +2:]
        i = line.find('{{')
        j = line.find('}}')
    return line


def _init_state():
    return {'cache': False,
            'prior_line': '',
            'prior_nl': '',
            'action': 'write',
            'stack': [],
            'do_else': [],
            'out_fmt': 'rst',
            'in_fmt': 'rst'}


def value_of_term(ctx, term):
    if term[0] in ('"', "'"):
        return term[1:-1]
    return expand_macro(ctx, term)


def validate_condition(ctx, *args):
    val = ''
    in_cond = False
    i = 0
    while  i < len(args):
        pad = ',' if in_cond else ' '
        if args[i][0].isalpha() or args[i][0] == '_':
            if args[i] == 'defined':
                i += 1
                if args[i] in ctx and ctx[args[1]]:
                    val += '%s%s' % ('True', pad)
                else:
                    val += '%s%s' % ('False', pad)
            elif args[i] == 'isfile':
                i += 1
                val = expand_macro(ctx, args[i])
                if os.path.isfile(val):
                    val += '%s%s' % ('True', pad)
                else:
                    val += '%s%s' % ('False', pad)
            elif args[i] in ctx or args[i] in ('not', 'in'):
                val += '%s%s' % (args[i], pad)
                if args[i] == 'in':
                    in_cond = True
                    val += '('
            else:
                val += '\'%s\'%s' % (expand_macro(ctx, args[i]), pad)
        else:
            val += '%s%s' % (args[i], pad)
        i += 1
    if in_cond:
        val += ')'
    try:
        res = eval(val, ctx)
    except BaseException:
        res = False
    return res
    # left = value_of_term(ctx, args[0])
    # if args[1] == '==':
    #     return left == value_of_term(ctx, args[2])
    # elif args[1] == '!=':
    #     return left != value_of_term(ctx, args[2])
    # elif args[1] == 'in':
    #     res = False
    #     i = 2
    #     while i < len(args):
    #         if left == value_of_term(ctx, args[i]):
    #             res = True
    #             break
    #         i += 1
    #     return res
    # elif args[1] == 'not' and args[2] == 'in':
    #     res = True
    #     i = 3
    #     while i < len(args):
    #         if left == value_of_term(ctx, args[i]):
    #             res = False
    #             break
    #         i += 1
    #     return res
    # return False


def default_token(ctx, token):
    if token in ctx:
        return ctx[token]
    return ''


def is_preproc_line(ctx, line, state):
    is_preproc = False
    if line[0:7] == '.. $if ':
        is_preproc = True
        if state['action'] != 'pass1':
            conditions = line[7:].strip().split(' ')
            res = validate_condition(ctx, *conditions)
            state['stack'].append(res)
            state['do_else'].append(res)
            if False in state['stack']:
                state['action'] = 'susp'
            else:
                state['action'] = 'write'
    elif line[0:9] == '.. $elif ':
        is_preproc = True
        if state['action'] != 'pass1':
            conditions = line[9:].strip().split(' ')
            if len(state['stack']):
                res = validate_condition(ctx, *conditions)
                state['stack'][-1] = res
                if res:
                    state['do_else'][-1] = res
                if False in state['stack']:
                    state['action'] = 'susp'
                else:
                    state['action'] = 'write'
            else:
                state['action'] = 'susp'
    elif line[0:8] == '.. $else':
        is_preproc = True
        if state['action'] != 'pass1':
            if len(state['stack']):
                state['stack'][-1] = not state['do_else'][-1]
                if False in state['stack']:
                    state['action'] = 'susp'
                else:
                    state['action'] = 'write'
            else:
                state['action'] = 'susp'
    elif line[0:6] == '.. $fi':
        is_preproc = True
        if state['action'] != 'pass1':
            if len(state['stack']):
                del state['stack'][-1]
                del state['do_else'][-1]
            if len(state['stack']):
                if False in state['stack']:
                    state['action'] = 'susp'
                else:
                    state['action'] = 'write'
            else:
                state['action'] = 'write'
    elif state['action'] != 'susp':
        if line[0:12] == '.. $include ':
            is_preproc = True
        elif line[0:12] == '.. $block ':
            is_preproc = True
    return state, is_preproc


def parse_acknoledge_list(ctx, source):
    lines = source.split('\n')
    lno = 0
    while lno < len(lines):
        if not lines[lno]:
            del lines[lno]
            continue
        elif lines[lno][0] == '#':
            del lines[lno]
            continue
        names = lines[lno].split(' ')
        if names[0] and names[0][0] == '*':
            ctr = 0
            for i in range(3):
                if ctx['contributors'].find(names[i]) >= 0:
                    ctr += 1
            if ctr >= 2:
                del lines[lno]
                continue
        lno += 1
    return '\n'.join(lines)


def line_of_list(ctx, state, line):
    text = line
    stop = True
    if line:
        if line[0] == '#':
            text = '\t'
        else:
            names = line.split(' ')
            if names[0] and names[0][0] == '*':
                stop = False
                if state['in_fmt'] == 'acknowledges':
                    ctr = 0
                    for i in range(3):
                        if ctx['contributors'].find(names[i]) >= 0:
                            ctr += 1
                    if ctr >= 2:
                        stop = True
                        text = '\t'
    if not stop:
        if state.get('out_fmt', 'rst') == 'html':
            if state['in_fmt'] == 'authors':
                fmt = '* `%s`__'
            else:
                fmt = '* %s'
            if line[0:2] == '* ':
                text = fmt % line[2:]
            else:
                text = fmt % line
        else:
            if state['in_fmt'] == 'authors':
                fmt = '* `%s`__'
            else:
                fmt = '* %s'
            if line[0:2] == '* ':
                text = fmt % line[2:]
            else:
                text = fmt % line
    return text


def append_line(state, line, nl_bef=None):
    nl = '\n' if nl_bef else ''
    if state['in_fmt'] == 'raw':
        text = nl + line
        state['prior_line'] = line
        state['prior_nl'] = nl
    elif state['cache']:
        if len(line) and len(state['prior_line']):
            text = state['prior_nl'] + state['prior_line'][0] * len(line) + nl
        else:
            text = state['prior_nl'] + state['prior_line'] + nl
        state['cache'] = False
        state['prior_line'] = line
        state['prior_nl'] = nl
        text += line
    else:
        text = nl + line
        state['prior_line'] = line
        state['prior_nl'] = nl
    return state, text


def parse_source(ctx, source, state=None):
    state = state or _init_state()
    # if state['action'] == 'pass1':
    #     state['in_fmt'] = 'raw'
    #     # return state, source
    target = ''
    for lno,line in enumerate(source.split('\n')):
        nl_bef = False if lno == 0 else True
        state, is_preproc = is_preproc_line(ctx, line, state)
        if state['action'] != 'susp':
            if is_preproc:
                if line[0:12] == '.. $include ':
                    filename = line[12:].strip()
                    state, text = parse_local_file(ctx,
                                                   filename,
                                                   state=state)
                    state, text = append_line(state, text, nl_bef=nl_bef)
                    target += text + '\n'
                elif line[0:12] == '.. $block ':
                    filename = line[12:].strip()
                    state, text = parse_local_file(ctx,
                                                   filename,
                                                   state=state)
                    state, text = append_line(state, text, nl_bef=nl_bef)
                    target += text
            elif state['in_fmt'] in ('authors', 'contributors', 'acknowledges'):
                text = line_of_list(ctx, state, line)
                if text != '\t':
                    state, text = append_line(state, text, nl_bef=nl_bef)
                    target += text
            elif state['in_fmt'] == 'rst' and (
                    line and ((line == '=' * len(line)) or
                              (line == '-' * len(line)))):
                if not state['prior_line']:
                    state['cache'] = True
                    state['prior_line'] = line
                    state['prior_nl'] = '\n' if nl_bef else ''
                else:
                    if len(state['prior_line']) > 2:
                        line = line[0] * len(state['prior_line'])
                    state['prior_line'] = line
                    state['prior_nl'] = '\n' if nl_bef else ''
                    state, text = append_line(state, line, nl_bef=nl_bef)
                    target += text
            else:
                in_fmt = state['in_fmt']
                if line.find('{{authors}}') >= 0:
                    state['in_fmt'] = 'authors'
                elif line.find('{{contributors}}') >= 0:
                    state['in_fmt'] = 'contributors'
                elif line.find('{{acknowledges}}') >= 0:
                    state['in_fmt'] = 'acknowledges'
                text = expand_macro_in_line(ctx, line, state=state)
                state['in_fmt'] = in_fmt
                state, text = append_line(state, text, nl_bef=nl_bef)
                target += text
    return state, target


def parse_local_file(ctx, filename, ignore_ntf=None, state=None):
    state = state or _init_state()
    full_fn = get_template_fn(ctx, filename, ignore_ntf=ignore_ntf)
    if not full_fn:
        token = filename[0:-4]
        action = 'get_default_%s' % token
        if action in list(globals()):
            return parse_source(ctx,
                                globals()[action](ctx),
                                state=state)
        elif filename[-4:] == '.txt':
            return parse_source(ctx,
                                default_token(ctx, filename[0:-4]),
                                state=state)
        return state, ''
    if ctx['opt_verbose']:
        print("Reading %s" % full_fn)
    fd = open(full_fn, 'rU')
    source = os0.u(fd.read())
    fd.close()
    if len(source) and filename == 'acknowledges.txt':
        source = source.replace('branch', 'prior_branch')
        state, source = parse_source(ctx, source, state=state)
        source = parse_acknoledge_list(ctx, source)
    if len(source):
        full_hfn = get_template_fn(ctx, 'header_' + filename)
        header = ''
        if full_hfn:
            fd = open(full_hfn, 'rU')
            header = os0.u(fd.read())
            fd.close()
        full_ffn = get_template_fn(ctx, 'footer_' + filename)
        footer = ''
        if full_ffn:
            fd = open(full_ffn, 'rU')
            footer = os0.u(fd.read())
            fd.close()
        source = header + source + footer
    return parse_source(ctx, source, state=state)


def parse_file(ctx, filename, ignore_ntf=None, out_fmt=None):
    state = _init_state()
    if out_fmt:
        state['out_fmt'] = out_fmt
    else:
        #  state['action'] = 'pass1'
        state['in_fmt'] = 'raw'
    return parse_local_file(ctx, filename,
                            ignore_ntf=ignore_ntf,
                            state=state)[1]


def read_manifest(ctx):
    if ctx['odoo_layer'] != 'module':
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
        ctx['manifest'] = {
            os0.u(k):os0.u(v) for k,v in ctx['manifest'].items()}
        ctx['manifest_file'] = manifest_file
    else:
        ctx['manifest'] = {}


def adj_version(ctx, version):
    if not version:
        version = '0.0'
    if version[0].isdigit():
        if version.find(ctx['odoo_fver']) != 0:
            version = '%s.%s' % (ctx['odoo_fver'], version)
    return version


def read_all_manifests(ctx):
    def valid_dir(dirname, level):
        if dirname[0:2] == '__':
            return False
        return True

    addons_info = {}
    if ctx['odoo_majver'] >= 10:
        manifest_file = '__manifest__.py'
    else:
        manifest_file = '__openerp__.py'
    # for root, dirs, files in os.walk('.', topdown=True):
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if valid_dir(d, ctx['odoo_layer'])]
        if ctx['odoo_layer'] != 'ocb' or root.find('addons') >= 0:
            module_name = os.path.basename(root)
            if ((ctx['odoo_layer'] == 'ocb' and module_name[0:5] == 'l10n_') or
                    module_name[0:5] == 'test_'):
                continue
            if manifest_file in files:
                full_fn = os.path.join(root,manifest_file)
                print(full_fn)  # debug
                try:
                    addons_info[module_name] = ast.literal_eval(open(
                        full_fn).read())
                    addons_info[module_name] = {
                        os0.u(k):os0.u(v) for k,v in addons_info[
                            module_name].items()}
                    if 'summary' not in addons_info[module_name]:
                        addons_info[module_name]['summary'] = addons_info[
                            module_name]['name'].strip()
                    addons_info[module_name]['version'] = adj_version(
                        ctx, addons_info[module_name].get('version', ''))
                    addons_info[module_name]['oca_version'] = 'N/A'
                    if root.find('__unported__') >= 0:
                        addons_info[module_name]['installable'] = False
                except KeyError:
                    pass
    if ctx['odoo_layer'] == 'ocb':
        oca_root = '/opt/odoo/oca%d' % ctx['odoo_majver']
    else:
        oca_root = '/opt/odoo/oca%d/%s' % (ctx['odoo_majver'],
                                           ctx['repos_name'])
    for root, dirs, files in os.walk(oca_root):
        dirs[:] = [d for d in dirs if valid_dir(d, ctx['odoo_layer'])]
        if ctx['odoo_layer'] != 'ocb' or root.find('addons') >= 0:
            module_name = os.path.basename(root)
            if ((ctx['odoo_layer'] == 'ocb' and module_name[0:5] == 'l10n_') or
                    module_name[0:5] == 'test_'):
                continue
            if manifest_file in files:
                full_fn = os.path.join(root,manifest_file)
                oca_manifest = ast.literal_eval(open(full_fn).read())
                oca_manifest = {
                    os0.u(k):os0.u(v) for k,v in oca_manifest.items()}
                oca_version = adj_version(ctx, oca_manifest.get('version', ''))
                if module_name not in addons_info:
                    addons_info[module_name] = {}
                    if 'summary' in oca_manifest:
                        addons_info[module_name]['summary'] = oca_manifest['summary'].strip()
                    else:
                        addons_info[module_name]['summary'] = oca_manifest['name'].strip()
                    addons_info[module_name]['version'] = 'N/A'
                addons_info[module_name]['oca_version'] = oca_version
                if root.find('__unported__') >= 0:
                    addons_info[module_name]['oca_installable'] = False
                else:
                    addons_info[module_name]['oca_installable'] = oca_manifest.get(
                        'installable', True)
    ctx['addons_info'] = addons_info


def manifest_contents(ctx):
    full_fn = ctx['manifest_file']
    source = ''
    if full_fn:
        fd = open(full_fn, 'rU')
        source = os0.u(fd.read())
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
                text = parse_file(ctx, 'readme_manifest.rst')
                target += "    '%s': r'''%s''',\n" % (item, text)
        elif item in ctx['manifest']:
            if isinstance(ctx['manifest'][item], basestring):
                text = ctx['manifest'][item].replace("'", '"')
                target += "    '%s': '%s',\n" % (item, text)
            else:
                text = str(ctx['manifest'][item])
                target += "    '%s': %s,\n" % (item, text)
    for item in ctx['manifest'].keys():
        if item not in MANIFEST_ITEMS:
            if isinstance(ctx['manifest'][item], basestring):
                text = ctx['manifest'][item].replace("'", '"')
                target += "    '%s': '%s',\n" % (item, text)
            else:
                text = str(ctx['manifest'][item])
                target += "    '%s': %s,\n" % (item, text)
    target += '}\n'
    return target


def xml_replace_text(ctx, root, item, text, pos=None):
    pos = pos or [1, 999]
    ctr = 0
    for element in root.iter():
        if element.tag == item:
            ctr += 1
            if ctr >= pos[0] and ctr <= pos[1]:
                element.text = text


def index_html_content(ctx, source):
    # pdb.set_trace()
    target = ''
    lines = ctx['descrizione'].split('\n')
    if lines[0]:
        title = '%s / %s' % (ctx['name'], lines[0])
    elif len(lines) > 1 and lines[1]:
        title = '%s / %s' % (ctx['name'], lines[1])
    else:
        title = ctx['name']
    for section in source.split('\f'):
        root = etree.XML(section)
        xml_replace_text(ctx, root, 'h2', title)
        target += '\n%s' % etree.tostring(root, pretty_print=True)
    for t in RST2HTML.keys():
        target = target.replace(t,RST2HTML[t])
    return target


def set_default_values(ctx):
    ctx['today'] = datetime.strftime(datetime.today(), '%Y-%m-%d')
    if ctx['write_html']:
        if os.path.isdir('./static/description'):
            ctx['dst_file'] = './static/description/index.html'
        else:
            ctx['dst_file'] = './index.html'
    elif ctx['odoo_layer'] == 'module' and ctx['rewrite_manifest']:
        ctx['dst_file'] = ctx['manifest_file']
    else:
        ctx['dst_file'] = './README.rst'
    if ctx['odoo_layer'] != 'module':
        ctx['manifest'] = {
            'name': 'repos_name',
            'development_status': 'Alfa',
        }
    ctx['maturity'] = ctx['manifest'].get('development_status', 'Alfa')
    ctx['name'] = ctx['manifest'].get('name',
                                      ctx['module_name'].replace('_', ' '))
    ctx['summary'] = ctx['manifest'].get('summary', ctx['name']).strip()
    ctx['zero_tools'] = '`Zeroincombenze Tools <https://github.com/zeroincombenze/tools>`__'
    if ctx['odoo_layer'] == 'ocb':
        ctx['local_path'] = '/opt/odoo/%s' % ctx['odoo_fver']
    elif ctx['odoo_layer'] == 'repository':
        ctx['local_path'] = '/opt/odoo/%s/%s/' % (ctx['odoo_fver'],
                                                  ctx['repos_name'])
    else:
        ctx['local_path'] = '/opt/odoo/%s/%s/' % (ctx['odoo_fver'],
                                                  ctx['repos_name'])


def generate_readme(ctx):
    if ctx['odoo_layer'] == 'ocb':
        ctx['module_name'] = ''
        ctx['repos_name'] = 'OCB'
        read_all_manifests(ctx)
    elif ctx['odoo_layer'] == 'repository':
        ctx['module_name'] = ''
        # ctx['repos_name'] = build_odoo_param('REPOS',
        #                                      odoo_vid=ctx['odoo_fver'])
        ctx['repos_name'] = os.path.basename(os.getcwd())
        read_all_manifests(ctx)
    else:
        if not ctx['module_name']:
            ctx['module_name'] = build_odoo_param('PKGNAME',
                                                  odoo_vid=ctx['odoo_fver'])
        if not ctx['repos_name']:
            ctx['repos_name'] = build_odoo_param('REPOS',
                                                 odoo_vid=ctx['odoo_fver'])
        read_manifest(ctx)
    set_default_values(ctx)
    for section in DEFINED_SECTIONS:
        ctx[section] = parse_file(ctx, '%s.rst' % section, ignore_ntf=True)
    for section in DEFINED_TAG:
        ctx[section] = parse_file(ctx, '%s.txt' % section, ignore_ntf=True)
    if ctx['write_html']:
        if not ctx['template_name']:
            ctx['template_name'] = 'readme_index.html'
        target = index_html_content(ctx,
                                    parse_file(ctx,
                                               ctx['template_name'],
                                               out_fmt='html'))
    else:
        if not ctx['template_name']:
            ctx['template_name'] = 'readme_main_%s.rst' % ctx['odoo_layer']
        target = parse_file(ctx,
                            ctx['template_name'],
                            out_fmt='rst')
    if ctx['rewrite_manifest']:
        target = manifest_contents(ctx)
    tmpfile = '%s.tmp' % ctx['dst_file']
    bakfile = '%s.bak' % ctx['dst_file']
    dst_file = ctx['dst_file']
    fd = open(tmpfile, 'w')
    fd.write(os0.b(target))
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
    parser.add_argument('-H', '--write-index_html',
                        action='store_true',
                        dest='write_html')
    parser.add_argument('-l', '--layer',
                        action='store',
                        help='ocb|module|repository',
                        dest='odoo_layer')
    parser.add_argument('-m', '--module_name',
                        action='store',
                        help='filename',
                        dest='module_name')
    parser.add_argument('-n')
    parser.add_argument('-q')
    parser.add_argument('-R', '--rewrite-manifest',
                        action='store_true',
                        dest='rewrite_manifest')
    parser.add_argument('-r', '--repos_name',
                        action='store',
                        help='dirname',
                        dest='repos_name')
    parser.add_argument('-t', '--template_name',
                        action='store',
                        help='filename',
                        dest='template_name')
    parser.add_argument('-V')
    parser.add_argument('-v')
    ctx = parser.parseoptargs(sys.argv[1:])
    if not ctx['git_orgid']:
        ctx['git_orgid'] = build_odoo_param('GIT_ORGID', odoo_vid=ctx['odoo_vid'])
    if ctx['git_orgid'] not in ('zero', 'oia', 'oca'):
        ctx['git_orgid'] = 'zero'
        print('Invalid git-org: use one of zero|oia|oca for -G switch (%s)' %
              ctx['git_orgid'])
    ctx['odoo_fver'] = build_odoo_param('FULLVER', odoo_vid=ctx['odoo_vid'])
    if ctx['odoo_fver'] not in ('12.0', '11.0', '10.0',
                                '9.0', '8.0', '7.0', '6.1'):
        ctx['odoo_fver'] = '11.0'
        print('Invalid odoo version: please use -b switch (%s)' %
              ctx['odoo_fver'])
    ctx['odoo_majver'] = int(ctx['odoo_fver'].split('.')[0])
    if ctx['odoo_layer'] not in ('ocb', 'module', 'repository'):
        if ctx['odoo_majver'] >= 10 and os.path.isfile('./__manifest__.py'):
            ctx['odoo_layer'] = 'module'
        elif os.path.isfile('./__openerp__.py'):
            ctx['odoo_layer'] = 'module'
        elif os.path.basename(os.getcwd()) == ctx['odoo_fver']:
            ctx['odoo_layer'] = 'ocb'
        else:
            ctx['odoo_layer'] = 'repository'
        print('Invalid layer: use one of ocb|module|repository '
              'for -l switch (%s)' % ctx['odoo_layer'])
    sts = generate_readme(ctx)
    sys.exit(sts)
