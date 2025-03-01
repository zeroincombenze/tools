# -*- coding: utf-8 -*-
# pylint: skip-file
#
# Copyright 2023-24 SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
"""openupgrade_(pre|post)_migrate v2.0.18
This file contains 2 functions that execute all migration actions on the module and
on the module items. The functions are called before and after installation.
These functions are just hooks to OCA openupgrade in order to simplify the migration
upgrade of modules, with simple declaration in __manifest__.py file.

You can add following key in the __manifest__:
'migrated_from_module': (string) prior name of current module
'migrate_deprecated': (string) new name of current module
'migrate_model': (list) prior model name and new model name
'merge_model': (list) prior model name and new model name
'migrate_field': (list) model name, prior field name and new field name

ACTIONS
* 'migrated_from_module': call openupgrade.rename_xmlids() [post] and mark old name
                          module with 'to uninstall' if it is installed [post] - Old
                          module should contain 'migrate_deprecated' clause
* 'migrate_deprecated': mark new name module with 'to install' if it is not installed
                        [pre] - New module have to contain 'migrate_from_module' clause
* 'migrate_model': call openupgrade.rename_xmlids() ... ? [post]
* 'migrate_model': call openupgrade.rename_xmlids() ... ? [post]
* 'migrate_field': call openupgrade.rename_xmlids() ... ? [post]

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
