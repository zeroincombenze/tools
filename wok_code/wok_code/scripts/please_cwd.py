#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NAME
    Various actions on current working directory.

SYNOPSIS
    please [action] [cwd] [options]

    * docs: create project documentation from egg-info or readme directory
    * edit: edit pofile or other project file
    * translate: create it.po file with italian translation for Odoo module
    * wep: clean temporary file in current working directory and sub direcotries

DESCRIPTION
    This command creates execute one of %(actions)s
    on current working directory.

OPTIONS
  %(options)s

EXAMPLES
    please docs

BUGS
    No known bugs.

SEE ALSO
    Full documentation at: <https://zeroincombenze-tools.readthedocs.io/>
"""
import os.path

__version__ = "2.0.8"


class PleaseCwd(object):
    def __init__(self, please):
        self.please = please

    # def get_actions(self):
    #     return ["docs", "translate", "wep"]

    def action_opts(self, parser):
        self.please.add_argument(parser, "-B")
        self.please.add_argument(parser, "-b")
        self.please.add_argument(parser, "-c")
        self.please.add_argument(parser, "-n")
        self.please.add_argument(parser, "-q")
        self.please.add_argument(parser, "-v")
        parser.add_argument('args', nargs="*")
        return parser

    def do_docs(self):
        please = self.please
        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_pypi_pkg():
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh"))
            return please.run_traced(cmd)
        return please.do_iter_action(self, act_all_pypi=True, act_tools=True)

    def do_edit(self):
        please = self.please
        if please.is_odoo_pkg():
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh"))
            return please.run_traced(cmd)
        return 1

    def do_translate(self):
        please = self.please
        if please.is_odoo_pkg():
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh"))
            return please.run_traced(cmd)
        return 1

    def do_wep(self):
        please = self.please
        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_pypi_pkg():
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "please.sh"))
            return please.run_traced(cmd)
        return please.do_iter_action(self, act_all_pypi=True, act_tools=True)

    def do_wep_db(self):
        please = self.please
        if please.is_odoo_pkg() or please.is_repo_odoo() or please.is_pypi_pkg():
            cmd = please.build_sh_me_cmd(
                cmd=os.path.join(os.path.dirname(__file__), "travis.sh"))
            return please.run_traced(cmd)
        return please.do_iter_action(self, act_all_pypi=True, act_tools=True)

    def do_action(self):
        return 126
