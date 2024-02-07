# flake8: noqa
# -*- coding: utf-8 -*-
# Import file library
"""
Import Partner from CSV

This program supplies functions to import records.
#
# Example of client software:
#
import csv
from import_records import (init_n_connect, set_header, add_item)
MYDICT_C = {
    'description': 'name',
}
MYDICT_S = {
}
def main():
    uid, ctx = init_n_connect()
    print("Import data %s on DB %s" % (ctx['flavour'],
                                       ctx['db_name']))
    ctr = 0
    with open(ctx['csv_fn'], 'rbU') as fd:
        hdr = False
        reader = csv.reader(fd, dialect='excel')
        for row in reader:
            if not hdr:
                set_header(ctx, row, 'model', MYDICT_C, MYDICT_S)
                hdr = True
                continue
            add_item(ctx, row)
            ctr += 1
    print('%d record added ...' % ctr)


Parameters as key of ctx:
    default_XXX: value for field XXX if not in csv file
    customers: import customers (from command line)
    company_name: company name to import data
    flavour: suffix to compose csv filename
    suppliers: import suppliers (from command line)
"""

from __future__ import print_function, unicode_literals
from __future__ import absolute_import

# from __future__ import division
from future import standard_library

# from builtins import *                                             # noqa: F403
import sys
import time
import csv

try:
    from python_plus import python_plus
except:
    import python_plus
try:
    from clodoo import clodoo
except:
    import clodoo
try:
    from z0lib import z0lib
except ImportError:
    import z0lib
standard_library.install_aliases()  # noqa: E402


__version__ = "2.0.9"


msg_time = time.time()


def msg_burst(text):
    global msg_time
    t = time.time() - msg_time
    if t > 3:
        print(text)
        msg_time = time.time()


def env_ref(ctx, xref, retxref_id=None):
    xrefs = xref.split(".")
    if len(xrefs) == 2:
        if xref.startswith("product.product_uom_"):
            xrefs[0] = "uom"
        model = "ir.model.data"
        ids = clodoo.searchL8(
            ctx, model, [("module", "=", xrefs[0]), ("name", "=", xrefs[1])]
        )
        if ids:
            if retxref_id:
                return ids[0]
            return clodoo.browseL8(ctx, model, ids[0]).res_id
    return False


def get_company_id(ctx):
    model = "res.company"
    company_id = ctx.get("default_company_id")
    if not company_id:
        company_id = env_ref(ctx, "base.main_company")
    if not company_id:
        company_name = ctx.get("company_name", "La % Azienda")
        ids = clodoo.searchL8(ctx, model, [("name", "ilike", company_name)])
        if not ids:
            ids = clodoo.searchL8(ctx, model, [("id", ">", 1)])
        if ids:
            company_id = ids[0]
        else:
            company_id = 1
    if "default_company_id" not in ctx:
        ctx["default_company_id"] = company_id
    return company_id


def get_many2one(ctx, value, model, parent_name=None, parent_value=None):
    if isinstance(value, basestring):
        rec_id = env_ref(ctx, value)
    elif isinstance(value, int):
        if model not in ctx["BIND"]:
            ctx["BIND"][model] = {}
        src_ctx = {}  # TODO
        if not ctx["BIND"][model].get(value):
            rec = clodoo.browseL8(src_ctx, ctx["model"], value)
            row = clodoo.extract_vals_from_rec(src_ctx, ctx["model"], rec, format="str")
        return ctx["BIND"][model].get(value)
    else:
        return None
    if not rec_id and value:
        if parent_name:
            domain = [(parent_name, "=", parent_value), ("name", "=", value)]
        else:
            domain = [("name", "=", value)]
        ids = clodoo.searchL8(ctx, model, domain)
        if not ids:
            if parent_name:
                domain = [(parent_name, "=", parent_value), ("name", "ilike", value)]
            else:
                domain = [("name", "ilike", value)]
            ids = clodoo.searchL8(ctx, model, domain)
        if ids:
            rec_id = ids[0]
    return rec_id


def get_country_id(ctx, value):
    if value:
        model = "res.country"
        rec_id = get_many2one(ctx, value, model)
        if "default_country_id" not in ctx:
            ctx["default_country_id"] = rec_id
    else:
        rec_id = ctx.get("default_country_id")
    return rec_id


def get_state_id(ctx, value, country_id=None):
    rec_id = False
    if value:
        if value.startswith("l10n_it_base.it_"):
            value = "base.state_it_%s" % value[:-2].lower()
        model = "res.country.state"
        parent_name = "country_id"
        if country_id:
            parent_value = country_id
        else:
            parent_value = get_country_id(ctx, False)
        rec_id = get_many2one(
            ctx, value, model, parent_name=parent_name, parent_value=parent_value
        )
    return rec_id


def get_uom_id(ctx, value):
    if value:
        model = "uom.uom"
        rec_id = get_many2one(ctx, value, model)
        if "uom_id" not in ctx:
            ctx["uom_id"] = rec_id
    else:
        rec_id = ctx.get("uom_id")
    return rec_id


def get_value(ctx, name, value):
    ttype = ctx["STRUCT"][name]["type"]
    if value is None:
        def_field_name = "default_%s" % name
        if def_field_name in ctx:
            value = ctx[def_field_name]
        elif not ctx["STRUCT"][name]["required"]:
            pass
        elif name == "company_id":
            value = get_company_id(ctx)
        elif name == "country_id":
            value = get_country_id(ctx, value)
        elif name == "state_id":
            value = get_state_id(ctx, value)
        elif name == "uom_id":
            value = get_uom_id(ctx, value)
    elif name in ("id", "valuation", "cost_method"):
        value = None
    elif ttype == "many2one":
        value = get_many2one(ctx, value, ctx["model"])
    elif ttype in ("one2many", "many2many"):
        value = get_many2one(ctx, value, ctx["model"])
        if value:
            value = [6, 0, [value]]
        else:
            value = None
    elif ttype == "boolean":
        value = eval(value)
    elif name in ctx["TNL"]:
        value = ctx["TNL"][name].get(value, value)
    return value


def write_log(msg):
    print(msg)
    with open("./import_records.log", "a") as fd:
        fd.write(b"%s\n" % python_plus._b(msg))


def add_item(ctx, row):
    def get_value_by_name(ctx, row, name, supplier=None):
        if supplier:
            if name not in ctx["HDR_SUPPLIER"]:
                return None
            return row[ctx["HDR_SUPPLIER"].index(name)]
        if name not in ctx["HDR_CUSTOMER"]:
            return None
        return row[ctx["HDR_CUSTOMER"].index(name)]

    python_plus.unicodes(row)
    msg_burst("Reading %s ..." % get_value_by_name(ctx, row, "name"))
    vals = {}
    is_customer = get_value_by_name(ctx, row, "customer")
    is_supplier = get_value_by_name(ctx, row, "is_supplier")
    supplier = is_supplier if not is_customer else False
    for ix, field in enumerate(ctx["STRUCT"]):
        if isinstance(row, (tuple, list)):
            value = get_value_by_name(ctx, row, field, supplier=supplier)
        else:
            value = row.get(field)
        vals[field] = get_value(ctx, field, value)
        ttype = ctx["STRUCT"][field]["type"]
        if ttype in ("one2many", "many2many", "many2one"):
            if vals[field]:
                ctx["BIND"][ctx["model"]][value] = vals[field]
            else:
                pass
    for item in list(vals.copy().keys()):
        if vals[item] is None:
            del vals[item]
    domain = []
    for key in ctx["SKEYS"]:
        if key in vals:
            domain.append((key, "=", vals[key]))
    rec_id = False
    if domain:
        ids = clodoo.searchL8(ctx, ctx["model"], domain)
        if 0 < len(ids) < 10:
            rec_id = ids[0]
    if rec_id:
        try:
            clodoo.writeL8(ctx, ctx["model"], rec_id, vals)
        except BaseException as e:
            write_log("Cannot write id %d (%s)" % (rec_id, e))
    else:
        try:
            clodoo.createL8(ctx, ctx["model"], vals)
        except BaseException as e:
            write_log("Cannot create %s (%s)" % (vals, e))


def set_header(ctx, row, model, customer_dict, purchase_dictionary, tnl, skeys):
    HDR_CUSTOMER = []
    HDR_SUPPLIER = []
    for field in row:
        if field.endswith("/id"):
            field = field[:-3]
        if field in customer_dict:
            HDR_CUSTOMER.append(customer_dict[field])
        else:
            HDR_CUSTOMER.append(field)
        if field in purchase_dictionary:
            HDR_SUPPLIER.append(purchase_dictionary[field])
        else:
            HDR_SUPPLIER.append(field)
    ctx["model"] = model
    ctx["HDR_CUSTOMER"] = HDR_CUSTOMER
    ctx["HDR_SUPPLIER"] = HDR_SUPPLIER
    ctx["TNL"] = tnl
    ctx["SKEYS"] = skeys
    ctx["STRUCT"] = clodoo.executeL8(ctx, ctx["model"], "fields_get")
    if "BIND" not in ctx:
        ctx["BIND"] = {}


def copy_db(ctx, src_ctx, MYDICT_C, MYDICT_S, TNL, skeys):
    set_header(ctx, [], ctx["model"], MYDICT_C, MYDICT_S, TNL, skeys)
    ctr = 0
    for rec in clodoo.browseL8(
        src_ctx, ctx["model"], clodoo.searchL8(src_ctx, ctx["model"], [], order="id")
    ):
        msg_burst("%d, %s" % (rec.name, rec.name))
        row = clodoo.extract_vals_from_rec(src_ctx, ctx["model"], rec, format="str")
        add_item(ctx, row)
        ctr += 1


def import_from_csv(ctx, MYDICT_C, MYDICT_S, TNL, skeys):
    ctr = 0
    with open(ctx["csv_fn"], "rbU") as fd:
        hdr = False
        reader = csv.reader(fd, dialect="excel")
        for row in reader:
            if not hdr:
                set_header(ctx, row, ctx["model"], MYDICT_C, MYDICT_S, TNL, skeys)
                hdr = True
                continue
            add_item(ctx, row)
            ctr += 1


def init_n_connect(flavour=None):
    title = "Importrecords %s" % flavour or ""
    parser = z0lib.parseoptargs(
        title, "© 2017-2021 by SHS-AV s.r.l.", version=__version__
    )
    parser.add_argument("-h")
    parser.add_argument(
        "-c",
        "--config",
        help="configuration command file",
        dest="conf_fn",
        metavar="file",
        default="./import_records.config",
    )
    parser.add_argument(
        "-d",
        "--dbname",
        help="DB name",
        dest="db_name",
        metavar="file",
        default="demo8",
    )
    parser.add_argument(
        "-e",
        "--customer",
        help="Import customers",
        action="store_true",
        dest="customers",
        default=False,
    )
    parser.add_argument("-m", "--model", help="Odoo model", dest="model")
    parser.add_argument(
        "-f",
        "--filename",
        help="Filename to import",
        dest="csv_fn",
        metavar="file",
        default=False,
    )
    parser.add_argument("-n")
    parser.add_argument("-q")
    parser.add_argument(
        "-s",
        "--supplier",
        help="Import suppliers",
        action="store_true",
        dest="suppliers",
        default=False,
    )
    parser.add_argument("-V")
    parser.add_argument("-v")
    parser.add_argument(
        "-w",
        "--src-config",
        help="Source DB configuration file",
        dest="src_conf_fn",
        metavar="file",
    )
    parser.add_argument(
        "-x",
        "--src-db_name",
        help="Source database name",
        dest="src_db_name",
        metavar="name",
        default="demo",
    )
    # Connect to DB
    ctx = parser.parseoptargs(sys.argv[1:], apply_conf=False)
    if not ctx.get("csv_fn") and (ctx.get("src_conf_fn") or ctx.get("src_db_name")):
        src_ctx = ctx.copy()
    else:
        src_uid = src_ctx = None
    ctx["flavour"] = flavour
    if not ctx["model"]:
        print("Missed model: use -m switch")
        exit(1)
    if not ctx["customers"] and not ctx["suppliers"]:
        ctx["customers"] = ctx["suppliers"] = True
    if not src_ctx and not ctx["csv_fn"]:
        if flavour:
            sfx = "_"
        else:
            sfx = ""
        ctx["csv_fn"] = "%s%s%s.csv" % (
            ctx["model"].replace(".", "_"),
            sfx,
            flavour or "",
        )
    uid, ctx = clodoo.oerp_set_env(confn=ctx["conf_fn"], db=ctx["db_name"], ctx=ctx)
    if src_ctx:
        src_uid, src_ctx = clodoo.oerp_set_env(
            confn=src_ctx["src_conf_fn"], db=src_ctx["src_db_name"], ctx=src_ctx
        )
    ctx["default_country_id"] = get_country_id(ctx, "Italia")
    ctx["default_is_company"] = True
    return uid, ctx, src_uid, src_ctx


