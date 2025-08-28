# -*- coding: utf-8 -*-
import csv

src_file = "/home/odoo/tmp/piano_conti.csv"
csv.register_dialect(
    "odoo", delimiter=(","), quotechar=('"'), quoting=csv.QUOTE_MINIMAL
)
csv_obj = csv.DictReader(
    open(src_file), fieldnames=[], restkey="undef_name", dialect="odoo"
)
hdr_read = False
group_code = ""
group_name = ""
ridix = {}
for row in csv_obj:
    if not hdr_read:
        csv_obj.fieldnames = row["undef_name"]
        hdr_read = True
        continue
    is_group = False
    line = {}
    for p in csv_obj.fieldnames:
        if p == "Mastro" and row[p]:
            group_code = row[p].strip()
            is_group = True
            continue
        elif p == "Descrizione" and is_group:
            group_name = row[p].strip()
            continue
        elif is_group:
            continue
        elif p == "Codice":
            line["code"] = row[p].strip()[0] + ("%7s" % row[p][1:].strip())
            continue
        elif p == "Descrizione" and not ridix.get("name"):
            line["name"] = row[p].strip()
            continue
        elif p == "Note:":
            line["name"] = row[p].strip()
            continue
    line["group_code"] = group_code
    line["group_name"] = group_name
    if not is_group and line.get("code"):
        ridix[line["code"]] = line

src_file = "/home/odoo/tmp/account.account-it_ridix.csv"
csv_obj = csv.DictReader(
    open(src_file), fieldnames=[], restkey="undef_name", dialect="odoo"
)
hdr_read = False
account = {}
for row in csv_obj:
    if not hdr_read:
        csv_obj.fieldnames = row["undef_name"]
        hdr_read = True
        continue
    line = {}
    for p in csv_obj.fieldnames:
        if p == "code":
            line[p] = row[p].strip()[0] + ("%7s" % row[p][1:].strip())
        elif p in ("id", "code", "name", "account_type", "reconcile", "tag_ids"):
            line[p] = row[p]
            continue
    if line["code"] in ridix:
        line["name"] = ridix[line["code"]]["name"]
        line["note"] = "Group_code='%s' / Group_name='%s'" % (
            ridix[line["code"]]["group_code"],
            ridix[line["code"]]["group_name"],
        )
    account[line["code"]] = line
for code, row in ridix.items():
    if code not in account:
        line = {
            "id": row["code"].replace(" ", ""),
            "code": row["code"],
            "name": row["name"],
            "account_type": "assset_fixed!",
            "reconcile": False,
            "tag_ids": "l10n_it_ridix.account_tag_B_ATT",
            "note": "Group_code='%s' / Group_name='%s'"
            % (row["group_code"], row["group_name"]),
        }
        account[line["code"]] = line
with open("/home/odoo/tmp/account.account.csv", "w") as fd:
    csv_obj = csv.writer(fd)
    writer = csv.DictWriter(
        fd,
        fieldnames=[
            "id",
            "code",
            "name",
            "account_type",
            "reconcile",
            "tag_ids",
            "note",
        ],
    )
    writer.writeheader()
    for code in sorted(account.keys()):
        print(account[code])
        writer.writerow(account[code])
