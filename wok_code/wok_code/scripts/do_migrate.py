#!/usr/bin/env python
# -*- coding: utf-8 -*-
from past.builtins import basestring
import sys
import os
import argparse
import re
import lxml.etree as ET
import yaml
from python_plus import _b
from z0lib import z0lib

__version__ = "2.0.7"

# RULES: every rule is list has the following format:
# EREGEX, (ACTION, PARAMETERS), ...
# where
# - EREGEX is an enhanced regular expression to apply the rule.
# - ACTION is the action to apply on current line
# - PARAMETERS are the values to supply on action
# - the list/tuple (ACTION, PARAMETERS) can be repeated more than once
#
# EREGEX
# EREGEX is an enhanced regular expression; the format are
# - REGEX is a python re: current line is processed if it matches REGEX
# - !REGEX is a python re: current line is processes if it does not match REGEX
#   If you will match "!" (exclamation point) user escape char "\": i.e. "\!match"
#   Escape before "!" is needed just at the beginning of the REGEX
# - !(RE)REGEX are two python re; if current line matches (BY search) the RE, rule is
#   skipped otherwise current line is processed if IT matches REGEX; i.e:  !pkg^import
#   Rule is applied on every line beginning with "import" but not on "import pkg"
# - {{EXPR}}EREGEX is double expression; EREGEX is validated if pythonic EXPR is true
#   Some test are useful, like:
#   * self.to_major_version -> to process rule against specific Odoo major version
#   * self.from_major_version -> to process rule against source Odoo major version
#   * self.python_version -> to proces rule against python version
#   * self.py23 -> to proces rule against python major version
# ACTION is the action will be executed: it can be prefixed by some simple expression
# if action begins with "/" (slash) it will be executed if EREGEX fails
# usually ACTION is executed when EREGEX is True
# i.e. ("s", "a", "b"), ("/d") -> If EREGEX, replace "a" with "b" else delete line
# ACTION can submitted to Odoo or python version:
# +[0-9] means from Odoo/python version
# -[0-9] means Odoo/version and older
# +[23]\.[0-9] means from python version
# -[23]\.[0-9] means python version and older
# i.e: ("+10s", "a", "b"), ("-7s", "b", "a") -> From Odoo 10.0 replace "a" with "b",
# with Odoo version 7.0 and older replace "b" with "a"
# ("+10-14s", "a", "b") -> From Odoo 10.0 to Odoo 14.0, replace "a" with "b"
# ACTION values:
# - "s": substitute REGEX REPLACE_TEXT
#   - The 1.st item is the EREGEX to search for replace (negate is not applied)
#   - The 2.nd item is the text to replace which can contain macros like %(classname)s
# - "d": delete line; stop immediately rule processing and re-read the line
# - "$": execute FUNCTION
#        All functions must have the format:    def my_fun(self, nro)
#                                                   [...]
#                                                   return do_break, offset
#        Function may ask for break: this means no other rules will be processed.
#        Function returns the offset for next line: the value 0 means read next line,
#        the value -1 re-read the current line, +1 skip next line, and so on
# - "=": execute python code
#
_RULES_GLOBALS = [
    (
        r"^# -\*- coding: utf-8 -\*-",
        ("$", "matches_utf8"),
    ),
    (
        "^# (flake8|pylint):",
        ("$", "matches_lint"),
    ),
    (
        "!(coding|flake8|pylint|python)^#",
        ("$", "matches_no_lint"),
    ),
    (
        "!^#",
        ("$", "matches_no_lint"),
    ),
    (
        r"^ *class [^(]+\(",
        ("$", "matches_class"),
    ),
    (
        r"^# -\*- encoding: utf-8 -\*-",
        ("d",),
    ),
]
_RULES_GLOBALS_XML = [
]
_RULES_TO_NEW_API = [
    (
        "^from openerp.osv import",
        ("s", "from openerp.osv import", "from odoo import"),
        ("s", "orm", "models"),
    ),
    (
        r"^ *class [^(]+\([^)]*\)",
        ("s", "orm.Model", "models.Model"),
        ("s", "osv.osv_memory", "models.TransientModel"),
    ),
    (
        r"^ *def [^(]+\(self, *cr, *uid, [^)]*\)",
        ("s", r"\(self, *cr, *uid,", "(self,"),
        ("s", r", *context=[^)]+", ""),
    ),
    ("^from openerp", ("s", "openerp", "odoo")),
    ("!(import).*osv.except_osv", ("s", "osv.except_osv", "UserError")),
]
_RULES_TO_OLD_API = [
    (
        "^from odoo import",
        ("s", "models", "orm"),
        ("s", "odoo", "openerp.osv"),
        ("s", "models.TransientModel", "osv.osv_memory"),
    ),
    (
        r"^ *class [^(]+\([^)]*\)",
        ("s", "models.Model", "orm.Model"),
    ),
    (
        r"^ *def [^(]+\(self, [^)]*\)",
        ("s", r"\(self,", "(self, cr, uid,"),
        ("s", r"\)", ", context=None)"),
    ),
    (
        "^from odoo.exceptions import UserError",
        ("s", "import UserError", "import Warning as UserError"),
    ),
    ("^from odoo", ("s", "odoo", "openerp")),
    (
        "from odoo.exceptions import UserError",
        (
            "s",
            "from odoo.exceptions import UserError",
            "from openerp.osv.osv import except_osv"
        ),
    ),
]
_RULES_TO_ODOO_PY3 = [
    (
        r"^ *super\([^)]*\)",
        ("s", r"super\([^)]*\)", "super()"),
        ("s", r"\(cr, *uid, *", "("),
        ("s", r", *context=[^)]+", ""),
    ),
]
_RULES_TO_ODOO_PY2 = [
    (
        r"^ *super\([^)]*\)",
        ("s", r"super\(\)", "super(%(classname)s, self)"),
        ("-8s", r"(\)\.[^(]+)\(", r"\1(cr, uid, "),
        ("-8s", r"(super[^)]+\)[^)]+)", r"\1, context=context"),
    ),
]
RULES_TO_XML_NEW = [
    (
        "^ *<openerp",
        ("$", "matches_openerp_tag"),
    ),
    (
        "^ *</openerp>",
        ("$", "matches_openerp_endtag"),
    ),
    (
        "^ *<data",
        ("$", "matches_data_tag"),
    ),
    (
        "^ *</data>",
        ("$", "matches_data_endtag"),
    ),
    (
        "^ *<odoo",
        ("$", "matches_odoo_tag"),
    ),
    (
        "^ *</odoo>",
        ("$", "matches_odoo_endtag"),
    ),
]
RULES_TO_XML_OLD = [
    (
        "^ *<odoo",
        ("$", "matches_odoo_tag"),
    ),
    (
        "^ *</odoo>",
        ("$", "matches_odoo_endtag"),
    ),
    (
        "^ *<openerp",
        ("$", "matches_openerp_tag"),
    ),
    (
        "^ *</openerp>",
        ("$", "matches_openerp_endtag"),
    ),
    (
        "^ *<data",
        ("$", "matches_data_tag"),
    ),
    (
        "^ *</data>",
        ("$", "matches_data_endtag"),
    ),
]
RULES_TO_PYPI_PY3 = [
    (
        r"^ *super\([^)]*\)",
        ("s", r"super\([^)]*\)", "super()"),
    ),
]
RULES_TO_PYPI_PY2 = [
    (
        r"^ *super\(\)",
        ("s", r"super\(\)", "super(%(classname)s, self)"),
    ),
]
RULES_TO_PYPI_FUTURE = [
    (
        r"^ *super\(\)",
        ("s", r"super\(\)", "super(%(classname)s, self)"),
    ),
]


class MigrateFile(object):

    def __init__(self, ffn, opt_args):
        self.sts = 0
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
        if opt_args.python_ver:
            self.python_version = opt_args.python_ver
            self.py23 = int(opt_args.python_ver.split(".")[0])
        else:
            self.python_version = "3.7"
            self.py23 = 3
        self.opt_args = opt_args
        self.lines = []
        with open(ffn, 'r') as fd:
            self.source = fd.read()
        self.lines = self.source.split('\n')
        self.analyze_source()

    def raise_error(self, message):
        sys.stderr.write(message)
        sys.stderr.write("\n")
        self.sts = 3

    def re_match(self, regex, line):
        try:
            x = re.match(regex, line)
        except BaseException as e:
            self.raise_error("Invalid regex: match('%s','%s') -> %s" % (regex, line, e))
            x = None
        return x

    def analyze_source(self):
        self.python_future = False
        if "from __future__ import" in self.source:
            self.python_future = True
        self.ignore_file = False
        if (
            not self.opt_args.force
            and ("# flake8: noqa" in self.source
                 or "# pylint: skip-file" in self.source)
        ):
            self.ignore_file = True
        elif not self.opt_args.force and os.path.basename(self.ffn) == "testenv.py":
            self.ignore_file = True

    def get_noupdate_property(self, nro):
        if "noupdate" in self.lines[nro]:
            x = re.search("noupdate *=\"[01]\"", self.lines[nro])
            return self.lines[nro][x.start():x.end()]
        return ""

    def matches_class(self, nro):
        x = self.re_match(r"^ *class [^(]+", self.lines[nro])
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
                    while not self.re_match("^ *<odoo", self.lines[nro]):
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

    def matches_utf8(self, nro):
        offset = 0
        if (
            self.opt_args.python_ver
            and self.opt_args.python_ver.startswith("2")
            and self.utf8_decl_nro < 0
        ):
            self.utf8_decl_nro = nro
        else:
            del self.lines[nro]
            offset = -1
        return False, offset

    def matches_lint(self, nro):
        offset = 0
        if self.utf8_decl_nro >= 0:
            del self.lines[self.utf8_decl_nro]
            self.utf8_decl_nro = -1
            offset = -1
        return False, offset

    def matches_no_lint(self, nro):
        offset = 0
        if (
            not self.utf8_decl_nro >= 0
            and self.py23 == 2
        ):
            self.lines.insert(nro, "# -*- coding: utf-8 -*-")
            self.utf8_decl_nro = nro
        return False, offset

    def comparable_version(self, version):
        return ".".join(
            [
                "%03d" % int(x)
                for x in version.split(".")
            ]
        )

    def update_line(self, nro, items, regex):
        action = items[0]
        params = items[1:] if len(items) > 1 else []
        if action.startswith("/"):
            not_expr = True
            action = action[1:]
        else:
            not_expr = False
            action = action
        if (
            (not_expr and regex)
            or (not not_expr and not regex)
        ):
            return False, 0
        if action.startswith("+"):
            x = self.re_match(r"\+[0-9]+\.[0-9]", action)
            if x:
                ver = action[x.start():x.end()]
                if (
                    self.comparable_version(self.opt_args.python_ver)
                    < self.comparable_version(ver)
                ):
                    return False, 0
            else:
                x = self.re_match(r"\+[0-9]+", action)
                ver = int(action[x.start() + 1:x.end()])
                if ver and ver < 6 and self.py23 < ver:
                    return False, 0
                if ver and ver >= 6 and self.to_major_version < ver:
                    return False, 0
            action = action[x.end():]
        if action.startswith("-"):
            x = self.re_match(r"\-[0-9]+\.[0-9]", action)
            if x:
                ver = action[x.start():x.end()]
                if (
                    self.comparable_version(self.opt_args.python_ver)
                    > self.comparable_version(ver)
                ):
                    return False, 0
            else:
                x = self.re_match(r"-[0-9]+", action)
                ver = int(action[x.start() + 1:x.end()])
                if ver and ver < 6 and self.py23 > ver:
                    return False, 0
                if ver and ver >= 6 and self.to_major_version > ver:
                    return False, 0
            action = action[x.end():]
        if action == "s":
            rule, expr, res, regex, not_expr, sre = self.split_py_re_rules(params[0])
            if sre and re.search(sre, self.lines[nro]):
                return False, 0
            if regex:
                self.lines[nro] = re.sub(regex,
                                         params[1] % self.__dict__,
                                         self.lines[nro])
            return False, 0
        elif action == "d":
            del self.lines[nro]
            return False, -1
        elif action == "$":
            if not hasattr(self, params[0]):
                self.raise_error("Function %s not found!" % params[0])
                return False, 0
            do_break, offset = getattr(self, params[0])(nro)
            return do_break, offset
        elif action == "=":
            try:
                eval(params[0])
            except BaseException as e:
                self.raise_error("Invalid expression %s" % params[0])
                self.raise_error(e)
            return False, 0
        else:
            self.raise_error("Invalid rule action %s" % action)
        return False, 0

    def split_py_re_rules(self, rule):
        x = self.re_match(r"\{\{.*\}\}", rule)
        if x:
            expr = rule[x.start() + 2: x.end() - 2].strip()
            rule = rule[x.end()]
            try:
                res = eval(expr)
            except BaseException as e:
                self.raise_error("Invalid expression %s" % expr)
                self.raise_error(e)
                res = False
        else:
            expr = ""
            res = True

        not_expr = False
        sre = ""
        if rule.startswith("!"):
            self.re_match(r"!\([^)]+\)+", rule)
            if x:
                sre = rule[x.start() + 2: x.end() - 1].strip()
                regex = rule[x.end():]
            else:
                regex = rule[1:]
                not_expr = True
        elif rule.startswith(r"\!"):
            regex = rule[1:]
        else:
            regex = rule

        return rule, expr, res, regex, not_expr, sre

    def rule_matches(self, rule, nro):
        """Match python expression and extract REGEX from EREGEX
        If python expression is False or REGEX does not match, return null regex"""
        rule, expr, res, regex, not_expr, sre = self.split_py_re_rules(rule)
        if not res:
            return res

        if sre and re.search(sre, self.lines[nro]):
            return False

        if (
            (not not_expr and not self.re_match(regex, self.lines[nro]))
            or (not_expr and self.re_match(regex, self.lines[nro]))
        ):
            return False
        return regex

    def load_config2(self, confname):
        configpath = os.path.join(
            os.path.dirname(os.path.abspath(os.path.expanduser(__file__))),
            "config",
            confname + ".yml")
        if os.path.isfile(configpath):
            with open(configpath, "r") as fd:
                return yaml.safe_load(fd)
        internal_name = "RULES_%s" % confname.upper()
        if internal_name not in globals():
            self.raise_error("File %s not found!" % configpath)
            return []
        return globals()[internal_name]

    def load_config(self, confname):
        rules = self.load_config2(confname)
        rules = [] if rules is None else rules
        for rule in rules:
            if not isinstance(rule, (list, tuple)):
                self.raise_error("Invalid rule %s of %s" % (rule, confname))
                return []
            if not isinstance(rule[0], basestring):
                self.raise_error("Invalid rule %s of %s" % (rule, confname))
                return []
            for subrule in rule[1:]:
                if not isinstance(subrule, (list, tuple)):
                    self.raise_error("Invalid rule %s of %s" % (rule, confname))
                    return []
                if len(subrule) > 1 and isinstance(subrule[1], (list, tuple)):
                    self.raise_error("Invalid rule %s of %s" % (rule, confname))
                    return []
        return rules

    def init_env(self):
        self.property_noupdate = False
        self.ctr_tag_data = 0
        self.ctr_tag_odoo = 0
        self.ctr_tag_openerp = 0
        self.classname = ""
        self.in_import = False
        self.UserError = False
        self.utf8_decl_nro = -1
        self.lines_2_rm = []

        TARGET = self.load_config("globals_xml" if self.is_xml else "globals")
        if self.opt_args.pypi_package:
            if self.python_future:
                TARGET += self.load_config("to_pypi_future")
            TARGET += self.load_config("to_pypi_py2" if self.py23 == 2
                                       else "to_pypi_py3")
        elif self.is_xml:
            TARGET += self.load_config("to_xml_old" if self.to_major_version < 8
                                       else "to_xml_new")
        elif self.from_major_version:
            if self.from_major_version < 8 and self.to_major_version >= 8:
                TARGET += self.load_config("to_new_api")
            elif self.from_major_version >= 8 and self.to_major_version < 8:
                TARGET += self.load_config("to_old_api")
            TARGET += self.load_config("to_odoo_py2" if self.to_major_version <= 10
                                       else "to_odoo_py3")
        else:
            TARGET += self.load_config("to_odoo_py2" if self.to_major_version <= 10
                                       else "to_odoo_py3")
        return TARGET

    def do_migrate_source(self):
        if self.ignore_file:
            return
        TGT_RULES = self.init_env()
        nro = 0
        while nro < len(self.lines):
            next_nro = nro + 1
            do_continue = False
            if not self.lines[nro]:
                do_continue = True
            else:
                for rule in TGT_RULES:
                    # rule format: (action, )
                    #              (action, (params), ...)
                    # Match python expression and extract REGEX from EREGEX
                    regex = self.rule_matches(rule[0], nro)
                    for subrule in rule[1:]:
                        # subrule may be: ("s", src, tgt) or ("d") or ...
                        do_break, offset = self.update_line(nro, subrule, regex)
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

    def format_file(self, out_ffn):
        prettier_config = False
        black_config = False
        path = os.path.dirname(os.path.abspath(os.path.expanduser(out_ffn)))
        while not prettier_config and not black_config:
            if os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
                black_config = os.path.join(path, ".pre-commit-config.yaml")
            if os.path.isfile(os.path.join(path, ".prettierrc.yml")):
                prettier_config = os.path.join(path, ".prettierrc.yml")
            if path == os.path.abspath(os.path.expanduser("~")) or path == "/":
                break
            path = os.path.dirname(path)
        if self.is_xml:
            if prettier_config:
                cmd = ("npx prettier --plugin=@prettier/plugin-xml --config=%s"
                       % prettier_config)
            else:
                cmd = "npx prettier --plugin=@prettier/plugin-xml --print-width=88"
            cmd = cmd + " --no-xml-self-closing-space --tab-width=4 --write "
            cmd += out_ffn
            z0lib.run_traced(cmd)
        else:
            cmd = "black --skip-string-normalization -q %s" % out_ffn
            z0lib.run_traced(cmd)

    def close(self):
        if self.opt_args.output:
            if os.path.isdir(self.opt_args.output):
                out_ffn = os.path.join(self.opt_args.output,
                                       os.path.basename(self.ffn))
            else:
                out_ffn = self.opt_args.output
            if not os.path.isdir(os.path.dirname(out_ffn)):
                os.mkdir(os.path.isdir(os.path.dirname(out_ffn)))
        else:
            out_ffn = self.ffn
        if not self.ignore_file and self.source != "\n".join(self.lines):
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
            if not self.opt_args.no_parse_with_formatter:
                self.format_file(out_ffn)
        elif self.opt_args.lint_anyway:
            self.format_file(out_ffn)


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Migrate source file",
        epilog="© 2021-2023 by SHS-AV s.r.l."
    )
    parser.add_argument('-a', '--lint-anyway', action='store_true')
    parser.add_argument('-b', '--to-version', default="12.0")
    parser.add_argument('-F', '--from-version')
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help="Parse file containing '# flake8: noqa' or '# pylint: skip-file'"
    )
    parser.add_argument('-o', '--output')
    parser.add_argument('-P', '--pypi-package', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument(
        '-w', '--no-parse-with-formatter',
        action='store_true',
        help="do nor execute black or prettier on modified files"
    )
    parser.add_argument('-y', '--python-ver')
    parser.add_argument('path')
    opt_args = parser.parse_args(cli_args)
    sts = 0
    if (
        opt_args.output
        and not os.path.isdir(opt_args.output)
        and not os.path.isdir(os.path.dirname(opt_args.output))
    ):
        sys.stderr.write('Path %s does not exist!' % os.path.dirname(opt_args.output))
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
                sts = source.sts
                if sts:
                    break
    elif os.path.isfile(opt_args.path):
        source = MigrateFile(opt_args.path, opt_args)
        source.do_migrate_source()
        source.close()
        sts = source.sts
    else:
        sys.stderr.write('Path %s does not exist!' % opt_args.path)
        sts = 2
    return sts


if __name__ == "__main__":
    exit(main())
