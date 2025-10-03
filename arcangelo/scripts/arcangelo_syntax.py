# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# import sys
# import os
import os.path as pth
import re

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

__version__ = "2.1.1"


def os_realpath(path):
    return pth.abspath(pth.expanduser(path))


def get_config_path(fn, is_config=False, sub=None):
    items = [pth.dirname(os_realpath(__file__))]
    if is_config:
        items.append("config")
    if sub and pth.isdir(pth.join(*items + [sub])):
        items.append(sub)
    items.append(fn)
    return pth.join(*items)


class Syntax(object):
    """The class syntax manages the rules to parse source of a specific language.
    Syntax rules are grouped by states; i.e. after comment delimiter usual parsing is
    broken. Some delimiters can shift from a state to another.
    A language can have as many as possible states; some common states are known
    globally.
    Globals states are:
        - "code": code parsing (initial state for almost languages)
        - "rem_eol": comment until end of line
        - "remark": multi line comment
        - "mtext": multi line text (initial state for xml/html)
        - "pre": preprocessor (c language)

    Every state can manages multiple items, every item has the own parsing rule;
    i.e. for object name regex rule may be "[a-zA-Z_][a-zA-Z0-9]*".
    A language state can have as many as possible items which generates tokens; some
    common items names are known across states. These common items are:
        - "name": object or variable name
        - "text": text constant
        - "text#": alternate text constant (where # ia a digit from 2)
        - "mtext": multi line text constant
        - "int": integer constant
        - "float" floating constant
    When the name of item is in states, system switches to state; every state must
    contains at least one name to switch another state. Only initial state, if is the
    unique state, can miss escape name to switch states.
    Items rule must cover all token kinds; to avoid infinite loop, system automatically
    can add 2 magic name: "nl", "s" and "other".
    The item "nl" spits lines by "\n" (new line); then item "s" is space separator and
    finally the item "other" capture any character not caught by rules.
    """
    def __init__(self, language):
        config = ConfigParser.ConfigParser()
        config_fqn = get_config_path(
            language + ".conf", is_config=True, sub="languages")
        if not pth.isfile(config_fqn) and language == "manifest-python":
            language = "python"
            config_fqn = get_config_path(
                language + ".conf", is_config=True, sub="languages")
        if not pth.isfile(config_fqn):
            language = "unknown"
            config_fqn = get_config_path(
                language + ".conf", is_config=True, sub="languages")
        config.read(config_fqn)
        if not config.has_section(language):
            raise SyntaxError("File %s w/o section %s" % (config_fqn, language))
        self.language = language
        self.states = [x.strip()
                       for x in config.get(language, "states").split(",")]
        self.syntax_rules = {}
        self.re_s = self.re_nl = self.re_other = self.re_rem_eol = None
        self.re_vt = re.compile("\v")
        for state in self.states:
            self.syntax_rules[state] = {}
            magic_names = []
            for (key, regex) in config.items(state):
                if key == "magic_names":
                    magic_names = [x.strip() for x in regex.split(",")]
                    continue
                self.syntax_rules[state][key] = re.compile(regex, re.M | re.S)
                if key == "rem_eol":
                    self.re_rem_eol = self.syntax_rules[state][key]
            if any([k not in self.states
                    for k in list(self.syntax_rules[state].keys())]):
                simple_state = False
                magic_names = magic_names or ["s", "nl", "other"]
            else:
                simple_state = True
                magic_names = magic_names or ["nl", "other"]
            for name in magic_names:
                if name == "nl":
                    if name not in self.syntax_rules[state].keys():
                        self.re_nl = re.compile(r"\n")
                    else:
                        self.re_nl = self.syntax_rules[state][name]
                        del self.syntax_rules[state][name]
                elif name == "s":
                    if name not in self.syntax_rules[state].keys():
                        self.re_s = re.compile(r"\s+", re.M | re.S)
                    else:
                        self.re_s = self.syntax_rules[state][name]
                        del self.syntax_rules[state][name]
                elif name == "other":
                    if name not in self.syntax_rules[state].keys():
                        if simple_state and self.syntax_rules[state]:
                            self.re_other = re.compile(
                                ".*?[^%s]" % "".join(
                                    [x.pattern[0]
                                     if x.pattern[0] != "\\" else x.pattern[0:2]
                                     for x in self.syntax_rules[state].values()]),
                                re.M | re.S)
                        else:
                            self.re_other = re.compile(".", re.M | re.S)
                    else:
                        self.re_other = self.syntax_rules[state][name]
                        del self.syntax_rules[state][name]

    def get_next_mo(self, source, spaces=False):
        if self.pos < len(source):
            if spaces == "vt":
                mo = self.re_vt.match(source, self.pos)
                if mo:
                    return "vt", mo
            if self.re_nl:
                mo = self.re_nl.match(source, self.pos)
                if mo:
                    return "nl", mo
            if self.re_s:
                mo = self.re_s.match(source, self.pos)
                if mo:
                    return "s", mo
            for (kind, rex) in self.syntax_rules[self.state].items():
                mo = rex.match(source, self.pos)
                if mo:
                    return kind, mo
            if self.re_other:
                mo = self.re_other.match(source, self.pos)
                if mo:
                    return "other", mo
            print("No syntax rule found for <<<%-.16s>>> ... (state=%s)"
                  % (source[self.pos:], self.state))
            kind = "other"
            pattern = "."
            self.re_other = re.compile(pattern, re.M | re.S)
            return kind, self.re_other.match(source, self.pos)
        return None, None

    def is_open_stmt(self):
        return (self.parens + self.brackets + self.braces + self.quotes)

    def action_nl(self, mo):
        self.lineno += 1
        self.linestart = mo.end()
        if not self.is_open_stmt():
            self.newline_pos.append(mo.end())

    def save_self(self, value, kind):
        self.saved_self = {
            "pos": self.pos,
            "value": value,
            "kind": kind,
        }

    def multiple_action_nl(self, saved_self, source):
        end = saved_self["pos"] + len(saved_self["value"])
        if saved_self["kind"] == "mtext":
            self.quotes = 1
        while "\n" in saved_self["value"]:
            mo = self.re_nl.search(source, saved_self["pos"])
            if not mo or mo.end() > end:
                break
            self.action_nl(mo)
            saved_self["pos"] = mo.end()
        if saved_self["kind"] == "mtext":
            self.quotes = 0

    # def unget_token(self, offset=0):
    #     self.saved_self = None
    #     self.pos = self.prior_pos + offset

    def tokenize(self, source, spaces=False):
        self.state = self.states[0]
        self.pos = 0
        self.linestart = 0
        self.lineno = 1
        self.column = 1
        self.pos = 0
        self.prior_pos = -1
        self.parens = 0
        self.brackets = 0
        self.braces = 0
        self.quotes = 0
        self.newline_pos = [0]
        self.language = None
        self.saved_self = None
        while self.pos < len(source):
            if self.saved_self:
                self.multiple_action_nl(self.saved_self, source)
            kind, mo = self.get_next_mo(source, spaces=spaces)
            value = mo.group()
            self.save_self(value, kind)
            start = mo.start()
            self.prior_pos = self.pos
            self.pos = end = mo.end()
            self.column = start - self.linestart + 1
            if kind in self.states:
                self.state = kind
            elif kind in ("nl", "s", "vt"):
                if not spaces:
                    continue
            elif kind in ("nl", "s"):
                continue
            elif kind == "op_lparen":
                self.parens += 1
            elif kind == "op_rparen":
                self.parens -= 1
            elif kind == "op_lbracket":
                self.brackets += 1
            elif kind == "op_rbracket":
                self.brackets -= 1
            elif kind == "op_lbrace":
                self.braces += 1
            elif kind == "op_rbrace":
                self.braces -= 1
            yield (kind, value, self.lineno, self.column, start, end)
        if self.saved_self:
            self.multiple_action_nl(self.saved_self, source)
