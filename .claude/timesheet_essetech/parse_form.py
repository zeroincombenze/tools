#!/usr/bin/env python3
"""Estrae gli id delle select dal salvataggio HTML del form timesheet EsseTech.

    python3 parse_form.py "Timesheet Entry Genarate _ CRM - EsseTech.html" form_config.json

Il file HTML contiene due form: quello vecchio nascosto (div
"o_website_timesheet_old") e quello vivo (div "o_website_timesheet").  Si legge
solo il secondo: nel primo i campi hanno nomi diversi (task_id, unit_amount).
"""
import html
import json
import re
import sys

SELECT_RE = re.compile(r'<select\b[^>]*\bname="([^"]+)"[^>]*>(.*?)</select>', re.S)
OPTION_RE = re.compile(r'<option\b([^>]*)>(.*?)</option>', re.S)
VALUE_RE = re.compile(r'\bvalue="([^"]*)"')
TAG_RE = re.compile(r'<[^>]+>')


def text_of(raw):
    """Testo visibile di una option, senza tag ed entita', spazi normalizzati."""
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub("", raw))).strip()


def parse(path):
    with open(path, encoding="utf-8") as fd:
        page = fd.read()

    # si parte dal form vivo, saltando quello nascosto "_old"
    start = page.find('class="o_website_timesheet"')
    if start < 0:
        raise SystemExit("form vivo non trovato: manca div.o_website_timesheet")
    page = page[start:]

    selects = {}
    for name, block in SELECT_RE.findall(page):
        options = []
        for attrs, raw in OPTION_RE.findall(block):
            match = VALUE_RE.search(attrs)
            value = match.group(1) if match else ""
            label = text_of(raw)
            if value:
                options.append({"id": value, "label": label})
        selects.setdefault(name, options)

    user = re.search(r'<input[^>]*\bname="user_id"[^>]*\bvalue="([^"]*)"', page)
    action = re.search(r'<form[^>]*\baction="([^"]*)"', page)
    return {
        "action": action.group(1) if action else "",
        "user_id": user.group(1) if user else "",
        "selects": selects,
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    config = parse(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else "form_config.json"
    with open(out, "w", encoding="utf-8") as fd:
        json.dump(config, fd, ensure_ascii=False, indent=1)

    print("action  : %s" % config["action"])
    print("user_id : %s" % config["user_id"])
    for name, options in sorted(config["selects"].items()):
        print("%-18s %2d opzioni" % (name, len(options)))
        for opt in options[:12]:
            print("    %-8s %s" % (opt["id"], opt["label"][:70]))
        if len(options) > 12:
            print("    ... altre %d" % (len(options) - 12))
    print("\nscritto : %s" % out)


if __name__ == "__main__":
    main()
