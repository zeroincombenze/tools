#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from io import open
import sys
import os
import os.path as pth
from datetime import datetime, timedelta
import argparse
import re

import lxml.etree as ET
import yaml
import mimetypes

from python_plus import _b, _u, qsplit
from z0lib import z0lib
try:
    from . import license_mgnt
except ImportError:  # pragma: no cover
    import license_mgnt

from .arcangelo_syntax import Syntax, get_config_path

__version__ = "2.1.1"

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


def is_device(path):
    return path and (
        path == "--" or path.startswith("/dev") or re.match("^[a-z0-9]+:", path))


def os_realpath(path):
    return pth.abspath(pth.expanduser(path))


class MigrateMeta(object):
    """The template class MigrateMeta manages the file and directory which code is to
    migrate. Migration workflow depends on file type/directory.
    For directory action may be:
    "no": do not process directory (ignore all file in it and keep them as they are)
    "mv": rename directory, if inplace, else copy directory with new name
    "rm": rename directory .bak, if inplace (remove directory) else ignore
    "ply": copy directory if it does not exit else do nothing (inplace do nothing)
    For file action may be:
    "no": do not process file and keep as is
    "mv": rename file, if inplace else copy file with new name
    "mv+no": rename file, if inplace else copy file with new name; never process
    "rm": rename file .bak, if inplace (remove file) else ignore
    "ply": copy file but do not process, if it does not exit else or inplace do nothing

    Processing file depends on its mime: currently are managed just python and
    xml files.
    """

    def __init__(self):
        for name in (
            "backport_multi",
            "final",
            "migration_multi",
            "python_future",
            "py23",
        ):
            setattr(self, name, False)
        for name in (
            "from_major_version",
            "to_major_version",
            "sts",
        ):
            setattr(self, name, 0)
        self.file_action = ""
        self.statements = []

    def raise_error(self, message):   # pragma: no cover
        sys.stderr.write(message)
        sys.stderr.write("\n")
        self.sts = 3

    def init_env_file(self):
        for name in (
            "classname",
            "indent",
            "language",
            "stage",
            "stmt_indent",
            "transition_stage",
        ):
            setattr(self, name, "")
        for name in (
            "dedent",
            "first_line",
        ):
            setattr(self, name, False)
        for name in (
            "header",
        ):
            setattr(self, name, True)

        self.stage = "header"
        self.try_indent = -1
        self.mig_rules = {}
        self.pass1_rules = {}
        self.imported = []

    def get_pyver_4_odoo(self, odoo_ver):
        odoo_major = int(odoo_ver.split(".")[0])
        if odoo_major <= 10:
            pyver = "2.7"
        else:
            pyver = "3.%d" % (int((odoo_major - 9) / 2) + 6)
        return pyver

    def populate_default_rule_categ(self, language):
        language = language.split("-")[0]
        if language:
            self.rule_categ.append("globals_" + language)
            if language in ("python", "manifest"):
                self.rule_categ.append("globals_py%s" % (self.py23 or 3))
                if self.set_python_future:
                    self.rule_categ.append("globals_future")

        if self.package_name:
            if language:
                self.rule_categ.append("%s_%s" % (self.package_name, language))
                if language in ("python", "manifest"):
                    self.rule_categ.append("%s_py%s" % (
                        self.package_name, self.py23 or 3))
                    if self.set_python_future:
                        self.rule_categ.append("%s_future" % self.package_name)

        if self.git_orgid:
            if language:
                self.rule_categ.append("%s_%s" % (self.git_orgid, language))
                if self.package_name:
                    self.rule_categ.append("%s-%s_%s" % (
                        self.package_name,
                        self.git_orgid,
                        language))
                if language in ("python", "manifest"):
                    self.rule_categ.append("%s_py%s" % (self.git_orgid, self.py23 or 3))
                    if self.set_python_future:
                        self.rule_categ.append("%s_future" % self.git_orgid)
                    if self.package_name:
                        self.rule_categ.append(
                            "%s-%s_py%s" % (
                                self.package_name,
                                self.git_orgid,
                                (self.py23 or 3)))
                        if self.python_future or self.set_python_future:
                            self.rule_categ.append("%s-%s_future" % (
                                self.package_name, self.git_orgid))

        if self.package_name:
            if (
                    self.from_major_version == self.to_major_version
                    and self.to_major_version
            ):
                fn = "%s%s_%s"
                self.rule_categ.append(
                    fn % (self.package_name, self.to_major_version, language))
                if self.git_orgid:
                    self.rule_categ.append("%s%s-%s_%s" % (
                        self.package_name,
                        self.to_major_version,
                        self.git_orgid,
                        language))
            elif self.from_major_version and self.to_major_version:
                fn = "%s%s_%s"
                if self.from_major_version < self.to_major_version:
                    # Migration to newer Odoo version
                    from_major_version = self.from_major_version - 1
                    to_major_version = from_major_version + 1
                    while to_major_version <= self.to_major_version:
                        self.rule_categ.append(
                            fn % (self.package_name, to_major_version, language))
                        if self.git_orgid:
                            self.rule_categ.append("%s%s-%s_%s" % (
                                self.package_name,
                                to_major_version,
                                self.git_orgid,
                                language))
                        from_major_version += 1
                        to_major_version = from_major_version + 1
                elif (
                        self.from_major_version > self.to_major_version
                        and self.package_name
                ):
                    # Backport to older Odoo version
                    from_major_version = self.from_major_version - 1
                    to_major_version = from_major_version + 1
                    while to_major_version >= self.to_major_version:
                        self.rule_categ.append(
                            fn % (self.package_name, to_major_version, language))
                        if self.git_orgid:
                            self.rule_categ.append("%s%s-%s_%s" % (
                                self.package_name,
                                to_major_version,
                                self.git_orgid,
                                language))
                        from_major_version -= 1
                        to_major_version = from_major_version + 1

    def detect_mig_rules(self, language=None):
        # language: (path|xml|python)
        # mig_rules structure:
        # - prio -> rule priority (int); it is the alias for beloved prio
        # - name -> rule name (text)
        #   - prio -> rule priority (int)
        #   - match/search -> regex to match/search (text)
        #   - ctx -> context to apply rule (text)
        #   - do -> action with arguments to do (struct list)
        #       - action -> action command to do (text)
        #       - args -> argument for action (list)
        #
        language = language or "path"
        self.rule_ctr = 0
        self.rule_categ = []
        self.mig_rules = {}
        self.pass1_rules = {}

        if self.opt_args.rule_groups:
            if "-" in self.opt_args.rule_groups:
                self.populate_default_rule_categ(language)

            for rule_cat in self.opt_args.rule_groups.split(","):
                if "-" in rule_cat:
                    rule_cat = rule_cat.replace("-", "")
                    if rule_cat in self.rule_categ:
                        ix = self.rule_categ.index(rule_cat)
                        del self.rule_categ[ix]
                else:
                    rule_cat = rule_cat.replace("+", "")
                    self.rule_categ.append(rule_cat)

        if not self.opt_args.rule_groups or "+" in self.opt_args.rule_groups:
            self.populate_default_rule_categ(language)
        # Local rules
        self.rule_categ.append(self.opt_args.add_rule_group)

    def load_config(self, confname, ignore_not_found=True, prio=1, no_store=False):
        """Load configuration file with rules and add them to migration rules.
        Currently still load old style rules.
        Every rule is list of PYEREX, (ACTION, PARAMETERS), ...

        Sort rule keys."""
        configpath = get_config_path(confname + ".yml", is_config=True)
        self.migrate_multi = False
        self.backport_multi = False
        if self.package_name and confname.startswith(self.package_name):
            x = confname[len(self.package_name):].split("-")[0].split("_")[0]
            if x.isdigit():
                cur_ver = int(x)
                self.final = cur_ver == self.to_major_version
                if self.from_major_version < self.to_major_version:
                    nxt_ver = cur_ver - 1
                    item = self.package_name + str(nxt_ver)
                    for x in self.rule_categ:
                        if x.startswith(item):
                            self.migrate_multi = True
                            break
                elif self.from_major_version > self.to_major_version:
                    nxt_ver = cur_ver + 1
                    item = self.package_name + str(nxt_ver)
                    for x in self.rule_categ:
                        if x.startswith(item):
                            self.backport_multi = True
                            break

        rules = {}
        rules_pass1 = {}
        if pth.isfile(configpath):
            if self.opt_args.debug:
                print(" .. analyzing %s" % configpath)
            with open(configpath, "r") as fd:
                yaml_rules = yaml.safe_load(fd)
                if isinstance(yaml_rules, dict):
                    rules = yaml_rules
                elif yaml_rules is not None:
                    self.raise_error("Invalid file %s!" % configpath)
                for rule in list(rules.keys()):
                    rules[rule]["fqn"] = pth.basename(configpath)
        elif not ignore_not_found:
            self.raise_error("File %s not found!" % configpath)
        elif self.opt_args.debug:
            print(" ..   no file %s found" % configpath)
        rules_2_rm = []
        rules_2_load = []
        rules_2_load_pass1 = []
        rules_2_pass1 = []
        valid_rules = []
        invalid_rules = []
        self.pass1 = True
        if self.opt_args.rules:
            for rule in [x.strip() for x in self.opt_args.rules.split(",")]:
                if rule.startswith("-"):
                    invalid_rules.append(rule.lstrip("-"))
                else:
                    valid_rules.append(rule.lstrip("+"))
        for (name, rule) in rules.items():
            if (
                    (invalid_rules and name in invalid_rules)
                    or (valid_rules and name not in valid_rules)
            ):
                rules_2_rm.append(name)
                continue
            if not isinstance(rule, dict):
                self.raise_error("Invalid rule <%s> in configuration file %s!"
                                 % (name, configpath))
            if "ctx" in rule:
                if "pass1" in rule["ctx"]:
                    for subrule in rule.get("do", []):
                        action = subrule.get("action", "")
                        if action in ("+", "-"):
                            args = subrule.get("args", [])
                            if len(args) > 0 and not hasattr(self, args[0]):
                                setattr(self, args[0], False)
                if not eval(rule["ctx"], self.__dict__):
                    rules_2_rm.append(name)
                    continue
            if "include" in rule:
                if rule["include"] not in self.rule_categ:
                    if "pass1" in rule.get("ctx", ""):
                        rules_2_load_pass1.append(rule["include"])
                    else:
                        rules_2_load.append(rule["include"])
                rules_2_rm.append(name)
                continue

            if "match" not in rule and "search" not in rule and "expr" not in rule:
                self.raise_error(
                    "Rule <%s> without 'match' neither 'search' neither 'expr'"
                    " in configuration file %s!" % (name, configpath))
            if "do" not in rule:
                self.raise_error("Rule <%s> without 'do' in configuration file %s!"
                                 % (name, configpath))
            if not isinstance(rule["do"], (list, tuple)):
                self.raise_error(
                    "Rule <%s> does not have to_do list in configuration file %s!"
                    % (rule, configpath))
            for todo in rule["do"]:
                if not isinstance(todo, dict):
                    self.raise_error("Invalid rule <%s> in configuration file %s!"
                                     % (name, configpath))
                if "action" not in todo:
                    self.raise_error("Rule <%s> without action, configuration file %s!"
                                     % (name, configpath))
            if "pass1" in rule.get("ctx", ""):
                rules_2_pass1.append(name)

        for (name, rule) in rules.items():
            rule["prio"] = int(rule.get("prio", "5"))
            if rule["prio"] == 0:
                rule["prio"] = rule["prio"] + prio
            elif rule["prio"] >= 9:
                rule["prio"] = 199 + prio
            else:
                rule["prio"] = rule["prio"] + (prio - 1) * 10
            rule["ctr"] = 0

            if (
                name not in rules_2_pass1
                and name in self.mig_rules
                and rule["prio"] > self.mig_rules[name]["prio"]
            ):
                # Less priority rule than current
                rules_2_rm.append(name)
            if (
                    name in rules_2_pass1
                    and name in self.pass1_rules
                    and rule["prio"] > self.pass1_rules[name]["prio"]
            ):
                # Less priority rule than current
                rules_2_rm.append(name)

        for name in rules_2_rm:
            del rules[name]
        for name in rules_2_pass1:
            rules_pass1[name] = rules[name]
            del rules[name]
        self.pass1 = False
        if no_store == "pass1":
            return rules_pass1
        elif no_store:
            return rules
        self.mig_rules.update(rules)

        for confname in rules_2_load:
            self.mig_rules.update(
                self.load_config(
                    confname,
                    ignore_not_found=False,
                    prio=prio,
                    no_store=True))
        for confname in rules_2_load_pass1:
            self.pass1_rules.update(
                self.load_config(
                    confname,
                    ignore_not_found=False,
                    prio=prio,
                    no_store="pass1"))

        self.mig_keys = sorted(
            [(v["prio"], k) for (k, v) in self.mig_rules.items()])
        self.pass1_rules.update(rules_pass1)
        self.pass1_keys = sorted(
            [(v["prio"], k) for (k, v) in self.pass1_rules.items()])

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
            (not not_re and not self.re_match(regex % self.__dict__, item))
            or (not_re and self.re_match(regex % self.__dict__, item))
        ):
            return False
        return regex

    def re_search(self, regex, item):
        try:
            x = re.search(regex, item)
        except BaseException as e:
            self.raise_error(
                "Invalid regex: search('%s','%s') -> %s" % (regex, item, e))
            x = None
        return x

    def search_rule(self, rule, item, partial=False):
        """Search python expression and extract REGEX from EREGEX
        If python expression is False or REGEX does not match, return null regex"""
        rule, pyres, regex, not_re, sre = self.split_pyrex_rules(rule)
        if not pyres:
            return pyres

        if sre and re.search(sre, item):
            return False

        if not partial and (
            (not not_re and not self.re_search(regex % self.__dict__, item))
            or (not_re and self.re_search(regex % self.__dict__, item))
        ):
            return False
        return regex

    def set_trigger(self, trigger, value):
        setattr(self, trigger, value)

    def get_mig_rules(self):
        return self.pass1_rules if self.pass1 else self.mig_rules

    def get_mig_keys(self):
        return self.pass1_keys if self.pass1 else self.mig_keys

    def apply_rules_on_item(self, item, stmtno=None):
        """Apply migration rule on current item.
        Current item may be a source line (with stmtno) or a full qualified name"""
        if stmtno is None:
            next_item = self.out_fn = None
            mimetypes.init()
            base = pth.basename(item)
            ext = pth.splitext(item)[1]
            if pth.isdir(item):
                self.mime = "inode/directory"
            elif base in ("__manifest__.py", "__openerp__.py"):
                self.mime = "text/manifest-python"
            elif base in ("history.rst", "HISTORY.rst", "CHANGELOG.rst"):
                self.mime = "text/history"
            else:
                self.mime = mimetypes.types_map.get(ext, "text/" + ext[1:])
            self.language = {
                "x-python": "python",
                # "manifest-python": "python",
            }.get(self.mime.split("/")[1], "")
            if not self.language and self.mime.split("/")[0] in ("image",):
                self.language = self.mime.split("/")[0]
            if not self.language:
                self.language = self.mime.split("/")[1]
        else:
            next_item = stmtno + 1
        do_continue = False
        self.stmtno = stmtno
        for (prio, key) in self.get_mig_keys():
            rule = self.get_mig_rules()[key]
            self.singleton = rule["ctr"] == 0
            regex = False if self.pass1 and "ctx" not in rule else ".*"
            if regex and "expr" in rule:
                self.line = item
                if not eval(rule["expr"], self.__dict__):
                    regex = False
            if regex:
                if (
                        stmtno is None
                        and key == "noop_file"
                        and self.language in ("image", )
                ):
                    regex = ".*"
                elif "match" in rule:
                    regex = self.match_rule(rule["match"], item)
                elif "search" in rule:
                    regex = self.search_rule(rule["search"], item)
            if not self.pass1 and regex:
                rule["ctr"] += 1
            do_continue, do_break, next_item = self.run_sub_rules(
                rule, regex, item, stmtno, next_item, key=key)
            item = self.statements[stmtno] if stmtno else item
            if do_continue or do_break:
                break
        if do_continue:
            return next_item
        if stmtno is not None:
            stmtno += 1
        return stmtno

    def load_all_config_rules(self, language=None):
        language = language or self.language
        if language != "path":
            self.language = language
        self.detect_mig_rules(language=language)
        prio = len(self.rule_categ) + 1 if language != "path" else 0
        for rule_cat in self.rule_categ:
            self.load_config(rule_cat, prio=prio)
            prio -= 1
        # if language not in ("path", "history") and not self.mig_rules:
        #     # No rule to process, ignore file
        #     self.file_action = "no"

    def list_rules(self):
        print("Rules to apply (Package %s version=%s)"
              % (self.package_name, self.package.release))
        if not self.opt_args.path:
            self.opt_args.path = [os_realpath("./")]
        for language in ("path", "python", "manifest-python", "history", "xml"):
            self.load_all_config_rules(language=language)
            if self.opt_args.list_rules > 1:
                self.print_rule_language(language)
            else:
                self.print_rule_classes(language)

    def print_rule_language(self, language):
        if "python" in language:
            print("\n===[%s: %s-%s(future=%s)]==="
                  % (self.package_name, language,
                     self.python_version, self.set_python_future))
        else:
            print("\n===[%s-%s: %s]==="
                  % (self.package_name, self.package.release, language))
        self.load_all_config_rules(language=language)
        if self.mig_rules:
            for (prio, key) in self.mig_keys:
                if self.mig_rules[key].get("search"):
                    print("  %-60.60s .*%s" % (
                        self.mig_rules[key]["fqn"] + "/" + key,
                        yellow(self.mig_rules[key]["search"])))
                elif self.mig_rules[key].get("match"):
                    print("  %-60.60s %s" % (
                        self.mig_rules[key]["fqn"] + "/" + key,
                        yellow(self.mig_rules[key]["match"])))
                else:
                    print("  %-60.60s" % (
                        self.mig_rules[key]["fqn"] + "/" + key))
                if self.opt_args.list_rules <= 2:
                    continue
                for item in self.mig_rules[key].get("do", {}):
                    text = item["action"]
                    if text == "$":
                        text += item["args"][0]
                    elif not item.get("args"):
                        pass
                    elif len(item["args"]) == 1:
                        text += " " + green(item["args"][0])
                    elif len(item["args"]) == 2:
                        text += (" " + red(item["args"][0]) + " "
                                 + green(item["args"][1]))
                    print("%8.8s %s" % ("", text))

    def print_rule_classes(self, language=None):
        if "python" in language:
            print("\n%s: %s=%s / future=%s"
                  % (self.package_name, language,
                     self.python_version, self.set_python_future))
        else:
            print("\n%s-%s: %s files"
                  % (self.package_name, self.package.release, language))
        self.detect_mig_rules(language=language)
        for rule in self.rule_categ:
            configpath = get_config_path(rule + ".yml", is_config=True)
            if pth.isfile(configpath):
                print("%8.8s> %s" % (language, rule))
            else:
                print("%8.8s> (%s)" % (language, rule))

    def list_syntax(self):
        if self.language == "unknown":
            self.language = "python"
        print("\n===[%s]===" % self.language)
        syntax = Syntax(self.language)
        for state in list(syntax.syntax_rules.keys()):
            print("---[%s]---" % state)
            for key, value in syntax.syntax_rules[state].items():
                print("%s=%s" % (key, value.pattern))


class MigrateEnv(MigrateMeta):
    """This class manages the migration environment
    Rules language is "path"
    """
    def __init__(self, opt_args):
        super().__init__()
        self.init_env_file()
        if hasattr(self, "fqn") and self.fqn and any(
                [x in self.fqn for x in opt_args.path]):
            self.recognize_package(path=self.fqn, default_name=opt_args.package_name)
        elif opt_args.path:
            opt_args.path = [os_realpath(p) for p in opt_args.path]
            self.recognize_package(path=opt_args.path[0],
                                   default_name=opt_args.package_name)
        else:
            self.recognize_package(default_name=opt_args.package_name)
        if opt_args.output and not is_device(opt_args.output):
            opt_args.output = os_realpath(opt_args.output)

        self.set_python_future = False

        if opt_args.from_version:
            self.from_version = opt_args.from_version
            self.from_major_version = int(opt_args.from_version.split('.')[0])
        else:
            self.from_version = ""
            self.from_major_version = 0
        if not opt_args.to_version or opt_args.to_version == "0.0":
            opt_args.to_version = self.package.release or "0.0"
        if opt_args.to_version == "0.0" and self.package_name == "odoo":
            opt_args.to_version = DEFAULT_ODOO_VER
        self.package.release = opt_args.to_version
        if opt_args.to_version and "." in opt_args.to_version:
            self.to_major_version = int(opt_args.to_version.split('.')[0])
        else:
            self.to_major_version = 0

        if (
                self.package_name == "odoo"
                and not opt_args.python
                and opt_args.to_version
        ):
            opt_args.python = self.get_pyver_4_odoo(opt_args.to_version)
        if opt_args.python == "2+3":
            if self.package_name == "odoo":
                self.python_version = self.get_pyver_4_odoo(opt_args.to_version)
            else:
                self.python_version = DEFAULT_PYTHON_VER
            self.set_python_future = True
        elif opt_args.python:
            self.python_version = opt_args.python
        elif self.package.python_versions:
            self.python_version = self.package.python_versions[0]
        else:
            self.python_version = DEFAULT_PYTHON_VER
        if self.package_name == "pypi":
            self.set_python_future = True
        self.py23 = int(self.python_version.split(".")[0])

        self.git_orgid = opt_args.git_orgid or self.package.git_orgid
        # Keep value for expression
        self.force = opt_args.force
        self.opt_args = opt_args
        self.load_all_config_rules(language="path")

    def init_env_file(self):
        super(MigrateEnv, self).init_env_file()

    def get_pkg_id(self, package_name):
        return {
            "Z0tools": "pypi",
            "Odoo": "odoo",
        }.get(package_name, package_name)

    def recognize_package(self, path=None, default_name=""):
        self.package_name = self.get_pkg_id(default_name)
        if path:
            self.package = z0lib.Package(
                path
                if pth.isdir(path)
                else pth.dirname(path))
        else:
            self.package = z0lib.Package()
            self.package.version = self.package.release = self.branch = "0.0"
        if not self.package_name:
            self.package_name = self.get_pkg_id(self.package.prjname) or "undefined"
        if not self.package.prjname:
            self.package.prjname = self.package_name

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
            return 0
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
        elif action in ("no", "rm", "ply"):
            # Ignore current file
            self.file_action = action
            return 0
        elif action == "+":
            if not args:
                self.raise_error("Action set trigger (+) w/o trigger name!")
                return 0
            if len(args) > 1:
                if re.match("[+-][0-9]+", args[1]):
                    self.set_trigger(args[0], int(args[1]) + getattr(self, args[0], 0))
                else:
                    self.set_trigger(args[0], args[1] % self.__dict__)
            else:
                self.set_trigger(args[0], True)
            return 0
        else:
            self.raise_error("Invalid rule action %s" % action)
        return 1

    def run_sub_rules(self, rule, regex, item, stmtno, next_lineno, key=None):
        do_continue = do_break = False
        for subrule in rule["do"]:
            if stmtno is None:
                do_break = self.action_on_file(subrule, regex, item)
                if do_break:
                    break
            else:
                do_break, offset = self.update_line(subrule, regex, stmtno, key=key)
                if offset:
                    next_lineno = stmtno + 1 + offset
                    if offset < 0:
                        do_continue = True
                        break
                elif do_break:
                    break
        return do_continue, do_break, next_lineno

    def process_file(self):
        self.do_process_source()
        self.close()
        return self.sts


class MigrateFile(MigrateEnv):
    """This class manages a file migration process.
    This class inherits some properties from Migration Environment
    Rules mime depends on file: "manifest-python", "python", "xml", "history", etc.
    """
    def __init__(self, opt_args, fqn, language=None, source=None):
        self.fqn = fqn
        super().__init__(opt_args)
        self.init_env_file()
        self.out_fn = None
        self.sts = 0
        self.tokenized = []
        self.remarks = []
        if self.fqn:
            if self.opt_args.verbose > 0:
                print("Reading %s ..." % self.fqn)
            self.load_all_config_rules(language="path")
            self.apply_rules_on_item(fqn)
            self.out_fn = self.out_fn or pth.basename(self.fqn)
            if self.sts or self.file_action in ("no", "rm", "ply"):
                return
        if language:
            self.load_all_config_rules(language=language)
        else:
            self.load_all_config_rules()
        if self.sts or self.file_action in ("no", "rm", "ply"):
            return
        if source:
            self.source = source
        else:
            self.read_source()
            if self.sts or self.file_action in ("no", "rm", "ply"):
                return
        self.syntax = Syntax(self.language)
        self.REX_CLOTAG = re.compile(r"<((td|tr)[^>]*)> *?</\2>")
        self.tokenize_source(check_shebang=True)

    def clone_env(self, language, source):
        new_env = self
        new_env.fqn = new_env.out_fn = None
        new_env.sts = 0
        new_env.source = source
        if language != new_env.language:
            new_env.load_all_config_rules(language=language)
        new_env.syntax = Syntax(self.language)
        new_env.REX_CLOTAG = re.compile(r"<((td|tr)[^>]*)> *?</\2>")
        new_env.tokenize_source()
        return new_env

    def read_source(self):
        try:
            with open(self.fqn, "r", encoding="utf-8") as fd:
                self.source = fd.read()
        except BaseException:
            self.source = ""
            self.file_action = "no"
            self.sts = 1
        if self.source and self.source[-1] != "\n":
            self.source += "\n"

    def check_shebang(self):
        mo = re.match("#![^\n]+", self.source)
        if mo:
            value = mo.group()
            for language in ("python", ):
                if language in value:
                    if self.language != language:
                        if "python3" in value:
                            self.python_version = DEFAULT_PYTHON_VER
                        else:
                            self.python_version = "2.7"
                        self.py23 = int(self.python_version.split(".")[0])
                        self.load_all_config_rules()
                        self.syntax = Syntax(language)
                    break

    def tokenize_source(
            self, hide_remark=False, check_shebang=False, split_statements=True):
        self.tokenized = []
        self.remarks = []
        if check_shebang:
            self.check_shebang()
        for token in self.syntax.tokenize(self.source):
            self.tokenized.append(token)
        if split_statements:
            self.split_source_statements()

    def init_env_file(self):
        super(MigrateFile, self).init_env_file()
        self.property_noupdate = False
        self.ctr_tag_data = 0
        self.ctr_tag_odoo = 0
        self.ctr_tag_openerp = 0
        self.in_import = False
        self.UserError = False
        self.utf8_lineno = -1
        self.lines_2_rm = []
        self.try_indent = -1

    def analyze_source(self):
        self.pass1 = True
        self.exceptions = []
        stmtno = 0
        while stmtno < len(self.statements):
            stmtno = self.apply_rules_on_item(self.statements[stmtno], stmtno=stmtno)
        self.exceptions = ", ".join(self.exceptions) if self.exceptions else ""
        self.pass1 = False

    def split_source_statements(self):
        self.statements = []
        ix = 0
        while ix < len(self.syntax.newline_pos):
            ix2 = ix + 1
            start = self.syntax.newline_pos[ix]
            if ix2 >= len(self.syntax.newline_pos):
                stop = len(self.source)
                if stop == start:
                    break
                stop = len(self.syntax.newline_pos)
                self.source += "\n"
            else:
                stop = self.syntax.newline_pos[ix2]
            self.statements.append(self.source[start: stop])
            ix = ix2

    def join_source_statements(self):
        while (
                len(self.statements) > 1
                and self.statements[-1] == "\n"
        ):
            del self.statements[-1]
        target = "".join(self.statements).replace("\t", "    ")
        if self.remarks:
            for ix in range(len(self.remarks)):
                pos = target.find("\v")
                if pos < 0:
                    break
                target = target[:pos] + self.remarks[ix] + target[pos:]
        if self.language == "xml":
            target = (
                "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
                + _u(ET.tostring(
                    ET.fromstring(_b(target)),
                    encoding="unicode",
                    with_comments=True,
                    pretty_print=True))
            )
            mo = self.REX_CLOTAG.search(target)
            while mo:
                target = self.REX_CLOTAG.sub(r"<\1/>", target)
                mo = self.REX_CLOTAG.search(target)
        if self.opt_args.analyze:
            colored_target = ""
            for (kind, value, row, column, start, end) in self.syntax.tokenize(
                    target, spaces=True):
                if kind in ("name",):
                    colored_target += "\033[31m" + value + "\033[0m"
                elif kind in ("text",):
                    colored_target += "\033[32m" + value + "\033[0m"
                elif kind in ("code", "uncode"):
                    colored_target += "\033[33m" + value + "\033[0m"
                elif kind in ("rem_eol", "remark"):
                    colored_target += "\033[34m" + value + "\033[0m"
                elif kind in ("op_lparen",
                              "op_rparen",
                              "op_lbracket",
                              "op_rbracket",
                              "op_lbrace",
                              "op_rbrace",
                              "assign",
                              "operator",):
                    colored_target += "\033[36m" + value + "\033[0m"
                elif kind in ("nl", "s"):
                    if self.syntax.is_open_stmt() and kind == "nl":
                        colored_target += "␤"
                    colored_target += value
                else:
                    colored_target += "\033[37m" + value + "\033[0m"
            target = colored_target
        return target

    def get_noupdate_property(self, stmtno):
        if "noupdate" in self.statements[stmtno]:
            x = re.search("noupdate *=\"(0|1|True|False)\"", self.statements[stmtno])
            return self.statements[stmtno][x.start(): x.end()]
        return ""

    def match_ignore_line(self, stmtno):
        return True, 0

    def match_found_api(self, stmtno):
        if re.match(r"^ @*api\.", self.statements[stmtno]):
            if re.match(r"^ @*api\.multi", self.statements[stmtno]):
                self.api_multi = True
        else:
            self.api_multi = False
        return False, 0

    def sort_from_odoo_import(self, stmtno):
        # Sort import
        mo = self.re_match(r"(from (odoo|openerp) import )([\w, ]+)",
                           self.statements[stmtno])
        if mo:
            self.statements[stmtno] = mo.groups()[0] + ", ".join(
                sorted([k.strip() for k in mo.groups()[-1].split(",")])) + "\n"
        return False, 0

    def match_odoo_tag(self, stmtno):
        if self.to_major_version < 8 and self.ctr_tag_openerp == 0:
            property_noupdate = self.get_noupdate_property(stmtno)
            if property_noupdate:
                self.statements.insert(stmtno + 1,
                                       "    <data %s>\n" % property_noupdate)
            else:
                self.statements.insert(stmtno + 1, "    <data>\n")
            self.statements[stmtno] = "<openerp>\n"
            self.ctr_tag_openerp += 1
        else:
            self.ctr_tag_odoo += 1
        return True, 0

    def match_openerp_tag(self, stmtno):
        if self.to_major_version >= 8 and self.ctr_tag_odoo == 0:
            self.statements[stmtno] = "<odoo>\n"
            self.ctr_tag_odoo += 1
        else:
            self.ctr_tag_openerp += 1
        return True, 0

    def match_data_tag(self, stmtno):
        offset = 0
        if self.ctr_tag_data == 0:
            property_noupdate = self.get_noupdate_property(stmtno)
            if self.ctr_tag_odoo == 1:
                del self.statements[stmtno]
                offset = -1
                if property_noupdate:
                    stmtno = 0
                    while not self.re_match("^ *<odoo", self.statements[stmtno]):
                        stmtno += 1
                    self.statements[stmtno] = "<odoo %s>\n" % property_noupdate
            else:
                self.ctr_tag_data += 1
        else:
            self.ctr_tag_data += 1
        return True, offset

    def match_data_endtag(self, stmtno):
        offset = 0
        if self.ctr_tag_data == 0 and self.ctr_tag_odoo == 1:
            del self.statements[stmtno]
            offset = -1
        else:
            self.ctr_tag_data -= 1
        return True, offset

    def match_openerp_endtag(self, stmtno):
        if self.ctr_tag_openerp == 0 and self.ctr_tag_odoo == 1:
            self.statements[stmtno] = "</odoo>"
            self.ctr_tag_odoo -= 1
        else:
            self.ctr_tag_openerp -= 1
        return True, 0

    def match_odoo_endtag(self, stmtno):
        offset = 0
        if self.ctr_tag_odoo == 0 and self.ctr_tag_openerp == 1:
            self.statements[stmtno] = "</openerp>"
            self.ctr_tag_openerp -= 1
            if self.ctr_tag_data:
                self.statements.insert(stmtno, "    </data>\n")
                self.ctr_tag_data -= 1
                offset = 1
        else:
            self.ctr_tag_odoo -= 1
        return True, offset

    def match_utf8(self, stmtno):
        offset = 0
        if (
            (self.python_future
             or self.opt_args.ignore_pragma
             or (self.opt_args.python and self.py23 == 2))
            and self.utf8_lineno < 0
        ):
            self.utf8_lineno = stmtno
        else:
            del self.statements[stmtno]
            offset = -1
        return False, offset

    def match_end_utf8(self, stmtno):
        offset = 0
        if self.utf8_lineno < 0 and (self.py23 == 2 or self.python_future):
            if not self.opt_args.ignore_pragma:
                self.statements.insert(stmtno, "# -*- coding: utf-8 -*-\n")
                self.utf8_lineno = stmtno
        return False, offset

    def match_lint(self, stmtno):
        offset = 0
        if self.utf8_lineno >= 0:
            del self.statements[self.utf8_lineno]
            self.utf8_lineno = -1
            offset = -1
        return False, offset

    def match_version(self, stmtno):
        if self.opt_args.from_version and self.opt_args.to_version:
            self.statements[stmtno] = re.sub(
                r"\b(" + self.from_version.replace(
                    ".", r"\.") + r")(\.[0-9]+(?:\.[0-9]+)*)\b",
                self.package.release + r"\2",
                self.statements[stmtno])
        return False, 0

    def cvt_attrs_formula(self, stmtno):
        mo = re.search("attrs=\".*?\"", self.statements[stmtno])
        if not mo:
            self.raise_error(
                "Internal error: attrs not found in %s!" % self.statements[stmtno])
        source = mo.group().split("=", 1)[1][1: -1].strip()
        unplugged = MigrateFile(self.opt_args, None, language="python", source=source)
        formula = expr = and_or = pos = ""
        state = ""
        # states: {property:[query(expr)]}
        for (kind, value, row, column, start, end) in unplugged.tokenized:
            if kind in ("op_lbracket", "op_rbracket"):
                continue
            if kind == "op_lbrace":
                state = "property"
            elif state == "property":
                if kind == "text":
                    formula = value[1: -1]
                elif value == ":":
                    formula += "=\""
                    state = ""
            elif not state:
                if value == "'|'":
                    and_or = "or"
                elif kind == "op_lparen":
                    expr = ""
                    state = "expr"
                    pos = "left"
                elif kind == "op_rparen":
                    formula += expr
                    if and_or:
                        formula += " " + and_or + " "
                        and_or = ""
                elif kind == "op_rbrace":
                    formula += "\""
                    self.statements[stmtno] = self.statements[stmtno].replace(
                        mo.group(), formula)
                    formula = expr = and_or = pos = ""
            elif state == "expr":
                if value == ",":
                    pass
                elif pos == "left":
                    expr = value[1: -1]
                    pos = "op"
                elif pos == "op":
                    op = value[1: -1]
                    if op == "=":
                        op = "=="
                    expr += " %s " % op
                    pos = "right"
                elif pos == "right":
                    expr += value
                    pos = state = ""
                    if expr.endswith(" == False"):
                        expr = "not " + expr.replace(" == False", "")
        return False, 0

    def cvt_formula_attrs(self, stmtno):
        mo = re.search("(invisible|readonly)=\".*?\"", self.statements[stmtno])
        if not mo:
            self.raise_error(
                "Internal error: invisible|readonly not found in %s!"
                % self.statements[stmtno])
        attr, source = mo.group().split("=", 1)
        source = source[1: -1].strip()
        unplugged = MigrateFile(self.opt_args, None, language="python", source=source)
        expr = and_or = pos = ""
        formula = "attrs="
        state = ""
        for (kind, value, row, column, start, end) in unplugged.tokenized:
            if kind == "op_lbrace":
                formula += "\""
            if state == "property":
                if kind == "text":
                    formula = value[1: -1]
                elif value == ":":
                    formula += "=\""
                    state = ""
            elif not state:
                if value == "'|'":
                    and_or = "or"
                elif kind == "op_lparen":
                    expr = ""
                    state = "expr"
                    pos = "left"
                elif kind == "op_rparen":
                    formula += expr
                    if and_or:
                        formula += " " + and_or + " "
                        and_or = ""
                elif kind == "op_rbracket":
                    formula += "\""
                    self.statements[stmtno] = self.statements[stmtno].replace(
                        mo.group(), formula)
                    formula = expr = and_or = pos = ""
            elif state == "expr":
                if value == ",":
                    pass
                elif pos == "left":
                    expr = value[1: -1]
                    pos = "op"
                elif pos == "op":
                    op = value[1: -1]
                    if op == "=":
                        op = "=="
                    expr += " %s " % op
                    pos = "right"
                elif pos == "right":
                    expr += value
                    pos = state = ""
                    if expr.endswith(" == False"):
                        expr = "not " + expr.replace(" == False", "")
        return False, 0

    def comparable_version(self, version):
        return ".".join(["%03d" % int(x) for x in version.split(".")])

    def trace_debug(self, key, stmtno, action):
        if self.opt_args.debug and key:
            self.statements[stmtno] += " # " + key + "/" + action

    def assign_stmtno(self, stmtno, value):
        if value.startswith("+"):
            new_lineno = stmtno + int(value[1:])
            if new_lineno >= (len(self.statements) - 1):
                new_lineno = len(self.statements) - 1
        elif value.startswith("-"):
            new_lineno = stmtno - int(value[1:])
            if new_lineno < 0:
                new_lineno = 0
        elif value in ("1.2", "1.3", "1.4", "1.5"):
            new_lineno = 0
            if self.statements[new_lineno].startswith("#!"):
                new_lineno += 1
            if value != "1.2" and re.search(
                    r"# (flake8: noqa|pylint: skip-file)", self.statements[new_lineno]):
                new_lineno += 1
            if value not in ("1.2", "1.3") and re.match(
                    r"# -\*- coding[:=] utf-8 -\*-", self.statements[new_lineno]):
                new_lineno += 1
            if value in ("1.4", "1.5"):
                while re.match("#", self.statements[new_lineno]):
                    new_lineno += 1
            if value == "1.5" and re.search(
                    r"\bimport\b", self.statements[new_lineno]):
                new_lineno += 1
        else:
            new_lineno = int(value)
            if new_lineno >= (len(self.statements) - 1):
                new_lineno = len(self.statements) - 1
        return new_lineno

    def update_line(self, subrule, regex, stmtno, key=None):
        """Update current line self.statements[stmtno]
        Rule is (action, params, ...)
        action may be: "/?([+-][0-9.]+)?(s|d|i|a|$|=|mv)"
        Action digest:
        's': substitute REGEX REPLACE_TEXT
        'd': delete line; stop immediately rule processing and re-read the line
        'i': insert line before current line
        'a': append line after current line
        '$': execute FUNCTION
        '+': set trigger TRIGGER_NAME (from 1st group of matching regex)
        '-': reset trigger TRIGGER_NAME
        '=': execute python code
        'mv': move current line to new position

        Args:
            stmtno (int): line number
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
            regex = self.match_rule(args[0], self.statements[stmtno], partial=True)
            if regex:
                self.statements[stmtno] = re.sub(regex,
                                                 args[1] % self.__dict__,
                                                 self.statements[stmtno])
                self.trace_debug(key, stmtno, action)
            return False, 0
        elif action == "d":
            if self.opt_args.debug and key:
                self.statements[stmtno] = "# " + key + "/" + action
            else:
                # delete current line
                del self.statements[stmtno]
            return True, -1
        elif action == "i":
            # insert line before current with params[0] or by params[1]
            new_lineno = self.assign_stmtno(
                stmtno, args[1]) if len(args) > 1 and args[1] else stmtno
            args[0] += "\n"
            self.statements.insert(new_lineno, args[0] % self.__dict__)
            self.trace_debug(key, stmtno, action)
            return True, -1 if new_lineno == stmtno else 0
        elif action == "a":
            # append line after current with params[0]
            args[0] += "\n"
            self.statements.insert(stmtno + 1, args[0] % self.__dict__, )
            self.trace_debug(key, stmtno + 1, action)
            return False, 0
        elif action == "$":
            if not hasattr(self, args[0]):
                self.raise_error("Function %s not found!" % args[0])
                return False, 0
            do_break, offset = getattr(self, args[0])(stmtno)
            self.trace_debug(key, stmtno, action + args[0] + "()")
            return do_break, offset
        elif action == "+":
            if not args:
                self.raise_error("Action set trigger (+) w/o trigger name!")
                return False, 0
            x = re.match(
                self.get_mig_rules()[key]["match"], self.statements[stmtno]
            ) if "match" in self.get_mig_rules()[key] else None
            if x and x.groups():
                self.set_trigger(args[0], x.groups()[0])
                self.trace_debug(key, stmtno, action + args[0])
            elif len(args) > 1:
                if re.match("[+-][0-9]+", args[1]):
                    self.set_trigger(args[0], int(args[1]) + getattr(self, args[0], 0))
                else:
                    self.set_trigger(args[0], args[1] % self.__dict__)
                self.trace_debug(key, stmtno, action + args[0] + args[1])
            else:
                self.set_trigger(args[0], True)
                self.trace_debug(key, stmtno, action + "True")
            return False, 0
        elif action == "-":
            if not args:
                self.raise_error("Action reset trigger (+) w/o trigger name!")
                return False, 0
            self.set_trigger(args[0], False)
            self.trace_debug(key, stmtno, action + args[0])
            return False, 0
        elif action == "=":
            try:
                eval(args[0], self.__dict__)
                self.trace_debug(key, stmtno, action + args[0])
            except BaseException as e:
                self.raise_error("Invalid expression %s" % args[0])
                self.raise_error(e)
            return False, 0
        elif action == "mv":
            # mv line (+#|-#|1.2|1.3|#)
            if not args:
                self.raise_error("Invalid expression mv")
                return False, 0
            new_lineno = self.assign_stmtno(stmtno, args[0])
            if new_lineno != stmtno:
                line = self.statements[stmtno]
                del self.statements[stmtno]
                self.statements.insert(new_lineno, line)
            return False, 0
        else:
            self.raise_error("Invalid rule action %s" % action)
        return False, 0

    def do_process_source(self):
        if self.opt_args.git_merge_conflict:
            return self.solve_git_merge()
        if self.opt_args.test_res_msg:
            return self.do_upgrade_res_msg()
        if self.file_action in ("no", "rm"):
            return self.do_copy_file()
        else:
            self.analyze_source()
            self.do_upgrade_license_comment()
            return self.do_upgrade_file()
        return False

    def do_copy_file(self):
        return False

    def do_upgrade_license_comment(self):
        License = license_mgnt.License()
        for stmtno, ln in enumerate(self.statements):
            if not self.statements[stmtno]:
                continue
            if not self.statements[stmtno].startswith("#"):
                break
            _, _, _, _, old_years = License.extract_info_from_line(
                self.statements[stmtno])
            _, _, _, _, cur_years = License.extract_info_from_line(
                self.statements[stmtno],
                odoo_major_version=self.to_major_version,
                force_from=True if self.opt_args.copyright_check > 1 else False)
            if old_years != cur_years:
                self.statements[stmtno] = self.statements[stmtno].replace(
                    old_years, cur_years, 1)
        return True

    def do_upgrade_file(self):
        def count_unbalanced(ln, left, right, comment_char="#"):
            ln = qsplit(ln, comment_char)[0]
            return len(qsplit(ln, left)) - (len(qsplit(ln, right)) if right else 1)

        if not self.file_action and self.mig_rules:
            stmtno = 0
            self.open_stmt = False
            self.imported = []
            self.try_indent = -1
            self.indent = self.stmt_indent = ""
            rex_import = re.compile(r"^ *(from [^\s]+)? import ")
            while stmtno < len(self.statements):
                self.first_line = stmtno == 0
                mo = self.syntax.re_s and self.syntax.re_s.match(
                    self.statements[stmtno])
                if mo:
                    pos = mo.end()
                    self.indent = self.statements[stmtno][mo.start(): mo.end()]
                else:
                    pos = 0
                    self.indent = ""
                self.dedent = self.indent < self.stmt_indent
                if pos < len(self.statements[stmtno]):
                    if (
                        self.syntax.re_rem_eol
                        and not self.syntax.re_rem_eol.match(self.statements[stmtno],
                                                             pos)
                    ):
                        self.header = False
                        mo = rex_import.match(self.statements[stmtno], pos)
                        if mo:
                            self.transition_stage = (
                                "import" if self.transition_stage == "import"
                                else self.stage)
                            self.stage = "import"
                            pkgs = self.statements[stmtno][mo.end():].split(
                                "#")[0].strip()
                            for pkg in pkgs.split(","):
                                pkg = pkg.strip()
                                if pkg not in self.imported:
                                    self.imported.append(pkg)
                            stmtno = self.apply_rules_on_item(
                                self.statements[stmtno], stmtno=stmtno)
                        elif (
                                self.stage != "import"
                                and self.transition_stage != "import"
                                and not self.imported
                        ):
                            self.transition_stage = self.stage
                            self.stage = "import"
                            prior_stmtno = stmtno
                            stmtno = self.apply_rules_on_item(
                                self.statements[stmtno], stmtno=stmtno)
                            if re.match(" *def ", self.statements[prior_stmtno]):
                                self.transition_stage = self.stage
                                self.stage = "function_body"
                            elif re.match(" *class ", self.statements[prior_stmtno]):
                                self.transition_stage = self.stage
                                self.stage = "class_body"
                            elif re.match("^ *try:", self.statements[prior_stmtno]):
                                self.try_indent = len(self.indent)
                            elif len(self.indent) <= self.try_indent:
                                self.try_indent = -1
                        else:
                            stmtno = self.apply_rules_on_item(
                                self.statements[stmtno], stmtno=stmtno)
                    else:
                        stmtno = self.apply_rules_on_item(
                            self.statements[stmtno], stmtno=stmtno)
                else:
                    stmtno = self.apply_rules_on_item(
                        self.statements[stmtno], stmtno=stmtno)
                self.stmt_indent = self.indent
        return True

    def do_upgrade_res_msg(self):
        if not self.opt_args.test_res_msg:
            return False
        test_res_msg = self.opt_args.test_res_msg.replace("\\n", "\n")
        if test_res_msg.startswith('"') or test_res_msg.startswith("'"):
            test_res_msg = test_res_msg[1: -1]
        if not test_res_msg.endswith("\n"):
            test_res_msg += "\n"
        mo = re.search("[0-9]+ TestPoint", test_res_msg)
        # if mo and "\n" in test_res_msg:
        #     left_mesg, suppl = test_res_msg.split("\n", 1)
        #     right_mesg = left_mesg[mo.end() - 10:]
        #     ctr = int(left_mesg[mo.start():].split(" ", 1)[0])
        #     left_mesg = left_mesg[: mo.start()]
        #     for ln in suppl.split("\n"):
        #         mo = re.search("[0-9]+ TestPoint", ln)
        #         if mo:
        #             ctr += int(ln[mo.start(): mo.end() - 10])
        #     test_res_msg = left_mesg + str(ctr) + right_mesg

        last_date = None
        found_list = False
        title_lineno = qua_lineno = i_start = i_end = -1
        date_limit = (
            datetime.strptime(self.opt_args.test_res_msg_range, "%Y-%m-%d")
            if self.opt_args.test_res_msg_range else (datetime.now() - timedelta(20))
        )
        for stmtno, ln in enumerate(self.statements):
            if ln == "\n":
                if found_list:
                    break
                continue
            if re.match(r"[0-9]+\.[0-9]+\.[0-9]+.*\([0-9]+", ln):
                if not last_date:
                    mo = re.search(r"\([0-9]{4}-[0-9]{2}-[0-9]{2}\)", ln)
                    if not mo:
                        print(red("Invalid changelog line: ") + ln)
                        break
                    i_start = mo.start() + 1
                    i_end = mo.end() - 1
                    last_date = datetime.strptime(ln[i_start: i_end], "%Y-%m-%d")
                    title_lineno = stmtno
                    continue
            if qua_lineno < 0 and re.match(r"['\"]*\* *\[QUA\]", ln):
                qua_lineno = stmtno
            if last_date and ln.startswith("*"):
                found_list = True
        if last_date and last_date >= date_limit and found_list:
            if qua_lineno >= 0:
                self.statements[qua_lineno] = test_res_msg
            else:
                if stmtno >= len(self.statements) or self.statements[stmtno]:
                    stmtno -= 1
                self.statements.insert(stmtno, test_res_msg)
                if not self.opt_args.dry_run:
                    with open(self.fqn, "w", encoding="utf-8") as fd:
                        fd.write("\n".join(self.statements))
            self.statements[title_lineno] = (
                self.statements[title_lineno][:i_start]
                + datetime.strftime(datetime.now(), "%Y-%m-%d")
                + self.statements[title_lineno][i_end:])
        return True

    def solve_git_merge(self):
        state = "both"
        state_lev = 0
        stmtno = 0
        while stmtno < len(self.statements):
            ln = self.statements[stmtno]
            if ln.startswith("<<<<<<<"):
                state = "left"
                state_lev += 1
                del self.statements[stmtno]
            elif ln.startswith(">>>>>>>"):
                state = "right"
                state_lev += 1
                del self.statements[stmtno]
            elif ln.startswith("=======") and state != "both":
                state_lev -= 1
                if not state_lev:
                    state = "both"
                del self.statements[stmtno]
            elif state not in ("both", self.opt_args.git_merge_conflict):
                del self.statements[stmtno]
            else:
                stmtno += 1
        return True

    def format_file(self, out_fqn):
        prettier_config = False
        black_config = False
        path = pth.dirname(out_fqn)
        out_fqn_dir_path = path
        while not prettier_config and not black_config:
            if pth.isfile(pth.join(path, ".pre-commit-config.yaml")):
                black_config = pth.join(path, ".pre-commit-config.yaml")
            if pth.isfile(pth.join(path, ".prettierrc.yml")):
                prettier_config = pth.join(path, ".prettierrc.yml")
            if path == os_realpath("~") or path == "/":
                break
            path = pth.dirname(path)
        if self.language == "xml":
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
        elif self.language in ("python", "manifest-python"):
            if self.language == "manifest-python" and self.opt_args.to_version:
                curcwd = os.getcwd()
                os.chdir(out_fqn_dir_path)
                opts = "-Rw -lmodule -Podoo"
                if self.opt_args.from_version and self.opt_args.to_version:
                    opts += " -F%s -b%s" % (self.opt_args.from_version,
                                            self.opt_args.to_version)
                if self.git_orgid:
                    opts += " -G%s" % self.git_orgid
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

    def print_output(self):
        print()
        print('👽 %s' % self.fqn)
        print(self.join_source_statements())
        print("---------------------------------------------------------------------")

    def close(self):
        if is_device(self.opt_args.output):
            out_fqn = self.opt_args.output
        elif self.opt_args.output:
            if pth.isdir(self.opt_args.output):
                root = [x for x in self.opt_args.path
                        if self.fqn.startswith(x)]
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
        elif self.opt_args.analyze:
            out_fqn = "--"
        else:
            out_fqn = pth.join(pth.dirname(self.fqn), self.out_fn)
        new_source = self.join_source_statements()
        if not self.file_action and (
                self.opt_args.lint_anyway
                or out_fqn != self.fqn
                or self.source != new_source
        ):
            if not is_device(out_fqn) and not self.opt_args.in_place:
                bakfile = '%s.bak' % out_fqn
                if pth.isfile(bakfile):
                    os.remove(bakfile)
                if pth.isfile(out_fqn):
                    os.rename(out_fqn, bakfile)
            if not self.opt_args.dry_run:
                if is_device(out_fqn):
                    self.print_output()
                else:
                    with open(out_fqn, "w", encoding="utf-8") as fd:
                        fd.write(new_source)
            if not is_device(out_fqn):
                if not self.opt_args.no_parse_with_formatter:
                    self.format_file(out_fqn)
                if self.opt_args.verbose > 0:
                    print('👽 %s' % out_fqn)
        elif self.file_action == "ply":
            if not pth.exists(out_fqn) and not is_device(out_fqn):
                cmd = "cp %s %s" % (self.fqn, out_fqn)
                z0lib.os_system(cmd, dry_run=self.opt_args.dry_run)
                if self.opt_args.verbose > 0:
                    print('👽 %s' % out_fqn)
        elif (
                self.file_action == "no"
                and self.fqn != out_fqn
                and not is_device(out_fqn)
        ):
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


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Beautiful source file", epilog="© 2021-2025 by SHS-AV s.r.l."
    )
    parser.add_argument(
        '-A', '--analyze',
        action='store_true',
        help='analyze source file(s)',
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
        help="python version, format #.##, 2+3 use future"
    )
    parser.add_argument(
        '-l', '--list-rules',
        action='count',
        default=0,
        help='list rule groups (-ll list with rules too, -lll full list)')
    parser.add_argument(
        '--list-syntax',
        action='store_true',
        help='list language syntax rules')
    parser.add_argument(
        "-n",
        "--dry-run",
        help="do nothing (dry-run)",
        action="store_true",
    )
    parser.add_argument('-o', '--output')
    parser.add_argument('--no-output', action='store_const', dest='output', const='--')
    parser.add_argument('-P', '--package-name')
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
    parser.add_argument(
        '--test-res-msg-range',
        help='Date limit to join test result message'
    )
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument(
        '-w',
        '--no-parse-with-formatter',
        action='store_true',
        help="do nor execute black or prettier on modified files",
    )
    parser.add_argument(
        '-y', '--assume-yes',
        action='store_true',
        help='force target path creation with different base name'
    )
    parser.add_argument(
        '--add-rule-group',
        default='.arcangelo',
        help='Add rule group form file, default is .arcangelo.yml',
    )
    parser.add_argument('path', nargs="*")
    opt_args = parser.parse_args(cli_args)

    if (
            opt_args.git_merge_conflict
            and opt_args.git_merge_conflict not in ("left", "right")
    ):
        print("Invalid value for switch --git-merge-conflict")
        print("Please use --git-merge-conflict=left or --git-merge-conflict=right")
        return 3
    if opt_args.analyze and opt_args.in_place:
        print("Switches --analyze and --in-place are mutually exclusive")
        return 3
    if opt_args.debug and opt_args.in_place:
        print("Switches --debug and --in-place are mutually exclusive")
        return 3

    sts = 0
    if opt_args.list_rules > 0:
        MigrateEnv(opt_args).list_rules()
        return sts
    elif opt_args.list_syntax:
        MigrateEnv(opt_args).list_syntax()
        return sts
    if not opt_args.path:
        sys.stderr.write('No path supplied!\n')
        return 2
    if (
        opt_args.output
        and not is_device(opt_args.output)
        and not pth.isdir(opt_args.output)
        and not pth.isdir(pth.dirname(opt_args.output))
    ):
        sys.stderr.write(
            'Path %s does not exist!\n' % pth.dirname(opt_args.output))
        return 2

    for path in opt_args.path:
        path = os_realpath(path)
        if pth.isdir(path):
            migrate_env = MigrateEnv(opt_args)
            if (
                not migrate_env.opt_args.assume_yes
                and migrate_env.opt_args.output
                and not is_device(migrate_env.opt_args.output)
                and pth.isdir(migrate_env.opt_args.output)
                and pth.basename(path) != pth.basename(migrate_env.opt_args.output)
                and migrate_env.opt_args.from_version
                and migrate_env.opt_args.to_version
                and migrate_env.opt_args.from_version != migrate_env.opt_args.to_version
            ):
                migrate_env.raise_error(
                    'Target path %s conflicts with source path %s for migration!!\n'
                    % (migrate_env.opt_args.output, path)
                )
                return 2
            if (
                migrate_env.opt_args.output
                and not is_device(migrate_env.opt_args.output)
                and not pth.isdir(migrate_env.opt_args.output)
            ):
                os.makedirs(migrate_env.opt_args.output)
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
                    fqn = os_realpath(pth.join(root, fn)) + "/"
                    migrate_env.apply_rules_on_item(fqn)
                for fn in files:
                    fqn = os_realpath(pth.join(root, fn))
                    sts = MigrateFile(opt_args, fqn).process_file()
                    if sts:
                        break
        elif pth.isfile(path):
            sts = MigrateFile(opt_args, path).process_file()
        else:
            sys.stderr.write('Path %s does not exist!\n' % path)
            sts = 2
        if sts:
            break
    return sts


if __name__ == "__main__":
    exit(main())
