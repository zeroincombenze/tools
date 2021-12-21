#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Documentation generator

This software generates the README.rst of OCB, repository and modules.
It also generates the index.html of the module.

Document may contains macro which format is {{macro_name}}.
Currently, the follow macros are recognized:

acknowledges
authors         Authors list
available_addons
branch          Odoo version for this repository/module
certifications  Certificates list
contact_us
contributors    Contributors list
configuration   How to configure
copyright_notes
description     English description of the repository/module (mandatory)
descrizione     Descrizione modulo/progetto in italiano (obbligatoria)
doc-URL         URL for button documentation
faq             FAG
features        Features of the repository/module
GPL             same of gpl
git_orgid       Git organization
gpl             License name: may be A-GPL or L-GPL
grymb_image_*   Symbol imagae (suffix is a supported symbol name)
help-URL        URL for button help
history         Changelog history
known_issues    Known issues
installation    How to install
name            Module name (must be a python name)
now
maintenance     Maintenance information
maturity
module_name
OCA-URL         URL to the same repository/module of OCA in github.com
oca_diff        OCA comparation
odoo_fver       Odoo full version (deprecated)
odoo_majver     Odoo major version; internal use to set some values
odoo_layer      Document layer, may be: ocb, module or repository
prerequisites   Installation prerequisites
prior_branch    Previous Odoo version of this repository/module
prior2_branch   Previous Odoo version of previous repository/module
proposals_for_enhancement
pypi_modules    pypi module list (may be set in __manifest__.rst)
pypi_sects      pypi section names to import (may be set in __manifest__.rst)
repos_name      Repository/project name
sponsor         Sponsors list
sommario        Traduzione italiana di summary
submodules      Sub module list (only in pypi projects)
summary         Repository/module summary (CR are translated into spaces)
support         Support informations
today
translators     Translators list
troubleshooting Troubleshooting information
try_me-URL      URL for button try-me
upgrade         How to upgrade
usage           How to usage

Documentation may contains some graphical symbols in format |symbol|.
Currently, follows symbols are recognized:

check
DesktopTelematico
en
exclamation
FatturaPA
halt
info
it
late
menu
no_check
right_do
same
warning
xml_schema
"""

from __future__ import print_function, unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
from past.builtins import basestring
import ast
import os
import re
import sys
from datetime import datetime
from shutil import copyfile
from lxml import etree
import license_mgnt
from python_plus import unicodes
from os0 import os0
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
try:
    from clodoo.clodoo import build_odoo_param
except ImportError:
    from clodoo import build_odoo_param

try:
    from python_plus.python_plus import _b
except ImportError:
    from python_plus import _b
# import pdb
standard_library.install_aliases()


__version__ = "1.0.4"

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CLEAR = "\033[0;m"
GIT_USER = {
    'zero': 'zeroincombenze',
    'oca': 'OCA',
    'powerp': 'PowERP-cloud',
    'didotech': 'didotech',
}
DEFINED_SECTIONS = ['description', 'descrizione', 'features',
                    'oca_diff', 'certifications', 'prerequisites',
                    'installation', 'configuration', 'upgrade',
                    'support', 'usage', 'maintenance',
                    'troubleshooting', 'known_issues',
                    'proposals_for_enhancement', 'history', 'faq',
                    'sponsor', 'copyright_notes', 'available_addons',
                    'contact_us']
DEFINED_TAG = ['__init__', '__manifest__',
               'name', 'summary', 'sommario',
               'maturity', 'module_name', 'repos_name',
               'today',
               'authors', 'contributors', 'translators', 'acknowledges',
               'maintainer']
DEFINED_TOKENS = DEFINED_TAG + DEFINED_SECTIONS
ZERO_PYPI_PKGS = 'wok_code'
ZERO_PYPI_SECTS = 'description usage'
LIST_TAG = ('authors',
            'contributors',
            'translators',
            'acknowledges',
            'maintainer')
DEFINED_GRYMB_SYMBOLS = {
    'it': ['flags/it_IT.png',
           'https://www.facebook.com/Zeroincombenze-'
           'Software-gestionale-online-249494305219415/'],
    'en': ['flags/en_US.png',
           'https://www.facebook.com/Zeroincombenze-'
           'Software-gestionale-online-249494305219415/'],
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
                   'https://github.com/zeroincombenze/grymb/'
                   'blob/master/certificates/iso/scope/xml-schema.md'],
    'DesktopTelematico':  [
        'certificates/ade/icons/DesktopTelematico.png',
        'https://github.com/zeroincombenze/grymb/'
        'blob/master/certificates/ade/scope/Desktoptelematico.md'],
    'FatturaPA': ['certificates/ade/icons/fatturapa.png',
                  'https://github.com/zeroincombenze/grymb/'
                  'blob/master/certificates/ade/scope/fatturapa.md'],
}
EXCLUDED_MODULES = ['lxml', ]
MANIFEST_ITEMS = ('name', 'version', 'category',
                  'summary', 'author', 'website',
                  'development_status', 'license', 'depends',
                  'external_dependencies',
                  'data', 'demo', 'test',
                  'maintainer',
                  'installable')
MANIFEST_ITEMS_REQUIRED = ('name', 'version', 'author', 'website',
                           'development_status', 'license')
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

def print_red_message(text):
    print('%s%s%s' % (RED, text, CLEAR))

def print_green_message(text):
    print('%s%s%s' % (GREEN, text, CLEAR))

def get_full_fn(ctx, src_path, filename):
    if src_path.startswith('./'):
        full_fn = os.path.join(ctx['path_name'],
                               src_path[2:].replace('${p}',
                                                    ctx['product_doc']),
                               filename)
    else:
        full_fn = os.path.join(src_path.replace('${p}',
                                                ctx['product_doc']),
                               filename)
    if (os.path.basename(os.path.dirname(full_fn)) == 'docs' and
            not os.path.isdir(os.path.dirname(full_fn))):
        full_fn = os.path.join(os.path.dirname(os.path.dirname(full_fn)),
                               'egg-info',
                               filename)
    return full_fn


def iter_template_path(debug_mode=None, body=None):
    for src_path in ('.',
                     './egg-info',
                     './readme',
                     './docs',
                     '%s/devel/pypi/tools/templates/${p}' % os.environ['HOME'],
                     '%s/devel/venv/bin/templates/${p}' % os.environ['HOME'],
                     '%s/devel/templates/${p}' % os.environ['HOME'],
                     '%s/devel/pypi/tools/templates' % os.environ['HOME'],
                     '%s/devel/venv/bin/templates' % os.environ['HOME'],
                     '%s/devel/templates' % os.environ['HOME']):
        if '/devel/pypi/tools/'in src_path and not debug_mode:
            continue
        elif '/devel/venv/bin/templates' in src_path and debug_mode:
            continue
        elif '/devel/templates' in src_path and debug_mode:
            continue
        if not body and (src_path.find('./docs') >= 0 or
                         src_path.find('./egg-info') >= 0 or
                         src_path.find('./readme') >= 0):
            continue
        yield src_path


def get_template_fn(ctx, template, ignore_ntf=None):

    def alternate_name(full_fn):
        if not full_fn.endswith('.rst'):
            if full_fn.endswith('.txt'):
                full_fn = '%s.rst' % full_fn[0: -4]
            else:
                full_fn = '%s.rst' % full_fn
            if os.path.isfile(full_fn):
                return True, full_fn
        if full_fn.endswith('.rst'):
            full_fn = os.path.join(
                os.path.dirname(full_fn),
                '%s.rst' % os.path.basename(full_fn)[0: -4].upper()
            )
            if os.path.isfile(full_fn):
                return True, full_fn
        return False, full_fn

    def search_tmpl(ctx, template, body):
        found = False
        if body:
            layered_template = '%s_%s' % (ctx['odoo_layer'], template)
            product_template = '%s_%s' % (ctx['product_doc'], template)
        else:
            layered_template = product_template = False
        for src_path in iter_template_path(debug_mode=ctx['dbg_template'],
                                           body=body):
            if body:
                full_fn = get_full_fn(ctx, src_path, product_template)
                if os.path.isfile(full_fn):
                    found = True
                    break
                found, full_fn = alternate_name(full_fn)
                if found:
                    break
                full_fn = get_full_fn(ctx, src_path, layered_template)
                if os.path.isfile(full_fn):
                    found = True
                    break
                found, full_fn = alternate_name(full_fn)
                if found:
                    break
            full_fn = get_full_fn(ctx, src_path, template)
            if os.path.isfile(full_fn):
                found = True
                break
            found, full_fn = alternate_name(full_fn)
            if found:
                break
            if template == 'acknowledges.txt':
                full_fn = get_full_fn(ctx, src_path, 'contributors.txt')
                if os.path.isfile(full_fn):
                    found = True
                    break
        if not body and not found:
            full_fn = ''
        return found, full_fn

    body = True if template[0:7] not in ('header_', 'footer_') else False
    found, full_fn = search_tmpl(ctx, template, body)
    if not found:
        if not body:
            return full_fn
        def_template = 'default_' + template
        found, full_fn = search_tmpl(ctx, def_template, False)
    if not found:
        if ignore_ntf:
            full_fn = ''
        else:
            raise IOError('Template %s not found' % template)
    return full_fn


def clean_summary(summary):
    return ' '.join(x.strip() for x in summary.split('\n'))


def get_default_prerequisites(ctx):
    if 'addons_info' not in ctx:
        return ''
    text = '''.. $if branch in '12.0'
* python 3.7+
* postgresql 9.6+ (experimental 10.0+)
.. $fi
.. $if branch in '11.0'
* python 3.6+
* postgresql 9.2+ (best 9.5)
.. $fi
.. $if branch in '6.1' '7.0' '8.0' '9.0' '10.0'
* python 2.7+ (best 2.7.5+)
* postgresql 9.2+ (best 9.5)
.. $fi
'''
    if os.path.isfile(os.path.join(ctx['path_name'], 'requirements.txt')):
        fd = open(os.path.join(ctx['path_name'], 'requirements.txt'), 'rU')
        for pkg in fd.read().split('\n'):
            if pkg and pkg[0] != '#':
                text += '* %s\n' % pkg.strip()
        fd.close()
    return text


def get_default_available_addons(ctx):
    if 'addons_info' not in ctx:
        return ''
    text = ''
    text += 'Avaiable Addons / Moduli disponibili\n'
    text += '------------------------------------\n'
    text += '\n'
    lol = 0
    for pkg in list(ctx['addons_info'].keys()):
        if len(pkg) > lol:
            lol = len(pkg)
    if lol > 36:
        lol = 36
    no_oca_diff = os0.str2bool(ctx.get('no_section_oca_diff', False), False)
    if no_oca_diff:
        fmt = '| %%-%d.%ds | %%-10.10s | %%-80.80s |\n' % (lol, lol)
        lne = fmt % ('', '', '')
    else:
        fmt = '| %%-%d.%ds | %%-10.10s | %%-10.10s | %%-80.80s |\n' % (lol, lol)
        lne = fmt % ('', '', '', '')
    lne = lne.replace(' ', '-').replace('|', '+')
    text += lne
    if no_oca_diff:
        text += fmt % ('Name / Nome',
                       'Version',
                       'Description / Descrizione')
    else:
        text += fmt % ('Name / Nome',
                       'Version',
                       'OCA Ver.',
                       'Description / Descrizione')
    text += lne
    for pkg in sorted(ctx['addons_info'].keys()):
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
        if no_oca_diff:
            text += fmt % (pkg,
                           version,
                           ctx['addons_info'][pkg]['summary'])
        else:
            text += fmt % (pkg,
                           version,
                           oca_version,
                           ctx['addons_info'][pkg]['summary'])
        text += lne
    return text


def url_by_doc(ctx, url):
    if not url.startswith('http') and not url.startswith('/'):
        if ctx['rewrite_manifest']:
            fmt = '/%s/static/src/img/%s'
            url = fmt % (ctx['module_name'],
                         url)
        else:
            fmt = 'https://raw.githubusercontent.com/%s/%s/%s/%s/static/'
            if ctx['odoo_majver'] < 8:
                fmt += 'src/img/%s'
            else:
                fmt += 'description/%s'
            url = fmt % (GIT_USER[ctx['git_orgid']],
                         ctx['repos_name'],
                         ctx['branch'],
                         ctx['module_name'],
                         url)
    return url


def torst(text, state=None):
    if text:
        text = text.replace('\a', '<').replace('\b', '>')
    return state, text


def totroff(text, state=None):
    return state, text


def tohtml(text, state=None):
    if not text:
        return state, text
    state = state or {}
    state['html_state'] = state.get('html_state', {})
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('\a', '<').replace('\b', '>')
    text = text.replace(' & ', ' &amp; ')

    for token in DEFINED_GRYMB_SYMBOLS:
        tok = '|' + token + '|'
        i = text.find(tok)
        while i >= 0:
            value = '<img src="%s"/>' % expand_macro(ctx,
                                                     'grymb_image_%s' % token)
            text = text[0: i] + value + text[i + len(tok):]
            i = text.find(tok)

    # Parse multi-line rst tags: <`>CODE<`> | <`>LINK<`__>
    i = text.find('`')
    j = text.find('`__')
    k = text.find('`', i + 1)
    while i >= 0 and (j > i or k > i):
        if k > 0 and (k < j or j < 0):
            text = u'%s<code>%s</code>%s' % (
                text[0:i],
                text[i + 1: k],
                text[k + 1:])
        else:
            t = text[i + 1: j]
            ii = t.find('<')
            jj = t.find('>')
            if ii < 0 and jj < 0:
                t = t.replace('&lt;', '<').replace('&gt;', '>')
                ii = t.find('<')
                jj = t.find('>')
            if ii >= 0 and jj > ii:
                url = t[ii + 1: jj]
                if url.startswith('http') and not url.startswith('https'):
                    url.replace('http', 'https')
                if url.startswith('http') and not url.endswith('/'):
                    url += '/'
                if (j + 3) < len(text):
                    text = u'%s<a href="%s">%s</a>%s' % (
                        text[0:i],
                        url,
                        t[0: ii - 1].strip(),
                        text[j + 3:]
                    )
                else:
                    text = u'%s<a href="%s">%s</a>' % (
                        text[0:i],
                        url,
                        t[0: ii - 1].strip()
                    )
            elif j >= 0 and t.find('&lt;') < 0 and t.find('&gt;'):
                text = text[0:i] + text[i + 1:j] + text[j + 3:]
            else:
                break
        i = text.find('`')
        j = text.find('`__')
        k = text.find('`', i + 1)
    # Parse multi-line rst tags: <**>BOLD<**>
    i = text.find('**')
    j = text.find('**', i + 2)
    while i > 0 and j > i:
        text = u'%s<b>%s</b>%s' % (
            text[0:i],
            text[i + 2: j],
            text[j + 2:])
        i = text.find('**')
        j = text.find('**', i + 2)
    # Parse single line rst tags; remove trailing and tailing empty lines
    lines = text.split('\n')
    while len(lines) > 1 and not lines[-1]:
        del lines[-1]
    while len(lines) and not lines[0]:
        del lines[0]
    # is_list = False
    in_list = False
    in_table = False
    open_para = 0
    lineno = 0
    while lineno < len(lines):
        if lines[lineno][0:2] != '..':
            if state['html_state'].get('tag') == 'image':
                x = re.match(r' +:alt:', lines[lineno])
                if x:
                    state['html_state']['alt'] = lines[lineno][x.end():].strip()
                    del lines[lineno]
                    continue
                x = re.match(r' +:target:', lines[lineno])
                if x:
                    state['html_state']['target'] = lines[lineno][x.end():].strip()
                    del lines[lineno]
                    continue
                lines.insert(lineno,
                    '<img src="%s"/>' % state['html_state']['url'])
                for tag in ('tag', 'alt', 'target'):
                    if tag in state['html_state']:
                        del state['html_state'][tag]
            elif (lines[lineno] and lines[lineno][0] == ' ' and
                    state['html_state'].get('tag') == 'code'):
                pass
            elif state['html_state'].get('tag') == 'code':
                lines.insert(lineno, '</code>')
                del state['html_state']['tag']
            elif re.match(r'^ *\+(-+\+)+ *$', lines[lineno]):
                if not in_table:
                    lines[lineno] ='<table style="width:100%; padding:2px; ' \
                                   'border-spacing:2px; text-align:left;"><tr>'
                    in_table = True
                else:
                    lines[lineno] = '</tr><tr>'
            elif in_table and re.match(r' *|.*| *$', lines[lineno]):
                cols = lines[lineno].split('|')
                del cols[0]
                row = ''
                for col in cols:
                    row += '</td><td>' + col.strip()
                row = row[5:-4]
                lines[lineno] = row
            elif in_table:
                lines[lineno - 1] = '%s</tr></table>' % lines[lineno - 1][:-4]
                in_table = False
                continue
            elif lines[lineno][0:2] == '* ':
                if not in_list:
                    lines.insert(lineno, '<ul>')
                    in_list = True
                    lineno += 1
                lines[lineno] = '<li>%s</li>' % lines[lineno][2:]
            elif lines[lineno][0:2] != '* ' and in_list:
                lines.insert(lineno, '</ul>')
                in_list = False
                # continue
            elif lines[lineno] == '':
                if state['html_state'].get('tag') == 'Code':
                    lines[lineno] = '<code>'
                    state['html_state']['tag'] = 'code'
                elif open_para:
                    lines[lineno] = '</p><p align="justify">'
                else:
                    lines[lineno] = '<p align="justify">'
                    open_para += 1
            elif (re.match(r'^=+$', lines[lineno]) and
                    lineno > 0 and
                    len(lines[lineno]) == len(lines[lineno - 1])):
                lines[lineno - 1] = '<h1>%s</h1>' % lines[lineno - 1]
                del lines[lineno]
                continue
            elif (re.match(r'^-+$', lines[lineno]) and
                  lineno > 0 and
                  len(lines[lineno]) == len(lines[lineno - 1])):
                lines[lineno - 1] = '<h2>%s</h2>' % lines[lineno - 1]
                del lines[lineno]
                continue
            elif (re.match(r'^~+$', lines[lineno]) and
                  lineno > 0 and
                  len(lines[lineno]) == len(lines[lineno - 1])):
                lines[lineno - 1] = '<h3>%s</h3>' % lines[lineno - 1]
                del lines[lineno]
                continue
            elif re.match(r'^:: *$', lines[lineno]):
                lines[lineno] = ''
                state['html_state']['tag'] = 'Code'
            elif lines[lineno] == '|':
                lines[lineno] = '<br/>'
            else:
                i = lines[lineno].find('*')
                j = lines[lineno].find('*', i + 1)
                while i > 0 and j > i:
                    lines[lineno] = u'%s<i>%s</i>%s' % (
                        lines[lineno][0:i],
                        lines[lineno][i + 1: j],
                        lines[lineno][j + 1:])
                    i = lines[lineno].find('*')
                    j = lines[lineno].find('*', i + 1)
        else:
            if in_table:
                lines[lineno - 1] = '</tr></table>'
                in_table = False
            elif in_list:
                lines.insert(lineno, '</ul>')
                in_list = False
            elif open_para:
                lines.insert(lineno, '</p>')
                open_para -= 1
            if lines[lineno].startswith('.. image::'):
                state['html_state']['tag'] = 'image'
                state['html_state']['url'] = lines[lineno][10:].strip()
                del lines[lineno]
                continue
        lineno += 1
    if state['html_state'].get('tag') == 'image':
        lines.append('<img src="%s"/>' % state['html_state']['url'])
        del state['html_state']
    elif in_table:
        lines[-1] = '</tr></table>'
        in_table = False
    elif in_list:
        lines.append('</ul>')
        in_list = False
    if open_para:
        lines.append('</p>')
        open_para -= 1
    return state, '\n'.join(lines)


def expand_macro(ctx, token, default=None):
    if token[0:12] == 'grymb_image_' and \
            token[12:] in DEFINED_GRYMB_SYMBOLS:
        value = 'https://raw.githubusercontent.com/zeroincombenze/grymb' \
                '/master/%s' % DEFINED_GRYMB_SYMBOLS[token[12:]][0]
    elif token[0:10] == 'grymb_url_' and \
            token[10:] in DEFINED_GRYMB_SYMBOLS:
        value = DEFINED_GRYMB_SYMBOLS[token[10:]][1]
    elif token == 'module_version':
        value = ctx['manifest'].get('version', '%s.0.1.0' % ctx['branch'])
    elif token == 'icon':
        value = url_by_doc(ctx, 'icon.png')
    elif token == 'GIT_URL_ROOT':
        value = 'https://github.com/%s/%s' % (
            GIT_USER[ctx['git_orgid']], ctx['repos_name'])
    elif token == 'GIT_URL':
        value = 'https://github.com/%s/%s.git' % (
            GIT_USER[ctx['git_orgid']], ctx['repos_name'])
    elif token == 'GIT_ORGID':
        value = ctx['git_orgid']
    elif token == 'badge-maturity':
        if ctx['development_status'].lower() == 'alfa':
            value = 'https://img.shields.io/badge/maturity-Alfa-red.png'
        elif ctx['development_status'].lower() == 'beta':
            value = 'https://img.shields.io/badge/maturity-Beta-yellow.png'
        elif ctx['development_status'].lower() in ('mature',
                                                   'production/stable'):
            value = 'https://img.shields.io/badge/maturity-Mature-green.png'
        else:
            value = 'https://img.shields.io/badge/maturity-Alfa-black.png'
    elif token == 'badge-gpl':
        if ctx['product_doc'] == 'pypi':
            value = 'AGPL'
        else:
            value = build_odoo_param(
                'LICENSE', odoo_vid=ctx['branch'], multi=True)
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
            GIT_USER[ctx['git_orgid']], ctx['repos_name'], ctx['branch'])
    elif token == 'badge-oca-codecov':
        value = 'https://codecov.io/gh/%s/%s/branch/%s/graph/badge.svg' % (
            'OCA', ctx['repos_name'], ctx['branch'])
    elif token == 'badge-doc':
        value = 'https://www.zeroincombenze.it/wp-content/' \
                'uploads/ci-ct/prd/button-docs-%d.svg' % (ctx['odoo_majver'])
    elif token == 'badge-help':
        value = 'https://www.zeroincombenze.it/wp-content/' \
                'uploads/ci-ct/prd/button-help-%s.svg' % (ctx['odoo_majver'])
    elif token == 'badge-try_me':
        value = 'https://www.zeroincombenze.it/wp-content/' \
                'uploads/ci-ct/prd/button-try-it-%s.svg' % (ctx['odoo_majver'])
    elif token == 'maturity-URL':
        value = 'https://odoo-community.org/page/development-status'
    elif token == 'ci-travis-URL':
        value = 'https://travis-ci.com/%s/%s' % (
            GIT_USER[ctx['git_orgid']], ctx['repos_name'])
    elif token == 'coverage-URL':
        value = 'https://coveralls.io/github/%s/%s' % (
            GIT_USER[ctx['git_orgid']], ctx['repos_name'])
    elif token == 'codecov-URL':
        value = 'https://codecov.io/gh/%s/%s/branch/%s' % (
            GIT_USER[ctx['git_orgid']], ctx['repos_name'], ctx['branch'])
    elif token == 'codecov-oca-URL':
        value = 'https://codecov.io/gh/%s/%s/branch/%s' % (
            'OCA', ctx['repos_name'], ctx['branch'])
    elif token == 'OCA-URL':
        value = 'https://github.com/OCA/%s/tree/%s' % (
            ctx['repos_name'], ctx['branch'])
    elif token == 'doc-URL':
        value = 'https://wiki.zeroincombenze.org/en/Odoo/%s/dev' % (
            ctx['branch'])
    elif token == 'help-URL':
        value = 'https://wiki.zeroincombenze.org/it/Odoo/%s/man' % (
            ctx['branch'])
    elif token == 'try_me-URL':
        if ctx['git_orgid'] == 'oca':
            value = 'http://runbot.odoo.com/runbot'
        else:
            value = 'https://erp%s.zeroincombenze.it' % (
                ctx['odoo_majver'])
    elif token in ('gpl', 'GPL'):
        if ctx['product_doc'] == 'pypi':
            value = 'AGPL'
        else:
            value = build_odoo_param(
                'LICENSE', odoo_vid=ctx['branch'], multi=True)
        if token == 'gpl':
            value = value.lower()
    elif token in ctx:
        value = ctx[token]
    elif default is not None:
        value = default
    else:
        value = parse_local_file(
            ctx, '%s.csv' % token,
            ignore_ntf=True,)[1] or parse_local_file(
            ctx, '%s.rst' % token,
            ignore_ntf=True,)[1] or 'Unknown %s' % token
    return value


def expand_macro_in_line(ctx, line, state=None):
    """Exapand content of macro like {{macro}}"""
    state = state or _init_state()
    out_fmt = state.get('out_fmt', 'rst')
    in_fmt = state.get('in_fmt', 'rst')
    srctype = state.get('srctype', '')
    i = line.find('{{')
    j = line.find('}}')
    while 0 <= i < j:
        tokens = line[i + 2: j].split(':')
        value = expand_macro(ctx, tokens[0])
        if value is False or value is None:
            print_red_message('*** Invalid macro %s!' % tokens[0])
            value = ''
        else:
            if tokens[0] in LIST_TAG:
                if len(value.split('\n')) > 1:
                    state['srctype'] = tokens[0]
                else:
                    value = line_of_list(ctx, state, value)
            in_fmt = 'rst'
        if state['in_fmt'] in ('html', 'troff'):
            state, value = parse_source(ctx, value, state=state,
                                        in_fmt=in_fmt, out_fmt=out_fmt)
            if 'srctype' in state:
                del state['srctype']
            return state, line[0:i] + value + line[j + 2:]
        if len(value.split('\n')) > 1:
            line = line[0:i] + value + line[j + 2:]
            state, value = parse_source(ctx, line, state=state,
                                        in_fmt=in_fmt, out_fmt=out_fmt)
            if 'srctype' in state:
                del state['srctype']
            return state, value
        if len(tokens) > 1:
            fmt = tokens[1]
            line = line[0:i] + (fmt % value) + line[j + 2:]
        else:
            line = line[0:i] + value + line[j + 2:]
        i = line.find('{{')
        j = line.find('}}')
    if srctype in LIST_TAG:
        line = line_of_list(ctx, state, line)
    return state, line


def _init_state():
    return {'cache': False,
            'prior_line': '',
            'prior_nl': '',
            'action': 'write',
            'stack': [],
            'do_else': [],
            'out_fmt': 'rst',
            'in_fmt': 'rst'}


def validate_condition(ctx, *args):
    val = ''
    in_cond = False
    i = 0
    while i < len(args):
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
                val += '%s%s' % (os.path.isfile(expand_macro(
                    ctx, args[i], default=args[i])), pad)
            elif args[i] in ctx or args[i] in ('not', 'in'):
                val += '%s%s' % (args[i], pad)
                if args[i] == 'in':
                    in_cond = True
                    val += '('
            else:
                val += '\'%s\'%s' % (expand_macro(ctx, args[i], default=''),
                                     pad)
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
        if line.startswith('.. $include '):
            is_preproc = True
        elif line.startswith('.. $block '):
            is_preproc = True
        elif line.startswith('.. $set '):
            is_preproc = True
        elif line.startswith('.. $merge_docs'):
            is_preproc = True
    return state, is_preproc


def parse_acknowledge_list(ctx, source):
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
                if names[i] in ctx['contributors']:
                    ctr += 1
            if ctr >= 2:
                del lines[lno]
                continue
        lno += 1
    return '\n'.join(lines)


def line_of_list(ctx, state, line):
    """Manage list of people like authors or contributors"""
    text = line.strip()
    stop = True
    if line:
        if line[0] == '#':
            text = ''
        else:
            names = line.split(' ')
            if names[0] and names[0][0] == '*':
                stop = False
                if state.get('srctype') == 'acknowledges':
                    ctr = 0
                    for i in range(3):
                        if ctx['contributors'].find(names[i]) >= 0:
                            ctr += 1
                    if ctr >= 2:
                        stop = True
                        text = ''
    if not stop:
        if state.get('srctype') == 'authors':
            line = line.replace('<', '\a').replace('>', '\b')
            fmt = '* `%s`__'
        else:
            fmt = '* %s'
        if text[0:2] == '* ':
            text = fmt % text[2:]
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


def tail(source, max_ctr=None, max_days=None, module=None):
    target = ''
    max_ctr = max_ctr or 12
    max_days = max_days or 360
    left = ''
    for lno, line in enumerate(source.split('\n')):
        if left:
            line = '%s%s' % (left, line)
            left = ''
        x = re.match(r'^[0-9]+\.[0-9]+\.[0-9]+', line)
        if x:
            max_ctr -= 1
            if max_ctr < 0:
                break
            x = re.search(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', line)
            if x and (datetime.now() -
                      datetime.strptime(line[x.start():x.end()],
                                        '%Y-%m-%d')).days > max_days:
                break
            if module:
                line = '%s: %s' % (module, line)
                left = '~' * (len(module) + 2)
        target += line
        target += '\n'
    return target


def sort_history(source):
    histories = {}
    hash = ''
    histories[hash] = ''
    for lno, line in enumerate(source.split('\n')):
        x = re.match(r'^.*: [0-9]+\.[0-9]+\.[0-9]+', line)
        if x:
            x = re.search(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', line)
            dt = line[x.start():x.end()]
            module = line.split(': ')[0]
            hash = '%s %s' % (dt, module)
            histories[hash] = ''
        histories[hash] += line
        histories[hash] += '\n'
    target = ''
    for item in sorted(histories.keys(), reverse=True):
        target += histories[item]
        target += '\n'
    return target


def parse_source(ctx, source, state=None, in_fmt=None, out_fmt=None):
    state = state or _init_state()
    out_fmt = out_fmt or state.get('out_fmt', 'rst')
    in_fmt = in_fmt or state.get('in_fmt', 'rst')
    target = ''
    for lno, line in enumerate(source.split('\n')):
        nl_bef = False if lno == 0 else True
        state, is_preproc = is_preproc_line(ctx, line, state)
        if state['action'] != 'susp':
            if is_preproc:
                if line.startswith('.. $include '):
                    filename = line[12:].strip()
                    state, text = parse_local_file(ctx,
                                                   filename,
                                                   state=state)
                    state, text = append_line(state, text, nl_bef=nl_bef)
                    target += text + '\n'
                elif line.startswith('.. $block '):
                    filename = line[12:].strip()
                    state, text = parse_local_file(ctx,
                                                   filename,
                                                   state=state)
                    state, text = append_line(state, text, nl_bef=nl_bef)
                    target += text
                elif line.startswith('.. $set '):
                    x = re.match(r'[a-zA-Z_]\w*', line[8:])
                    if x:
                        name = line[8:8 + x.end()]
                        i = 9 + x.end()
                        value = line[i:]
                        ctx[name] = value
                elif line.startswith('.. $merge_docs'):
                    for module in ctx['pypi_modules'].split(' '):
                        # Up to global pypi root
                        module_dir = os.path.abspath(
                            os.path.join(os.getcwd(), '..', '..'))
                        while os.path.isdir(os.path.join(module_dir, module)):
                            # down to module root
                            module_dir = os.path.join(module_dir, module)
                        if os.path.isdir(os.path.join(module_dir, 'docs')):
                            for name in ctx['pypi_sects'].split(' '):
                                name = 'rtd_%s' % name
                                src = os.path.join(
                                    module_dir, 'docs', '%s.rst' % name)
                                if os.path.isfile(src):
                                    tgt = os.path.join(
                                        '.', 'pypi_%s_%s.rst' % (module, name))
                                    copyfile(src, tgt)
                                    target += '\n   pypi_%s_%s' % (module,
                                                                   name)
                            target += '\n'
            elif in_fmt == 'rst' and (
                    line and ((line == '=' * len(line)) or
                              (line == '-' * len(line)) or
                              (line == '~' * len(line)))):
                if not state['prior_line']:
                    # =============
                    # Title level 1
                    # =============
                    state['cache'] = True
                    state['prior_line'] = line
                    state['prior_nl'] = '\n' if nl_bef else ''
                else:
                    # Title
                    # =====
                    if len(state['prior_line']) > 2:
                        line = line[0] * len(state['prior_line'])
                    state['prior_line'] = line
                    state['prior_nl'] = '\n' if nl_bef else ''
                    state, text = append_line(state, line, nl_bef=nl_bef)
                    target += text
            else:
                state, text = expand_macro_in_line(ctx, line, state=state)
                if (not ctx['write_html'] and
                        re.match(r'^\.\. +.*image::', text)):
                    x = re.match(r'^\.\. +.*image::', text)
                    url = url_by_doc(ctx, text[x.end():].strip())
                    text = text[0:x.end() + 1] + url
                state, text = append_line(state, text, nl_bef=nl_bef)
                target += text
    if in_fmt == 'rst' and out_fmt == 'html':
        state, target = tohtml(target, state=state)
    elif in_fmt == 'rst' and out_fmt == 'troff':
        state, target = totroff(target, state=state)
    else:
        state, target = torst(target, state=state)
    return state, target


def parse_local_file(ctx, filename, ignore_ntf=None, state=None,
                     in_fmt=None, out_fmt=None, section=None):
    state = state or _init_state()
    if out_fmt:
        state['out_fmt'] = out_fmt
    elif not state['out_fmt']:
        state['out_fmt'] = 'raw'
    if in_fmt:
        state['in_fmt'] = in_fmt
    elif filename.endswith('.html'):
        state['in_fmt'] = 'html'
    elif filename.endswith('.troff'):
        state['in_fmt'] = 'troff'
    elif not state['in_fmt']:
        state['in_fmt'] = 'raw'
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
    if section:
        ctx['%s_filename'] = full_fn
    full_fn_csv = False
    if full_fn.endswith('.csv'):
        full_fn_csv = full_fn
        full_fn = '%s.rst' % full_fn_csv[: -4]
        os.system('cvt_csv_2_rst -b %s -q %s %s' % (
            ctx['branch'], full_fn_csv, full_fn))
    with open(full_fn, 'rU') as fd:
        source = fd.read().decode('utf-8')
    if full_fn_csv:
        os.unlink(full_fn)
    if len(source) and filename == 'acknowledges.txt':
        state, source1 = parse_source(ctx,
                                      source.replace('branch', 'prior_branch'),
                                      state=state)
        state, source2 = parse_source(ctx,
                                      source.replace('branch', 'prior2_branch'),
                                      state=state)
        source = parse_acknowledge_list(
            ctx, '\n'.join(set(source1.split('\n')) |
                           set(source2.split('\n'))))
    if len(source) and filename == 'history.rst':
        source = tail(source)
        if ctx['odoo_layer'] == 'module':
            ctx['history-summary'] = tail(
                source, max_ctr=1, max_days=15)
    if len(source):
        if ctx['trace_file']:
            mark = '.. !! from "%s"\n\n' % filename
            source = mark + source
        full_hfn = get_template_fn(ctx, 'header_' + filename)
        header = ''
        if full_hfn:
            fd = open(full_hfn, 'rU')
            header = os0.u(fd.read())
            fd.close()
            if len(header) and ctx['trace_file']:
                mark = '.. !! from "%s"\n\n' % full_hfn
                header = mark + header
        full_ffn = get_template_fn(ctx, 'footer_' + filename)
        footer = ''
        if full_ffn:
            fd = open(full_ffn, 'rU')
            footer = os0.u(fd.read())
            fd.close()
            if len(footer) and ctx['trace_file']:
                mark = '.. !! from "%s"\n\n' % full_ffn
                footer = mark + footer
        source = header + source + footer
    return parse_source(ctx, source, state=state)


def read_manifest_file(ctx, manifest_path, force_version=None):
    try:
        manifest = ast.literal_eval(open(manifest_path).read())
    except (ImportError, IOError, SyntaxError):
        raise Exception('Wrong manifest file %s' % manifest_path)
    if force_version:
        manifest['version'] = adj_version(ctx, manifest.get('version', ''))
    return unicodes(manifest)


def fake_setup(**kwargs):
    globals()['setup_args'] = kwargs


def read_history(ctx, full_fn, module=None):
    if module:
        with open(full_fn, 'r') as fd:
            ctx['histories'] += tail(
                os0.u(fd.read()),
                max_days=60,
                module=module)
    with open(full_fn, 'r') as fd:
        ctx['history-summary'] += tail(
            os0.u(fd.read()),
            max_ctr=1,
            max_days=15,
            module=module)


def read_setup(ctx):
    if ctx['product_doc'] == 'pypi':
        MANIFEST_LIST = ('../setup.py', './setup.py')
    else:
        MANIFEST_LIST = ('./setup.py', )
    for manifest in MANIFEST_LIST:
        manifest_filename = os.path.abspath(
            os.path.join(ctx['path_name'], manifest))
        if os.path.isfile(manifest_filename):
            break
        manifest_filename = ''
    if manifest_filename:
        with open(manifest_filename, 'r') as fd:
            content = _b(fd.read().replace('setup(', 'fake_setup(').replace(
                'setup (', 'fake_setup('))
            exec(content)
            ctx['manifest'] = globals()['setup_args']
        ctx['manifest_filename'] = manifest_filename
    else:
        if not ctx['suppress_warning']:
            print_red_message('*** Warning: manifest file not found!')
        ctx['manifest'] = {}
    ctx['history-summary'] = ''
    if ctx['odoo_layer'] == 'repository':
        ctx['histories'] = ''
        for root, dirs, files in os.walk('../'):
            for dir in dirs:
                if dir == 'tools':
                    continue
                full_fn = os.path.join(root, dir, 'egg-info', 'history.rst')
                if os.path.isfile(full_fn):
                    read_history(ctx, full_fn, module=os.path.basename(dir))
        ctx['histories'] = sort_history(ctx['histories'])
        ctx['history-summary'] = sort_history(ctx['history-summary'])
    else:
        full_fn = os.path.join('.', 'egg-info', 'history.rst')
        if os.path.isfile(full_fn):
            with open(full_fn, 'r') as fd:
                read_history(ctx, full_fn)


def read_manifest(ctx):
    if ctx['odoo_layer'] != 'module':
        ctx['manifest'] = {}
        return
    if ctx['odoo_majver'] >= 10:
        MANIFEST_LIST = ('__manifest__.py', '__openerp__.py')
    else:
        MANIFEST_LIST = ('__openerp__.py', )
    for manifest in MANIFEST_LIST:
        manifest_filename = os.path.join(ctx['path_name'], manifest)
        if os.path.isfile(manifest_filename):
            break
        manifest_filename = ''
    if manifest_filename:
        ctx['manifest'] = read_manifest_file(
            ctx, manifest_filename, force_version=True)
        ctx['manifest_filename'] = manifest_filename
    else:
        if not ctx['suppress_warning']:
            print_red_message('*** Warning: manifest file not found!')
        ctx['manifest'] = {}


def adj_version(ctx, version):
    if not version:
        version = '0.1.0'
    if version[0].isdigit():
        if not version.startswith(ctx['branch']):
            version = '%s.%s' % (ctx['branch'], version)
    return version


def read_all_manifests(ctx, path=None, module2search=None):

    def valid_dir(dirname):
        if (dirname.startswith('.') or
                dirname.startswith('__')
                or dirname == 'setup'):
            return False
        return True

    path = path or '.'
    ctx['manifest'] = {}
    ctx['histories'] = ''
    ctx['history-summary'] = ''
    addons_info = {}
    local_modules = 'l10n_%s' % ctx['lang'][0:2]
    if ctx['odoo_majver'] >= 10:
        manifest_file = '__manifest__.py'
    else:
        manifest_file = '__openerp__.py'
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if valid_dir(d)]
        # For OCB read just addons
        if (module2search or
                ctx['odoo_layer'] != 'ocb' or
                root.find('addons') >= 0):
            module_name = os.path.basename(root)
            if module2search and module2search != module_name:
                continue
            # Ignore local modules
            if (not module2search and
                    (module_name.startswith('l10n_') and
                    not module_name.startswith(local_modules)) or
                    module_name.startswith('test_')):
                continue
            if manifest_file in files:
                full_fn = os.path.join(root, manifest_file)
                try:
                    addons_info[module_name] = read_manifest_file(
                        ctx, full_fn, force_version=True)
                    if 'summary' not in addons_info[module_name]:
                        addons_info[module_name]['summary'] = addons_info[
                            module_name]['name'].strip()
                    else:
                        addons_info[module_name][
                            'summary'] = clean_summary(
                                addons_info[module_name]['summary'])
                    addons_info[module_name]['oca_version'] = 'N/A'
                    if root.find('__unported__') >= 0:
                        addons_info[module_name]['installable'] = False
                    if module2search:
                        break
                except KeyError:
                    pass
                full_fn = os.path.join(root, 'egg-info', 'history.rst')
                if os.path.isfile(full_fn):
                    with open(full_fn, 'r') as fd:
                        ctx['histories'] += tail(
                            os0.u(fd.read()),
                            max_days=180, module=module_name)
                        with open(full_fn, 'r') as fd:
                            ctx['history-summary'] += tail(
                                os0.u(fd.read()),
                                max_ctr=1,
                                max_days=15,
                                module=module_name)
    if not module2search:
        if ctx['odoo_layer'] == 'ocb':
            oca_root = '%s/oca%d' %  (os.environ['HOME'], ctx['odoo_majver'])
        else:
            oca_root = '%s/oca%d/%s' % (os.environ['HOME'],
                                        ctx['odoo_majver'],
                                        ctx['repos_name'])
        for root, dirs, files in os.walk(oca_root):
            dirs[:] = [d for d in dirs if valid_dir(d)]
            if ctx['odoo_layer'] != 'ocb' or root.find('addons') >= 0:
                module_name = os.path.basename(root)
                if ((ctx['odoo_layer'] == 'ocb' and module_name[0:5] == 'l10n_') or
                        module_name[0:5] == 'test_'):
                    continue
                if manifest_file in files:
                    full_fn = os.path.join(root, manifest_file)
                    oca_manifest = read_manifest_file(
                        ctx, full_fn, force_version=True)
                    oca_version = oca_manifest['version']
                    if module_name not in addons_info:
                        addons_info[module_name] = {}
                        if 'summary' in oca_manifest:
                            addons_info[module_name][
                                'summary'] = clean_summary(
                                    oca_manifest['summary'])
                        else:
                            addons_info[module_name][
                                'summary'] = oca_manifest['name'].strip()
                        addons_info[module_name]['version'] = 'N/A'
                    addons_info[module_name]['oca_version'] = oca_version
                    if root.find('__unported__') >= 0:
                        addons_info[module_name]['oca_installable'] = False
                    else:
                        addons_info[module_name][
                            'oca_installable'] = oca_manifest.get('installable',
                                                                  True)
        ctx['histories'] = sort_history(ctx['histories'])
        ctx['history-summary'] = sort_history(ctx['history-summary'])
    ctx['addons_info'] = addons_info


def manifest_item(ctx, item):
    if item == 'website':
        if ctx['set_authinfo']:
            text = ctx['license_mgnt'].get_website()
        else:
            text = ctx['manifest'].get(item, ctx['license_mgnt'].get_website())
        target = "    '%s': '%s',\n" % (item, text)
    elif item == 'maintainer':
        if ctx['set_authinfo']:
            text = ctx['license_mgnt'].get_maintainer()
        else:
            text = ctx['manifest'].get(
                item, ctx['license_mgnt'].get_maintainer())
        target = "    '%s': '%s',\n" % (item, text)
    elif item == 'author':
        if ctx['set_authinfo']:
            text = ctx['license_mgnt'].summary_authors()
        else:
            text = ctx['manifest'].get(item,
                                       ctx['license_mgnt'].summary_authors())
        target = "    '%s': '%s',\n" % (item, text)
    elif isinstance(ctx['manifest'][item], basestring):
        while ctx['manifest'][item].startswith('\n'):
            ctx['manifest'][item] = ctx['manifest'][item][1:]
        while ctx['manifest'][item].endswith('\n'):
            ctx['manifest'][item] = ctx['manifest'][item][:-1]
        ctx['manifest'][item] = ctx['manifest'][item].strip()
        if '\n' in ctx['manifest'][item]:
            text = ctx['manifest'][item].replace('"', "'")
            pfx = '    \'%s\': """%s\n'
            lastline = len(text.split('\n')) - 1
            for ii, ln in enumerate(text.split('\n')):
                if pfx:
                    target = pfx % (item, ln)
                    pfx = ''
                elif ii < lastline:
                    target += '%s\n' % ln
                else:
                    target += '%s"""\n' % ln
        else:
            text = ctx['manifest'][item].replace("'", '"')
            target = "    '%s': '%s',\n" % (item, text)
    elif isinstance(ctx['manifest'][item], list):
        if len(ctx['manifest'][item]) == 0:
            target = ''
        elif len(ctx['manifest'][item]) == 1:
            text = str(ctx['manifest'][item])
            target = "    '%s': %s,\n" % (item, text)
        else:
            target = "    '%s': [\n" % item
            for kk in ctx['manifest'][item]:
                if isinstance(kk, basestring):
                    text = kk.replace("'", '"')
                    target += "        '%s',\n" % text
                else:
                    text = str(kk)
                    target += "        %s,\n" % text
            target += "    ],\n"
    else:
        text = str(ctx['manifest'][item])
        target = "    '%s': %s,\n" % (item, text)
    return target

def read_dependecies_license(ctx):
    def_license = 'LGPL-3' if ctx['odoo_majver'] > 8 else 'AGPL-3'
    license = ctx['manifest'].get('license', def_license)
    if license == 'AGPL-3':
        return
    saved_manifest = ctx['manifest'].copy()
    root = build_odoo_param('ROOT', odoo_vid='.', multi=True)
    for module in ctx['manifest'].get('depends', []):
        read_all_manifests(ctx, path=root, module2search=module)
        if module not in ctx['addons_info']:
            if not ctx['suppress_warning']:
                print_red_message(
                    '*** Unknow license of module %s: license may be invalid!' %
                    module
                )
        elif (ctx['addons_info'][module].get('license',
                                           def_license) == 'AGPL-3' and
                not ctx['suppress_warning']):
            print_red_message(
                '*** INVALID LICENSE %s: depending module <%s> is AGPL-3 ***' %
                (license, module)
            )
    ctx['manifest'] = saved_manifest

def manifest_contents(ctx):
    full_fn = ctx['manifest_filename']
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
    if ctx['opt_gpl'] not in ('agpl', 'lgpl', 'opl', 'oee'):
        ctx['opt_gpl'] = ctx['license_mgnt'].get_license(
            odoo_majver=ctx['odoo_majver'])
    AUTHINFO = {
        'license': {
            'agpl': 'AGPL-3',
            'lgpl': 'LGPL-3',
            'opl': 'OPL-1',
            'oee': 'OEE-1',
        }[ctx['opt_gpl']],
        'author': ctx['license_mgnt'].summary_authors(),
        'website': ctx['license_mgnt'].get_website(),
        'maintainer': ctx['license_mgnt'].get_maintainer(),
    }
    for item in MANIFEST_ITEMS:
        if item not in ctx['manifest'] and item in MANIFEST_ITEMS_REQUIRED:
            if item == 'license':
                ctx['manifest'][item] = AUTHINFO[item]
            elif item == 'authors':
                ctx['manifest'][item] = ctx['license_mgnt'].summary_authors()
            elif item in ctx:
                ctx['manifest'][item] = ctx[item]
        elif (item == 'license' and
              ctx['manifest'][item] != AUTHINFO[item] and
              not ctx['suppress_warning']):
            print_red_message(
                '*** Warning: manifest license %s does not match required %s!' %
                (ctx['manifest'][item], AUTHINFO[item])
            )
            print('Update manifest file %s!' % ctx['manifest_filename'])
        elif (item in ('authors', 'website', 'maintainer') and
              ctx['manifest'].get(item) and
              ctx['manifest'][item] != AUTHINFO[item] and
              not ctx['suppress_warning']):
            print_red_message(
                '*** Warning: manifest %s %s does not match required %s!' %
                (item, ctx['manifest'][item], AUTHINFO[item])
            )
            print('Use -W switch to force required value!')
        if item in ctx['manifest'] or (ctx['set_authinfo'] and
                                       item in MANIFEST_ITEMS_REQUIRED):
            target += manifest_item(ctx, item)
    for item in list(ctx['manifest'].keys()):
        if item != 'description' and item not in MANIFEST_ITEMS:
            target += manifest_item(ctx, item)
    if ctx['odoo_majver'] < 8:
        text = parse_local_file(ctx, 'readme_manifest.rst')[1]
        target += "    'description': r'''%s''',\n" % text
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
    target = ''
    title = '%s / %s' % (ctx['summary'], ctx['sommario'])
    for section in source.split('\f'):
        try:
            root = etree.XML(section)
        except SyntaxError as e:
            print_red_message('***** Error %s *****' % e)
            root = e
        xml_replace_text(ctx, root, 'h2', title)
        try:
            target += '\n%s' % etree.tostring(root, pretty_print=True)
        except SyntaxError as e:
            print_red_message('***** Error %s *****' % e)
            target += section
    for t in list(RST2HTML.keys()):
        target = target.replace(t, RST2HTML[t])
    return target


def set_default_values(ctx):
    ctx['today'] = datetime.strftime(datetime.today(), '%Y-%m-%d')
    ctx['now'] = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
    if ctx['product_doc'] == 'pypi' and (not ctx['branch'] or
                                         ctx['branch'] == '.'):
        ctx['branch'] = '.'.join(ctx['manifest'].get(
            'version', '').split('.')[0:2])
    if ctx['manifest'].get('version', ''):
        if not ctx.get('odoo_fver'):
            ctx['odoo_fver'] = ctx['manifest']['version']
    # TODO: to remove early
    if not ctx.get('odoo_fver'):
        ctx['odoo_fver'] = ctx['branch']
    if ctx['product_doc'] == 'odoo':
        ctx['odoo_majver'] = int(ctx['odoo_fver'].split('.')[0])
        if not ctx.get('prior_branch'):
            pmv = ctx['odoo_majver'] - 1
            if pmv == 6:
                ctx['prior_branch'] = '%d.1' % pmv
            elif pmv > 6:
                ctx['prior_branch'] = '%d.0' % pmv
            if not ctx.get('prior2_branch'):
                pmv = ctx['odoo_majver'] - 2
                if pmv == 6:
                    ctx['prior2_branch'] = '%d.1' % pmv
                elif pmv > 6:
                    ctx['prior2_branch'] = '%d.0' % pmv
    else:
        releases = [int(x) for x in ctx['branch'].split('.')]
        if not ctx.get('prior_branch'):
            ctx['odoo_majver'] = releases[0]
            pmv = ctx['odoo_majver'] - 1
            ctx['prior_branch'] = '%d.%d' % (pmv, releases[1])
    if ctx['output_file']:
        ctx['dst_file'] = ctx['output_file']
    elif ctx['write_html']:
        if os.path.isdir('./static/description'):
            ctx['dst_file'] = './static/description/index.html'
        else:
            ctx['dst_file'] = './index.html'
        ctx['trace_file'] = False
    elif ctx['odoo_layer'] == 'module' and ctx['rewrite_manifest']:
        ctx['dst_file'] = ctx['manifest_filename']
    elif ctx['odoo_layer'] == 'module' and ctx['write_man_page']:
        ctx['dst_file'] = 'page.man'
    else:
        ctx['dst_file'] = './README.rst'
    if ctx['odoo_layer'] != 'module':
        ctx['manifest'] = {
            'name': 'repos_name',
            'development_status': 'Alfa',
        }
    if ctx['product_doc'] == 'odoo':
        ctx['development_status'] = ctx['manifest'].get(
            'development_status',
            ctx.get('force_maturity', 'Alpha')) or 'Alpha'
    else:
        ctx['development_status'] = 'Alfa'
        for item in ctx['manifest'].get('classifiers', []):
            if item.startswith('Development Status'):
                ctx['development_status'] = item.split('-')[1].strip()
                break
    ctx['name'] = ctx['manifest'].get('name',
                                      ctx['module_name'].replace('_', ' '))
    ctx['summary'] = ctx['manifest'].get(
        'summary', ctx['name']).strip().replace('\n', ' ')
    ctx['zero_tools'] = '`Zeroincombenze Tools ' \
                        '<https://zeroincombenze-tools.readthedocs.io/>`__'
    if ctx['odoo_layer'] == 'ocb':
        ctx['local_path'] = '%s/%s' % (os.environ['HOME'], ctx['branch'])
    elif ctx['odoo_layer'] == 'repository':
        ctx['local_path'] = '%s/%s/%s/' % (os.environ['HOME'],
                                           ctx['branch'],
                                           ctx['repos_name'])
    else:
        ctx['local_path'] = '%s/%s/%s/' % (os.environ['HOME'],
                                           ctx['branch'],
                                           ctx['repos_name'])


def read_purge_readme(ctx, source):
    if source is None:
        return '', '', ''
    lines = source.split('\n')
    out_sections = {
        'description': '',
        'authors': '',
        'contributors': '',
    }
    cur_sect = 'description'
    ix = 0
    while ix < len(lines):
        if not ix:
            line = lines[ix].strip()
        else:
            line = lines[ix]
            ln = line.lower()
            if line.startswith('Authors'):
                if (lines[ix + 1].startswith('~~~~~~~') or
                        lines[ix + 1].startswith('-------')):
                    cur_sect = 'authors'
                    ix += 2
                    continue
            elif line.startswith('Contributors'):
                if (lines[ix + 1].startswith('~~~~~~~~~~~~') or
                        lines[ix + 1].startswith('------------')):
                    cur_sect = 'contributors'
                    ix += 2
                    continue
            else:
                for token in ('usage', 'getting started', 'installation',
                              'upgrade', 'support', 'history', 'credits',
                              'maintainer', 'maintenance', 'configuration',
                              'troubleshooting', 'known_issues', 'faq',
                              'sponsor', 'copyright',
                              'translators', 'acknowledges'):
                    if ln.startswith(token):
                        cur_sect = ''
                        break
        if cur_sect:
            out_sections[cur_sect] += '%s\n' % line
        ix += 1
    for sect in ('description', 'authors', 'contributors'):
        while out_sections[sect].startswith('\n'):
            out_sections[sect] = out_sections[sect][1:]
        while out_sections[sect].endswith('\n\n'):
            out_sections[sect] = out_sections[sect][: -1]
    return (out_sections['description'],
            out_sections['authors'],
            out_sections['contributors'])


def merge_lists(left, right):
    left = left.split('\n')
    right = right.split('\n')
    for item in right:
        if item not in left:
            left.append(item)
    return '\n'.join(left)


def purge_list(source):
    source = source.replace(
        '\n\n', '\n').replace(
        '`__', '').replace(
        '`', '').replace(
        '--\n', '--\n\n')
    lines = source.split('\n')
    target = []
    for line in lines:
        if not line or line not in target:
            target.append(line)
    source = '\n'.join(target)
    while (source != '\n' and source.startswith('\n') and
           source[1] in ('*', '-', '#', '.')):
        source = source[1:]
    if source and not source.endswith('\n'):
        source = source + '\n'
    return source


def write_egg_info(ctx):

    def write_file(path, section):
        force_write = False
        if (section == 'history' and
                ctx['odoo_layer'] in ('repository', 'ocb') and
                ctx['histories']):
            ctx[section] = ctx['histories']
            force_write = True
        if (force_write or
                not os.path.isfile(os.path.join(path, '%s.rst' % section))):
            with open(os.path.join(path, '%s.rst' % section), 'w') as fd:
                if section == 'history' and not ctx[section]:
                    header = '%s (%s)' % (
                        ctx['manifest'].get('version', ''),
                        ctx['today'])
                    dash = '~' * len(header)
                    line = '* [IMP] Created documentation directory'
                    ctx[section] = '%s\n%s\n\n%s\n' % (header, dash, line)
                if path == './readme' and section == 'CONTRIBUTORS':
                    fd.write(ctx['authors'])
                fd.write(ctx[section.lower()])

    if os.path.isdir('./egg-info'):
        for section in ('authors', 'contributors',
                        'description', 'descrizione', 'history'):
            write_file('./egg-info', section)
    elif os.path.isdir('./readme'):
        for section in ('CONTRIBUTORS', 'DESCRIPTION'):
            write_file('./readme', section)


def generate_readme(ctx):

    def validate_authors_contributors(ctx):
        contributors = ''
        for line in ctx['contributors'].split('\n'):
            if not line:
                continue
            (org_id, name, website,
             email, years) = ctx['license_mgnt'].extract_info_from_line(line)
            if website and not email:
                ctx['authors'] = '%s\n%s\n' % (ctx['authors'], line)
                continue
            contributors += line + '\n'
        for section in LIST_TAG:
            if section == 'contributors':
                ctx[section] = purge_list(contributors)
            else:
                ctx[section] = purge_list(ctx[section])
        return ctx

    def set_sommario(ctx):
        if not ctx['sommario']:
            lines = ctx['descrizione'].split('\n')
            if lines[0]:
                ctx['sommario'] = lines[0]
            elif len(lines) > 1 and lines[1]:
                ctx['sommario'] = lines[1]
            else:
                ctx['sommario'] = ctx['name']
        return ctx

    def set_values_of_manifest(ctx):
        if not ctx.get('pypi_modules'):
            ctx['pypi_modules'] = '%s' % ZERO_PYPI_PKGS
        if not ctx.get('pypi_sects'):
            ctx['pypi_sects'] = '%s' % ZERO_PYPI_SECTS
        return ctx

    def read_manifest_setup(ctx):
        if ctx['product_doc'] == 'pypi':
            if ctx['odoo_layer'] == 'repository':
                ctx['module_name'] = ''
            else:
                ctx['module_name'] = os.path.basename(ctx['path_name'])
            ctx['repos_name'] = 'tools'
            read_setup(ctx)
        elif ctx['odoo_layer'] == 'ocb':
            ctx['module_name'] = ''
            ctx['repos_name'] = 'OCB'
            read_all_manifests(ctx)
        elif ctx['odoo_layer'] == 'repository':
            ctx['module_name'] = ''
            ctx['repos_name'] = os.path.basename(ctx['path_name'])
            read_all_manifests(ctx)
        else:
            if not ctx['module_name']:
                ctx['module_name'] = build_odoo_param(
                    'PKGNAME', odoo_vid='.', multi=True)
                if not ctx['module_name']:
                    ctx['module_name'] = build_odoo_param(
                        'PKGNAME', odoo_vid=ctx['branch'], multi=True)
            if not ctx['repos_name']:
                ctx['repos_name'] = build_odoo_param(
                    'REPOS', odoo_vid='.', multi=True)
                if not ctx['repos_name']:
                    ctx['repos_name'] = build_odoo_param(
                        'REPOS', odoo_vid=ctx['branch'], multi=True)
            read_manifest(ctx)
        return ctx

    for section in ('histories', 'history-summary',
                    'rdme_description', 'rdme_authors', 'rdme_contributors'):
        ctx[section] = ''
    # Read predefined section / tags
    if ctx['odoo_layer'] == 'module':
        for fn in ('./README.md', './README.rst'):
            if not os.path.isfile(fn):
                continue
            with open(fn, 'rbU') as fd:
                (ctx['rdme_description'],
                 ctx['rdme_authors'],
                 ctx['rdme_contributors']) = read_purge_readme(
                    ctx, os0.u(fd.read()))
            break

    ctx = read_manifest_setup(ctx)
    set_default_values(ctx)
    ctx['license_mgnt'] = license_mgnt.License()
    ctx['license_mgnt'].add_copyright(ctx['git_orgid'], '', '', '', '')
    for section in DEFINED_TAG:
        out_fmt = None
        ctx[section] = parse_local_file(ctx, '%s.txt' % section,
                                        ignore_ntf=True,
                                        out_fmt=out_fmt,
                                        section=section)[1]
    for section in DEFINED_SECTIONS:
        out_fmt = None
        ctx[section] = parse_local_file(ctx, '%s.rst' % section,
                                        ignore_ntf=True,
                                        out_fmt=out_fmt,
                                        section=section)[1]
        if section in ZERO_PYPI_SECTS and ctx.get('submodules'):
            for sub in ctx.get('submodules').split(' '):
                ctx[section] += '\n\n'
                ctx[section] += parse_local_file(
                    ctx, '%s_%s.rst' % (section, sub),
                    ignore_ntf=True,
                    out_fmt=out_fmt,
                    section='%s_%s' % (section, sub))[1]
    if ctx['odoo_layer']:
        if not ctx['configuration']:
            ctx['configuration'] = parse_local_file(
                ctx, 'CONFIGURE.rst',
                ignore_ntf=True,
                out_fmt=None,
                section='configuration')[1]
        if not ctx['description'] or ctx['description'] == 'N/A':
            ctx['description'] = ctx['rdme_description']
        ctx['authors'] = merge_lists(ctx['rdme_authors'], ctx['authors'])
        ctx['contributors'] = merge_lists(ctx['rdme_contributors'],
                                          ctx['contributors'])

    ctx = validate_authors_contributors(ctx)
    ctx = set_sommario(ctx)
    ctx = set_values_of_manifest(ctx)
    if ctx['module_name']:
        read_dependecies_license(ctx)
    if ctx['set_authinfo']:
        write_egg_info(ctx)
    if ctx['write_html']:
        if not ctx['template_name']:
            ctx['template_name'] = 'readme_index.html'
        target = index_html_content(ctx,
                                    parse_local_file(ctx,
                                                     ctx['template_name'],
                                                     out_fmt='html')[1])
    else:
        if not ctx['template_name']:
            ctx['template_name'] = 'readme_main_%s.rst' % ctx['odoo_layer']
        target = parse_local_file(ctx,
                                  ctx['template_name'],
                                  out_fmt='rst')[1]
    if ctx['rewrite_manifest'] and ctx['odoo_layer'] == 'module':
        target = manifest_contents(ctx)
    tmpfile = '%s.tmp' % ctx['dst_file']
    bakfile = '%s.bak' % ctx['dst_file']
    dst_file = ctx['dst_file']
    if ctx['opt_verbose']:
        print("Writing %s" % dst_file)
    with open(tmpfile, 'w') as fd:
        fd.write(os0.b(target))
    if os.path.isfile(bakfile):
        os.remove(bakfile)
    if os.path.isfile(dst_file):
        os.rename(dst_file, bakfile)
    os.rename(tmpfile, dst_file)
    if (ctx['rewrite_manifest'] and
            ctx['odoo_layer'] == 'module' and
            not ctx['suppress_warning']):
        print(
            '\n\nYou should update license info of the files.\n'
            'Please, type\n'
            '> topep8 -h\n'
            'for furthermore information\n'
        )
    if ctx['opt_verbose']:
        if ctx['history-summary']:
            print('\nRecent History\n~~~~~~~~~~~~~~\n')
            print_green_message(ctx['history-summary'])
        else:
            if ctx['odoo_layer'] == 'module' and ctx['module_name']:
                item = ctx['module_name']
            else:
                item = 'code'
            print_red_message('Missed documentation for last %s updates!!!' %
                              item)


if __name__ == "__main__":
    parser = z0lib.parseoptargs("Generate README",
                                "© 2018-2021 by SHS-AV s.r.l.",
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
    parser.add_argument('-g', '--gpl-info',
                        action='store',
                        dest='opt_gpl',
                        default='')
    parser.add_argument('-H', '--write-index_html',
                        action='store_true',
                        dest='write_html')
    parser.add_argument('-l', '--layer',
                        action='store',
                        help='ocb|module|repository',
                        dest='odoo_layer')
    parser.add_argument('-L', '--lang',
                        action='store',
                        help='iso code',
                        dest='lang',
                        default='it_IT')
    parser.add_argument('-m', '--module-name',
                        action='store',
                        help='filename',
                        dest='module_name')
    parser.add_argument('-M', '--force-maturity',
                        action='store',
                        help='Alfa,Beta,Mature,Production/stable',
                        dest='force_maturity')
    parser.add_argument('-n')
    parser.add_argument('-o', '--output-file',
                        action='store',
                        help='filename',
                        dest='output_file')
    parser.add_argument('-P', '--product-doc',
                        action='store',
                        help='may be odoo or pypi',
                        dest='product_doc',
                        default='')
    parser.add_argument('-p', '--path-name',
                        action='store',
                        help='pathname',
                        dest='path_name',
                        default='.')
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
    parser.add_argument('-T', '--trace-file',
                        action='store_true',
                        dest='trace_file')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('-W', '--write-authinfo',
                        action='store_true',
                        dest='set_authinfo')
    parser.add_argument('-w', '--suppress-warning',
                        action='store_true',
                        dest='suppress_warning')
    parser.add_argument('-Y', '--write-man-page',
                        action='store_true',
                        dest='write_man_page')
    ctx = unicodes(parser.parseoptargs(sys.argv[1:]))
    ctx['path_name'] = os.path.abspath(ctx['path_name'])
    if not ctx['product_doc']:
        if '/pypi/' in ctx['path_name'] or ctx['path_name'].endswith('/tools'):
            ctx['product_doc'] = 'pypi'
        else:
            ctx['product_doc'] = 'odoo'
    if ctx['product_doc'] == 'pypi':
        ctx['git_orgid'] = 'zero'
        ctx['branch'] = ctx['odoo_vid'] if ctx['odoo_vid'] != '.' else ''
        ctx['odoo_majver'] = 0
    else:
        ctx['branch'] = build_odoo_param('FULLVER',
            odoo_vid=ctx['odoo_vid'], multi=True)
        if ctx['branch'] not in ('14.0', '13.0', '12.0', '11.0', '10.0',
                                 '9.0', '8.0', '7.0', '6.1'):
            ctx['branch'] = '12.0'
            if not ctx['suppress_warning']:
                print_red_message(
                    '*** Invalid odoo version: please use -b switch (%s)' %
                    ctx['branch'])
        ctx['odoo_majver'] = int(ctx['branch'].split('.')[0])
        if not ctx['git_orgid']:
            ctx['git_orgid'] = build_odoo_param(
                'GIT_ORGID', odoo_vid=ctx['odoo_vid'], multi=True)
    if ctx['git_orgid'] not in ('zero', 'oca', 'powerp', 'didotech'):
        ctx['git_orgid'] = 'zero'
        if not ctx['suppress_warning'] and ctx['product_doc'] != 'pypi':
            print_red_message(
                '*** Invalid git-org: use -G %s or of zero|oca|didotech' %
                ctx['git_orgid'])
    if ctx['odoo_layer'] not in ('ocb', 'module', 'repository'):
        if ctx['product_doc'] == 'odoo':
            if (ctx['odoo_majver'] >= 10 and
                    os.path.isfile(os.path.join(ctx['path_name'],
                                                '__manifest__.py')) and
                    os.path.isfile(os.path.join(ctx['path_name'],
                                                '__init__.py'))):
                ctx['odoo_layer'] = 'module'
            elif (ctx['odoo_majver'] < 10 and
                    os.path.isfile(os.path.join(ctx['path_name'],
                                                '__openerp__.py')) and
                    os.path.isfile(os.path.join(ctx['path_name'],
                                                '__init__.py'))):
                ctx['odoo_layer'] = 'module'
            elif (ctx['odoo_majver'] >= 10 and
                    os.path.isdir(os.path.join(ctx['path_name'],
                        'odoo')) and
                    os.path.isfile(os.path.join(ctx['path_name'],
                        'odoo-bin'))):
                ctx['odoo_layer'] = 'ocb'
            elif (ctx['odoo_majver'] < 10 and
                  os.path.isdir(os.path.join(ctx['path_name'],
                                             'openerp')) and
                  (os.path.isfile(os.path.join(ctx['path_name'],
                                               'openerp-server'))) or
                  os.path.isfile(os.path.join(ctx['path_name'],
                                              'server', 'openerp-server'))):
                ctx['odoo_layer'] = 'ocb'
            else:
                ctx['odoo_layer'] = 'repository'
        else:
            if os.path.isfile(os.path.join(ctx['path_name'],
                                           '../setup.py')):
                ctx['odoo_layer'] = 'module'
            else:
                ctx['odoo_layer'] = 'repository'
    sts = generate_readme(ctx)
    sys.exit(sts)