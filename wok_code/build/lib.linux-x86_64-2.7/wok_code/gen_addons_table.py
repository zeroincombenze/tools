#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
This script replaces markers in the README.md files of an Odoo repository
with the list of addons present in the repository. It preserves the marker
so it can be run again.
The script must be run from the root of the repository,
where the README.md file can be found.
Based on OCA code it is changed for Odoo Italia Associazione.
Cmdline parameters:
    gen_addons_table.py [{addons|}] [OCA_original_dir]
Markers in README.md must have the form:
[//]: # (addons)
Insert list of modules with version and description; if path supplied, insert
OCA version of module
[//]: # (end addons)
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from past.builtins import cmp
from future import standard_library
# from builtins import *                                             # noqa: F403
import ast
import os
import re
import sys
standard_library.install_aliases()                                 # noqa: E402


MARKERS = r'(\[//\]: # \(addons\))|(\[//\]: # \(end addons\))'
MANIFESTS = ('__openerp__.py', '__manifest__.py')
__version__ = "1.0.4"


class UserError(Exception):
    def __init__(self, msg):
        self.msg = msg


def extract_des(description):
    description_en = ''
    description_it = ''
    return description_en, description_it


def sanitize_cell(s):
    if not s:
        return ''
    s = ' '.join(s.split())
    return s


def render_markdown_table(header, rows):
    table = []
    rows = [header, ['---'] * len(header)] + rows
    for row in rows:
        table.append(' | '.join(row))
    return '\n'.join(table)


def print_addons(header, rows_available, rows_unported):
    addons = []
    if rows_available:
        addons.extend([
            '\n',
            '\n',
            'Available addons\n',
            '----------------\n',
            render_markdown_table(header, rows_available),
            '\n'
        ])
    if rows_unported:
        addons.extend([
            '\n',
            '\n',
            'Unported addons\n',
            '---------------\n',
            render_markdown_table(header, rows_unported),
            '\n'
        ])
    addons.append('\n')
    for line in addons:
        sys.stdout.write(line)


def replace_in_readme(readme_path, header, rows_available, rows_unported):
    readme = open(readme_path).read()
    parts = re.split(MARKERS, readme, flags=re.MULTILINE)
    if len(parts) != 7:
        raise UserError('Addons markers not found or incorrect in %s' %
                        readme_path)
    addons = []
    if rows_available:
        addons.extend([
            '\n',
            '\n',
            'Available addons\n',
            '----------------\n',
            render_markdown_table(header, rows_available),
            '\n'
        ])
    if rows_unported:
        addons.extend([
            '\n',
            '\n',
            'Unported addons\n',
            '---------------\n',
            render_markdown_table(header, rows_unported),
            '\n'
        ])
    addons.append('\n')
    parts[2:5] = addons
    parts = [p.encode('utf-8') if isinstance(p, str) else p for p in parts]
    readme = ''.join(parts)
    open(readme_path, 'w').write(readme)


def get_values_from_manifest(addon_path, manifest_path, element):
    manifest = ast.literal_eval(open(manifest_path).read())
    addon_name = os.path.basename(addon_path)
    link = '[%s](%s/)' % (addon_name, addon_path)
    version = manifest.get('version') or ''
    summary = manifest.get('summary') or manifest.get('name')
    summary = sanitize_cell(summary)
    # description = manifest.get('description') or ''
    # description_en, description_it = extract_des(description)
    installable = manifest.get('installable', True)
    if not installable and version != 'deprecated':
        version = version + ' (unported)'
    return [link, version, summary], installable


def gen_addons_table(args):
    if len(args) and args[0] in ('addons', ):
        inline = True
        element = args[0]
    else:
        inline = False
        element = 'addons'
        readme_path = 'README.md'
        if not os.path.isfile(readme_path):
            raise UserError('%s not found' % readme_path)
    if len(args) > 2 and os.path.isdir(args[2]):
        original_OCA = args[2]
    else:
        original_OCA = False
    # list addons in . and __unported__
    addon_paths = []
    for addon_path in os.listdir('.'):
        addon_paths.append((addon_path, False))
    unported_directory = '__unported__'
    if os.path.isdir(unported_directory):
        for addon_path in os.listdir(unported_directory):
            addon_path = os.path.join(unported_directory, addon_path)
            addon_paths.append((addon_path, True))
    addon_paths = sorted(addon_paths, lambda x, y: cmp(x[0], y[0]))
    # load manifestsif original_OCA:
    if original_OCA:
        header = ('addon', 'version', 'OCA version', 'summary')
    else:
        header = ('addon', 'version', 'summary')
    rows_available = []
    rows_unported = []
    # rows_original = []
    for addon_path, unported in addon_paths:
        for manifest_file in MANIFESTS:
            manifest_path = os.path.join(addon_path, manifest_file)
            has_manifest = os.path.isfile(manifest_path)
            if has_manifest:
                break
        if has_manifest:
            row, installable = get_values_from_manifest(addon_path,
                                                        manifest_path,
                                                        element)
            if unported and installable:
                raise UserError('%s is in __unported__ but is marked '
                                'installable.' % addon_path)
            o_row = ['', ':x:', '']
            if original_OCA:
                addon_name = os.path.basename(addon_path)
                OCA_addon_path = os.path.join(original_OCA, addon_name)
                for o_manifest_file in MANIFESTS:
                    o_manifest_path = os.path.join(OCA_addon_path,
                                                   o_manifest_file)
                    o_has_manifest = os.path.isfile(o_manifest_path)
                    if o_has_manifest:
                        break
                if o_has_manifest:
                    o_row, o_installable = get_values_from_manifest(
                        OCA_addon_path, o_manifest_path, 'addons')
                if row[1] != o_row[1]:
                    row.insert(2, o_row[1])
                else:
                    row.insert(2, ':repeat:')
            if installable:
                rows_available.append(row)
            else:
                rows_unported.append(row)
    if not inline:
        # replace table in README.md
        replace_in_readme(readme_path, header, rows_available, rows_unported)
    else:
        print_addons(header, rows_available, rows_unported)


def main(args):
    try:
        gen_addons_table(args)
    except UserError as e:
        print(e.msg)
        exit(1)


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
