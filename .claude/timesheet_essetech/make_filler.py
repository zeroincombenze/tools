#!/usr/bin/env python3
"""Generate the browser form-filler from the converted timesheet records."""
import json
import sys

TEMPLATE = r"""(function () {
    "use strict";
    var RECORDS = __RECORDS__;
    // l'indice e' legato al lotto: un CSV nuovo riparte da zero da solo
    var KEY = "esse_ts_idx_" + "__BATCH__";

    var form = document.querySelector(".o_website_timesheet form");
    if (!form) {
        alert("Form non trovato. Apri https://dueesseti.odoo.com/create/timesheet");
        return;
    }
    function field(name) {
        return form.querySelector('[name="' + name + '"]');
    }

    var problems = [];

    function safe(label, fn) {
        try {
            fn();
        } catch (err) {                       // un campo rotto non ferma gli altri
            problems.push(label + ": " + err.message);
            console.error(label, err);
        }
    }

    function setText(name, value) {
        var el = field(name);
        if (!el) { problems.push("campo mancante: " + name); return; }
        el.value = value;
        el.dispatchEvent(new Event("input", {bubbles: true}));
        el.dispatchEvent(new Event("change", {bubbles: true}));
    }

    // I quattro menu (partner/project/task/ticket) sono widget select2 v3: NON
    // si deve lanciare "change" sulla select, il loro initSelection va in errore.
    // Si imposta il valore reale (e' quello che viene inviato) e si aggiorna a
    // mano l'etichetta mostrata dal widget.
    function setSelect(name, value) {
        var el = field(name);
        if (!el) { problems.push("campo mancante: " + name); return; }
        var opt = null;
        if (value) {
            opt = el.querySelector('option[value="' + value + '"]');
            if (!opt) { problems.push("opzione assente: " + name + "=" + value); return; }
            opt.classList.remove("disabled");
            opt.disabled = false;
        }
        el.value = value;

        var box = document.getElementById("s2id_" + (el.id || name));
        if (!box) {                           // select normale (es. report_type)
            el.dispatchEvent(new Event("change", {bubbles: true}));
            return;
        }
        var chosen = box.querySelector(".select2-chosen");
        if (chosen) { chosen.textContent = opt ? opt.textContent.trim() : ""; }
        var choice = box.querySelector(".select2-choice");
        if (choice) { choice.classList.remove("select2-default"); }
    }

    function dump() {
        var out = {};
        new FormData(form).forEach(function (v, k) { out[k] = v; });
        console.table(out);
        return out;
    }

    function banner(html, color) {
        var old = document.getElementById("esse_ts_banner");
        if (old) { old.remove(); }
        var div = document.createElement("div");
        div.id = "esse_ts_banner";
        div.style.cssText = "position:fixed;top:0;left:0;right:0;z-index:99999;padding:8px 16px;"
            + "font:14px/1.4 monospace;color:#fff;background:" + color + ";text-align:center";
        div.innerHTML = html;
        document.body.appendChild(div);
    }

    var idx = parseInt(localStorage.getItem(KEY) || "0", 10);
    if (idx >= RECORDS.length) {
        banner("Completati tutti i " + RECORDS.length + " record. "
               + "Per ricominciare: localStorage.removeItem('" + KEY + "')", "#198754");
        return;
    }
    var rec = RECORDS[idx];

    safe("partner_id", function () { setSelect("partner_id", rec.partner_id); });
    safe("project_id", function () { setSelect("project_id", rec.project_id); });
    safe("timesheet_task_id", function () {
        setSelect("timesheet_task_id", rec.timesheet_task_id);
    });
    safe("report_type", function () { setSelect("report_type", rec.report_type); });
    if (rec.ticket_id) {
        safe("ticket_id", function () { setSelect("ticket_id", rec.ticket_id); });
    }
    safe("helpdesk_ref", function () { setText("helpdesk_ref", rec.helpdesk_ref || ""); });
    safe("date", function () { setText("date", rec.date); });
    safe("time_from", function () { setText("time_from", rec.time_from); });
    safe("time_to", function () { setText("time_to", rec.time_to); });
    safe("name", function () { setText("name", rec.name); });
    safe("internal_name", function () { setText("internal_name", rec.internal_name || ""); });

    var total = field("total_hours");
    if (total && (!total.value || total.value === "n/a")) {
        total.value = rec.total_hours;          // fallback: di norma lo calcola il sito
    }

    banner("Record <b>" + (idx + 1) + " / " + RECORDS.length + "</b> (riga CSV " + rec.line
           + ") &nbsp;|&nbsp; " + rec.date + " &nbsp; " + rec.time_from + "&rarr;" + rec.time_to
           + " (" + rec.total_hours + ") &nbsp;|&nbsp; " + rec.task_label
           + " &nbsp;|&nbsp; " + (rec.report_type === "internal" ? "Interno" : "Esterno")
           + "<br>" + rec.name
           + (problems.length
              ? "<br><b>PROBLEMI:</b> " + problems.join(" / ")
              : "<br><small>Controlla i campi, poi premi <b>Salva e nuova</b>. "
                + "L'indice avanza solo al salvataggio.</small>"),
           problems.length ? "#dc3545" : "#0d6efd");

    // l'indice avanza solo quando il form viene realmente inviato
    form.addEventListener("submit", function () {
        localStorage.setItem(KEY, String(idx + 1));
    }, {once: true, capture: true});

    window.ts = {
        dump: dump,
        status: function () {
            console.log("record " + (idx + 1) + "/" + RECORDS.length, rec);
        },
        goto: function (n) {
            localStorage.setItem(KEY, String(Math.max(0, n - 1)));
            console.log("prossimo record: " + n + " - rilancia il filler");
        },
        reset: function () {
            localStorage.removeItem(KEY);
            console.log("indice azzerato");
        }
    };
    console.log("Record " + (idx + 1) + "/" + RECORDS.length, rec);
    console.log("Valori che verranno inviati:");
    dump();
})();
"""


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "timesheet_records.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "timesheet_filler.js"
    with open(src, encoding="utf-8") as fd:
        records = json.load(fd)

    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    batch = "%s_%s_%d" % (min(r["date"] for r in records),
                          max(r["date"] for r in records), len(records))
    script = TEMPLATE.replace("__RECORDS__", payload).replace("__BATCH__", batch)

    with open(out, "w", encoding="utf-8") as fd:
        fd.write(script)
    print("%s  %d record, %d byte" % (out, len(records), len(script)))


if __name__ == "__main__":
    main()
