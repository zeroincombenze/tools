# -*- coding: utf-8 -*-
#
# Copyright 2023-24 SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
"""openupgrade_(pre|post)_migrate v2.0.18
This file contains 2 functions that execute all migration actions on the module and
on the module items. The functions are called before and after installation.
Thesefunctions are just hooks to OCA openupgrade in order to simplify the migration
upgrade of modules, with simple declaration in __manifest__.py file.

You can add following key in the __manifest__:
'module_oldname': prior name of renamed module

ACTIONS
* Module renamed: call openupgrade.rename_xmlids() and mark old name module with
  'to uninstall' if it is installed
Notice:
__init__.py in current module root must contain the statement:
    from ._openupgrademigrate_ import openupgrade_migrate
__manifest__.py in current module root must contain the statement:
    "pre_init_hook": "openupgrade_migrate",
"""
import os
# import sys
# import re
import logging

from odoo import api, SUPERUSER_ID
# from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def openupgrade_pre_migrate(cr):
    def rename_module(old_name, new_name):
        pass

    env = api.Environment(cr, SUPERUSER_ID, {})
    path = __file__
    while path != "/":
        path = os.path.dirname(path)
        manifest_path = os.path.join(path, "__manifest__.py")
        if os.path.isfile(manifest_path):
            break
        manifest_path = os.path.join(path, "__openerp__.py")
        if os.path.isfile(manifest_path):
            break
    try:
        manifest = eval(open(manifest_path, "r").read())
    except (ImportError, IOError, SyntaxError):
        manifest = {}
    cur_module = os.path.basename(os.path.dirname(manifest_path))
    disable_migr = env["ir.config_parameter"].search(
        [("key", "=", "disable_module_automigrate")]
    )
    disable_migr = disable_migr and eval(disable_migr[0].value) or False
    if not disable_migr:
        if manifest.get("module_oldname"):
            rename_module(manifest["module_oldname"], cur_module)


def openupgrade_post_migrate(cr):
    def rename_module(old_name, new_name):
        pass

    env = api.Environment(cr, SUPERUSER_ID, {})
    path = __file__
    while path != "/":
        path = os.path.dirname(path)
        manifest_path = os.path.join(path, "__manifest__.py")
        if os.path.isfile(manifest_path):
            break
        manifest_path = os.path.join(path, "__openerp__.py")
        if os.path.isfile(manifest_path):
            break
    try:
        manifest = eval(open(manifest_path, "r").read())
    except (ImportError, IOError, SyntaxError):
        manifest = {}
    cur_module = os.path.basename(os.path.dirname(manifest_path))
    disable_migr = env["ir.config_parameter"].search(
        [("key", "=", "disable_module_automigrate")]
    )
    disable_migr = disable_migr and eval(disable_migr[0].value) or False
    if not disable_migr:
        if manifest.get("module_oldname"):
            rename_module(manifest["module_oldname"], cur_module)
