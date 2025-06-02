#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# from past.builtins import basestring
from io import open
import sys
import os
import os.path as pth
from datetime import datetime
import argparse
import re
import lxml.etree as ET
import yaml
from python_plus import _b, _u, qsplit
from z0lib import z0lib

try:
    import license_mgnt
except ImportError:
    from wok_code.scripts import license_mgnt

__version__ = "2.0.22"

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CLEAR = "\033[0;m"
DEFAULT_ODOO_VER = "18.0"
DEFAULT_PYTHON_VER = "3.10"

INVALID_NAMES = [
    "build",
    "debian",
    "dist",
    "filestore",
    "migrations",
    "setup",
    # "tests",
    "tmp",
    "venv_odoo",
    "win32",
]


def get_pyver_4_odoo(odoo_ver):
    odoo_major = int(odoo_ver.split(".")[0])
    if odoo_major <= 10:
        pyver = "2.7"
    else:
        pyver = "3.%d" % (int((odoo_major - 9) / 2) + 6)
    return pyver


class MigrateMeta(object):

    def raise_error(self, message):   # pragma: no cover
        sys.stderr.write(message)
        sys.stderr.write("\n")
        self.sts = 3

    def populate_default_rule_categ(self, mime):
        self.rule_categ.append("globals_" + mime)
        if mime in ("py", "manifest"):
            self.rule_categ.append("globals_py%s" % self.py23)

        if self.opt_args.git_orgid:
            self.rule_categ.append("%s-%s_%s" % (
                self.opt_args.package_name,
                self.opt_args.git_orgid,
                mime))

        self.rule_categ.append("%s_%s" % (self.opt_args.package_name, mime))

        if mime == "py":
            if self.python_future:
                self.rule_categ.append("%s_future" % self.opt_args.package_name)
            else:
                self.rule_categ.append(
                    "%s_py%s" % (self.opt_args.package_name, self.py23))

        if (
                not self.from_major_version
                or self.from_major_version == self.to_major_version
        ):
            fn = "%s_%s_%s"
            self.rule_categ.append(
                fn % (self.opt_args.package_name, mime, self.to_major_version))
            if self.opt_args.git_orgid:
                self.rule_categ.append("%s-%s_%s_%s" % (
                    self.opt_args.package_name,
                    self.opt_args.git_orgid,
                    mime,
                    self.to_major_version))
        elif self.from_major_version and self.to_major_version:
            fn = "%s_%s_%s"
            if self.from_major_version < self.to_major_version:
                # Migration to newer Odoo version
                from_major_version = self.from_major_version - 1
                to_major_version = from_major_version + 1
                while to_major_version <= self.to_major_version:
                    self.rule_categ.append(
                        fn % (self.opt_args.package_name, mime, to_major_version))
                    if self.opt_args.git_orgid:
                        self.rule_categ.append("%s-%s_%s_%s" % (
                            self.opt_args.package_name,
                            self.opt_args.git_orgid,
                            mime,
                            to_major_version))
                    from_major_version += 1
                    to_major_version = from_major_version + 1
            elif self.from_major_version > self.to_major_version:
                # Backport to older Odoo version
                from_major_version = self.from_major_version - 1
                to_major_version = from_major_version + 1
                while to_major_version >= self.to_major_version:
                    self.rule_categ.append(
                        fn % (self.opt_args.package_name, mime, to_major_version))
                    if self.opt_args.git_orgid:
                        self.rule_categ.append("%s-%s_%s_%s" % (
                            self.opt_args.package_name,
                            self.opt_args.git_orgid,
                            mime,
                            to_major_version))
                    from_major_version -= 1
                    to_major_version = from_major_version + 1

    def store_mig_rules(self, mime="path"):
        # mime: (path|xml|py)
        self.rule_ctr = 0
        self.rule_categ = []
        self.mig_rules = {}

        if self.opt_args.rule_groups:
            if "-" in self.opt_args.rule_groups:
                self.populate_default_rule_categ(mime)

            for rule in self.opt_args.rule_groups.split(","):
                if "-" in rule:
                    rule = rule.replace("-", "")
                    if rule in self.rule_categ:
                        ix = self.rule_categ.index(rule)
                        del self.rule_categ[ix]
                else:
                    rule = rule.replace("+", "")
                    self.rule_categ.append(rule)

        if not self.opt_args.rule_groups or "+" in self.opt_args.rule_groups:
            self.populate_default_rule_categ(mime)
        # Local rules
        self.rule_categ.append(self.opt_args.add_rule_group)

    def load_config(self, confname, ignore_not_found=True, prio=1, no_store=False):
        """Load configuration file with rules and add them to migration rules.
        Currently still load old style rules.
        Every rule is list of PYEREX, (ACTION, PARAMETERS), ...

        Sort rule keys."""
        configpath = pth.join(
            pth.dirname(pth.abspath(pth.expanduser(__file__))),
            "config",
            confname + ".yml",
        )
        self.final = True if confname.endswith("_%d" % self.to_major_version) else False
        self.migrate_multi = False
        self.backport_multi = False
        if "_" in confname:
            x = confname.rsplit("_", 1)[-1]
            if x.isdigit():
                cur_ver = int(x)
                if self.from_major_version < self.to_major_version:
                    nxt_ver = cur_ver - 1
                    for x in self.rule_categ:
                        if x.endswith("_%s" % nxt_ver):
                            self.migrate_multi = True
                            break
                if self.from_major_version > self.to_major_version:
                    nxt_ver = cur_ver + 1
                    for x in self.rule_categ:
                        if x.endswith("_%s" % nxt_ver):
                            self.backport_multi = True
                            break

        rules = {}
        if pth.isfile(configpath):
            with open(configpath, "r") as fd:
                yaml_rules = yaml.safe_load(fd)
                if isinstance(yaml_rules, dict):
                    rules = yaml_rules
                elif yaml_rules is not None:
                    self.raise_error("Invalid file %s!" % configpath)
        elif not ignore_not_found:
            self.raise_error("File %s not found!" % configpath)
        rules_2_rm = []
        rules_2_load = []
        valid_rules = []
        invalid_rules = []
        if self.opt_args.rules and prio > 0:
            if "-" in self.opt_args.rules:
                invalid_rules = self.opt_args.rules.replace("-", "").split(",")
            else:
                valid_rules = self.opt_args.rules.split(",")
        for (name, item) in rules.items():
            if invalid_rules and name in invalid_rules:
                rules_2_rm.append(name)
                continue
            if valid_rules and name not in valid_rules:
                rules_2_rm.append(name)
                continue
            if not isinstance(item, dict):
                self.raise_error("Invalid rule <%s> in configuration file %s!"
                                 % (name, configpath))
            if "ctx" in item and not eval(item["ctx"], self.__dict__):
                rules_2_rm.append(name)
                continue
            if "include" in item:
                if item["include"] not in self.rule_categ:
                    rules_2_load.append(item["include"])
                rules_2_rm.append(name)
                continue

            item["prio"] = int(item.get("prio", "5"))
            if item["prio"] >= 9:
                item["prio"] = 199 + prio
            elif prio > 0:
                item["prio"] = item["prio"] + (prio - 1) * 10

            if name in self.mig_rules and item["prio"] > self.mig_rules[name]["prio"]:
                continue
            if "match" not in item:
                self.raise_error("Rule <%s> without 'match' in configuration file %s!"
                                 % (name, configpath))
            if "do" not in item:
                self.raise_error("Rule <%s> without 'do' in configuration file %s!"
                                 % (name, configpath))
            if not isinstance(item["do"], (list, tuple)):
                self.raise_error(
                    "Rule <%s> does not have do_do list in configuration file %s!"
                    % (item, configpath))
            for todo in item["do"]:
                if not isinstance(todo, dict):
                    self.raise_error("Invalid rule <%s> in configuration file %s!"
                                     % (name, configpath))
                if "action" not in todo:
                    self.raise_error("Rule <%s> without action, configuration file %s!"
                                     % (name, configpath))
            if (
                (prio == 0 and item["prio"] > 0)
                or (prio > 0 and item["prio"] == 0)
            ):
                rules_2_rm.append(name)
        for name in rules_2_rm:
            del rules[name]
        if no_store:
            return rules
        for fn in rules_2_load:
            rules.update(self.load_config(fn,
                                          ignore_not_found=False,
                                          prio=prio,
                                          no_store=True))
        self.mig_rules.update(rules)
        self.mig_keys = sorted(
            [(v["prio"], k) for (k, v) in self.mig_rules.items()])

    def split_pyrex_rules(self, rule):
        """Split pyrex rule into python expression and eregex rules.

        PYEREX is (python expression + enhanced regular expression)** is a set of 3
        distinct expressions, which are:

            #. Python expression (in order to apply eregex): enclosed by double braces
            #. Status eregex match (in order to apply eregex): enclosed by parens
            #. Applicable eregex to match item

        ACTION is applied if (python expression AND status eregex AND applicable eregex)
        the undeclared python expression or undeclared status eregx returns always true.

        eregex is a regular expression (python re) that may be negative if it starts
        with ! (exclamation mark)

        Returns:
            * rule w/o python expression
            * python expression result (True|False)
            * clean regex
            * negative regex flag
            * search regex to apply before regex
        """
        x = self.re_match(r"\{\{.*\}\}", rule)
        if x:
            # Found python expression
            expr = rule[x.start() + 2: x.end() - 2].strip()
            rule = rule[x.end()]
            try:
                pyres = eval(expr, self.__dict__)
            except BaseException as e:
                self.raise_error("Invalid expression %s" % expr)
                self.raise_error(e)
                pyres = False
        else:
            # python expression undeclared: result is True
            pyres = True

        not_re = False
        sre = ""
        x = self.re_match(r"^!\(([^)]+)\)+", rule)
        if x:
            sre = x.groups()[0]
            regex = rule[x.end():]
        elif rule.startswith(r"\!"):
            regex = rule[1:]
            not_re = True
        else:
            regex = rule

        return rule, pyres, regex, not_re, sre

    def re_match(self, regex, item):
        try:
            x = re.match(regex, item)
        except BaseException as e:
            self.raise_error("Invalid regex: match('%s','%s') -> %s" % (regex, item, e))
            x = None
        return x

    def match_rule(self, rule, item, partial=False):
        """Match python expression and extract REGEX from EREGEX
        If python expression is False or REGEX does not match, return null regex"""
        rule, pyres, regex, not_re, sre = self.split_pyrex_rules(rule)
        if not pyres:
            return pyres

        if sre and re.search(sre, item):
            return False

        if not partial and (
            (not not_re and not self.re_match(regex, item))
            or (not_re and self.re_match(regex, item))
        ):
            return False

        return regex

    def apply_rules_on_item(self, item, lineno=None):
        if lineno is None:
            next_lineno = self.out_fn = None
        else:
            next_lineno = lineno + 1
        do_continue = False
        for (prio, key) in self.mig_keys:
            rule = self.mig_rules[key]
            regex = self.match_rule(rule["match"], item)
            do_continue, do_break, next_lineno = self.run_sub_rules(
                rule, regex, item, lineno, next_lineno, key=key)
            if lineno:
                item = self.lines[lineno]
            if do_continue or do_break:
                break
        if do_continue:
            return next_lineno
        if lineno is not None:
            lineno += 1
        return lineno


class MigrateEnv(MigrateMeta):
    def __init__(self, opt_args):
        if opt_args.path:
            opt_args.path = [pth.expanduser(p) for p in opt_args.path]
        if opt_args.output:
            opt_args.output = pth.expanduser(opt_args.output)
        self.out_fn = None

        self.def_python_future = self.python_future = self.keep_as_is = False
        if opt_args.from_version:
            self.from_version = opt_args.from_version
            self.from_major_version = int(opt_args.from_version.split('.')[0])
        else:
            self.from_version = ""
            self.from_major_version = 0
        branch = ""
        if (not opt_args.to_version or opt_args.to_version == "0.0") and opt_args.path:
            curcwd = os.getcwd()
            if pth.isdir(opt_args.path[0]):
                os.chdir(opt_args.path[0])
            elif pth.isdir(pth.dirname(opt_args.path[0])):
                os.chdir(pth.dirname(opt_args.path[0]))
            sts, stdout, stderr = z0lib.os_system_traced(
                "git branch", verbose=False, dry_run=False
            )
            os.chdir(curcwd)
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
            elif opt_args.package_name == "odoo":
                opt_args.to_version = DEFAULT_ODOO_VER
            else:
                opt_args.to_version = "0.0"
        self.to_version = opt_args.to_version
        if opt_args.to_version and "." in opt_args.to_version:
            self.to_major_version = int(opt_args.to_version.split('.')[0])
        else:
            self.to_major_version = 0
        if (
                opt_args.package_name == "odoo"
                and not opt_args.python
                and opt_args.to_version
        ):
            opt_args.python = get_pyver_4_odoo(opt_args.to_version)
        if opt_args.python == "2-3":
            if opt_args.package_name == "odoo":
                self.python_version = get_pyver_4_odoo(opt_args.to_version)
            else:
                self.python_version = DEFAULT_PYTHON_VER
            self.def_python_future = True
        elif opt_args.python:
            self.python_version = opt_args.python
        else:
            self.python_version = DEFAULT_PYTHON_VER
            if opt_args.package_name == "pypi":
                self.def_python_future = True
        self.py23 = int(self.python_version.split(".")[0])
        self.first_line = False
        self.header = True
        self.stage = "header"
        self.transition_stage = ""
        self.imported = []
        self.try_indent = -1
        self.opt_args = opt_args

        self.store_mig_rules(mime="path")
        for rule in self.rule_categ:
            self.load_config(rule, prio=0)

    def action_on_file(self, subrule, regex, fqn):
        """Apply a rule on current file
        Rule is (action, params, ...)
        action may be: "/?([+-][0-9.]+)?(mv|rm|no)"

        Args:
            fqn (str): full qualified name
            subrule (list): current rule to apply
            regex (str): regex to match rule

        Returns:
            sts
        """
        action = subrule["action"]
        args = subrule.get("args", [])
        if action.startswith("/"):
            not_re = True
            action = action[1:]
        else:
            not_re = False
            action = action
        if (not_re and regex) or (not not_re and not regex):
            return 1
        if action == "mv":
            # mv fqn new_fqn
            subrule, pyres, regex, not_re, sre = self.split_pyrex_rules(args[0])
            if sre and re.search(sre, fqn):
                return 1
            if regex:
                self.out_fn = re.sub(
                    regex, pth.basename(fqn), args[1] % self.__dict__
                )
            return 0
        elif action == "no":
            # Ignore current file
            self.keep_as_is = True
            return 0
        elif action == "rm":
            self.keep_as_is = True
            return 0
        else:
            self.raise_error("Invalid rule action %s" % action)
        return 1

    def run_sub_rules(self, rule, regex, item, dummy, dummy2, key=None):
        do_continue = do_break = False
        for subrule in rule["do"]:
            do_break = self.action_on_file(subrule, regex, item)
        return do_continue, do_break, dummy


class MigrateFile(MigrateMeta):
    def __init__(self, fqn, opt_args, migrate_env):
        self.sts = 0
        self.REX_CLOTAG = re.compile(r"<((td|tr)[^>]*)> *?</\2>")
        if opt_args.verbose > 0:
            print("Reading %s ..." % fqn)
        for trigger in ("first_line", "migrate_multi", "backport_multi"):
            setattr(self, trigger, False)
        self.header = True
        self.stage = "pre"
        self.transition_stage = ""
        self.imported = []
        self.try_indent = -1
        self.fqn = fqn
        base = pth.basename(fqn)
        self.out_fn = migrate_env.out_fn or base
        if base in ("__manifest__.py", "__openerp__.py"):
            self.mime = "manifest"
        elif base in ("history.rst", "HISTORY.rst", "CHANGELOG.rst"):
            self.mime = "history"
        else:
            self.mime = pth.splitext(fqn)[1][1:]
        for kk in (
            "from_version",
            "to_version",
            "from_major_version",
            "to_major_version",
            "def_python_future",
            "python_version",
            "py23",
            "opt_args",
            "keep_as_is",
        ):
            setattr(self, kk, getattr(migrate_env, kk))

        self.lines = []
        try:
            with open(fqn, "r", encoding="utf-8") as fd:
                self.source = fd.read()
        except BaseException:
            self.source = ""
            self.keep_as_is = True
        self.lines = self.source.split('\n')
        self.analyze_source()

    def analyze_source(self):
        self.python_future = self.def_python_future
        self.exception_osv = False
        self.exceptions = []
        if (
                not self.opt_args.from_version
                and self.lines
                and self.lines[0].startswith("#!")
        ):
            if "python3" in self.lines[0]:
                self.from_version = DEFAULT_PYTHON_VER
                self.from_major_version = 3
            elif "python3" in self.lines[0]:
                self.from_version = "2.7"
                self.from_major_version = 2
        for ln in self.lines:
            if not ln:
                continue
            if "from __future__ import" in ln or "from past.builtins import " in ln:
                self.python_future = True
            if not self.opt_args.force and (
                "# flake8: noqa" in ln or "# pylint: skip-file" in ln
            ):
                self.keep_as_is = True
            x = re.search(r"raise *(odoo|openerp)\.exceptions\.[A-Z][A-Za-z0-9_]+", ln)
            if x:
                exception = ln[x.start(): x.end()].split(".")[2]
                if exception not in self.exceptions:
                    self.exceptions.append(exception)
            x = re.search(r"raise osv\.except_osv", ln)
            if x:
                self.exception_osv = True

        self.exceptions = ", ".join(self.exceptions) if self.exceptions else ""
        if not self.source or not self.opt_args.force and (
                pth.basename(self.fqn) in ("testenv.py", "conf.py", "_check4deps_.py")
                or "/tests/data/" in pth.abspath(self.fqn)
        ):
            self.keep_as_is = True

    def get_noupdate_property(self, lineno):
        if "noupdate" in self.lines[lineno]:
            x = re.search("noupdate *=\"(0|1|True|False)\"", self.lines[lineno])
            return self.lines[lineno][x.start(): x.end()]
        return ""

    def set_trigger(self, trigger, value):
        setattr(self, trigger, value)

    def match_ignore_line(self, lineno):
        return True, 0

    def match_found_api(self, lineno):
        if re.match(r"^ @*api\.", self.lines[lineno]):
            if re.match(r"^ @*api\.multi", self.lines[lineno]):
                self.api_multi = True
        else:
            self.api_multi = False
        return False, 0

    def sort_from_odoo_import(self, lineno):
        # Sort import
        x = self.re_match(r"(from (odoo|openerp) import )([\w, ]+)", self.lines[lineno])
        if x:
            self.lines[lineno] = x.groups()[0] + ", ".join(
                sorted([k.strip() for k in x.groups()[-1].split(",")]))
        return False, 0

    def match_odoo_tag(
        self,
        lineno,
    ):
        if self.to_major_version < 8 and self.ctr_tag_openerp == 0:
            property_noupdate = self.get_noupdate_property(lineno)
            if property_noupdate:
                self.lines.insert(lineno + 1, "    <data %s>" % property_noupdate)
            else:
                self.lines.insert(lineno + 1, "    <data>")
            self.lines[lineno] = "<openerp>"
            self.ctr_tag_openerp += 1
        else:
            self.ctr_tag_odoo += 1
        return True, 0

    def match_openerp_tag(self, lineno):
        if self.to_major_version >= 8 and self.ctr_tag_odoo == 0:
            self.lines[lineno] = "<odoo>"
            self.ctr_tag_odoo += 1
        else:
            self.ctr_tag_openerp += 1
        return True, 0

    def match_data_tag(self, lineno):
        offset = 0
        if self.ctr_tag_data == 0:
            property_noupdate = self.get_noupdate_property(lineno)
            if self.ctr_tag_odoo == 1:
                del self.lines[lineno]
                offset = -1
                if property_noupdate:
                    lineno = 0
                    while not self.re_match("^ *<odoo", self.lines[lineno]):
                        lineno += 1
                    self.lines[lineno] = "<odoo %s>" % property_noupdate
            else:
                self.ctr_tag_data += 1
        else:
            self.ctr_tag_data += 1
        return True, offset

    def match_data_endtag(self, lineno):
        offset = 0
        if self.ctr_tag_data == 0 and self.ctr_tag_odoo == 1:
            del self.lines[lineno]
            offset = -1
        else:
            self.ctr_tag_data -= 1
        return True, offset

    def match_openerp_endtag(self, lineno):
        if self.ctr_tag_openerp == 0 and self.ctr_tag_odoo == 1:
            self.lines[lineno] = "</odoo>"
            self.ctr_tag_odoo -= 1
        else:
            self.ctr_tag_openerp -= 1
        return True, 0

    def match_odoo_endtag(self, lineno):
        offset = 0
        if self.ctr_tag_odoo == 0 and self.ctr_tag_openerp == 1:
            self.lines[lineno] = "</openerp>"
            self.ctr_tag_openerp -= 1
            if self.ctr_tag_data:
                self.lines.insert(lineno, "    </data>")
                self.ctr_tag_data -= 1
                offset = 1
        else:
            self.ctr_tag_odoo -= 1
        return True, offset

    def match_utf8(self, lineno):
        offset = 0
        if (
            (self.python_future
             or self.opt_args.ignore_pragma
             or (self.opt_args.python and self.py23 == 2))
            and self.utf8_lineno < 0
        ):
            self.utf8_lineno = lineno
        else:
            del self.lines[lineno]
            offset = -1
        return False, offset

    def match_end_utf8(self, lineno):
        offset = 0
        if self.utf8_lineno < 0 and (self.py23 == 2 or self.python_future):
            if not self.opt_args.ignore_pragma:
                self.lines.insert(lineno, "# -*- coding: utf-8 -*-")
                self.utf8_lineno = lineno
        return False, offset

    def match_lint(self, lineno):
        offset = 0
        if self.utf8_lineno >= 0:
            del self.lines[self.utf8_lineno]
            self.utf8_lineno = -1
            offset = -1
        return False, offset

    def match_version(self, lineno):
        if self.opt_args.from_version and self.opt_args.to_version:
            self.lines[lineno] = self.lines[lineno].replace(self.opt_args.from_version,
                                                            self.opt_args.to_version,
                                                            1)
        return False, 0

    def comparable_version(self, version):
        return ".".join(["%03d" % int(x) for x in version.split(".")])

    def trace_debug(self, key, lineno, action):
        if self.opt_args.debug and key:
            self.lines[lineno] += " # " + key + "/" + action

    def update_line(self, subrule, regex, lineno, key=None):
        """Update current line self.lines[lineno]
        Rule is (action, params, ...)
        action may be: "/?([+-][0-9.]+)?(s|d|i|a|$|=)"

        Args:
            lineno (int): line number
            subrule (list): current rule to apply
            regex (str): regex to match rule

        Returns:
            do_break, offset
        """
        action = subrule["action"]
        args = subrule.get("args", [])
        if action.startswith("/"):
            not_re = True
            action = action[1:]
        else:
            not_re = False
            action = action
        if (not_re and regex) or (not not_re and not regex):
            return False, 0
        if action == "s":
            regex = self.match_rule(args[0], self.lines[lineno], partial=True)
            if regex:
                self.lines[lineno] = re.sub(regex,
                                            args[1] % self.__dict__,
                                            self.lines[lineno])

                self.trace_debug(key, lineno, action)
            return False, 0
        elif action == "d":
            if self.opt_args.debug and key:
                self.lines[lineno] = "# " + key + "/" + action
            else:
                # delete current line
                del self.lines[lineno]
            return True, -1
        elif action == "i":
            # insert line before current with params[0]
            self.lines.insert(lineno, args[0] % self.__dict__, )
            self.trace_debug(key, lineno, action)
            return True, -1
        elif action == "a":
            # append line after current with params[0]
            self.lines.insert(lineno + 1, args[0] % self.__dict__, )
            self.trace_debug(key, lineno + 1, action)
            return False, 0
        elif action == "$":
            if not hasattr(self, args[0]):
                self.raise_error("Function %s not found!" % args[0])
                return False, 0
            do_break, offset = getattr(self, args[0])(lineno)
            self.trace_debug(key, lineno, action + args[0] + "()")
            return do_break, offset
        elif action == "+":
            if not args:
                self.raise_error("Action set trigger (+) w/o trigger name!")
                return False, 0
            x = re.match(self.mig_rules[key]["match"], self.lines[lineno])
            if x:
                self.set_trigger(args[0], x.groups()[0])
                self.trace_debug(key, lineno, action + args[0])
            return False, 0
        elif action == "-":
            if not args:
                self.raise_error("Action reset trigger (+) w/o trigger name!")
                return False, 0
            self.set_trigger(args[0], False)
            self.trace_debug(key, lineno, action + args[0])
            return False, 0
        elif action == "=":
            try:
                eval(args[0], self.__dict__)
                self.trace_debug(key, lineno, action + args[0])
            except BaseException as e:
                self.raise_error("Invalid expression %s" % args[0])
                self.raise_error(e)
            return False, 0
        else:
            self.raise_error("Invalid rule action %s" % action)
        return False, 0

    def init_env(self):
        self.property_noupdate = False
        self.ctr_tag_data = 0
        self.ctr_tag_odoo = 0
        self.ctr_tag_openerp = 0
        self.classname = ""
        self.in_import = False
        self.UserError = False
        self.utf8_lineno = -1
        self.lines_2_rm = []

        self.store_mig_rules(mime=self.mime)
        prio = len(self.rule_categ) + 1
        for rule in self.rule_categ:
            self.load_config(rule, prio=prio)
            prio -= 1
        if not self.mig_rules:
            # No rule to process, ignore file
            self.keep_as_is = True

    def run_sub_rules(self, rule, regex, item, lineno, next_lineno, key=None):
        do_continue = do_break = False
        for subrule in rule["do"]:
            do_break, offset = self.update_line(subrule, regex, lineno, key=key)
            if offset:
                next_lineno = lineno + 1 + offset
                if offset < 0:
                    do_continue = True
                    break
            elif do_break:
                break
        return do_continue, do_break, next_lineno

    def do_process_source(self):
        if self.opt_args.git_merge_conflict:
            self.solve_git_merge()
        if self.keep_as_is:
            return self.do_copy_file()
        else:
            meth = "do_upgrade_" + self.mime
            if hasattr(self, meth):
                return getattr(self, meth)()
            meth = "do_upgrade_file"
            if hasattr(self, meth):
                return getattr(self, meth)()
        return False

    def do_copy_file(self):
        return False

    def do_upgrade_py(self):
        res = self.do_upgrade_file()
        if (
                self.opt_args.copyright_check
                and self.opt_args.package_name == "odoo"
                and self.opt_args.to_version
        ):
            License = license_mgnt.License()
            for lineno, ln in enumerate(self.lines):
                if not self.lines[lineno]:
                    continue
                if not self.lines[lineno].startswith("#"):
                    break
                _, _, _, _, old_years = License.extract_info_from_line(
                    self.lines[lineno])
                _, _, _, _, cur_years = License.extract_info_from_line(
                    self.lines[lineno],
                    odoo_major_version=self.to_major_version,
                    force_from=True if self.opt_args.copyright_check > 1 else False)
                if old_years != cur_years:
                    self.lines[lineno] = self.lines[lineno].replace(
                        old_years, cur_years, 1)
        return res

    def do_upgrade_manifest(self):
        return self.do_upgrade_py()

    def do_upgrade_history(self):
        res = self.do_upgrade_file()
        self.do_upgrade_res_msg()
        return res

    def do_upgrade_file(self):

        def count_unbalanced(ln, left, right):
            ln = qsplit(ln, "#")[0]
            return len(qsplit(ln, left)) - (len(qsplit(ln, right)) if right else 1)

        self.init_env()
        if not self.keep_as_is:
            lineno = parens = brackets = braces = quotes = angles = 0
            self.open_stmt = False
            self.header = True
            self.stage = "header"
            self.transition_stage = ""
            self.imported = []
            self.try_indent = -1
            self.indent = self.stmt_indent = ""
            while lineno < len(self.lines):
                self.first_line = lineno == 0
                if self.lines[lineno]:
                    if not re.match("^ *#", self.lines[lineno]):
                        self.header = False
                        if (
                                re.match("^ *from .* import ", self.lines[lineno])
                                or re.match("^ *import ", self.lines[lineno])
                        ):
                            self.transition_stage = self.stage
                            self.stage = "import"
                            pkgs = re.split("import", self.lines[lineno])[1]
                            pkgs = pkgs.split("#")[0]
                            for pkg in pkgs.split(","):
                                pkg = pkg.strip()
                                if pkg not in self.imported:
                                    self.imported.append(pkg)
                        elif re.match("^ *def ", self.lines[lineno]):
                            self.transition_stage = self.stage
                            self.stage = "function_body"
                        elif re.match("^ *class ", self.lines[lineno]):
                            self.transition_stage = self.stage
                            self.stage = "class_body"
                        elif self.stage:
                            self.transition_stage = self.stage
                            self.stage = ""
                    else:
                        self.transition_stage = self.stage
                        self.stage = "comment"
                    x = re.match(r"[\s]*", self.lines[lineno])
                    self.indent = self.lines[lineno][x.start():x.end()] if x else ""
                    if not self.open_stmt:
                        self.dedent = self.indent < self.stmt_indent
                        self.stmt_indent = self.indent
                        if re.match("^ *try:", self.lines[lineno]):
                            self.try_indent = len(self.indent)
                        elif len(self.indent) <= self.try_indent:
                            self.try_indent = -1
                lineno = self.apply_rules_on_item(self.lines[lineno], lineno=lineno)
                if lineno < len(self.lines) and self.lines[lineno]:
                    if self.mime == "xml":
                        angles += count_unbalanced(self.lines[lineno], "<", ">")
                    elif self.mime in ("py", "manifest"):
                        parens += count_unbalanced(self.lines[lineno], "(", ")")
                        brackets += count_unbalanced(self.lines[lineno], "[", "]")
                        braces += count_unbalanced(self.lines[lineno], "{", "}")
                        quotes += count_unbalanced(self.lines[lineno], '"""', None)
                        quotes = quotes % 2
                    self.open_stmt = (parens + brackets + braces + quotes + angles) != 0
        return True

    def do_upgrade_res_msg(self):
        if not self.opt_args.test_res_msg:
            return False
        test_res_msg = self.opt_args.test_res_msg.replace("\\n", "\n")
        if test_res_msg.startswith('"') or test_res_msg.startswith("'"):
            test_res_msg = test_res_msg[1: -1]
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
        title_lineno = qua_lineno = i_start = i_end = -1
        for lineno, ln in enumerate(self.lines):
            if not ln:
                if found_list:
                    break
                continue
            if not last_date and re.match(r"[0-9]+\.[0-9]+\.[0-9]+.*\([0-9]+", ln):
                x = re.search(r"\([0-9]{4}-[0-9]{2}-[0-9]{2}\)", ln)
                if not x:
                    print(red("Invalid changelog line: ") + ln)
                    continue
                i_start = x.start() + 1
                i_end = x.end() - 1
                last_date = ln[i_start: i_end]
                title_lineno = lineno
                continue
            if qua_lineno < 0 and re.match(r"['\"]*\* *\[QUA\]", ln):
                qua_lineno = lineno
            if last_date and ln.startswith("*"):
                found_list = True
        if (
            last_date
            and found_list
            and (datetime.now() - datetime.strptime(last_date, "%Y-%m-%d")).days < 20
        ):
            if qua_lineno:
                self.lines[qua_lineno] = test_res_msg
            else:
                lineno -= lineno - 1
                self.lines.insert(lineno, test_res_msg)
                if not self.opt_args.dry_run:
                    with open(self.fqn, "w", encoding="utf-8") as fd:
                        fd.write("\n".join(self.lines))
            self.lines[title_lineno] = (
                self.lines[title_lineno][:i_start]
                + datetime.strftime(datetime.now(), "%Y-%m-%d")
                + self.lines[title_lineno][i_end:])
        return True

    def solve_git_merge(self):
        state = "both"
        state_lev = 0
        lineno = 0
        while lineno < len(self.lines):
            ln = self.lines[lineno]
            if ln.startswith("<<<<<<<"):
                state = "left"
                state_lev += 1
                del self.lines[lineno]
            elif ln.startswith(">>>>>>>"):
                state = "right"
                state_lev += 1
                del self.lines[lineno]
            elif ln.startswith("=======") and state != "both":
                state_lev -= 1
                if not state_lev:
                    state = "both"
                del self.lines[lineno]
            elif state not in ("both", self.opt_args.git_merge_conflict):
                del self.lines[lineno]
            else:
                lineno += 1

    def write_xml(self, out_fqn):
        with open(out_fqn, "w", encoding="utf-8") as fd:
            source_xml = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
            source_xml += _u(ET.tostring(
                ET.fromstring(_b("\n".join(self.lines).replace('\t', '    '))),
                encoding="unicode", with_comments=True, pretty_print=True))
            x = self.REX_CLOTAG.search(source_xml)
            while x:
                source_xml = self.REX_CLOTAG.sub(r"<\1/>", source_xml)
                x = self.REX_CLOTAG.search(source_xml)
            fd.write(source_xml)

    def format_file(self, out_fqn):
        prettier_config = False
        black_config = False
        path = pth.dirname(pth.abspath(pth.expanduser(out_fqn)))
        out_fqn_dir_path = path
        while not prettier_config and not black_config:
            if pth.isfile(pth.join(path, ".pre-commit-config.yaml")):
                black_config = pth.join(path, ".pre-commit-config.yaml")
            if pth.isfile(pth.join(path, ".prettierrc.yml")):
                prettier_config = pth.join(path, ".prettierrc.yml")
            if path == pth.abspath(pth.expanduser("~")) or path == "/":
                break
            path = pth.dirname(path)
        if self.mime == "xml":
            if prettier_config:
                cmd = (
                    "npx prettier --plugin=@prettier/plugin-xml --config=%s"
                    % prettier_config
                )
            else:
                cmd = "npx prettier --plugin=@prettier/plugin-xml --print-width=88"
            cmd += " --no-xml-self-closing-space --tab-width=4 --prose-wrap=always"
            # cmd += " --bracket-same-line"
            cmd += " --write "
            cmd += out_fqn
            sts = z0lib.os_system(cmd, dry_run=self.opt_args.dry_run)
            if sts:
                self.opt_args.no_parse_with_formatter = True
        elif self.mime in ("py", "manifest"):
            if self.mime == "manifest" and self.opt_args.to_version:
                curcwd = os.getcwd()
                os.chdir(out_fqn_dir_path)
                opts = "-Rw -lmodule -Podoo"
                if self.opt_args.from_version and self.opt_args.to_version:
                    opts += " -F%s -b%s" % (self.opt_args.from_version,
                                            self.opt_args.to_version)
                if self.opt_args.git_orgid:
                    opts += " -G%s" % self.opt_args.git_orgid
                cmd = "%s %s %s" % (
                    sys.executable,
                    pth.join(pth.dirname(__file__), "gen_readme.py"),
                    opts)
                z0lib.os_system_traced(cmd, dry_run=self.opt_args.dry_run)
                os.chdir(curcwd)
            opts = "--skip-source-first-line"
            if (
                    (self.py23 == 2 or self.python_future)
                    and not self.opt_args.string_normalization
            ):
                opts += " --skip-string-normalization"
            cmd = "black %s -q %s" % (opts, out_fqn)
            sts = z0lib.os_system(cmd, dry_run=self.opt_args.dry_run)
            if sts:
                self.opt_args.no_parse_with_formatter = True

    def close(self):
        if self.opt_args.output:
            if pth.isdir(self.opt_args.output):
                root = [pth.abspath(x) for x in self.opt_args.path
                        if self.fqn.startswith(pth.abspath(x))]
                if root:
                    out_fqn = pth.join(self.opt_args.output,
                                       self.fqn[len(root[0]) + 1:])
                    out_fqn = pth.join(pth.dirname(out_fqn), self.out_fn)
                else:
                    out_fqn = pth.join(self.opt_args.output, self.out_fn)
            else:
                out_fqn = self.opt_args.output
            if not pth.isdir(pth.dirname(out_fqn)):
                os.makedirs(pth.dirname(out_fqn))
        else:
            out_fqn = pth.join(pth.dirname(self.fqn), self.out_fn)
        if not self.keep_as_is and (
                self.opt_args.lint_anyway
                or out_fqn != self.fqn
                or self.source != "\n".join(self.lines)):
            if not self.opt_args.in_place:
                bakfile = '%s.bak' % out_fqn
                if pth.isfile(bakfile):
                    os.remove(bakfile)
                if pth.isfile(out_fqn):
                    os.rename(out_fqn, bakfile)
            if not self.opt_args.dry_run:
                if self.mime == "xml":
                    self.write_xml(out_fqn)
                else:
                    with open(out_fqn, "w", encoding="utf-8") as fd:
                        fd.write("\n".join(self.lines))
            if not self.opt_args.no_parse_with_formatter:
                self.format_file(out_fqn)
            if self.opt_args.verbose > 0:
                print('👽 %s' % out_fqn)
        elif self.keep_as_is and self.fqn != out_fqn:
            cmd = "cp %s %s" % (self.fqn, out_fqn)
            z0lib.os_system(cmd, dry_run=self.opt_args.dry_run)
            if self.opt_args.verbose > 0:
                print('👽 %s' % out_fqn)


def red(text):
    return RED + text + CLEAR


def yellow(text):
    return YELLOW + text + CLEAR


def green(text):
    return GREEN + text + CLEAR


def print_rule_mime(migrate_env, opt_args, mime):
    print("\n===[%s]===" % mime)
    migrate_env.store_mig_rules(mime=mime)
    prio = len(migrate_env.rule_categ) + 1
    for rule in migrate_env.rule_categ:
        migrate_env.load_config(rule, prio=0 if mime == "path" else prio)
        prio -= 1
    if migrate_env.mig_rules:
        for (prio, key) in migrate_env.mig_keys:
            print("  %-40.40s %s" % (
                key,
                yellow(migrate_env.mig_rules[key].get("match", ">>> include"))))
            if opt_args.list_rules <= 2:
                continue
            for item in migrate_env.mig_rules[key].get("do", {}):
                text = item["action"]
                if text == "$":
                    text += item["args"][0]
                elif not item.get("args"):
                    pass
                elif len(item["args"]) == 1:
                    text += " " + green(item["args"][0])
                elif len(item["args"]) == 2:
                    text += (" " + red(item["args"][0]) + " " + green(item["args"][1]))
                print("%8.8s %s" % ("", text))


def print_rule_classes(migrate_env, mime):
    print()
    migrate_env.store_mig_rules(mime=mime)
    for rule in migrate_env.rule_categ:
        print("%4.4s> %s" % (mime, rule))


def list_rules(opt_args):
    if not opt_args.path:
        opt_args.path = ["./"]
    migrate_env = MigrateEnv(opt_args)
    for trigger in ("first_line", "migrate_multi", "backport_multi"):
        setattr(migrate_env, trigger, True)
    opt_args.header = True
    for mime in ("path", "py", "manifest", "history", "xml"):
        if opt_args.list_rules > 1:
            print_rule_mime(migrate_env, opt_args, mime)
        else:
            print_rule_classes(migrate_env, mime)
    return 0


def process_file(migrate_env, fqn):
    migrate_env.apply_rules_on_item(fqn)
    source = MigrateFile(fqn, migrate_env.opt_args, migrate_env)
    source.do_process_source()
    source.close()
    return source.sts


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Beautiful source file", epilog="© 2021-2025 by SHS-AV s.r.l."
    )
    parser.add_argument(
        '-a', '--lint-anyway',
        action='store_true',
        help='set to True when migrate software',
    )
    parser.add_argument(
        '-B', '--debug',
        action='store_true',
        help='add comment with applied rule: do not use in production',
    )
    parser.add_argument('-b', '--to-version')
    parser.add_argument(
        '-C', '--rule-groups',
        help=('Rule groups (comma separated) to parse'
              ' (use + for adding, - for removing)'
              ' use switch -l to see default groups list')
    )
    parser.add_argument('-c', '--copyright-check', action='count', default=0)
    parser.add_argument('-F', '--from-version')
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help="Parse file even containing '# flake8: noqa' or '# pylint: skip-file'",
    )
    parser.add_argument("-G", "--git-org", action="store", dest="git_orgid")
    parser.add_argument(
        "--git-merge-conflict",
        metavar="left|right",
        help="Keep left or right side code after git merge conflict")
    parser.add_argument(
        '--ignore-pragma',
        action='store_true',
        help='ignore coding utf-8 declaration'
    )
    parser.add_argument('-i', '--in-place', action='store_true')
    parser.add_argument(
        '-j', '--python',
        help="python version, format #.##, 2-3 use future"
    )
    parser.add_argument(
        '-l', '--list-rules',
        action='count',
        default=0,
        help='list rule groups (-ll list with rules too, -lll full list)')
    parser.add_argument(
        "-n",
        "--dry-run",
        help="do nothing (dry-run)",
        action="store_true",
    )
    parser.add_argument('-o', '--output')
    parser.add_argument('-P', '--package-name', default='odoo')
    parser.add_argument(
        '-R', '--rules',
        help=('Rules (comma separated) to parse (use - for removing)'
              ' use switch -ll to see default rules list')
    )
    parser.add_argument(
        "-S", "--string-normalization",
        action='store_true',
        help='force double quote enclosing strings'
    )
    parser.add_argument('--test-res-msg')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument(
        '-w',
        '--no-parse-with-formatter',
        action='store_true',
        help="do nor execute black or prettier on modified files",
    )
    parser.add_argument(
        '--add-rule-group',
        default='.arcangelo',
        help='Add rule group form file, default is .arcangelo.yml',
    )
    parser.add_argument('path', nargs="*")
    opt_args = parser.parse_args(cli_args)

    if opt_args.list_rules > 0:
        return list_rules(opt_args)

    if (
            opt_args.git_merge_conflict
            and opt_args.git_merge_conflict not in ("left", "right")
    ):
        print("Invalid value for switch --git-merge-conflict")
        print("Please use --git-merge-conflict=left or --git-merge-conflict=right")
        return 3

    sts = 0
    migrate_env = MigrateEnv(opt_args)
    if not migrate_env.opt_args.path:
        sys.stderr.write('No path supplied!\n')
        return 2
    if (
        migrate_env.opt_args.output
        and not pth.isdir(migrate_env.opt_args.output)
        and not pth.isdir(pth.dirname(migrate_env.opt_args.output))
    ):
        sys.stderr.write(
            'Path %s does not exist!\n' % pth.dirname(migrate_env.opt_args.output))
        return 2

    for path in migrate_env.opt_args.path:
        if pth.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [
                    d
                    for d in dirs
                    if (
                        not d.startswith(".")
                        and not d.startswith("_")
                        and not d.endswith("~")
                        and d
                        not in INVALID_NAMES
                        and not os.path.islink(pth.join(root, d))
                    )
                ]
                for fn in dirs:
                    fqn = pth.abspath(pth.join(root, fn)) + "/"
                    migrate_env.apply_rules_on_item(fqn)
                for fn in files:
                    sts = process_file(migrate_env, pth.abspath(pth.join(root, fn)))
                    if sts:
                        break
        elif pth.isfile(path):
            sts = process_file(migrate_env, path)
        else:
            sys.stderr.write('Path %s does not exist!\n' % path)
            sts = 2
        if sts:
            break
    return sts


if __name__ == "__main__":
    exit(main())

