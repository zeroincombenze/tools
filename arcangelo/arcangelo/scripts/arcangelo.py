#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from io import open
import sys
import os
import os.path as pth
from datetime import datetime
import argparse
import re
import lxml.etree as ET
import yaml
import mimetypes

from pygments.util import shebang_matches
from python_plus import _b, _u, qsplit
from z0lib import z0lib
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
try:
    from . import license_mgnt
except ImportError:  # pragma: no cover
    import license_mgnt

__version__ = "2.1.0"

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


def get_config_path(fn, is_config=False):
    items = [pth.dirname(pth.abspath(pth.expanduser(__file__)))]
    if is_config:
        items.append("config")
    items.append(fn)
    return pth.join(*items)


class Syntax(object):
    """The class syntax manages the rules to parse source of a specific language.
    Syntax rules are grouped by states; i.e. after comment delimiter usual parsing is
    broken. Some delimiters can shift from a state to another.
    A language can have as many as possible states; some common states are named
    globally.
    Globals states are:
        - "code": code parsing (initial state for almost languages)
        - "rem_eol": comment until end of line
        - "remark": multi line comment
        - "mtext": multi line text (initial state for xml/html)
        - "pre": preprocessor (c language)

    Every state can manages multiple items, every item has the own parsing rule;
    i.e. for object name regex rule is "[a-zA-Z_][a-zA-Z0-9]*".
    A language state can have as many as possible items; some common items are name
    globally.
    Global names are:
        - "name": object or variable name
        - "text": text constant
        - "mtext": multi line text constant
        - "int": integer constant
        - "float" floating constant
    When name is in states, system switches state, so state name contains just the
    token to start new state; i.e. python mtext is triple quotes.
    """

    def __init__(self, language):
        config = ConfigParser.ConfigParser()
        config_fqn = get_config_path(language + ".conf", is_config=True)
        if not pth.isfile(config_fqn):
            language = "unknown"
            config_fqn = get_config_path(language + ".conf", is_config=True)
        config.read(config_fqn)
        if not config.has_section(language):
            raise SyntaxError("File %s w/o section %s" % (config_fqn, language))
        self.states = config.get(language, "states").split(",")
        self.syntax_rules = {}
        self.tok_regex = {}
        shebang = False
        for state in self.states:
            self.syntax_rules[state] = {}
            magic_names = []
            if not shebang:
                self.syntax_rules[state]["shebang"] = re.compile("#![^\n]*")
                shebang = True
            for (key, regex) in config.items(state):
                if key == "magic_names":
                    magic_names = [x.strip() for x in regex.split(",")]
                    continue
                self.syntax_rules[state][key] = re.compile(regex)
            for name in ("nl", "s", "gather"):
                if name == "nl" and name not in self.syntax_rules[state].keys():
                    self.syntax_rules[state]["nl"] = re.compile(r"\n")
                elif name == "s" and name not in self.syntax_rules[state].keys():
                    self.syntax_rules[state]["s"] = re.compile(r"\s+")
                elif name == "gather" and name not in self.syntax_rules[state].keys():
                    if len(self.syntax_rules[state]) == 1:
                        self.syntax_rules[state]["gather"] = re.compile(".*?" + list(
                            self.syntax_rules[state].values())[0].pattern)
                    else:
                        self.syntax_rules[state]["gather"] = re.compile(".")

    def get_next_mo(self, source):
        if self.pos < len(source):
            for (kind, rex) in self.syntax_rules[self.state].items():
                mo = rex.match(source, self.pos)
                if mo:
                    return kind, mo
        return None, None

    def action_nl(self, mo):
        self.lineno += 1
        if (self.parens + self.brackets + self.brackets + self.quotes) == 0:
            self.newline_pos.append(mo.end())

    def tokenize(self, source):
        self.state = self.states[0]
        self.pos = 0
        self.lineno = 1
        self.pos = 0
        self.parens = 0
        self.brackets = 0
        self.braces = 0
        self.quotes = 0
        self.newline_pos = [0]
        while self.pos < len(source):
            kind, mo = self.get_next_mo(source)
            value = mo.group()
            start = mo.start() - self.pos
            end = mo.end() - self.pos
            if start < 0 or end <= 0:
                break
            if kind == "shebang":
                if self.pos != 0:
                    continue
                for language in ("python", ):
                    if language in value and self.language != language:
                        self.language = language
                        if "python3" in value:
                            self.python_version = DEFAULT_PYTHON_VER
                        else:
                            self.python_version = "2.7"
                        self.py23 = int(self.python_version.split(".")[0])
                        yield (kind, value, self.lineno, start, end)
                self.pos = mo.end()
                continue
            self.pos = mo.end()
            if kind in self.states:
                self.state = kind
            elif kind == "nl":
                self.action_nl(mo)
                continue
            elif kind == "s":
                continue
            elif kind == "gather":
                if self.syntax_rules[self.state][kind].pattern != ".":
                    for (kind2, rex) in self.syntax_rules[self.state].items():
                        mo2 = rex.search(source, self.pos)
                        if mo2:
                            self.state = kind2
                            self.pos = mo2.start() - 1
                            break
                continue
            elif kind == "op_lparen":
                self.parens += 1
            elif kind == "op_rparen":
                self.parens -= 1
            yield (kind, value, self.lineno, start, end)


class MigrateMeta(object):

    def raise_error(self, message):   # pragma: no cover
        sys.stderr.write(message)
        sys.stderr.write("\n")
        self.sts = 3

    def init_env_file(self, migrate_env=None):
        if migrate_env:
            for kk in (
                    "mime",
                    "language",
                    "from_version",
                    "to_version",
                    "from_major_version",
                    "to_major_version",
                    "python_future",
                    "set_python_future",
                    "python_version",
                    "py23",
                    "opt_args",
                    "file_action",
            ):
                setattr(self, kk, getattr(migrate_env, kk))
        self.header = True
        self.property_noupdate = False
        self.ctr_tag_data = 0
        self.ctr_tag_odoo = 0
        self.ctr_tag_openerp = 0
        self.classname = ""
        self.indent = ""
        self.in_import = False
        self.UserError = False
        self.utf8_lineno = -1
        self.lines_2_rm = []
        self.file_action = ""
        self.py23 = int(self.python_version.split(".")[0])
        self.first_line = False
        self.stage = "header"
        self.transition_stage = ""
        self.try_indent = -1
        self.force = self.opt_args.force
        for trigger in ("first_line", "migrate_multi", "backport_multi"):
            setattr(self, trigger, False)
        self.final = False
        self.imported = []
        self.mig_rules = {}
        self.pass1_rules = {}

    def get_pyver_4_odoo(self, odoo_ver):
        odoo_major = int(odoo_ver.split(".")[0])
        if odoo_major <= 10:
            pyver = "2.7"
        else:
            pyver = "3.%d" % (int((odoo_major - 9) / 2) + 6)
        return pyver

    def populate_default_rule_categ(self, language):
        self.rule_categ.append("globals_" + language)
        if language in ("python", "manifest-python"):
            self.rule_categ.append("globals_py%s" % self.py23)
            if self.set_python_future:
                self.rule_categ.append("globals_future")

        if self.opt_args.git_orgid:
            self.rule_categ.append("%s-%s_%s" % (
                self.opt_args.package_name,
                self.opt_args.git_orgid,
                language))

        self.rule_categ.append("%s_%s" % (self.opt_args.package_name, language))

        if language == "python":
            if self.python_future or self.set_python_future:
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
                fn % (self.opt_args.package_name, language, self.to_major_version))
            if self.opt_args.git_orgid:
                self.rule_categ.append("%s-%s_%s_%s" % (
                    self.opt_args.package_name,
                    self.opt_args.git_orgid,
                    language,
                    self.to_major_version))
        elif self.from_major_version and self.to_major_version:
            fn = "%s_%s_%s"
            if self.from_major_version < self.to_major_version:
                # Migration to newer Odoo version
                from_major_version = self.from_major_version - 1
                to_major_version = from_major_version + 1
                while to_major_version <= self.to_major_version:
                    self.rule_categ.append(
                        fn % (self.opt_args.package_name, language, to_major_version))
                    if self.opt_args.git_orgid:
                        self.rule_categ.append("%s-%s_%s_%s" % (
                            self.opt_args.package_name,
                            self.opt_args.git_orgid,
                            language,
                            to_major_version))
                    from_major_version += 1
                    to_major_version = from_major_version + 1
            elif self.from_major_version > self.to_major_version:
                # Backport to older Odoo version
                from_major_version = self.from_major_version - 1
                to_major_version = from_major_version + 1
                while to_major_version >= self.to_major_version:
                    self.rule_categ.append(
                        fn % (self.opt_args.package_name, language, to_major_version))
                    if self.opt_args.git_orgid:
                        self.rule_categ.append("%s-%s_%s_%s" % (
                            self.opt_args.package_name,
                            self.opt_args.git_orgid,
                            language,
                            to_major_version))
                    from_major_version -= 1
                    to_major_version = from_major_version + 1

    def detect_mig_rules(self, language=None):
        # languafe: (path|xml|python)
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
                elif self.from_major_version > self.to_major_version:
                    nxt_ver = cur_ver + 1
                    for x in self.rule_categ:
                        if x.endswith("_%s" % nxt_ver):
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
        Current item may be a source line (with lineno) or a full qualified name"""
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
                "manifest-python": "python",
            }.get(self.mime.split("/")[1], "")
            if not self.language and self.mime.split("/")[0] in ("image",):
                self.language = self.mime.split("/")[0]
            if not self.language:
                self.language = self.mime.split("/")[1]
        else:
            next_item = stmtno + 1
        do_continue = False
        self.lineno = stmtno
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


class MigrateEnv(MigrateMeta):
    """This class manages the migration environment
    Rules mime is "path"
    """
    def __init__(self, opt_args):
        if opt_args.path:
            opt_args.path = [pth.expanduser(p) for p in opt_args.path]
        if opt_args.output:
            opt_args.output = pth.expanduser(opt_args.output)
        self.out_fn = None
        self.mime = None
        self.language = "unknown"

        self.set_python_future = self.python_future = False
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
            opt_args.python = self.get_pyver_4_odoo(opt_args.to_version)
        if opt_args.python == "2+3":
            if opt_args.package_name == "odoo":
                self.python_version = self.get_pyver_4_odoo(opt_args.to_version)
            else:
                self.python_version = DEFAULT_PYTHON_VER
            self.set_python_future = True
        elif opt_args.python:
            self.python_version = opt_args.python
        else:
            self.python_version = DEFAULT_PYTHON_VER
            if opt_args.package_name == "pypi":
                self.set_python_future = True
        self.opt_args = opt_args
        self.init_env_file()
        self.detect_mig_rules(language="path")
        for rule_cat in self.rule_categ:
            self.load_config(rule_cat, prio=0)

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
        elif action in ("no", "rm", "new"):
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

    def run_sub_rules(self, rule, regex, item, dummy, next_dummy, key=None):
        do_continue = do_break = False
        for subrule in rule["do"]:
            do_break = self.action_on_file(subrule, regex, item)
        return do_continue, do_break, dummy


class MigrateFile(MigrateMeta):
    """This class manages a file migration process.
    This class inherits some properties from Migration Environment
    Rules mime depends on file: "manifest-python", "python", "xml", "history", etc.
    """
    def __init__(self, fqn, opt_args, migrate_env):
        self.sts = 0
        self.REX_CLOTAG = re.compile(r"<((td|tr)[^>]*)> *?</\2>")
        if opt_args.verbose > 0:
            print("Reading %s ..." % fqn)
        self.fqn = fqn
        base = pth.basename(fqn)
        self.out_fn = migrate_env.out_fn or base
        self.init_env_file(migrate_env=migrate_env)
        if self.file_action in ("no", "rm", "new"):
            return
        try:
            with open(fqn, "r", encoding="utf-8") as fd:
                self.source = fd.read()
        except BaseException:
            self.source = ""
            self.file_action = "no"
            return
        self.tokenized = []
        self.syntax = Syntax(self.language)
        for (kind, value, line_num, start, end) in self.syntax.tokenize(self.source):
            if kind == "shebang":
                self.syntax = Syntax(self.language)
                continue
            self.tokenized.append((kind, value, line_num, start, end))
        self.statements = []
        ix = 0
        while ix < len(self.syntax.newline_pos):
            ix2 = ix + 1
            start = self.syntax.newline_pos[ix]
            if ix2 >= len(self.syntax.newline_pos):
                stop = len(self.source)
                if stop == start:
                    break
            stop = self.syntax.newline_pos[ix2]
            self.statements.append(self.source[start: stop])
            ix = ix2

    def init_env_file(self, migrate_env=None):
        super(MigrateFile, self).init_env_file(migrate_env=migrate_env)
        self.detect_mig_rules(language=self.language)
        prio = len(self.rule_categ) + 1
        for rule_cat in self.rule_categ:
            self.load_config(rule_cat, prio=prio)
            prio -= 1
        if not self.mig_rules:
            # No rule to process, ignore file
            self.file_action = "no"

    def analyze_source(self):
        self.pass1 = True
        self.exceptions = []
        stmtno = 0
        while stmtno < len(self.statements):
            stmtno = self.apply_rules_on_item(self.statements[stmtno], stmtno=stmtno)
        self.exceptions = ", ".join(self.exceptions) if self.exceptions else ""
        self.pass1 = False

    def get_noupdate_property(self, lineno):
        if "noupdate" in self.statements[lineno]:
            x = re.search("noupdate *=\"(0|1|True|False)\"", self.statements[lineno])
            return self.statements[lineno][x.start(): x.end()]
        return ""

    def match_ignore_line(self, lineno):
        return True, 0

    def match_found_api(self, lineno):
        if re.match(r"^ @*api\.", self.statements[lineno]):
            if re.match(r"^ @*api\.multi", self.statements[lineno]):
                self.api_multi = True
        else:
            self.api_multi = False
        return False, 0

    def sort_from_odoo_import(self, lineno):
        # Sort import
        x = self.re_match(r"(from (odoo|openerp) import )([\w, ]+)", self.statements[lineno])
        if x:
            self.statements[lineno] = x.groups()[0] + ", ".join(
                sorted([k.strip() for k in x.groups()[-1].split(",")]))
        return False, 0

    def match_odoo_tag(
        self,
        lineno,
    ):
        if self.to_major_version < 8 and self.ctr_tag_openerp == 0:
            property_noupdate = self.get_noupdate_property(lineno)
            if property_noupdate:
                self.statements.insert(lineno + 1, "    <data %s>" % property_noupdate)
            else:
                self.statements.insert(lineno + 1, "    <data>")
            self.statements[lineno] = "<openerp>"
            self.ctr_tag_openerp += 1
        else:
            self.ctr_tag_odoo += 1
        return True, 0

    def match_openerp_tag(self, lineno):
        if self.to_major_version >= 8 and self.ctr_tag_odoo == 0:
            self.statements[lineno] = "<odoo>"
            self.ctr_tag_odoo += 1
        else:
            self.ctr_tag_openerp += 1
        return True, 0

    def match_data_tag(self, lineno):
        offset = 0
        if self.ctr_tag_data == 0:
            property_noupdate = self.get_noupdate_property(lineno)
            if self.ctr_tag_odoo == 1:
                del self.statements[lineno]
                offset = -1
                if property_noupdate:
                    lineno = 0
                    while not self.re_match("^ *<odoo", self.statements[lineno]):
                        lineno += 1
                    self.statements[lineno] = "<odoo %s>" % property_noupdate
            else:
                self.ctr_tag_data += 1
        else:
            self.ctr_tag_data += 1
        return True, offset

    def match_data_endtag(self, lineno):
        offset = 0
        if self.ctr_tag_data == 0 and self.ctr_tag_odoo == 1:
            del self.statements[lineno]
            offset = -1
        else:
            self.ctr_tag_data -= 1
        return True, offset

    def match_openerp_endtag(self, lineno):
        if self.ctr_tag_openerp == 0 and self.ctr_tag_odoo == 1:
            self.statements[lineno] = "</odoo>"
            self.ctr_tag_odoo -= 1
        else:
            self.ctr_tag_openerp -= 1
        return True, 0

    def match_odoo_endtag(self, lineno):
        offset = 0
        if self.ctr_tag_odoo == 0 and self.ctr_tag_openerp == 1:
            self.statements[lineno] = "</openerp>"
            self.ctr_tag_openerp -= 1
            if self.ctr_tag_data:
                self.statements.insert(lineno, "    </data>")
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
            del self.statements[lineno]
            offset = -1
        return False, offset

    def match_end_utf8(self, lineno):
        offset = 0
        if self.utf8_lineno < 0 and (self.py23 == 2 or self.python_future):
            if not self.opt_args.ignore_pragma:
                self.statements.insert(lineno, "# -*- coding: utf-8 -*-")
                self.utf8_lineno = lineno
        return False, offset

    def match_lint(self, lineno):
        offset = 0
        if self.utf8_lineno >= 0:
            del self.statements[self.utf8_lineno]
            self.utf8_lineno = -1
            offset = -1
        return False, offset

    def match_version(self, lineno):
        if self.opt_args.from_version and self.opt_args.to_version:
            self.statements[lineno] = re.sub(
                r"\b(" + self.from_version.replace(
                    ".", r"\.") + r")(\.[0-9]+(?:\.[0-9]+)*)\b",
                self.to_version + r"\2",
                self.statements[lineno])
        return False, 0

    def comparable_version(self, version):
        return ".".join(["%03d" % int(x) for x in version.split(".")])

    def trace_debug(self, key, lineno, action):
        if self.opt_args.debug and key:
            self.statements[lineno] += " # " + key + "/" + action

    def assing_lineno(self, lineno, value):
        if value.startswith("+"):
            new_lineno = lineno + int(value[1:])
            if new_lineno >= (len(self.statements) - 1):
                new_lineno = len(self.statements) - 1
        elif value.startswith("-"):
            new_lineno = lineno - int(value[1:])
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

    def update_line(self, subrule, regex, lineno, key=None):
        """Update current line self.statements[lineno]
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
            regex = self.match_rule(args[0], self.statements[lineno], partial=True)
            if regex:
                self.statements[lineno] = re.sub(regex,
                                                 args[1] % self.__dict__,
                                                 self.statements[lineno])
                self.trace_debug(key, lineno, action)
            return False, 0
        elif action == "d":
            if self.opt_args.debug and key:
                self.statements[lineno] = "# " + key + "/" + action
            else:
                # delete current line
                del self.statements[lineno]
            return True, -1
        elif action == "i":
            # insert line before current with params[0] or by params[1]
            new_lineno = self.assing_lineno(
                lineno, args[1]) if len(args) > 1 and args[1] else lineno
            self.statements.insert(new_lineno, args[0] % self.__dict__)
            self.trace_debug(key, lineno, action)
            return True, -1 if new_lineno == lineno else 0
        elif action == "a":
            # append line after current with params[0]
            self.statements.insert(lineno + 1, args[0] % self.__dict__, )
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
            x = re.match(
                self.get_mig_rules()[key]["match"], self.statements[lineno]
            ) if "match" in self.get_mig_rules()[key] else None
            if x and x.groups():
                self.set_trigger(args[0], x.groups()[0])
                self.trace_debug(key, lineno, action + args[0])
            elif len(args) > 1:
                if re.match("[+-][0-9]+", args[1]):
                    self.set_trigger(args[0], int(args[1]) + getattr(self, args[0], 0))
                else:
                    self.set_trigger(args[0], args[1] % self.__dict__)
                self.trace_debug(key, lineno, action + args[0] + args[1])
            else:
                self.set_trigger(args[0], True)
                self.trace_debug(key, lineno, action + "True")
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
        elif action == "mv":
            # mv line (+#|-#|1.2|1.3|#)
            if not args:
                self.raise_error("Invalid expression mv")
                return False, 0
            new_lineno =  self.assing_lineno(lineno, args[0])
            if new_lineno != lineno:
                line = self.statements[lineno]
                del self.statements[lineno]
                self.statements.insert(new_lineno, line)
            return False, 0
        else:
            self.raise_error("Invalid rule action %s" % action)
        return False, 0

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
        if self.file_action in ("no", "rm"):
            return self.do_copy_file()
        else:
            self.analyze_source()
            meth = "do_upgrade_" + self.language
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
            for lineno, ln in enumerate(self.statements):
                if not self.statements[lineno]:
                    continue
                if not self.statements[lineno].startswith("#"):
                    break
                _, _, _, _, old_years = License.extract_info_from_line(
                    self.statements[lineno])
                _, _, _, _, cur_years = License.extract_info_from_line(
                    self.statements[lineno],
                    odoo_major_version=self.to_major_version,
                    force_from=True if self.opt_args.copyright_check > 1 else False)
                if old_years != cur_years:
                    self.statements[lineno] = self.statements[lineno].replace(
                        old_years, cur_years, 1)
        return res

    def do_upgrade_manifest(self):
        return self.do_upgrade_py()

    def do_upgrade_history(self):
        res = self.do_upgrade_file()
        self.do_upgrade_res_msg()
        return res

    def do_upgrade_file(self):

        def count_unbalanced(ln, left, right, comment_char="#"):
            ln = qsplit(ln, comment_char)[0]
            return len(qsplit(ln, left)) - (len(qsplit(ln, right)) if right else 1)

        if not self.file_action:
            self.init_env_file()
            stmtno = 0
            self.open_stmt = False
            self.imported = []
            self.try_indent = -1
            self.indent = self.stmt_indent = ""
            while stmtno < len(self.statements):
                self.first_line = stmtno == 0
                if self.statements[stmtno]:
                    if not re.match("^ *#", self.statements[stmtno]):
                        self.header = False
                        if (
                                re.match("^ *from .* import ", self.statements[stmtno])
                                or re.match("^ *import ", self.statements[stmtno])
                        ):
                            self.transition_stage = (
                                "import" if self.transition_stage == "import" else self.stage)
                            self.stage = "import"
                            pkgs = re.split("import", self.statements[stmtno])[1]
                            pkgs = pkgs.split("#")[0]
                            for pkg in pkgs.split(","):
                                pkg = pkg.strip()
                                if pkg not in self.imported:
                                    self.imported.append(pkg)
                        elif re.match(" *def ", self.statements[stmtno]):
                            self.transition_stage = self.stage
                            self.stage = "function_body"
                        elif re.match(" *class ", self.statements[stmtno]):
                            self.transition_stage = (
                                "import"
                                if self.stage in ("header", "import")
                                else self.stage)
                            self.stage = "class_body"
                        elif (
                            re.match("[^# ]", self.statements[stmtno])
                            and self.stage == "header"
                        ):
                            self.transition_stage = self.stage
                            self.stage = "import"
                    mo = self.syntax.syntax_rules[self.syntax.states[0]]["s"].match(
                        self.statements[stmtno])
                    self.indent = (
                        self.statements[stmtno][mo.start(): mo.end()] if mo else "")
                    self.dedent = self.indent < self.stmt_indent
                    self.stmt_indent = self.indent
                    if re.match("^ *try:", self.statements[stmtno]):
                        self.try_indent = len(self.indent)
                    elif len(self.indent) <= self.try_indent:
                        self.try_indent = -1
                stmtno = self.apply_rules_on_item(
                    self.statements[stmtno], stmtno=stmtno)
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
        for lineno, ln in enumerate(self.statements):
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
                self.statements[qua_lineno] = test_res_msg
            else:
                lineno -= lineno - 1
                self.statements.insert(lineno, test_res_msg)
                if not self.opt_args.dry_run:
                    with open(self.fqn, "w", encoding="utf-8") as fd:
                        fd.write("\n".join(self.statements))
            self.statements[title_lineno] = (
                    self.statements[title_lineno][:i_start]
                + datetime.strftime(datetime.now(), "%Y-%m-%d")
                + self.statements[title_lineno][i_end:]) + "\n"
        return True

    def solve_git_merge(self):
        state = "both"
        state_lev = 0
        lineno = 0
        while lineno < len(self.statements):
            ln = self.statements[lineno]
            if ln.startswith("<<<<<<<"):
                state = "left"
                state_lev += 1
                del self.statements[lineno]
            elif ln.startswith(">>>>>>>"):
                state = "right"
                state_lev += 1
                del self.statements[lineno]
            elif ln.startswith("=======") and state != "both":
                state_lev -= 1
                if not state_lev:
                    state = "both"
                del self.statements[lineno]
            elif state not in ("both", self.opt_args.git_merge_conflict):
                del self.statements[lineno]
            else:
                lineno += 1

    def write_xml(self, out_fqn):
        with open(out_fqn, "w", encoding="utf-8") as fd:
            source_xml = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
            source_xml += _u(ET.tostring(
                ET.fromstring(_b("\n".join(self.statements).replace('\t', '    '))),
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
                if self.opt_args.git_orgid:
                    opts += " -G%s" % self.opt_args.git_orgid
                cmd = "%s %s %s" % (
                    sys.executable,
                    get_config_path("gen_readme.py"),
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
        if not self.file_action and (
                self.opt_args.lint_anyway
                or out_fqn != self.fqn
                or self.source != "".join(self.statements)):
            if not self.opt_args.in_place:
                bakfile = '%s.bak' % out_fqn
                if pth.isfile(bakfile):
                    os.remove(bakfile)
                if pth.isfile(out_fqn):
                    os.rename(out_fqn, bakfile)
            if not self.opt_args.dry_run:
                if self.language == "xml":
                    self.write_xml(out_fqn)
                else:
                    with open(out_fqn, "w", encoding="utf-8") as fd:
                        fd.write("\n".join(self.statements))
            if not self.opt_args.no_parse_with_formatter:
                self.format_file(out_fqn)
            if self.opt_args.verbose > 0:
                print('👽 %s' % out_fqn)
        elif self.file_action == "new":
            if not pth.exists(out_fqn):
                cmd = "cp %s %s" % (self.fqn, out_fqn)
                z0lib.os_system(cmd, dry_run=self.opt_args.dry_run)
                if self.opt_args.verbose > 0:
                    print('👽 %s' % out_fqn)
        elif self.file_action == "no" and self.fqn != out_fqn:
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
    migrate_env.detect_mig_rules(language=migrate_env.language)
    prio = len(migrate_env.rule_categ) + 1
    for rule in migrate_env.rule_categ:
        migrate_env.load_config(rule, prio)
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
    migrate_env.detect_mig_rules(language=migrate_env.language)
    for rule in migrate_env.rule_categ:
        print("%4.4s> %s" % (mime, rule))


def list_rules(opt_args):
    if not opt_args.path:
        opt_args.path = ["./"]
    migrate_env = MigrateEnv(opt_args)
    for trigger in ("first_line", "migrate_multi", "backport_multi"):
        setattr(migrate_env, trigger, True)
    opt_args.header = True
    for mime in ("path", "python", "manifest-python", "history", "xml"):
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

    if opt_args.list_rules > 0:
        return list_rules(opt_args)

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
            if (
                not migrate_env.opt_args.assume_yes
                and migrate_env.opt_args.output
                and pth.isdir(migrate_env.opt_args.output)
                and pth.basename(path) != pth.basename(migrate_env.opt_args.output)
                and migrate_env.opt_args.from_version
                and migrate_env.opt_args.to_version
                and migrate_env.opt_args.from_version != migrate_env.opt_args.to_version
            ):
                sys.stderr.write(
                    'Target path %s conflicts with source path %s for migration!!\n'
                    % (migrate_env.opt_args.output, path)
                )
                return 2
            if (
                migrate_env.opt_args.output
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
                    fqn = pth.abspath(pth.join(root, fn)) + "/"
                    migrate_env.apply_rules_on_item(fqn)
                for fn in files:
                    fqn = pth.abspath(pth.join(root, fn))
                    sts = process_file(migrate_env, fqn)
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
