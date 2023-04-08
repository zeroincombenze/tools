#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import argparse
import re
import lxml.etree as ET
from python_plus import _b

__version__ = "2.0.6"

# RULES: every rule is list:
# 1. element is the regex to apply: if regex matches line all the next elements
#    of the rule list are applied on current source line.
#    The "!" (exclamation point) at the beginning of the line means negation
#    If exclamation point is followed by "(TEXT)" and TEXT is in line, rule is skipped
#    i.e:  !my_text^import
#    Rule is applied on every line beginning with "import" but not on "import my_text"
#    If "(" does not follow exclamation point, the regex is negated
#    i.e.  !^import
#    Rule is applied on every line which does not begin with "import"
# 2. Every element (from 2.nd) may be a text or a list
#    If element is a list, it contains a couple of item for substitution
#    - The 1.st item is the regex to search for replace
#    - The 2.nd item is the text to replace; item cna contains macros like %(classname)s
#   If the element is a text, it is a function to apply.
#   All functions have the format:  def my_fun(self, nro)
#                                       [...]
#                                       return do_break, offset
#   Function may ask for break: this means no other rules will be executed.
#   Function must return the offset for next line (default is 0)
#   The value -1 re-read the current line, +1 skip next line, and so on
#
RULES_GLOBALS = [
    (
        r"^ *class [^(]+\(",
        "matches_class",
    ),
    (
        r"^(from [\w.]+ )?import",
        "matches_import",
    ),
    (
        r"!^(from [\w.]+ )?import",
        "no_matches_import",
    ),
]
RULES_GLOBALS_XML = [
]
RULES_TO_NEW_API = [
    (
        "^from openerp.osv import",
        ("from openerp.osv import", "from odoo import"),
        ("orm", "models"),
    ),
    (
        r"^ *class [^(]+\([^)]*\)",
        ("orm.Model", "models.Model"),
        ("osv.osv_memory", "models.TransientModel"),
    ),
    (
        r"^ *def [^(]+\(self, *cr, *uid, [^)]*\)",
        (r"\(self, *cr, *uid,", "(self,"),
        (r", *context=[^)]+", ""),
    ),
    ("^from openerp", ("openerp", "odoo")),
    ("!(import).*osv.except_osv", ("osv.except_osv", "UserError")),
]
RULES_TO_OLD_API = [
    (
        "^from odoo import",
        (
            ("models", "orm"),
            ("odoo", "openerp.osv"),
            ("models.TransientModel", "osv.osv_memory"),
        )
    ),
    (
        r"^ *class [^(]+\([^)]*\)",
        ("models.Model", "orm.Model"),
    ),
    (
        r"^ *def [^(]+\(self, [^)]*\)",
        (r"\(self,", "(self, cr, uid,"),
        (r"\)", ", context=None)"),
    ),
    (
        "^from odoo.exceptions import UserError",
        ("import UserError", "import Warning as UserError"),
    ),
    ("^from odoo", ("odoo", "openerp")),
    ("!(import).*UserError", ("UserError", "osv.except_osv")),
]
RULES_TO_ODOO_PY3 = [
    (
        r"^ *super\([^)]*\)",
        (r"super\([^)]*\)", "super()"),
        (r"\(cr, *uid, *", "("),
        (r", *context=[^)]+", ""),
    ),
]
RULES_TO_ODOO_PY2 = [
    (
        r"^ *super\([^)]*\)",
        (r"super\(\)", "super(%(classname)s, self)"),
        (r"(\)\.[^(]+)\(", r"\1(cr, uid, "),
        (r"(super[^)]+\)[^)]+)", r"\1, context=context"),
    ),
]
RULES_TO_XML_NEW = [
    (
        "^ *<openerp",
        "matches_openerp_tag",
    ),
    (
        "^ *</openerp>",
        "matches_openerp_endtag",
    ),
    (
        "^ *<data",
        "matches_data_tag",
    ),
    (
        "^ *</data>",
        "matches_data_endtag",
    ),
    (
        "^ *<odoo",
        "matches_odoo_tag",
    ),
    (
        "^ *</odoo>",
        "matches_odoo_endtag",
    ),
]
RULES_TO_XML_OLD = [
    (
        "^ *<odoo",
        "matches_odoo_tag",
    ),
    (
        "^ *</odoo>",
        "matches_odoo_endtag",
    ),
    (
        "^ *<openerp",
        "matches_openerp_tag",
    ),
    (
        "^ *</openerp>",
        "matches_openerp_endtag",
    ),
    (
        "^ *<data",
        "matches_data_tag",
    ),
    (
        "^ *</data>",
        "matches_data_endtag",
    ),
]
RULES_TO_PYPI_PY3 = [
    (
        r"^ *super\([^)]*\)",
        (r"super\([^)]*\)", "super()"),
    ),
]
RULES_TO_PYPI_PY2 = [
    (
        r"^ *super\(\)",
        (r"super\(\)", "super(%(classname)s, self)"),
    ),
]
RULES_TO_PYPI_FUTURE = [
    (
        r"^ *super\(\)",
        (r"super\(\)", "super(%(classname)s, self)"),
    ),
]
TAG_UTF8 = "# -*- coding: utf-8 -*-"
UNTAG_UTF8 = "# -*- encoding: utf-8 -*-"


class MigrateFile(object):

    def __init__(self, ffn, opt_args):
        if opt_args.verbose > 0:
            print("Reading %s ..." % ffn)
        self.ffn = ffn
        self.is_xml = ffn.endswith(".xml")
        if opt_args.from_version:
            self.from_major_version = int(opt_args.from_version.split('.')[0])
        else:
            self.from_major_version = 0
        self.to_major_version = int(opt_args.to_version.split('.')[0])
        if not opt_args.pypi_package:
            if self.to_major_version <= 10:
                opt_args.python_ver = "2.7"
            elif self.to_major_version <= 14:
                opt_args.python_ver = "3.7"
            else:
                opt_args.python_ver = "3.8"
        self.opt_args = opt_args
        self.lines = []
        with open(ffn, 'r') as fd:
            self.source = fd.read()
        self.lines = self.source.split('\n')
        self.analyze_source()

    def analyze_source(self):
        self.python_future = False
        if "from __future__ import" in self.source:
            self.python_future = True
        self.except_osv = False
        if self.from_major_version <= 8:
            if "osv.except_osv" in self.source:
                self.except_osv = True

    def matches_import(self, nro):
        self.in_import = True
        if (
            re.match("from odoo.exceptions import UserError", self.lines[nro])
            and self.to_major_version < 8
        ):
            del self.lines[nro]
            return False, -1
        if "UserError" in self.lines[nro]:
            self.UserError = True
        return False, 0

    def no_matches_import(self, nro):
        if (
            self.in_import
            and self.except_osv
            and not self.UserError
        ):
            self.lines.insert(nro - 1, "from odoo.exceptions import UserError")
            self.UserError = True
            return False, +1
        self.in_import = False
        return False, 0

    def get_noupdate_property(self, nro):
        if "noupdate" in self.lines[nro]:
            x = re.search("noupdate *=\"[01]\"", self.lines[nro])
            return self.lines[nro][x.start():x.end()]
        return ""

    def matches_class(self, nro):
        x = re.match(r"^ *class [^(]+", self.lines[nro])
        self.classname = self.lines[nro][x.start() + 6: x.end()].strip()
        return False, 0

    def matches_odoo_tag(self, nro,):
        if self.to_major_version < 8 and self.ctr_tag_openerp == 0:
            property_noupdate = self.get_noupdate_property(nro)
            if property_noupdate:
                self.lines.insert(nro + 1, "    <data %s>" % property_noupdate)
            else:
                self.lines.insert(nro + 1, "    <data>")
            self.lines[nro] = "<openerp>"
            self.ctr_tag_openerp += 1
        else:
            self.ctr_tag_odoo += 1
        return True, 0

    def matches_openerp_tag(self, nro):
        if self.to_major_version >= 8 and self.ctr_tag_odoo == 0:
            self.lines[nro] = "<odoo>"
            self.ctr_tag_odoo += 1
        else:
            self.ctr_tag_openerp += 1
        return True, 0

    def matches_data_tag(self, nro):
        offset = 0
        if self.ctr_tag_data == 0:
            property_noupdate = self.get_noupdate_property(nro)
            if self.ctr_tag_odoo == 1:
                del self.lines[nro]
                offset = -1
                if property_noupdate:
                    nro = 0
                    while not re.match("^ *<odoo", self.lines[nro]):
                        nro += 1
                    self.lines[nro] = "<odoo %s>" % property_noupdate
            else:
                self.ctr_tag_data += 1
        else:
            self.ctr_tag_data += 1
        return True, offset

    def matches_data_endtag(self, nro):
        offset = 0
        if self.ctr_tag_data == 0 and self.ctr_tag_odoo == 1:
            del self.lines[nro]
            offset = -1
        else:
            self.ctr_tag_data -= 1
        return True, offset

    def matches_openerp_endtag(self, nro):
        if self.ctr_tag_openerp == 0 and self.ctr_tag_odoo == 1:
            self.lines[nro] = "</odoo>"
            self.ctr_tag_odoo -= 1
        else:
            self.ctr_tag_openerp -= 1
        return True, 0

    def matches_odoo_endtag(self, nro):
        offset = 0
        if self.ctr_tag_odoo == 0 and self.ctr_tag_openerp == 1:
            self.lines[nro] = "</openerp>"
            self.ctr_tag_openerp -= 1
            if self.ctr_tag_data:
                self.lines.insert(nro, "    </data>")
                self.ctr_tag_data -= 1
                offset = 1
        else:
            self.ctr_tag_odoo -= 1
        return True, offset

    def update_line(self, nro, item):
        if isinstance(item, (list, tuple)):
            self.lines[nro] = re.sub(item[0],
                                     item[1] % self.__dict__,
                                     self.lines[nro])
            return False, 0
        if not hasattr(self, item):
            print("Function %s not found!" % item)
            return False, 0
        do_break, offset = getattr(self, item)(nro)
        return do_break, offset

    def do_migrate_source(self):
        def init_env():
            self.property_noupdate = False
            self.ctr_tag_data = 0
            self.ctr_tag_odoo = 0
            self.ctr_tag_openerp = 0
            self.ctr_tag_utf8 = False
            self.classname = ""
            self.in_import = False
            self.UserError = False
            self.coding_line = -1
            self.lines_2_rm = []
            TARGET = RULES_GLOBALS_XML if self.is_xml else RULES_GLOBALS
            if self.opt_args.pypi_package:
                if self.python_future:
                    TARGET += RULES_TO_PYPI_FUTURE
                if self.opt_args.python_ver:
                    TARGET += (
                        RULES_TO_PYPI_PY2
                        if (int(self.opt_args.python_ver.split(".")[0]) == 2)
                        else RULES_TO_PYPI_PY3
                    )
            elif self.is_xml:
                TARGET += (RULES_TO_XML_OLD
                           if self.to_major_version < 8 else RULES_TO_XML_NEW)
            elif self.from_major_version:
                if self.from_major_version < 8 and self.to_major_version >= 8:
                    TARGET += RULES_TO_NEW_API
                elif self.from_major_version >= 8 and self.to_major_version < 8:
                    TARGET += RULES_TO_OLD_API
                TARGET += (
                    RULES_TO_ODOO_PY2
                    if self.to_major_version <= 10 else RULES_TO_ODOO_PY3
                )
            else:
                TARGET += (
                    RULES_TO_ODOO_PY2
                    if self.to_major_version <= 10 else RULES_TO_ODOO_PY3
                )
            return TARGET

        def rule_matches(rule, nro):
            not_expr = False
            if rule[0].startswith("!"):
                x = re.match(r"!\([\w.]*\)+", rule[0])
                if x:
                    token = rule[0][x.start() + 2: x.end() - 1].strip()
                    if token in self.lines[nro]:
                        return False
                    regex = rule[0][x.end():]
                else:
                    regex = rule[0][2:]
                    not_expr = True
            else:
                regex = rule[0]
            if (
                (not not_expr and not re.match(regex, self.lines[nro]))
                or (not_expr and re.match(regex, self.lines[nro]))
            ):
                return False
            return regex

        TGT_RULES = init_env()
        nro = 0
        while nro < len(self.lines):
            next_nro = nro + 1
            if not self.lines[nro]:
                nro += 1
                continue

            do_continue = False
            if self.lines[nro] == TAG_UTF8:
                if self.coding_line < 0:
                    self.found_tag = True
                    self.coding_line = nro
                else:
                    del self.lines[nro]
                    continue
            elif self.lines[nro] == UNTAG_UTF8:
                del self.lines[nro]
                continue
            elif (
                self.lines[nro].startswith("# flake8:")
                or self.lines[nro].startswith("# pylint:")
            ):
                if self.coding_line >= 0:
                    del self.lines[self.coding_line]
                    self.found_tag = False
                    self.coding_line = -1
                    nro -= 1
                    continue
            for rule in TGT_RULES:
                if not isinstance(rule[1:], (list, tuple)):
                    print("Invalid rule")
                    print(rule)
                    return
                regex = rule_matches(rule, nro)
                if not regex:
                    continue
                for subrule in rule[1:]:
                    if isinstance(subrule[0], (list, tuple)):
                        for item in subrule:
                            do_break, offset = self.update_line(nro, item)
                    else:
                        do_break, offset = self.update_line(nro, subrule)
                    if offset:
                        next_nro = nro + 1 + offset
                        if offset < 0:
                            do_continue = True
                            break
                    elif do_break:
                        break
                if do_continue or do_break:
                    break
            if do_continue:
                nro = next_nro
                continue

            # if not self.is_xml:
            #     if self.matches_class(nro):
            #         pass
            nro += 1

    def write_xml(self, out_ffn):
        with open(out_ffn, 'w') as fd:
            xml = ET.fromstring(
                _b("\n".join(self.lines).replace('\t', '    '))
            )
            fd.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
            fd.write(ET.tostring(
                xml,
                encoding="unicode",
                with_comments=True,
                pretty_print=True)
            )

    def close(self):
        if self.source != "\n".join(self.lines):
            if self.opt_args.output:
                if os.path.isdir(self.opt_args.output):
                    out_ffn = os.path.join(self.opt_args.output,
                                           os.path.basename(self.ffn))
                else:
                    out_ffn = self.opt_args.output
            else:
                out_ffn = self.ffn

            bakfile = '%s.bak' % out_ffn
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            if os.path.isfile(out_ffn):
                os.rename(out_ffn, bakfile)
            if self.is_xml:
                self.write_xml(out_ffn)
            else:
                with open(out_ffn, 'w') as fd:
                    fd.write("\n".join(self.lines))
            if self.opt_args.verbose > 0:
                print('👽 %s' % out_ffn)


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Migrate source file",
        epilog="© 2021-2023 by SHS-AV s.r.l."
    )
    parser.add_argument('-b', '--to-version', default="12.0")
    parser.add_argument('-F', '--from-version')
    parser.add_argument('-o', '--output')
    parser.add_argument('-P', '--pypi-package', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument('-y', '--python-ver')
    parser.add_argument('path')
    opt_args = parser.parse_args(cli_args)
    sts = 0
    if (
        opt_args.output
        and not os.path.isdir(opt_args.output)
        and not os.path.isdir(os.path.dirname(opt_args.output))
    ):
        print('Path %s does not exist!' % os.path.dirname(opt_args.output))
        sts = 2
    elif os.path.isdir(opt_args.path):
        for root, dirs, files in os.walk(opt_args.path):
            if 'setup' in dirs:
                del dirs[dirs.index('setup')]
            for fn in files:
                if not fn.endswith('.py') and not fn.endswith('.xml'):
                    continue
                source = MigrateFile(os.path.join(root, fn), opt_args)
                source.do_migrate_source()
                source.close()
    elif os.path.isfile(opt_args.path):
        source = MigrateFile(opt_args.path, opt_args)
        source.do_migrate_source()
        source.close()
    else:
        print('Path %s does not exist!' % opt_args.path)
        sts = 2
    return sts


if __name__ == "__main__":
    exit(main())
