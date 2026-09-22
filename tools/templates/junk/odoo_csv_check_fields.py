#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""Genera il file dei campi Odoo di odoo_csv_check.py leggendo il codice
python dei moduli.

Colonne prodotte: model, name, ttype, relation, required, module, selection
- module: modulo che definisce il campo
- selection: valori validi dei campi selection, JSON {"chiave": "etichetta"};
  vuoto se i valori sono calcolati a runtime (selection dinamica)

I moduli vengono cercati sotto le directory indicate; con -c l'ordine di
ricerca (e la scelta tra moduli omonimi) segue l'addons_path del file di
configurazione Odoo, con -d vengono letti solo i moduli installati nel
database indicato (altrimenti tutti i moduli installabili).

Vengono risolti _inherit (estensioni e mixin), _inherits (delega), campi
related=, selection_add e i campi automatici (id, create_uid, ...).

Uso:
    odoo_csv_check_fields.py [-f odoo_csv_check_fields.csv]
        [-c /etc/odoo/odoo18-ee.conf] [-d DATABASE] DIR [DIR ...]
es. odoo_csv_check_fields.py -c /etc/odoo/odoo18-ee.conf -d ridix18 ~/odoo18
"""
import argparse
import ast
import configparser
import csv
import json
import os
import subprocess
import sys

TTYPES = {
    "Boolean": "boolean", "Integer": "integer", "Float": "float",
    "Monetary": "monetary", "Char": "char", "Text": "text", "Html": "html",
    "Date": "date", "Datetime": "datetime", "Binary": "binary", "Image": "binary",
    "Selection": "selection", "Reference": "reference", "Json": "json",
    "Many2one": "many2one", "One2many": "one2many", "Many2many": "many2many",
    "Many2oneReference": "many2one_reference", "Properties": "properties",
    "PropertiesDefinition": "properties_definition",
}
RELATIONAL = ("many2one", "one2many", "many2many")
# classi di campo definite dai moduli (es. JobSerialized(fields.Json)): nome -> ttype
CUSTOM_TTYPES = {}
MODULE_PATHS = {}  # modulo -> directory, per risolvere gli import odoo.addons.*
_CONSTANTS = {}  # file -> {nome: nodo ast} delle costanti a livello di modulo
MODEL_BASES = ("Model", "TransientModel", "AbstractModel")
SKIP_DIRS = ("tests", "migrations", "upgrades", "static", "__pycache__",
             "node_modules", ".git")
SKIP_ROOT_DIRS = (".git", "node_modules", "_not_installable", "setup", "debian",
                  "doc", "__pycache__")
HEADER = ["model", "name", "ttype", "relation", "required", "module", "selection"]


# ---------------------------------------------------------------------------
# Moduli
# ---------------------------------------------------------------------------
def read_manifest(path):
    for fn in ("__manifest__.py", "__openerp__.py"):
        manifest = os.path.join(path, fn)
        if os.path.isfile(manifest):
            try:
                with open(manifest, encoding="utf-8") as fd:
                    return ast.literal_eval(fd.read())
            except (ValueError, SyntaxError):
                return {"installable": False}
    return None


def find_modules(roots, max_depth=3):
    """{nome modulo: [path]} per tutti i moduli sotto le directory indicate"""
    found = {}
    for root in roots:
        root = os.path.abspath(os.path.expanduser(root))
        for cur, dirs, _files in os.walk(root):
            depth = cur[len(root):].count(os.sep)
            if read_manifest(cur) is not None:
                found.setdefault(os.path.basename(cur), []).append(cur)
                dirs[:] = []
                continue
            dirs[:] = sorted(
                d for d in dirs
                if d not in SKIP_ROOT_DIRS and not d.startswith(("venv", "."))
            ) if depth < max_depth else []
    return found


def addons_path(config):
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(config)
    value = cp.get("options", "addons_path", fallback="")
    return [os.path.abspath(p.strip()) for p in value.split(",") if p.strip()], \
        cp.get("options", "db_user", fallback="")


def installed_modules(database, user):
    """{nome modulo: versione installata}"""
    cmd = ["psql", "-d", database, "-AtF", " ", "-c",
           "select name, coalesce(latest_version, '') from ir_module_module"
           " where state = 'installed'"]
    if user and user != "False":
        cmd[1:1] = ["-U", user]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode:
        raise SystemExit("Lettura moduli da %s non riuscita: %s"
                         % (database, proc.stderr.strip()))
    return dict((line.split(" ", 1) + [""])[:2] for line in proc.stdout.splitlines())


def select_modules(found, paths, installed):
    """{nome: path} dei moduli da leggere; avvisa su assenti e omonimi"""
    selected = {}
    for name, candidates in sorted(found.items()):
        if installed is not None and name not in installed:
            continue
        if paths:
            ordered = [c for p in paths for c in candidates
                       if os.path.dirname(c) == p]
            if not ordered:
                continue  # fuori dall'addons_path
        else:
            ordered = candidates
        if len(ordered) > 1:
            # tra moduli omonimi vale quello con la versione installata
            version = (installed or {}).get(name)
            same = [c for c in ordered
                    if version and (read_manifest(c) or {}).get("version") == version]
            if same:
                ordered = same + [c for c in ordered if c not in same]
            print("Modulo %s in più directory, usato %s" % (name, ordered[0]),
                  file=sys.stderr)
        manifest = read_manifest(ordered[0]) or {}
        if installed is None and not manifest.get("installable", True):
            continue
        selected[name] = ordered[0]
    if installed is not None:
        for name in sorted(set(installed) - set(selected)):
            print("Modulo installato %s: codice non trovato" % name, file=sys.stderr)
    return selected


def load_order(modules):
    """Ordina i moduli rispettando le dipendenze (depends)"""
    deps = {
        name: [d for d in (read_manifest(path) or {}).get("depends", [])
               if d in modules]
        for name, path in modules.items()
    }
    if "base" in modules:
        for name in deps:
            if name != "base" and "base" not in deps[name]:
                deps[name].append("base")
    # come Odoo: per profondità nel grafo delle dipendenze, poi per nome
    depth = {}

    def get_depth(name, stack=()):
        if name not in depth:
            if name in stack:
                return 0  # ciclo: lo si ignora
            depth[name] = 1 + max(
                (get_depth(d, stack + (name,)) for d in deps[name]), default=-1)
        return depth[name]

    return sorted(modules, key=lambda name: (get_depth(name), name))


# ---------------------------------------------------------------------------
# Analisi del codice
# ---------------------------------------------------------------------------
def const(node):
    return node.value if isinstance(node, ast.Constant) else None


def text(node):
    """Stringa costante, anche dentro _("...") / _lt("...")"""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Call) and node.args and isinstance(node.func, ast.Name) \
            and node.func.id in ("_", "_lt"):
        return const(node.args[0])
    return None


def str_list(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [e.value for e in node.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    return []


def addons_file(dotted):
    """'odoo.addons.base.models.res_partner' -> path del file, se noto"""
    parts = dotted.split(".")
    if len(parts) < 3 or parts[:2] != ["odoo", "addons"] \
            or parts[2] not in MODULE_PATHS:
        return None
    base = os.path.join(MODULE_PATHS[parts[2]], *parts[3:])
    for path in (base + ".py", os.path.join(base, "__init__.py")):
        if os.path.isfile(path):
            return path
    return None


def file_constants(path, tree=None):
    """Costanti a livello di modulo di un file python (liste e tuple),
    comprese quelle importate con from odoo.addons.<modulo>... import NOME"""
    if path in _CONSTANTS:
        return _CONSTANTS[path]
    _CONSTANTS[path] = consts = {}
    if tree is None:
        try:
            with open(path, encoding="utf-8") as fd:
                tree = ast.parse(fd.read(), path)
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
            return consts
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                and isinstance(stmt.targets[0], ast.Name) \
                and isinstance(stmt.value, (ast.List, ast.Tuple, ast.Name)):
            consts[stmt.targets[0].id] = stmt.value
        elif isinstance(stmt, ast.ImportFrom) and stmt.module and not stmt.level:
            source = addons_file(stmt.module)
            if source:
                for alias in stmt.names:
                    value = file_constants(source).get(alias.name)
                    if value is not None:
                        consts[alias.asname or alias.name] = value
    return consts


def selection_list(node, consts=None, depth=0):
    """[(chiave, etichetta)] di una selection statica, None se dinamica"""
    if isinstance(node, ast.Name) and consts and depth < 5:
        value = consts.get(node.id)
        return selection_list(value, consts, depth + 1) if value is not None else None
    if not isinstance(node, (ast.List, ast.Tuple)):
        return None
    values = []
    for elt in node.elts:
        if not isinstance(elt, (ast.List, ast.Tuple)) or not elt.elts:
            return None
        key = const(elt.elts[0])
        if key is None and not isinstance(elt.elts[0], ast.Constant):
            return None
        label = (text(elt.elts[1]) or "") if len(elt.elts) > 1 else None
        values.append((key, label))
    return values


def field_ttype(name):
    return TTYPES.get(name) or CUSTOM_TTYPES.get(name)


def field_class(call):
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
            and func.value.id == "fields" and field_ttype(func.attr):
        return func.attr
    if isinstance(func, ast.Name) and field_ttype(func.id):
        return func.id
    return None


def register_field_classes(tree):
    """Registra le classi derivate da un campo Odoo; il ttype è l'attributo
    'type' della classe, altrimenti quello della classe base"""
    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef) or cls.name in TTYPES:
            continue
        base_ttype = None
        for base in cls.bases:
            name = base.attr if isinstance(base, ast.Attribute) else \
                base.id if isinstance(base, ast.Name) else None
            if name == "Field" or field_ttype(name):
                base_ttype = field_ttype(name) or ""
                break
        if base_ttype is None:
            continue
        for stmt in cls.body:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                    and isinstance(stmt.targets[0], ast.Name) \
                    and stmt.targets[0].id == "type" \
                    and isinstance(const(stmt.value), str):
                base_ttype = const(stmt.value)
        if base_ttype:
            CUSTOM_TTYPES[cls.name] = base_ttype


def base_kind(cls):
    for base in cls.bases:
        name = base.attr if isinstance(base, ast.Attribute) else \
            base.id if isinstance(base, ast.Name) else None
        if name in MODEL_BASES:
            return name
    return None


def parse_field(cls_name, call, module, consts=None):
    """Attributi di una definizione di campo (solo quelli specificati)"""
    ttype = field_ttype(cls_name)
    kw = {k.arg: k.value for k in call.keywords if k.arg}
    attrs = {"ttype": ttype, "module": module}
    if ttype in RELATIONAL:
        node = kw.get("comodel_name") or (call.args[0] if call.args else None)
        if node is not None and isinstance(const(node), str):
            attrs["relation"] = const(node)
    if "required" in kw and isinstance(const(kw["required"]), bool):
        attrs["required"] = const(kw["required"])
    if ttype == "many2one" and const(kw.get("delegate")) is True:
        attrs["delegate"] = True
    if "related" in kw and isinstance(const(kw["related"]), str):
        attrs["related"] = const(kw["related"])
    if ttype == "selection":
        node = kw.get("selection") or (call.args[0] if call.args else None)
        if node is not None:
            attrs["selection"] = selection_list(node, consts)  # None = dinamica
        if "selection_add" in kw:
            attrs["selection_add"] = selection_list(kw["selection_add"], consts) or []
    return attrs


class ModelDef:
    def __init__(self, name):
        self.name = name
        self.parents = []  # _inherit diversi dal modello stesso
        self.inherits = []  # _inherits: modelli delegati
        self.abstract = False
        self.log_access = True
        self.defs = {}  # campo -> [attributi di ogni definizione, in ordine]
        self.defined = False  # esiste una classe con _name


def scan(modules, order):
    models = {}
    for module in order:
        for root, dirs, files in os.walk(modules[module]):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for fn in sorted(files):
                if fn.endswith(".py") and not fn.startswith("__manifest__"):
                    scan_file(os.path.join(root, fn), module, models)
    return models


def scan_file(path, module, models):
    try:
        with open(path, encoding="utf-8") as fd:
            tree = ast.parse(fd.read(), path)
    except (SyntaxError, UnicodeDecodeError, ValueError) as exc:
        print("Saltato %s: %s" % (path, exc), file=sys.stderr)
        return
    register_field_classes(tree)
    consts = file_constants(path, tree)
    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        name, inherit, inherits, log_access, found = None, [], {}, None, []
        for stmt in cls.body:
            # anche le assegnazioni annotate: child_ids: Partner = fields...
            if isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                targets = [stmt.target]
            elif isinstance(stmt, ast.Assign):
                targets = stmt.targets
            else:
                continue
            if len(targets) != 1 or not isinstance(targets[0], ast.Name):
                continue
            target = targets[0].id
            if target == "_name":
                name = const(stmt.value)
            elif target == "_inherit":
                inherit = str_list(stmt.value)
            elif target == "_inherits" and isinstance(stmt.value, ast.Dict):
                inherits = {const(k): const(v)
                            for k, v in zip(stmt.value.keys, stmt.value.values)}
            elif target == "_log_access":
                log_access = const(stmt.value)
            elif isinstance(stmt.value, ast.Call):
                cls_name = field_class(stmt.value)
                if cls_name:
                    found.append((target, parse_field(
                        cls_name, stmt.value, module, consts)))
        kind = base_kind(cls)
        if not isinstance(name, str) and not inherit:
            continue
        if not kind and not found and not inherit:
            continue
        targets = [name] if isinstance(name, str) else inherit
        for model in targets:
            mdef = models.setdefault(model, ModelDef(model))
            if isinstance(name, str):
                mdef.defined = True
                if kind == "AbstractModel":
                    mdef.abstract = True
            if log_access is False:
                mdef.log_access = False
            for parent in inherit:
                if parent != model and parent not in mdef.parents:
                    mdef.parents.append(parent)
            for parent, fname in inherits.items():
                if parent and parent not in mdef.inherits:
                    mdef.inherits.append(parent)
                if fname and fname not in mdef.defs:
                    mdef.defs.setdefault(fname, []).append(
                        {"ttype": "many2one", "relation": parent, "module": module})
            for fname, attrs in found:
                mdef.defs.setdefault(fname, []).append(attrs)
                if attrs.get("delegate") and attrs.get("relation") \
                        and attrs["relation"] not in mdef.inherits:
                    mdef.inherits.append(attrs["relation"])


def merge(base, attrs):
    """Applica una definizione di campo sopra gli attributi ereditati"""
    result = dict(base)
    add = attrs.get("selection_add")
    for key, value in attrs.items():
        if key in ("selection_add", "delegate"):
            continue
        if key == "module" and "module" in result:
            continue  # resta il modulo che ha creato il campo
        result[key] = value
    if attrs.get("ttype") and base.get("ttype") and attrs["ttype"] != base["ttype"]:
        result.pop("selection", None) if attrs["ttype"] != "selection" else None
    if add is not None and result.get("selection") is not None:
        keys = {k for k, _l in result["selection"]}
        result["selection"] = result["selection"] + [
            (k, l) for k, l in add if k not in keys and l is not None]
    elif add is not None and "selection" not in result:
        result["selection"] = [(k, l) for k, l in add if l is not None]
    return result


class Resolver:
    def __init__(self, models):
        self.models = models
        self.cache = {}

    def fields(self, model, stack=()):
        """{campo: attributi} del modello, con ereditarietà risolta"""
        if model in self.cache:
            return self.cache[model]
        mdef = self.models.get(model)
        if mdef is None or model in stack:
            return {}
        stack = stack + (model,)
        result = {}
        if mdef.defined:
            result["id"] = {"ttype": "integer", "module": "base"}
            result["display_name"] = {"ttype": "char", "module": "base"}
            if not mdef.abstract and mdef.log_access:
                for fname, ttype, rel in (
                        ("create_uid", "many2one", "res.users"),
                        ("create_date", "datetime", ""),
                        ("write_uid", "many2one", "res.users"),
                        ("write_date", "datetime", "")):
                    result[fname] = {"ttype": ttype, "relation": rel, "module": "base"}
        for parent in mdef.inherits:  # delega: campi del padre come related
            for fname, attrs in self.fields(parent, stack).items():
                if fname not in result and fname not in mdef.defs:
                    result[fname] = dict(attrs)
        for parent in mdef.parents:
            for fname, attrs in self.fields(parent, stack).items():
                result[fname] = merge(result.get(fname, {}), attrs) \
                    if fname in result else dict(attrs)
        for fname, defs in mdef.defs.items():
            attrs = result.get(fname, {})
            for d in defs:
                attrs = merge(attrs, d)
            result[fname] = attrs
        self.cache[model] = result
        return result

    def resolve_related(self, model, attrs, depth=0):
        """Relazione e valori selection dei campi related"""
        path = attrs.get("related")
        if not path or depth > 10:
            return attrs
        current = model
        target = None
        parts = path.split(".")
        for ix, part in enumerate(parts):
            target = self.fields(current).get(part)
            if target is None:
                return attrs
            target = self.resolve_related(current, target, depth + 1)
            if ix < len(parts) - 1:
                current = target.get("relation")
                if not current:
                    return attrs
        result = dict(attrs)
        if result["ttype"] in RELATIONAL and not result.get("relation"):
            result["relation"] = target.get("relation", "")
        if result["ttype"] == "selection" and "selection" not in result:
            result["selection"] = target.get("selection")
        return result


def selection_json(attrs):
    if attrs.get("ttype") != "selection" or attrs.get("selection") is None:
        return ""
    return json.dumps({str(k): l for k, l in attrs["selection"]},
                      ensure_ascii=False)


def generate(csv_path, roots, config=None, database=None):
    found = find_modules(roots)
    paths, db_user = addons_path(config) if config else ([], "")
    installed = installed_modules(database, db_user) if database else None
    modules = select_modules(found, paths, installed)
    MODULE_PATHS.update(modules)
    order = load_order(modules)
    models = scan(modules, order)
    resolver = Resolver(models)
    rows = []
    for model in sorted(models):
        if not models[model].defined:
            continue  # estensione di un modello non presente
        for fname, attrs in sorted(resolver.fields(model).items()):
            if "ttype" not in attrs:
                continue
            attrs = resolver.resolve_related(model, attrs)
            rows.append({
                "model": model,
                "name": fname,
                "ttype": attrs["ttype"],
                "relation": attrs.get("relation", "") or "",
                "required": "t" if attrs.get("required") else "f",
                "module": attrs.get("module", ""),
                "selection": selection_json(attrs),
            })
    with open(csv_path, "w", encoding="utf-8", newline="") as fd:
        writer = csv.DictWriter(fd, HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("Moduli letti: %d" % len(modules))
    print("Modelli: %d, campi: %d, campi selection con valori: %d" % (
        len({r["model"] for r in rows}), len(rows),
        sum(1 for r in rows if r["selection"])))
    print("File: %s" % csv_path)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Genera il file dei campi Odoo dal codice dei moduli")
    parser.add_argument(
        "-f", "--fields-file",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "odoo_csv_check_fields.csv"),
        help="file dei campi da generare (default: %(default)s)")
    parser.add_argument("-c", "--config",
                        help="configurazione Odoo: addons_path e db_user")
    parser.add_argument("-d", "--database",
                        help="legge solo i moduli installati in questo database")
    parser.add_argument("dirs", nargs="+", metavar="DIR",
                        help="directory in cui cercare i moduli Odoo")
    args = parser.parse_args(argv)
    for base in args.dirs:
        if not os.path.isdir(os.path.expanduser(base)):
            raise SystemExit("Directory %s non trovata" % base)
    if args.config and not os.path.isfile(args.config):
        raise SystemExit("Configurazione %s non trovata" % args.config)
    generate(args.fields_file, args.dirs, args.config, args.database)


if __name__ == "__main__":
    main()
