# -*- coding: utf-8 -*-
#
# Copyright SHS-AV s.r.l. <http://www.zeroincombenze.org>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
#    All Rights Reserved
#
"""Clodoo core functions
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library

# from builtins import int
from past.builtins import basestring, long
from builtins import str

from past.utils import old_div
import os
import sys
import datetime
import re
import inspect
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

try:
    import odoorpc
except ImportError:
    raise ImportError("Package odoorpc not found!")
if sys.version_info[0] == 2:
    try:
        import oerplib
    except ImportError:
        raise ImportError("Package oerplib not found!")
else:
    try:
        import oerplib3 as oerplib
    except ImportError:
        raise ImportError("Package oerplib3 not found!")

# from os0 import os0
from python_plus import str2bool, _u
try:
    from z0lib.z0lib import z0lib
except ImportError:
    try:
        from z0lib import z0lib
    except ImportError:
        import z0lib
try:
    from clodoolib import debug_msg_log, msg_log, decrypt, crypt
except ImportError:
    from clodoo.clodoolib import debug_msg_log, msg_log, decrypt, crypt
try:
    from transodoo import read_stored_dict, translate_from_sym, translate_from_to
except ImportError:
    from clodoo.transodoo import read_stored_dict, translate_from_sym, translate_from_to
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    postgres_drive = True
except BaseException:  # pragma: no cover
    postgres_drive = False
standard_library.install_aliases()  # noqa: E402


STS_FAILED = 1
STS_SUCCESS = 0
CNX_DICT = {
    "odoo_version": "*",
    "admin_passwd": "admin",
    "autoconnect": True,
    "cnx": None,
    "confn": "",
    "crypt_password": "Ec{fu",
    "crypt2_password": "",
    "data_dir": "",
    "dbfilter": ".*",
    "db_host": "localhost",
    "db_name": "demo",
    "db_password": "",
    "db_port": 5432,
    "db_user": "postgres",
    "dry_run": False,
    "http_port": None,
    "lang": "en_US",
    "level": 1,
    "logfile": False,
    "login_user": "admin",
    "login_password": "admin",
    "login2_user": "",
    "login2_password": "",
    "multi_user": False,
    "no_login": False,
    "protocol": None,
    "psycopg2": False,
    "server_version": None,
    "xmlrpc_port": None,
    "_cr": None,
}
CNX_PARAMS = list(CNX_DICT.keys())
OLD_CNX_PARAMS = {
    # "confn": "confn",
    "cnx": "odoo_cnx",
    "odoo_version": "oe_version",
    "protocol": "svc_protocol",
    "odoo_major_version": "majver",
}
SUPPL_PARAMS = [
    "caller",
    "caller_fqn",
    "odoo_major_version",
    "pypi",
    "run_daemon",
    "run_tty",
    "server_version",
    "user"
]

__version__ = "2.0.14"


class Clodoo(object):
    def __init__(self, **kwargs):
        for item in CNX_PARAMS:
            setattr(self, item, kwargs.get(item, CNX_DICT[item]))
        for item in SUPPL_PARAMS:
            setattr(self, item, None)
        stack = inspect.stack()
        ctr = 0
        matched = False
        for ix in range(15):
            if os.path.basename(stack[ix][1]).startswith("clodoo"):
                matched = True
                continue
            if matched:
                break
            ctr += 1
            if ctr > 0:
                break
        self.caller_fqn = inspect.stack()[ix][1]
        self.caller = os.path.splitext(os.path.basename(self.caller_fqn))[0]
        self.confn = self.confn or self.caller + ".conf"
        self.conf_fns = self.confn.split(",")
        self.run_daemon = False if os.isatty(0) else True
        self.run_tty = not self.run_daemon
        self.set_odoo_version(self.odoo_version)
        self.read_config()
        for item in CNX_PARAMS:
            if item in kwargs:
                setattr(self, item, kwargs[item])
        self.env = []
        if self.autoconnect:
            self.connect()
            if self.cnx and not self.no_login:
                self.do_login()
                if self.pypi == "odoorpc":
                    self.env = self.cnx.env

    def set_odoo_version(self, odoo_version):
        if odoo_version and "." in odoo_version:
            self.odoo_version = odoo_version
            self.odoo_major_version = int(odoo_version.split(".")[0])
            if self.odoo_major_version < 6 or self.odoo_major_version > 18:
                self.odoo_major_version = 0
                self.odoo_version = None
        else:
            self.odoo_major_version = 0
            self.odoo_version = odoo_version or "*"

    def get_rpc_port(self):
        if self.odoo_major_version and self.odoo_major_version < 10:
            port = self.xmlrpc_port or self.http_port
        else:
            port = self.http_port or self.xmlrpc_port
        return port or 8069

    def get_rpc_protocol(self):
        if not self.pypi:
            protocol = self.protocol
        elif self.pypi == "oerplib" or (self.odoo_major_version
                                        and self.odoo_major_version < 10):
            protocol = self.protocol or "xmlrpc"
        else:
            protocol = self.protocol or "jsonrpc"
        return protocol

    def read_config(self):
        self._conf_obj = ConfigParser.RawConfigParser({})
        self.conf_fns = self._conf_obj.read(self.conf_fns)
        if self.conf_fns:
            sect = "options"
            for item in CNX_PARAMS:
                item2 = OLD_CNX_PARAMS.get(item)
                if self._conf_obj.has_option(sect, item):
                    value = self._conf_obj.get(sect, item)
                elif item2 and self._conf_obj.has_option(sect, item2):
                    value = self._conf_obj.get(sect, item2)
                else:
                    continue
                if value and value != "False":
                    setattr(self, item, value)

    def connect_oerplib(self, protocol="xmlrpc"):
        try:
            self.cnx = oerplib.OERP(
                server=self.db_host,
                protocol=protocol,
                port=self.get_rpc_port(),
            )
            self.server_version = self.cnx.db.server_version()
            self.protocol = "xmlrpc"
            self.pypi = "oerplib"
        except BaseException:  # pragma: no cover
            self.cnx = None
            self.pypi = self.protocol = ""

    def connect_odoorpc(self, protocol="odoorpc"):
        try:
            self.cnx = odoorpc.ODOO(self.db_host, port=self.get_rpc_port())
            if eval(self.cnx.version.split(".")[0]) < 10:
                raise ValueError("Invalid Odoo version")
            self.server_version = self.cnx.version
            self.protocol = protocol
            self.pypi = "odoorpc"
        except BaseException:  # pragma: no cover
            self.cnx = None
            self.pypi = self.protocol = ""

    def connect(self):
        self.server_version = self.odoo_version if self.odoo_version != "*" else ""
        protocol = self.get_rpc_protocol()
        if not protocol:
            self.connect_odoorpc()
            if not self.protocol:
                self.connect_oerplib()
        elif protocol == "xmlrpc":
            self.connect_oerplib()
        else:
            self.connect_odoorpc()
            if not self.cnx and not self.odoo_major_version:
                # Try if older Odoo version
                self.connect_oerplib()
        if self.odoo_version == "*":
            x = re.match(r"[0-9]+\.[0-9]+", self.server_version)
            self.odoo_version = self.server_version[0: x.end()]
        return self.cnx

    def try_to_login(self, username, pwd):
        if self.pypi == "oerplib":
            try:
                user = self.cnx.login(database=self.db_name, user=username, passwd=pwd)
            except BaseException:
                return False
        else:
            try:
                self.cnx.login(db=self.db_name, login=username, password=pwd)
                user = self.cnx.env.user
            except BaseException:
                return False
        return user

    def do_login(self):
        userlist = []
        for u in self.login_user.split(",") + self.login2_user.split(","):
            if u and u not in userlist:
                userlist.append(u)
        cryptlist = []
        for p in self.login_password.split(",") + self.login2_password.split(","):
            if p:
                p = crypt(p)
                if p not in cryptlist:
                    cryptlist.append(p)
        for p in self.crypt_password.split(",") + self.crypt2_password.split(","):
            if p and p not in cryptlist:
                cryptlist.append(p)

        user = False
        for username in userlist:
            for pwd in cryptlist:
                user = self.try_to_login(username, decrypt(pwd))
                if user:
                    break
            if user:
                break
        if not user:
            return user
        self.user = user
        self.user_id = user.id
        self._pwd = pwd
        if user:
            self.psql_connect()
        return user

    def psql_connect(self):
        self._cr = False
        if postgres_drive and self.psycopg2:
            cnx = psycopg2.connect(dbname=self.db_name,
                                   user=self.db_user,
                                   password=self.db_password,
                                   port=self.db_port)
            cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self._cr = cnx.cursor()
        return self._cr

    def browse(self, model, id, context=None):
        if self.pypi == "oerplib":
            return self.cnx.browse(model, id, context=context)
        if context:
            return self.cnx.env[model].with_context(context).browse(id)
        else:
            return self.cnx.env[model].browse(id)

    def search(self, model, domain, order=None, context=None):
        if self.pypi == "oerplib":
            return self.cnx.search(model, domain, order=order, context=context)
        if context:
            return self.cnx.env[model].with_context(context).search(domain, order=order)
        else:
            return self.cnx.env[model].search(domain, order=order)

    def create(self, model, vals, context=None):
        if self.pypi == "oerplib":
            return self.cnx.create(model, vals, context=context)
        if context:
            return self.cnx.env[model].with_context(context).create(vals)
        else:
            return self.cnx.env[model].create(vals)

    def write(self, model, ids, vals, context=None):
        if self.pypi == "oerplib":
            return self.cnx.write(model, ids, vals, context=context)
        if context:
            return self.cnx.env[model].with_context(context).write(ids, vals)
        else:
            return self.cnx.env[model].write(ids, vals)

    def unlink(self, model, ids, context=None):
        ids = ids if isinstance(ids, (list, tuple)) else [ids]
        if self.pypi == "oerplib":
            return self.cnx.unlink(model, ids, context=context)
        if context:
            return self.cnx.env[model].with_context(context).unlink(ids)
        else:
            return self.cnx.env[model].unlink(ids)

    def execute(self, model, action, *args):
        if self.odoo_major_version < 10 and action == "invoice_open":
            return self.cnx.exec_workflow(model, action, *args)
        else:
            return self.cnx.execute_kw(model, action, *args)

    def return_dict(self):
        ctx = {"self": self}
        for k in CNX_PARAMS + SUPPL_PARAMS:
            v = getattr(self, k)
            if v is not None:
                ctx[OLD_CNX_PARAMS.get(k, k)] = v
        # ctx["majver"] = self.odoo_major_version
        return ctx


#############################################################################
# Low level (driver) functions
def psql_connect(ctx):
    cr = False
    if postgres_drive and ctx.get("psycopg2", False):
        dbname = ctx["db_name"]
        dbuser = ctx["db_user"]
        pwd = ctx.get("db_password")
        port = ctx.get("db_port") or 5432
        cnx = psycopg2.connect(dbname=dbname, user=dbuser, password=pwd, port=port)
        cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cr = cnx.cursor()
    return cr


#############################################################################
# Connection and database
#

def exec_sql(ctx, query, response=None):
    ctx["_cr"] = psql_connect(ctx)
    try:
        ctx["_cr"].execute(query)
        if response:
            response = ctx["_cr"].fetchall()
        else:
            response = True
    except psycopg2.OperationalError:
        # os0.wlog("Error executing sql %s" % query)
        response = False
    try:
        ctx["_cr"].close()
    except psycopg2.OperationalError:
        pass
    return response


def sql_reconnect(ctx):
    try:
        ctx["_cr"].close()
    except BaseException:
        pass
    ctx["_cr"] = psql_connect(ctx)


def connectL8(ctx):
    """Open connection to Odoo service"""
    if ctx.get("odoo_vid") and not ctx("odoo_version"):
        ctx["odoo_version"] = ctx["odoo_vid"]
    if ctx.get("db") and not ctx("db_name"):
        ctx["db_name"] = ctx["db"]
    if ctx.get("self"):
        del ctx["self"]
    self = Clodoo(**ctx)
    odoo = self.cnx
    ctx.update(self.return_dict())
    if not odoo:
        if ctx["oe_version"] != "*":
            return "!Odoo server %s is not running!" % ctx["oe_version"]
    else:
        x = re.match(r"[0-9]+\.[0-9]+", ctx["server_version"])
        if ctx["server_version"][0: x.end()] != ctx["oe_version"]:
            return "!Invalid Odoo Server version: expected %s, found %s!" % (
                ctx["oe_version"],
                ctx["server_version"],
            )
    return odoo


#############################################################################
# Primitive version indipendent
#
def create_model_object(ctx, resource, id, deep=3):
    model = ctx["odoo_session"].get_model(resource)
    values = model.read(id, [])
    fields = model.fields_get()
    for k, v in values.items():
        if k == "id":
            setattr(model, k, v)
        elif fields[k]["type"] == "many2one":
            if v and deep:
                rel_model = fields[k]["relation"]
                setattr(
                    model, k, create_model_object(ctx, rel_model, v[0], deep=deep - 1)
                )
            else:
                setattr(model, k, v)
        elif fields[k]["type"] in ("one2many", "many2many"):
            setattr(model, k, v)
        else:
            setattr(model, k, v)
    return model


def searchL8(ctx, model, domain, order=None, context=None):
    return ctx["self"].search(model, domain, order, context=context)


def browseL8(ctx, model, id, context=None):
    return ctx["self"].browse(model, id, context=context)


def createL8(ctx, model, vals, context=None):
    vals = drop_invalid_fields(ctx, model, vals)
    vals = complete_fields(ctx, model, vals)
    return ctx["self"].create(model, vals, context=context)


def writeL8(ctx, model, ids, vals, context=None):
    vals = drop_invalid_fields(ctx, model, vals)
    return ctx["self"].write(model, ids, vals, context=context)


def unlinkL8(ctx, model, ids, context=None):
    return ctx["self"].unlink(model, ids, context=context)


def executeL8(ctx, model, action, *args):
    action = translate_from_to(
        ctx, model, action, "10.0", ctx["oe_version"], type="action"
    )
    return ctx["self"].execute(model, action, args)


def execute_action_L8(ctx, model, action, ids):
    sts = 0
    if model == "account.invoice":
        ids = [ids] if isinstance(ids, (int, long)) else ids
        try:
            if ctx["majver"] >= 10:
                executeL8(ctx, model, "compute_taxes", ids)
            else:
                executeL8(ctx, model, "button_compute", ids)
                executeL8(ctx, model, "button_reset_taxes", ids)
                ids = ids[0]
        except RuntimeError:
            pass
    elif model == "sale.order":
        ids = [ids] if isinstance(ids, (int, long)) else ids
        try:
            executeL8(ctx, model, "compute_tax_id", ids)
        except RuntimeError:
            pass
    executeL8(ctx, model, action, ids)
    return sts


###########################################################
# Version adaptive functions
#
def drop_fields(ctx, model, vals, to_delete):
    for name in to_delete:
        if isinstance(vals, (list, tuple)):
            del vals[vals.index(name)]
        else:
            del vals[name]
        msg = "Invalid field %s of %s)" % (name, model)
        debug_msg_log(ctx, 6, msg)
    return vals


def complete_fields(ctx, model, vals):
    to_delete = []
    for name in ctx.get("STRUCT", {}).get(model, {}):
        if is_required_field(ctx, model, name) and (name not in vals or not vals[name]):
            vals[name] = set_some_values(ctx, None, name, "", model=model, row=vals)
            if not vals.get(name):
                to_delete.append(name)
    return drop_fields(ctx, model, vals, to_delete)


def drop_invalid_fields(ctx, model, vals):
    if model in ctx.get("STRUCT", {}).get(model, {}):
        if isinstance(vals, (list, tuple)):
            to_delete = list(set(vals) - set(ctx["STRUCT"][model].keys()))
        else:
            to_delete = list(set(vals.keys()) - set(ctx["STRUCT"][model].keys()))
        return drop_fields(ctx, model, vals, to_delete)
    return vals


def tnl_2_ver_seq_code(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    if src_ver == "10.0" and tgt_ver == "8.0":
        if not searchL8(ctx, "ir.sequence.type", [("code", "=", vals[new_name])]):
            createL8(
                ctx,
                "ir.sequence.type",
                {"code": vals[new_name], "name": vals[new_name].replace(".", " ")},
            )
    if name != new_name:
        del vals[name]
    return vals


def tnl_2_ver_acc_type(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    TNL_9_TO_10 = {
        "income": "other",
        "none": "other",
        "liability": "payable",
        "asset": "other",
        "expense": "other",
    }
    TNL_10_TO_9 = {
        "receivable": "asset",
        "liquidity": "asset",
        "payable": "liability",
        "other": "none",
    }
    tbl = False
    src_v = eval(src_ver.split(".")[0])
    tgt_v = eval(tgt_ver.split(".")[0])
    if src_v < 10 and tgt_v >= 10:
        tbl = TNL_9_TO_10
    elif src_v >= 10 and tgt_v < 10:
        tbl = TNL_10_TO_9
    if tbl:
        vals[new_name] = tbl[vals[name]]
    # vals[new_name] = translate_from_to(ctx,
    #                                    model,
    #                                    vals[name],
    #                                    src_ver,
    #                                    tgt_ver,
    #                                    type='value',
    #                                    fld_name='report_type')
    if name != new_name:
        del vals[name]
    return vals


def tnl_2_ver_group(ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None):
    """Type Group"""
    if name != new_name:
        del vals[name]
    if new_name in vals and src_ver == "10.0" and tgt_ver == "8.0":
        if vals[new_name] == "group":
            vals["child_depend"] = True
            del vals[new_name]
    return vals


def tnl_2_ver_type_tax_use(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    if vals.get(new_name) not in ("sale", "purchase"):
        if vals["description"][-1] == "v":
            vals[new_name] = "sale"
        else:
            vals[new_name] = "purchase"
        if vals["type_tax_use"] == "sale":
            code = "IT%s%sD" % ("D", vals["description"][0:-1])
            ids = searchL8(ctx, "account.tax.code", [("code", "=", code)])
            if ids:
                vals["base_code_id"] = ids[0]
                vals["ref_base_code_id"] = ids[0]
            code = "IT%s%sV" % ("D", vals["description"][0:-1])
            ids = searchL8(ctx, "account.tax.code", [("code", "=", code)])
            if ids:
                vals["tax_code_id"] = ids[0]
                vals["ref_tax_code_id"] = ids[0]
        elif vals["type_tax_use"] == "purchase":
            code = "IT%s%sD" % ("C", vals["description"][0:-1])
            ids = searchL8(ctx, "account.tax.code", [("code", "=", code)])
            if ids:
                vals["base_code_id"] = ids[0]
                vals["ref_base_code_id"] = ids[0]
            code = "IT%s%sV" % ("C", vals["description"][0:-1])
            ids = searchL8(ctx, "account.tax.code", [("code", "=", code)])
            if ids:
                vals["tax_code_id"] = ids[0]
                vals["ref_tax_code_id"] = ids[0]
    if name != new_name:
        del vals[name]
    return vals


def tnl_2_ver_tax_amount(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    if src_ver == "10.0" and tgt_ver == "8.0":
        vals[new_name] = old_div(vals[new_name], 100)
    elif src_ver == "8.0" and tgt_ver == "10.0":
        vals[new_name] = vals[new_name] * 100
    if name != new_name:
        del vals[name]
    return vals


def tnl_2_ver_vat(ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None):
    """External vat may not contain ISO code"""
    if (
        isinstance(vals[new_name], basestring)
        and len(vals[new_name]) == 11
        and vals[new_name].isdigit()
    ):
        vals[new_name] = "IT%s" % vals[new_name]
    else:
        vals[new_name] = vals[new_name]
    if name != new_name:
        del vals[name]
    return vals


def tnl_2_ver_state_id(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    if "country_id" in vals:
        vals[new_name] = get_state_id(
            ctx, vals[new_name], country_id=vals["country_id"]
        )
    else:
        vals[new_name] = get_state_id(ctx, vals[new_name])
    if name != new_name:
        del vals[name]
    return vals


def tnl_2_ver_child_id(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    if eval(tgt_ver.split(".")[0]) >= 10 and vals[name]:
        vals = {}
    return vals


def tnl_2_ver_set_value(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    vals[new_name] = default
    if name != new_name:
        del vals[name]
    return vals


def tnl_2_ver_drop_record(
    ctx, model, vals, new_name, name, src_ver, tgt_ver, default=None
):
    vals = {}
    return vals


def cvt_from_ver_2_ver(ctx, model, src_ver, tgt_ver, vals):
    APPLY = {
        "account.account.type": {"type": "acc_type()", "report_type": "acc_type()"},
        "account.account": {"child_id": "child_id()"},
        "account.tax": {"type": "group()", "type_tax_use": "type_tax_use()"},
        "res.partner": {"is_company": "true", "vat": "vat()", "state_id": "state_id()"},
        "ir.sequence": {"code": "seq_code()"},
    }

    def process_fields(
        ctx, model, vals, src_ver, tgt_ver, field_list=None, excl_list=None
    ):
        for name in vals.copy():
            new_name = translate_from_to(ctx, model, name, src_ver, tgt_ver)
            if not new_name:
                new_name = name
            if name == "company_id":
                if ctx.get("by_company"):
                    vals[name] = ctx["company_id"]
            elif model in APPLY:
                default = ""
                if new_name in APPLY[model]:
                    default = APPLY[model][new_name]
                if field_list and new_name and new_name not in field_list:
                    continue
                if excl_list and new_name and new_name in excl_list:
                    continue
                if default.endswith("()"):
                    apply = "tnl_2_ver_%s" % default[:-2]
                    default = False
                elif default:
                    apply = "tnl_2_ver_set_value"
                    if default == "true":
                        default = str2bool(default, True)
                else:
                    apply = ""
                if not apply or apply not in list(globals()):
                    if name != new_name:
                        vals[new_name] = vals[name]
                        del vals[name]
                    continue
                if not new_name:
                    vals = globals()[apply](
                        ctx, model, vals, name, name, src_ver, tgt_ver, default=default
                    )
                else:
                    vals = globals()[apply](
                        ctx,
                        model,
                        vals,
                        new_name,
                        name,
                        src_ver,
                        tgt_ver,
                        default=default,
                    )
                if not vals:
                    break
        return vals

    if ctx.get("mindroot"):
        if not ctx.get("by_company") and "company_id" in vals:
            ctx["company_id"] = vals["company_id"]
        elif model_has_company(ctx, model):
            ctx["company_id"] = ctx["def_company_id"]
        if ctx.get("company_id"):
            ctx["country_id"] = browseL8(
                ctx, "res.company", ctx["company_id"]
            ).partner_id.country_id.id
        else:
            ctx["country_id"] = False
        pf_list = ("company_id", "country_id", "street")
        vals = process_fields(ctx, model, vals, src_ver, tgt_ver, field_list=pf_list)
        vals = process_fields(ctx, model, vals, src_ver, tgt_ver, excl_list=pf_list)
    return vals


def extr_table_generic(ctx, model, keys=None, alls=None):
    get_model_structure(ctx, model)
    field_names = []
    for field in ctx["STRUCT"][model]:
        if (
            alls
            or (keys and field in keys)
            or (not keys and not ctx["STRUCT"][model][field]["readonly"])
        ):
            field_names.append(field)
    return field_names


def get_val_from_field(ctx, model, rec, field, format=False):
    if not hasattr(rec, field):
        return None
    res = rec[field]
    if res:
        if callable(rec[field]):
            return None
        get_model_structure(ctx, model)
        if ctx["STRUCT"][model][field]["ttype"] in ("many2many", "one2many"):
            res = []
            for id in rec[field]:
                res.append(id.id)
            if format == "cmd":
                res = [(6, 0, res)]
        elif ctx["STRUCT"][model][field]["ttype"] in ("date", "datetime"):
            if format in ("cmd", "str"):
                res = str(res)
        elif ctx["STRUCT"][model][field]["ttype"] == "many2one":
            res = rec[field].id
            if format == "cmd":
                res = [(6, 0, res)]
        elif ctx["STRUCT"][model][field]["ttype"] == ("integer", "float"):
            if format == "cmd":
                res = str(res)
    return res


def extract_vals_from_rec(ctx, model, rec, keys=None, format=False):
    if keys:
        if isinstance(keys, dict):
            field_names = keys.keys()
        elif isinstance(keys, list):
            field_names = keys
        else:
            keys = None
    if not keys:
        func = "extr_table_%s" % model
        func = func.replace(".", "_")
        if func in globals():
            field_names = globals()[func](ctx)
        else:
            field_names = extr_table_generic(ctx, model)
    res = {}
    for field in field_names:
        res[field] = get_val_from_field(ctx, model, rec, field, format=format)
    return res


FIX_7_0 = {
    "res.partner": {"name": {"required": True}},
    "product.product": {"name": {"required": True}},
    "product.template": {"name": {"required": True}},
    "res.users": {"name": {"required": True}},
    "account.invoice": {
        "company_id": {"readonly": False},
        "number": {"readonly": False},
        "date_invoice": {"readonly": False},
        "journal_id": {"readonly": False},
        "account_id": {"readonly": False},
        "amount_tax": {"readonly": False},
        "amount_total": {"readonly": False},
        "amount_untaxed": {"readonly": False},
        "internal_number": {"readonly": False},
        "move_id": {"readonly": False},
        "name": {"readonly": False},
        "partner_id": {"readonly": False},
    },
    "account.invoice.line": {
        "company_id": {"readonly": False},
        "number": {"readonly": False},
        "date_invoice": {"readonly": False},
        "journal_id": {"readonly": False},
    },
}
FIX_ALL = {
    "message_follower_ids": {"readonly": True},
    "message_ids": {"readonly": True},
    "message_is_follower": {"readonly": True},
    "message_summary": {"readonly": True},
    "message_unread": {"readonly": True},
}


def get_model_structure(ctx, model, ignore=None):
    read_stored_dict(ctx)
    ignore = ignore or []
    if ctx.get("STRUCT", {}).get(model, {}) and not ignore:
        return
    ctx["STRUCT"] = ctx.get("STRUCT", {})
    ctx["STRUCT"][model] = ctx["STRUCT"].get(model, {})
    ir_model = "ir.model.fields"
    for field in browseL8(
        ctx, ir_model, searchL8(ctx, ir_model, [("model", "=", model)])
    ):
        res = FIX_7_0.get(model, {}).get(field, {}).get("required", None)
        required = res if res is not None else field.required
        if (
            field.name == "id"
            or (ctx["majver"] >= 9 and field.compute)
            or field.name in ignore
            or field.ttype in ("binary", "reference")
        ):
            readonly = True
        else:
            readonly = FIX_ALL.get(model, {}).get(field, {}).get(
                "readonly", False
            ) or FIX_7_0.get(model, {}).get(field, {}).get("readonly", False)
        ctx["STRUCT"][model][field.name] = {
            "ttype": field.ttype,
            "relation": field.relation,
            "required": required,
            "readonly": readonly,
        }
    # FIX for Odoo 7.0
    field = "id"
    if field not in ctx["STRUCT"][model]:
        ctx["STRUCT"][model][field] = {
            "ttype": "integer",
            "relation": False,
            "required": False,
            "readonly": True,
        }
    field = "name"
    if model in ("res.users", "res.partner", "product.product", "product.template"):
        if field not in ctx["STRUCT"][model]:
            ctx["STRUCT"][model][field] = {
                "ttype": "char",
                "relation": False,
                "required": True,
                "readonly": False,
            }


def build_model_struct(ctx):
    o_model = {}
    for p in (
        "model",
        "model_code",
        "model_name",
        "model_action",
        "model_keyids",
        "hide_cid",
        "alias_model2",
        "alias_field",
    ):
        if p in ctx:
            o_model[p] = ctx[p]
    if not o_model.get("model_code") and not o_model.get("model_name"):
        o_model["model_code"] = "id"
    if not o_model.get("model_keyids") and ctx.get("header_id"):
        o_model["model_keyids"] = ctx["header_id"]
    return o_model


def get_model_model(ctx, o_model):
    if "model" in o_model:
        if isinstance(o_model["model"], basestring):
            model = o_model["model"]
        else:
            model_selector = o_model.get("cur_model", o_model["model"].keys()[0])
            model = o_model["model"][model_selector]
    else:
        model = False
    return model


def get_model_name(ctx, o_model):
    if "model_name" in o_model:
        if isinstance(o_model["model_name"], basestring):
            model_name = o_model["model_name"]
        else:
            model_selector = o_model.get("cur_model", o_model["model_name"].keys()[0])
            model_name = o_model["model_name"][model_selector]
    else:
        model_name = False
    return model_name


def get_res_users(ctx, user, field):
    if field == "name":
        if ctx["oe_version"] == "6.1":
            return user.name
        else:
            return user.partner_id.name
    elif field == "lang":
        if ctx["oe_version"] == "6.1":
            return user.context_lang
        else:
            return user.partner_id.lang
    elif field == "email":
        if ctx["oe_version"] == "6.1":
            return user.user_email
        else:
            return user.partner_id.email
    elif field == "country_id":
        if ctx["oe_version"] == "6.1":
            if user.company_id.country_id:
                return user.company_id.country_id.id
            return False
        else:
            if user.partner_id.country_id:
                return user.partner_id.country_id.id
            elif user.company_id.country_id:
                return user.company_id.country_id.id
            return False
    return user[field]


###########################################################
# Others
#
def _get_model_bone(ctx, o_model):
    """Inherit model structure from a parent model"""
    model = None
    hide_cid = False
    if ctx is not None:
        if "model" in ctx:
            model = ctx["model"]
            if model == "":
                model = None
            else:
                if "hide_cid" in ctx:
                    hide_cid = ctx["hide_cid"]
                else:
                    hide_cid = not model_has_company(ctx, model)
    if model is None:
        if "model" in o_model:
            model = o_model["model"]
            if model == "":
                model = None
            if "hide_cid" in o_model:
                hide_cid = o_model["hide_cid"]
            else:
                hide_cid = not model_has_company(ctx, model)
    return model, hide_cid


def _import_file_model(ctx, o_model, csv_fn):
    """Get model name of import file"""
    model, hide_cid = _get_model_bone(ctx, o_model)
    if model is None:
        model = z0lib.nakedname(csv_fn).replace("-", ".").replace("_", ".")
    return model, hide_cid


def _get_model_code(ctx, o_model):
    """Get key field(s) name of  model"""
    if "model_code" in o_model:
        code = o_model["model_code"]
    elif "code" in o_model:
        code = o_model["code"]
    elif "name" in o_model:
        code = o_model["name"]
    elif "code" in ctx:
        code = "code"
    elif "name" in ctx:
        code = "name"
    elif "id" in ctx:
        code = "id"
    else:
        code = "name"
    return code


def _get_model_name(ctx, o_model):
    """Get description field(s) name of  model"""
    if "model_name" in o_model:
        name = o_model["model_name"]
    elif "name" in o_model:
        name = o_model["name"]
    elif "code" in o_model:
        name = o_model["code"]
    elif "name" in ctx:
        name = "name"
    elif "code" in ctx:
        name = "code"
    else:
        name = "name"
    return name


def _import_file_dbtype(o_model, fields, csv_fn):
    """Get db selector name of import file"""
    if "db_type" in o_model:
        db_type = o_model["db_type"]
    elif "db_type" in fields:
        db_type = "db_type"
    else:
        db_type = False
    return db_type


def import_file_get_hdr(ctx, o_model, csv_obj, csv_fn, row):
    """Analyze csv file header and get header names
    Header will be used to load value in table
    @ return:
    @ ['tables']       table aliases, if import many tables
                       i.e. {'H': 'move', 'D': 'move.line'}
    @ ['model']        model name
    @ ['hide_cid']     do not add company_id
    @ ['name']         field name which is the record description
    @ ['code']         field name which is the record key
    @ ['db_type']      db type to record selection
    @ ['repl_by_id']   search by id if no record name found
    @ ['hide_id']      if true, no id will be returned
    @ ['alias_field']  field name to create external identifier
    @ ['alias_field2'] field name to create external identifier of many2one
    Returned fields may be text if import just 1 table or
    dictionary if import more tables; key is table id
    i.e. return['name'] = {'A': 'name', 'B': 'name'}
    """
    o_skull = o_model.copy()
    csv_obj.fieldnames = row["undef_name"]
    o_skull["model"], o_skull["hide_cid"] = _import_file_model(ctx, o_model, csv_fn)
    o_skull["name"] = _get_model_name(csv_obj.fieldnames, o_model)
    o_skull["code"] = _get_model_code(csv_obj.fieldnames, o_model)
    o_skull["db_type"] = _import_file_dbtype(o_model, csv_obj.fieldnames, csv_fn)
    if o_skull["code"] != "id" and "id" in csv_obj.fieldnames:
        o_skull["repl_by_id"] = True
    else:
        o_skull["repl_by_id"] = False
    o_skull["hide_id"] = True
    o_skull["alias_model2"] = o_model.get("alias_model2", "")
    o_skull["alias_field"] = o_model.get("alias_field", "")
    return o_skull


def get_company_id(ctx):
    value = get_db_alias(ctx, "z0bug.mycompany")
    if not value or (isinstance(value, basestring) and not value.isdigit()):
        model = "res.company"
        company_name = ctx.get("company_name", "La % Azienda")
        ids = searchL8(ctx, model, [("name", "ilike", company_name)])
        if not ids:
            ids = searchL8(ctx, model, [("id", ">", 1)])
        if ids:
            value = ids[0]
        else:
            value = 1
    if "company_id" not in ctx and isinstance(value, (int, long)):
        ctx["company_id"] = value
    return value


def get_country_id(ctx, value):
    if value:
        model = "res.country"
        if value[0:5] == "base.":
            ids = searchL8(ctx, model, [("code", "=", value[5:].upper())])
        else:
            ids = searchL8(ctx, model, [("code", "=", value.upper())])
        if not ids:
            ids = searchL8(ctx, model, [("name", "ilike", value)])
        if ids:
            value = ids[0]
        else:
            value = False
    else:
        value = ctx["def_country_id"]
    return value


def get_state_id(ctx, value, country_id=None):
    if value:
        if not country_id:
            country_id = ctx["def_country_id"]
        model = "res.country.state"
        ids = searchL8(
            ctx, model, [("country_id", "=", country_id), ("code", "=", value.upper())]
        )
        if not ids:
            ids = searchL8(
                ctx, model, [("country_id", "=", country_id), ("name", "ilike", value)]
            )
        if ids:
            value = ids[0]
        else:
            value = False
    return value


def set_null_val_code_n_name(ctx, name, val, row=None):
    if name == "code":
        if row and "name" in row:
            value = hex(hash(row["name"]))[2:]
        else:
            value = hex(hash(datetime.datetime.now().microsecond))[2:]
    return value


def set_null_val_account_account_type(ctx, name, val, row=None):
    return set_null_val_code_n_name(ctx, name, val, row=row)


def set_null_val_account_account(ctx, name, val, row=None):
    if name == "code":
        return set_null_val_code_n_name(ctx, name, val, row=row)
    return val


def set_null_val_account_tax(ctx, name, val, row=None):
    if name == "applicable_type":
        return "true"
    return val


def set_null_val_account_invoice(ctx, name, val, row=None):
    if name == "state":
        return "draft"
    return val


def set_null_val_ir_sequence(ctx, name, val, row=None):
    if name == "number_increment":
        return 1
    return val


def set_some_values(ctx, o_model, name, value, model=None, row=None):
    """Set default value for empties fields"""
    if not model:
        model = get_model_model(ctx, o_model)
    if not value and name in ctx.get("DEFAULT", ""):
        value = ctx["DEFAULT"][name]
    elif name == "company_id":
        if not value:
            value = ctx["company_id"]
    elif name == "country_id":
        value = get_country_id(ctx, value)
    else:
        func = "set_null_val_%s" % model.replace(".", "_")
        if func in globals():
            return globals()[func](ctx, name, value, row=row)
        elif model == "res.partner":
            if name == "is_company":
                return True
            elif name == "vat":
                if ctx.get("country_code") == "IT" and value.isdigit():
                    value = "IT%011d" % eval(value)
            elif name == "state_id":
                if row and "country_id" in row:
                    value = get_state_id(ctx, value, country_id=row["country_id"])
                else:
                    value = get_state_id(ctx, value)
        elif model == "res.users":
            if name == "email":
                if ctx["with_demo"]:
                    return ctx["def_email"]
                elif not ctx["with_demo"]:
                    return ctx["zeroadm_mail"]
    return value


def eval_value(ctx, o_model, name, value):
    """Evaluate value read from csv file: may be a function or macro
    @ ctx:         global parameters
    @ o_model:     special names
    @ name:        field name
    @ value:       field value (constant, macro or expression)
    """
    name = _u(name)
    value = _u(value)
    msg = "eval_value(name=%s, value=%s)" % (name, value)
    debug_msg_log(ctx, 6, msg)
    if not value and o_model:
        return set_some_values(ctx, o_model, name, value)
    elif isinstance(value, basestring):
        eval_dict = True
        token = "$1$!" if isinstance(value, str) else b"$1$!"
        if value.startswith(token):
            value = decrypt(value[4:])
        if is_db_alias(ctx, value):
            value = get_db_alias(ctx, value)
        else:
            token = "=" if isinstance(value, str) else b"="
            tok_left = "${" if isinstance(value, str) else b"${"
            tok_right = "}" if isinstance(value, str) else b"}"
            tok_beg = "[(" if isinstance(value, str) else b"[("
            tok_end = ")]" if isinstance(value, str) else b")]"
            if value.startswith(token):
                value = expr(ctx, o_model, name, value[1:])
                eval_dict = False
            elif tok_left in value and tok_right in value:
                value = expr(ctx, o_model, name, value)
                eval_dict = False
            elif value.startswith(tok_beg) and value.endswith(tok_end):
                value = expr(ctx, o_model, name, value)
                eval_dict = False
        if isinstance(value, basestring):
            if value in ("None", "True", "False") or (
                value[0:2] == "[(" and value[-2:] == ")]"
            ):
                if eval_dict:
                    try:
                        value = eval(value, None, ctx)
                    except BaseException:  # pragma: no cover
                        pass
                else:
                    try:
                        value = eval(value)
                    except BaseException:  # pragma: no cover
                        pass
            elif value.isdigit():
                ir_model = "ir.model.fields"
                ids = searchL8(
                    ctx, ir_model, [("model", "=", o_model), ("name", "=", name)]
                )
                if ids:
                    ttype = browseL8(ctx, ir_model, ids[0]).ttype
                    if ttype in ("integer", "float", "many2one"):
                        try:
                            value = eval(value)
                        except BaseException:  # pragma: no cover
                            pass
    return value


def expr(ctx, o_model, code, value):
    """Evaluate python expression value"""
    if isinstance(value, basestring):
        i, j = get_macro_pos(value)
        if i >= 0 and j > i:
            v = value[i + 2: j]
            x, y = get_macro_pos(v)
            while x >= 0 and y > i:
                v = expr(ctx, o_model, code, v)
                value = value[0: i + 2] + v + value[j:]
                i, j = get_macro_pos(value)
                v = value[i + 2: j]
                x, y = get_macro_pos(v)
            res = ""
            while i >= 0 and j > i:
                v = value[i + 2: j]
                if v.find(":") >= 0:
                    v = _query_expr(ctx, o_model, code, v)
                else:
                    if v == "zeroadm_email" and ctx["with_demo"]:
                        v = "def_email"
                    try:
                        v = eval(v, None, ctx)
                    except BaseException:  # pragma: no cover
                        pass
                if i > 0:
                    res = concat_res(res, value[0:i])
                value = value[j + 1:]
                res = concat_res(res, v)
                i, j = get_macro_pos(value)
            value = concat_res(res, value)
    if isinstance(value, basestring) and value[0:2] == "[(" and value[-2:] == ")]":
        res = []
        for v in value[2:-2].split(","):
            res.append(get_db_alias(ctx, v, fmt="string"))
        value = "[(%s)]" % ",".join(res)
    if isinstance(value, basestring):
        value = get_db_alias(ctx, value)
    return value


def _get_simple_query_id(ctx, model, code, value, hide_cid):
    """Execute a simple query to get ids from selection field(s)
    Do not expand value
    @ ctx:         global parameters
    @ model:       model name
    @ code:        field name
    @ value:       field value (just constant)
    @ hide_cid:    hide company_id
    """
    ids = _get_raw_query_id(ctx, model, code, value, hide_cid, "=")
    if model == "ir.model.data" and len(ids) == 1:
        try:
            ids = [browseL8(ctx, "ir.model.data", ids[0]).res_id]
        except BaseException:  # pragma: no cover
            ids = None
    if ids is None:
        return []
    if len(ids) == 0 and model != "res.users":
        ids = _get_raw_query_id(ctx, model, code, value, hide_cid, "ilike")
    return ids


def _get_raw_query_id(ctx, model, code, value, hide_cid, op):
    if not hide_cid and "company_id" in ctx:
        where = [("company_id", "=", ctx["company_id"])]
    else:
        where = []
    if isinstance(code, list) and isinstance(value, list):
        for i, c in enumerate(code):
            if i < len(value):
                where = append_2_where(ctx, model, c, value[i], where, op)
            else:
                where = append_2_where(ctx, model, c, "", where, op)
    else:
        where = append_2_where(ctx, model, code, value, where, op)
    try:
        ids = searchL8(ctx, model, where)
    except BaseException:  # pragma: no cover
        ids = None
    return ids


def append_2_where(ctx, model, code, value, where, op):
    if value is not None and value != "":
        value = eval_value(ctx, model, code, value)
        if isinstance(value, basestring) and value and value[0] == "~":
            where.append("|")
            where.append((code, op, value))
            where.append((code, op, value[1:]))
        elif not isinstance(value, basestring) and op in (
            "like",
            "ilike",
            "=like",
            "=ilike",
        ):
            where.append((code, "=", value))
        else:
            where.append((code, op, value))
    elif code == "country_id":
        where.append((code, "=", ctx["def_country_id"]))
    elif code != "id" and code[-3:] == "_id":
        where.append((code, "=", ""))
    return where


def get_query_id(ctx, o_model, row):
    """Execute a query to get ids from fields in row read from csv
    Value may be expanded
    @ o_model:     special names
    @ ctx:         global parameters
    @ row:         record fields
    """
    model, hide_cid = _get_model_bone(ctx, o_model)
    msg = "get_query_id(model=%s, hide_company=%s)" % (model, hide_cid)
    debug_msg_log(ctx, 6, msg)
    ids = []
    if o_model["repl_by_id"] and row.get("id", None):
        o_skull = o_model.copy()
        o_skull["code"] = "id"
        o_skull["hide_id"] = False
        value = eval_value(ctx, o_skull, "id", row["id"])
        if isinstance(value, (int, long)):
            ids = searchL8(ctx, model, [("id", "=", value)])
    if not ids:
        if o_model["code"].find(",") >= 0:
            code = o_model["code"].split(",")
        else:
            code = o_model["code"]
        if isinstance(code, list):
            value = []
            for p in code:
                value.append(row.get(p, ""))
        else:
            value = row.get(code, "")
        if not value:
            if o_model["name"].find(",") >= 0:
                code = o_model["name"].split(",")
            else:
                code = o_model["name"]
            if isinstance(code, list):
                value = []
                for p in code:
                    value.append(row.get(p, ""))
            else:
                value = row.get(code, "")
        if model is None or not value:
            ids = []
        else:
            ids = _get_simple_query_id(ctx, model, code, value, hide_cid)
    return ids


def _query_expr(ctx, o_model, code, value):
    msg = "_quer_expr(value=%s)" % value
    debug_msg_log(ctx, 6, msg)
    model, name, value, hide_cid, fldname = _get_model_parms(ctx, o_model, value)
    if model:
        if fldname == "db_type":
            value = o_model.get("db_type", "")
        elif fldname == "oe_versions":
            value = value == ctx["server_version"]
        else:
            value = _get_simple_query_id(ctx, model, name, value, hide_cid)
            if isinstance(value, list):
                if len(value):
                    value = value[0]
                    if fldname != "id":
                        o = browseL8(ctx, model, value)
                        value = getattr(o, fldname)
                else:
                    value = None
    return value


def is_valid_field(ctx, model, name):
    get_model_structure(ctx, model)
    if name in ctx["STRUCT"][model]:
        return True
    return False


def is_required_field(ctx, model, name):
    get_model_structure(ctx, model)
    if name in ctx["STRUCT"][model]:
        return ctx["STRUCT"][model][name]["required"]
    return False


def model_has_company(ctx, model):
    return is_valid_field(ctx, model, "company_id")


def get_macro_pos(value):
    i = value.find("${")
    o = 0
    j = value.find("}", o)
    if i >= 0:
        p = i + 2
        k = value.find("${", p)
    else:
        k = -1
    while k >= 0 and j >= 0 and k < j:
        o = j + 1
        j = value.find("}", o)
        p = k + 1
        k = value.find("${", p)
    return i, j


def _get_model_parms(ctx, o_model, value):
    """Extract model parameters and pure value from value and structure"""
    model, hide_cid = _get_model_bone(ctx, o_model)
    sep = "::"
    name = "name"
    fldname = "id"
    i = value.find(sep)
    if i >= 0:
        hide_cid = False
    else:
        sep = ":"
        i = value.find(sep)
        if i >= 0:
            hide_cid = True
    if i < 0:
        n, v = is_db_alias(ctx, value)
        if n:
            model = "ir.model.data"
            name = ["module", "name"]
            value = v
            hide_cid = True
        else:
            model = None
            try:
                value = eval(value, None, ctx)
            except BaseException:  # pragma: no cover
                pass
    else:
        model = value[:i]
        value = value[i + len(sep):]
        model, fldname = _get_name_n_ix(model, deflt=fldname)
        model, x = _get_name_n_params(model, name)
        if x.find(",") >= 0:
            name = x.split(",")
            value = value.split(",")
        else:
            name = x
    return model, name, value, hide_cid, fldname


def concat_res(res, value):
    if isinstance(res, basestring) and res:
        if isinstance(value, basestring):
            res = res + value
        elif isinstance(value, (bool, int, long, float)):
            res = res + str(value)
    elif isinstance(res, (bool, int, long, float)):
        if isinstance(value, basestring) and value:
            res = str(res) + value
        elif isinstance(value, (bool, int, long, float)):
            res = str(res) + str(value)
    else:
        res = value
    return res


def is_db_alias(ctx, value):
    model, name, value, hide_cid = get_model_alias(value)
    if model == "ir.transodoo":
        if value[2] and value[2] != "0":
            return (
                translate_from_to(
                    ctx, value[0], name, value[1], value[2], ctx["oe_version"]
                )
                != ""
            )
        else:
            return translate_from_sym(ctx, value[0], value[1], ctx["oe_version"]) != ""
    if ctx["pypi"] == "odoorpc":
        if (
            model
            and name
            and value
            and ctx["odoo_session"]
            .env[model]
            .search([(name[0], "=", value[0]), (name[1], "=", value[1])])
        ):
            return True
    else:
        if (
            model
            and name
            and value
            and searchL8(
                ctx, model, [(name[0], "=", value[0]), (name[1], "=", value[1])]
            )
        ):
            return True
    return False


def get_db_alias(ctx, value, fmt=None):
    if is_db_alias(ctx, value):
        model, name, value, hide_cid = get_model_alias(value)
        if model == "ir.transodoo":
            if value[2] and value[2] != "0":
                return translate_from_to(
                    ctx, value[0], value[1], value[2], ctx["oe_version"]
                )
            else:
                return translate_from_sym(ctx, value[0], value[1], ctx["oe_version"])
        ids = _get_simple_query_id(ctx, model, name, value, hide_cid)
        if isinstance(ids, list):
            if len(ids):
                if name == "id" or isinstance(name, list):
                    value = ids[0]
                    if fmt == "string":
                        value = str(value)
                else:
                    o = browseL8(ctx, model, ids[0])
                    value = getattr(o, name)
            else:
                value = None
    return value


def get_model_alias(value):
    if value:
        items = value.split(".")
        if (
            len(items) == 3
            and items[0]
            and items[0][0].isalpha()
            and items[-1]
            and items[-1][0].isdigit()
        ):
            model = "ir.transodoo"
            name = ["module", "name", "version"]
            value = [items[0], items[1], items[2]]
            hide_cid = True
            return model, name, value, hide_cid
        elif len(items) == 2 and items[0] and items[0][0].isalpha():
            model = "ir.model.data"
            name = ["module", "name"]
            value = [items[0], items[1]]
            hide_cid = True
            return model, name, value, hide_cid
    return None, None, value, None


def put_model_alias(ctx, model=None, name=None, ref=None, id=None, module=None):
    if ref:
        refs = ref.split(".")
        if len(refs):
            if not module:
                module = refs[0]
            if not name:
                name = refs[1]
    module = module or "base"
    if model and name and id:
        ids = searchL8(
            ctx,
            "ir.model.data",
            [("model", "=", model), ("module", "=", module), ("name", "=", name)],
        )
        if ids:
            writeL8(ctx, "ir.model.data", ids, {"res_id": id})
        else:
            vals = {"module": module, "model": model, "name": name, "res_id": id}
            createL8(ctx, "ir.model.data", vals)
    else:
        msg = "Invalid alias ref"
        msg_log(ctx, ctx["level"], msg)


def _get_name_n_params(name, deflt=None):
    """Extract name and params from string like 'name(params)'"""
    deflt = "" if deflt is None else deflt
    i = name.find("(")
    j = name.rfind(")")
    if i >= 0 and j >= i:
        n = name[:i]
        p = name[i + 1: j]
    else:
        n = name
        p = deflt
    return n, p


def _get_name_n_ix(name, deflt=None):
    """Extract name and subscription from string like 'name[ix]'"""
    deflt = "" if deflt is None else deflt
    i = name.find("[")
    j = name.rfind("]")
    if i >= 0 and j >= i:
        n = name[:i]
        x = name[i + 1: j]
    else:
        n = name
        x = deflt
    return n, x
