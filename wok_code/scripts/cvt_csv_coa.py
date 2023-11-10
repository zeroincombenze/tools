#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
usage: cvt_csv_coa.py [-h] -A ACTION -b ODOO_VER -f CSV_ODOO_VER [-n] [-q] [-V]
                        [-v]
                        src_csvfile dst_csvfile

Manage csv file of Odoo CoA

positional arguments:
  src_csvfile
  dst_csvfile

optional arguments:
  -h, --help            show this help message and exit
  -b ODOO_VER, --odoo-branch ODOO_VER
  -m MAX_COL_WIDTH, --max-col-width MAX_COL_WIDTH
  -n, --dry-run         do nothing (dry-run)
  -q, --quiet           silent mode
  -V, --version         show program's version number and exit
  -v, --verbose         verbose mode
"""

from __future__ import print_function, unicode_literals

import csv
import os
import sys
import argparse
import time

from os0 import os0
from python_plus import unicodes
from clodoo import transodoo

__version__ = "2.0.12"

msg_time = time.time()
VALID_ACTIONS = ("export-comparable", "export-full", "export-z0bug", "export-group")
VERSIONS = ["6.1", "7.0", "8.0", "9.0", "10.0", "11.0", "12.0", "13.0", "14.0"]


class CvtCsvFile(object):
    def __init__(self, opt_args):
        self.opt_args = opt_args
        if opt_args.from_version:
            self.from_major_version = int(opt_args.from_version.split(".")[0])
        else:
            self.from_major_version = 0
        self.to_major_version = int(opt_args.to_version.split(".")[0])
        self.ctx = {}
        transodoo.read_stored_dict(self.ctx)

    def set_default_hdr_account(self):
        return {
            "id": {},
            "code": {},
            "name": {},
            "group_id:id": {"rel": "account.group"},
            "reconcile": {"type": "bool"},
            "user_type_id:id": {},
            "internal_type": {},
            "parent_id:id": {},
            "chart_template_id:id": {},
            "company_id:id": {},
            "_requirements": {},
        }

    def set_hdr_out_comparable_account(self):
        return [
            "code",
            "name",
            "user_type_id:id",
        ]

    def set_hdr_out_z0bug_account(self):
        return [
            "id",
            # "_requirements",
            "code",
            "name",
            "user_type_id:id",
            "group_id:id",
            "reconcile",
            "company_id:id",
        ]

    def set_hdr_out_account(self):
        return [
            "id",
            "code",
            "name",
            "user_type_id:id",
            "group_id:id",
            "reconcile",
            "chart_template_id:id",
        ]

    def set_hdr_out_group_account(self):
        return []

    def set_default_hdr_tax(self):
        return {
            "id": {},
            "description": {},
            "name": {},
            "sequence": {},
            "amount": {"type": "float"},
            "amount_type": {"tnl": True},
            "type_tax_use": {"tnl": True},
            "price_include": {"type": "bool"},
            "account_id:id": {"rel": "account.account"},
            "refund_account_id:id": {"rel": "account.account"},
            "kind_id:id": {},
            "rc_type": {"tnl": True},
            "rc_sale_tax_id:id": {},
            "payability": {},
            "tag_ids:id": {},
            "children_tax_ids:id": {},
            "tag_group:id": {"rel": "account.tax.group"},
            "chart_template_id:id": {},
            "company_id:id": {},
            "_requirements": {},
        }

    def set_hdr_out_comparable_tax(self):
        return [
            "description",
            "name",
            "amount",
            "amount_type",
            "type_tax_use",
            "price_include",
        ]

    def set_hdr_out_z0bug_tax(self):
        return [
            "id",
            "_requirements",
            "description",
            "name",
            "sequence",
            "amount",
            "amount_type",
            "type_tax_use",
            "price_include",
            "account_id:id",
            "refund_account_id:id",
            "kind_id:id",
            "rc_type",
            "rc_sale_tax_id:id",
            "payability",
            # "company_id:id",
        ]

    def set_hdr_out_tax(self):
        return [
            "id",
            "description",
            "name",
            "sequence",
            "amount",
            "amount_type",
            "type_tax_use",
            "price_include",
            "account_id:id",
            "refund_account_id:id",
            "tag_ids:id",
            "children_tax_ids:id",
            "chart_template_id:id",
            "tag_group:id",
        ]

    def set_hdr_out_group_tax(self):
        return []

    def set_some_values_account(self, row):
        item = "user_type_id:id"
        if self.to_major_version > 9:
            if row["code"].startswith("121") or row["code"].startswith("123"):
                row[item] = "account.data_account_type_fixed_assets"
            elif row["code"] == "152220":
                row[item] = "account.data_account_type_current_assets"
            elif row["code"] == "152420":
                row[item] = "account.data_account_type_non_current_assets"
            elif row["code"].startswith("211"):
                row[item] = "account.data_account_type_equity"
            elif row["code"].startswith("65"):
                row[item] = "account.data_account_type_depreciation"
            elif row["code"] == "190120":
                row[item] = "account.data_account_type_prepayments"
            elif (
                row["code"].startswith("610")
                and row[item] == "account.data_account_type_expenses"
            ):
                row[item] = "account.data_account_type_direct_costs"
            elif row["code"] == "870230":
                row[item] = "account.data_unaffected_earnings"
            elif (
                row["code"].startswith("8")
                and row[item] == "account.data_account_type_income"
            ):
                row[item] = "account.data_account_type_other_income"
            elif (
                row[item] == "account.data_account_type_current_assets"
                and "+12 M" in row["name"]
            ):
                row[item] = "account.data_account_type_non_current_assets"
            elif (
                row[item] == "account.data_account_type_liability"
                and "+12 M" in row["name"]
            ):
                row[item] = "account.data_account_type_non_current_liabilities"

        if self.to_major_version > 9:
            item = "group_id:id"
        else:
            item = "parent_id:id"
        if not row[item]:
            if len(row["code"]) >= 6:
                if row["code"].startswith("126"):
                    row[item] = "125"
                elif row["code"].startswith("154"):
                    row[item] = "153"
                elif row["code"].startswith("18"):
                    row[item] = "180"
                elif (
                    row["code"].startswith("12")
                    or row["code"].startswith("15")
                    or row["code"].startswith("265")
                    or row["code"].startswith("651")
                    or row["code"].startswith("652")
                ):
                    row[item] = row["code"][0:3]
                else:
                    row[item] = row["code"][0:2]
            elif len(row["code"]) >= 3:
                row[item] = row["code"][0:2]
            elif len(row["code"]) >= 2:
                row[item] = row["code"][0:1]
            else:
                row[item] = ""

        return row

    def set_some_values_tax(self, row):
        return row

    def get_xref(self, xref):
        if isinstance(xref, str):
            if "." not in xref:
                xref = "z0bug.%s" % xref
        return xref

    def get_key(self, xref, is_id=None):
        if isinstance(xref, str):
            if "." in xref:
                module, xid = xref.split(".", 1)
            else:
                module, xid = "z0bug", xref
            if module == "external":
                xref = xid
            elif module == "z0bug":
                if xid.startswith("coa_") or xid.startswith("tax_"):
                    xref = xid[4:]
                else:
                    xref = xid
            elif module == "l10n_it_account_tax_kind":
                xref = xid.replace("_", ".").upper()
            elif module == self.opt_args.module or is_id:
                xref = xid
        return xref

    def read_csv_file(self, csv_fn=None):
        self.ffn = csv_fn or self.opt_args.src_csvfile
        self.lines = []
        self.groups = []
        with open(self.ffn, "r") as fd:
            self.hdr = False
            reader = csv.reader(fd)
            for row in reader:
                if not self.hdr:
                    self.hdr = {
                        "account.account": self.set_default_hdr_account,
                        "account.tax": self.set_default_hdr_tax,
                    }[self.opt_args.model]()
                    self.hdr_out = {
                        (
                            "account.account",
                            "export-comparable",
                        ): self.set_hdr_out_comparable_account,
                        (
                            "account.account",
                            "export-z0bug",
                        ): self.set_hdr_out_z0bug_account,
                        ("account.account", "export-full"): self.set_hdr_out_account,
                        (
                            "account.account",
                            "export-group",
                        ): self.set_hdr_out_group_account,
                        (
                            "account.tax",
                            "export-comparable",
                        ): self.set_hdr_out_comparable_tax,
                        ("account.tax", "export-z0bug"): self.set_hdr_out_z0bug_tax,
                        ("account.tax", "export-full"): self.set_hdr_out_tax,
                        ("account.tax", "export-group"): self.set_hdr_out_group_tax,
                    }[self.opt_args.model, self.opt_args.action]()

                    next_id = len(row)
                    for name in self.hdr.keys():
                        ttype = ""
                        if name.endswith(":id"):
                            name = (
                                transodoo.translate_from_to(
                                    self.ctx,
                                    self.opt_args.model,
                                    name.replace(":id", ""),
                                    self.opt_args.to_version,
                                    self.opt_args.from_version,
                                    ttype="field",
                                )
                                + ":id"
                            )
                        elif name.endswith("/id"):
                            name = (
                                transodoo.translate_from_to(
                                    self.ctx,
                                    self.opt_args.model,
                                    name.replace(":id", ""),
                                    self.opt_args.to_version,
                                    self.opt_args.from_version,
                                    ttype="field",
                                )
                                + ":id"
                            )
                        else:
                            name = transodoo.translate_from_to(
                                self.ctx,
                                self.opt_args.model,
                                name,
                                self.opt_args.to_version,
                                self.opt_args.from_version,
                                ttype="field",
                            )
                        if name == "id" or name.endswith(":id"):
                            if name in row:
                                ix = row.index(name)
                            elif name.replace(":id", "/id") in row:
                                ix = row.index(name.replace(":id", "/id"))
                            elif name[:-3] in row:
                                ix = row.index(name[:-3])
                            else:
                                ix = next_id
                                next_id += 1
                            ttype = "m2o"
                        elif name in row:
                            ix = row.index(name)
                        else:
                            ix = next_id
                            next_id += 1
                        self.hdr[name]["ix"] = ix
                        if name in self.hdr_out:
                            ox = self.hdr_out.index(name)
                            self.hdr[name]["ox"] = ox
                        if ttype:
                            self.hdr[name]["type"] = ttype
                            if ttype == "m2o":
                                self.hdr[name]["tnl"] = True
                    if self.opt_args.verbose:
                        print(self.hdr_out)
                    continue

                line = unicodes(row)
                while len(line) < next_id:
                    line.append("")
                row = {}
                for name in self.hdr.keys():
                    ix = self.hdr[name]["ix"]
                    if name == "id":
                        row[name] = self.get_key(line[ix], is_id=True)
                    elif name == "chart_template_id:id":
                        row[name] = "l10n_chart_it_zeroincombenze"
                    elif self.hdr[name].get("type", "") == "m2o" and "." in line[ix]:
                        value = transodoo.translate_from_to(
                            self.ctx,
                            "ir.model.data",
                            self.get_xref(line[ix]),
                            self.opt_args.from_version,
                            self.opt_args.to_version,
                            ttype="xref",
                            fld_name=name,
                        )
                        if isinstance(value, (list, tuple)):
                            row[name] = self.get_key(value[0])
                        else:
                            row[name] = self.get_key(value)
                    elif self.hdr[name].get("type", "") == "bool":
                        value = os0.str2bool(line[ix], False)
                        if self.opt_args.alt_format:
                            if self.opt_args.action == "export-z0bug":
                                row[name] = value
                            else:
                                row[name] = "TRUE" if value else "FALSE"
                        elif self.opt_args.action == "export-z0bug":
                            row[name] = 1 if value else 0
                        else:
                            row[name] = value
                    elif (
                        self.hdr[name].get("type", "") == "float"
                        and line[ix]
                        and line[ix].isdigit()
                    ):
                        row[name] = eval(line[ix])
                    else:
                        if self.hdr[name].get("tnl", ""):
                            value = transodoo.translate_from_to(
                                self.ctx,
                                self.opt_args.model,
                                line[ix],
                                self.opt_args.from_version,
                                self.opt_args.to_version,
                                ttype="value",
                                fld_name=name,
                            )
                            if isinstance(value, (list, tuple)):
                                row[name] = value[0]
                            else:
                                row[name] = value
                        else:
                            row[name] = line[ix]

                row = {
                    "account.account": self.set_some_values_account,
                    "account.tax": self.set_some_values_tax,
                }[self.opt_args.model](row)
                line = [row[name] for name in self.hdr_out]
                if self.opt_args.verbose:
                    print(line)
                self.lines.append(line)

    def get_format(self, fmt_id=None):
        if self.opt_args.action == "export-z0bug" and not fmt_id:
            fmt = "external.%s"
        elif self.opt_args.module == "l10n_it":
            fmt = "%s.%%s" % self.opt_args.module
        else:
            fmt = (
                "z0bug.%s_%%s"
                % {
                    "account.account": "coa",
                    "account.tax": "tax",
                }[self.opt_args.model]
            )
        return fmt

    def format_out(self):
        for nro, line in enumerate(self.lines):
            fmt = self.get_format()
            fmt_id = self.get_format(fmt_id=True)
            for name in self.hdr_out:
                ox = self.hdr[name]["ox"]
                if not line[ox]:
                    continue
                if name == "id" and self.opt_args.action == "export-z0bug":
                    self.lines[nro][ox] = fmt_id % line[ox]
                elif (
                    self.hdr[name].get("rel", "")
                    and self.opt_args.action == "export-z0bug"
                ):
                    self.lines[nro][ox] = fmt % line[ox]

        if self.opt_args.action == "export-z0bug":
            self.hdr_out = [x.replace(":id", "") for x in self.hdr_out]

    def merge(self, merge):
        for merge_line in merge.lines:
            rec_id = merge_line[merge.hdr["id"]["ox"]]
            for ii, line in enumerate(self.lines):
                if rec_id == line[self.hdr["id"]["ox"]]:
                    for name in self.hdr_out:
                        if name in merge.hdr_out:
                            merge_ox = merge.hdr[name]["ox"]
                            ox = self.hdr[name]["ox"]
                            if not line[ox] and merge_line[merge_ox]:
                                self.lines[ii][ox] = merge_line[merge_ox]
                    break

    def close(self):
        if not self.opt_args.tgt_csvfile:
            self.opt_args.tgt_csvfile = self.ffn
        if not self.opt_args.dry_run:
            self.format_out()
            bakfile = "%s.bak" % self.opt_args.tgt_csvfile
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            if os.path.isfile(self.opt_args.tgt_csvfile):
                os.rename(self.opt_args.tgt_csvfile, bakfile)
            with open(self.opt_args.tgt_csvfile, "w") as fd:
                csv_obj = csv.writer(fd)
                csv_obj.writerow(self.hdr_out)
                for line in self.lines:
                    ln = []
                    for x in line:
                        ln.append(x)
                    csv_obj.writerow(ln)
                if self.opt_args.verbose > 0:
                    print("👽 %s" % self.opt_args.tgt_csvfile)


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Manage csv file of Odoo CoA / Taxes",
        epilog="© 2020-2023 by SHS-AV s.r.l.",
    )
    parser.add_argument(
        "-A",
        "--action",
        action="store",
        dest="action",
        help="Actions are %s" % ",".join(VALID_ACTIONS),
    )
    parser.add_argument("-b", "--to-version", dest="to_version", default="12.0")
    parser.add_argument("-F", "--from-version", dest="from_version")
    parser.add_argument("-m", "--merge-csv", dest="merge_csvfile")
    parser.add_argument("-M", "--module")
    parser.add_argument("-n", "--dry-run", dest="dry_run", action="store_true")
    parser.add_argument("-o", "--tgt-csvfile", dest="tgt_csvfile")
    parser.add_argument("-t", "--model", default="account.account")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("-z", "--alt-format", dest="alt_format", action="store_true")
    parser.add_argument("src_csvfile")
    opt_args = parser.parse_args(cli_args)

    if opt_args.model not in ("account.account", "account.tax"):
        print("Invalid model: use account.account or account.tax")
        return 1
    if opt_args.action not in VALID_ACTIONS:
        print("Invalid action %s!" % opt_args.action)
        print("Valid action are: %s" % ",".join(VALID_ACTIONS))
        return 1
    if opt_args.to_version not in VERSIONS:
        print("Invalid Odoo target version %s: use -b option" % opt_args.to_version)
        return 1
    if not opt_args.from_version:
        opt_args.from_version = opt_args.to_version
    if opt_args.from_version not in VERSIONS:
        print("Invalid Odoo source version %s: use -F option" % opt_args.from_version)
        return 1
    opt_args.src_csvfile = os.path.expanduser(opt_args.src_csvfile)
    if not os.path.isfile(opt_args.src_csvfile):
        print("File %s not found!" % opt_args.src_csvfile)
        return 1
    if opt_args.merge_csvfile:
        opt_args.merge_csvfile = os.path.expanduser(opt_args.merge_csvfile)
        if not os.path.isfile(opt_args.merge_csvfile):
            print("File %s not found!" % opt_args.merge_csvfile)
            return 1

    CsvFile = CvtCsvFile(opt_args)
    CsvFile.read_csv_file()
    if opt_args.merge_csvfile:
        CsvMerge = CvtCsvFile(opt_args)
        CsvMerge.read_csv_file(opt_args.merge_csvfile)
        CsvFile.merge(CsvMerge)
    CsvFile.close()

