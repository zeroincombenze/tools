# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""
    Clodoo Regression Test Suite
"""
import ast
import os
import sys
import time
from configparser import ConfigParser
from datetime import datetime
from multiprocessing import Process
from subprocess import PIPE, Popen

from zerobug import z0test

try:
    from clodoo import clodoo
except ImportError:
    import clodoo


__version__ = "2.0.9"


MODULE_ID = "clodoo"
TEST_FAILED = 1
TEST_SUCCESS = 0

MANIFEST_FILES = ["__manifest__.py", "__odoo__.py", "__openerp__.py", "__terp__.py"]


def get_server_path(odoo_full, odoo_version, travis_home):
    odoo_version = odoo_version.replace("/", "-")
    odoo_org, odoo_repo = odoo_full.split("/")
    server_dirname = "%s-%s" % (odoo_repo, odoo_version)
    server_path = os.path.join(travis_home, server_dirname)
    return server_path


def get_server_script(server_path):
    if os.path.isfile(os.path.join(server_path, "odoo-bin")):
        return "odoo-bin"
    elif os.path.isfile(os.path.join(server_path, "openerp-server")):
        return "openerp-server"
    return "Script not found!"


def get_script_path(server_path, script_name):
    script_path = os.path.join(server_path, "server")
    if os.path.isdir(script_path):
        script_path = os.path.join(server_path, "server", script_name)
    else:
        script_path = os.path.join(server_path, script_name)
    return script_path


def set_conf_data(addons_path, data_dir=None, logfile=None):
    data_dir = data_dir or os.path.expanduser(
        os.environ.get("DATA_DIR", os.path.expanduser("~/data_dir"))
    )
    conf_data = {
        "addons_path": addons_path,
        "data_dir": data_dir,
        "db_password": clodoo.decrypt('Wg".:gfL'),
    }
    if logfile:
        conf_data["logfile"] = logfile
    if os.uname()[1][0:3] == "shs":
        pid = os.getpid()
        if pid > 18000:
            rpcport = str(pid)
        else:
            rpcport = str(18000 + pid)
        conf_data["xmlrpc_port"] = rpcport
        conf_data["db_user"] = "odoo"
    return conf_data


def get_modules(path, depth=1):
    """Return modules of path repo (used in test_server.py)"""
    return sorted(list(get_modules_info(path, depth).keys()))


def get_modules_info(path, depth=1):
    """Return a digest of each installable module's manifest in path repo"""
    # Avoid empty basename when path ends with slash
    path = os.path.expanduser(path)
    if not os.path.basename(path):
        path = os.path.dirname(path)

    modules = {}
    if os.path.isdir(path) and depth > 0:
        for module in os.listdir(path):
            manifest_path = is_module(os.path.join(path, module))
            if manifest_path:
                try:
                    manifest = ast.literal_eval(open(manifest_path).read())
                except ImportError:
                    raise Exception("Wrong file %s" % manifest_path)
                if manifest.get("installable", True):
                    modules[module] = {
                        "application": manifest.get("application"),
                        "depends": manifest.get("depends") or [],
                        "auto_install": manifest.get("auto_install"),
                    }
            else:
                deeper_modules = get_modules_info(os.path.join(path, module), depth - 1)
                modules.update(deeper_modules)
    return modules


def is_module(path):
    """return False if the path doesn't contain an odoo module, and the full
    path to the module manifest otherwise"""

    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        return False
    files = os.listdir(path)
    filtered = [x for x in files if x in (MANIFEST_FILES + ["__init__.py"])]
    if len(filtered) == 2 and "__init__.py" in filtered:
        return os.path.join(path, next(x for x in filtered if x != "__init__.py"))
    else:
        return False


def is_addons(path):
    res = get_modules(path) != []
    return res


def get_addons(path, depth=1):
    path = os.path.expanduser(path)
    if not os.path.exists(path) or depth < 0:
        return []
    res = []
    if is_addons(path):
        res.append(path)
    else:
        new_paths = [
            os.path.join(path, x)
            for x in sorted(os.listdir(path))
            if os.path.isdir(os.path.join(path, x))
        ]
        for new_path in new_paths:
            res.extend(get_addons(new_path, depth - 1))
    return res


def get_addons_path(
    travis_dependencies_dir, travis_base_dir, server_path, odoo_test_select
):
    addons_path_list = []
    for ldir in ("server/openerp", "openerp", "odoo"):
        if os.path.isdir(os.path.join(server_path, ldir, "addons")):
            addons_path_list = [os.path.join(server_path, ldir, "addons")]
            break
    addons_path_list.append(os.path.join(server_path, "addons"))
    if travis_base_dir:
        if odoo_test_select != "NO-CORE":
            addons_path_list.extend(get_addons(travis_base_dir))
    if travis_dependencies_dir:
        addons_path_list.extend(get_addons(travis_dependencies_dir))
    addons_path = ",".join(addons_path_list)
    return addons_path


def write_server_conf(data, version):
    fname_conf = os.path.expanduser("~/.openerp_serverrc")
    if not os.path.exists(fname_conf):
        fconf = open(fname_conf, "w")
        fconf.close()
    config = ConfigParser()
    config.read(fname_conf)
    if not config.has_section("options"):
        config["options"] = {}
    config["options"].update(data)
    with open(fname_conf, "w") as configfile:
        config.write(configfile)


def get_odoo_cmd(script_path, db=None, modules=None, loglevel=None):
    loglevel = loglevel or "info"
    cmd_odoo = [script_path, "--log-level=%s" % loglevel]
    if db:
        cmd_odoo += ["-d", db]
    if modules:
        cmd_odoo += ["--stop-after-init", "--init", ",".join(modules)]
    return cmd_odoo


def run_odoo_cmd(cmd_odoo):
    prc = Popen(cmd_odoo, stderr=PIPE, stdout=PIPE)
    res, err = prc.communicate()
    print(res)


def str_secret(obj):
    def str_list_secret(obj):
        obj_secret = []
        skip_next = False
        for param in obj:
            if skip_next:
                skip_next = False
                continue
            if param.startswith("--pass"):
                obj_secret.append(param.split("=")[0] + "=***")
                continue
            if param.startswith("--pwd"):
                obj_secret.append("--log-db=***")
                continue
            obj_secret.append(param)
        return obj_secret

    def str_dict_secret(obj):
        obj_secret = obj.copy()
        for param in obj:
            if param in (
                "db_password",
                "login_password",
                "crypt_password",
                "login2_password",
                "crypt2_password",
                "oneadm_pwd",
                "botadm_pwd",
                "admin_passwd",
            ):
                obj_secret[param] = "***"
        return obj_secret

    if isinstance(obj, (list, tuple)):
        return str_list_secret(obj)
    elif isinstance(obj, dict):
        return str_dict_secret(obj)
    return obj


def version():
    return __version__


class RegressionTest:
    def __init__(self, zarlib):
        self.Z = zarlib
        self.ctx = {}
        self.uid = False
        self.db = os.environ.get("MQT_TEST_DB", "clodoo_test")
        self.odoo_full = os.environ.get("ODOO_REPO", "zeroincombenze/OCB")
        self.odoo_version = os.environ.get("VERSION", "10.0")

    def check_4_db(self, dbname):
        cmd = ["psql"] + ["-Upostgres"] + ["-tl"]
        prc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        res, err = prc.communicate()
        dbname = " %s " % dbname
        if res.find(dbname) >= 0:
            return True
        else:
            return False

    def __test_01(self, z0ctx):
        sts = TEST_SUCCESS
        travis_debug_mode = eval(os.environ.get("TRAVIS_DEBUG_MODE", "0"))
        if not z0ctx["dry_run"]:
            travis_home = os.environ.get("HOME", os.path.expanduser("~"))
            print("Odoo repo=%s" % self.odoo_full)
            print("Odoo ver=%s" % self.odoo_version)
            server_path = get_server_path(
                self.odoo_full, self.odoo_version, travis_home
            )
            script_name = get_server_script(server_path)
            script_path = get_script_path(server_path, script_name)
            addons_path = get_addons_path(False, False, server_path, "ALL")
            self.logfile = os.path.join(
                os.environ.get("HOME", os.path.expanduser("~")),
                "odoo_%s.log" % self.odoo_version.replace(".", "-"),
            )
            conf_data = set_conf_data(addons_path, logfile=self.logfile)
            self.rpcport = conf_data.get("xmlrpc_port", 8069)
            write_server_conf(conf_data, self.odoo_version)
            cmd_odoo = get_odoo_cmd(script_path)
            print("script_name=%s" % script_name)
            print("script_path=%s" % script_path)
            print("addons_path=%s" % addons_path)
            print("conf_data=%s" % str_secret(conf_data))
            print("cmd_odoo=%s" % cmd_odoo)
            # run_odoo_cmd(cmd_odoo)
            prc = Process(target=run_odoo_cmd, args=(cmd_odoo,))
            prc.start()
            if os.environ.get("TRAVIS", "") == "true":
                time.sleep(6)
            else:
                time.sleep(3)
            if travis_debug_mode >= 2:
                pass
            self.uid, self.ctx = clodoo.oerp_set_env(
                db=self.db,
                ctx={
                    "oe_version": "*",
                    "no_login": True,
                    "xmlrpc_port": self.rpcport,
                    "conf_fn": "./no_filename.conf",
                },
            )
        else:
            self.ctx = {"oe_version": self.odoo_version}
        sts = self.Z.test_result(
            z0ctx, "connect(%s)" % self.db, self.odoo_version, self.ctx["oe_version"]
        )

        if not z0ctx["dry_run"]:
            self.ctx["test_unit_mode"] = True
            clodoo.act_drop_db(self.ctx)
            sts = clodoo.act_new_db(self.ctx)
        sts = self.Z.test_result(z0ctx, "new_db(%s)" % self.db, TEST_SUCCESS, sts)
        if not z0ctx["dry_run"]:
            res = self.check_4_db(self.db)
        else:
            res = True
        sts = self.Z.test_result(z0ctx, "_db(%s)" % self.db, True, res)
        if not z0ctx["dry_run"]:
            self.uid, self.ctx = clodoo.oerp_set_env(
                db=self.db,
                ctx={
                    "oe_version": self.ctx["oe_version"],
                    "xmlrpc_port": self.rpcport,
                    "conf_fn": "./no_filename.conf",
                },
            )
            self.ctx["test_unit_mode"] = True
            res = self.uid
        else:
            res = 1
        sts = self.Z.test_result(z0ctx, "login_%s" % self.db, 1, res)
        if not z0ctx["dry_run"]:
            prc.terminate()
        return sts

    def __test_02(self, z0ctx):
        sts = TEST_SUCCESS
        ctx = self.ctx
        if not z0ctx["dry_run"]:
            ids = clodoo.searchL8(ctx, "res.users", [])
        else:
            ids = [1]
        sts = self.Z.test_result(z0ctx, "searchL8(res.users)", True, 1 in ids)
        if sts == TEST_SUCCESS:
            model = "res.users"
            if not z0ctx["dry_run"]:
                user = clodoo.browseL8(ctx, "res.users", 1)
                user_id = user.id
            else:
                user_id = 1
            sts = self.Z.test_result(z0ctx, "browseL8(res.users)", 1, user_id)
        if sts == TEST_SUCCESS:
            if not z0ctx["dry_run"]:
                RES = clodoo.get_val_from_field(ctx, model, user, "login")
            else:
                RES = "admin"
            sts = self.Z.test_result(z0ctx, "user[login] (char)", "admin", RES)
        if sts == TEST_SUCCESS:
            if not z0ctx["dry_run"]:
                RES = clodoo.get_val_from_field(ctx, model, user, "active")
            else:
                RES = True
            sts = self.Z.test_result(z0ctx, "user[active] (bool)", True, RES)
        if sts == TEST_SUCCESS:
            if not z0ctx["dry_run"]:
                RES = clodoo.get_val_from_field(ctx, model, user, "company_id")
            else:
                RES = True
            sts = self.Z.test_result(z0ctx, "user[company_id] (m2o)", True, RES)
        if sts == TEST_SUCCESS:
            if not z0ctx["dry_run"]:
                RES = clodoo.get_val_from_field(ctx, model, user, "company_ids")
            else:
                RES = [1]
            sts = self.Z.test_result(z0ctx, "user[company_ids] (m2m)", [1], RES)
        if sts == TEST_SUCCESS:
            if not z0ctx["dry_run"]:
                RES = clodoo.get_val_from_field(
                    ctx, model, user, "company_ids", format="cmd"
                )
            else:
                RES = [(6, 0, [1])]
            sts = self.Z.test_result(
                z0ctx, "user[company_ids] (cmd)", [(6, 0, [1])], RES
            )
        if sts == TEST_SUCCESS:
            if not z0ctx["dry_run"]:
                RES = clodoo.get_val_from_field(ctx, model, user, "login_date")
            else:
                RES = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sts = self.Z.test_result(
                z0ctx,
                "user[login_date] (date[time])",
                datetime.now().strftime("%Y-%m-%d"),
                str(RES)[0:10],
            )
        if sts == TEST_SUCCESS:
            if not z0ctx["dry_run"]:
                RES = clodoo.get_val_from_field(
                    ctx, model, user, "login_date", format="cmd"
                )
            else:
                RES = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sts = self.Z.test_result(
                z0ctx,
                "user[login_date] (date[time])",
                datetime.now().strftime("%Y-%m-%d"),
                RES[0:10],
            )
        return sts

    def __test_03(self, z0ctx):
        sts = TEST_SUCCESS
        ctx = self.ctx
        if not z0ctx["dry_run"]:
            model = "ir.model"
            rec = clodoo.browseL8(
                ctx,
                model,
                clodoo.searchL8(ctx, model, [("model", "=", "res.users")])[0],
            )
            RES = clodoo.get_val_from_field(ctx, model, rec, "field_id")
        else:
            RES = [1, 2, 3]
        sts = self.Z.test_result(
            z0ctx,
            "ir_model[field_id] (o2m)",
            True,
            isinstance(RES, list) and len(RES) > 1,
        )
        if sts == TEST_SUCCESS:
            record_list = RES
            if not z0ctx["dry_run"]:
                model = "ir.model"
                RES = clodoo.get_val_from_field(
                    ctx, model, rec, "field_id", format="cmd"
                )
            else:
                RES = [(6, 0, record_list)]
            sts = self.Z.test_result(
                z0ctx, "ir_model[field_id] (cmd)", [(6, 0, record_list)], RES
            )
        return sts

    def __test_04(self, z0ctx):
        sts = TEST_SUCCESS
        ctx = self.ctx
        model = "res.users"
        vals = {"name": "admin", "partner_id": 1, "email": "myname@example.com"}
        for tgt_ver in ("12.0", "11.0", "10.0", "9.0", "8.0", "7.0", "6.1"):
            for name in vals:
                if not z0ctx["dry_run"]:
                    new_name, RES = clodoo.cvt_value_from_ver_to_ver(
                        ctx, model, name, vals[name], "7.0", tgt_ver
                    )
                else:
                    RES = new_name = True
                if name == "name":
                    TRES = vals[name]
                    sts = self.Z.test_result(z0ctx, "cvt(%s)" % name, TRES, RES)
                elif name == "partner_id":
                    if tgt_ver == "6.1":
                        TRES = False
                    else:
                        TRES = vals[name]
                    sts = self.Z.test_result(z0ctx, "cvt(%s)" % name, TRES, RES)
                elif name == "email":
                    if tgt_ver == "6.1":
                        TRES = "user_email"
                    else:
                        TRES = name
                    sts = self.Z.test_result(z0ctx, "cvt(%s)" % name, TRES, new_name)
        return sts

    def __test_05(self, z0ctx):
        sts = TEST_SUCCESS
        ctx = self.ctx
        model = "res.users"
        vals = {"name": "admin", "partner_id": 1, "email": "myname@example.com"}
        for tgt_ver in ("12.0", "11.0", "10.0", "9.0", "8.0", "7.0", "6.1"):
            if not z0ctx["dry_run"]:
                new_vals = clodoo.cvt_from_ver_2_ver(ctx, model, "7.0", tgt_ver, vals)
            else:
                new_vals = vals
            if tgt_ver == "6.1":
                TRES = ["name", "user_email"]
            else:
                TRES = sorted(vals.keys())
            sts = self.Z.test_result(
                z0ctx, "cvt_rec(res.users)", TRES, sorted(new_vals.keys())
            )
        return sts


#
# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )
