#!/usr/bin/env python
# -*- coding: utf-8 -*-
from past.builtins import basestring
import sys
import os
from datetime import datetime
import argparse
import re
import lxml.etree as ET
import yaml
from python_plus import _b
from z0lib import z0lib

__version__ = "2.0.11"

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
# - !(RE)REGEX are two python re; if current line matches (by search) the RE, rule is
#   skipped otherwise current line is processed if it matches REGEX; i.e:  !pkg^import
#   Rule is applied on every line beginning with "import" but not on "import pkg"
# - {{EXPR}}EREGEX is double expression; EREGEX is validated if pythonic EXPR is true
#   Some test are useful, like:
#   * self.to_major_version -> to process rule against specific Odoo major version
#   * self.from_major_version -> to process rule against source Odoo major version
#   * self.pythonsion -> to proces rule against python version
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
#        Function may requires break: this means no other rules will be processed.
#        Function returns the offset for next line: the value 0 means read next line,
#        the value -1 re-read the current line, +1 skip next line, and so on
# - "=": execute python code
#


# RULES_TO_XML_NEW = [
#     (
#         "^ *<openerp",
#         ("$", "matches_openerp_tag"),
#     ),
#     (
#         "^ *</openerp>",
#         ("$", "matches_openerp_endtag"),
#     ),
#     (
#         "^ *<data",
#         ("$", "matches_data_tag"),
#     ),
#     (
#         "^ *</data>",
#         ("$", "matches_data_endtag"),
#     ),
#     (
#         "^ *<odoo",
#         ("$", "matches_odoo_tag"),
#     ),
#     (
#         "^ *</odoo>",
#         ("$", "matches_odoo_endtag"),
#     ),
# ]
# RULES_TO_XML_OLD = [
#     (
#         "^ *<odoo",
#         ("$", "matches_odoo_tag"),
#     ),
#     (
#         "^ *</odoo>",
#         ("$", "matches_odoo_endtag"),
#     ),
#     (
#         "^ *<openerp",
#         ("$", "matches_openerp_tag"),
#     ),
#     (
#         "^ *</openerp>",
#         ("$", "matches_openerp_endtag"),
#     ),
#     (
#         "^ *<data",
#         ("$", "matches_data_tag"),
#     ),
#     (
#         "^ *</data>",
#         ("$", "matches_data_endtag"),
#     ),
# ]


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
        self.def_python_future = False
        if not opt_args.to_version or opt_args.to_version == "0.0":
            branch = ""
            sts, stdout, stderr = z0lib.run_traced(
                "git branch", verbose=False, dry_run=False
            )
            if sts == 0 and stdout:
                sts = 1
                for ln in stdout.split("\n"):
                    if ln.startswith("*"):
                        branch = ln[2:]
                        sts = 0
                        break
            if sts == 0:
                x = re.match(r"[0-9]+\.[0-9]+", branch)
                if not x:
                    sts = 1
            if sts == 0:
                branch = branch[x.start(): x.end()]
                opt_args.to_version = branch
            else:
                opt_args.to_version = "12.0"
        self.to_major_version = int(opt_args.to_version.split('.')[0])
        if not opt_args.pypi_package:
            if self.to_major_version <= 10:
                opt_args.python = "2.7"
                self.def_python_future = True
            elif self.to_major_version <= 14:
                opt_args.python = "3.7"
            else:
                opt_args.python = "3.8"
        if opt_args.python:
            self.python_version = opt_args.python
            self.py23 = int(opt_args.python.split(".")[0])
        else:
            self.python_version = "3.7"
            self.py23 = 3
            if opt_args.pypi_package:
                self.def_python_future = True
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
        self.python_future = self.def_python_future
        self.ignore_file = False
        for ln in self.lines:
            if not ln:
                continue
            if not ln.startswith("#"):
                break
            if "from __future__ import" in ln or "from past.builtins import " in ln:
                self.python_future = True
            if not self.opt_args.force and (
                "# flake8: noqa" in ln or "# pylint: skip-file" in ln
            ):
                self.ignore_file = True
        if not self.opt_args.force and (
            os.path.basename(self.ffn) in ("testenv.py", "conf.py", "_check4deps_.py")
            or "/tests/data/" in os.path.abspath(self.ffn)
        ):
            self.ignore_file = True

    def get_noupdate_property(self, nro):
        if "noupdate" in self.lines[nro]:
            x = re.search("noupdate *=\"[01]\"", self.lines[nro])
            return self.lines[nro][x.start(): x.end()]
        return ""

    def matches_ignore(self, nro):
        return True, 0

    def matches_class(self, nro):
        x = self.re_match(r"^ *class [^(]+", self.lines[nro])
        self.classname = self.lines[nro][x.start() + 6: x.end()].strip()
        return False, 0

    def matches_odoo_tag(
        self,
        nro,
    ):
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
            (self.python_future
             or self.opt_args.ignore_pragma
             or (self.opt_args.python and self.py23 == 2))
            and self.utf8_decl_nro < 0
        ):
            self.utf8_decl_nro = nro
        else:
            del self.lines[nro]
            offset = -1
        return False, offset

    def matches_end_utf8(self, nro):
        offset = 0
        if self.utf8_decl_nro < 0 and (self.py23 == 2 or self.python_future):
            if not self.opt_args.ignore_pragma:
                self.lines.insert(nro, "# -*- coding: utf-8 -*-")
                self.utf8_decl_nro = nro
        return False, offset

    def matches_lint(self, nro):
        offset = 0
        if self.utf8_decl_nro >= 0:
            del self.lines[self.utf8_decl_nro]
            self.utf8_decl_nro = -1
            offset = -1
        return False, offset

    def comparable_version(self, version):
        return ".".join(["%03d" % int(x) for x in version.split(".")])

    def update_line(self, nro, items, regex):
        action = items[0]
        params = items[1:] if len(items) > 1 else []
        if action.startswith("/"):
            not_expr = True
            action = action[1:]
        else:
            not_expr = False
            action = action
        if (not_expr and regex) or (not not_expr and not regex):
            return False, 0
        if action.startswith("+"):
            x = self.re_match(r"\+[0-9]+\.[0-9]", action)
            if x:
                ver = action[x.start(): x.end()]
                if self.comparable_version(
                    self.opt_args.python
                ) < self.comparable_version(ver):
                    return False, 0
            else:
                x = self.re_match(r"\+[0-9]+", action)
                ver = int(action[x.start() + 1: x.end()])
                if ver and ver < 6 and self.py23 < ver:
                    return False, 0
                if ver and ver >= 6 and self.to_major_version < ver:
                    return False, 0
            action = action[x.end():]
        if action.startswith("-"):
            x = self.re_match(r"\-[0-9]+\.[0-9]", action)
            if x:
                ver = action[x.start(): x.end()]
                if self.comparable_version(
                    self.opt_args.python
                ) > self.comparable_version(ver):
                    return False, 0
            else:
                x = self.re_match(r"-[0-9]+", action)
                ver = int(action[x.start() + 1: x.end()])
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
                self.lines[nro] = re.sub(
                    regex, params[1] % self.__dict__, self.lines[nro]
                )
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

        if (not not_expr and not self.re_match(regex, self.lines[nro])) or (
            not_expr and self.re_match(regex, self.lines[nro])
        ):
            return False
        return regex

    def load_config2(self, confname):
        configpath = os.path.join(
            os.path.dirname(os.path.abspath(os.path.expanduser(__file__))),
            "config",
            confname + ".yml",
        )
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
            else:
                TARGET += self.load_config(
                    "to_pypi_py2" if self.py23 == 2 else "to_pypi_py3"
                )
        elif self.is_xml:
            TARGET += self.load_config(
                "to_xml_old" if self.to_major_version < 9 else "to_xml_new"
            )
        elif self.from_major_version:
            if self.from_major_version < 8 and self.to_major_version >= 8:
                TARGET += self.load_config("to_new_api")
            elif self.from_major_version >= 8 and self.to_major_version < 8:
                TARGET += self.load_config("to_old_api")
            TARGET += self.load_config(
                "to_odoo_py2" if self.to_major_version <= 10 else "to_odoo_py3"
            )
        else:
            TARGET += self.load_config(
                "to_odoo_py2" if self.to_major_version <= 10 else "to_odoo_py3"
            )
        return TARGET

    def do_process_source(self):
        if self.ignore_file:
            return
        if os.path.basename(self.ffn) in (
                "history.rst", "HISTORY.rst", "CHANGELOG.rst"):
            return self.do_upgrade_history()
        if self.ffn.endswith('.py') or self.ffn.endswith('.xml'):
            return self.do_migrate_source()
        return False

    def do_migrate_source(self):

        def run_sub_rules(rule, nro, regex, next_nro):
            do_continue = do_break = False
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
            return do_continue, do_break, next_nro

        TGT_RULES = self.init_env()
        nro = 0
        while nro < len(self.lines):
            next_nro = nro + 1
            do_continue = False
            for rule in TGT_RULES:
                regex = self.rule_matches(rule[0], nro)
                do_continue, do_break, next_nro = run_sub_rules(
                    rule, nro, regex, next_nro)
                if do_continue or do_break:
                    break
            if do_continue:
                nro = next_nro
                continue
            nro += 1

    def do_upgrade_history(self):
        if not self.opt_args.test_res_msg:
            return
        test_res_msg = self.opt_args.test_res_msg.replace("\\n", "\n")
        x = re.search("[0-9]+ TestPoint", test_res_msg)
        if x and "\n" in test_res_msg:
            left_mesg, suppl = test_res_msg.split("\n", 1)
            right_mesg = left_mesg[x.end() - 10:]
            ctr = int(left_mesg[x.start():].split(" ", 1)[0])
            left_mesg = left_mesg[: x.start()]
            for ln in suppl.split("\n"):
                x = re.search("[0-9]+ TestPoint", ln)
                if x:
                    ctr += int(ln[x.start(): x.end() - 10])
            test_res_msg = left_mesg + str(ctr) + right_mesg
        last_date = ""
        found_list = False
        title_nro = qua_nro = i_start = i_end = -1
        for nro, ln in enumerate(self.lines):
            if not ln:
                if found_list:
                    break
                continue
            if not last_date and re.match(r"[0-9]+\.[0-9]+\.[0-9]+.*\([0-9]+", ln):
                x = re.search(r"\([0-9]{4}-[0-9]{2}-[0-9]{2}\)", ln)
                i_start = x.start() + 1
                i_end = x.end() - 1
                last_date = ln[i_start: i_end]
                title_nro = nro
                continue
            if qua_nro < 0 and ln.startswith("* [QUA]"):
                qua_nro = nro
            if last_date and ln.startswith("*"):
                found_list = True
        if (
            last_date
            and found_list
            and (datetime.now() - datetime.strptime(last_date, "%Y-%m-%d")).days < 20
        ):
            if qua_nro:
                self.lines[qua_nro] = test_res_msg
            else:
                nro -= nro - 1
                self.lines.insert(nro, test_res_msg)
                if not self.opt_args.dry_run:
                    with open(self.ffn, 'w') as fd:
                        fd.write("\n".join(self.lines))
            self.lines[title_nro] = (
                self.lines[title_nro][:i_start]
                + datetime.strftime(datetime.now(), "%Y-%m-%d")
                + self.lines[title_nro][i_end:])

    def write_xml(self, out_ffn):
        with open(out_ffn, 'w') as fd:
            xml = ET.fromstring(_b("\n".join(self.lines).replace('\t', '    ')))
            fd.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
            fd.write(
                ET.tostring(
                    xml, encoding="unicode", with_comments=True, pretty_print=True
                )
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
                cmd = (
                    "npx prettier --plugin=@prettier/plugin-xml --config=%s"
                    % prettier_config
                )
            else:
                cmd = "npx prettier --plugin=@prettier/plugin-xml --print-width=88"
            cmd += " --no-xml-self-closing-space --tab-width=4 --prose-wrap=always"
            cmd += " --write "
            cmd += out_ffn
            z0lib.run_traced(cmd, dry_run=self.opt_args.dry_run)
        else:
            opts = "--skip-source-first-line"
            if self.py23 == 2 or self.python_future:
                opts += " --skip-string-normalization"
            cmd = "black %s -q %s" % (opts, out_ffn)
            z0lib.run_traced(cmd, dry_run=self.opt_args.dry_run)

    def close(self):
        if self.opt_args.output:
            if os.path.isdir(self.opt_args.output):
                out_ffn = os.path.join(self.opt_args.output, os.path.basename(self.ffn))
            else:
                out_ffn = self.opt_args.output
            if not os.path.isdir(os.path.dirname(out_ffn)):
                os.mkdir(os.path.isdir(os.path.dirname(out_ffn)))
        else:
            out_ffn = self.ffn
        if not self.ignore_file and (out_ffn != self.ffn
                                     or self.source != "\n".join(self.lines)):
            if not self.opt_args.in_place:
                bakfile = '%s.bak' % out_ffn
                if os.path.isfile(bakfile):
                    os.remove(bakfile)
                if os.path.isfile(out_ffn):
                    os.rename(out_ffn, bakfile)
            if not self.opt_args.dry_run:
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
        description="Beautiful source file", epilog="© 2021-2023 by SHS-AV s.r.l."
    )
    parser.add_argument('-a', '--lint-anyway', action='store_true')
    parser.add_argument('-b', '--to-version')
    parser.add_argument('-F', '--from-version')
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help="Parse file containing '# flake8: noqa' or '# pylint: skip-file'",
    )
    parser.add_argument('--ignore-pragma', action='store_true')
    parser.add_argument('-i', '--in-place', action='store_true')
    parser.add_argument('-j', '--python')
    parser.add_argument(
        "-n",
        "--dry-run",
        help="do nothing (dry-run)",
        action="store_true",
    )
    parser.add_argument('-o', '--output')
    parser.add_argument('-P', '--pypi-package', action='store_true')
    parser.add_argument('--test-res-msg')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument(
        '-w',
        '--no-parse-with-formatter',
        action='store_true',
        help="do nor execute black or prettier on modified files",
    )
    parser.add_argument('path', nargs="*")
    opt_args = parser.parse_args(cli_args)
    sts = 0
    if (
        opt_args.output
        and not os.path.isdir(opt_args.output)
        and not os.path.isdir(os.path.dirname(opt_args.output))
    ):
        sys.stderr.write('Path %s does not exist!' % os.path.dirname(opt_args.output))
        sts = 2
    else:
        for path in opt_args.path or ("./",):
            if os.path.isdir(os.path.expanduser(path)):
                for root, dirs, files in os.walk(os.path.expanduser(path)):
                    if 'setup' in dirs:
                        del dirs[dirs.index('setup')]
                    for fn in files:
                        if not fn.endswith('.py') and not fn.endswith('.xml'):
                            continue
                        source = MigrateFile(
                            os.path.abspath(os.path.join(root, fn)), opt_args
                        )
                        source.do_process_source()
                        source.close()
                        sts = source.sts
                        if sts:
                            break
            elif os.path.isfile(path):
                source = MigrateFile(os.path.abspath(path), opt_args)
                source.do_process_source()
                source.close()
                sts = source.sts
            else:
                sys.stderr.write('Path %s does not exist!' % path)
                sts = 2
    return sts


if __name__ == "__main__":
    exit(main())
