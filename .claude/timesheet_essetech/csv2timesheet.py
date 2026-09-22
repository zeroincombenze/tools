#!/usr/bin/env python3
"""Converte un CSV di attivita' nei record del form timesheet EsseTech.

    python3 csv2timesheet.py attivita.csv form_config.json timesheet_records.json

Colonne richieste : date, time_start, time_stop, name, task
Colonne opzionali : internal, ticket, helpdesk_ref, internal_name

Gli orari si accettano sia in ore decimali (10.25) sia in HH:MM (10:15).
La colonna "internal" (True/False) diventa il campo Tipo: Interno / Esterno.
La colonna "task" e' l'etichetta della select Lavoro, risolta sugli id letti
da form_config.json (prodotto da parse_form.py).

Opzioni:
    --corrections FILE   JSON {"testo errato": "testo corretto"} applicato alle
                         descrizioni dopo la normalizzazione degli spazi
    --partner VALORE     id o etichetta del Cliente, se il form ne offre piu' di uno
    --project VALORE     id o etichetta del Progetto, idem
"""
import argparse
import csv
import datetime
import json
import re
import sys
from collections import defaultdict

REQUIRED = ("date", "time_start", "time_stop", "name", "task")


def norm(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def key(text):
    return norm(text).lower()


def hhmm(value):
    """Ore decimali o HH:MM -> 'HH:MM'. 10.25 -> '10:15'."""
    value = norm(value)
    if ":" in value:
        hours, minutes = value.split(":", 1)
        total = int(hours) * 60 + int(minutes)
    else:
        total = int(round(float(value.replace(",", ".")) * 60))
    return "%02d:%02d" % divmod(total, 60)


def minutes_of(text):
    return int(text[:2]) * 60 + int(text[3:])


def pick_one(options, wanted, label):
    """Sceglie una option per id o etichetta; se ce n'e' una sola la usa."""
    if wanted:
        for opt in options:
            if opt["id"] == wanted or key(opt["label"]) == key(wanted):
                return opt["id"]
        for opt in options:
            if key(wanted) in key(opt["label"]):
                return opt["id"]
        raise SystemExit("%s: nessuna opzione corrisponde a %r" % (label, wanted))
    if len(options) == 1:
        return options[0]["id"]
    raise SystemExit(
        "%s: il form offre %d opzioni, indica quale usare" % (label, len(options)))


def find_ticket(options, wanted):
    """Cerca un ticket per id, per numero (#1390) o per pezzo di titolo."""
    wanted = norm(wanted)
    if not wanted:
        return "", None
    digits = re.sub(r"\D", "", wanted)
    for opt in options:
        if opt["id"] == digits or opt["id"] == wanted:
            return opt["id"], None
    if digits:
        for opt in options:
            if "#" + digits in opt["label"]:
                return opt["id"], None
    hits = [o for o in options if key(wanted) in key(o["label"])]
    if len(hits) == 1:
        return hits[0]["id"], None
    if not hits:
        return "", "ticket non trovato: %r" % wanted
    return "", "ticket ambiguo (%d corrispondenze): %r" % (len(hits), wanted)


def convert(args):
    with open(args.form_config, encoding="utf-8") as fd:
        config = json.load(fd)
    selects = config["selects"]

    corrections = {}
    if args.corrections:
        with open(args.corrections, encoding="utf-8") as fd:
            corrections = {norm(k): v for k, v in json.load(fd).items()}

    partner_id = pick_one(selects.get("partner_id", []), args.partner, "Cliente")
    project_id = pick_one(selects.get("project_id", []), args.project, "Progetto")
    tasks = {key(o["label"]): o["id"] for o in selects.get("timesheet_task_id", [])}
    tickets = selects.get("ticket_id", [])
    today = datetime.date.today().isoformat()

    records, warnings, fixed = [], [], []
    with open(args.csv, newline="", encoding="utf-8") as fd:
        reader = csv.DictReader(fd)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit("colonne mancanti nel CSV: %s" % ", ".join(missing))

        for lineno, row in enumerate(reader, start=2):
            task = norm(row["task"])
            task_id = tasks.get(key(task))
            if not task_id:
                warnings.append("riga %d: Lavoro sconosciuto %r" % (lineno, task))
                continue

            start, stop = hhmm(row["time_start"]), hhmm(row["time_stop"])
            if minutes_of(stop) <= minutes_of(start):
                warnings.append(
                    "riga %d: fine %s non successiva a inizio %s" % (lineno, stop, start))

            date = norm(row["date"])
            if date > today:
                warnings.append("riga %d: data futura %s, il form la rifiuta" % (lineno, date))

            name = norm(row["name"])
            name = corrections.get(name, name)
            if name != norm(row["name"]) or norm(row["name"]) != (row["name"] or "").strip():
                fixed.append("riga %d: %r -> %r" % (lineno, (row["name"] or "").strip(), name))

            ticket_id, issue = find_ticket(tickets, row.get("ticket", ""))
            if issue:
                warnings.append("riga %d: %s" % (lineno, issue))

            internal = key(row.get("internal", "true")) != "false"
            records.append({
                "line": lineno,
                "partner_id": partner_id,
                "project_id": project_id,
                "timesheet_task_id": task_id,
                "task_label": task,
                "report_type": "internal" if internal else "external",
                "date": date,
                "time_from": start,
                "time_to": stop,
                "total_hours": "%02d:%02d" % divmod(
                    minutes_of(stop) - minutes_of(start), 60),
                "name": name,
                "internal_name": norm(row.get("internal_name", "")),
                "helpdesk_ref": norm(row.get("helpdesk_ref", "")),
                "ticket_id": ticket_id,
            })

    by_date = defaultdict(list)
    for rec in records:
        by_date[rec["date"]].append(rec)
    for date, recs in sorted(by_date.items()):
        ordered = sorted(recs, key=lambda r: r["time_from"])
        for prev, cur in zip(ordered, ordered[1:]):
            if cur["time_from"] < prev["time_to"]:
                warnings.append("%s: %s-%s si sovrappone a %s-%s" % (
                    date, prev["time_from"], prev["time_to"],
                    cur["time_from"], cur["time_to"]))
    return records, warnings, fixed


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv")
    parser.add_argument("form_config")
    parser.add_argument("out", nargs="?", default="timesheet_records.json")
    parser.add_argument("--corrections")
    parser.add_argument("--partner")
    parser.add_argument("--project")
    args = parser.parse_args()

    records, warnings, fixed = convert(args)
    if not records:
        raise SystemExit("nessun record convertito")

    minutes = sum(minutes_of(r["total_hours"]) for r in records)
    print("record  : %d" % len(records))
    print("date    : %s .. %s" % (min(r["date"] for r in records),
                                  max(r["date"] for r in records)))
    print("totale  : %dh%02d" % divmod(minutes, 60))
    print("lavori  :")
    per_task = defaultdict(int)
    for rec in records:
        per_task[rec["task_label"]] += 1
    for task, count in sorted(per_task.items(), key=lambda kv: -kv[1]):
        print("          %-36s %3d" % (task, count))
    print("esterni : %d" % sum(1 for r in records if r["report_type"] == "external"))
    print("ticket  : %d" % sum(1 for r in records if r["ticket_id"]))

    if fixed:
        print("\nCORREZIONI (%d):" % len(fixed))
        for item in fixed:
            print("  " + item)
    if warnings:
        print("\nATTENZIONE (%d):" % len(warnings))
        for item in warnings:
            print("  " + item)
    else:
        print("\nnessun problema rilevato")

    with open(args.out, "w", encoding="utf-8") as fd:
        json.dump(records, fd, ensure_ascii=False, indent=1)
    print("\nscritto : %s" % args.out)
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
