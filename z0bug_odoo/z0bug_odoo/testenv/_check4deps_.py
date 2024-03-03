# -*- coding: utf-8 -*-
#
# Copyright 2023-24 SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
import os
import sys
import re
import logging

from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def check_4_depending(cr):
    """check_4_depending v2.0.17
    This function check for valid modules which current module depends on.
    Usually Odoo checks for depending on, through "depends" field in the manifest, but
    Odoo does not check for the version range neither check for incompatibilities.
    With three new fields: "version_depends", "conflicts" (on odoo modules) and
    "version_external_dependencies" (on python packages), this function checks for
    version range, like pip or apt/yum commands. Example:
        "version_depends": ["dep_module>=12.0.2.0"],
        "version_external_dependencies": ["Werkzeug>=0.16"],
        "conflicts": [
            "incompatible!", "quite_incompatible",
            "inv_auth!=~Danger", "req_auth=~?MySelf"
        ],
        "pre_init_hook": "check_4_depending",
    In above example, current module installation fails if:
        * version of the module named "dep_module" is less than 12.0.2.0
        * modules named "incompatible" is installed
        * module "quite_incompatible" is installed (*)
        * author name or maintainer name of module "inv_auth" is 'Danger' (**)
        * author name or maintainer name of module "req_ath" is not 'MySelf' (**)
        * python package Werkzeug is less than 0.16.
    Incompatibility is overridden if system parameter "disable_module_incompatibility"
    is True and one of following rules is true:
        (*) module name to match does not end with symbol "!"
        (**) regex operators are '=~?' or '!=~?'
    Summary:
        - Operators == != >= <= > < match with module version
        - "Conflicts" key matches module 'name' (can be disabled) or 'name!' (always)
        - Operators =~ (always) !=~ (negate+always) =~? (disable) !=~? (negate+disable)
          match regex on module author or module maintainer
    Notice:
    __init__.py in current module root must contain the statement:
        from ._check4deps_ import check_4_depending
    __manifest__.py in current module root must containt the statement:
        "pre_init_hook": "check_4_depending",
    """

    def comp_versions(version):
        return [
            "%05d" % int(x) if x.isdigit() else x
            for x in version.split(".")
        ]

    def display_name(mtype):
        return "Package" if mtype == "pypi" else "Module"

    def eval_condition_conflicts(mtype, app, op, disable_check):
        if app["version"]:
            uninstallable_reason = (
                "Module '%s' conflicts with installed %s '%s'"
                % (
                    cur_module,
                    display_name(mtype),
                    app["name"],
                )
            )
            if "!" not in op:
                uninstallable_reason += (
                    " - Use config param <disable_module_incompatibility> to install!")
            _logger.error(uninstallable_reason)
            if not disable_check or "!" in op:
                return uninstallable_reason
        return False

    def eval_regex(mtype, app, op, ver_to_match, disable_check):
        a = re.search("(?i)" + ver_to_match, app["author"])
        m = re.search("(?i)" + ver_to_match, app["maintainer"])
        if op.startswith("=~") and ((not a and not m) or not app["version"]):
            uninstallable_reason = (
                "%s '%s' is not installable because author or maintainer of module '%s'"
                " must match with '%s'"
                % (
                    display_name(mtype),
                    cur_module,
                    app["name"],
                    ver_to_match,
                )
            )
            if "?" in op:
                uninstallable_reason += (
                    " - Use config param <disable_module_incompatibility> to install!")
            _logger.error(uninstallable_reason)
            if not disable_check or "?" not in op:
                return uninstallable_reason
        elif op.startswith("!=~") and (a or m) and app["version"]:
            uninstallable_reason = (
                "%s '%s' is not installable because found author or maintainer '%s'"
                " in module '%s'"
                % (
                    display_name(mtype),
                    cur_module,
                    ver_to_match,
                    app["name"],
                )
            )
            if "?" in op:
                uninstallable_reason += (
                    " - Use config param <disable_module_incompatibility> to install!")
            _logger.error(uninstallable_reason)
            if not disable_check or "?" not in op:
                return uninstallable_reason
        return False

    def eval_version_match(mtype, app, op, ver_to_match, condition):
        if not eval("%s%s%s" % (comp_versions(app["version"]),
                                op,
                                comp_versions(ver_to_match))):
            uninstallable_reason = (
                "%s '%s' is not installable because it does not match with '%s%s'"
                " (is %s)"
                % (
                    display_name(mtype),
                    cur_module,
                    app["name"],
                    condition,
                    app["version"],
                )
            )
            _logger.error(uninstallable_reason)
            return uninstallable_reason

    def eval_condition(mtype, app, condition, disable_check):
        """evaluate condition and return reason for match"""
        x = op_re.match(condition)
        if x:
            op = condition[x.start(): x.end()]
            ver_to_match = condition[x.end():]
        else:
            op = ver_to_match = ""
        if op in ("", "!"):
            return eval_condition_conflicts(mtype, app, op, disable_check)
        elif op in ("=~", "!=~", "=~?", "!=~?"):
            return eval_regex(mtype, app, op, ver_to_match, disable_check)
        elif not app["version"]:
            uninstallable_reason = "%s '%s' not installed" % (
                display_name(mtype),
                app["name"],
            )
            _logger.error(uninstallable_reason)
            return uninstallable_reason
        return eval_version_match(mtype, app, op, ver_to_match, condition)

    def get_odoo_module_info(app_name):
        odoo_module = env["ir.module.module"].search([("name", "=", app_name)])
        if not odoo_module or odoo_module[0].state != "installed":
            app = {"name": app_name, "version": False, "author": "", "maintainer": ""}
        else:
            app = {"name": app_name,
                   "version": odoo_module[0].installed_version,
                   "author": odoo_module[0].author or "",
                   "maintainer": odoo_module[0].maintainer or ""}
        return app

    def get_pypi_info(app_name):
        if sys.version_info[0] == 2:
            import pkg_resources
            try:
                version = pkg_resources.get_distribution(app_name).version
            except BaseException:
                version = False
        elif sys.version_info < (3, 8):
            import importlib_metadata as metadata
            try:
                version = metadata.version(app_name)
            except BaseException:
                version = False
        else:
            from importlib import metadata
            try:
                version = metadata.version(app_name)
            except BaseException:
                version = False
        return {"name": app_name, "version": version}

    def check_for_all_dependecies(dependecies_list, mtype="odoo", disable_check=False):
        if not isinstance(dependecies_list, (list, tuple)):
            dependecies_list = [dependecies_list]
        uninstallable_reason = ""
        for pkg_with_ver in dependecies_list:
            x = item_re.match(pkg_with_ver)
            if not x and mtype == "conflicts":
                app_name = pkg_with_ver
                conditions = []
            else:
                ix = x.end()
                app_name = pkg_with_ver[x.start(): ix]
                conditions = pkg_with_ver[ix:].split(",")
            if mtype in ("odoo", "conflicts"):
                app = get_odoo_module_info(app_name)
            elif mtype == "pypi":
                app = get_pypi_info(app_name)
            else:
                raise UserError("Unknown depend on type %s" % mtype)

            for condition in conditions:
                uninstallable_reason = eval_condition(
                    mtype, app, condition, disable_check)
                if uninstallable_reason:
                    break
            if uninstallable_reason:
                break
        if uninstallable_reason:
            raise UserError(uninstallable_reason)

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
    disable_check = env["ir.config_parameter"].search(
        [("key", "=", "disable_module_incompatibility")]
    )
    disable_check = disable_check and eval(disable_check[0].value) or False
    item_re = re.compile("[^>=<~!?]+")
    op_re = re.compile("[>=<~!?]+")
    check_for_all_dependecies(
        manifest.get("version_external_dependencies", []),
        mtype="pypi", disable_check=disable_check
    )
    check_for_all_dependecies(
        manifest.get("version_depends", []), mtype="odoo", disable_check=disable_check
    )
    check_for_all_dependecies(
        manifest.get("conflicts", []), mtype="conflicts", disable_check=disable_check
    )



