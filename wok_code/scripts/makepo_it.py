#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import os.path
import sys
import argparse
import re

__version__ = "2.0.12"

PO_DEFAULT = r"""# Translation of Odoo Server.
# This file contains the translation of the following modules:
#   * MODULE
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 12.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2023-06-26 19:07+0000\n"
"PO-Revision-Date: 2023-06-26 22:06:00+0000\n"
"Language-Team: \n"
"Language: it\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Last-Translator: \n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"X-Generator: makepo_it.py\n"
"""


def add_po_line(potext, line):
    potext += line
    potext += "\n"
    return potext


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Make or create a PO file",
        epilog="© 2020-2023 by SHS-AV s.r.l.",
    )
    parser.add_argument("-b", "--branch", default="12.0")
    parser.add_argument("-C", "--clear-base-tnl", dest="clear_base_tnl")
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument("-m", "--module")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("file_po", default="./i18n/it.po")
    opt_args = parser.parse_args(cli_args)

    opt_args.file_po = os.path.abspath(opt_args.file_po)
    i18n_dir = os.path.dirname(opt_args.file_po)
    if not os.path.isdir(i18n_dir):
        if not opt_args.force:
            print("Dir %s not found!" % i18n_dir)
            return 1
        os.mkdir(i18n_dir)
    if not os.path.isfile(opt_args.file_po):
        if not opt_args.force:
            print("File %s not found!" % argparse.file_po)
            return 1
        with open(opt_args.file_po, 'w') as fd:
            fd.write(PO_DEFAULT)

    with open(opt_args.file_po, 'r') as fd:
        LAST_TNL_NAME = 'Antonio M. Vigliotti'
        LAST_TNL_MAIL = 'antoniomaria.vigliotti@gmail.com'
        LAST_TEAM_NAME = 'Zeroincombenze'
        LAST_TEAM_URL = 'https://www.zeroincombenze.it'
        polines = fd.read().split('\n')
        potext = ''
        saved_lines = []
        for line in polines:
            if re.match("#[ \t]+\\*", line):
                potext = add_po_line(potext, "#\t* %s" % opt_args.module)
            elif line.startswith('#. module:'):
                potext = add_po_line(potext, r'#. module: %s' % opt_args.module)
            elif line.startswith('"Project-Id-Version:'):
                potext = add_po_line(
                    potext, r'"Project-Id-Version: Odoo (%s)\n"' % opt_args.branch
                )
            elif line.startswith('"Last-Translator:'):
                potext = add_po_line(
                    potext,
                    r'"Last-Translator: %s <%s>\n"' % (LAST_TNL_NAME, LAST_TNL_MAIL),
                )
            elif line.startswith('"Language-Team:'):
                potext = add_po_line(
                    potext,
                    r'"Language-Team: %s (%s)\n"' % (LAST_TEAM_NAME, LAST_TEAM_URL),
                )
                potext = add_po_line(potext, r'"Language: it\n"')
            elif line.startswith('"Language:'):
                pass
            elif line.startswith('"language'):
                pass
            elif line.startswith('"Plural-Forms:'):
                potext = add_po_line(
                    potext, r'"Plural-Forms: nplurals=2; plural=(n != 1);\n"'
                )
            elif opt_args.clear_base_tnl:
                if line.startswith('#: model:ir.module.module,description'):
                    saved_lines.append(line)
                    discard_saved_lines = True
                elif line.startswith('#: model:ir.module.module,shortdesc'):
                    saved_lines.append(line)
                    discard_saved_lines = True
                elif line.startswith('#: model:ir.module.module,summary'):
                    saved_lines.append(line)
                    discard_saved_lines = True
                elif saved_lines:
                    if not line or line.startswith('#'):
                        if not discard_saved_lines:
                            for ln in saved_lines:
                                potext += ln + '\n'
                        saved_lines = []
                        discard_saved_lines = False
                        potext = add_po_line(potext, line)
                    else:
                        saved_lines.append(line)
                else:
                    potext = add_po_line(potext, line)
            elif line == '""':
                continue
            elif re.match(r'^(msgid|msgstr) *"(<.+>)?\\n"', line):
                if line.startswith("msgid "):
                    potext = add_po_line(potext, 'msgid ""')
                    potext = add_po_line(potext, line[6:])
                elif line.startswith("msgstr "):
                    potext = add_po_line(potext, 'msgstr ""')
                    potext = add_po_line(potext, line[7:])
            elif len(line) >= 80 and not re.match(r"^\" +<", line):
                if line.startswith("msgid "):
                    potext = add_po_line(potext, 'msgid ""')
                    line = line[6:]
                elif line.startswith("msgstr "):
                    potext = add_po_line(potext, 'msgstr ""')
                    line = line[7:]
                spos = -1
                if not line.startswith("#") and len(line) >= 88:
                    spos = line.rfind(" ", 0, 80)
                if spos < 0:
                    potext = add_po_line(potext, line)
                else:
                    potext = add_po_line(potext, line[:spos + 1] + '"')
                    potext = add_po_line(potext, '"' + line[spos + 1:])
            else:
                potext = add_po_line(potext, line)
        if saved_lines and not discard_saved_lines:
            for ln in saved_lines:
                potext = add_po_line(potext, ln)
            # saved_lines = []

    with open(opt_args.file_po, 'w') as fd:
        fd.write(potext)


if __name__ == "__main__":
    exit(main())

