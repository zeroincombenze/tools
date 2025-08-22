#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create map of Odoo modules
"""
import os.path
import sys

# import os
from datetime import datetime
import argparse
import ast
from python_plus import unicodes

__version__ = "2.0.11"


class OdooMap(object):
    """ """

    def __init__(self, opt_args):
        self.opt_args = opt_args
        self.module_map = {}
        self.repositories = {}
        self.duplicate_modules = []

    def ismodule(self, path):
        if os.path.isdir(path):
            if (
                os.path.isfile(os.path.join(path, "__manifest__.py"))
                or os.path.isfile(os.path.join(path, "__openerp__.py"))
            ) and os.path.isfile(os.path.join(path, "__init__.py")):
                return True
        return False

    def set_module(self, path):
        name = os.path.basename(path)
        reponame = os.path.basename(os.path.dirname(path))
        if reponame == "addons":
            reponame = "OCB"
        manifest_file = os.path.join(path, "__manifest__.py")
        if not os.path.isfile(manifest_file):
            manifest_file = os.path.join(path, "__openerp__.py")
        manifest = self.read_manifest_file(manifest_file)
        return {
            "name": name,
            "reponame": reponame,
            "path": path,
            "depends": manifest.get("depends", []),
            "external_dependencies": manifest.get("external_dependencies", []),
        }

    def set_repo(self, name, path):
        return {
            "name": name,
            "path": path,
            "oca_dependencies": [],
            "requirements": [],
        }

    def read_manifest_file(self, manifest_path):
        try:
            manifest = ast.literal_eval(open(manifest_path).read())
        except (ImportError, IOError, SyntaxError):
            raise Exception("Wrong manifest file %s" % manifest_path)
        return unicodes(manifest)

    def write_fn_dependencies(self, repo):
        path = repo["path"]
        fn_oca_dependencies = os.path.join(path, "oca_dependencies.txt~")
        with open(fn_oca_dependencies, "w") as fd:
            fd.write(
                "# Generated on %s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            for reponame in sorted(repo["oca_dependencies"]):
                fd.write("%s\n" % reponame)

    def build_map(self):
        target_path = os.path.abspath(self.opt_args.target_path)
        for root, dirs, files in os.walk(target_path, topdown=True, followlinks=False):
            dirs[:] = [
                d
                for d in dirs
                if d not in (".git", "__to_remove", "doc", "setup", ".idea")
            ]
            for base in dirs:
                path = os.path.join(root, base)
                if self.ismodule(path):
                    module = self.set_module(path)
                    repo = self.set_repo(module["reponame"], os.path.dirname(path))
                    modulename = module["name"]
                    reponame = repo["name"]
                    if modulename in self.module_map:
                        print("Duplicate module %s" % modulename)
                        self.duplicate_modules.append(modulename)
                        if (
                            reponame.startswith("l10n-italy")
                            or self.module_map[modulename]["reponame"] == "uncovered"
                        ):
                            self.module_map[modulename] = module
                    else:
                        self.module_map[modulename] = module
                    if reponame not in self.repositories:
                        self.repositories[reponame] = repo
        for modulename, module in self.module_map.items():
            reponame = module["reponame"]
            for dep_name in module["depends"]:
                if dep_name not in self.module_map:
                    print(
                        "Module %s not found! It is required by %s"
                        % (dep_name, modulename)
                    )
                    continue
                dep_reponame = self.module_map[dep_name]["reponame"]
                if (
                    dep_reponame != reponame
                    and dep_reponame != "OCB"
                    and dep_reponame
                    not in self.repositories[reponame]["oca_dependencies"]
                ):
                    self.repositories[reponame]["oca_dependencies"].append(dep_reponame)
            print(module)
        print("")
        for name, repo in self.repositories.items():
            print("%s = %s" % (name, repo["oca_dependencies"]))
            self.write_fn_dependencies(repo)
        print("")
        for name in self.duplicate_modules:
            print("Duplicate module: %s" % name)


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Map Odoo modules", epilog="© 2022-2023 by SHS-AV s.r.l."
    )
    parser.add_argument(
        "-b",
        "--odoo-branch",
        dest="odoo_branch",
        default="12.0",
        help="Default Odoo version",
    )
    parser.add_argument("-c", "--config", help="Odoo configuration file")
    parser.add_argument(
        "-G",
        "--git-orgs",
        help="Git organizations, comma separated - " "May be: oca librerp or zero",
    )
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-p", "--target-path", help="Local directory")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    odoo_map = OdooMap(parser.parse_args(cli_args))
    odoo_map.build_map()
    sts = 0
    return sts


if __name__ == "__main__":
    exit(main())
