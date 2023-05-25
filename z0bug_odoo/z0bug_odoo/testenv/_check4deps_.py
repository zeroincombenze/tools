# Copyright 2023 SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
import os
import sys
import re
import ast

from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError


def check_4_depending(cr):
    """check_4_depending v0.1.0
    This function check for valid modules which current module depends on.
    The depending on check is executed from "depends" field in the manifest,
    but Odoo does not check for the version range neither check for incompatibilities.
    Adding two new fields "version_depends" (for odoo modules) and
    "version_external_dependencies" (for python packages),
    this function check for version range, like pip or apt/yum etc. Example:
        "version_depends": [
            "dep_module>=12.0.2.0",
            "incompatible!?"
        ],
        "version_external_dependencies": ["Werkzeug>=0.16"]
    Module installation fails if module named "dep_module" version is less than 12.0.2.0
    and fails is module named "incompatible" is installed.
    The symbol "?" at the end of module declaration disables the check for the module,
    if the system parameter "disable_module_incompatibility" is True.
    """

    def comp_versions(version):
        return [
            "%05d" % int(x) if x.isdigit() else x
            for x in version.split(".")
        ]

    def display_name(mtype):
        return "Package" if mtype == "pypi" else "Module"

    def check_for_all_dependecies(dependecies_list, mtype="odoo", disable_check=False):
        uninstallable_reason = ""
        for pkg_with_ver in dependecies_list:
            x = item_re.match(pkg_with_ver)
            ix = x.end()
            app_name = pkg_with_ver[x.start(): ix]
            conditions = pkg_with_ver[ix:].split(",")
            if mtype == "odoo":
                odoo_module = env["ir.module.module"].search([("name", "=", app_name)])
                if not odoo_module or odoo_module[0].state != "installed":
                    app = {"name": app_name, "version": False}
                else:
                    app = {"name": app_name,
                           "version": odoo_module[0].installed_version}
            elif mtype == "pypi":
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
                app = {"name": app_name, "version": version}
            else:
                raise UserError("Invalid type %s declaration" % mtype)

            for condition in conditions:
                x = op_re.match(condition)
                op = condition[x.start(): x.end()]
                ver_to_match = condition[x.end():]
                if op != "!" and not app["version"]:
                    if not disable_check:
                        uninstallable_reason = "%s '%s' not installed" % (
                            display_name(mtype),
                            app["name"],
                        )
                        break
                elif op == "!" and app["version"]:
                    uninstallable_reason = (
                        "Installed %s '%s' is incompatible with '%s'"
                        % (
                            display_name(mtype),
                            app["name"],
                            cur_module,
                        )
                    )
                    break
                elif not eval("%s%s%s" % (comp_versions(app["version"]),
                                          op,
                                          comp_versions(ver_to_match))
                ):
                    uninstallable_reason = (
                        "%s '%s' is not installable because does not match %s%s"
                        % (
                            display_name(mtype),
                            cur_module,
                            app_name,
                            condition,
                        )
                    )
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
        manifest = ast.literal_eval(open(manifest_path, "r").read())
    except (ImportError, IOError, SyntaxError):
        manifest = {}
    cur_module = os.path.basename(os.path.dirname(manifest_path))
    disable_check = env["ir.config_parameter"].search(
        [("key", "=", "disable_module_incompatibility")]
    )
    disable_check = disable_check and disable_check[0].value or False
    item_re = re.compile("[^>=<!?]+")
    op_re = re.compile("[>=<!?]+")
    check_for_all_dependecies(
        manifest.get("version_depends", []), mtype="odoo", disable_check=disable_check
    )
    check_for_all_dependecies(
        manifest.get("version_external_dependencies", []),
        mtype="pypi", disable_check=disable_check
    )
